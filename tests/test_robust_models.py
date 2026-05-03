import pytest
from pydantic import ValidationError
from models import Address, RawTransaction

def test_address_model_string_input():
    # Test that Address can be initialized with a string
    addr = Address.model_validate("0x123")
    assert addr.hash == "0x123"

def test_address_model_dict_input():
    # Test that Address can be initialized with a dictionary
    addr = Address.model_validate({"hash": "0x456"})
    assert addr.hash == "0x456"

def test_raw_transaction_aliases():
    # Test that RawTransaction handles 'transactionHash' alias
    data = {
        "transactionHash": "0xabc",
        "timeStamp": "123456",
        "from": "0xfrom",
        "to": "0xto",
        "value": "100",
        "gas": "21000"
    }
    tx = RawTransaction.model_validate(data)
    assert tx.hash == "0xabc"
    assert tx.gasUsed == "21000"
    assert tx.from_address.hash == "0xfrom"

def test_raw_transaction_missing_gas():
    # Test that RawTransaction handles missing gasUsed/gas
    data = {
        "hash": "0xabc",
        "timeStamp": "123456",
        "from": "0xfrom",
        "to": "0xto",
        "value": "100"
    }
    tx = RawTransaction.model_validate(data)
    assert tx.hash == "0xabc"
    assert tx.gasUsed is None
