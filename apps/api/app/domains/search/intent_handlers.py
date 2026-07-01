"""Search intent handlers (Strategy pattern, OCP: RF 2.3, 2.4, 2.5).

Each handler implements a single intent. Swapping the underlying vision/matching
engine (perceptual hashing today, embeddings tomorrow) only requires a new
IImageMatcher implementation -- callers depend on IntentHandler/IImageMatcher
only (DIP), satisfying RNF 2.1 (interchangeable search engine via a stable JSON
contract).
"""

from abc import ABC, abstractmethod
from typing import List

from app.domains.catalog.models import ListingType
from app.domains.catalog.repositories import CatalogRepository
from app.domains.reports.repositories import ReportRepository
from app.domains.search.schemas import SearchResultItem
from app.infrastructure.image_matcher import IImageMatcher
from app.infrastructure.image_utils import decode_image_data_url


class IntentHandler(ABC):
    """Extension point: one implementation per SearchIntent value."""

    @abstractmethod
    async def process(self, image_url: str, metadata: dict) -> List[SearchResultItem]:
        pass


class AdoptionIntentHandler(IntentHandler):
    """RF 2.3: results exclusively from the NGO/shelter adoption catalog."""

    def __init__(self, catalog_repository: CatalogRepository, image_matcher: IImageMatcher):
        self.catalog_repository = catalog_repository
        self.image_matcher = image_matcher

    async def process(self, image_url: str, metadata: dict) -> List[SearchResultItem]:
        listings = await self.catalog_repository.get_by_type(ListingType.ADOPCION)
        query_image = decode_image_data_url(image_url)
        query_hash = self.image_matcher.compute_hash(query_image)

        results = [
            SearchResultItem(
                id=listing.id,
                title=listing.title,
                description=f"{listing.source_name} — {listing.breed or listing.species or 'mascota'}",
                image_url=listing.photo_url,
                relevance_score=(
                    self.image_matcher.similarity(query_hash, listing.photo_phash)
                    if listing.photo_phash
                    else listing.relevance_score_base
                ),
                source="adoption_catalog",
            )
            for listing in listings
        ]
        return sorted(results, key=lambda r: r.relevance_score, reverse=True)


class SalesIntentHandler(IntentHandler):
    """RF 2.4: results exclusively from legally certified commercial breeders."""

    def __init__(self, catalog_repository: CatalogRepository, image_matcher: IImageMatcher):
        self.catalog_repository = catalog_repository
        self.image_matcher = image_matcher

    async def process(self, image_url: str, metadata: dict) -> List[SearchResultItem]:
        listings = await self.catalog_repository.get_by_type(ListingType.VENTA, certified_only=True)
        query_image = decode_image_data_url(image_url)
        query_hash = self.image_matcher.compute_hash(query_image)

        results = [
            SearchResultItem(
                id=listing.id,
                title=listing.title,
                description=f"{listing.source_name} (criadero certificado) — {listing.breed or listing.species or ''}",
                image_url=listing.photo_url,
                relevance_score=(
                    self.image_matcher.similarity(query_hash, listing.photo_phash)
                    if listing.photo_phash
                    else listing.relevance_score_base
                ),
                source="certified_breeder",
            )
            for listing in listings
        ]
        return sorted(results, key=lambda r: r.relevance_score, reverse=True)


class LostPetIntentHandler(IntentHandler):
    """RF 2.5: contrast the uploaded photo against active lost-pet reports."""

    def __init__(self, report_search_repository: ReportRepository, image_matcher: IImageMatcher):
        self.report_search_repository = report_search_repository
        self.image_matcher = image_matcher

    async def process(self, image_url: str, metadata: dict) -> List[SearchResultItem]:
        active_reports = await self.report_search_repository.get_active()
        query_image = decode_image_data_url(image_url)
        query_hash = self.image_matcher.compute_hash(query_image)

        results = []
        for report in active_reports:
            pet_hash = report.pet.photo_phash if report.pet else None
            # No hash available (e.g. pet registered before this column existed): show
            # the report with a 0.0 score rather than hiding a legitimate active alert.
            score = self.image_matcher.similarity(query_hash, pet_hash) if pet_hash else 0.0
            results.append(
                SearchResultItem(
                    id=report.id,
                    title=f"Reporte activo #{report.id[:8]}",
                    description=report.description,
                    image_url=report.pet.photo_url if report.pet else None,
                    relevance_score=score,
                    source="lost_reports",
                    url=f"/reports/{report.id}",
                )
            )

        return sorted(results, key=lambda r: r.relevance_score, reverse=True)
