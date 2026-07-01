"""Image search domain routes."""

from typing import Optional

from fastapi import APIRouter, Depends

from app.core.dependencies import get_image_search_service, get_current_user_optional
from app.domains.search.schemas import ImageSearchRequest, ImageSearchResponse
from app.domains.search.services import ImageSearchService
from app.domains.users.schemas import UserResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=ImageSearchResponse)
async def search_by_image(
    request: ImageSearchRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    service: ImageSearchService = Depends(get_image_search_service),
):
    """RF 2.1/2.2: single endpoint, intent determines Adopción/Venta/Verificar Pérdida."""
    user_id = current_user.id if current_user else None
    return await service.search(user_id, request)


@router.get("/{search_id}", response_model=ImageSearchResponse)
async def get_search(
    search_id: str,
    service: ImageSearchService = Depends(get_image_search_service),
):
    """Retrieve a previously executed search by ID."""
    return await service.get_search(search_id)
