"""Failures raised before extraction or any document understanding occurs."""

from __future__ import annotations


class IngestionError(Exception):
    code = "ingestion_error"
    status_code = 422


class UnsupportedDocumentError(IngestionError):
    code = "unsupported_document"


class MediaTypeMismatchError(IngestionError):
    code = "media_type_mismatch"


class FileTooLargeError(IngestionError):
    code = "file_too_large"
    status_code = 413


class DocumentNotFoundError(IngestionError):
    code = "document_not_found"
    status_code = 404


class PersistenceError(IngestionError):
    code = "persistence_error"
    status_code = 500

