from unittest.mock import mock_open, patch, call
from cointracker_writer import write_transaction_data_to_cointracker_csv
import os

def test_write_transaction_data_to_cointracker_csv():
    mock_data = [
        {
            "Date": "2023-01-01 00:00:00",
            "Received Amount": "1",
            "Received Currency": "ETH",
            "Sent Amount": "3000",
            "Sent Currency": "USD",
            "Fee Amount": "10",
            "Fee Currency": "USD",
            "Label": "trade"
        }
    ]
    output_file = "output/cointracker_test.csv"

    m = mock_open()
    with patch("builtins.open", m), \
         patch("os.makedirs") as mock_makedirs:
        write_transaction_data_to_cointracker_csv(output_file, mock_data)

        mock_makedirs.assert_called_once_with(os.path.dirname(output_file), exist_ok=True)
        m.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

        handle = m()

        handle.write.assert_has_calls([
            call('Date,Received Quantity,Received Currency,Sent Quantity,Sent Currency,Fee Amount,Fee Currency,Tag\r\n'),
            call('2023-01-01 00:00:00,1,ETH,3000,USD,10,USD,trade\r\n')
        ])
