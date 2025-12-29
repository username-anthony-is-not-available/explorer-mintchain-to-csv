from unittest.mock import patch, MagicMock, mock_open
from main import process_transactions, main, Args, process_batch_transactions
from models import RawTransaction, RawTokenTransfer, Transaction
import pytest
from pydantic import ValidationError
import responses
from config import EXPLORER_URLS

CHAIN = "mintchain"
WALLET_ADDRESS = "0x1234567890123456789012345678901234567890"

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
                'from': {'hash': 'sender'}, 'to': {'hash': 'test_wallet'}, 'hash': '0x2', 'tokenDecimal': '18'
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
    transactions = process_transactions('test_wallet', CHAIN)
    assert len(transactions) == 3

    # Test with a start date
    transactions = process_transactions('test_wallet', CHAIN, start_date_str='2023-02-01')
    assert len(transactions) == 2
    assert transactions[0].date == '1676894400'

    # Test with an end date
    transactions = process_transactions('test_wallet', CHAIN, end_date_str='2023-02-28')
    assert len(transactions) == 2
    assert transactions[1].date == '1676894400'

    # Test with both a start and end date
    transactions = process_transactions('test_wallet', CHAIN, start_date_str='2023-01-01', end_date_str='2023-01-31')
    assert len(transactions) == 1
    assert transactions[0].date == '1673784000'


@patch('main.fetch_transactions', return_value=[])
@patch('main.fetch_token_transfers', return_value=[])
@patch('main.fetch_internal_transactions', return_value=[])
def test_process_transactions_no_data(mock_fetch_internal, mock_fetch_token, mock_fetch_regular):
    transactions = process_transactions('test_wallet', CHAIN)
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
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [Transaction.model_validate({'Date': '1', 'Description': 'test', 'TxHash': '0x1'})]

    main()

    mock_process.assert_called_with('0x123', CHAIN, None, None)
    mock_write_csv.assert_called_with('output/blockchain_transactions.csv', [{'Date': '1', 'Sent Amount': None, 'Sent Currency': None, 'Received Amount': None, 'Received Currency': None, 'Fee Amount': None, 'Fee Currency': None, 'Net Worth Amount': None, 'Net Worth Currency': None, 'Label': None, 'Description': 'test', 'TxHash': '0x1'}])
    mock_getenv.assert_not_called()

def test_args_validation():
    # Test for invalid date format
    with pytest.raises(ValidationError):
        Args.model_validate({'wallet': '0x123', 'start_date': '2023-13-01', 'format': 'csv'})

    # Test for missing wallet and address_file
    with pytest.raises(ValidationError):
        Args.model_validate({'format': 'csv'})

    # Test for providing both wallet and address_file
    with pytest.raises(ValidationError):
        Args.model_validate({'wallet': '0x123', 'address_file': 'addresses.txt', 'format': 'csv'})

    # Test for valid arguments
    args = Args.model_validate({'wallet': '0x123', 'start_date': '2023-01-01', 'format': 'csv', 'chain': 'etherscan'})
    assert args.wallet == '0x123'
    assert args.start_date == '2023-01-01'
    assert args.chain == 'etherscan'

    # Test with address_file
    args = Args.model_validate({'address_file': 'addresses.txt', 'format': 'csv'})
    assert args.address_file == 'addresses.txt'


@patch('main.process_transactions')
def test_process_batch_transactions(mock_process_transactions):
    # Mock the file content
    mock_file_content = "0xaddress1\n0xaddress2\n"
    mock_open_context = mock_open(read_data=mock_file_content)

    # Mock the return value of process_transactions for each address
    mock_process_transactions.side_effect = [
        [Transaction.model_validate({'Date': '1673784000', 'Description': 'tx1', 'TxHash': '0x1'})],
        [Transaction.model_validate({'Date': '1676894400', 'Description': 'tx2', 'TxHash': '0x2'})],
    ]

    with patch('builtins.open', mock_open_context):
        result = process_batch_transactions('dummy_path.txt', CHAIN)

    # Verify the results
    assert len(result) == 2
    assert result[0].description == 'tx1'
    assert result[1].description == 'tx2'

    # Verify that process_transactions was called for each address
    assert mock_process_transactions.call_count == 2
    mock_process_transactions.assert_any_call('0xaddress1', CHAIN, None, None)
    mock_process_transactions.assert_any_call('0xaddress2', CHAIN, None, None)


@responses.activate
def test_process_transactions_with_mocked_api():
    base_url = EXPLORER_URLS[CHAIN]

    # Mock for fetch_transactions
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc",
        json={"result": [{
            "hash": "0x1", "from": {"hash": WALLET_ADDRESS}, "to": {"hash": "0x456"}, "value": "100",
            "timeStamp": "1673784000", "gasUsed": "21000", "gasPrice": "1000000000"
        }]},
        status=200,
    )

    # Mock for fetch_token_transfers
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=tokentx&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc",
        json={"result": [{
            "hash": "0x2", "from": {"hash": "0x789"}, "to": {"hash": WALLET_ADDRESS}, "timeStamp": "1676894400",
            "total": {"value": "200"}, "token": {"symbol": "TKN"}, "tokenDecimal": "18"
        }]},
        status=200,
    )

    # Mock for fetch_internal_transactions
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=txlistinternal&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc",
        json={"result": [{
            "hash": "0x3", "from": {"hash": WALLET_ADDRESS}, "to": {"hash": "0xabc"}, "value": "300",
            "timeStamp": "1679745600", "gasUsed": "21000", "gasPrice": "1000000000"
        }]},
        status=200,
    )

    # Test with no date range
    transactions = process_transactions(WALLET_ADDRESS, CHAIN)
    assert len(transactions) == 3
    assert transactions[0].tx_hash == '0x1'
    assert transactions[1].tx_hash == '0x2'
    assert transactions[2].tx_hash == '0x3'

    # Test with a start date
    transactions = process_transactions(WALLET_ADDRESS, CHAIN, start_date_str='2023-02-01')
    assert len(transactions) == 2
    assert transactions[0].tx_hash == '0x2'
    assert transactions[1].tx_hash == '0x3'

    # Test with an end date
    transactions = process_transactions(WALLET_ADDRESS, CHAIN, end_date_str='2023-02-28')
    assert len(transactions) == 2
    assert transactions[0].tx_hash == '0x1'
    assert transactions[1].tx_hash == '0x2'


@patch('main.argparse.ArgumentParser')
@patch('main.process_transactions')
@patch('main.write_transaction_data_to_json')
def test_main_json_output(mock_write_json, mock_process, mock_argparse):
    mock_args = MagicMock()
    mock_args.wallet = '0x123'
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = 'json'
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [Transaction.model_validate({'Date': '1', 'Description': 'test', 'TxHash': '0x1'})]

    main()

    mock_process.assert_called_with('0x123', CHAIN, None, None)
    mock_write_json.assert_called_with('output/blockchain_transactions.json', [{'Date': '1', 'Sent Amount': None, 'Sent Currency': None, 'Received Amount': None, 'Received Currency': None, 'Fee Amount': None, 'Fee Currency': None, 'Net Worth Amount': None, 'Net Worth Currency': None, 'Label': None, 'Description': 'test', 'TxHash': '0x1'}])


@patch('main.argparse.ArgumentParser')
@patch('main.process_transactions')
@patch('main.write_transaction_data_to_csv')
def test_main_csv_output(mock_write_csv, mock_process, mock_argparse):
    mock_args = MagicMock()
    mock_args.wallet = '0x123'
    mock_args.start_date = None
    mock_args.end_date = None
    mock_args.format = 'csv'
    mock_args.chain = CHAIN
    mock_args.address_file = None
    mock_argparse.return_value.parse_args.return_value = mock_args

    mock_process.return_value = [Transaction.model_validate({'Date': '1', 'Description': 'test', 'TxHash': '0x1'})]

    main()

    mock_process.assert_called_with('0x123', CHAIN, None, None)
    mock_write_csv.assert_called_with('output/blockchain_transactions.csv', [{'Date': '1', 'Sent Amount': None, 'Sent Currency': None, 'Received Amount': None, 'Received Currency': None, 'Fee Amount': None, 'Fee Currency': None, 'Net Worth Amount': None, 'Net Worth Currency': None, 'Label': None, 'Description': 'test', 'TxHash': '0x1'}])
