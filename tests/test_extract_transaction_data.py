from models import RawTokenTransfer, RawTransaction, Transaction, Address, Token, Total
from extract_transaction_data import extract_transaction_data

WALLET_ADDRESS = "0x1234567890123456789012345678901234567890"

def test_extract_transaction_data_regular_transaction_sent():
    raw_trx_data = {
        "hash": "0xabc",
        "from": {"hash": WALLET_ADDRESS},
        "to": {"hash": "0x456"},
        "value": "1000000000000000000", # 1 ETH
        "timeStamp": "1672531200",
        "gasUsed": "21000",
        "gasPrice": "1000000000"
    }
    raw_trx = RawTransaction.model_validate(raw_trx_data)
    transactions = extract_transaction_data([raw_trx], "transaction", WALLET_ADDRESS, "mintchain")
    assert len(transactions) == 1
    trx = transactions[0]
    assert trx.sent_amount == "1"
    assert trx.sent_currency == "ETH"
    assert trx.fee_amount == "0.000021"
    assert trx.fee_currency == "ETH"
    assert trx.received_amount is None

def test_extract_transaction_data_regular_transaction_received():
    raw_trx_data = {
        "hash": "0xabc",
        "from": {"hash": "0x456"},
        "to": {"hash": WALLET_ADDRESS},
        "value": "2500000000000000000", # 2.5 ETH
        "timeStamp": "1672531200",
        "gasUsed": "21000",
        "gasPrice": "1000000000"
    }
    raw_trx = RawTransaction.model_validate(raw_trx_data)
    transactions = extract_transaction_data([raw_trx], "transaction", WALLET_ADDRESS, "mintchain")
    assert len(transactions) == 1
    trx = transactions[0]
    assert trx.received_amount == "2.5"
    assert trx.received_currency == "ETH"
    assert trx.sent_amount is None
    assert trx.fee_amount is None

def test_extract_transaction_data_token_transfer_sent():
    raw_token_trx_data = {
        "hash": "0xdef",
        "from": {"hash": WALLET_ADDRESS},
        "to": {"hash": "0x456"},
        "timeStamp": "1672531201",
        "total": {"value": "2000000"},
        "token": {"symbol": "USDC"},
        "tokenDecimal": "6"
    }
    raw_token_trx = RawTokenTransfer.model_validate(raw_token_trx_data)
    transactions = extract_transaction_data([raw_token_trx], "token_transfers", WALLET_ADDRESS, "mintchain")
    assert len(transactions) == 1
    trx = transactions[0]
    assert trx.sent_amount == "2"
    assert trx.sent_currency == "USDC"
    assert trx.received_amount is None
    assert trx.fee_amount is None

def test_extract_transaction_data_token_transfer_received():
    raw_token_trx_data = {
        "hash": "0xdef",
        "from": {"hash": "0x456"},
        "to": {"hash": WALLET_ADDRESS},
        "timeStamp": "1672531201",
        "total": {"value": "500000000000000000000"}, # 500 TKN
        "token": {"symbol": "TKN"},
        "tokenDecimal": "18"
    }
    raw_token_trx = RawTokenTransfer.model_validate(raw_token_trx_data)
    transactions = extract_transaction_data([raw_token_trx], "token_transfers", WALLET_ADDRESS, "mintchain")
    assert len(transactions) == 1
    trx = transactions[0]
    assert trx.received_amount == "500"
    assert trx.received_currency == "TKN"
    assert trx.sent_amount is None
    assert trx.fee_amount is None

def test_extract_transaction_data_internal_transaction_sent():
    raw_trx_data = {
        "hash": "0xghi",
        "from": {"hash": WALLET_ADDRESS},
        "to": {"hash": "0x456"},
        "value": "300000000000000000", # 0.3 ETH
        "timeStamp": "1672531202",
        "gasUsed": "21000",
        "gasPrice": "1000000000"
    }
    raw_trx = RawTransaction.model_validate(raw_trx_data)
    transactions = extract_transaction_data([raw_trx], "internal_transaction", WALLET_ADDRESS, "mintchain")
    assert len(transactions) == 1
    trx = transactions[0]
    assert trx.description == "internal"
    assert trx.sent_amount == "0.3"
    assert trx.sent_currency == "ETH"
    assert trx.fee_amount == "0.000021"
    assert trx.fee_currency == "ETH"
    assert trx.received_amount is None

def test_extract_transaction_data_internal_transaction_received():
    raw_trx_data = {
        "hash": "0xghi",
        "from": {"hash": "0x456"},
        "to": {"hash": WALLET_ADDRESS},
        "value": "450000000000000000", # 0.45 ETH
        "timeStamp": "1672531202",
        "gasUsed": "21000",
        "gasPrice": "1000000000"
    }
    raw_trx = RawTransaction.model_validate(raw_trx_data)
    transactions = extract_transaction_data([raw_trx], "internal_transaction", WALLET_ADDRESS, "mintchain")
    assert len(transactions) == 1
    trx = transactions[0]
    assert trx.description == "internal"
    assert trx.received_amount == "0.45"
    assert trx.received_currency == "ETH"
    assert trx.sent_amount is None
    assert trx.fee_amount is None
