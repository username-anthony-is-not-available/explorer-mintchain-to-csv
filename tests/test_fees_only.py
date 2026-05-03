import pytest
from extract_transaction_data import extract_transaction_data
from models import RawTransaction, Address

def test_extract_transaction_data_fees_only():
    wallet_address = "0xwallet"
    # Transaction where user is sender (should include fee)
    tx1 = RawTransaction.model_validate({
        "hash": "0x1",
        "timeStamp": "1704067200",
        "from": wallet_address,
        "to": "0xother",
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "1000000000"
    })
    # Transaction where user is receiver (should be skipped in fees-only)
    tx2 = RawTransaction.model_validate({
        "hash": "0x2",
        "timeStamp": "1704067200",
        "from": "0xother",
        "to": wallet_address,
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "1000000000"
    })
    
    transaction_data = [tx1, tx2]
    extracted = extract_transaction_data(
        transaction_data, "transaction", wallet_address, "mintchain", fees_only=True
    )
    
    assert len(extracted) == 1
    assert extracted[0].tx_hash == "0x1"
    assert extracted[0].sent_amount is None
    assert extracted[0].received_amount is None
    assert extracted[0].fee_amount == "0.000021"
    assert extracted[0].label == "cost"
    assert "Gas Fee" in extracted[0].description
