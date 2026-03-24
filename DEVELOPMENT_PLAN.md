# DEVELOPMENT_PLAN.md

Детальный план разработки платформы LandPlan

## ФАЗА ПОДГОТОВКИ (1-2 недели)

### Цель
Установить инфраструктуру разработки, создать структуру проекта, настроить конфигурацию и pipelines.

### Компоненты

#### 1.1 Backend инфраструктура
- **Стек**: FastAPI (Python 3.11+), Poetry для управления зависимостями
- **Структура проекта**:
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py (точка входа)
  │   ├── config.py (окружение, настройки)
  │   ├── core/
  │   │   ├── security.py (JWT, auth)
  │   │   ├── logging.py
  │   │   └── exceptions.py
  │   ├── bounded_contexts/
  │   │   ├── identity_access/
  │   │   ├── lands/
  │   │   ├── services/
  │   │   ├── companies/
  │   │   ├── recommendations/
  │   │   ├── applications/
  │   │   ├── reviews/
  │   │   ├── notifications/
  │   │   ├── admin/
  │   │   └── integrations/
  │   ├── db/
  │   │   ├── base.py (SQLAlchemy setup)
  │   │   ├── session.py
  │   │   └── migrations/ (Alembic)
  │   └── schemas/ (Pydantic DTO)
  ├── tests/
  ├── pyproject.toml
  └── .env.example
  ```

#### 1.2 Frontend инфраструктура
- **Стек**: React 18+ с TypeScript, Vite
- **Структура проекта**:
  ```
  frontend/
  ├── public/
  ├── src/
  │   ├── main.tsx
  │   ├── App.tsx
  │   ├── index.css
  │   ├── pages/ (маршруты)
  │   │   ├── MapPage.tsx
  │   │   ├── LandCardPage.tsx
  │   │   ├── CompaniesPage.tsx
  │   │   └── CabinetPage.tsx
  │   ├── components/
  │   │   ├── Map/
  │   │   ├── LandCard/
  │   │   ├── ServicesList/
  │   │   └── RecommendationsBlock/
  │   ├── services/ (API clients)
  │   │   ├── landsApi.ts
  │   │   ├── companiesApi.ts
  │   │   └── recommendationsApi.ts
  │   ├── hooks/
  │   ├── context/ (state management)
  │   ├── types/
  │   └── utils/
  ├── package.json
  └── .env.example
  ```

#### 1.3 Database инфраструктура
- PostgreSQL 15+ с PostGIS для геоданных
- Alembic для миграций
- Индексы на:
  - `lands.latitude, lands.longitude` (geo-queries)
  - `lands.region_id, lands.city_id` (фильтрация)
  - `companies.region_id` (поиск компаний)
  - `applications.user_id, applications.status` (заявки)

#### 1.4 Docker + CI/CD
- `docker-compose.yml` для локальной разработки (FastAPI, PostgreSQL, Redis)
- GitHub Actions для:
  - Lint (pylint, black, mypy для backend; ESLint для frontend)
  - Unit tests
  - Build образов

#### 1.5 Конфигурация окружения
- `.env` для локальной разработки
- Settings через Pydantic (`config.py`)
- Переменные для PostgreSQL, Redis, JWT_SECRET, API_KEYS

### Результат фазы
- Готовая структура оба стека
- Docker-compose для локальной разработки
- Базовый pipeline CI/CD
- Документация по запуску

---

## ФАЗА 1: BACKEND ФУНДАМЕНТ (1-1.5 недели)

### Цель
Создать базовую структуру backend, настроить БД, реализовать identity/auth.

### Компоненты

#### 1.1 Database Schema (основная часть)
**Таблицы для реализации**:

```sql
-- Базовые таблицы
users (id, role, email, phone, password_hash, full_name, status, created_at, updated_at)
user_profiles (user_id, avatar_url, preferred_region, notification_settings)

-- Справочники
regions (id, name, slug)
cities (id, region_id, name, slug)
categories (id, name, slug, icon, sort_order, is_active)
sources (id, type, name, config, is_active)

-- Основные таблицы (структура только)
lands (id, external_id, source_id, title, description, address, region_id, city_id,
       latitude, longitude, price, area, land_category, allowed_usage, deal_type,
       status, is_actual, published_at, updated_at)
land_features (land_id, has_water, has_electricity, has_gas, has_roads,
               boundaries_defined, build_ready, notes)

-- Справочники для услуг
services (id, category_id, name, slug, short_description, full_description,
          is_required_default, priority, is_active)

-- Справочник компаний (структура только)
companies (id, legal_name, public_name, description, logo_url, rating, reviews_count,
           verification_status, contact_phone, contact_email, website, is_active,
           created_at, updated_at)
company_regions (id, company_id, region_id)
company_services (id, company_id, service_id, base_price_from, is_active)
```

#### 1.2 Models (SQLAlchemy ORM)
**Файлы в `app/models/`**:
- `user.py` — User, UserProfile
- `reference.py` — Region, City, Category, Source
- `land.py` — Land, LandFeature
- `service.py` — Service
- `company.py` — Company, CompanyRegion, CompanyService

#### 1.3 Identity & Access (Bounded Context)
**Файл: `app/bounded_contexts/identity_access/`**

- **Модели**: User (role: user, company, admin, moderator)
- **Сервисы**:
  - UserService (CRUD, password hash)
  - AuthService (JWT, refresh tokens, role verification)
- **Endpoints**:
  - `POST /api/v1/auth/register` → создание пользователя
  - `POST /api/v1/auth/login` → JWT + refresh
  - `POST /api/v1/auth/refresh` → обновление токена
  - `POST /api/v1/auth/logout` → инвалидация
- **Security**:
  - JWTBearer для защиты endpoints
  - Password hashing (bcrypt)
  - Rate limiting на auth endpoints

#### 1.4 Core Infrastructure
**Файл: `app/core/`**

- `security.py`:
  - `create_access_token(data: dict, expires_delta: Optional[timedelta])`
  - `verify_token(token: str) -> dict`
  - `get_current_user()` dependency
  - `get_password_hash(password: str)`
  - `verify_password(plain: str, hashed: str)`

- `exceptions.py`:
  - `AuthenticationException`
  - `AuthorizationException`
  - `NotFoundError`
  - `ValidationError`

- `logging.py`:
  - Структурированное логирование (JSON)

#### 1.5 Database setup
**Файл: `app/db/`**

- `base.py`: SQLAlchemy Base, engine creation
- `session.py`: SessionLocal, get_db dependency
- `migrations/`: Alembic инициализация

### Результат фазы
- Готовая структура БД (все таблицы, индексы)
- User/Auth API готов и работает
- Миграции Alembic настроены
- Tests для auth (регистрация, логин, JWT)

---

## ФАЗА 2: CORE API ДЛЯ ОСНОВНЫХ СУЩНОСТЕЙ (1.5-2 недели)

### Цель
Реализовать API для участков, услуг, компаний — основной витрины платформы.

### Компоненты

#### 2.1 Lands Bounded Context
**Файл: `app/bounded_contexts/lands/`**

**Models**:
- Land (с полным набором полей)
- LandFeature (has_water, has_electricity, etc.)

**Services** (`lands_service.py`):
- `get_lands(filters: LandsFilterDTO) -> List[LandDTO]`
- `get_land_by_id(land_id: int) -> LandDetailDTO`
- `create_land(data: CreateLandDTO) -> LandDTO` (для импорта)
- `update_land(land_id: int, data: UpdateLandDTO) -> LandDTO`

**API Endpoints** (`lands_routes.py`):
- `GET /api/v1/lands` — список с фильтрами (region, city, price_min/max, deal_type, q, bbox, page)
- `GET /api/v1/lands/{id}` — карточка участка
- `GET /api/v1/lands/{id}/features` — особенности участка

**Filtering Logic**:
- Server-side фильтрация (БД queries)
- Pagination (limit/offset или cursor)
- GEO queries (bbox) через PostGIS
- Full-text search через ILIKE (временно, до Elasticsearch)

**DTOs**:
- `LandListDTO` (для списка)
- `LandDetailDTO` (для карточки)
- `LandFeatureDTO`
- `LandsFilterDTO`

#### 2.2 Services Catalog Bounded Context
**Файл: `app/bounded_contexts/services/`**

**Models**:
- Category
- Service

**Services** (`services_service.py`):
- `get_categories() -> List[CategoryDTO]`
- `get_services(category_id: Optional[int]) -> List[ServiceDTO]`
- `get_service_by_id(service_id: int) -> ServiceDetailDTO`

**API Endpoints** (`services_routes.py`):
- `GET /api/v1/categories` — список категорий
- `GET /api/v1/services` — список услуг (опционально filtered by category)
- `GET /api/v1/services/{id}` — детали услуги

**DTOs**:
- `CategoryDTO`
- `ServiceDTO`
- `ServiceDetailDTO`

**Data Load** (initial):
- Seed-данные категорий и услуг (из спека: вода, геология, кадастр, юристы, и т.д.)
- SQL скрипт или Alembic migration

#### 2.3 Companies Bounded Context
**Файл: `app/bounded_contexts/companies/`**

**Models**:
- Company
- CompanyRegion
- CompanyService

**Services** (`companies_service.py`):
- `get_companies(filters: CompaniesFilterDTO) -> List[CompanyDTO]`
- `get_company_by_id(company_id: int) -> CompanyDetailDTO`
- `create_company(data: CreateCompanyDTO) -> CompanyDTO` (для самой компании)
- `update_company(company_id: int, data: UpdateCompanyDTO) -> CompanyDTO`

**API Endpoints** (`companies_routes.py`):
- `GET /api/v1/companies` — список компаний (filter by region, service, q)
- `GET /api/v1/companies/{id}` — карточка компании
- `GET /api/v1/companies/{id}/services` — услуги компании
- `GET /api/v1/companies/{id}/regions` — регионы присутствия

**DTOs**:
- `CompanyListDTO`
- `CompanyDetailDTO`
- `CompanyServiceDTO`
- `CompaniesFilterDTO`

#### 2.4 Integration слой (Lands → Services → Companies)
**Файл: `app/bounded_contexts/` (интеграционный слой)**

**Service** (`integration_service.py`):
- `get_lands_with_services_and_companies(land_id: int) -> CompositeDTO`
  - Возвращает Land + рекомендованные Services + релевантные Companies

Это промежуточный слой перед Recommendations Engine, используется в API endpoints.

#### 2.5 Testing
- Unit tests для LandsService, CompaniesService, ServicesService
- Integration tests для API endpoints
- Fixtures для seed-данных

### Результат фазы
- Полный API для поиска участков, услуг, компаний
- Фильтрация и пагинация работают
- Релевантные DTOs определены
- Тесты покрывают 70%+ основного функционала

---

## ФАЗА 3: RECOMMENDATIONS ENGINE (2-2.5 недели)

### Цель
Реализовать ядро платформы — логику связи "участок → услуги → компании".

### Компоненты

#### 3.1 Recommendations Engine
**Файл: `app/bounded_contexts/recommendations/`**

**Core Logic** (`recommendation_engine.py`):

```python
class RecommendationEngine:
    def get_recommendations(self, land: Land) -> RecommendationsDTO:
        """
        Анализирует характеристики участка и возвращает:
        - Обязательные услуги
        - Рекомендованные услуги
        - Последовательность (priority order)
        """
        recommendations = []

        # Rule 1: Водоснабжение
        if not land.features.has_water:
            recommendations.append({
                'services': ['water_analysis', 'drilling', 'water_supply'],
                'priority': 1,  # критично
                'reason': 'Вода отсутствует'
            })

        # Rule 2: Кадастр
        if not land.features.boundaries_defined:
            recommendations.append({
                'services': ['cadastre', 'boundaries'],
                'priority': 2,
                'reason': 'Границы не определены'
            })

        # Rule 3: Покупка
        if land.deal_type == 'purchase':
            recommendations.append({
                'services': ['legal', 'appraisal'],
                'priority': 2,
                'reason': 'Требуется для покупки'
            })

        # Rule 4: Строительство
        if not land.features.build_ready:
            recommendations.append({
                'services': ['geology', 'design', 'construction'],
                'priority': 3,
                'reason': 'Подготовка к строительству'
            })

        # ... дополнительные правила

        return RecommendationsDTO(
            land_id=land.id,
            recommended_services=self._flatten_services(recommendations),
            steps=self._build_plan_steps(recommendations),
            next_actions=self._prioritize_actions(recommendations)
        )
```

**Models**:
- `LandRecommendation` (кэш рекомендаций в БД для производительности)
- `LandPlan` (план освоения, создается при выборе услуг)
- `LandPlanStep` (отдельные этапы плана)

**Services** (`recommendations_service.py`):
- `get_recommendations(land_id: int) -> RecommendationsDTO`
- `create_land_plan(land_id: int, selected_services: List[int]) -> LandPlanDTO`
- `get_land_plan(land_plan_id: int) -> LandPlanDetailDTO`
- `compute_and_cache_recommendations(land_id: int)` (фоновая задача)

#### 3.2 Land Plan Engine
**Файл: `app/bounded_contexts/recommendations/land_plan.py`**

**Логика**:
- После выбора пользователем услуг, система создает `LandPlan`
- `LandPlan` состоит из упорядоченных `LandPlanStep`
- Каждый step:
  - Привязан к Service
  - Имеет статус (pending, in_progress, completed)
  - Может быть привязан к Company (после выбора подрядчика)
  - Может иметь Application (заявку)

**Structure**:
```python
class LandPlan:
    id: int
    user_id: int
    land_id: int
    status: str  # active, paused, completed
    steps: List[LandPlanStep]
    created_at: datetime
    updated_at: datetime

class LandPlanStep:
    id: int
    land_plan_id: int
    service_id: int
    order: int  # последовательность
    status: str  # pending, in_progress, completed, skipped
    selected_company_id: Optional[int]
    application_id: Optional[int]
    created_at: datetime
    updated_at: datetime
```

#### 3.3 API Endpoints
**Файл: `app/bounded_contexts/recommendations/routes.py`**

- `GET /api/v1/lands/{id}/recommendations` → RecommendationsDTO
  - Возвращает список рекомендованных услуг и приоритизацию

- `POST /api/v1/land-plans` → LandPlanDTO
  - Создает план на основе выбранных услуг
  - Payload: `{ land_id, selected_service_ids }`

- `GET /api/v1/land-plans/{id}` → LandPlanDetailDTO
  - Полный план с шагами и статусами

- `PATCH /api/v1/land-plan-steps/{id}` → LandPlanStepDTO
  - Обновление статуса шага / выбор компании

#### 3.4 DTOs
- `RecommendationsDTO`
- `LandPlanDTO`
- `LandPlanDetailDTO`
- `LandPlanStepDTO`

#### 3.5 Testing
- Unit tests для RulesEngine (каждое правило отдельно)
- Integration tests для создания/обновления LandPlan
- Edge cases (участок без features, с partial features)

### Критические аспекты
1. **Интерпретируемость**: Каждая рекомендация должна иметь `reason`
2. **Кэширование**: Рекомендации вычисляются один раз и кэшируются
3. **Расширяемость**: Правила должны быть легко добавляемы (возможно, конфиг)
4. **Производительность**: Не должны вычисляться на каждый запрос

### Результат фазы
- Recommendations Engine работает с набором базовых правил
- LandPlan API полностью реализован
- Рекомендации кэшируются в БД
- Тесты покрывают основные сценарии

---

## ФАЗА 4: FRONTEND — ОСНОВНЫЕ ЭКРАНЫ (2-2.5 недели)

## ФАЗА 5: СИСТЕМА ЗАЯВОК И ЛИЧНЫЕ КАБИНЕТЫ (1.5-2 недели)

## ФАЗА 6: ИНТЕГРАЦИИ И ИМПОРТ ДАННЫХ (1.5-2 недели)

## ФАЗА 7: STAGE 2 И ДАЛЬШЕ (эволюция продукта)

(см. полный документ выше)

---

## TIMELINE И DEPENDENCIES

| Фаза | Недели | MVP Ready |
|------|--------|-----------|
| Подготовка | 1-2 | - |
| Фаза 1 | 1-1.5 | - |
| Фаза 2 | 1.5-2 | - |
| Фаза 3 | 2-2.5 | ✓ |
| Фаза 4 | 2-2.5 | ✓ |
| Фаза 5 | 1.5-2 | ✓✓ MVP |
| Фаза 6 | 1.5-2 | ✓ |

**Итого для MVP**: ~10-13 недель (2.5-3 месяца)

---

## CRITICAL SUCCESS FACTORS

1. **Recommendations Engine не должен быть тривиальным** — это дифференциатор
2. **Данные должны быть актуальны** — импорт/дедупликация критичны
3. **UX flow "участок → рекомендации → заявка" должен быть бесшовным**
4. **Performance должен быть хорош с самого начала** (indexing, caching, clustering)
5. **RBAC (roles) должны быть понятными и правильно реализованы** (user vs company vs admin)
