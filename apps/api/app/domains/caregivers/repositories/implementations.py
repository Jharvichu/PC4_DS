"""Caregiver repository implementations."""

import uuid
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.caregivers.models import Caregiver, CaregiverRating
from app.domains.caregivers.schemas import CaregiverRegister


class CaregiverRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, caregiver_id: str) -> Optional[Caregiver]:
        stmt = select(Caregiver).where(Caregiver.id == caregiver_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> Optional[Caregiver]:
        stmt = select(Caregiver).where(Caregiver.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_id: str, data: CaregiverRegister) -> Caregiver:
        caregiver = Caregiver(
            id=str(uuid.uuid4()),
            user_id=user_id,
            role_type=data.role_type,
            accepted_species=",".join(data.accepted_species) if data.accepted_species else None,
            accepted_sizes=",".join(data.accepted_sizes) if data.accepted_sizes else None,
            can_administer_medication=data.can_administer_medication,
            specialization=data.specialization,
        )
        self.db.add(caregiver)
        await self.db.commit()
        await self.db.refresh(caregiver)
        return caregiver

    async def update(self, caregiver_id: str, data: dict) -> Optional[Caregiver]:
        caregiver = await self.get_by_id(caregiver_id)
        if not caregiver:
            return None

        for key, value in data.items():
            if value is not None and hasattr(caregiver, key):
                if key in ("accepted_species", "accepted_sizes") and isinstance(value, list):
                    value = ",".join(value)
                setattr(caregiver, key, value)

        await self.db.commit()
        await self.db.refresh(caregiver)
        return caregiver

    async def list_public(self, role_type: Optional[str] = None) -> List[Caregiver]:
        conditions = [Caregiver.is_public.is_(True)]
        if role_type:
            conditions.append(Caregiver.role_type == role_type)

        stmt = select(Caregiver).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_alert_subscribers(self) -> List[Caregiver]:
        stmt = select(Caregiver).where(
            and_(Caregiver.is_public.is_(True), Caregiver.receives_alerts.is_(True))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CaregiverRatingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, caregiver_id: str, rater_id: str, score: int, comment: Optional[str]) -> CaregiverRating:
        rating = CaregiverRating(
            id=str(uuid.uuid4()),
            caregiver_id=caregiver_id,
            rater_id=rater_id,
            score=score,
            comment=comment,
        )
        self.db.add(rating)
        await self.db.commit()
        await self.db.refresh(rating)
        return rating

    async def get_by_caregiver(self, caregiver_id: str) -> List[CaregiverRating]:
        stmt = select(CaregiverRating).where(CaregiverRating.caregiver_id == caregiver_id).order_by(
            CaregiverRating.created_at.desc()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
