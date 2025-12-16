import json
import os


def write_transaction_data_to_json(output_file, transaction_data):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the output directory exists

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transaction_data, f, indent=4)
