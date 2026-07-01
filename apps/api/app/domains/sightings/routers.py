"""Sighting domain routes."""

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.dependencies import get_sighting_service, get_current_user_optional
from app.domains.sightings.schemas import SightingCreate, SightingResponse
from app.domains.sightings.services import SightingService
from app.domains.users.schemas import UserResponse

router = APIRouter(prefix="/sightings", tags=["sightings"])


@router.post("/", response_model=SightingResponse, status_code=status.HTTP_201_CREATED)
async def create_sighting(
    sighting_data: SightingCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    service: SightingService = Depends(get_sighting_service),
):
    """Report a sighting of a lost pet (RF 1.3). Citizen may be anonymous.
    The owner notification (RF 1.4) is dispatched in the background."""
    citizen_id = current_user.id if current_user else None
    sighting, report_id, owner_id = await service.create_sighting(citizen_id, sighting_data)
    background_tasks.add_task(service.dispatch_sighting_notification, report_id, owner_id, sighting.id)
    return sighting


@router.get("/report/{report_id}", response_model=List[SightingResponse])
async def get_sightings_for_report(
    report_id: str,
    service: SightingService = Depends(get_sighting_service),
):
    """Get all sightings reported for a given lost-pet report."""
    return await service.get_sightings_for_report(report_id)
