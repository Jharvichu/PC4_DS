"""Pet domain routes."""

from typing import List

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_pet_service, get_current_user
from app.domains.pets.schemas import PetCreate, PetUpdate, PetResponse
from app.domains.pets.services import PetService
from app.domains.users.schemas import UserResponse

router = APIRouter(prefix="/pets", tags=["pets"])


@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
async def create_pet(
    pet_data: PetCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    """Register a new pet for the current user."""
    return await service.create_pet(current_user.id, pet_data)


@router.get("/me", response_model=List[PetResponse])
async def get_my_pets(
    current_user: UserResponse = Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    """Get all pets belonging to the current user."""
    return await service.get_my_pets(current_user.id)


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: str,
    service: PetService = Depends(get_pet_service),
):
    """Get pet by ID."""
    return await service.get_pet(pet_id)


@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: str,
    pet_data: PetUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    """Update a pet owned by the current user."""
    return await service.update_pet(pet_id, current_user.id, pet_data)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(
    pet_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: PetService = Depends(get_pet_service),
):
    """Delete a pet owned by the current user."""
    await service.delete_pet(pet_id, current_user.id)
