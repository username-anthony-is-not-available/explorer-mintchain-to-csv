import csv
import os
from unittest.mock import MagicMock, patch
from koinly_writer import write_transaction_data_to_koinly_csv

@patch('os.makedirs')
def test_write_transaction_data_to_koinly_csv_mintchain(mock_makedirs: MagicMock) -> None:
    output_file = 'output/koinly_transactions_mintchain.csv'
    transaction_data = [
        {
            'Date': '1672531200',
            'Sent Amount': '1',
            'Sent Currency': 'ETH',
            'Received Amount': '',
            'Received Currency': '',
            'Fee Amount': '0.001',
            'Fee Currency': 'ETH',
            'Net Worth Amount': '',
            'Net Worth Currency': '',
            'Label': 'transfer',
            'Description': 'transaction',
            'TxHash': '0x123'
        },
        {
            'Date': '1672531201',
            'Sent Amount': '100',
            'Sent Currency': 'TKN',
            'Received Amount': '',
            'Received Currency': '',
            'Fee Amount': '0.001',
            'Fee Currency': 'ETH',
            'Net Worth Amount': '',
            'Net Worth Currency': '',
            'Label': 'token_transfer',
            'Description': 'token_transfer',
            'TxHash': '0x456'
        },
        {
            'Date': '1672531202',
            'Sent Amount': '',
            'Sent Currency': '',
            'Received Amount': '1',
            'Received Currency': 'ETH',
            'Fee Amount': '0',
            'Fee Currency': 'ETH',
            'Net Worth Amount': '',
            'Net Worth Currency': '',
            'Label': 'staking',
            'Description': 'transaction',
            'TxHash': '0x789'
        }
    ]

    expected_processed_data = [
        {**transaction_data[0], 'Label': ''},
        {**transaction_data[1], 'Label': ''},
        {**transaction_data[2], 'Label': 'staking'},
    ]

    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        write_transaction_data_to_koinly_csv(output_file, transaction_data, chain='mintchain')

        mock_makedirs.assert_called_once_with(os.path.dirname(output_file), exist_ok=True)
        mock_open.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

        mock_file = mock_open.return_value.__enter__.return_value
        writer = csv.DictWriter(
            mock_file,
            fieldnames=[
                'Date', 'Sent Amount', 'Sent Currency', 'Received Amount',
                'Received Currency', 'Fee Amount', 'Fee Currency',
                'Net Worth Amount', 'Net Worth Currency', 'Label',
                'Description', 'TxHash'
            ]
        )
        writer.writeheader()
        writer.writerows(expected_processed_data)


@patch('os.makedirs')
def test_write_transaction_data_to_koinly_csv_etherscan(mock_makedirs: MagicMock) -> None:
    output_file = 'output/koinly_transactions_etherscan.csv'
    transaction_data = [
        {
            'Date': '1672531200',
            'Sent Amount': '1',
            'Sent Currency': 'ETH',
            'Received Amount': '',
            'Received Currency': '',
            'Fee Amount': '0.001',
            'Fee Currency': 'ETH',
            'Net Worth Amount': '',
            'Net Worth Currency': '',
            'Label': 'transfer',
            'Description': 'transaction',
            'TxHash': '0x123'
        }
    ]

    # For etherscan, 'transfer' should remain 'transfer' as it's not in KOINLY_LABEL_MAP
    expected_processed_data = [
        {**transaction_data[0], 'Label': 'transfer'},
    ]

    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        write_transaction_data_to_koinly_csv(output_file, transaction_data, chain='etherscan')

        mock_open.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

        mock_file = mock_open.return_value.__enter__.return_value
        writer = csv.DictWriter(
            mock_file,
            fieldnames=[
                'Date', 'Sent Amount', 'Sent Currency', 'Received Amount',
                'Received Currency', 'Fee Amount', 'Fee Currency',
                'Net Worth Amount', 'Net Worth Currency', 'Label',
                'Description', 'TxHash'
            ]
        )
        writer.writeheader()
        writer.writerows(expected_processed_data)
