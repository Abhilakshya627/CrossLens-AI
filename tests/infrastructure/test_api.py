from __future__ import annotations

from fastapi.testclient import TestClient

from infrastructure.api.app import create_app
from infrastructure.config import Settings


def test_health_endpoint_exposes_only_system_status() -> None:
    app = create_app(settings=Settings(environment="test", _env_file=None))

    with TestClient(app) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "v1",
        "service": "crosslens-ai",
        "status": "healthy",
        "environment": "test",
    }

