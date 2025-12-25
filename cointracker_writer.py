import csv
import os
from typing import Dict, List, Union

def write_transaction_data_to_cointracker_csv(output_file: str, transaction_data: List[Dict[str, Union[str, None]]]) -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the output directory exists

    fieldnames: List[str] = ['Date', 'Received Quantity', 'Received Currency', 'Sent Quantity', 'Sent Currency',
                             'Fee Amount', 'Fee Currency', 'Tag']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for trx in transaction_data:
            writer.writerow({
                'Date': trx.get('Date'),
                'Received Quantity': trx.get('Received Amount'),
                'Received Currency': trx.get('Received Currency'),
                'Sent Quantity': trx.get('Sent Amount'),
                'Sent Currency': trx.get('Sent Currency'),
                'Fee Amount': trx.get('Fee Amount'),
                'Fee Currency': trx.get('Fee Currency'),
                'Tag': trx.get('Label')
            })
