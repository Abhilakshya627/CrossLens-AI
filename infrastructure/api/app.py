"""Health-only FastAPI composition root for the infrastructure foundation."""

from __future__ import annotations

from fastapi import FastAPI

from contracts.system import HealthResponse
from infrastructure.config import Settings
from infrastructure.container import ApplicationContainer


def create_app(
    *,
    settings: Settings | None = None,
    container: ApplicationContainer | None = None,
) -> FastAPI:
    """Create the HTTP host without exposing any module implementation or datastore."""
    if settings is not None and container is not None:
        raise ValueError("provide settings or container, not both")

    resolved_container = container or ApplicationContainer.create(settings)
    app = FastAPI(title="CrossLens AI", version="0.1.0")
    app.state.container = resolved_container

    @app.get("/healthz", response_model=HealthResponse, tags=["system"])
    async def healthcheck() -> HealthResponse:
        return HealthResponse(environment=resolved_container.settings.environment)

    return app

