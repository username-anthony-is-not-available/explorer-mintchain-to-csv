import csv
import os
from writers import CoinTrackingWriter

def test_cointracking_writer_write(tmp_path):
    writer = CoinTrackingWriter()
    output_file = str(tmp_path / "test_cointracking.csv")
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

    writer.write(output_file, transaction_data, chain="etherscan")

    assert os.path.exists(output_file)
    with open(output_file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Type"] == "Trade"
        assert rows[0]["Buy Amount"] == "2000.0"
        assert rows[0]["Buy Cur."] == "USDC"
        assert rows[0]["Sell Amount"] == "1.0"
        assert rows[0]["Sell Cur."] == "ETH"
        assert rows[0]["Fee"] == "0.01"
        assert rows[0]["Exchange"] == "etherscan"
