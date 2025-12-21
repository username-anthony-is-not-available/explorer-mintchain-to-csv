import os
import csv
import json
import shutil
import pytest
from csv_writer import write_transaction_data_to_csv
from json_writer import write_transaction_data_to_json

MOCK_DATA = [
    {
        "Date": "2023-01-15T12:00:00.000Z",
        "Sent Amount": "1",
        "Sent Currency": "ETH",
        "Received Amount": "",
        "Received Currency": "",
        "Fee Amount": "0.01",
        "Fee Currency": "ETH",
        "Net Worth Amount": "",
        "Net Worth Currency": "",
        "Label": "",
        "Description": "transaction",
        "TxHash": "0x123"
    }
]

TEST_OUTPUT_DIR = "test_output"

@pytest.fixture(autouse=True)
def setup_and_cleanup_files():
    """Fixture to set up and clean up the test output directory."""
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    yield
    shutil.rmtree(TEST_OUTPUT_DIR)

def test_write_to_csv_creates_file():
    """Tests that write_transaction_data_to_csv creates a file."""
    output_file = os.path.join(TEST_OUTPUT_DIR, "test.csv")
    write_transaction_data_to_csv(output_file, MOCK_DATA)
    assert os.path.exists(output_file)

def test_write_to_csv_writes_correct_data():
    """Tests that write_transaction_data_to_csv writes the correct data."""
    output_file = os.path.join(TEST_OUTPUT_DIR, "test.csv")
    write_transaction_data_to_csv(output_file, MOCK_DATA)
    with open(output_file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == list(MOCK_DATA[0].keys())
        row = next(reader)
        assert row == list(MOCK_DATA[0].values())

def test_write_to_json_creates_file():
    """Tests that write_transaction_data_to_json creates a file."""
    output_file = os.path.join(TEST_OUTPUT_DIR, "test.json")
    write_transaction_data_to_json(output_file, MOCK_DATA)
    assert os.path.exists(output_file)

def test_write_to_json_writes_correct_data():
    """Tests that write_transaction_data_to_json writes the correct data."""
    output_file = os.path.join(TEST_OUTPUT_DIR, "test.json")
    write_transaction_data_to_json(output_file, MOCK_DATA)
    with open(output_file, "r") as f:
        data = json.load(f)
        assert data == MOCK_DATA
