"""Image search repository implementations."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.search.models import ImageSearch, SearchStatus
from app.domains.search.schemas import SearchResultItem


class ImageSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: Optional[str], image_url: str, intent: str) -> ImageSearch:
        search = ImageSearch(
            id=str(uuid.uuid4()),
            user_id=user_id,
            image_url=image_url,
            intent=intent,
            status=SearchStatus.PROCESANDO,
        )
        self.db.add(search)
        await self.db.commit()
        await self.db.refresh(search)
        return search

    async def update_results(
        self, search_id: str, results: List[SearchResultItem], status: SearchStatus
    ) -> Optional[ImageSearch]:
        stmt = select(ImageSearch).where(ImageSearch.id == search_id)
        result = await self.db.execute(stmt)
        search = result.scalar_one_or_none()
        if not search:
            return None

        search.results = [r.dict() for r in results]
        search.status = status
        await self.db.commit()
        await self.db.refresh(search)
        return search

    async def get_by_id(self, search_id: str) -> Optional[ImageSearch]:
        stmt = select(ImageSearch).where(ImageSearch.id == search_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
