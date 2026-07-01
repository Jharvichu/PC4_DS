"""Sighting domain models (RF 1.3: anonymous citizen sighting reports)."""

from enum import Enum

from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class ConfidenceLevel(str, Enum):
    """How confident the citizen is that this is the reported pet."""

    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


class Sighting(Base):
    """A citizen-submitted sighting of a potentially lost pet."""

    __tablename__ = "sightings"

    id = Column(String, primary_key=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    # Nullable: RF 1.3 explicitly allows anonymous citizens with no account.
    citizen_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    photo_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    confidence_level = Column(String, nullable=False, default=ConfidenceLevel.MEDIA)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_sightings_report", "report_id"),
        Index("idx_sightings_location", "latitude", "longitude"),
    )

    report = relationship("Report", back_populates="sightings")
    citizen = relationship("User", back_populates="sightings")
