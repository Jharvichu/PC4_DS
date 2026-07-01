"""Pet repository interfaces (DIP)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.pets.models import Pet
from app.domains.pets.schemas import PetCreate, PetUpdate


class IPetRepository(ABC):
    """Interface for pet repository operations."""

    @abstractmethod
    async def get_by_id(self, pet_id: str) -> Optional[Pet]:
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: str) -> List[Pet]:
        pass

    @abstractmethod
    async def create(self, owner_id: str, pet: PetCreate, photo_phash: Optional[str] = None) -> Pet:
        pass

    @abstractmethod
    async def update(self, pet_id: str, data: PetUpdate, photo_phash: Optional[str] = None) -> Optional[Pet]:
        pass

    @abstractmethod
    async def delete(self, pet_id: str) -> bool:
        pass
