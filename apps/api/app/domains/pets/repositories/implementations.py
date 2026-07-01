"""Pet repository implementations."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pets.models import Pet
from app.domains.pets.schemas import PetCreate, PetUpdate


class PetRepository:
    """Pet repository for database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pet_id: str) -> Optional[Pet]:
        stmt = select(Pet).where(Pet.id == pet_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: str) -> List[Pet]:
        stmt = select(Pet).where(Pet.owner_id == owner_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, owner_id: str, pet: PetCreate, photo_phash: Optional[str] = None) -> Pet:
        db_pet = Pet(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            name=pet.name,
            species=pet.species,
            breed=pet.breed,
            photo_url=pet.photo_url,
            photo_phash=photo_phash,
            description=pet.description,
            microchip_id=pet.microchip_id,
        )
        self.db.add(db_pet)
        await self.db.commit()
        await self.db.refresh(db_pet)
        return db_pet

    async def update(self, pet_id: str, data: PetUpdate, photo_phash: Optional[str] = None) -> Optional[Pet]:
        pet = await self.get_by_id(pet_id)
        if not pet:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(pet, key, value)

        if photo_phash is not None:
            pet.photo_phash = photo_phash

        await self.db.commit()
        await self.db.refresh(pet)
        return pet

    async def delete(self, pet_id: str) -> bool:
        pet = await self.get_by_id(pet_id)
        if not pet:
            return False

        await self.db.delete(pet)
        await self.db.commit()
        return True
