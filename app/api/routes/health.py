"""Health check router."""
from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Perform system health check")
async def get_health() -> HealthResponse:
    """Return health status of the API."""
    return HealthResponse(status="ok")

