"""
Health check endpoint.

AWS App Runner (and most container orchestrators) periodically hit a
health-check URL to decide if the container is alive and ready to receive
traffic. If this endpoint doesn't respond quickly with a 200, App Runner
will consider the instance unhealthy and cycle it.
"""

from fastapi import APIRouter

from app.config import settings
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
    )
