"""Image search repository interfaces (DIP)."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.search.models import ImageSearch, SearchStatus
from app.domains.search.schemas import SearchResultItem


class IImageSearchRepository(ABC):
    """Persistence for logged search requests."""

    @abstractmethod
    async def create(self, user_id: Optional[str], image_url: str, intent: str) -> ImageSearch:
        pass

    @abstractmethod
    async def update_results(
        self, search_id: str, results: List[SearchResultItem], status: SearchStatus
    ) -> Optional[ImageSearch]:
        pass

    @abstractmethod
    async def get_by_id(self, search_id: str) -> Optional[ImageSearch]:
        pass
