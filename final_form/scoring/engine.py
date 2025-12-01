"""Scoring engine for computing scale scores.

The engine is generic - it reads all scoring rules from the instrument spec.
No per-questionnaire code is allowed.
"""

from typing import Literal

from pydantic import BaseModel

from final_form.recoding.recoder import RecodedSection
from final_form.registry.models import InstrumentSpec
from final_form.scoring.methods import compute_score, prorate_score
from final_form.scoring.reverse import apply_reverse_scoring, get_max_value_for_item


class ScoringError(Exception):
    """Raised when scoring fails."""

    pass


class ScaleScore(BaseModel):
    """A computed scale score."""

    scale_id: str
    name: str
    value: float | None
    method: Literal["sum", "average", "sum_then_double"]
    items_used: int
    items_total: int
    missing_items: list[str]
    reversed_items: list[str]
    prorated: bool = False
    error: str | None = None


class ScoringResult(BaseModel):
    """Result of scoring all scales in an instrument."""

    instrument_id: str
    instrument_version: str
    scales: list[ScaleScore]

    def get_scale(self, scale_id: str) -> ScaleScore | None:
        """Get a scale score by its ID."""
        for scale in self.scales:
            if scale.scale_id == scale_id:
                return scale
        return None


class ScoringEngine:
    """Generic scoring engine that computes scale scores from recoded items.

    The engine reads all scoring rules from the instrument specification:
    - Which items belong to each scale
    - Which items are reverse scored
    - The scoring method (sum, average, sum_then_double)
    - How many missing items are allowed

    No per-questionnaire code is allowed. All behavior is data-driven.
    """

    def score(
        self,
        section: RecodedSection,
        instrument: InstrumentSpec,
    ) -> ScoringResult:
        """Compute all scale scores for a recoded section.

        Args:
            section: The recoded section with numeric values.
            instrument: The instrument specification.

        Returns:
            ScoringResult with scores for all scales.
        """
        # Build lookup for item values
        item_values: dict[str, int | float | None] = {}
        for item in section.items:
            item_values[item.item_id] = item.value

        # Score each scale
        scale_scores: list[ScaleScore] = []
        for scale in instrument.scales:
            score = self._score_scale(scale, item_values, instrument)
            scale_scores.append(score)

        return ScoringResult(
            instrument_id=section.instrument_id,
            instrument_version=section.instrument_version,
            scales=scale_scores,
        )

    def _score_scale(
        self,
        scale,
        item_values: dict[str, int | float | None],
        instrument: InstrumentSpec,
    ) -> ScaleScore:
        """Score a single scale."""
        # Collect values for items in this scale
        values: dict[str, int | float] = {}
        missing_items: list[str] = []

        for item_id in scale.items:
            value = item_values.get(item_id)
            if value is None:
                missing_items.append(item_id)
            else:
                values[item_id] = value

        # Check if too many items are missing
        if len(missing_items) > scale.missing_allowed:
            return ScaleScore(
                scale_id=scale.scale_id,
                name=scale.name,
                value=None,
                method=scale.method,
                items_used=len(values),
                items_total=len(scale.items),
                missing_items=missing_items,
                reversed_items=scale.reversed_items,
                prorated=False,
                error=f"Too many missing items: {len(missing_items)} missing, "
                f"{scale.missing_allowed} allowed",
            )

        # If no values at all, can't score
        if not values:
            return ScaleScore(
                scale_id=scale.scale_id,
                name=scale.name,
                value=None,
                method=scale.method,
                items_used=0,
                items_total=len(scale.items),
                missing_items=missing_items,
                reversed_items=scale.reversed_items,
                prorated=False,
                error="No values available for scoring",
            )

        # Apply reverse scoring if needed
        if scale.reversed_items:
            # Get max value from first item's response map
            # (assuming all items in scale have same response range)
            first_item_id = scale.items[0]
            first_item_spec = instrument.get_item(first_item_id)
            if first_item_spec:
                max_value = get_max_value_for_item(first_item_spec.response_map)
                values = apply_reverse_scoring(values, scale.reversed_items, max_value)

        # Get list of values in scale order
        value_list = [values[item_id] for item_id in scale.items if item_id in values]

        # Compute score
        prorated = len(missing_items) > 0
        if prorated:
            score_value = prorate_score(value_list, scale.method, len(scale.items))
        else:
            score_value = compute_score(value_list, scale.method)

        return ScaleScore(
            scale_id=scale.scale_id,
            name=scale.name,
            value=score_value,
            method=scale.method,
            items_used=len(values),
            items_total=len(scale.items),
            missing_items=missing_items,
            reversed_items=scale.reversed_items,
            prorated=prorated,
            error=None,
        )

    def score_scale(
        self,
        section: RecodedSection,
        instrument: InstrumentSpec,
        scale_id: str,
    ) -> ScaleScore | None:
        """Score a single scale.

        Args:
            section: The recoded section.
            instrument: The instrument specification.
            scale_id: The scale to score.

        Returns:
            ScaleScore for the specified scale, or None if not found.
        """
        scale = instrument.get_scale(scale_id)
        if scale is None:
            return None

        # Build lookup for item values
        item_values: dict[str, int | float | None] = {}
        for item in section.items:
            item_values[item.item_id] = item.value

        return self._score_scale(scale, item_values, instrument)
