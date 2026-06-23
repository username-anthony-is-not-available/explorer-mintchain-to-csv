import csv
import os
from writers import TurboTaxWriter

def test_turbotax_writer_write(tmp_path):
    writer = TurboTaxWriter()
    output_file = str(tmp_path / "test_turbotax.csv")
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
        assert rows[0]["Type"] == "swap"
        assert rows[0]["Sent Asset"] == "ETH"
        assert rows[0]["Sent Amount"] == "1.0"
        assert rows[0]["Received Asset"] == "USDC"
        assert rows[0]["Received Amount"] == "2000.0"
