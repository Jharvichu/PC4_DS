"""Caregiver network domain models (RF 3.1-3.4)."""

from enum import Enum

from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, DateTime, Text, Index, func
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class CaregiverRoleType(str, Enum):
    """Caregiver role enumeration (RF 3.1)."""

    SOLIDARIO = "SOLIDARIO"
    PROFESIONAL = "PROFESIONAL"
    ESPECIALIZADO = "ESPECIALIZADO"


class VerificationStatus(str, Enum):
    """Identity document verification status (RNF 3.1)."""

    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


class Caregiver(Base):
    """A user acting as a pet caregiver."""

    __tablename__ = "caregivers"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    role_type = Column(String, nullable=False, default=CaregiverRoleType.SOLIDARIO)

    # RF 3.2: service restrictions
    accepted_species = Column(String, nullable=True)  # comma-separated: "PERRO,GATO"
    accepted_sizes = Column(String, nullable=True)  # comma-separated: "PEQUEÑO,MEDIANO,GRANDE"
    can_administer_medication = Column(Boolean, default=False)
    specialization = Column(String, nullable=True)  # only meaningful for ESPECIALIZADO

    # RNF 3.1: identity verification gate before the profile is public
    id_document_url = Column(String, nullable=True)
    id_verification_status = Column(String, nullable=False, default=VerificationStatus.PENDIENTE)
    is_public = Column(Boolean, default=False)

    # RF 3.3: toggle for receiving lost-pet alerts (feature 1 integration)
    receives_alerts = Column(Boolean, default=True)

    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_caregivers_role", "role_type"),
        Index("idx_caregivers_public", "is_public"),
    )

    user = relationship("User")
    ratings = relationship("CaregiverRating", back_populates="caregiver", cascade="all, delete-orphan")


class CaregiverRating(Base):
    """A verified review left by a pet owner (RF 3.4)."""

    __tablename__ = "caregiver_ratings"

    id = Column(String, primary_key=True)
    caregiver_id = Column(String, ForeignKey("caregivers.id"), nullable=False, index=True)
    rater_id = Column(String, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    caregiver = relationship("Caregiver", back_populates="ratings")
