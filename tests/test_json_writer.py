import os
import json
from unittest.mock import MagicMock, mock_open, patch
from json_writer import write_transaction_data_to_json

# Mock data for testing
MOCK_TRANSACTION_DATA = [
    {
        "Date": "1673784000",
        "Sent Amount": "1",
        "Sent Currency": "ETH",
        "Received Amount": "",
        "Received Currency": "",
        "Fee Amount": "21000000000000",
        "Fee Currency": "ETH",
        "Net Worth Amount": "",
        "Net Worth Currency": "",
        "Label": "",
        "Description": "transaction",
        "TxHash": "0x123",
    }
]

@patch("os.makedirs")
@patch("json.dump")
def test_write_transaction_data_to_json(mock_json_dump, mock_makedirs):
    """Tests that transaction data is correctly written to a JSON file."""
    output_file = "test_output.json"

    # Use mock_open to avoid actual file I/O
    m = mock_open()
    with patch("builtins.open", m):
        write_transaction_data_to_json(output_file, MOCK_TRANSACTION_DATA)

    # Check that the file was opened for writing
    m.assert_called_once_with(output_file, 'w', encoding='utf-8')

    # Check that json.dump was called with the correct data
    mock_json_dump.assert_called_once_with(MOCK_TRANSACTION_DATA, m(), indent=4)
