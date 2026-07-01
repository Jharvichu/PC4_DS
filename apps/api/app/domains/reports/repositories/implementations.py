"""Report repository implementations."""

import uuid
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.reports.models import Report, ReportStatus
from app.domains.reports.schemas import ReportCreate


class ReportRepository:
    """Concrete report repository for CRUD and search operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, report_id: str) -> Optional[Report]:
        stmt = select(Report).where(Report.id == report_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, owner_id: str, report: ReportCreate) -> Report:
        db_report = Report(
            id=str(uuid.uuid4()),
            pet_id=report.pet_id,
            owner_id=owner_id,
            status=ReportStatus.ACTIVO,
            last_seen_latitude=report.last_seen_latitude,
            last_seen_longitude=report.last_seen_longitude,
            last_seen_address=report.last_seen_address,
            alert_radius_km=report.alert_radius_km,
            description=report.description,
            contact_is_anonymous=report.contact_is_anonymous,
        )
        self.db.add(db_report)
        await self.db.commit()
        await self.db.refresh(db_report)
        return db_report

    async def update_status(self, report_id: str, status: ReportStatus) -> Optional[Report]:
        report = await self.get_by_id(report_id)
        if not report:
            return None

        report.status = status
        if status == ReportStatus.ENCONTRADO:
            from datetime import datetime

            report.found_date = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_by_owner(self, owner_id: str) -> List[Report]:
        stmt = select(Report).where(Report.owner_id == owner_id).order_by(Report.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_in_bounding_box(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[Report]:
        stmt = select(Report).where(
            and_(
                Report.status == ReportStatus.ACTIVO,
                Report.last_seen_latitude.between(min_lat, max_lat),
                Report.last_seen_longitude.between(min_lon, max_lon),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active(self) -> List[Report]:
        # RF 2.5: LostPetIntentHandler reads report.pet.photo_phash for every result;
        # eager-load to avoid an N+1 query per active report.
        stmt = (
            select(Report)
            .options(selectinload(Report.pet))
            .where(Report.status == ReportStatus.ACTIVO)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
