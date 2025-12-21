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

        sender_address = trx.get('from', {}).get('hash', '')
        receiver_address = trx.get('to', {}).get('hash', '')

        # Handle regular transaction data
        if transaction_type in ['internal_transaction', 'transaction']:
            is_sender = sender_address == wallet_address
            is_receiver = receiver_address == wallet_address

            base_transaction.update({
                'Date': trx.get('timeStamp', ''),
                'Sent Amount': trx.get('value', '') if is_sender else '',
                'Sent Currency': 'ETH' if is_sender else '',
                'Received Amount': trx.get('value', '') if is_receiver else '',
                'Received Currency': 'ETH' if is_receiver else '',
                'Fee Amount': f"{(int(trx.get('gasUsed', '0')) * int(trx.get('gasPrice', '0'))) / 1e18:.6f}" if is_sender else '',
                'Fee Currency': 'ETH' if is_sender else '',
                'Net Worth Amount': '',
                'Net Worth Currency': '',
                'Label': '',
                'Description': 'internal' if transaction_type == 'internal_transaction' else 'transaction',
                'TxHash': trx.get('hash', '')
            })

        # Handle token transfer details
        if transaction_type in ['token_transfers']:
            is_sender = sender_address == wallet_address
            is_receiver = receiver_address == wallet_address

            base_transaction.update({
                'Date': trx.get('timeStamp', ''),
                'Sent Amount': trx.get('total', {}).get('value', '') if is_sender else '',
                'Sent Currency': trx.get('token', {}).get('symbol', '') if is_sender else '',
                'Received Amount': trx.get('total', {}).get('value', '') if is_receiver else '',
                'Received Currency': trx.get('token', {}).get('symbol', '') if is_receiver else '',
                'Fee Amount': '',
                'Fee Currency': '',
                'Net Worth Amount': '',
                'Net Worth Currency': '',
                'Label': '',
                'Description': 'token_transfer',
                'TxHash': trx.get('hash', '')
            })

        extracted_data.append(base_transaction)

    return extracted_data
