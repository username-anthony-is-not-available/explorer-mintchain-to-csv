from decimal import Decimal
from balance_utils import calculate_token_balances, format_balance_summary
from models import Transaction

def test_calculate_token_balances():
    transactions = [
        Transaction.model_validate({
            "Date": "2024-01-01 00:00:00 UTC",
            "timestamp": 1,
            "Received Amount": "10.5",
            "Received Currency": "ETH",
            "TxHash": "0x1",
            "Description": "test"
        }),
        Transaction.model_validate({
            "Date": "2024-01-01 01:00:00 UTC",
            "timestamp": 2,
            "Sent Amount": "5.0",
            "Sent Currency": "ETH",
            "TxHash": "0x2",
            "Description": "test",
            "Fee Amount": "0.1",
            "Fee Currency": "ETH"
        }),
        Transaction.model_validate({
            "Date": "2024-01-01 02:00:00 UTC",
            "timestamp": 3,
            "Received Amount": "100.0",
            "Received Currency": "USDC",
            "TxHash": "0x3",
            "Description": "test"
        })
    ]
    
    balances = calculate_token_balances(transactions)
    
    assert balances["ETH"] == Decimal("5.4")  # 10.5 - 5.0 - 0.1
    assert balances["USDC"] == Decimal("100.0")

def test_format_balance_summary():
    balances = {
        "ETH": Decimal("5.400000"),
        "USDC": Decimal("100.0")
    }
    summary = format_balance_summary(balances)
    assert "ETH" in summary
    assert "5.4" in summary
    assert "USDC" in summary
    assert "100" in summary
