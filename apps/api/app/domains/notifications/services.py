"""Notification domain services: AlertDispatcher (RF 1.4, RNF 1.1) and preferences."""

import asyncio
from typing import Dict, List, Optional

from app.domains.notifications.models import NotificationType
from app.domains.notifications.repositories import (
    NotificationRepository,
    NotificationPreferenceRepository,
)
from app.domains.notifications.schemas import (
    NotificationResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)
from app.infrastructure.geo import GeoPoint, GeospatialService
from app.infrastructure.notification_channels import INotificationChannel


class AlertDispatcher:
    """Orchestrates fan-out of an alert to users within a radius (RF 1.4).

    Kept independent of the reports/sightings domains: it only needs a center
    point, a radius, and a message. This lets ReportService and SightingService
    both trigger alerts without coupling to each other.
    """

    def __init__(
        self,
        preference_repository: NotificationPreferenceRepository,
        notification_repository: NotificationRepository,
        channels: Dict[str, INotificationChannel],
        geo_service: GeospatialService,
    ):
        self.preference_repository = preference_repository
        self.notification_repository = notification_repository
        self.channels = channels
        self.geo_service = geo_service

    async def dispatch_alert(
        self,
        center: GeoPoint,
        radius_km: float,
        message: str,
        notification_type: NotificationType,
        report_id: Optional[str] = None,
        sighting_id: Optional[str] = None,
    ) -> int:
        """Send `message` to every user with active alerts inside `radius_km`.

        RNF 1.1: must complete well under 5s. We use a bounding-box pre-filter
        (cheap, indexable) before the exact Haversine check, and fan the actual
        sends out concurrently via asyncio.gather.
        """
        min_lat, max_lat, min_lon, max_lon = self.geo_service.bounding_box(center, radius_km)

        candidates = await self.preference_repository.get_active_within_bounding_box(
            min_lat, max_lat, min_lon, max_lon
        )

        recipients = [
            pref
            for pref in candidates
            if pref.latitude is not None
            and pref.longitude is not None
            and self.geo_service.is_within_radius(center, GeoPoint(pref.latitude, pref.longitude), radius_km)
        ]

        await asyncio.gather(*(self._notify_user(pref, message, notification_type, report_id, sighting_id) for pref in recipients))

        return len(recipients)

    async def notify_user_directly(
        self,
        user_id: str,
        message: str,
        notification_type: NotificationType,
        report_id: Optional[str] = None,
        sighting_id: Optional[str] = None,
    ) -> None:
        """Send a targeted notification to a single user (e.g. new sighting -> owner)."""
        preference = await self.preference_repository.get_by_user(user_id)
        if preference is None:
            # No preferences configured yet: fall back to console + default channel
            channel = self.channels["console"]
            await channel.send(user_id, message)
            await self.notification_repository.create(
                user_id=user_id,
                report_id=report_id,
                sighting_id=sighting_id,
                type_=notification_type.value,
                content=message,
                channel=channel.name,
            )
            return

        await self._notify_user(preference, message, notification_type, report_id, sighting_id)

    async def _notify_user(self, preference, message: str, notification_type: NotificationType, report_id, sighting_id) -> None:
        enabled_channels: List[str] = []
        if preference.push_enabled:
            enabled_channels.append("push")
        if preference.sms_enabled:
            enabled_channels.append("sms")
        if preference.email_enabled:
            enabled_channels.append("email")

        if not enabled_channels:
            enabled_channels = ["console"]

        for channel_name in enabled_channels:
            channel = self.channels.get(channel_name, self.channels["console"])
            delivered = await channel.send(preference.user_id, message)
            await self.notification_repository.create(
                user_id=preference.user_id,
                report_id=report_id,
                sighting_id=sighting_id,
                type_=notification_type.value,
                content=message,
                channel=channel.name if delivered else "console",
            )


class NotificationService:
    """User-facing notification queries and preference management (SRP)."""

    def __init__(
        self,
        notification_repository: NotificationRepository,
        preference_repository: NotificationPreferenceRepository,
    ):
        self.notification_repository = notification_repository
        self.preference_repository = preference_repository

    async def get_my_notifications(self, user_id: str) -> List[NotificationResponse]:
        notifications = await self.notification_repository.get_by_user(user_id)
        return [NotificationResponse.from_orm(n) for n in notifications]

    async def mark_as_read(self, notification_id: str) -> NotificationResponse:
        notification = await self.notification_repository.mark_as_read(notification_id)
        return NotificationResponse.from_orm(notification)

    async def get_preferences(self, user_id: str) -> Optional[NotificationPreferenceResponse]:
        pref = await self.preference_repository.get_by_user(user_id)
        return NotificationPreferenceResponse.from_orm(pref) if pref else None

    async def update_preferences(
        self, user_id: str, data: NotificationPreferenceUpdate
    ) -> NotificationPreferenceResponse:
        pref = await self.preference_repository.upsert(user_id, data.dict(exclude_unset=True))
        return NotificationPreferenceResponse.from_orm(pref)
