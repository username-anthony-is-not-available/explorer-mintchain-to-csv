import csv
import os
from writers import AccointingWriter

def test_accointing_writer_write(tmp_path):
    writer = AccointingWriter()
    output_file = str(tmp_path / "test_accointing.csv")
    transaction_data = [
        {
            "Date": "2024-01-01 12:00:00 UTC",
            "Sent Amount": "1.0",
            "Sent Currency": "ETH",
            "Received Amount": "2000.0",
            "Received Currency": "USDC",
            "Fee Amount": "0.01",
            "Fee Currency": "ETH",
            "Label": "swap",
            "Description": "Uniswap Swap",
            "TxHash": "0x123"
        }
    ]

    writer.write(output_file, transaction_data)

    assert os.path.exists(output_file)
    with open(output_file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["transaction_type"] == "order"
        assert rows[0]["in_buy_amount"] == "2000.0"
        assert rows[0]["in_buy_asset"] == "USDC"
        assert rows[0]["out_sell_amount"] == "1.0"
        assert rows[0]["out_sell_asset"] == "ETH"
        assert rows[0]["classification"] == "swap"
