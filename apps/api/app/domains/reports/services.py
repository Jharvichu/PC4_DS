"""Report domain services (SRP + DIP: depends on AlertDispatcher abstraction)."""

import logging
from typing import List

from app.config import get_settings
from app.domains.notifications.models import NotificationType
from app.domains.notifications.services import AlertDispatcher
from app.domains.reports.models import ReportStatus
from app.domains.reports.repositories import ReportRepository
from app.domains.reports.schemas import ReportCreate, ReportResponse, ReportPublicResponse
from app.infrastructure.geo import GeoPoint
from app.infrastructure.timing import log_slow_operation
from app.shared.exceptions import NotFoundError, ForbiddenError

logger = logging.getLogger(__name__)
settings = get_settings()


class ReportService:
    """Business logic for lost-pet reports, including triggering alerts."""

    def __init__(self, repository: ReportRepository, alert_dispatcher: AlertDispatcher):
        self.repository = repository
        self.alert_dispatcher = alert_dispatcher

    async def create_report(self, owner_id: str, report_data: ReportCreate) -> ReportResponse:
        """RF 1.1/1.2: create the report. Alert dispatch is scheduled separately
        (see dispatch_new_report_alert) so the HTTP response isn't blocked on it."""
        db_report = await self.repository.create(owner_id, report_data)
        return ReportResponse.from_orm(db_report)

    async def dispatch_new_report_alert(self, report_id: str, report_data: ReportCreate) -> None:
        """RF 1.4 / RNF 1.1: fan out alerts within the radius. Meant to run as a
        FastAPI BackgroundTask after the report-creation response has been sent.
        Exceptions are logged, not raised, since no client is listening anymore."""
        try:
            center = GeoPoint(report_data.last_seen_latitude, report_data.last_seen_longitude)
            message = f"Mascota perdida reportada cerca de ti. {report_data.description[:100]}"

            async with log_slow_operation("dispatch_new_report_alert", settings.ALERT_PROCESSING_TIMEOUT_SECONDS):
                await self.alert_dispatcher.dispatch_alert(
                    center=center,
                    radius_km=report_data.alert_radius_km,
                    message=message,
                    notification_type=NotificationType.NUEVA_PERDIDA,
                    report_id=report_id,
                )
        except Exception:
            logger.exception("Failed to dispatch alert for report %s", report_id)

    async def get_report(self, report_id: str, requester_id: str) -> ReportResponse:
        """Full owner-facing details; only the report's owner may view it."""
        report = await self.repository.get_by_id(report_id)
        if not report:
            raise NotFoundError(f"Report {report_id} not found")
        if report.owner_id != requester_id:
            raise ForbiddenError("You do not own this report")
        return ReportResponse.from_orm(report)

    async def get_report_public(self, report_id: str) -> ReportPublicResponse:
        """RNF 1.2: anonymized view for citizens (no owner_id, no contact info)."""
        report = await self.repository.get_by_id(report_id)
        if not report:
            raise NotFoundError(f"Report {report_id} not found")
        return ReportPublicResponse.from_orm(report)

    async def get_my_reports(self, owner_id: str) -> List[ReportResponse]:
        reports = await self.repository.get_by_owner(owner_id)
        return [ReportResponse.from_orm(r) for r in reports]

    async def update_status(self, report_id: str, owner_id: str, status: ReportStatus) -> ReportResponse:
        report = await self.repository.get_by_id(report_id)
        if not report:
            raise NotFoundError(f"Report {report_id} not found")
        if report.owner_id != owner_id:
            raise ForbiddenError("You do not own this report")

        updated = await self.repository.update_status(report_id, status)
        return ReportResponse.from_orm(updated)

    async def get_active_public_reports(self) -> List[ReportPublicResponse]:
        reports = await self.repository.get_active()
        return [ReportPublicResponse.from_orm(r) for r in reports]
