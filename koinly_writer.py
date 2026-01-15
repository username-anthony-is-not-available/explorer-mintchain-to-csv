import csv
import os
from typing import Dict, List, Union
from models import TransactionType

KOINLY_LABEL_MAP = {
    TransactionType.STAKING.value: "staking",
    TransactionType.AIRDROP.value: "airdrop",
    TransactionType.MINING.value: "mining",
}

def write_transaction_data_to_koinly_csv(output_file: str, transaction_data: List[Dict[str, Union[str, None]]]) -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    processed_transactions = []
    for tx in transaction_data:
        processed_tx = tx.copy()
        label = processed_tx.get("Label")
        if label and label in KOINLY_LABEL_MAP:
            processed_tx["Label"] = KOINLY_LABEL_MAP[label]
        processed_transactions.append(processed_tx)

    fieldnames: List[str] = [
        'Date',
        'Sent Amount',
        'Sent Currency',
        'Received Amount',
        'Received Currency',
        'Fee Amount',
        'Fee Currency',
        'Net Worth Amount',
        'Net Worth Currency',
        'Label',
        'Description',
        'TxHash'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_transactions)
