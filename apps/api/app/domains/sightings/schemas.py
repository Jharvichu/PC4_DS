"""Sighting domain schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.domains.sightings.models import ConfidenceLevel


class SightingCreate(BaseModel):
    """Schema for reporting a sighting (RF 1.3)."""

    report_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    photo_url: str
    description: Optional[str] = None
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIA


class SightingResponse(BaseModel):
    """Sighting response. Citizen identity is not exposed to the owner (RNF 1.2)."""

    id: str
    report_id: str
    latitude: float
    longitude: float
    photo_url: str
    description: Optional[str] = None
    confidence_level: str
    created_at: datetime

    class Config:
        from_attributes = True
