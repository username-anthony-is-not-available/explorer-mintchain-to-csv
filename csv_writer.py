import csv
import os


def write_transaction_data_to_csv(output_file, transaction_data):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the output directory exists

    fieldnames = ['Date', 'Sent Amount', 'Sent Currency', 'Received Amount', 'Received Currency',
                  'Fee Amount', 'Fee Currency', 'Net Worth Amount', 'Net Worth Currency',
                  'Label', 'Description', 'TxHash']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for trx in transaction_data:
            writer.writerow(trx)
