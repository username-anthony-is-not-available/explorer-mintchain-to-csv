import pytest
from pydantic import ValidationError
from models import Address, Token, Total, RawTransaction, RawTokenTransfer, Transaction

def test_address_model():
    addr = Address(hash="0x123")
    assert addr.hash == "0x123"

def test_token_model():
    token = Token(symbol="ETH")
    assert token.symbol == "ETH"

def test_total_model():
    total = Total(value="100")
    assert total.value == "100"

def test_raw_transaction_model():
    data = {
        "hash": "0xabc",
        "timeStamp": "1234567890",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "value": "1000",
        "gasUsed": "21000",
        "gasPrice": "50"
    }
    trx = RawTransaction.model_validate(data)
    assert trx.hash == "0xabc"
    assert trx.from_address.hash == "0xfrom"

def test_raw_token_transfer_model():
    data = {
        "hash": "0xdef",
        "timeStamp": "1234567890",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "total": {"value": "500"},
        "token": {"symbol": "TOK"},
        "tokenDecimal": "18"
    }
    trx = RawTokenTransfer.model_validate(data)
    assert trx.hash == "0xdef"
    assert trx.token.symbol == "TOK"

def test_transaction_model():
    data = {
        "Date": "1234567890",
        "Description": "test",
        "TxHash": "0xghi"
    }
    trx = Transaction.model_validate(data)
    assert trx.date == "1234567890"

def test_invalid_raw_transaction():
    with pytest.raises(ValidationError):
        RawTransaction.model_validate({"hash": "0xabc"})

def test_invalid_raw_token_transfer():
    with pytest.raises(ValidationError):
        RawTokenTransfer.model_validate({"hash": "0xdef"})

def test_invalid_transaction():
    with pytest.raises(ValidationError):
        Transaction.model_validate({"Date": "123"})
