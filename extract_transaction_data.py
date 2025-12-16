from typing import Any, Dict, List


def extract_transaction_data(
    transaction_data: List[Dict[str, Any]],
    transaction_type: str,
    wallet_address: str
) -> List[Dict[str, Any]]:
    extracted_data: List[Dict[str, Any]] = []

    for trx in transaction_data:
        # Base transaction fields
        base_transaction: Dict[str, Any] = {}

        # Handle regular transaction data
        if transaction_type in ['internal_transaction', 'transaction']:
            base_transaction.update({
                'Date': trx.get('timeStamp', ''),
                'Sent Amount': trx.get('value', '') if trx.get('from', '') == wallet_address else '',
                'Sent Currency':  'ETH' if trx.get('from', '') == wallet_address else '',
                'Received Amount': trx.get('value', '') if trx.get('to', '') == wallet_address else '',
                'Received Currency': 'ETH' if trx.get('to', '') == wallet_address else '',
                'Fee Amount': str(int(trx.get('gasUsed', '0')) * int(trx.get('gasPrice', '0'))) if trx.get('from', '') == wallet_address else '',
                'Fee Currency': 'ETH' if trx.get('from', '') == wallet_address else '',
                'Net Worth Amount': '',
                'Net Worth Currency': '',
                'Label': '',
                'Description': 'internal' if transaction_type == 'internal_transaction' else 'transaction',
                'TxHash': trx.get('hash', '')
            })

        # Handle token transfer details
        if transaction_type in ['token_transfers']:
            base_transaction.update({
                'Date': trx.get('timeStamp', ''),
                'Sent Amount': trx.get('value', '') if trx.get('from', '') == wallet_address else '',
                'Sent Currency':  trx.get('tokenSymbol', '') if trx.get('from', '') == wallet_address else '',
                'Received Amount': trx.get('value', '') if trx.get('to', '') == wallet_address else '',
                'Received Currency': trx.get('tokenSymbol', '') if trx.get('to', '') == wallet_address else '',
                'Fee Amount': '',  # Not available in token transfer API
                'Fee Currency': '', # Not available in token transfer API
                'Net Worth Amount': '',
                'Net Worth Currency': '',
                'Label': '',
                'Description': 'token_transfer',
                'TxHash': trx.get('hash', '')
            })

        extracted_data.append(base_transaction)

    return extracted_data
