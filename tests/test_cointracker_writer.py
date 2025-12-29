from unittest.mock import mock_open, patch, call
import pytest
from cointracker_writer import write_transaction_data_to_cointracker_csv
import os

@pytest.mark.parametrize("transaction_data, expected_row", [
    # Trade
    (
        {
            "Date": "2023-01-01 00:00:00",
            "Received Amount": "1",
            "Received Currency": "ETH",
            "Sent Amount": "3000",
            "Sent Currency": "USD",
            "Fee Amount": "10",
            "Fee Currency": "USD",
            "Label": "trade"
        },
        '2023-01-01 00:00:00,1,ETH,3000,USD,10,USD,trade\r\n'
    ),
    # Buy
    (
        {
            "Date": "2023-09-03 15:45:25",
            "Received Amount": "1",
            "Received Currency": "BTC",
            "Sent Amount": "45000",
            "Sent Currency": "USD",
            "Fee Amount": "0.0004",
            "Fee Currency": "BTC",
            "Label": ""
        },
        '2023-09-03 15:45:25,1,BTC,45000,USD,0.0004,BTC,\r\n'
    ),
    # Staking Reward
    (
        {
            "Date": "2023-09-01 00:00:00",
            "Received Amount": "0.01",
            "Received Currency": "ETH",
            "Sent Amount": None,
            "Sent Currency": None,
            "Fee Amount": None,
            "Fee Currency": None,
            "Label": "staking"
        },
        '2023-09-01 00:00:00,0.01,ETH,,,,,staking\r\n'
    ),
    # Outgoing Transfer
    (
        {
            "Date": "2023-09-02 12:30:00",
            "Received Amount": None,
            "Received Currency": None,
            "Sent Amount": "5",
            "Sent Currency": "BTC",
            "Fee Amount": "0.0001",
            "Fee Currency": "BTC",
            "Label": ""
        },
        '2023-09-02 12:30:00,,,5,BTC,0.0001,BTC,\r\n'
    ),
    # Incoming Transfer
    (
        {
            "Date": "2023-09-02 12:30:00",
            "Received Amount": "5",
            "Received Currency": "BTC",
            "Sent Amount": None,
            "Sent Currency": None,
            "Fee Amount": None,
            "Fee Currency": None,
            "Label": ""
        },
        '2023-09-02 12:30:00,5,BTC,,,,,\r\n'
    ),
])
def test_write_transaction_data_to_cointracker_csv(transaction_data, expected_row):
    output_file = "output/cointracker_test.csv"

    m = mock_open()
    with patch("builtins.open", m), \
         patch("os.makedirs") as mock_makedirs:
        write_transaction_data_to_cointracker_csv(output_file, [transaction_data])

        mock_makedirs.assert_called_once_with(os.path.dirname(output_file), exist_ok=True)
        m.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

        handle = m()

        handle.write.assert_has_calls([
            call('Date,Received Quantity,Received Currency,Sent Quantity,Sent Currency,Fee Amount,Fee Currency,Tag\r\n'),
            call(expected_row)
        ])
