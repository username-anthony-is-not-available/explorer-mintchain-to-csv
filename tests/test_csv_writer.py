import os
import csv
from unittest.mock import MagicMock, mock_open, patch
from csv_writer import write_transaction_data_to_csv

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
def test_write_transaction_data_to_csv(mock_makedirs):
    """Tests that transaction data is correctly written to a CSV file."""
    output_file = "test_output.csv"

    # Use mock_open to avoid actual file I/O
    m = mock_open()
    with patch("builtins.open", m):
        write_transaction_data_to_csv(output_file, MOCK_TRANSACTION_DATA)

    # Check that the file was opened for writing
    m.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

    # Check that the header was written correctly
    handle = m()
    handle.write.assert_any_call('Date,Sent Amount,Sent Currency,Received Amount,Received Currency,Fee Amount,Fee Currency,Net Worth Amount,Net Worth Currency,Label,Description,TxHash\r\n')

    # Check that the data row was written correctly
    handle.write.assert_any_call('1673784000,1,ETH,,,21000000000000,ETH,,,,transaction,0x123\r\n')
