import csv
import io
import os
from unittest.mock import mock_open, patch, call
from csv_writer import write_transaction_data_to_csv

def test_write_transaction_data_to_csv():
    mock_data = [
        {
            "Date": "1672531200",
            "Sent Amount": "100",
            "Sent Currency": "ETH",
            "Received Amount": None,
            "Received Currency": None,
            "Fee Amount": "0.000021",
            "Fee Currency": "ETH",
            "TxHash": "0xabc",
            "Description": "transaction",
            "Net Worth Amount": "",
            "Net Worth Currency": "",
            "Label": "",
        }
    ]
    output_file = "output/test.csv"

    m = mock_open()
    with patch("builtins.open", m), \
         patch("os.makedirs") as mock_makedirs:
        write_transaction_data_to_csv(output_file, mock_data)

        mock_makedirs.assert_called_once_with(os.path.dirname(output_file), exist_ok=True)
        m.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

        handle = m()

        # Check that the header and data rows were written correctly
        handle.write.assert_has_calls([
            call('Date,Sent Amount,Sent Currency,Received Amount,Received Currency,Fee Amount,Fee Currency,Net Worth Amount,Net Worth Currency,Label,Description,TxHash\r\n'),
            call('1672531200,100,ETH,,,0.000021,ETH,,,,transaction,0xabc\r\n')
        ])

def test_write_multiple_transactions_to_csv():
    mock_data = [
        {
            "Date": "1672531200", "Sent Amount": "100", "Sent Currency": "ETH", "Received Amount": None,
            "Received Currency": None, "Fee Amount": "0.000021", "Fee Currency": "ETH", "TxHash": "0xabc",
            "Description": "transaction", "Net Worth Amount": "", "Net Worth Currency": "", "Label": "",
        },
        {
            "Date": "1672531201", "Sent Amount": None, "Sent Currency": None, "Received Amount": "200",
            "Received Currency": "TKN", "Fee Amount": None, "Fee Currency": None, "TxHash": "0xdef",
            "Description": "token_transfer", "Net Worth Amount": "", "Net Worth Currency": "", "Label": "deposit",
        }
    ]
    output_file = "output/test_multiple.csv"

    m = mock_open()
    with patch("builtins.open", m), \
         patch("os.makedirs") as mock_makedirs:
        write_transaction_data_to_csv(output_file, mock_data)

        mock_makedirs.assert_called_once_with(os.path.dirname(output_file), exist_ok=True)
        m.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

        handle = m()

        handle.write.assert_has_calls([
            call('Date,Sent Amount,Sent Currency,Received Amount,Received Currency,Fee Amount,Fee Currency,Net Worth Amount,Net Worth Currency,Label,Description,TxHash\r\n'),
            call('1672531200,100,ETH,,,0.000021,ETH,,,,transaction,0xabc\r\n'),
            call('1672531201,,,200,TKN,,,,,deposit,token_transfer,0xdef\r\n')
        ])
