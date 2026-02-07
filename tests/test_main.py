from unittest.mock import MagicMock, mock_open, patch

import pytest
from pydantic import ValidationError

from main import (
    Args,
    combine_and_sort_transactions,
    main,
    process_transactions,
)
from models import RawTokenTransfer, RawTransaction, Transaction

CHAIN = "mintchain"
WALLET_ADDRESS = "0x1234567890123456789012345678901234567890"


@pytest.fixture
def mock_adapter():
    with patch("main.ADAPTERS", new_callable=dict) as mock_adapters:
        mock_adapter_instance = MagicMock()
        mock_adapter_class = MagicMock(return_value=mock_adapter_instance)
        mock_adapters[CHAIN] = mock_adapter_class

        mock_adapter_instance.get_transactions.return_value = [
            RawTransaction.model_validate(
                {
                    "timeStamp": "1673784000",
                    "value": "1",
                    "from": {"hash": "test_wallet"},
                    "to": {"hash": "recipient"},
                    "gasUsed": "21000",
                    "gasPrice": "1000000000",
                    "hash": "0x1",
                }
            )
        ]
        mock_adapter_instance.get_token_transfers.return_value = [
            RawTokenTransfer.model_validate(
                {
                    "timeStamp": "1676894400",
                    "total": {"value": "10"},
                    "token": {"symbol": "TOK"},
                    "from": {"hash": "sender"},
                    "to": {"hash": "test_wallet"},
                    "hash": "0x2",
                    "tokenDecimal": "18",
                }
            )
        ]
        mock_adapter_instance.get_internal_transactions.return_value = [
            RawTransaction.model_validate(
                {
                    "timeStamp": "1679745600",
                    "value": "2",
                    "from": {"hash": "test_wallet"},
                    "to": {"hash": "recipient"},
                    "gasUsed": "21000",
                    "gasPrice": "1000000000",
                    "hash": "0x3",
                }
            )
        ]
        yield mock_adapter_instance


def test_date_range_filtering(mock_adapter):
    # Test with no date range
    transactions = process_transactions("test_wallet", CHAIN)
    assert len(transactions) == 3

    # Test with a start date
    transactions = process_transactions("test_wallet", CHAIN, start_date_str="2023-02-01")
    assert len(transactions) == 2
    assert transactions[0].date == "1676894400"

    # Test with an end date
    transactions = process_transactions("test_wallet", CHAIN, end_date_str="2023-02-28")
    assert len(transactions) == 2
    assert transactions[1].date == "1676894400"

    # Test with both a start and end date
    transactions = process_transactions(
        "test_wallet", CHAIN, start_date_str="2023-01-01", end_date_str="2023-01-31"
    )
    assert len(transactions) == 1
    assert transactions[0].date == "1673784000"


def test_combine_and_sort_transactions():
    transactions = [
        Transaction.model_validate({"Date": "1679745600", "Description": "tx3", "TxHash": "0x3"}),
        Transaction.model_validate({"Date": "1673784000", "Description": "tx1", "TxHash": "0x1"}),
    ]
    token_transfers = [
        Transaction.model_validate({"Date": "1676894400", "Description": "tx2", "TxHash": "0x2"})
    ]
    internal_transactions = []

    sorted_transactions = combine_and_sort_transactions(
        transactions, token_transfers, internal_transactions
    )

    assert len(sorted_transactions) == 3
    assert sorted_transactions[0].description == "tx1"
    assert sorted_transactions[1].description == "tx2"
    assert sorted_transactions[2].description == "tx3"


def test_process_transactions_no_data(mock_adapter):
    mock_adapter.get_transactions.return_value = []
    mock_adapter.get_token_transfers.return_value = []
    mock_adapter.get_internal_transactions.return_value = []

    transactions = process_transactions("test_wallet", CHAIN)
    assert len(transactions) == 0


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_csv")
@patch("main.os.getenv")
def test_main_csv_output_with_wallet_arg(
    mock_getenv, mock_write_csv, mock_process, mock_argparse
):
    mock_args = MagicMock()
    addr = "0x" + "a" * 40
    mock_args.wallet = addr
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "csv"
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [
        Transaction.model_validate({"Date": "1", "Description": "test", "TxHash": "0x1"})
    ]

    main()

    mock_process.assert_called_with(addr, CHAIN, None, None)
    mock_write_csv.assert_called_with(
        f"output/{addr}_transactions.csv",
        [
            {
                "Date": "1",
                "Sent Amount": None,
                "Sent Currency": None,
                "Received Amount": None,
                "Received Currency": None,
                "Fee Amount": None,
                "Fee Currency": None,
                "Net Worth Amount": None,
                "Net Worth Currency": None,
                "Label": None,
                "Description": "test",
                "TxHash": "0x1",
            }
        ],
    )
    mock_getenv.assert_not_called()


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_json")
def test_main_json_output(mock_write_json, mock_process, mock_argparse):
    mock_args = MagicMock()
    addr = "0x" + "b" * 40
    mock_args.wallet = addr
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "json"
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [
        Transaction.model_validate({"Date": "1", "Description": "test", "TxHash": "0x1"})
    ]

    main()

    mock_process.assert_called_with(addr, CHAIN, None, None)
    mock_write_json.assert_called_with(
        f"output/{addr}_transactions.json",
        [
            {
                "Date": "1",
                "Sent Amount": None,
                "Sent Currency": None,
                "Received Amount": None,
                "Received Currency": None,
                "Fee Amount": None,
                "Fee Currency": None,
                "Net Worth Amount": None,
                "Net Worth Currency": None,
                "Label": None,
                "Description": "test",
                "TxHash": "0x1",
            }
        ],
    )


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_csv")
def test_main_csv_output(mock_write_csv, mock_process, mock_argparse):
    mock_args = MagicMock()
    addr = "0x" + "c" * 40
    mock_args.wallet = addr
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "csv"
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [
        Transaction.model_validate({"Date": "1", "Description": "test", "TxHash": "0x1"})
    ]

    main()

    mock_process.assert_called_with(addr, CHAIN, None, None)
    mock_write_csv.assert_called_with(
        f"output/{addr}_transactions.csv",
        [
            {
                "Date": "1",
                "Sent Amount": None,
                "Sent Currency": None,
                "Received Amount": None,
                "Received Currency": None,
                "Fee Amount": None,
                "Fee Currency": None,
                "Net Worth Amount": None,
                "Net Worth Currency": None,
                "Label": None,
                "Description": "test",
                "TxHash": "0x1",
            }
        ],
    )
