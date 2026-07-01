"""Notification repository implementations."""

import uuid
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.notifications.models import Notification, NotificationPreference


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: str, report_id: Optional[str], sighting_id: Optional[str], type_: str, content: str, channel: str
    ) -> Notification:
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            report_id=report_id,
            sighting_id=sighting_id,
            type=type_,
            content=content,
            channel=channel,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_by_user(self, user_id: str) -> List[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(stmt)
        notification = result.scalar_one_or_none()
        if not notification:
            return None
        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)
        return notification


class NotificationPreferenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: str) -> Optional[NotificationPreference]:
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, user_id: str, data: dict) -> NotificationPreference:
        pref = await self.get_by_user(user_id)
        if not pref:
            pref = NotificationPreference(id=str(uuid.uuid4()), user_id=user_id)
            self.db.add(pref)

        for key, value in data.items():
            if value is not None:
                setattr(pref, key, value)

        await self.db.commit()
        await self.db.refresh(pref)
        return pref

    async def get_active_within_bounding_box(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[NotificationPreference]:
        stmt = select(NotificationPreference).where(
            and_(
                NotificationPreference.alerts_active.is_(True),
                NotificationPreference.latitude.between(min_lat, max_lat),
                NotificationPreference.longitude.between(min_lon, max_lon),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
