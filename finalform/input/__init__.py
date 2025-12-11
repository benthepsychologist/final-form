"""Form input handling for finalform.

Provides the FormInputClient for managing field_id -> item_id mappings,
and the high-level process_form_submission API for processing canonical
form submissions.
"""

from finalform.input.client import FormInputClient
from finalform.input.process import (
    MissingFormIdError,
    MissingItemMapError,
    UnmappedFieldError,
    process_form_submission,
)

__all__ = [
    "FormInputClient",
    "MissingFormIdError",
    "MissingItemMapError",
    "UnmappedFieldError",
    "process_form_submission",
]
