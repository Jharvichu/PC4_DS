"""Caregiver repository interfaces (DIP, ISP: ratings segregated from CRUD)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.caregivers.models import Caregiver, CaregiverRating
from app.domains.caregivers.schemas import CaregiverRegister


class ICaregiverRepository(ABC):
    """CRUD + queries for caregiver profiles."""

    @abstractmethod
    async def get_by_id(self, caregiver_id: str) -> Optional[Caregiver]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Caregiver]:
        pass

    @abstractmethod
    async def create(self, user_id: str, data: CaregiverRegister) -> Caregiver:
        pass

    @abstractmethod
    async def update(self, caregiver_id: str, data: dict) -> Optional[Caregiver]:
        pass

    @abstractmethod
    async def list_public(self, role_type: Optional[str] = None) -> List[Caregiver]:
        pass

    @abstractmethod
    async def list_alert_subscribers(self) -> List[Caregiver]:
        """Caregivers with receives_alerts=True and a verified public profile."""
        pass


class ICaregiverRatingRepository(ABC):
    """Persistence for caregiver ratings/reviews."""

    @abstractmethod
    async def create(self, caregiver_id: str, rater_id: str, score: int, comment: Optional[str]) -> CaregiverRating:
        pass

    @abstractmethod
    async def get_by_caregiver(self, caregiver_id: str) -> List[CaregiverRating]:
        pass
