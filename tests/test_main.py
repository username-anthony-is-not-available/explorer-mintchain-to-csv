from unittest.mock import patch, MagicMock
from main import process_transactions, main


@patch('main.fetch_transactions')
@patch('main.fetch_token_transfers')
@patch('main.fetch_internal_transactions')
def test_date_range_filtering(mock_fetch_internal, mock_fetch_token, mock_fetch_regular):
    # Corrected mock data to match expected nested structure for 'from' and 'to'
    mock_fetch_regular.return_value = [{'timeStamp': '1673784000', 'value': '1', 'from': {'hash': 'test_wallet'}, 'to': {'hash': 'recipient'}, 'gasUsed': '21000', 'gasPrice': '1000000000'}]
    mock_fetch_token.return_value = [{'timeStamp': '1676894400', 'value': '10', 'tokenSymbol': 'TOK', 'from': {'hash': 'test_wallet'}, 'to': {'hash': 'recipient'}, 'gasUsed': '21000', 'gasPrice': '1000000000'}]
    mock_fetch_internal.return_value = [{'timeStamp': '1679745600', 'value': '2', 'from': {'hash': 'test_wallet'}, 'to': {'hash': 'recipient'}, 'gasUsed': '21000', 'gasPrice': '1000000000'}]

    # Test with no date range
    transactions = process_transactions('test_wallet')
    assert len(transactions) == 3

    # Test with a start date
    transactions = process_transactions('test_wallet', start_date_str='2023-02-01')
    assert len(transactions) == 2
    # The 'Date' field is a string, so we assert for a string
    assert transactions[0]['Date'] == '1676894400'

    # Test with an end date
    transactions = process_transactions('test_wallet', end_date_str='2023-02-28')
    assert len(transactions) == 2
    assert transactions[1]['Date'] == '1676894400'

    # Test with both a start and end date
    transactions = process_transactions('test_wallet', start_date_str='2023-01-01', end_date_str='2023-01-31')
    assert len(transactions) == 1
    assert transactions[0]['Date'] == '1673784000'


@patch('main.fetch_transactions', return_value=[])
@patch('main.fetch_token_transfers', return_value=[])
@patch('main.fetch_internal_transactions', return_value=[])
def test_process_transactions_no_data(mock_fetch_internal, mock_fetch_token, mock_fetch_regular):
    transactions = process_transactions('test_wallet')
    assert len(transactions) == 0


@patch('main.argparse.ArgumentParser')
@patch('main.process_transactions')
@patch('main.write_transaction_data_to_csv')
@patch('main.os.getenv')
def test_main_csv_output_with_wallet_arg(mock_getenv, mock_write_csv, mock_process, mock_argparse):
    # Setup mock for argparse
    mock_args = MagicMock()
    mock_args.wallet = '0x123'
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = 'csv'
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [{'test': 'data'}]

    main()

    mock_process.assert_called_with('0x123', None, None)
    mock_write_csv.assert_called_with('output/blockchain_transactions.csv', [{'test': 'data'}])
    mock_getenv.assert_not_called()


@patch('main.argparse.ArgumentParser')
@patch('main.process_transactions')
@patch('main.write_transaction_data_to_json')
@patch('main.os.getenv', return_value=None)
def test_main_json_output_with_wallet_arg(mock_getenv, mock_write_json, mock_process, mock_argparse):
    # Setup mock for argparse
    mock_args = MagicMock()
    mock_args.wallet = '0x456'
    mock_args.start_date = '2023-01-01'
    mock_args.end_date = '2023-12-31'
    mock_args.format = 'json'
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [{'json': 'data'}]

    main()

    mock_process.assert_called_with('0x456', '2023-01-01', '2023-12-31')
    mock_write_json.assert_called_with('output/blockchain_transactions.json', [{'json': 'data'}])


@patch('main.argparse.ArgumentParser')
@patch('main.process_transactions')
@patch('main.write_transaction_data_to_csv')
@patch('main.os.getenv', return_value='0x789')
def test_main_with_wallet_from_env(mock_getenv, mock_write_csv, mock_process, mock_argparse):
    # Setup mock for argparse
    mock_args = MagicMock()
    mock_args.wallet = None  # No wallet arg provided
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = 'csv'
    mock_argparse.return_value.parse_args.return_value = mock_args

    main()

    mock_getenv.assert_called_with('WALLET_ADDRESS')
    mock_process.assert_called_with('0x789', None, None)
    mock_write_csv.assert_called_once()


@patch('main.argparse.ArgumentParser')
@patch('main.logging.error')
@patch('main.os.getenv', return_value=None)
def test_main_no_wallet_address(mock_getenv, mock_log_error, mock_argparse):
    # Setup mock for argparse
    mock_args = MagicMock()
    mock_args.wallet = None
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = 'csv'
    mock_argparse.return_value.parse_args.return_value = mock_args

    main()

    mock_log_error.assert_called_with("No wallet address provided. Set it in the .env file or use the --wallet argument.")
