"""Pet domain services (SRP)."""

from typing import List

from app.domains.pets.repositories import PetRepository
from app.domains.pets.schemas import PetCreate, PetUpdate, PetResponse
from app.infrastructure.image_matcher import IImageMatcher
from app.infrastructure.image_utils import decode_image_data_url
from app.shared.exceptions import NotFoundError, ForbiddenError


class PetService:
    """Pet service for business logic."""

    def __init__(self, repository: PetRepository, image_matcher: IImageMatcher):
        self.repository = repository
        self.image_matcher = image_matcher

    async def create_pet(self, owner_id: str, pet_data: PetCreate) -> PetResponse:
        """RF 2.1: validates the photo is JPEG/PNG; RF 2.5: caches its perceptual
        hash so image search can compare against active reports without
        re-decoding every pet photo on every search."""
        image = decode_image_data_url(pet_data.photo_url)
        photo_phash = self.image_matcher.compute_hash(image)
        db_pet = await self.repository.create(owner_id, pet_data, photo_phash)
        return PetResponse.from_orm(db_pet)

    async def get_pet(self, pet_id: str) -> PetResponse:
        pet = await self.repository.get_by_id(pet_id)
        if not pet:
            raise NotFoundError(f"Pet {pet_id} not found")
        return PetResponse.from_orm(pet)

    async def get_my_pets(self, owner_id: str) -> List[PetResponse]:
        pets = await self.repository.get_by_owner(owner_id)
        return [PetResponse.from_orm(p) for p in pets]

    async def update_pet(self, pet_id: str, owner_id: str, data: PetUpdate) -> PetResponse:
        pet = await self.repository.get_by_id(pet_id)
        if not pet:
            raise NotFoundError(f"Pet {pet_id} not found")
        if pet.owner_id != owner_id:
            raise ForbiddenError("You do not own this pet")

        photo_phash = None
        if data.photo_url is not None:
            image = decode_image_data_url(data.photo_url)
            photo_phash = self.image_matcher.compute_hash(image)

        updated = await self.repository.update(pet_id, data, photo_phash)
        return PetResponse.from_orm(updated)

    async def delete_pet(self, pet_id: str, owner_id: str) -> None:
        pet = await self.repository.get_by_id(pet_id)
        if not pet:
            raise NotFoundError(f"Pet {pet_id} not found")
        if pet.owner_id != owner_id:
            raise ForbiddenError("You do not own this pet")

        await self.repository.delete(pet_id)
