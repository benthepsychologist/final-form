"""Reverse scoring utilities.

Applies reverse scoring to specified items by computing (max_value - value).
"""


def apply_reverse_scoring(
    values: dict[str, int | float],
    reversed_items: list[str],
    max_value: int,
) -> dict[str, int | float]:
    """Apply reverse scoring to specified items.

    Reverse scoring transforms a value by computing (max_value - value).
    For example, if max_value is 3 and value is 1, the reversed value is 2.

    Args:
        values: Dictionary mapping item_id to value.
        reversed_items: List of item_ids that should be reverse scored.
        max_value: The maximum value in the response scale.

    Returns:
        Dictionary with reverse scoring applied to specified items.
    """
    result = dict(values)

    for item_id in reversed_items:
        if item_id in result and result[item_id] is not None:
            original = result[item_id]
            result[item_id] = max_value - original

    return result


def get_max_value_for_item(response_map: dict[str, int]) -> int:
    """Get the maximum value from a response map.

    Args:
        response_map: Dictionary mapping response text to numeric value.

    Returns:
        The maximum numeric value in the response map.
    """
    return max(response_map.values())
