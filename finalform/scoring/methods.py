"""Scoring methods for computing scale scores.

Supports sum, average, and sum_then_double methods.
"""

from typing import Literal


def compute_score(
    values: list[int | float],
    method: Literal["sum", "average", "sum_then_double"],
) -> float:
    """Compute a scale score using the specified method.

    Args:
        values: List of item values (must not contain None).
        method: The scoring method to use.

    Returns:
        The computed score.

    Raises:
        ValueError: If method is unknown or values list is empty.
    """
    if not values:
        raise ValueError("Cannot compute score from empty values list")

    if method == "sum":
        return float(sum(values))

    elif method == "average":
        return sum(values) / len(values)

    elif method == "sum_then_double":
        return float(sum(values) * 2)

    else:
        raise ValueError(f"Unknown scoring method: {method}")


def prorate_score(
    values: list[int | float],
    method: Literal["sum", "average", "sum_then_double"],
    total_items: int,
) -> float:
    """Compute a prorated score when some items are missing.

    For sum-based methods, prorates by scaling up based on the proportion
    of items answered. For average, simply uses the available values.

    Args:
        values: List of available item values.
        method: The scoring method to use.
        total_items: The total number of items in the scale.

    Returns:
        The prorated score.
    """
    if not values:
        raise ValueError("Cannot compute prorated score from empty values list")

    if method == "average":
        # Average doesn't need prorating - just compute mean of available values
        return sum(values) / len(values)

    # For sum-based methods, scale up proportionally
    available_items = len(values)
    proportion = total_items / available_items
    raw_score = sum(values)

    if method == "sum":
        return raw_score * proportion

    elif method == "sum_then_double":
        return raw_score * proportion * 2

    else:
        raise ValueError(f"Unknown scoring method: {method}")
