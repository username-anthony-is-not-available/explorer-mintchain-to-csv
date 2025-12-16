import json
import os
from typing import Any, Dict, List


def write_transaction_data_to_json(output_file: str, transaction_data: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure the output directory exists

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transaction_data, f, indent=4)
