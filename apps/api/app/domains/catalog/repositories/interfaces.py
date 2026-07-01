"""Catalog repository interface (DIP)."""

from abc import ABC, abstractmethod
from typing import List

from app.domains.catalog.models import CatalogListing


class ICatalogRepository(ABC):
    """Interface for catalog listing queries (RF 2.3, RF 2.4)."""

    @abstractmethod
    async def get_by_type(self, listing_type: str, certified_only: bool = False) -> List[CatalogListing]:
        pass
