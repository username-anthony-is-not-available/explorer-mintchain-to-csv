"""Helpers for exact arithmetic with currency and token amounts."""

from decimal import Decimal, localcontext


def _addition_precision(left: Decimal, right: Decimal) -> int:
    """Return enough significant digits to add two finite Decimal values exactly."""
    values = (left, right)
    nonzero_values = [value for value in values if value]
    if not nonzero_values:
        return 1

    highest_adjusted = max(value.adjusted() for value in nonzero_values)
    lowest_exponent = min(value.as_tuple().exponent for value in values)
    return max(1, highest_adjusted - lowest_exponent + 1)


def add_exact(left: Decimal, right: Decimal) -> Decimal:
    """Add two Decimal values without rounding away lower-order digits."""
    with localcontext() as context:
        context.prec = max(context.prec, _addition_precision(left, right))
        return left + right


def multiply_exact(left: Decimal, right: Decimal) -> Decimal:
    """Multiply two Decimal values without rounding away significant digits."""
    precision = max(
        1,
        len(left.as_tuple().digits) + len(right.as_tuple().digits),
    )
    with localcontext() as context:
        context.prec = max(context.prec, precision)
        return left * right
