"""Image search domain service (SRP + OCP via intent handler dictionary)."""

from typing import Dict, Optional

from app.config import get_settings
from app.domains.search.intent_handlers import IntentHandler
from app.domains.search.models import SearchIntent, SearchStatus
from app.domains.search.repositories import ImageSearchRepository
from app.domains.search.schemas import ImageSearchRequest, ImageSearchResponse, SearchResultItem
from app.infrastructure.timing import log_slow_operation
from app.shared.exceptions import NotFoundError, ValidationError

settings = get_settings()


class ImageSearchService:
    """Dispatches an image search to the handler matching the chosen intent."""

    def __init__(self, repository: ImageSearchRepository, handlers: Dict[SearchIntent, IntentHandler]):
        self.repository = repository
        self.handlers = handlers

    async def search(self, user_id: Optional[str], request: ImageSearchRequest) -> ImageSearchResponse:
        """RF 2.1/2.2: single entry point; intent determines which catalog is searched."""
        handler = self.handlers.get(request.intent)
        if not handler:
            raise ValidationError(f"Unsupported intent: {request.intent}")

        search_log = await self.repository.create(user_id, request.image_url, request.intent)

        try:
            async with log_slow_operation("image_search", settings.IMAGE_SEARCH_TIMEOUT_SECONDS):
                results = await handler.process(request.image_url, request.metadata)
            updated = await self.repository.update_results(search_log.id, results, SearchStatus.COMPLETADO)
        except Exception:
            await self.repository.update_results(search_log.id, [], SearchStatus.ERROR)
            raise

        return ImageSearchResponse(
            id=updated.id,
            intent=updated.intent,
            status=updated.status,
            results=[SearchResultItem(**r) for r in (updated.results or [])],
            created_at=str(updated.created_at),
        )

    async def get_search(self, search_id: str) -> ImageSearchResponse:
        search = await self.repository.get_by_id(search_id)
        if not search:
            raise NotFoundError(f"Search {search_id} not found")

        return ImageSearchResponse(
            id=search.id,
            intent=search.intent,
            status=search.status,
            results=[SearchResultItem(**r) for r in (search.results or [])],
            created_at=str(search.created_at),
        )
