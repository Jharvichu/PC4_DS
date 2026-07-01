"""User domain models."""

from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Index, func
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class UserRole(str, Enum):
    """User role enumeration."""

    CIUDADANO = "CIUDADANO"
    CUIDADOR_SOLIDARIO = "CUIDADOR_SOLIDARIO"
    CUIDADOR_PROFESIONAL = "CUIDADOR_PROFESIONAL"
    ESPECIALISTA = "ESPECIALISTA"
    ADMIN = "ADMIN"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(String, nullable=False, default=UserRole.CIUDADANO)
    location = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
    )

    # Relationships
    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="owner", cascade="all, delete-orphan")
    sightings = relationship("Sighting", back_populates="citizen", cascade="all, delete-orphan")
