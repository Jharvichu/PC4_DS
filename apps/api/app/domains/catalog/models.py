"""Adoption/sales catalog domain models (RF 2.3, RF 2.4)."""

from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, String, func

from app.infrastructure.database import Base


class ListingType(str, Enum):
    """Which search intent this listing belongs to."""

    ADOPCION = "ADOPCION"
    VENTA = "VENTA"


class CatalogListing(Base):
    """A single adoption (NGO/shelter) or sales (breeder) catalog entry."""

    __tablename__ = "catalog_listings"

    id = Column(String, primary_key=True)
    listing_type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    species = Column(String, nullable=True)
    breed = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    photo_phash = Column(String, nullable=True)
    source_name = Column(String, nullable=False)  # NGO/shelter or breeder name
    is_certified = Column(Boolean, nullable=False, default=False)  # RF 2.4: only relevant for VENTA
    # Flat baseline score shown when there's no photo_phash to compare against (seed data).
    relevance_score_base = Column(Float, nullable=False, default=0.3)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
