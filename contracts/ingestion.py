"""Contracts for registering versioned source material without understanding it."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator

from contracts.common import ArtifactStatus, ContractModel, ProcessingError, utc_now


class DocumentKind(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    TXT = "txt"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"


class JobStatus(StrEnum):
    QUEUED = "queued"
    INGEST_REGISTERED = "ingest_registered"
    EXTRACTING = "extracting"
    NORMALIZING = "normalizing"
    GRAPH_UPDATING = "graph_updating"
    EMBEDDING = "embedding"
    VERIFYING = "verifying"
    REASONING = "reasoning"
    FINDINGS_READY = "findings_ready"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Document(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    document_id: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=512)
    kind: DocumentKind
    created_at: datetime = Field(default_factory=utc_now)


class DocumentVersion(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    document_id: str = Field(min_length=1, max_length=128)
    document_version_id: str = Field(min_length=1, max_length=128)
    version_number: int = Field(ge=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("content_sha256")
    @classmethod
    def validate_sha256(cls, value: str) -> str:
        if any(character not in "0123456789abcdef" for character in value.lower()):
            raise ValueError("content_sha256 must be a hexadecimal SHA-256 digest")
        return value.lower()


class SourceAsset(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    document_id: str = Field(min_length=1, max_length=128)
    document_version_id: str = Field(min_length=1, max_length=128)
    source_asset_id: str = Field(min_length=1, max_length=128)
    media_type: str = Field(min_length=1, max_length=255)
    byte_size: int = Field(ge=0)
    storage_locator: str = Field(min_length=1, max_length=2_048)
    status: ArtifactStatus = ArtifactStatus.PENDING


class ProcessingJob(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    document_id: str = Field(min_length=1, max_length=128)
    document_version_id: str = Field(min_length=1, max_length=128)
    job_id: str = Field(min_length=1, max_length=128)
    idempotency_key: str = Field(min_length=1, max_length=255)
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    error: ProcessingError | None = None


class DocumentIngestionRequest(ContractModel):
    workspace_id: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=512)
    declared_kind: DocumentKind
    idempotency_key: str = Field(min_length=1, max_length=255)
    existing_document_id: str | None = Field(default=None, max_length=128)


class DocumentIngestionResult(ContractModel):
    document: Document
    document_version: DocumentVersion
    source_asset: SourceAsset
    processing_job: ProcessingJob
