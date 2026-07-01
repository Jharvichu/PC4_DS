"""Pet domain models."""

from enum import Enum

from sqlalchemy import Column, String, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class PetSpecies(str, Enum):
    """Pet species enumeration."""

    PERRO = "PERRO"
    GATO = "GATO"
    OTRO = "OTRO"


class Pet(Base):
    """Pet model."""

    __tablename__ = "pets"

    id = Column(String, primary_key=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    species = Column(String, nullable=False, default=PetSpecies.OTRO)
    breed = Column(String, nullable=True)
    photo_url = Column(String, nullable=False)  # RF 1.1: required to report a pet as lost
    photo_phash = Column(String, nullable=True)  # perceptual hash for image search matching (RF 2.5)
    description = Column(String, nullable=True)
    microchip_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_pets_owner", "owner_id"),
        Index("idx_pets_species", "species"),
    )

    owner = relationship("User", back_populates="pets")
    reports = relationship("Report", back_populates="pet", cascade="all, delete-orphan")
