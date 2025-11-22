"""
Pydantic models for questionnaire measures, form mappings, and canonical data.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Questionnaire Measure Models (from org.canonical/questionnaire_measure)
# ============================================================================


class Anchors(BaseModel):
    """Response scale definition with numeric values and text labels."""

    min: float = Field(description="Minimum anchor value")
    max: float = Field(description="Maximum anchor value")
    labels: Dict[str, str] = Field(
        description="Mapping of numeric values (as strings) to text labels"
    )


class Scoring(BaseModel):
    """Scoring method and parameters for a subscale."""

    method: Literal["sum", "average", "sum_then_double"] = Field(
        description="Scoring method to apply"
    )
    min: float = Field(description="Minimum possible score")
    max: float = Field(description="Maximum possible score")
    higher_is_better: bool = Field(description="Whether higher scores indicate better outcomes")
    note: Optional[str] = Field(default=None, description="Optional notes about scoring method")


class Range(BaseModel):
    """Interpretation range with severity label."""

    min: float = Field(description="Minimum score for this range (inclusive)")
    max: float = Field(description="Maximum score for this range (inclusive)")
    label: str = Field(description="Human-readable label for this range")
    severity: str = Field(
        description="Severity classification (e.g., minimal, mild, moderate, severe)"
    )
    description: str = Field(description="Detailed description of what this range means")


class Subscale(BaseModel):
    """Subscale scoring definition."""

    included_items: List[int] = Field(
        description="Array of item numbers (1-indexed) included in this subscale", min_length=1
    )
    reversed_items: List[int] = Field(
        default_factory=list, description="Array of item numbers (1-indexed) that are reverse-scored"
    )
    scoring: Scoring = Field(description="Scoring method and parameters")
    ranges: List[Range] = Field(description="Interpretation ranges with severity labels", min_length=1)


class QuestionnaireMeasure(BaseModel):
    """Canonical questionnaire measure definition."""

    name: str = Field(description="Full name of the questionnaire measure")
    description: str = Field(description="Description of what the measure assesses")
    interpretation: Optional[str] = Field(
        default=None, description="Clinical interpretation guidance"
    )
    instructions: Optional[str] = Field(
        default=None, description="Instructions presented to respondents"
    )
    item_prefix: str = Field(
        description="Canonical item ID prefix (e.g., 'phq_9_', 'gad_7_')",
        pattern=r"^[a-z0-9_]+_$",
    )
    anchors: Anchors = Field(description="Response scale definition")
    items: List[str] = Field(description="Array of item text strings in order", min_length=1)
    scores: Dict[str, Subscale] = Field(
        description="Scoring definitions for subscales (one or more)", min_length=1
    )


# ============================================================================
# Form Mapping Models (from org.canonical/form_mapping)
# ============================================================================


class FormMetadata(BaseModel):
    """Metadata about the specific form being mapped."""

    form_name: str = Field(description="Human-readable form name")
    form_platform: Literal[
        "google_forms", "typeform", "qualtrics", "redcap", "surveymonkey", "jotform", "other"
    ] = Field(description="Form platform identifier")
    form_id: Optional[str] = Field(
        default=None, description="Platform-specific form identifier (URL, UUID, etc.)"
    )
    created_date: Optional[str] = Field(
        default=None, description="Date this mapping was created (YYYY-MM-DD)"
    )
    notes: Optional[str] = Field(default=None, description="Optional notes about this mapping")


class ItemMapping(BaseModel):
    """Item-level mapping from platform ID to canonical ID."""

    form_question_id: str = Field(description="Platform-specific question identifier")
    canonical_item_id: str = Field(
        description="Canonical item ID from questionnaire measure (e.g., 'phq_9_1')",
        pattern=r"^[a-z0-9_]+_[0-9]+$",
    )
    value_mappings: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional custom value mappings. If not provided, uses measure's anchor labels.",
    )
    notes: Optional[str] = Field(default=None, description="Optional notes about this mapping")


class FormMapping(BaseModel):
    """Form-to-measure mapping definition."""

    form_metadata: FormMetadata = Field(description="Metadata about the form")
    measure_id: str = Field(
        description="Canonical measure identifier (e.g., 'phq_9', 'gad_7')",
        pattern=r"^[a-z0-9_]+$",
    )
    item_mappings: List[ItemMapping] = Field(
        description="Array of item-level mappings", min_length=1
    )


# ============================================================================
# Canonical Form Response Models (input from canonizer)
# ============================================================================


class CanonicalFormItem(BaseModel):
    """Single item from a canonical form response."""

    question_id: Optional[str] = Field(
        default=None, description="Platform ID, canonical ID, or question text"
    )
    question_text: Optional[str] = Field(default=None, description="Full question text")
    answer_value: Optional[str | float | int] = Field(
        default=None, description="Answer value (text, numeric, or numeric-as-string)"
    )


class CanonicalFormResponse(BaseModel):
    """Canonical form response from canonizer."""

    form_id: str = Field(description="Form identifier")
    response_id: str = Field(description="Response identifier")
    timestamp: Optional[str] = Field(default=None, description="Response timestamp")
    items: List[CanonicalFormItem] = Field(description="Form items")


# ============================================================================
# Scored Output Models (output from final-form)
# ============================================================================


class ScoredItem(BaseModel):
    """Single scored item with canonical ID and numeric value."""

    canonical_item_id: str = Field(description="Canonical item ID (e.g., 'phq_9_1')")
    original_value: Optional[str | float | int] = Field(
        default=None, description="Original answer value from form"
    )
    numeric_value: float = Field(description="Recoded numeric value")
    reversed: bool = Field(default=False, description="Whether this item was reverse-scored")


class SubscaleScore(BaseModel):
    """Calculated subscale score with interpretation."""

    subscale_name: str = Field(description="Subscale identifier")
    raw_score: float = Field(description="Calculated raw score")
    score_range: Range = Field(description="Interpretation range for this score")
    included_items: List[str] = Field(description="Canonical IDs of items included in score")
    completeness: float = Field(
        description="Proportion of items answered (0.0-1.0)", ge=0.0, le=1.0
    )


class ScoredResponse(BaseModel):
    """Fully scored and interpreted questionnaire response."""

    response_id: str = Field(description="Response identifier")
    measure_id: str = Field(description="Questionnaire measure ID")
    measure_name: str = Field(description="Full measure name")
    timestamp: Optional[str] = Field(default=None, description="Response timestamp")
    items: List[ScoredItem] = Field(description="Scored items with canonical IDs")
    subscales: List[SubscaleScore] = Field(description="Subscale scores and interpretations")
    metadata: Dict[str, any] = Field(
        default_factory=dict, description="Additional metadata and diagnostics"
    )
