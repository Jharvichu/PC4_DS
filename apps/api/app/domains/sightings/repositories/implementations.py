"""Sighting repository implementations."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.sightings.models import Sighting
from app.domains.sightings.schemas import SightingCreate


class SightingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, citizen_id: Optional[str], sighting: SightingCreate) -> Sighting:
        db_sighting = Sighting(
            id=str(uuid.uuid4()),
            report_id=sighting.report_id,
            citizen_id=citizen_id,
            latitude=sighting.latitude,
            longitude=sighting.longitude,
            photo_url=sighting.photo_url,
            description=sighting.description,
            confidence_level=sighting.confidence_level,
        )
        self.db.add(db_sighting)
        await self.db.commit()
        await self.db.refresh(db_sighting)
        return db_sighting

    async def get_by_report(self, report_id: str) -> List[Sighting]:
        stmt = select(Sighting).where(Sighting.report_id == report_id).order_by(Sighting.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, sighting_id: str) -> Optional[Sighting]:
        stmt = select(Sighting).where(Sighting.id == sighting_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
