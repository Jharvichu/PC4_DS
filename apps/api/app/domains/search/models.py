"""Image search domain models (RF 2.1-2.5)."""

from enum import Enum

from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, func

from app.infrastructure.database import Base


class SearchIntent(str, Enum):
    """User's intent for an image search (RF 2.2)."""

    ADOPCION = "ADOPCION"
    VENTA = "VENTA"
    VERIFICAR_PERDIDA = "VERIFICAR_PERDIDA"


class SearchStatus(str, Enum):
    """Processing status of a search request."""

    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"


class ImageSearch(Base):
    """A logged image search request and its results."""

    __tablename__ = "image_searches"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    image_url = Column(String, nullable=False)
    intent = Column(String, nullable=False)
    # RNF 2.1: results stored as standard JSON so the underlying search engine
    # (mock today, Vision API / Rekognition tomorrow) can change transparently.
    results = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default=SearchStatus.PROCESANDO)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
