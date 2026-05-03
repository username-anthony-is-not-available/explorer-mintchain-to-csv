import pytest
from pydantic import ValidationError
from models import Transaction, TransactionType

def test_transaction_valid():
    data = {
        "Date": "2024-01-01 00:00:00 UTC",
        "timestamp": 1704067200,
        "Sent Amount": "1.5",
        "Sent Currency": "ETH",
        "TxHash": "0x123",
        "Description": "test",
        "Label": TransactionType.SWAP
    }
    tx = Transaction.model_validate(data)
    assert tx.sent_amount == "1.5"
    assert tx.sent_currency == "ETH"
    assert tx.label == "swap"

def test_transaction_invalid_currency_missing():
    data = {
        "Date": "2024-01-01 00:00:00 UTC",
        "timestamp": 1704067200,
        "Sent Amount": "1.5",
        "TxHash": "0x123",
        "Description": "test"
    }
    with pytest.raises(ValidationError) as excinfo:
        Transaction.model_validate(data)
    assert "sent_currency must be provided if sent_amount is set" in str(excinfo.value)

def test_transaction_label_string():
    data = {
        "Date": "2024-01-01 00:00:00 UTC",
        "timestamp": 1704067200,
        "TxHash": "0x123",
        "Description": "test",
        "Label": "custom_label"
    }
    tx = Transaction.model_validate(data)
    assert tx.label == "custom_label"

def test_transaction_label_enum_value():
    data = {
        "Date": "2024-01-01 00:00:00 UTC",
        "timestamp": 1704067200,
        "TxHash": "0x123",
        "Description": "test",
        "Label": "bridge"
    }
    tx = Transaction.model_validate(data)
    assert tx.label == "bridge"
