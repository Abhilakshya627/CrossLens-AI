"""Shared, database-independent primitives for public CrossLens contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CONTRACT_VERSION = "v1"


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for contract defaults."""
    return datetime.now(timezone.utc)


class ContractModel(BaseModel):
    """Base model for stable cross-module payloads."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: Literal[CONTRACT_VERSION] = CONTRACT_VERSION


class ActorType(StrEnum):
    USER = "user"
    SERVICE = "service"
    WORKER = "worker"
    SYSTEM = "system"


class ArtifactStatus(StrEnum):
    PENDING = "pending"
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    SUPERSEDED = "superseded"


class EvidenceStatus(StrEnum):
    UNASSESSED = "unassessed"
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class SourceContentType(StrEnum):
    DOCUMENT_TEXT = "document_text"
    TABLE = "table"
    SPREADSHEET_CELL = "spreadsheet_cell"
    SPREADSHEET_RANGE = "spreadsheet_range"
    IMAGE = "image"
    IMAGE_REGION = "image_region"
    FIGURE = "figure"


class BoundingBox(ContractModel):
    left: float = Field(ge=0)
    top: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class SourceLocation(ContractModel):
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = Field(default=None, max_length=512)
    sheet_name: str | None = Field(default=None, max_length=255)
    cell_range: str | None = Field(default=None, max_length=128)
    bounding_box: BoundingBox | None = None
    image_region_label: str | None = Field(default=None, max_length=255)

    def is_anchored(self) -> bool:
        return any(
            (
                self.page_number is not None,
                self.section is not None,
                self.sheet_name is not None,
                self.cell_range is not None,
                self.bounding_box is not None,
                self.image_region_label is not None,
            )
        )


class SourceCitation(ContractModel):
    """A citeable link to a versioned, atomic source fragment."""

    workspace_id: str = Field(min_length=1, max_length=128)
    document_id: str = Field(min_length=1, max_length=128)
    document_version_id: str = Field(min_length=1, max_length=128)
    source_fragment_id: str = Field(min_length=1, max_length=128)
    location: SourceLocation
    excerpt: str | None = Field(default=None, max_length=2_000)

    @model_validator(mode="after")
    def require_citeable_location(self) -> "SourceCitation":
        if not self.location.is_anchored():
            raise ValueError("a source citation requires a citeable source location")
        return self


class Provenance(ContractModel):
    created_by: str = Field(min_length=1, max_length=128)
    actor_type: ActorType
    created_at: datetime = Field(default_factory=utc_now)
    processing_run_id: str | None = Field(default=None, max_length=128)


class Confidence(ContractModel):
    score: float = Field(ge=0, le=1)
    method: str = Field(min_length=1, max_length=128)


class ProcessingError(ContractModel):
    code: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=2_000)
    retryable: bool


class TypedAttribute(ContractModel):
    """A deliberately typed replacement for arbitrary cross-module metadata."""

    key: str = Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")
    value: str = Field(max_length=4_000)


class ContractEnvelope(ContractModel):
    request_id: str = Field(min_length=1, max_length=128)
    emitted_at: datetime = Field(default_factory=utc_now)
