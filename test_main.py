import unittest
from unittest.mock import patch, MagicMock
from main import process_transactions, main

class TestTransactionProcessing(unittest.TestCase):
    @patch('main.fetch_transactions')
    @patch('main.fetch_token_transfers')
    @patch('main.fetch_internal_transactions')
    def test_date_range_filtering(self, mock_fetch_internal, mock_fetch_token, mock_fetch_regular):
        # Mock the return values of the fetch functions
        mock_fetch_regular.return_value = [
            {
                "timeStamp": "1673784000",
                "value": "1",
                "gasUsed": "21000",
                "gasPrice": "1000000000",
                "hash": "0x123",
                "from": "test_wallet",
                "to": "recipient",
            }
        ]
        mock_fetch_token.return_value = [
            {
                "timeStamp": "1676894400",
                "value": "10",
                "tokenSymbol": "TOK",
                "hash": "0x456",
                "from": "test_wallet",
                "to": "recipient",
            }
        ]
        mock_fetch_internal.return_value = [
            {
                "timeStamp": "1679745600",
                "value": "2",
                "gasUsed": "21000",
                "gasPrice": "1000000000",
                "hash": "0x789",
                "from": "test_wallet",
                "to": "recipient",
            }
        ]

        # Test with no date range
        transactions = process_transactions('test_wallet')
        self.assertEqual(len(transactions), 3)

        # Test with a start date
        transactions = process_transactions('test_wallet', start_date_str='2023-02-01')
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['Date'], '1676894400')

        # Test with an end date
        transactions = process_transactions('test_wallet', end_date_str='2023-02-28')
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[1]['Date'], '1676894400')

        # Test with both a start and end date
        transactions = process_transactions('test_wallet', start_date_str='2023-01-01', end_date_str='2023-01-31')
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['Date'], '1673784000')

class TestMain(unittest.TestCase):
    @patch('main.argparse.ArgumentParser')
    @patch('main.process_transactions')
    @patch('main.write_transaction_data_to_csv')
    def test_main_csv_output(self, mock_write_csv, mock_process, mock_argparse):
        # Mock command-line arguments
        mock_args = MagicMock()
        mock_args.wallet = 'test_wallet'
        mock_args.start_date = None
        mock_args.end_date = None
        mock_args.format = 'csv'
        mock_argparse.return_value.parse_args.return_value = mock_args

        # Mock process_transactions to return some data
        mock_process.return_value = [{'Date': '1673784000'}]

        main()

        # Check that the CSV writer was called
        mock_write_csv.assert_called_once()

    @patch('main.argparse.ArgumentParser')
    @patch('main.process_transactions')
    @patch('main.write_transaction_data_to_json')
    def test_main_json_output(self, mock_write_json, mock_process, mock_argparse):
        # Mock command-line arguments
        mock_args = MagicMock()
        mock_args.wallet = 'test_wallet'
        mock_args.start_date = None
        mock_args.end_date = None
        mock_args.format = 'json'
        mock_argparse.return_value.parse_args.return_value = mock_args

        # Mock process_transactions to return some data
        mock_process.return_value = [{'Date': '1673784000'}]

        main()

        # Check that the JSON writer was called
        mock_write_json.assert_called_once()

    @patch('main.argparse.ArgumentParser')
    @patch('main.logging.error')
    def test_main_no_wallet(self, mock_log_error, mock_argparse):
        # Mock command-line arguments
        mock_args = MagicMock()
        mock_args.wallet = None
        mock_argparse.return_value.parse_args.return_value = mock_args

        with patch('main.os.getenv', return_value=None):
            main()

        # Check that an error was logged
        mock_log_error.assert_called_once_with("No wallet address provided. Set it in the .env file or use the --wallet argument.")

if __name__ == '__main__':
    unittest.main()
