from decimal import Decimal
from typing import Dict, List
from models import Transaction

def calculate_token_balances(transactions: List[Transaction]) -> Dict[str, Decimal]:
    """
    Calculates the final balance for each token symbol found in the transactions.
    """
    balances: Dict[str, Decimal] = {}

    for tx in transactions:
        # Handle Sent Amount
        if tx.sent_amount and tx.sent_currency:
            symbol = tx.sent_currency
            amount = Decimal(tx.sent_amount)
            balances[symbol] = balances.get(symbol, Decimal(0)) - amount

        # Handle Received Amount
        if tx.received_amount and tx.received_currency:
            symbol = tx.received_currency
            amount = Decimal(tx.received_amount)
            balances[symbol] = balances.get(symbol, Decimal(0)) + amount

        # Handle Fee (Fees are always sent)
        if tx.fee_amount and tx.fee_currency:
            symbol = tx.fee_currency
            amount = Decimal(tx.fee_amount)
            balances[symbol] = balances.get(symbol, Decimal(0)) - amount

    return balances

def format_balance_summary(balances: Dict[str, Decimal]) -> str:
    """
    Formats the balance dictionary into a human-readable table string.
    """
    if not balances:
        return "No token transactions found to calculate balances."

    lines = ["", "--- Token Balance Audit Summary ---", f"{'Token':<15} | {'Balance':>20}"]
    lines.append("-" * 38)
    
    # Sort by symbol for readability
    for symbol in sorted(balances.keys()):
        balance = balances[symbol]
        # Format balance to string, stripping trailing zeros
        formatted_balance = format(balance, "f")
        if "." in formatted_balance:
            formatted_balance = formatted_balance.rstrip("0").rstrip(".")
        if formatted_balance == "":
            formatted_balance = "0"
            
        lines.append(f"{symbol:<15} | {formatted_balance:>20}")
    
    lines.append("-" * 38)
    return "\n".join(lines)
