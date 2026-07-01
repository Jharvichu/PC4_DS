"""Notification repository interfaces (DIP)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.notifications.models import Notification, NotificationPreference


class INotificationRepository(ABC):
    """Persistence for notification logs."""

    @abstractmethod
    async def create(
        self, user_id: str, report_id: Optional[str], sighting_id: Optional[str], type_: str, content: str, channel: str
    ) -> Notification:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: str) -> List[Notification]:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        pass


class INotificationPreferenceRepository(ABC):
    """Persistence for per-user notification preferences (RF 3.3)."""

    @abstractmethod
    async def get_by_user(self, user_id: str) -> Optional[NotificationPreference]:
        pass

    @abstractmethod
    async def upsert(self, user_id: str, data: dict) -> NotificationPreference:
        pass

    @abstractmethod
    async def get_active_within_bounding_box(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[NotificationPreference]:
        pass
