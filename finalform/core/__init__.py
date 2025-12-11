"""Core shared infrastructure for finalform.

Contains domain-agnostic models, protocols, and utilities shared
across all measurement domains (questionnaire, lab, vital, wearable).

Most types are re-exported from their canonical locations in the
builders and diagnostics modules.
"""

from finalform.core.diagnostics import (
    DiagnosticError,
    DiagnosticWarning,
    FormDiagnostic,
    MeasureDiagnostic,
    ProcessingDiagnostics,
    ProcessingStatus,
    QualityMetrics,
)
from finalform.core.domain import DomainProcessor
from finalform.core.factory import create_router, get_default_router
from finalform.core.models import (
    MeasurementEvent,
    Observation,
    ProcessingResult,
    Source,
    Telemetry,
)
from finalform.core.router import DomainRouter

__all__ = [
    # Models
    "MeasurementEvent",
    "Observation",
    "ProcessingResult",
    "Source",
    "Telemetry",
    # Diagnostics
    "DiagnosticError",
    "DiagnosticWarning",
    "FormDiagnostic",
    "MeasureDiagnostic",
    "ProcessingDiagnostics",
    "ProcessingStatus",
    "QualityMetrics",
    # Domain
    "DomainProcessor",
    "DomainRouter",
    # Factory
    "create_router",
    "get_default_router",
]
