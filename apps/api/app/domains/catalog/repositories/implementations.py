"""Catalog repository implementation."""

from typing import List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.catalog.models import CatalogListing


class CatalogRepository:
    """Concrete catalog repository for adoption/sales listing queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_type(self, listing_type: str, certified_only: bool = False) -> List[CatalogListing]:
        conditions = [CatalogListing.listing_type == listing_type]
        if certified_only:
            conditions.append(CatalogListing.is_certified.is_(True))

        stmt = select(CatalogListing).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
