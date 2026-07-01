"""Caregiver domain routes."""

from typing import List, Optional

from fastapi import APIRouter, Depends, status

from app.core.dependencies import (
    get_caregiver_service,
    get_caregiver_rating_service,
    get_current_admin_user,
    get_current_user,
)
from app.domains.caregivers.schemas import (
    CaregiverRegister,
    CaregiverRestrictionsUpdate,
    CaregiverAlertToggle,
    IdentityDocumentSubmit,
    VerificationReview,
    CaregiverRatingCreate,
    CaregiverRatingResponse,
    CaregiverResponse,
)
from app.domains.caregivers.services import CaregiverService, CaregiverRatingService
from app.domains.users.schemas import UserResponse

router = APIRouter(prefix="/caregivers", tags=["caregivers"])


@router.post("/", response_model=CaregiverResponse, status_code=status.HTTP_201_CREATED)
async def register_caregiver(
    data: CaregiverRegister,
    current_user: UserResponse = Depends(get_current_user),
    service: CaregiverService = Depends(get_caregiver_service),
):
    """Register the current user as a caregiver (RF 3.1)."""
    return await service.register(current_user.id, data)


@router.get("/", response_model=List[CaregiverResponse])
async def list_caregivers(
    role_type: Optional[str] = None,
    species: Optional[str] = None,
    service: CaregiverService = Depends(get_caregiver_service),
):
    """List verified, public caregivers, optionally filtered by role/species."""
    return await service.list_public_caregivers(role_type, species)


@router.get("/me", response_model=CaregiverResponse)
async def get_my_caregiver_profile(
    current_user: UserResponse = Depends(get_current_user),
    service: CaregiverService = Depends(get_caregiver_service),
):
    """Get the current user's caregiver profile."""
    return await service.get_my_profile(current_user.id)


@router.get("/{caregiver_id}", response_model=CaregiverResponse)
async def get_caregiver(
    caregiver_id: str,
    service: CaregiverService = Depends(get_caregiver_service),
):
    """Get a caregiver's public profile."""
    return await service.get_by_id(caregiver_id)


@router.put("/me/restrictions", response_model=CaregiverResponse)
async def update_restrictions(
    data: CaregiverRestrictionsUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: CaregiverService = Depends(get_caregiver_service),
):
    """RF 3.2: define accepted species, sizes, and medication capability."""
    return await service.update_restrictions(current_user.id, data)


@router.put("/me/alerts-toggle", response_model=CaregiverResponse)
async def toggle_alerts(
    data: CaregiverAlertToggle,
    current_user: UserResponse = Depends(get_current_user),
    service: CaregiverService = Depends(get_caregiver_service),
):
    """RF 3.3: toggle receiving lost-pet alerts."""
    return await service.toggle_alerts(current_user.id, data.receives_alerts)


@router.post("/me/identity-document", response_model=CaregiverResponse)
async def submit_identity_document(
    data: IdentityDocumentSubmit,
    current_user: UserResponse = Depends(get_current_user),
    service: CaregiverService = Depends(get_caregiver_service),
):
    """RNF 3.1: submit identity document for verification."""
    return await service.submit_identity_document(current_user.id, data)


@router.put("/{caregiver_id}/verification", response_model=CaregiverResponse)
async def review_verification(
    caregiver_id: str,
    data: VerificationReview,
    admin: UserResponse = Depends(get_current_admin_user),
    service: CaregiverService = Depends(get_caregiver_service),
):
    """RNF 3.1: admin approves/rejects a caregiver's identity document."""
    return await service.review_verification(caregiver_id, data.status)


@router.post("/{caregiver_id}/ratings", response_model=CaregiverRatingResponse, status_code=status.HTTP_201_CREATED)
async def add_rating(
    caregiver_id: str,
    data: CaregiverRatingCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: CaregiverRatingService = Depends(get_caregiver_rating_service),
):
    """RF 3.4: submit a verified review for a caregiver."""
    return await service.add_rating(current_user.id, caregiver_id, data)


@router.get("/{caregiver_id}/ratings", response_model=List[CaregiverRatingResponse])
async def get_ratings(
    caregiver_id: str,
    service: CaregiverRatingService = Depends(get_caregiver_rating_service),
):
    """Get all ratings for a caregiver."""
    return await service.get_ratings(caregiver_id)
