"""Sighting repository interfaces (DIP)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.sightings.models import Sighting
from app.domains.sightings.schemas import SightingCreate


class ISightingRepository(ABC):
    """Interface for sighting persistence."""

    @abstractmethod
    async def create(self, citizen_id: Optional[str], sighting: SightingCreate) -> Sighting:
        pass

    @abstractmethod
    async def get_by_report(self, report_id: str) -> List[Sighting]:
        pass

    @abstractmethod
    async def get_by_id(self, sighting_id: str) -> Optional[Sighting]:
        pass
