"""Точка входа приложения FastAPI"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import ApplicationException
from app.core.logging import setup_logging, get_logger
from app.db.base import init_db
from app.bounded_contexts.identity_access import routes as auth_routes
from app.bounded_contexts.lands import routes as lands_routes
from app.bounded_contexts.services import routes as services_routes
from app.bounded_contexts.companies import routes as companies_routes
from app.bounded_contexts.recommendations import routes as recommendations_routes
from app.bounded_contexts.applications import routes as applications_routes
from app.bounded_contexts.reviews import routes as reviews_routes
from app.bounded_contexts.integrations import routes as integrations_routes
from app.bounded_contexts.admin import routes as admin_routes

# Инициализация логирования
setup_logging()
logger = get_logger(__name__)

# Создание приложения FastAPI
app = FastAPI(
    title="Моя Земля API",
    description="Платформа подбора земельных участков и сопровождения их освоения",
    version="0.1.0",
    debug=settings.debug,
)

# Добавление CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Обработчики исключений
@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exc: ApplicationException):
    """Обработка пользовательских исключений приложения"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details,
        },
    )


# Endpoint проверки здоровья
@app.get("/api/v1/health", tags=["Здоровье"])
async def health_check():
    """Endpoint проверки здоровья сервиса"""
    return {"status": "ok"}


# Инициализация БД при запуске
@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info("Приложение запускается")
    init_db()
    logger.info("База данных инициализирована")


@app.on_event("shutdown")
async def shutdown_event():
    """Событие выключения приложения"""
    logger.info("Приложение завершает работу")


# Include routers
app.include_router(auth_routes.router)
app.include_router(lands_routes.router)
app.include_router(services_routes.router)
app.include_router(companies_routes.router)
app.include_router(recommendations_routes.router)
app.include_router(applications_routes.router)
app.include_router(reviews_routes.router)
app.include_router(integrations_routes.router)
app.include_router(admin_routes.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
    )
