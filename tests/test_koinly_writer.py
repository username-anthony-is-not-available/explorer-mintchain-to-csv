import csv
import os
from unittest.mock import MagicMock, patch
from koinly_writer import write_transaction_data_to_koinly_csv

@patch('os.makedirs')
def test_write_transaction_data_to_koinly_csv(mock_makedirs: MagicMock) -> None:
    output_file = 'output/koinly_transactions.csv'
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
            'Label': 'cost',
            'Description': 'transaction',
            'TxHash': '0x1234567890abcdef'
        }
    ]

    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        write_transaction_data_to_koinly_csv(output_file, transaction_data)

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
        writer.writerows(transaction_data)
