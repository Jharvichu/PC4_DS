"""Sighting domain services (SRP + DIP)."""

import logging
from typing import List, Optional, Tuple

from app.config import get_settings
from app.domains.notifications.models import NotificationType
from app.domains.notifications.services import AlertDispatcher
from app.domains.reports.repositories import ReportRepository
from app.domains.sightings.repositories import SightingRepository
from app.domains.sightings.schemas import SightingCreate, SightingResponse
from app.infrastructure.image_utils import decode_image_data_url
from app.infrastructure.timing import log_slow_operation
from app.shared.exceptions import NotFoundError

logger = logging.getLogger(__name__)
settings = get_settings()


class SightingService:
    """Business logic for citizen sighting reports."""

    def __init__(
        self,
        repository: SightingRepository,
        report_repository: ReportRepository,
        alert_dispatcher: AlertDispatcher,
    ):
        self.repository = repository
        self.report_repository = report_repository
        self.alert_dispatcher = alert_dispatcher

    async def create_sighting(
        self, citizen_id: Optional[str], sighting_data: SightingCreate
    ) -> Tuple[SightingResponse, str, str]:
        """RF 1.3: register a sighting. Returns (response, report_id, owner_id) so the
        router can schedule the owner notification as a background task without
        exposing owner_id through the public SightingResponse schema (RNF 1.2)."""
        report = await self.report_repository.get_by_id(sighting_data.report_id)
        if not report:
            raise NotFoundError(f"Report {sighting_data.report_id} not found")

        decode_image_data_url(sighting_data.photo_url)  # RF 2.1: reject anything but JPEG/PNG

        db_sighting = await self.repository.create(citizen_id, sighting_data)

        return SightingResponse.from_orm(db_sighting), report.id, report.owner_id

    async def dispatch_sighting_notification(self, report_id: str, owner_id: str, sighting_id: str) -> None:
        """RF 1.4 / RNF 1.1: notify the pet owner. Meant to run as a FastAPI
        BackgroundTask after the sighting-creation response has been sent."""
        try:
            message = "Alguien reportó un posible avistamiento de tu mascota."
            async with log_slow_operation("dispatch_sighting_notification", settings.ALERT_PROCESSING_TIMEOUT_SECONDS):
                await self.alert_dispatcher.notify_user_directly(
                    user_id=owner_id,
                    message=message,
                    notification_type=NotificationType.AVISTAMIENTO,
                    report_id=report_id,
                    sighting_id=sighting_id,
                )
        except Exception:
            logger.exception("Failed to dispatch sighting notification for report %s", report_id)

    async def get_sightings_for_report(self, report_id: str) -> List[SightingResponse]:
        sightings = await self.repository.get_by_report(report_id)
        return [SightingResponse.from_orm(s) for s in sightings]
