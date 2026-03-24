"""Seed data for categories and services

Revision ID: 002_seed_categories_services
Revises: 001_initial_schema
Create Date: 2024-03-17

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_seed_categories_services'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


CATEGORIES = [
    ('water_analysis', 'Анализ воды', 'water_analysis', 'droplet', 1),
    ('banks', 'Банки', 'banks', 'bank', 2),
    ('drilling', 'Бурение', 'drilling', 'drill', 3),
    ('geology', 'Геология', 'geology', 'mountain', 4),
    ('house_projects', 'Проекты домов', 'house_projects', 'home', 5),
    ('drainage', 'Дренаж', 'drainage', 'droplet', 6),
    ('landscaping', 'Ландшафт', 'landscaping', 'leaf', 7),
    ('cadastre', 'Кадастр', 'cadastre', 'map', 8),
    ('appraisal', 'Оценка', 'appraisal', 'percent', 9),
    ('boundaries', 'Границы участка', 'boundaries', 'box', 10),
    ('land_transfer', 'Перевод категории', 'land_transfer', 'exchange', 11),
    ('design', 'Проектирование', 'design', 'pencil', 12),
    ('construction', 'Строительство', 'construction', 'hammer', 13),
    ('legal', 'Юристы', 'legal', 'briefcase', 14),
]

SERVICES = [
    # Water Analysis (category 1)
    (1, 'water_analysis', 'Анализ воды', 'Анализ качества воды', True, 1),
    (1, 'water_drilling', 'Бурение скважины', 'Бурение скважины для воды', True, 1),
    (1, 'water_supply', 'Водоснабжение', 'Система водоснабжения', True, 2),

    # Banks (category 2)
    (2, 'bank_financing', 'Финансирование', 'Помощь с финансированием', False, 3),
    (2, 'mortgage', 'Ипотека', 'Оформление ипотеки', False, 3),

    # Drilling (category 3)
    (3, 'well_drilling', 'Бурение скважины', 'Профессиональное бурение', True, 1),
    (3, 'geothermal', 'Геотермальное бурение', 'Бурение для геотермального отопления', False, 2),

    # Geology (category 4)
    (4, 'geological_survey', 'Геологическое исследование', 'Комплексное исследование грунта', True, 1),
    (4, 'soil_testing', 'Тестирование грунта', 'Анализ характеристик грунта', True, 1),

    # House Projects (category 5)
    (5, 'house_project_design', 'Проект дома', 'Профессиональное проектирование дома', False, 2),
    (5, 'cottage_design', 'Проект коттеджа', 'Дизайн и проектирование коттеджа', False, 2),

    # Drainage (category 6)
    (6, 'drainage_system', 'Система дренажа', 'Устройство дренажной системы', False, 2),
    (6, 'water_treatment', 'Очистка воды', 'Система очистки воды', False, 3),

    # Landscaping (category 7)
    (7, 'landscape_design', 'Ландшафтный дизайн', 'Дизайн ландшафта участка', False, 3),
    (7, 'landscaping_work', 'Благоустройство', 'Работы по благоустройству', False, 3),

    # Cadastre (category 8)
    (8, 'cadastral_survey', 'Кадастровая съемка', 'Проведение кадастровой съемки', True, 1),
    (8, 'boundary_determination', 'Определение границ', 'Определение границ участка', True, 1),
    (8, 'cadastral_registration', 'Регистрация в кадастре', 'Регистрация участка в кадастре', True, 2),

    # Appraisal (category 9)
    (9, 'land_appraisal', 'Оценка земли', 'Профессиональная оценка земельного участка', False, 2),
    (9, 'market_analysis', 'Анализ рынка', 'Анализ стоимости на рынке', False, 3),

    # Boundaries (category 10)
    (10, 'boundary_marking', 'Разметка границ', 'Физическая разметка границ участка', False, 2),
    (10, 'boundary_restoration', 'Восстановление границ', 'Восстановление утраченных границ', False, 2),

    # Land Transfer (category 11)
    (11, 'land_transfer_consultation', 'Консультация по переводу', 'Консультация о возможности перевода категории', False, 2),
    (11, 'land_transfer_execution', 'Перевод категории', 'Оформление перевода категории земли', False, 2),

    # Design (category 12)
    (12, 'architectural_design', 'Архитектурный проект', 'Архитектурное проектирование', False, 2),
    (12, 'engineering_design', 'Инженерный проект', 'Инженерное проектирование', False, 2),
    (12, 'construction_project', 'Проект строительства', 'Полный проект строительства', False, 2),

    # Construction (category 13)
    (13, 'foundation', 'Фундамент', 'Устройство фундамента', False, 2),
    (13, 'building_construction', 'Строительство дома', 'Строительство жилого дома', False, 2),
    (13, 'road_construction', 'Дорожные работы', 'Строительство дорог на участке', False, 3),

    # Legal (category 14)
    (14, 'legal_consultation', 'Юридическая консультация', 'Консультация юриста', False, 3),
    (14, 'purchase_support', 'Сопровождение покупки', 'Юридическое сопровождение покупки участка', True, 1),
    (14, 'contract_drafting', 'Оформление договора', 'Подготовка и оформление договора', False, 2),
    (14, 'dispute_resolution', 'Разрешение споров', 'Разрешение земельных споров', False, 3),
]


def upgrade() -> None:
    """Insert seed data"""

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

    now = datetime.utcnow()

    # Insert categories
    categories_data = [
        {
            'slug': slug,
            'name': name,
            'icon': icon,
            'sort_order': sort_order,
            'is_active': True,
            'created_at': now,
        }
        for slug, name, icon, sort_order in [(c[1], c[0], c[2], c[4]) for c in CATEGORIES]
    ]

    # Reorder to match CATEGORIES structure
    for i, (slug, name, icon, sort_order) in enumerate([(c[1], c[0], c[2], c[4]) for c in CATEGORIES]):
        op.execute(
            categories_table.insert().values(
                slug=slug,
                name=name,
                icon=icon,
                sort_order=sort_order,
                is_active=True,
                created_at=now,
            )
        )

    # Insert services - get category ids from database
    for category_id, slug, name, description, is_required, priority in SERVICES:
        op.execute(
            services_table.insert().values(
                category_id=category_id,
                slug=slug,
                name=name,
                short_description=description,
                is_required_default=is_required,
                priority=priority,
                is_active=True,
                created_at=now,
            )
        )


def downgrade() -> None:
    """Remove seed data"""
    op.execute("DELETE FROM services")
    op.execute("DELETE FROM categories")
