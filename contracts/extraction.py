"""Contracts for provenance-preserving multimodal extraction output."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from contracts.common import (
    ArtifactStatus,
    Confidence,
    ContractModel,
    ProcessingError,
    SourceContentType,
    SourceLocation,
)
from contracts.ingestion import DocumentVersion, SourceAsset


class ExtractionWarning(ContractModel):
    code: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=2_000)
    source_fragment_id: str | None = Field(default=None, max_length=128)


class SourceFragment(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    document_id: str = Field(min_length=1, max_length=128)
    document_version_id: str = Field(min_length=1, max_length=128)
    source_fragment_id: str = Field(min_length=1, max_length=128)
    content_type: SourceContentType
    location: SourceLocation
    text: str | None = Field(default=None, max_length=100_000)

    @model_validator(mode="after")
    def require_content_or_anchor(self) -> "SourceFragment":
        if not self.text and not self.location.is_anchored():
            raise ValueError("a source fragment needs text or a source location anchor")
        return self


class ExtractedTable(ContractModel):
    source_fragment_id: str = Field(min_length=1, max_length=128)
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


class ExtractedObservation(ContractModel):
    observation_id: str = Field(min_length=1, max_length=128)
    source_fragment_id: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=4_000)
    confidence: Confidence
    visibility_limitations: tuple[str, ...] = ()


class ExtractionRequest(ContractModel):
    document_version: DocumentVersion
    source_asset: SourceAsset


class ExtractionResult(ContractModel):
    document_version_id: str = Field(min_length=1, max_length=128)
    status: ArtifactStatus
    source_fragments: tuple[SourceFragment, ...] = ()
    tables: tuple[ExtractedTable, ...] = ()
    observations: tuple[ExtractedObservation, ...] = ()
    warnings: tuple[ExtractionWarning, ...] = ()
    errors: tuple[ProcessingError, ...] = ()

