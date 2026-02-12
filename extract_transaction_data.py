from decimal import Decimal
from typing import Sequence, Union
from models import RawTokenTransfer, RawTransaction, Transaction
from transaction_categorization import categorize_transaction

AnyRawTransaction = Union[RawTransaction, RawTokenTransfer]

def scale_amount(amount: str, decimals: int) -> str:
    """Scales an amount from base units to decimal units."""
    if not amount or not amount.isdigit():
        return amount
    scaled = Decimal(amount) / Decimal(10**decimals)
    # Format to string, avoiding scientific notation and stripping trailing zeros
    formatted = format(scaled, 'f')
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted if formatted != "" else "0"

def extract_transaction_data(
    transaction_data: Sequence[AnyRawTransaction],
    transaction_type: str,
    wallet_address: str,
    chain: str
) -> list[Transaction]:
    extracted_data: list[Transaction] = []

    for trx in transaction_data:
        is_sender = trx.from_address.hash.lower() == wallet_address.lower()
        is_receiver = trx.to_address.hash.lower() == wallet_address.lower()

        data = {
            'Date': trx.timeStamp,
            'TxHash': trx.hash,
            'Description': '',
            'Sent Amount': None,
            'Sent Currency': None,
            'Received Amount': None,
            'Received Currency': None,
            'Fee Amount': None,
            'Fee Currency': None,
            'Net Worth Amount': '',
            'Net Worth Currency': '',
            'Label': categorize_transaction(trx, chain),
        }

        if isinstance(trx, RawTransaction):
            data['Description'] = 'internal' if transaction_type == 'internal_transaction' else 'transaction'
            if is_sender:
                data['Sent Amount'] = scale_amount(trx.value, 18)
                data['Sent Currency'] = 'ETH'
                fee_value = str(int(trx.gasUsed) * int(trx.gasPrice))
                data['Fee Amount'] = scale_amount(fee_value, 18)
                data['Fee Currency'] = 'ETH'
            if is_receiver:
                data['Received Amount'] = scale_amount(trx.value, 18)
                data['Received Currency'] = 'ETH'

        elif isinstance(trx, RawTokenTransfer):
            data['Description'] = 'token_transfer'
            decimals = int(trx.tokenDecimal) if trx.tokenDecimal.isdigit() else 18
            if is_sender:
                data['Sent Amount'] = scale_amount(trx.total.value, decimals)
                data['Sent Currency'] = trx.token.symbol
            if is_receiver:
                data['Received Amount'] = scale_amount(trx.total.value, decimals)
                data['Received Currency'] = trx.token.symbol

        extracted_data.append(Transaction.model_validate(data))

    return extracted_data
