from unittest.mock import MagicMock, mock_open, patch

from main import main
from models import Transaction

CHAIN = "mintchain"


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_csv")
def test_main_batch_wallet_arg(mock_write_csv, mock_process, mock_argparse):
    """
    Tests processing of multiple wallets provided via the --wallet argument.
    """
    mock_args = MagicMock()
    # Using 42-char addresses
    addr1 = "0x" + "1" * 40
    addr2 = "0x" + "2" * 40
    mock_args.wallet = f"{addr1},{addr2}"
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "csv"
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    # Mock return values for each wallet processed
    mock_process.side_effect = [
        [Transaction.model_validate({"Date": "1", "Description": "tx1", "TxHash": "0x1"})],
        [Transaction.model_validate({"Date": "2", "Description": "tx2", "TxHash": "0x2"})],
    ]

    main()

    # Verify process_transactions is called for each address
    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None)
    mock_process.assert_any_call(addr2, CHAIN, None, None)

    # Verify separate CSV files are written for each address
    assert mock_write_csv.call_count == 2
    mock_write_csv.assert_any_call(
        f"output/{addr1}_transactions.csv",
        [
            {
                "Date": "1", "Sent Amount": None, "Sent Currency": None,
                "Received Amount": None, "Received Currency": None, "Fee Amount": None,
                "Fee Currency": None, "Net Worth Amount": None, "Net Worth Currency": None,
                "Label": None, "Description": "tx1", "TxHash": "0x1",
            }
        ],
    )
    mock_write_csv.assert_any_call(
        f"output/{addr2}_transactions.csv",
        [
            {
                "Date": "2", "Sent Amount": None, "Sent Currency": None,
                "Received Amount": None, "Received Currency": None, "Fee Amount": None,
                "Fee Currency": None, "Net Worth Amount": None, "Net Worth Currency": None,
                "Label": None, "Description": "tx2", "TxHash": "0x2",
            }
        ],
    )


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_json")
@patch("builtins.open", new_callable=mock_open)
def test_main_batch_address_file(mock_open_file, mock_write_json, mock_process, mock_argparse):
    """
    Tests processing of multiple wallets from a file specified by --address-file.
    """
    addr1 = "0x" + "3" * 40
    addr2 = "0x" + "4" * 40
    mock_open_file.return_value.__enter__.return_value = [f"{addr1}\n", f"{addr2}\n"]

    mock_args = MagicMock()
    mock_args.wallet = None
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "json"
    mock_args.chain = CHAIN
    mock_args.address_file = "addresses.txt"
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.side_effect = [
        [Transaction.model_validate({"Date": "3", "Description": "tx3", "TxHash": "0x3", "Sent Amount": "1"})],
        [Transaction.model_validate({"Date": "4", "Description": "tx4", "TxHash": "0x4", "Sent Amount": "1"})],
    ]

    main()

    mock_open_file.assert_called_with("addresses.txt", "r", newline='')
    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None)
    mock_process.assert_any_call(addr2, CHAIN, None, None)

    assert mock_write_json.call_count == 2


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_csv")
@patch("main.os.getenv")
def test_main_batch_env_var(mock_getenv, mock_write_csv, mock_process, mock_argparse):
    """
    Tests processing of multiple wallets from the WALLET_ADDRESSES environment variable.
    """
    addr1 = "0x" + "5" * 40
    addr2 = "0x" + "6" * 40
    mock_args = MagicMock()
    mock_args.wallet = None
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "csv"
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    # Mock environment variables
    def getenv_side_effect(key):
        if key == 'WALLET_ADDRESSES':
            return f"{addr1},{addr2}"
        return None
    mock_getenv.side_effect = getenv_side_effect

    mock_process.side_effect = [
        [Transaction.model_validate({"Date": "5", "Description": "tx5", "TxHash": "0x5"})],
        [Transaction.model_validate({"Date": "6", "Description": "tx6", "TxHash": "0x6"})],
    ]

    main()

    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None)
    mock_process.assert_any_call(addr2, CHAIN, None, None)

    assert mock_write_csv.call_count == 2


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_json")
@patch("main.csv.reader")
@patch("builtins.open", new_callable=mock_open)
def test_main_batch_address_file_csv(mock_open_file, mock_csv_reader, mock_write_json, mock_process, mock_argparse):
    """
    Tests processing of multiple wallets from a CSV file.
    """
    addr1 = "0x" + "7" * 40
    addr2 = "0x" + "8" * 40
    # Mock CSV reader to return rows
    mock_csv_reader.return_value = [
        ["address", "name"],
        [addr1, "Alice"],
        [addr2, "Bob"]
    ]

    mock_args = MagicMock()
    mock_args.wallet = None
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "json"
    mock_args.chain = CHAIN
    mock_args.address_file = "addresses.csv"
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.side_effect = [[], []]

    main()

    mock_open_file.assert_called_with("addresses.csv", "r", newline='')
    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None)
    mock_process.assert_any_call(addr2, CHAIN, None, None)
