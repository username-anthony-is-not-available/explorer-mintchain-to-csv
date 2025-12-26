from unittest.mock import mock_open, patch, call
import pytest
from cryptotaxcalculator_writer import write_transaction_data_to_cryptotaxcalculator_csv
import os

@pytest.mark.parametrize("transaction_data, expected_row", [
    (
        {
            "Date": "2023-01-01 00:00:00",
            "Sent Amount": "3000",
            "Sent Currency": "USD",
            "Received Amount": "1",
            "Received Currency": "ETH",
            "Fee Amount": "10",
            "Fee Currency": "USD"
        },
        '2023-01-01 00:00:00,buy,ETH,USD,1,,,10,,,\r\n'
    ),
    (
        {
            "Date": "2023-01-01 00:00:00",
            "Sent Amount": "1",
            "Sent Currency": "BTC",
            "Received Amount": "30000",
            "Received Currency": "USD",
            "Fee Amount": "10",
            "Fee Currency": "USD"
        },
        '2023-01-01 00:00:00,sell,BTC,USD,1,,,10,,,\r\n'
    ),
    (
        {
            "Date": "2023-01-01 00:00:00",
            "Received Amount": "0.5",
            "Received Currency": "ETH",
        },
        '2023-01-01 00:00:00,deposit,ETH,,0.5,,,,,,\r\n'
    ),
    (
        {
            "Date": "2023-01-01 00:00:00",
            "Sent Amount": "0.5",
            "Sent Currency": "ETH",
        },
        '2023-01-01 00:00:00,withdrawal,ETH,,0.5,,,,,,\r\n'
    )
])
def test_write_transaction_data_to_cryptotaxcalculator_csv(transaction_data, expected_row):
    output_file = "output/cryptotaxcalculator_test.csv"

    m = mock_open()
    with patch("builtins.open", m), \
         patch("os.makedirs") as mock_makedirs:
        write_transaction_data_to_cryptotaxcalculator_csv(output_file, [transaction_data])

        mock_makedirs.assert_called_once_with(os.path.dirname(output_file), exist_ok=True)
        m.assert_called_once_with(output_file, 'w', newline='', encoding='utf-8')

        handle = m()

        handle.write.assert_has_calls([
            call('Date,Type,Symbol,Currency,Volume,Price,PriceAUD,Fee,FeeAUD,Total,TotalAUD\r\n'),
            call(expected_row)
        ])
