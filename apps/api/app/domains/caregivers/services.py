"""Caregiver domain services (SRP: registration, restrictions, verification, ratings)."""

from typing import List, Optional

from app.domains.caregivers.models import VerificationStatus
from app.domains.caregivers.repositories import CaregiverRepository, CaregiverRatingRepository
from app.domains.caregivers.role_strategies import get_role_strategy
from app.domains.caregivers.schemas import (
    CaregiverRegister,
    CaregiverRestrictionsUpdate,
    CaregiverResponse,
    CaregiverRatingCreate,
    CaregiverRatingResponse,
    IdentityDocumentSubmit,
)
from app.domains.notifications.repositories import NotificationPreferenceRepository
from app.domains.reports.repositories import ReportRepository
from app.shared.exceptions import NotFoundError, ForbiddenError, ConflictError, BusinessLogicError


class CaregiverService:
    """Registration, restrictions, and alert-toggle logic for caregivers."""

    def __init__(self, repository: CaregiverRepository, preference_repository: NotificationPreferenceRepository):
        self.repository = repository
        self.preference_repository = preference_repository

    async def register(self, user_id: str, data: CaregiverRegister) -> CaregiverResponse:
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            raise ConflictError("User is already registered as a caregiver")

        caregiver = await self.repository.create(user_id, data)
        return CaregiverResponse.from_orm(caregiver)

    async def get_by_id(self, caregiver_id: str) -> CaregiverResponse:
        caregiver = await self.repository.get_by_id(caregiver_id)
        if not caregiver:
            raise NotFoundError(f"Caregiver {caregiver_id} not found")
        return CaregiverResponse.from_orm(caregiver)

    async def get_my_profile(self, user_id: str) -> CaregiverResponse:
        caregiver = await self.repository.get_by_user_id(user_id)
        if not caregiver:
            raise NotFoundError("Caregiver profile not found for this user")
        return CaregiverResponse.from_orm(caregiver)

    async def update_restrictions(
        self, user_id: str, data: CaregiverRestrictionsUpdate
    ) -> CaregiverResponse:
        """RF 3.2: define service restrictions (species, sizes, medication)."""
        caregiver = await self.repository.get_by_user_id(user_id)
        if not caregiver:
            raise NotFoundError("Caregiver profile not found for this user")

        updated = await self.repository.update(caregiver.id, data.dict(exclude_unset=True))
        return CaregiverResponse.from_orm(updated)

    async def toggle_alerts(self, user_id: str, receives_alerts: bool) -> CaregiverResponse:
        """RF 3.3: toggle whether this caregiver receives lost-pet alerts.

        This flips the caregiver-facing flag *and* the underlying
        NotificationPreference.alerts_active used by AlertDispatcher, so the
        toggle actually gates delivery instead of being purely informational.
        """
        caregiver = await self.repository.get_by_user_id(user_id)
        if not caregiver:
            raise NotFoundError("Caregiver profile not found for this user")

        updated = await self.repository.update(caregiver.id, {"receives_alerts": receives_alerts})
        await self.preference_repository.upsert(user_id, {"alerts_active": receives_alerts})
        return CaregiverResponse.from_orm(updated)

    async def submit_identity_document(self, user_id: str, data: IdentityDocumentSubmit) -> CaregiverResponse:
        """RNF 3.1: submit ID document; profile stays private until approved."""
        caregiver = await self.repository.get_by_user_id(user_id)
        if not caregiver:
            raise NotFoundError("Caregiver profile not found for this user")

        updated = await self.repository.update(
            caregiver.id,
            {
                "id_document_url": data.document_url,
                "id_verification_status": VerificationStatus.PENDIENTE,
                "is_public": False,
            },
        )
        return CaregiverResponse.from_orm(updated)

    async def review_verification(self, caregiver_id: str, status: VerificationStatus) -> CaregiverResponse:
        """RNF 3.1: approve/reject identity document. Only APROBADO makes the profile public."""
        caregiver = await self.repository.get_by_id(caregiver_id)
        if not caregiver:
            raise NotFoundError(f"Caregiver {caregiver_id} not found")
        if not caregiver.id_document_url:
            raise BusinessLogicError("No identity document submitted yet")

        updated = await self.repository.update(
            caregiver_id,
            {
                "id_verification_status": status,
                "is_public": status == VerificationStatus.APROBADO,
            },
        )
        return CaregiverResponse.from_orm(updated)

    async def list_public_caregivers(
        self, role_type: Optional[str] = None, species: Optional[str] = None
    ) -> List[CaregiverResponse]:
        """List verified public caregivers, optionally filtered by role/species (LSP via strategies)."""
        caregivers = await self.repository.list_public(role_type)

        if species:
            caregivers = [c for c in caregivers if get_role_strategy(c.role_type).can_accept_species(c, species)]

        return [CaregiverResponse.from_orm(c) for c in caregivers]


class CaregiverRatingService:
    """RF 3.4: verified reviews and average rating calculation."""

    def __init__(
        self,
        repository: CaregiverRatingRepository,
        caregiver_repository: CaregiverRepository,
        report_repository: ReportRepository,
    ):
        self.repository = repository
        self.caregiver_repository = caregiver_repository
        self.report_repository = report_repository

    async def add_rating(self, rater_id: str, caregiver_id: str, data: CaregiverRatingCreate) -> CaregiverRatingResponse:
        """RF 3.4: only the owner of the cited report can leave a 'verified' review."""
        caregiver = await self.caregiver_repository.get_by_id(caregiver_id)
        if not caregiver:
            raise NotFoundError(f"Caregiver {caregiver_id} not found")

        report = await self.report_repository.get_by_id(data.report_id)
        if not report:
            raise NotFoundError(f"Report {data.report_id} not found")
        if report.owner_id != rater_id:
            raise ForbiddenError("Only the report's owner can rate a caregiver for it")

        rating = await self.repository.create(caregiver_id, rater_id, data.score, data.comment)

        # Recalculate rolling average (SRP: this service owns the rating math)
        all_ratings = await self.repository.get_by_caregiver(caregiver_id)
        new_average = sum(r.score for r in all_ratings) / len(all_ratings)

        await self.caregiver_repository.update(
            caregiver_id, {"rating_average": round(new_average, 2), "rating_count": len(all_ratings)}
        )

        return CaregiverRatingResponse.from_orm(rating)

    async def get_ratings(self, caregiver_id: str) -> List[CaregiverRatingResponse]:
        ratings = await self.repository.get_by_caregiver(caregiver_id)
        return [CaregiverRatingResponse.from_orm(r) for r in ratings]
