"""Notification domain schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Notification response."""

    id: str
    user_id: str
    report_id: Optional[str] = None
    sighting_id: Optional[str] = None
    type: str
    content: str
    is_read: bool
    channel: str
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""

    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    radius_km: Optional[float] = Field(default=None, gt=0, le=50)
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    alerts_active: Optional[bool] = None


class NotificationPreferenceResponse(BaseModel):
    """Notification preference response."""

    id: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float
    push_enabled: bool
    sms_enabled: bool
    email_enabled: bool
    alerts_active: bool

    class Config:
        from_attributes = True
