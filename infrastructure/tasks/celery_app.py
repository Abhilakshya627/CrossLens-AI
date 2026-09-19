"""Celery application factory with no business tasks registered in Phase 1."""

from __future__ import annotations

from celery import Celery

from infrastructure.config import Settings, get_settings


def create_celery_app(settings: Settings | None = None) -> Celery:
    resolved_settings = settings or get_settings()
    app = Celery("crosslens")
    app.conf.update(
        broker_url=resolved_settings.celery_broker_url,
        result_backend=resolved_settings.celery_result_backend,
        task_track_started=True,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )
    return app


celery_app = create_celery_app()

