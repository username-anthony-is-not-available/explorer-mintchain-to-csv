import os
import csv
from unittest.mock import mock_open, patch
from cryptotaxcalculator_writer import write_transaction_data_to_cryptotaxcalculator_csv

def test_write_transaction_data_to_cryptotaxcalculator_csv():
    mock_data = [
        # DeFi Swap - Fiat to Crypto (Buy)
        {'Date': '2024-01-01 12:00:00', 'Sent Amount': '1000', 'Sent Currency': 'USD', 'Received Amount': '0.5', 'Received Currency': 'ETH', 'Label': 'defi_swap', 'Fee Amount': '10', 'Fee Currency': 'USD', 'TxHash': '0x1'},
        # DeFi Swap - Crypto to Fiat (Sell)
        {'Date': '2024-01-02 12:00:00', 'Sent Amount': '0.5', 'Sent Currency': 'ETH', 'Received Amount': '1000', 'Received Currency': 'USD', 'Label': 'defi_swap', 'Fee Amount': '0.001', 'Fee Currency': 'ETH', 'TxHash': '0x2'},
        # Simple Transfer - Send
        {'Date': '2024-01-03 12:00:00', 'Sent Amount': '100', 'Sent Currency': 'USDC', 'Received Amount': None, 'Received Currency': None, 'Label': 'simple_transfer', 'Fee Amount': '5', 'Fee Currency': 'ETH', 'TxHash': '0x3'},
        # Simple Transfer - Receive
        {'Date': '2024-01-04 12:00:00', 'Sent Amount': None, 'Sent Currency': None, 'Received Amount': '100', 'Received Currency': 'USDC', 'Label': 'simple_transfer', 'Fee Amount': '0', 'Fee Currency': 'ETH', 'TxHash': '0x4'},
        # NFT Transfer - Send
        {'Date': '2024-01-05 12:00:00', 'Sent Amount': '1', 'Sent Currency': 'COOLCAT', 'Received Amount': None, 'Received Currency': None, 'Label': 'nft_transfer', 'Fee Amount': '0.01', 'Fee Currency': 'ETH', 'TxHash': '0x5'},
        # No Label - Crypto to Crypto (Sell)
        {'Date': '2024-01-06 12:00:00', 'Sent Amount': '0.1', 'Sent Currency': 'BTC', 'Received Amount': '1.5', 'Received Currency': 'ETH', 'Label': None, 'Fee Amount': '0.0001', 'Fee Currency': 'BTC', 'TxHash': '0x6'},
    ]

    output_file = "test.csv"

    expected_header = ['Timestamp (UTC)', 'Type', 'Base Currency', 'Base Amount', 'Quote Currency', 'Quote Amount', 'Fee Currency', 'Fee Amount', 'ID']
    expected_rows = [
        expected_header,
        ['2024-01-01 12:00:00', 'buy', 'ETH', '0.5', 'USD', '1000', 'USD', '10', '0x1'],
        ['2024-01-02 12:00:00', 'sell', 'ETH', '0.5', 'USD', '1000', 'ETH', '0.001', '0x2'],
        ['2024-01-03 12:00:00', 'send', 'USDC', '100', '', '', 'ETH', '5', '0x3'],
        ['2024-01-04 12:00:00', 'receive', 'USDC', '100', '', '', 'ETH', '0', '0x4'],
        ['2024-01-05 12:00:00', 'send', 'COOLCAT', '1', '', '', 'ETH', '0.01', '0x5'],
        ['2024-01-06 12:00:00', 'sell', 'BTC', '0.1', 'ETH', '1.5', 'BTC', '0.0001', '0x6'],
    ]

    with patch('builtins.open', mock_open()) as mock_file, \
         patch('os.makedirs') as mock_makedirs:
        write_transaction_data_to_cryptotaxcalculator_csv(output_file, mock_data)

        # Verify that os.makedirs was called correctly
        mock_makedirs.assert_called_once_with(os.path.dirname(output_file), exist_ok=True)

        # Get all the calls to mock_file().write()
        write_calls = mock_file().write.call_args_list

        # Flatten the list of lists of calls into a single list of strings
        written_content = "".join(call.args[0] for call in write_calls)

        # Use csv.reader to parse the written content
        reader = csv.reader(written_content.strip().splitlines())

        # Get the actual rows from the reader
        actual_rows = list(reader)

        # Assert that the actual rows match the expected rows
        assert actual_rows == expected_rows
