"""Hybrid retrieval contracts; relevance is kept distinct from verification."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from contracts.common import ContractModel, SourceCitation
from contracts.extraction import SourceFragment
from contracts.graph import GraphRelationship
from contracts.knowledge import Claim, Condition, Fact, Observation


class RetrievalStatus(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    NO_RESULTS = "no_results"
    FAILED = "failed"


class RetrievalRequest(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    query: str = Field(min_length=1, max_length=8_000)
    top_k: int = Field(default=20, ge=1, le=100)
    document_version_ids: tuple[str, ...] = ()


class RetrievedEvidence(ContractModel):
    evidence_id: str = Field(min_length=1, max_length=128)
    relevance_score: float = Field(ge=0, le=1)
    excerpt: str = Field(min_length=1, max_length=4_000)
    source_references: tuple[SourceCitation, ...] = Field(min_length=1)


class RetrievalResult(ContractModel):
    request: RetrievalRequest
    status: RetrievalStatus
    items: tuple[RetrievedEvidence, ...] = ()
    graph_relationships: tuple[GraphRelationship, ...] = ()


class EvidenceBundle(ContractModel):
    """The compact, inspectable context for verification and later reasoning."""

    workspace_id: str = Field(min_length=1, max_length=128)
    query: str = Field(min_length=1, max_length=8_000)
    relevant_claims: tuple[Claim, ...] = ()
    relevant_facts: tuple[Fact, ...] = ()
    observations: tuple[Observation, ...] = ()
    conditions: tuple[Condition, ...] = ()
    graph_relationships: tuple[GraphRelationship, ...] = ()
    source_fragments: tuple[SourceFragment, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()


class VectorRecord(ContractModel):
    vector_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    source_fragment_id: str = Field(min_length=1, max_length=128)
    document_version_id: str = Field(min_length=1, max_length=128)
    embedding: tuple[float, ...] = Field(min_length=1)

