"""seed catalog listings

Revision ID: 5a42b6014d69
Revises: 57f22fdb80b5
Create Date: 2026-07-01 15:52:57.731462

RF 2.3 / RF 2.4: demo adoption (NGO/shelter) and sales (breeder) catalog rows so
those search intents don't return empty results. None of these ship with a real
photo (photo_phash=NULL) since no real ONG/breeder images are available for this
academic project -- they surface with a flat relevance_score_base until real
photos are added directly to the table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a42b6014d69'
down_revision: Union[str, None] = '57f22fdb80b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

catalog_listings = sa.table(
    "catalog_listings",
    sa.column("id", sa.String),
    sa.column("listing_type", sa.String),
    sa.column("title", sa.String),
    sa.column("species", sa.String),
    sa.column("breed", sa.String),
    sa.column("photo_url", sa.String),
    sa.column("photo_phash", sa.String),
    sa.column("source_name", sa.String),
    sa.column("is_certified", sa.Boolean),
    sa.column("relevance_score_base", sa.Float),
)

SEED_ROWS = [
    {
        "id": "seed-adopcion-1",
        "listing_type": "ADOPCION",
        "title": "Firulais busca hogar",
        "species": "PERRO",
        "breed": "Mestizo",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "Refugio Patitas Felices",
        "is_certified": False,
        "relevance_score_base": 0.3,
    },
    {
        "id": "seed-adopcion-2",
        "listing_type": "ADOPCION",
        "title": "Michi busca hogar",
        "species": "GATO",
        "breed": "Mestizo",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "ONG Huellitas",
        "is_certified": False,
        "relevance_score_base": 0.3,
    },
    {
        "id": "seed-adopcion-3",
        "listing_type": "ADOPCION",
        "title": "Cachorros en adopción",
        "species": "PERRO",
        "breed": "Labrador mestizo",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "Refugio Patitas Felices",
        "is_certified": False,
        "relevance_score_base": 0.3,
    },
    {
        "id": "seed-adopcion-4",
        "listing_type": "ADOPCION",
        "title": "Gatitos en adopción",
        "species": "GATO",
        "breed": "Mestizo",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "ONG Huellitas",
        "is_certified": False,
        "relevance_score_base": 0.3,
    },
    {
        "id": "seed-venta-1",
        "listing_type": "VENTA",
        "title": "Cachorros Golden Retriever",
        "species": "PERRO",
        "breed": "Golden Retriever",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "Criadero Golden Perú",
        "is_certified": True,
        "relevance_score_base": 0.3,
    },
    {
        "id": "seed-venta-2",
        "listing_type": "VENTA",
        "title": "Gatos Persas certificados",
        "species": "GATO",
        "breed": "Persa",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "Criadero Felinos del Sur",
        "is_certified": True,
        "relevance_score_base": 0.3,
    },
    {
        "id": "seed-venta-3",
        "listing_type": "VENTA",
        "title": "Cachorros Bulldog Francés",
        "species": "PERRO",
        "breed": "Bulldog Francés",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "Criadero Bulldogs Lima",
        "is_certified": True,
        "relevance_score_base": 0.3,
    },
    {
        "id": "seed-venta-4-sin-certificar",
        "listing_type": "VENTA",
        "title": "Cachorros mestizos (sin certificar)",
        "species": "PERRO",
        "breed": "Mestizo",
        "photo_url": None,
        "photo_phash": None,
        "source_name": "Vendedor informal",
        "is_certified": False,  # deliberately not certified: proves RF 2.4's filter excludes it
        "relevance_score_base": 0.3,
    },
]


def upgrade() -> None:
    op.bulk_insert(catalog_listings, SEED_ROWS)


def downgrade() -> None:
    ids = [row["id"] for row in SEED_ROWS]
    op.execute(
        catalog_listings.delete().where(catalog_listings.c.id.in_(ids))
    )
