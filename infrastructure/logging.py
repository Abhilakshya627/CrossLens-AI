"""Structured JSON logging without leaking source material or secrets."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Final

from infrastructure.config import Settings

_STANDARD_RECORD_FIELDS: Final = frozenset(logging.makeLogRecord({}).__dict__)
_SAFE_CONTEXT_FIELDS: Final = frozenset(
    {
        "event",
        "workspace_id",
        "document_id",
        "document_version_id",
        "job_id",
        "source_fragment_id",
        "finding_id",
        "request_id",
    }
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str | int | float | bool | None] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _SAFE_CONTEXT_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(settings: Settings) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

