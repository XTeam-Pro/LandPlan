"""Seed data for sources and regions

Revision ID: 003_seed_sources_and_regions
Revises: 002_seed_categories_services
Create Date: 2026-03-17

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '003_seed_sources_and_regions'
down_revision = '002_seed_categories_services'
branch_labels = None
depends_on = None


REGIONS = [
    ('Moscow', 'moscow'),
    ('Saint Petersburg', 'saint-petersburg'),
    ('Novosibirsk', 'novosibirsk'),
]

CITIES = [
    (1, 'Moscow', 'moscow'),
    (1, 'Krasnogorsk', 'krasnogorsk'),
    (2, 'Saint Petersburg', 'saint-petersburg'),
    (2, 'Pushkin', 'pushkin'),
    (3, 'Novosibirsk', 'novosibirsk'),
    (3, 'Akademgorodok', 'akademgorodok'),
]

SOURCES = [
    ('private', 'Private Listings (Mock)', {'description': 'Private land listings from classifieds platforms', 'update_frequency': 'weekly'}),
    ('bankruptcy', 'Bankruptcy Auctions (Mock)', {'description': 'Distressed property auctions from bankruptcy proceedings', 'update_frequency': 'biweekly'}),
    ('government', 'Government Sales (Mock)', {'description': 'Government-owned land for public sale', 'update_frequency': 'monthly'}),
]


def upgrade() -> None:
    """Insert seed data"""

    regions_table = sa.table(
        'regions',
        sa.column('name', sa.String),
        sa.column('slug', sa.String),
        sa.column('created_at', sa.DateTime),
    )

    cities_table = sa.table(
        'cities',
        sa.column('region_id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('slug', sa.String),
        sa.column('created_at', sa.DateTime),
    )

    sources_table = sa.table(
        'sources',
        sa.column('type', sa.String),
        sa.column('name', sa.String),
        sa.column('config', sa.JSON),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )

    now = datetime.utcnow()

    # Insert regions
    for name, slug in REGIONS:
        op.execute(
            regions_table.insert().values(
                name=name,
                slug=slug,
                created_at=now,
            )
        )

    # Insert cities
    for region_id, name, slug in CITIES:
        op.execute(
            cities_table.insert().values(
                region_id=region_id,
                name=name,
                slug=slug,
                created_at=now,
            )
        )

    # Insert sources
    for source_type, name, config in SOURCES:
        op.execute(
            sources_table.insert().values(
                type=source_type,
                name=name,
                config=config,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )


def downgrade() -> None:
    """Remove seed data"""
    op.execute("DELETE FROM sources")
    op.execute("DELETE FROM cities")
    op.execute("DELETE FROM regions")
