from __future__ import annotations

from infrastructure.config import Settings
from infrastructure.container import ApplicationContainer
from infrastructure.tasks.celery_app import create_celery_app


def test_container_has_no_premature_module_adapters() -> None:
    container = ApplicationContainer.create(Settings(environment="test", _env_file=None))

    assert container.dependencies.graph_store is None
    assert container.dependencies.vector_store is None
    assert container.dependencies.llm_provider is None


def test_celery_factory_uses_configured_urls_without_connecting() -> None:
    app = create_celery_app(
        Settings(
            environment="test",
            celery_broker_url="redis://example.test:6379/4",
            celery_result_backend="redis://example.test:6379/5",
            _env_file=None,
        )
    )

    assert app.conf.broker_url == "redis://example.test:6379/4"
    assert app.conf.result_backend == "redis://example.test:6379/5"
