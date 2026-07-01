"""Image search domain schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.domains.search.models import SearchIntent


class ImageSearchRequest(BaseModel):
    """Schema for a search request (RF 2.1, RF 2.2)."""

    image_url: str
    intent: SearchIntent
    # RNF 2.1: standard metadata envelope, decoupled from any specific vision engine
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResultItem(BaseModel):
    """A single search result entry (RNF 2.1: stable JSON shape)."""

    id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    relevance_score: float = 0.0
    source: str  # "adoption_catalog" | "certified_breeder" | "lost_reports"
    url: Optional[str] = None


class ImageSearchResponse(BaseModel):
    """Search response returned to the client."""

    id: str
    intent: str
    status: str
    results: List[SearchResultItem]
    created_at: str

    class Config:
        from_attributes = True
