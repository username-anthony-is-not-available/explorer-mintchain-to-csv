from concurrent.futures import ThreadPoolExecutor
import threading
from unittest.mock import MagicMock, mock_open, patch

from main import main, process_batch_transactions
from models import Transaction
from writers import WriterFactory

CHAIN = "mintchain"


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.WriterFactory")
def test_main_batch_wallet_arg(mock_factory, mock_process, mock_argparse):
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
    mock_args.fees_only = False
    mock_args.consolidated = False
    mock_args.run_validation = False
    mock_args.password = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    # Mock return values for each wallet processed
    mock_process.side_effect = [
        [Transaction.model_validate({"Date": "2023-01-01 00:00:01 UTC", "timestamp": 1, "Description": "tx1", "TxHash": "0x1"})],
        [Transaction.model_validate({"Date": "2023-01-01 00:00:02 UTC", "timestamp": 2, "Description": "tx2", "TxHash": "0x2"})],
    ]

    main()

    # Verify process_transactions is called for each address
    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None, fees_only=False, rpc_url=None)
    mock_process.assert_any_call(addr2, CHAIN, None, None, fees_only=False, rpc_url=None)

    # Verify separate CSV files are written for each address
    assert mock_factory.get_writer.return_value.write.call_count == 2
    mock_factory.get_writer.return_value.write.assert_any_call(
        f"output/{addr1}_transactions.csv",
        [
            {
                "Date": "2023-01-01 00:00:01 UTC", "Sent Amount": None, "Sent Currency": None,
                "Received Amount": None, "Received Currency": None, "Fee Amount": None,
                "Fee Currency": None, "Net Worth Amount": None, "Net Worth Currency": None,
                "Label": None, "Description": "tx1", "TxHash": "0x1",
            }
        ],
        chain=CHAIN,
        consolidated=False
    )
    mock_factory.get_writer.return_value.write.assert_any_call(
        f"output/{addr2}_transactions.csv",
        [
            {
                "Date": "2023-01-01 00:00:02 UTC", "Sent Amount": None, "Sent Currency": None,
                "Received Amount": None, "Received Currency": None, "Fee Amount": None,
                "Fee Currency": None, "Net Worth Amount": None, "Net Worth Currency": None,
                "Label": None, "Description": "tx2", "TxHash": "0x2",
            }
        ],
        chain=CHAIN,
        consolidated=False
    )


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.WriterFactory")
@patch("builtins.open", new_callable=mock_open)
def test_main_batch_address_file(mock_open_file, mock_factory, mock_process, mock_argparse):
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
    mock_args.fees_only = False
    mock_args.consolidated = False
    mock_args.password = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.side_effect = [
        [Transaction.model_validate({"Date": "2023-01-01 00:00:03 UTC", "timestamp": 3, "Description": "tx3", "TxHash": "0x3", "Sent Amount": "1", "Sent Currency": "ETH"})],
        [Transaction.model_validate({"Date": "2023-01-01 00:00:04 UTC", "timestamp": 4, "Description": "tx4", "TxHash": "0x4", "Sent Amount": "1", "Sent Currency": "ETH"})],
    ]

    main()

    mock_open_file.assert_any_call("addresses.txt", "r", newline='')
    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None, fees_only=False, rpc_url=None)
    mock_process.assert_any_call(addr2, CHAIN, None, None, fees_only=False, rpc_url=None)

    assert mock_factory.get_writer.return_value.write.call_count == 2


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.WriterFactory")
@patch("main.os.getenv")
def test_main_batch_env_var(mock_getenv, mock_factory, mock_process, mock_argparse):
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
    mock_args.fees_only = False
    mock_args.consolidated = False
    mock_args.password = None
    mock_args.rpc_url = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    # Mock environment variables
    def getenv_side_effect(key):
        if key == 'WALLET_ADDRESSES':
            return f"{addr1},{addr2}"
        if key == 'ENV_PASSWORD':
            return None
        return None

    mock_getenv.side_effect = getenv_side_effect

    mock_process.side_effect = [
        [Transaction.model_validate({"Date": "2023-01-01 00:00:05 UTC", "timestamp": 5, "Description": "tx5", "TxHash": "0x5"})],
        [Transaction.model_validate({"Date": "2023-01-01 00:00:06 UTC", "timestamp": 6, "Description": "tx6", "TxHash": "0x6"})],
    ]

    main()

    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None, fees_only=False, rpc_url=None)
    mock_process.assert_any_call(addr2, CHAIN, None, None, fees_only=False, rpc_url=None)

    assert mock_factory.get_writer.return_value.write.call_count == 2


@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.WriterFactory")
@patch("main.csv.reader")
@patch("builtins.open", new_callable=mock_open)
def test_main_batch_address_file_csv(mock_open_file, mock_csv_reader, mock_factory, mock_process, mock_argparse):
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
    mock_args.fees_only = False
    mock_args.consolidated = False
    mock_args.password = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.side_effect = [[], []]

    main()

    mock_open_file.assert_any_call("addresses.csv", "r", newline='')
    assert mock_process.call_count == 2
    mock_process.assert_any_call(addr1, CHAIN, None, None, fees_only=False, rpc_url=None)
    mock_process.assert_any_call(addr2, CHAIN, None, None, fees_only=False, rpc_url=None)


def test_batch_processing_no_deadlock_with_many_wallets(tmp_path, monkeypatch):
    """
    Verifies batch processing >= 10 wallets (exceeding GLOBAL_EXECUTOR max_workers)
    completes concurrently without nested ThreadPoolExecutor deadlock.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "output").mkdir()
    addresses = [f"0x{i:040x}" for i in range(1, 16)]

    mock_adapter_instance = MagicMock()
    mock_adapter_instance.get_transactions.return_value = []
    mock_adapter_instance.get_token_transfers.return_value = []
    mock_adapter_instance.get_internal_transactions.return_value = []
    mock_adapter_instance.get_nft_transfers.return_value = []
    mock_adapter_instance.get_1155_transfers.return_value = []
    mock_adapter_class = MagicMock(return_value=mock_adapter_instance)

    # Run inside a timeout guard so a deadlock fails fast instead of hanging the test suite.
    with patch.dict("main.ADAPTERS", {CHAIN: mock_adapter_class}):
        with ThreadPoolExecutor(max_workers=1) as guard:
            future = guard.submit(
                process_batch_transactions,
                addresses,
                CHAIN,
                "csv",
            )
            future.result(timeout=5.0)

    assert mock_adapter_instance.get_transactions.call_count == 15
    for addr in addresses:
        assert (tmp_path / "output" / f"{addr}_transactions.csv").exists()


def test_batch_processing_runs_wallets_concurrently():
    """
    Verifies process_batch_transactions executes wallet tasks concurrently across threads.
    """
    barrier = threading.Barrier(2, timeout=2.0)
    seen_threads = set()
    lock = threading.Lock()

    def concurrent_process(*args, **kwargs):
        with lock:
            seen_threads.add(threading.get_ident())
        barrier.wait()
        return []

    addresses = ["0x" + "1" * 40, "0x" + "2" * 40]
    with patch("main.process_transactions", side_effect=concurrent_process):
        with patch("main.WriterFactory"):
            process_batch_transactions(addresses, CHAIN, "csv", max_workers=2)

    assert len(seen_threads) == 2


def test_batch_processing_handles_partial_wallet_failures(tmp_path, monkeypatch):
    """
    Verifies an error in one wallet does not abort processing for the remaining wallets.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "output").mkdir()
    addr_ok = "0x" + "a" * 40
    addr_fail = "0x" + "b" * 40

    def selective_process(wallet_address, *args, **kwargs):
        if wallet_address == addr_fail:
            raise RuntimeError("transient explorer failure")
        return [
            Transaction.model_validate(
                {
                    "Date": "2023-01-01 00:00:01 UTC",
                    "timestamp": 1,
                    "Description": "ok",
                    "TxHash": "0x1",
                }
            )
        ]

    with patch("main.process_transactions", side_effect=selective_process):
        process_batch_transactions([addr_ok, addr_fail], CHAIN, "json")

    assert (tmp_path / "output" / f"{addr_ok}_transactions.json").exists()
    assert not (tmp_path / "output" / f"{addr_fail}_transactions.json").exists()


def test_batch_processing_empty_addresses():
    """
    Verifies empty address lists exit cleanly without invoking ThreadPoolExecutor(max_workers=0).
    """
    with patch("main.process_single_wallet") as mock_single:
        process_batch_transactions([], CHAIN, "csv")
    mock_single.assert_not_called()
