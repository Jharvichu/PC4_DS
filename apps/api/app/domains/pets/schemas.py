"""Pet domain schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.domains.pets.models import PetSpecies


class PetCreate(BaseModel):
    """Schema for pet creation."""

    name: str = Field(..., min_length=1, max_length=100)
    species: PetSpecies
    breed: Optional[str] = None
    photo_url: str = Field(..., min_length=1)  # RF 1.1: photo is required to report a pet as lost
    description: Optional[str] = None
    microchip_id: Optional[str] = None


class PetUpdate(BaseModel):
    """Schema for pet update."""

    name: Optional[str] = None
    breed: Optional[str] = None
    photo_url: Optional[str] = None
    description: Optional[str] = None
    microchip_id: Optional[str] = None


class PetResponse(BaseModel):
    """Schema for pet response."""

    id: str
    owner_id: str
    name: str
    species: str
    breed: Optional[str] = None
    photo_url: Optional[str] = None
    description: Optional[str] = None
    microchip_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
