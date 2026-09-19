"""Public ports implemented by infrastructure adapters, not business modules."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from contracts.common import SourceCitation
from contracts.extraction import ExtractedObservation
from contracts.graph import (
    EvidenceGraphUpdate,
    GraphNode,
    GraphQueryResult,
    GraphRelationship,
    GraphTraversalQuery,
    ProvenancePath,
)
from contracts.reasoning import EmbeddingRequest, EmbeddingResult, ReasoningRequest, ReasoningResult
from contracts.retrieval import RetrievalRequest, RetrievalResult, VectorRecord
from contracts.ingestion import (
    Document,
    DocumentIngestionResult,
    DocumentVersion,
    ProcessingJob,
    SourceAsset,
)


@runtime_checkable
class GraphStore(Protocol):
    async def create_node(self, node: GraphNode) -> GraphNode: ...

    async def update_node(self, node: GraphNode) -> GraphNode: ...

    async def create_relationship(self, relationship: GraphRelationship) -> GraphRelationship: ...

    async def update_relationship(self, relationship: GraphRelationship) -> GraphRelationship: ...

    async def get_node(self, workspace_id: str, node_id: str) -> GraphNode | None: ...

    async def get_neighbors(self, query: GraphTraversalQuery) -> GraphQueryResult: ...

    async def traverse(self, query: GraphTraversalQuery) -> GraphQueryResult: ...

    async def query_subgraph(self, query: GraphTraversalQuery) -> GraphQueryResult: ...

    async def get_provenance(self, workspace_id: str, node_id: str) -> tuple[ProvenancePath, ...]: ...

    async def get_source_references(
        self, workspace_id: str, node_id: str
    ) -> tuple[SourceCitation, ...]: ...

    async def apply_update(self, update: EvidenceGraphUpdate) -> GraphQueryResult: ...


@runtime_checkable
class VectorStore(Protocol):
    async def upsert(self, records: tuple[VectorRecord, ...]) -> None: ...

    async def search(self, request: RetrievalRequest) -> RetrievalResult: ...


@runtime_checkable
class RelationalStore(Protocol):
    async def create_document(self, document: Document) -> Document: ...

    async def create_document_version(self, document_version: DocumentVersion) -> DocumentVersion: ...

    async def create_source_asset(self, source_asset: SourceAsset) -> SourceAsset: ...

    async def create_processing_job(self, job: ProcessingJob) -> ProcessingJob: ...

    async def get_processing_job(self, workspace_id: str, job_id: str) -> ProcessingJob | None: ...

    async def update_processing_job(self, job: ProcessingJob) -> ProcessingJob: ...

    async def get_document(self, workspace_id: str, document_id: str) -> Document | None: ...

    async def get_latest_document_version(
        self, workspace_id: str, document_id: str
    ) -> DocumentVersion | None: ...

    async def get_ingestion_by_idempotency(
        self, workspace_id: str, idempotency_key: str
    ) -> DocumentIngestionResult | None: ...

    async def register_document_ingestion(
        self, result: DocumentIngestionResult, create_document: bool
    ) -> DocumentIngestionResult: ...

    async def healthcheck(self) -> bool: ...


@runtime_checkable
class FileStore(Protocol):
    async def write_bytes(self, locator: str, content: bytes, media_type: str) -> str: ...

    async def read_bytes(self, locator: str) -> bytes: ...

    async def delete(self, locator: str) -> None: ...


@runtime_checkable
class LLMProvider(Protocol):
    async def generate_structured(self, request: ReasoningRequest) -> ReasoningResult: ...


@runtime_checkable
class VLMProvider(Protocol):
    async def observe_image(self, source_fragment_id: str, image_bytes: bytes) -> ExtractedObservation: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResult: ...
