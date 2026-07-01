"""Notification domain routes."""

from typing import List

from fastapi import APIRouter, Depends

from app.core.dependencies import get_notification_service, get_current_user
from app.domains.notifications.schemas import (
    NotificationResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)
from app.domains.notifications.services import NotificationService
from app.domains.users.schemas import UserResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    current_user: UserResponse = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Get all notifications for the current user."""
    return await service.get_my_notifications(current_user.id)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a notification as read."""
    return await service.mark_as_read(notification_id)


@router.get("/preferences/me", response_model=NotificationPreferenceResponse)
async def get_my_preferences(
    current_user: UserResponse = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Get current user's notification preferences (radius, channels, toggle)."""
    prefs = await service.get_preferences(current_user.id)
    if not prefs:
        # Return sensible defaults if not yet configured
        return await service.update_preferences(current_user.id, NotificationPreferenceUpdate())
    return prefs


@router.put("/preferences/me", response_model=NotificationPreferenceResponse)
async def update_my_preferences(
    data: NotificationPreferenceUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Update notification preferences, including the RF 3.3 alerts_active toggle."""
    return await service.update_preferences(current_user.id, data)
