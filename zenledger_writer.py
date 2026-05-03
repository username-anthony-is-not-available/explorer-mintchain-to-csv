import csv
import os
from typing import Dict, List, Union

def map_transaction_type(tx: Dict[str, Union[str, None]]) -> str:
    """
    Maps transaction data to ZenLedger transaction types.
    """
    sent_amount = tx.get("Sent Amount")
    received_amount = tx.get("Received Amount")
    label = tx.get("Label")

    if label == "swap":
        return "trade"
    if sent_amount and received_amount:
        return "trade"
    if sent_amount:
        return "send"
    if received_amount:
        return "receive"
    return "send"  # Default to send if only fee is present

def write_transaction_data_to_zenledger_csv(
    output_file: str,
    transaction_data: List[Dict[str, Union[str, None]]]
) -> None:
    """
    Writes transaction data to a ZenLedger-compatible CSV file.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    zenledger_data = []
    for tx in transaction_data:
        zenledger_tx = {
            "Timestamp": tx.get("Date"),
            "Type": map_transaction_type(tx),
            "IN Amount": tx.get("Received Amount"),
            "IN Currency": tx.get("Received Currency"),
            "OUT Amount": tx.get("Sent Amount"),
            "OUT Currency": tx.get("Sent Currency"),
            "Fee Amount": tx.get("Fee Amount"),
            "Fee Currency": tx.get("Fee Currency"),
        }
        zenledger_data.append(zenledger_tx)

    fieldnames = [
        "Timestamp",
        "Type",
        "IN Amount",
        "IN Currency",
        "OUT Amount",
        "OUT Currency",
        "Fee Amount",
        "Fee Currency",
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(zenledger_data)
