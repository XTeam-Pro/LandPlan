"""Add new services, categories, and model fields

Revision ID: 003_add_new_services_and_fields
Revises: 002_seed_categories_services
Create Date: 2024-03-24

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '003_add_new_services_and_fields'
down_revision = '002_seed_categories_services'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new columns to lands, companies, users; add new services."""

    # -- Land model new columns --
    op.add_column('lands', sa.Column('cadastral_number', sa.String(50), nullable=True))
    op.add_column('lands', sa.Column('photos', sa.JSON(), nullable=True, server_default='[]'))
    op.add_column('lands', sa.Column('listing_type', sa.String(50), nullable=False, server_default='import'))
    op.add_column('lands', sa.Column('has_building', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('lands', sa.Column('contact_phone', sa.String(20), nullable=True))
    op.add_column('lands', sa.Column('owner_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))

    op.create_index('ix_lands_cadastral_number', 'lands', ['cadastral_number'])
    op.create_index('ix_lands_listing_type', 'lands', ['listing_type'])
    op.create_index('ix_lands_has_building', 'lands', ['has_building'])

    # Make source_id nullable (user listings don't have a source)
    op.alter_column('lands', 'source_id', nullable=True)

    # -- Company model new column --
    op.add_column('companies', sa.Column('display_order', sa.Integer(), nullable=False, server_default='1000'))
    op.create_index('ix_companies_display_order', 'companies', ['display_order'])

    # -- New categories and services --
    now = datetime.utcnow()

    categories_table = sa.table(
        'categories',
        sa.column('slug', sa.String),
        sa.column('name', sa.String),
        sa.column('icon', sa.String),
        sa.column('sort_order', sa.Integer),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
    )

    services_table = sa.table(
        'services',
        sa.column('category_id', sa.Integer),
        sa.column('slug', sa.String),
        sa.column('name', sa.String),
        sa.column('short_description', sa.String),
        sa.column('is_required_default', sa.Boolean),
        sa.column('priority', sa.Integer),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
    )

    # Add "Газификация" category
    op.execute(
        categories_table.insert().values(
            slug='gasification',
            name='Газификация',
            icon='flame',
            sort_order=15,
            is_active=True,
            created_at=now,
        )
    )

    # Add "Агентства недвижимости" category
    op.execute(
        categories_table.insert().values(
            slug='real_estate_agencies',
            name='Агентства недвижимости',
            icon='building',
            sort_order=16,
            is_active=True,
            created_at=now,
        )
    )

    # Add "Электроснабжение" category
    op.execute(
        categories_table.insert().values(
            slug='electricity',
            name='Электроснабжение',
            icon='zap',
            sort_order=17,
            is_active=True,
            created_at=now,
        )
    )

    # Gasification services (category 15)
    op.execute(
        services_table.insert().values(
            category_id=15,
            slug='gas_connection',
            name='Подключение газа',
            short_description='Подключение к газовой сети',
            is_required_default=False,
            priority=2,
            is_active=True,
            created_at=now,
        )
    )
    op.execute(
        services_table.insert().values(
            category_id=15,
            slug='gas_project',
            name='Проект газификации',
            short_description='Разработка проекта газификации участка',
            is_required_default=False,
            priority=2,
            is_active=True,
            created_at=now,
        )
    )
    op.execute(
        services_table.insert().values(
            category_id=15,
            slug='gas_installation',
            name='Монтаж газового оборудования',
            short_description='Установка и подключение газового оборудования',
            is_required_default=False,
            priority=2,
            is_active=True,
            created_at=now,
        )
    )

    # Real estate agency services (category 16)
    op.execute(
        services_table.insert().values(
            category_id=16,
            slug='land_search',
            name='Поиск участка',
            short_description='Помощь в поиске подходящего земельного участка',
            is_required_default=False,
            priority=3,
            is_active=True,
            created_at=now,
        )
    )
    op.execute(
        services_table.insert().values(
            category_id=16,
            slug='deal_support',
            name='Сопровождение сделки',
            short_description='Полное сопровождение сделки купли-продажи',
            is_required_default=False,
            priority=2,
            is_active=True,
            created_at=now,
        )
    )

    # Electricity services (category 17)
    op.execute(
        services_table.insert().values(
            category_id=17,
            slug='electricity_connection',
            name='Подключение электричества',
            short_description='Подключение к электросети',
            is_required_default=False,
            priority=2,
            is_active=True,
            created_at=now,
        )
    )
    op.execute(
        services_table.insert().values(
            category_id=17,
            slug='electrical_project',
            name='Проект электроснабжения',
            short_description='Разработка проекта электроснабжения',
            is_required_default=False,
            priority=2,
            is_active=True,
            created_at=now,
        )
    )

    # Update "Оформление договора" → "Полное юридическое сопровождение"
    op.execute(
        sa.text(
            "UPDATE services SET name = 'Полное юридическое сопровождение', "
            "short_description = 'Комплексное юридическое сопровождение сделки с земельным участком', "
            "slug = 'full_legal_support' "
            "WHERE slug = 'contract_drafting'"
        )
    )


def downgrade() -> None:
    """Remove added columns and services."""
    # Revert legal service name
    op.execute(
        sa.text(
            "UPDATE services SET name = 'Оформление договора', "
            "short_description = 'Подготовка и оформление договора', "
            "slug = 'contract_drafting' "
            "WHERE slug = 'full_legal_support'"
        )
    )

    # Remove new services
    op.execute(sa.text("DELETE FROM services WHERE category_id >= 15"))
    op.execute(sa.text("DELETE FROM categories WHERE slug IN ('gasification', 'real_estate_agencies', 'electricity')"))

    # Remove new columns
    op.drop_index('ix_companies_display_order', 'companies')
    op.drop_column('companies', 'display_order')

    op.drop_index('ix_lands_has_building', 'lands')
    op.drop_index('ix_lands_listing_type', 'lands')
    op.drop_index('ix_lands_cadastral_number', 'lands')
    op.drop_column('lands', 'owner_user_id')
    op.drop_column('lands', 'contact_phone')
    op.drop_column('lands', 'has_building')
    op.drop_column('lands', 'listing_type')
    op.drop_column('lands', 'photos')
    op.drop_column('lands', 'cadastral_number')
