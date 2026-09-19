"""The only composition boundary allowed to wire infrastructure to public ports."""

from __future__ import annotations

from dataclasses import dataclass

from contracts.ports import EmbeddingProvider, FileStore, GraphStore, LLMProvider, RelationalStore, VLMProvider, VectorStore
from infrastructure.config import Settings, get_settings
from infrastructure.logging import configure_logging


@dataclass(frozen=True, kw_only=True)
class DependencyRegistry:
    """Adapter slots remain empty until their owning phase provides an adapter."""

    relational_store: RelationalStore | None = None
    graph_store: GraphStore | None = None
    vector_store: VectorStore | None = None
    file_store: FileStore | None = None
    llm_provider: LLMProvider | None = None
    vlm_provider: VLMProvider | None = None
    embedding_provider: EmbeddingProvider | None = None


@dataclass(frozen=True, kw_only=True)
class ApplicationContainer:
    settings: Settings
    dependencies: DependencyRegistry

    @classmethod
    def create(cls, settings: Settings | None = None) -> "ApplicationContainer":
        resolved_settings = settings or get_settings()
        configure_logging(resolved_settings)
        return cls(settings=resolved_settings, dependencies=DependencyRegistry())

