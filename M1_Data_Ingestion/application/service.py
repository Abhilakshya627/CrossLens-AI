"""Register validated source material and queue, but never understand, a document."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from contracts.common import ArtifactStatus
from contracts.ingestion import (
    Document,
    DocumentIngestionRequest,
    DocumentIngestionResult,
    DocumentVersion,
    JobStatus,
    ProcessingJob,
    SourceAsset,
)
from contracts.ports import FileStore, RelationalStore
from M1_Data_Ingestion.domain.errors import DocumentNotFoundError, PersistenceError
from M1_Data_Ingestion.domain.validation import UploadPayload, validate_upload


@dataclass(frozen=True, slots=True)
class IngestionService:
    relational_store: RelationalStore
    file_store: FileStore
    max_upload_bytes: int

    async def ingest(
        self, request: DocumentIngestionRequest, payload: UploadPayload
    ) -> DocumentIngestionResult:
        existing = await self.relational_store.get_ingestion_by_idempotency(
            request.workspace_id, request.idempotency_key
        )
        if existing is not None:
            return existing

        upload = validate_upload(payload, request.declared_kind, self.max_upload_bytes)
        document, create_document, version_number = await self._resolve_document(request)
        document_version = DocumentVersion(
            workspace_id=request.workspace_id,
            document_id=document.document_id,
            document_version_id=_new_id("document-version"),
            version_number=version_number,
            content_sha256=upload.content_sha256,
        )
        source_asset = SourceAsset(
            workspace_id=request.workspace_id,
            document_id=document.document_id,
            document_version_id=document_version.document_version_id,
            source_asset_id=_new_id("source-asset"),
            media_type=upload.media_type,
            byte_size=upload.byte_size,
            storage_locator=_storage_locator(
                request.workspace_id, document.document_id, document_version.document_version_id
            ),
            status=ArtifactStatus.COMPLETE,
        )
        processing_job = ProcessingJob(
            workspace_id=request.workspace_id,
            document_id=document.document_id,
            document_version_id=document_version.document_version_id,
            job_id=_new_id("processing-job"),
            idempotency_key=request.idempotency_key,
            status=JobStatus.QUEUED,
        )
        result = DocumentIngestionResult(
            document=document,
            document_version=document_version,
            source_asset=source_asset,
            processing_job=processing_job,
        )

        await self.file_store.write_bytes(source_asset.storage_locator, upload.content, upload.media_type)
        try:
            return await self.relational_store.register_document_ingestion(result, create_document)
        except Exception as error:
            await self.file_store.delete(source_asset.storage_locator)
            raise PersistenceError("could not register the document ingestion") from error

    async def get_job(self, workspace_id: str, job_id: str) -> ProcessingJob | None:
        return await self.relational_store.get_processing_job(workspace_id, job_id)

    async def _resolve_document(
        self, request: DocumentIngestionRequest
    ) -> tuple[Document, bool, int]:
        if request.existing_document_id is None:
            return (
                Document(
                    workspace_id=request.workspace_id,
                    document_id=_new_id("document"),
                    display_name=request.display_name,
                    kind=request.declared_kind,
                ),
                True,
                1,
            )

        document = await self.relational_store.get_document(
            request.workspace_id, request.existing_document_id
        )
        if document is None:
            raise DocumentNotFoundError("the requested document does not exist in this workspace")
        latest_version = await self.relational_store.get_latest_document_version(
            request.workspace_id, document.document_id
        )
        if latest_version is None:
            raise PersistenceError("a persisted document has no document version")
        return document, False, latest_version.version_number + 1


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4()}"


def _storage_locator(workspace_id: str, document_id: str, document_version_id: str) -> str:
    return f"{workspace_id}/{document_id}/{document_version_id}/original"
