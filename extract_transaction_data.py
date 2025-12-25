from typing import Sequence, Union
from models import RawTokenTransfer, RawTransaction, Transaction
from transaction_categorization import categorize_transaction

AnyRawTransaction = Union[RawTransaction, RawTokenTransfer]

def extract_transaction_data(
    transaction_data: Sequence[AnyRawTransaction],
    transaction_type: str,
    wallet_address: str
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
            'Label': categorize_transaction(trx),
        }

        if isinstance(trx, RawTransaction):
            data['Description'] = 'internal' if transaction_type == 'internal_transaction' else 'transaction'
            if is_sender:
                data['Sent Amount'] = trx.value
                data['Sent Currency'] = 'ETH'
                data['Fee Amount'] = f"{(int(trx.gasUsed) * int(trx.gasPrice)) / 1e18:.6f}"
                data['Fee Currency'] = 'ETH'
            if is_receiver:
                data['Received Amount'] = trx.value
                data['Received Currency'] = 'ETH'

        elif isinstance(trx, RawTokenTransfer):
            data['Description'] = 'token_transfer'
            if is_sender:
                data['Sent Amount'] = trx.total.value
                data['Sent Currency'] = trx.token.symbol
            if is_receiver:
                data['Received Amount'] = trx.total.value
                data['Received Currency'] = trx.token.symbol

        extracted_data.append(Transaction.model_validate(data))

    return extracted_data
