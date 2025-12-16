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
                'Date': trx.get('timestamp', ''),
                'Sent Amount': trx.get('value', '') if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Sent Currency':  'ETH' if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Received Amount': trx.get('value', '') if trx.get('to', {}).get('hash', '') == wallet_address else '',
                'Received Currency': 'ETH' if trx.get('to', {}).get('hash', '') == wallet_address else '',
                'Fee Amount': trx.get('fee', '') if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Fee Currency': 'ETH' if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Net Worth Amount': '',
                'Net Worth Currency': '',
                'Label': '',
                'Description': trx.get('type', ''),
                'TxHash': trx.get('tx_hash', '')
            })

        # Handle token transfer details
        if transaction_type in ['token_transfers']:
            base_transaction.update({
                'Date': trx.get('timestamp', ''),
                'Sent Amount': trx.get('total', {}).get('value', '') if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Sent Currency':  trx.get('token', {}).get('symbol', '') if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Received Amount': trx.get('total', {}).get('value', '') if trx.get('to', {}).get('hash', '') == wallet_address else '',
                'Received Currency': trx.get('token', {}).get('symbol', '') if trx.get('to', {}).get('hash', '') == wallet_address else '',
                'Fee Amount': trx.get('fee', '') if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Fee Currency': 'ETH' if trx.get('from', {}).get('hash', '') == wallet_address else '',
                'Net Worth Amount': '',
                'Net Worth Currency': '',
                'Label': '',
                'Description': trx.get('type', ''),
                'TxHash': trx.get('tx_hash', '')
            })

        extracted_data.append(base_transaction)

    return extracted_data
