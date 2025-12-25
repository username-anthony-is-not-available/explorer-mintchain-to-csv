import csv
import os
from typing import Dict, List, Union

def write_transaction_data_to_cryptotaxcalculator_csv(output_file: str, transaction_data: List[Dict[str, Union[str, None]]]) -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    header: List[str] = ['Date', 'Type', 'Symbol', 'Currency', 'Volume', 'Price', 'PriceAUD', 'Fee', 'FeeAUD', 'Total', 'TotalAUD']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for trx in transaction_data:
            # NOTE: The Price, PriceAUD, Total, and TotalAUD fields are required by the
            # CryptoTaxCalculator format but are not available in the source data.
            # These fields will be left blank in the output CSV.
            row_data = {
                'Date': trx.get('Date') or '',
                'Type': '',
                'Symbol': '',
                'Currency': '',
                'Volume': '',
                'Price': '',
                'PriceAUD': '',
                'Fee': trx.get('Fee Amount') or '',
                'FeeAUD': '',
                'Total': '',
                'TotalAUD': ''
            }

            sent_amount = trx.get('Sent Amount')
            sent_currency = trx.get('Sent Currency')
            received_amount = trx.get('Received Amount')
            received_currency = trx.get('Received Currency')

            if sent_amount and received_amount:
                if sent_currency in ['USD', 'EUR', 'GBP'] and received_currency not in ['USD', 'EUR', 'GBP']:
                    row_data['Type'] = 'buy'
                    row_data['Symbol'] = received_currency
                    row_data['Currency'] = sent_currency
                    row_data['Volume'] = received_amount
                elif sent_currency not in ['USD', 'EUR', 'GBP'] and received_currency in ['USD', 'EUR', 'GBP']:
                    row_data['Type'] = 'sell'
                    row_data['Symbol'] = sent_currency
                    row_data['Currency'] = received_currency
                    row_data['Volume'] = sent_amount
                else:
                    row_data['Type'] = 'sell'
                    row_data['Symbol'] = sent_currency
                    row_data['Currency'] = received_currency
                    row_data['Volume'] = sent_amount
            elif received_amount:
                row_data['Type'] = 'deposit'
                row_data['Symbol'] = received_currency
                row_data['Volume'] = received_amount
            elif sent_amount:
                row_data['Type'] = 'withdrawal'
                row_data['Symbol'] = sent_currency
                row_data['Volume'] = sent_amount

            writer.writerow([row_data[field] for field in header])
