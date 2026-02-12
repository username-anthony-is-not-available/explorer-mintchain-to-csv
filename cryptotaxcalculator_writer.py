import csv
import os
from typing import Dict, List, Union

def write_transaction_data_to_cryptotaxcalculator_csv(output_file: str, transaction_data: List[Dict[str, Union[str, None]]]) -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    header = ['Timestamp (UTC)', 'Type', 'Base Currency', 'Base Amount', 'Quote Currency', 'Quote Amount', 'Fee Currency', 'Fee Amount', 'ID']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for trx in transaction_data:
            row_data = {
                'Timestamp (UTC)': trx.get('Date') or '',
                'Type': '',
                'Base Currency': '',
                'Base Amount': '',
                'Quote Currency': '',
                'Quote Amount': '',
                'Fee Currency': trx.get('Fee Currency') or '',
                'Fee Amount': trx.get('Fee Amount') or '',
                'ID': trx.get('TxHash') or ''
            }

            label = trx.get('Label')
            sent_amount = trx.get('Sent Amount')
            sent_currency = trx.get('Sent Currency')
            received_amount = trx.get('Received Amount')
            received_currency = trx.get('Received Currency')

            # Start with a robust fallback based on Sent/Received amounts
            if sent_amount and received_amount:
                # Default for any swap is 'sell'
                row_data['Type'] = 'sell'
                row_data['Base Currency'] = sent_currency
                row_data['Base Amount'] = sent_amount
                row_data['Quote Currency'] = received_currency
                row_data['Quote Amount'] = received_amount
            elif sent_amount:
                row_data['Type'] = 'send'
                row_data['Base Currency'] = sent_currency
                row_data['Base Amount'] = sent_amount
            elif received_amount:
                row_data['Type'] = 'receive'
                row_data['Base Currency'] = received_currency
                row_data['Base Amount'] = received_amount

            # Refine classification with the label if it exists
            if label == 'swap':
                fiat_currencies = ['USD', 'EUR', 'GBP', 'AUD']
                sent_is_fiat = sent_currency in fiat_currencies
                received_is_fiat = received_currency in fiat_currencies

                if sent_is_fiat and not received_is_fiat:
                    row_data['Type'] = 'buy'
                    row_data['Base Currency'] = received_currency
                    row_data['Base Amount'] = received_amount
                    row_data['Quote Currency'] = sent_currency
                    row_data['Quote Amount'] = sent_amount
                # The 'sell' case is already handled by the default logic

            writer.writerow([row_data[field] for field in header])
