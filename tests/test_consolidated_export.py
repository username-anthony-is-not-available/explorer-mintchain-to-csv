import os
import csv
from unittest.mock import MagicMock, patch
from main import main

@patch("main.argparse.ArgumentParser")
@patch("main.process_transactions")
@patch("main.write_transaction_data_to_csv")
def test_main_consolidated_export(mock_write_csv, mock_process, mock_argparse):
    # Setup mock arguments
    addr1 = "0x" + "1" * 40
    addr2 = "0x" + "2" * 40
    mock_args = MagicMock()
    mock_args.wallet = f"{addr1},{addr2}"
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = "csv"
    mock_args.chain = "mintchain"
    mock_args.address_file = None
    mock_args.fees_only = False
    mock_args.consolidated = True
    mock_args.password = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    # Mock return transactions for each wallet
    from models import Transaction
    tx1 = Transaction.model_validate({"Date": "2023-01-01 00:00:01 UTC", "timestamp": 1, "Description": "tx1", "TxHash": "0x1"})
    tx2 = Transaction.model_validate({"Date": "2023-01-01 00:00:02 UTC", "timestamp": 2, "Description": "tx2", "TxHash": "0x2"})
    
    mock_process.side_effect = [[tx1], [tx2]]

    main()

    # Verify that write_transaction_data_to_csv was called ONCE for consolidated
    # and not twice (since consolidated=True)
    # Wait, in the current implementation, process_batch_transactions handles consolidated.
    # It still calls process_transactions for each wallet.
    assert mock_write_csv.call_count == 1
    
    # Check the call arguments
    args, kwargs = mock_write_csv.call_args
    output_file = args[0]
    output_data = args[1]
    
    assert output_file == "output/consolidated_transactions.csv"
    assert len(output_data) == 2
    assert output_data[0]["Wallet"] == addr1
    assert output_data[1]["Wallet"] == addr2
