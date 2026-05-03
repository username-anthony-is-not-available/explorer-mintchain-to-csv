from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence, Union
from config import NATIVE_CURRENCIES
from models import (
    Raw1155Transfer,
    RawNFTTransfer,
    RawTokenTransfer,
    RawTransaction,
    Transaction,
)
from transaction_categorization import categorize_transaction
from price_service import get_token_price

AnyRawTransaction = Union[
    RawTransaction, RawTokenTransfer, RawNFTTransfer, Raw1155Transfer
]


def scale_amount(amount: str, decimals: int) -> str:
    """Scales an amount from base units to decimal units."""
    if not amount or not amount.isdigit():
        return amount
    scaled = Decimal(amount) / Decimal(10**decimals)
    # Format to string, avoiding scientific notation and stripping trailing zeros
    formatted = format(scaled, "f")
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted if formatted != "" else "0"


def format_timestamp(ts: str) -> str:
    """Formats a unix timestamp into a Koinly-compatible date string."""
    dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def extract_transaction_data(
    transaction_data: Sequence[AnyRawTransaction],
    transaction_type: str,
    wallet_address: str,
    chain: str,
    fees_only: bool = False,
) -> list[Transaction]:
    extracted_data: list[Transaction] = []

    for trx in transaction_data:
        is_sender = trx.from_address.hash.lower() == wallet_address.lower()
        is_receiver = trx.to_address.hash.lower() == wallet_address.lower()

        data = {
            "Date": format_timestamp(trx.timeStamp),
            "timestamp": int(trx.timeStamp),
            "TxHash": trx.hash,
            "Description": "",
            "Sent Amount": None,
            "Sent Currency": None,
            "Received Amount": None,
            "Received Currency": None,
            "Fee Amount": None,
            "Fee Currency": None,
            "Net Worth Amount": "",
            "Net Worth Currency": "",
            "Label": categorize_transaction(trx, chain),
        }

        native_currency = NATIVE_CURRENCIES.get(chain, "ETH")
        if isinstance(trx, RawTransaction):
            data["Description"] = (
                "internal"
                if transaction_type == "internal_transaction"
                else "transaction"
            )
            if is_sender:
                data["Sent Amount"] = scale_amount(trx.value, 18)
                data["Sent Currency"] = native_currency
                if trx.gasPrice and trx.gasUsed:
                    try:
                        fee_value = str(int(trx.gasUsed) * int(trx.gasPrice))
                        data["Fee Amount"] = scale_amount(fee_value, 18)
                        data["Fee Currency"] = native_currency
                    except (ValueError, TypeError):
                        pass
            if is_receiver:
                data["Received Amount"] = scale_amount(trx.value, 18)
                data["Received Currency"] = native_currency

        elif isinstance(trx, RawTokenTransfer):
            data["Description"] = "token_transfer"
            decimals = int(trx.tokenDecimal) if trx.tokenDecimal.isdigit() else 18
            if is_sender:
                data["Sent Amount"] = scale_amount(trx.total.value, decimals)
                data["Sent Currency"] = trx.token.symbol
            if is_receiver:
                data["Received Amount"] = scale_amount(trx.total.value, decimals)
                data["Received Currency"] = trx.token.symbol

        elif isinstance(trx, RawNFTTransfer):
            data["Description"] = "nft_transfer"
            if is_sender:
                data["Sent Amount"] = "1"
                data["Sent Currency"] = trx.tokenSymbol
            if is_receiver:
                data["Received Amount"] = "1"
                data["Received Currency"] = trx.tokenSymbol

        elif isinstance(trx, Raw1155Transfer):
            data["Description"] = "1155_transfer"
            if is_sender:
                data["Sent Amount"] = trx.tokenValue
                data["Sent Currency"] = trx.tokenSymbol
            if is_receiver:
                data["Received Amount"] = trx.tokenValue
                data["Received Currency"] = trx.tokenSymbol

        # Fetch and calculate net worth
        price = None
        amount_to_value = None
        currency_to_value = None

        if data["Sent Amount"] and data["Sent Currency"]:
            amount_to_value = data["Sent Amount"]
            currency_to_value = data["Sent Currency"]
            contract_address = trx.contractAddress if isinstance(trx, RawTokenTransfer) else None
            price = get_token_price(chain, data["timestamp"], contract_address, currency_to_value)
        elif data["Received Amount"] and data["Received Currency"]:
            amount_to_value = data["Received Amount"]
            currency_to_value = data["Received Currency"]
            contract_address = trx.contractAddress if isinstance(trx, RawTokenTransfer) else None
            price = get_token_price(chain, data["timestamp"], contract_address, currency_to_value)

        if price is not None and amount_to_value:
            try:
                net_worth = Decimal(amount_to_value) * price
                formatted_net_worth = format(net_worth, "f")
                if "." in formatted_net_worth:
                    formatted_net_worth = formatted_net_worth.rstrip("0").rstrip(".")
                data["Net Worth Amount"] = formatted_net_worth if formatted_net_worth != "" else "0"
                data["Net Worth Currency"] = "USD"
            except (ValueError, ArithmeticError):
                pass

        if fees_only:
            # For fees-only mode, we only care about transactions where the user paid a fee (is_sender)
            if not is_sender or not data.get("Fee Amount"):
                continue
            # Reset amounts to focus only on fees
            data["Sent Amount"] = None
            data["Sent Currency"] = None
            data["Received Amount"] = None
            data["Received Currency"] = None
            data["Net Worth Amount"] = ""
            data["Net Worth Currency"] = ""
            data["Description"] = f"Gas Fee ({data['Description']})"
            data["Label"] = "cost"

        extracted_data.append(Transaction.model_validate(data))

    return extracted_data
