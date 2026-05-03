import os
import csv
from zenledger_writer import write_transaction_data_to_zenledger_csv, map_transaction_type

def test_map_transaction_type():
    # Trade
    assert map_transaction_type({"Sent Amount": "1", "Received Amount": "100"}) == "trade"
    assert map_transaction_type({"Label": "swap"}) == "trade"
    
    # Send
    assert map_transaction_type({"Sent Amount": "1", "Received Amount": None}) == "send"
    
    # Receive
    assert map_transaction_type({"Sent Amount": None, "Received Amount": "100"}) == "receive"
    
    # Default (Fee only or similar)
    assert map_transaction_type({"Sent Amount": None, "Received Amount": None, "Fee Amount": "0.1"}) == "send"

def test_write_transaction_data_to_zenledger_csv(tmp_path):
    output_file = os.path.join(tmp_path, "zenledger_test.csv")
    transaction_data = [
        {
            "Date": "2024-01-01 00:00:00 UTC",
            "Sent Amount": "1.0",
            "Sent Currency": "ETH",
            "Received Amount": None,
            "Received Currency": None,
            "Fee Amount": "0.01",
            "Fee Currency": "ETH",
            "TxHash": "0x1"
        },
        {
            "Date": "2024-01-01 01:00:00 UTC",
            "Sent Amount": None,
            "Sent Currency": None,
            "Received Amount": "100.0",
            "Received Currency": "USDC",
            "Fee Amount": None,
            "Fee Currency": None,
            "TxHash": "0x2"
        }
    ]
    
    write_transaction_data_to_zenledger_csv(output_file, transaction_data)
    
    assert os.path.exists(output_file)
    with open(output_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["Type"] == "send"
        assert rows[0]["OUT Amount"] == "1.0"
        assert rows[1]["Type"] == "receive"
        assert rows[1]["IN Amount"] == "100.0"
