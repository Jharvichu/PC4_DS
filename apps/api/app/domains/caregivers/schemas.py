"""Caregiver domain schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.domains.caregivers.models import CaregiverRoleType, VerificationStatus


class CaregiverRegister(BaseModel):
    """Schema for registering as a caregiver (RF 3.1)."""

    role_type: CaregiverRoleType
    accepted_species: Optional[List[str]] = None
    accepted_sizes: Optional[List[str]] = None
    can_administer_medication: bool = False
    specialization: Optional[str] = None

    @field_validator("specialization")
    @classmethod
    def specialization_requires_role(cls, v, info):
        role = info.data.get("role_type")
        if role == CaregiverRoleType.ESPECIALIZADO and not v:
            raise ValueError("specialization is required for ESPECIALIZADO caregivers")
        return v


class CaregiverRestrictionsUpdate(BaseModel):
    """RF 3.2: update service restrictions."""

    accepted_species: Optional[List[str]] = None
    accepted_sizes: Optional[List[str]] = None
    can_administer_medication: Optional[bool] = None


class CaregiverAlertToggle(BaseModel):
    """RF 3.3: toggle alert reception."""

    receives_alerts: bool


class IdentityDocumentSubmit(BaseModel):
    """RNF 3.1: submit identity document for verification."""

    document_url: str


class VerificationReview(BaseModel):
    """Admin action to approve/reject a submitted identity document."""

    status: VerificationStatus


class CaregiverRatingCreate(BaseModel):
    """RF 3.4: submit a verified review."""

    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=500)
    report_id: str  # proves the reviewer actually used this caregiver for a real report


class CaregiverRatingResponse(BaseModel):
    id: str
    caregiver_id: str
    score: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CaregiverResponse(BaseModel):
    """Public caregiver profile."""

    id: str
    user_id: str
    role_type: str
    accepted_species: Optional[str] = None
    accepted_sizes: Optional[str] = None
    can_administer_medication: bool
    specialization: Optional[str] = None
    id_verification_status: str
    is_public: bool
    receives_alerts: bool
    rating_average: float
    rating_count: int
    created_at: datetime

    class Config:
        from_attributes = True
