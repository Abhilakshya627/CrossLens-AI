"""File-kind validation and MIME detection; this module never parses document meaning."""

from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

from contracts.ingestion import DocumentKind
from M1_Data_Ingestion.domain.errors import (
    FileTooLargeError,
    MediaTypeMismatchError,
    UnsupportedDocumentError,
)

_EXTENSION_KINDS = {
    ".pdf": DocumentKind.PDF,
    ".docx": DocumentKind.DOCX,
    ".xlsx": DocumentKind.XLSX,
    ".csv": DocumentKind.CSV,
    ".txt": DocumentKind.TXT,
    ".png": DocumentKind.PNG,
    ".jpg": DocumentKind.JPG,
    ".jpeg": DocumentKind.JPEG,
}

_MEDIA_TYPES = {
    DocumentKind.PDF: "application/pdf",
    DocumentKind.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    DocumentKind.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    DocumentKind.CSV: "text/csv",
    DocumentKind.TXT: "text/plain",
    DocumentKind.PNG: "image/png",
    DocumentKind.JPG: "image/jpeg",
    DocumentKind.JPEG: "image/jpeg",
}


@dataclass(frozen=True, slots=True)
class UploadPayload:
    file_name: str
    content: bytes


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    file_name: str
    kind: DocumentKind
    media_type: str
    content_sha256: str
    byte_size: int
    content: bytes


def validate_upload(payload: UploadPayload, declared_kind: DocumentKind, max_bytes: int) -> ValidatedUpload:
    file_name = Path(payload.file_name).name
    if not file_name or file_name in {".", ".."}:
        raise UnsupportedDocumentError("a file name is required")
    if len(payload.content) > max_bytes:
        raise FileTooLargeError(f"file exceeds the configured {max_bytes}-byte limit")

    extension_kind = _EXTENSION_KINDS.get(Path(file_name).suffix.lower())
    if extension_kind is None:
        raise UnsupportedDocumentError("the file extension is not supported")
    if extension_kind is not declared_kind:
        raise MediaTypeMismatchError("declared document kind does not match the file extension")

    detected_kind = detect_kind(payload.content, extension_kind)
    if detected_kind is not extension_kind:
        raise MediaTypeMismatchError("file content does not match the declared document kind")

    return ValidatedUpload(
        file_name=file_name,
        kind=detected_kind,
        media_type=_MEDIA_TYPES[detected_kind],
        content_sha256=hashlib.sha256(payload.content).hexdigest(),
        byte_size=len(payload.content),
        content=payload.content,
    )


def detect_kind(content: bytes, extension_kind: DocumentKind) -> DocumentKind:
    if extension_kind is DocumentKind.PDF:
        return DocumentKind.PDF if content.startswith(b"%PDF-") else DocumentKind.TXT
    if extension_kind is DocumentKind.PNG:
        return DocumentKind.PNG if content.startswith(b"\x89PNG\r\n\x1a\n") else DocumentKind.TXT
    if extension_kind in {DocumentKind.JPG, DocumentKind.JPEG}:
        return extension_kind if content.startswith(b"\xff\xd8\xff") else DocumentKind.TXT
    if extension_kind in {DocumentKind.DOCX, DocumentKind.XLSX}:
        return _detect_office_kind(content)
    if extension_kind is DocumentKind.CSV:
        _validate_text(content)
        return DocumentKind.CSV
    if extension_kind is DocumentKind.TXT:
        _validate_text(content)
        return DocumentKind.TXT
    raise UnsupportedDocumentError("the file type is not supported")


def _detect_office_kind(content: bytes) -> DocumentKind:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = set(archive.namelist())
    except zipfile.BadZipFile:
        return DocumentKind.TXT
    if any(member.startswith("word/") for member in members):
        return DocumentKind.DOCX
    if any(member.startswith("xl/") for member in members):
        return DocumentKind.XLSX
    return DocumentKind.TXT


def _validate_text(content: bytes) -> None:
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise MediaTypeMismatchError("text files must be UTF-8 encoded") from error

