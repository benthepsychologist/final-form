"""Core diagnostics models for processing status tracking.

Re-exports base types from the diagnostics module.
These are used across all domains.
"""

# Re-export from diagnostics.models - these are the canonical definitions
from finalform.diagnostics.models import (
    DiagnosticError,
    DiagnosticWarning,
    FormDiagnostic,
    MeasureDiagnostic,
    ProcessingStatus,
    QualityMetrics,
)

# Alias for clarity in domain processor context
ProcessingDiagnostics = FormDiagnostic

__all__ = [
    "DiagnosticError",
    "DiagnosticWarning",
    "FormDiagnostic",
    "MeasureDiagnostic",
    "ProcessingDiagnostics",
    "ProcessingStatus",
    "QualityMetrics",
]
