from unittest.mock import patch, MagicMock
from main import process_transactions, main, Args
from models import RawTransaction, RawTokenTransfer, Transaction
import pytest
from pydantic import ValidationError

@pytest.fixture
def mock_fetch_data():
    with patch('main.fetch_transactions') as mock_fetch_regular, \
         patch('main.fetch_token_transfers') as mock_fetch_token, \
         patch('main.fetch_internal_transactions') as mock_fetch_internal:

        mock_fetch_regular.return_value = [
            RawTransaction.model_validate({
                'timeStamp': '1673784000', 'value': '1', 'from': {'hash': 'test_wallet'},
                'to': {'hash': 'recipient'}, 'gasUsed': '21000', 'gasPrice': '1000000000', 'hash': '0x1'
            })
        ]
        mock_fetch_token.return_value = [
            RawTokenTransfer.model_validate({
                'timeStamp': '1676894400', 'total': {'value': '10'}, 'token': {'symbol': 'TOK'},
                'from': {'hash': 'sender'}, 'to': {'hash': 'test_wallet'}, 'hash': '0x2'
            })
        ]
        mock_fetch_internal.return_value = [
            RawTransaction.model_validate({
                'timeStamp': '1679745600', 'value': '2', 'from': {'hash': 'test_wallet'},
                'to': {'hash': 'recipient'}, 'gasUsed': '21000', 'gasPrice': '1000000000', 'hash': '0x3'
            })
        ]
        yield mock_fetch_regular, mock_fetch_token, mock_fetch_internal

def test_date_range_filtering(mock_fetch_data):
    # Test with no date range
    transactions = process_transactions('test_wallet')
    assert len(transactions) == 3

    # Test with a start date
    transactions = process_transactions('test_wallet', start_date_str='2023-02-01')
    assert len(transactions) == 2
    assert transactions[0].date == '1676894400'

    # Test with an end date
    transactions = process_transactions('test_wallet', end_date_str='2023-02-28')
    assert len(transactions) == 2
    assert transactions[1].date == '1676894400'

    # Test with both a start and end date
    transactions = process_transactions('test_wallet', start_date_str='2023-01-01', end_date_str='2023-01-31')
    assert len(transactions) == 1
    assert transactions[0].date == '1673784000'


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
    mock_args = MagicMock()
    mock_args.wallet = '0x123'
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = 'csv'
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [Transaction.model_validate({'Date': '1', 'Description': 'test', 'TxHash': '0x1'})]

    main()

    mock_process.assert_called_with('0x123', None, None)
    mock_write_csv.assert_called_with('output/blockchain_transactions.csv', [{'Date': '1', 'Sent Amount': None, 'Sent Currency': None, 'Received Amount': None, 'Received Currency': None, 'Fee Amount': None, 'Fee Currency': None, 'Net Worth Amount': None, 'Net Worth Currency': None, 'Label': None, 'Description': 'test', 'TxHash': '0x1'}])
    mock_getenv.assert_not_called()

def test_args_validation():
    with pytest.raises(ValidationError):
        Args.model_validate({'start_date': '2023-13-01', 'format':'csv'}) # Invalid date
    with pytest.raises(ValidationError):
        Args.model_validate({'end_date': 'not-a-date', 'format':'csv'})
    args = Args.model_validate({'start_date': '2023-01-01', 'format':'csv'})
    assert args.start_date == '2023-01-01'
