import unittest
from unittest.mock import patch
from main import process_transactions

class TestTransactionProcessing(unittest.TestCase):
    @patch('main.fetch_transactions')
    @patch('main.fetch_token_transfers')
    @patch('main.fetch_internal_transactions')
    def test_date_range_filtering(self, mock_fetch_internal, mock_fetch_token, mock_fetch_regular):
        # Mock the return values of the fetch functions
        mock_fetch_regular.return_value = [{'timestamp': '2023-01-15T12:00:00.000Z', 'value': '1', 'from': {'hash': 'test_wallet'}, 'to': {'hash': 'recipient'}}]
        mock_fetch_token.return_value = [{'timestamp': '2023-02-20T12:00:00.000Z', 'total': {'value': '10'}, 'token': {'symbol': 'TOK'}, 'from': {'hash': 'test_wallet'}, 'to': {'hash': 'recipient'}}]
        mock_fetch_internal.return_value = [{'timestamp': '2023-03-25T12:00:00.000Z', 'value': '2', 'from': {'hash': 'test_wallet'}, 'to': {'hash': 'recipient'}}]

        # Test with no date range
        transactions = process_transactions('test_wallet')
        self.assertEqual(len(transactions), 3)

        # Test with a start date
        transactions = process_transactions('test_wallet', start_date_str='2023-02-01')
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['Date'], '2023-02-20T12:00:00.000Z')

        # Test with an end date
        transactions = process_transactions('test_wallet', end_date_str='2023-02-28')
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[1]['Date'], '2023-02-20T12:00:00.000Z')

        # Test with both a start and end date
        transactions = process_transactions('test_wallet', start_date_str='2023-01-01', end_date_str='2023-01-31')
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['Date'], '2023-01-15T12:00:00.000Z')

if __name__ == '__main__':
    unittest.main()
