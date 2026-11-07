from decimal import Decimal

from decimal_utils import add_exact, multiply_exact
from extract_transaction_data import scale_amount


def test_scale_amount_preserves_large_token_precision():
    assert scale_amount(
        "1234567890123456789012345678901234567891", 18
    ) == "1234567890123456789012.345678901234567891"


def test_add_exact_preserves_digits_beyond_default_context():
    result = add_exact(
        Decimal("123456789012345678901234567890.12345678901234567890"),
        Decimal("0.00000000000000000001"),
    )

    assert result == Decimal("123456789012345678901234567890.12345678901234567891")


def test_multiply_exact_preserves_digits_beyond_default_context():
    result = multiply_exact(
        Decimal("1234567890123456789012.345678901234567890"),
        Decimal("1.23456789"),
    )

    assert result == Decimal("1524157875171467887517.14678875171467887501905210")
