"""Diagnostics collection for processing pipeline.

Tracks errors, warnings, and quality metrics throughout the
form processing pipeline.
"""

from finalform.diagnostics.collector import DiagnosticsCollector
from finalform.diagnostics.models import (
    DiagnosticError,
    DiagnosticWarning,
    FormDiagnostic,
    MeasureDiagnostic,
    ProcessingStatus,
    QualityMetrics,
)

__all__ = [
    "DiagnosticsCollector",
    "DiagnosticError",
    "DiagnosticWarning",
    "FormDiagnostic",
    "MeasureDiagnostic",
    "ProcessingStatus",
    "QualityMetrics",
]
