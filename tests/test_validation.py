import pytest
from pydantic import ValidationError
from models import (
    Address,
    Raw1155Transfer,
    RawNFTTransfer,
    RawTokenTransfer,
    RawTransaction,
    Token,
    Total,
    Transaction,
)

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
            "tokenDecimal": "18",
            "contractAddress": "0xtok"
    }
    trx = RawTokenTransfer.model_validate(data)
    assert trx.hash == "0xdef"
    assert trx.token.symbol == "TOK"

def test_transaction_model():
    data = {
        "Date": "2023-01-01 00:00:00 UTC",
        "timestamp": 1234567890,
        "Description": "test",
        "TxHash": "0xghi"
    }
    trx = Transaction.model_validate(data)
    assert trx.date == "2023-01-01 00:00:00 UTC"
    assert trx.timestamp == 1234567890

def test_raw_transaction_no_gas_price():
    data = {
        "hash": "0xabc",
        "timeStamp": "1234567890",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "value": "1000",
        "gasUsed": "21000"
    }
    trx = RawTransaction.model_validate(data)
    assert trx.gasPrice is None

def test_invalid_raw_transaction():
    with pytest.raises(ValidationError):
        RawTransaction.model_validate({"hash": "0xabc"})

def test_invalid_raw_token_transfer():
    with pytest.raises(ValidationError):
        RawTokenTransfer.model_validate({"hash": "0xdef"})

def test_invalid_transaction():
    with pytest.raises(ValidationError):
        Transaction.model_validate({"Date": "123"})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("timeStamp", "not-a-timestamp"),
        ("value", "1.25"),
        ("gasUsed", "-1"),
        ("gasPrice", "0x5208"),
    ],
)
def test_raw_transaction_rejects_invalid_integer_formats(field, value):
    data = {
        "hash": "0xabc",
        "timeStamp": "1234567890",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "value": "1000",
        "gasUsed": "21000",
        "gasPrice": "50",
    }
    data[field] = value

    with pytest.raises(ValidationError):
        RawTransaction.model_validate(data)


def test_raw_token_transfer_rejects_invalid_amount_and_decimals():
    data = {
        "hash": "0xdef",
        "timeStamp": "1234567890",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "total": {"value": "10.5"},
        "token": {"symbol": "TOK"},
        "tokenDecimal": "6",
        "contractAddress": "0xtok",
    }

    with pytest.raises(ValidationError):
        RawTokenTransfer.model_validate(data)

    data["total"]["value"] = "10"
    data["tokenDecimal"] = "six"
    with pytest.raises(ValidationError):
        RawTokenTransfer.model_validate(data)


def test_raw_nft_and_erc1155_models_reject_invalid_integer_fields():
    nft_data = {
        "hash": "0xnft",
        "timeStamp": "1234567890",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "tokenID": "one",
        "tokenName": "NFT",
        "tokenSymbol": "NFT",
    }
    erc1155_data = {
        "hash": "0x1155",
        "timeStamp": "1234567890",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "tokenID": "1",
        "tokenValue": "1.5",
        "tokenName": "Multi-token",
        "tokenSymbol": "MTK",
    }

    with pytest.raises(ValidationError):
        RawNFTTransfer.model_validate(nft_data)
    with pytest.raises(ValidationError):
        Raw1155Transfer.model_validate(erc1155_data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("Sent Amount", "NaN"),
        ("Received Amount", "-0.1"),
        ("Fee Amount", "1.2.3"),
        ("Net Worth Amount", "Infinity"),
    ],
)
def test_transaction_rejects_invalid_decimal_amounts(field, value):
    data = {
        "Date": "2023-01-01 00:00:00 UTC",
        "timestamp": 1,
        "Sent Currency": "TOK",
        "Received Currency": "TOK",
        "Fee Currency": "ETH",
        "Net Worth Currency": "USD",
        "Description": "test",
        "TxHash": "0xabc",
        field: value,
    }

    with pytest.raises(ValidationError):
        Transaction.model_validate(data)


def test_transaction_rejects_negative_timestamp():
    with pytest.raises(ValidationError):
        Transaction.model_validate(
            {
                "Date": "2023-01-01 00:00:00 UTC",
                "timestamp": -1,
                "Description": "test",
                "TxHash": "0xabc",
            }
        )
