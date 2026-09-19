"""Provider-neutral local AI requests and schema-validated result contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from contracts.common import Confidence, ContractModel, SourceCitation
from contracts.retrieval import EvidenceBundle
from contracts.verification import VerificationResult


class ProviderMode(StrEnum):
    DISABLED = "disabled"
    LOCAL = "local"
    CLOUD = "cloud"


class ReasoningStatus(StrEnum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    FAILED = "failed"


class ReasoningRequest(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    question: str = Field(min_length=1, max_length=8_000)
    evidence_bundle: EvidenceBundle
    verification_results: tuple[VerificationResult, ...] = ()
    provider_mode: ProviderMode = ProviderMode.DISABLED


class ReasoningResult(ContractModel):
    reasoning_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    status: ReasoningStatus
    answer: str = Field(min_length=1, max_length=12_000)
    uncertainty: tuple[str, ...] = ()
    source_references: tuple[SourceCitation, ...] = ()
    confidence: Confidence | None = None

    @model_validator(mode="after")
    def require_citations_for_completed_reasoning(self) -> "ReasoningResult":
        if self.status is ReasoningStatus.COMPLETE and not self.source_references:
            raise ValueError("completed reasoning requires source references")
        return self


class EmbeddingRequest(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    input_ids: tuple[str, ...] = Field(min_length=1)
    texts: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def align_inputs(self) -> "EmbeddingRequest":
        if len(self.input_ids) != len(self.texts):
            raise ValueError("input_ids and texts must have equal lengths")
        return self


class EmbeddingResult(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    input_ids: tuple[str, ...] = Field(min_length=1)
    vectors: tuple[tuple[float, ...], ...] = Field(min_length=1)

    @model_validator(mode="after")
    def align_vectors(self) -> "EmbeddingResult":
        if len(self.input_ids) != len(self.vectors):
            raise ValueError("input_ids and vectors must have equal lengths")
        return self

