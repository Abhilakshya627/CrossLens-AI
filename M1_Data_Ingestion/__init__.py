"""Public M1 data-ingestion interface."""

from M1_Data_Ingestion.api.router import create_router
from M1_Data_Ingestion.application.service import IngestionService

__all__ = ["IngestionService", "create_router"]

