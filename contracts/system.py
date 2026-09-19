"""Small public contracts for system-level API responses."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from contracts.common import ContractModel


class ServiceStatus(StrEnum):
    HEALTHY = "healthy"


class HealthResponse(ContractModel):
    service: str = Field(default="crosslens-ai")
    status: ServiceStatus = ServiceStatus.HEALTHY
    environment: str = Field(min_length=1, max_length=32)

