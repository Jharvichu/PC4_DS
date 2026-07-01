"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.domains.caregivers import routers as caregiver_routers
from app.domains.notifications import routers as notification_routers
from app.domains.pets import routers as pet_routers
from app.domains.reports import routers as report_routers
from app.domains.search import routers as search_routers
from app.domains.sightings import routers as sighting_routers
from app.domains.users import routers as user_routers
from app.infrastructure import models_registry  # noqa: F401  (registers all ORM models)
from app.middleware.error_handling import exception_handler
from app.shared.exceptions import AppException

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_exception_handler(AppException, exception_handler)

API_PREFIX = "/api"

app.include_router(user_routers.router, prefix=API_PREFIX)
app.include_router(pet_routers.router, prefix=API_PREFIX)
app.include_router(report_routers.router, prefix=API_PREFIX)
app.include_router(sighting_routers.router, prefix=API_PREFIX)
app.include_router(notification_routers.router, prefix=API_PREFIX)
app.include_router(caregiver_routers.router, prefix=API_PREFIX)
app.include_router(search_routers.router, prefix=API_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.API_VERSION}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
