"""Notification domain models."""

from enum import Enum

from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey, func

from app.infrastructure.database import Base


class NotificationType(str, Enum):
    """Notification type enumeration."""

    NUEVA_PERDIDA = "NUEVA_PERDIDA"
    AVISTAMIENTO = "AVISTAMIENTO"
    ALERTA_RADIO = "ALERTA_RADIO"


class Notification(Base):
    """Persisted log of a dispatched notification."""

    __tablename__ = "notifications"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=True, index=True)
    sighting_id = Column(String, ForeignKey("sightings.id"), nullable=True)
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    channel = Column(String, nullable=False)  # e.g. "push", "sms", "email"
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class NotificationPreference(Base):
    """Per-user preference: alert radius & enabled channels."""

    __tablename__ = "notification_preferences"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, nullable=False, default=5.0)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    email_enabled = Column(Boolean, default=True)
    alerts_active = Column(Boolean, default=True)  # RF 3.3: toggle receiving alerts
