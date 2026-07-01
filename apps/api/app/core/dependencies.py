"""Dependency Injection container for FastAPI."""

from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.caregivers.repositories import CaregiverRepository, CaregiverRatingRepository
from app.domains.caregivers.services import CaregiverService, CaregiverRatingService
from app.domains.catalog.repositories import CatalogRepository
from app.domains.notifications.repositories import (
    NotificationRepository,
    NotificationPreferenceRepository,
)
from app.domains.notifications.services import AlertDispatcher, NotificationService
from app.domains.pets.repositories import PetRepository
from app.domains.pets.services import PetService
from app.domains.reports.repositories import ReportRepository
from app.domains.reports.services import ReportService
from app.domains.search.intent_handlers import AdoptionIntentHandler, SalesIntentHandler, LostPetIntentHandler
from app.domains.search.models import SearchIntent
from app.domains.search.repositories import ImageSearchRepository
from app.domains.search.services import ImageSearchService
from app.domains.sightings.repositories import SightingRepository
from app.domains.sightings.services import SightingService
from app.domains.users.models import UserRole
from app.domains.users.repositories import UserRepository
from app.domains.users.schemas import UserResponse
from app.domains.users.services import UserService
from app.infrastructure.auth import decode_access_token
from app.infrastructure.database import get_db
from app.infrastructure.geo import GeospatialService
from app.infrastructure.image_matcher import IImageMatcher, PerceptualHashMatcher
from app.infrastructure.notification_channels import ConsoleChannel
from app.shared.exceptions import ForbiddenError

security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Users / Auth
# ---------------------------------------------------------------------------


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Require a valid JWT; raises 401 if absent or invalid."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return await service.get_user(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    service: UserService = Depends(get_user_service),
) -> Optional[UserResponse]:
    """RF 1.3 / RF 2.1: allow anonymous citizens. Returns None instead of raising."""
    if not credentials:
        return None

    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        return None

    try:
        return await service.get_user(payload["sub"])
    except Exception:
        return None


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Require the caller's role to be ADMIN (RNF 3.1: gate caregiver verification review)."""
    if current_user.role != UserRole.ADMIN.value:
        raise ForbiddenError("Admin access required")
    return current_user


# ---------------------------------------------------------------------------
# Infrastructure singletons
# ---------------------------------------------------------------------------

_geo_service = GeospatialService()
_image_matcher = PerceptualHashMatcher()

_channels = {
    "console": ConsoleChannel(),
}


def get_geo_service() -> GeospatialService:
    return _geo_service


def get_image_matcher() -> IImageMatcher:
    return _image_matcher


# ---------------------------------------------------------------------------
# Notifications / Alerts
# ---------------------------------------------------------------------------


async def get_notification_repository(db: AsyncSession = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)


async def get_notification_preference_repository(
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferenceRepository:
    return NotificationPreferenceRepository(db)


async def get_alert_dispatcher(
    preference_repository: NotificationPreferenceRepository = Depends(get_notification_preference_repository),
    notification_repository: NotificationRepository = Depends(get_notification_repository),
    geo_service: GeospatialService = Depends(get_geo_service),
) -> AlertDispatcher:
    return AlertDispatcher(preference_repository, notification_repository, _channels, geo_service)


async def get_notification_service(
    notification_repository: NotificationRepository = Depends(get_notification_repository),
    preference_repository: NotificationPreferenceRepository = Depends(get_notification_preference_repository),
) -> NotificationService:
    return NotificationService(notification_repository, preference_repository)


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------


async def get_pet_repository(db: AsyncSession = Depends(get_db)) -> PetRepository:
    return PetRepository(db)


async def get_pet_service(
    repository: PetRepository = Depends(get_pet_repository),
    image_matcher: IImageMatcher = Depends(get_image_matcher),
) -> PetService:
    return PetService(repository, image_matcher)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


async def get_report_repository(db: AsyncSession = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db)


async def get_report_service(
    repository: ReportRepository = Depends(get_report_repository),
    alert_dispatcher: AlertDispatcher = Depends(get_alert_dispatcher),
) -> ReportService:
    return ReportService(repository, alert_dispatcher)


# ---------------------------------------------------------------------------
# Sightings
# ---------------------------------------------------------------------------


async def get_sighting_repository(db: AsyncSession = Depends(get_db)) -> SightingRepository:
    return SightingRepository(db)


async def get_sighting_service(
    repository: SightingRepository = Depends(get_sighting_repository),
    report_repository: ReportRepository = Depends(get_report_repository),
    alert_dispatcher: AlertDispatcher = Depends(get_alert_dispatcher),
) -> SightingService:
    return SightingService(repository, report_repository, alert_dispatcher)


# ---------------------------------------------------------------------------
# Caregivers
# ---------------------------------------------------------------------------


async def get_caregiver_repository(db: AsyncSession = Depends(get_db)) -> CaregiverRepository:
    return CaregiverRepository(db)


async def get_caregiver_rating_repository(db: AsyncSession = Depends(get_db)) -> CaregiverRatingRepository:
    return CaregiverRatingRepository(db)


async def get_caregiver_service(
    repository: CaregiverRepository = Depends(get_caregiver_repository),
    preference_repository: NotificationPreferenceRepository = Depends(get_notification_preference_repository),
) -> CaregiverService:
    return CaregiverService(repository, preference_repository)


async def get_caregiver_rating_service(
    repository: CaregiverRatingRepository = Depends(get_caregiver_rating_repository),
    caregiver_repository: CaregiverRepository = Depends(get_caregiver_repository),
    report_repository: ReportRepository = Depends(get_report_repository),
) -> CaregiverRatingService:
    return CaregiverRatingService(repository, caregiver_repository, report_repository)


# ---------------------------------------------------------------------------
# Image Search
# ---------------------------------------------------------------------------


async def get_image_search_repository(db: AsyncSession = Depends(get_db)) -> ImageSearchRepository:
    return ImageSearchRepository(db)


async def get_catalog_repository(db: AsyncSession = Depends(get_db)) -> CatalogRepository:
    return CatalogRepository(db)


async def get_image_search_service(
    repository: ImageSearchRepository = Depends(get_image_search_repository),
    report_repository: ReportRepository = Depends(get_report_repository),
    catalog_repository: CatalogRepository = Depends(get_catalog_repository),
    image_matcher: IImageMatcher = Depends(get_image_matcher),
) -> ImageSearchService:
    handlers = {
        SearchIntent.ADOPCION: AdoptionIntentHandler(catalog_repository, image_matcher),
        SearchIntent.VENTA: SalesIntentHandler(catalog_repository, image_matcher),
        SearchIntent.VERIFICAR_PERDIDA: LostPetIntentHandler(report_repository, image_matcher),
    }
    return ImageSearchService(repository, handlers)
