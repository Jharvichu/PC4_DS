"""Lost pet report domain schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.domains.reports.models import ReportStatus


class ReportCreate(BaseModel):
    """Schema for report creation (RF 1.1, RF 1.2)."""

    pet_id: str
    last_seen_latitude: float = Field(..., ge=-90, le=90)
    last_seen_longitude: float = Field(..., ge=-180, le=180)
    last_seen_address: Optional[str] = None
    description: str = Field(..., min_length=10, max_length=1000)
    alert_radius_km: float = Field(default=5.0, gt=0, le=50)
    contact_is_anonymous: bool = True

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("description cannot be blank")
        return v


class ReportStatusUpdate(BaseModel):
    """Schema for updating a report's status."""

    status: ReportStatus


class ReportResponse(BaseModel):
    """Full report response (for the owner)."""

    id: str
    pet_id: str
    owner_id: str
    status: str
    last_seen_latitude: float
    last_seen_longitude: float
    last_seen_address: Optional[str] = None
    last_seen_date: datetime
    alert_radius_km: float
    description: Optional[str] = None
    contact_is_anonymous: bool
    created_at: datetime
    found_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportPublicResponse(BaseModel):
    """Anonymized report response for citizens (RNF 1.2: owner identity hidden)."""

    id: str
    pet_id: str
    status: str
    last_seen_latitude: float
    last_seen_longitude: float
    last_seen_address: Optional[str] = None
    last_seen_date: datetime
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
