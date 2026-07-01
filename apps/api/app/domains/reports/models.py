"""Lost pet report domain models."""

from enum import Enum

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class ReportStatus(str, Enum):
    """Report status enumeration."""

    ACTIVO = "ACTIVO"
    ENCONTRADO = "ENCONTRADO"
    CANCELADO = "CANCELADO"


class Report(Base):
    """Lost pet report model."""

    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    pet_id = Column(String, ForeignKey("pets.id"), nullable=False, index=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default=ReportStatus.ACTIVO, index=True)

    # Geographic point stored as "lat,lon" (see app.infrastructure.geo.GeoPoint)
    last_seen_latitude = Column(Float, nullable=False)
    last_seen_longitude = Column(Float, nullable=False)
    last_seen_address = Column(String, nullable=True)
    last_seen_date = Column(DateTime, nullable=False, server_default=func.now())

    alert_radius_km = Column(Float, nullable=False, default=5.0)
    description = Column(String, nullable=True)

    # RNF 1.2: owner identity must stay anonymous to citizens reporting sightings
    contact_is_anonymous = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    found_date = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_reports_status_owner", "status", "owner_id"),
        Index("idx_reports_location", "last_seen_latitude", "last_seen_longitude"),
    )

    pet = relationship("Pet", back_populates="reports")
    owner = relationship("User", back_populates="reports")
    sightings = relationship("Sighting", back_populates="report", cascade="all, delete-orphan")
