import argparse
import os
from datetime import datetime

from dotenv import load_dotenv

from csv_writer import write_transaction_data_to_csv
from json_writer import write_transaction_data_to_json
from extract_transaction_data import extract_transaction_data
from fetch_blockchain_data import (
    fetch_internal_transactions,
    fetch_token_transfers,
    fetch_transactions,
)

# Load environment variables from .env file
load_dotenv()

# Constants
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

def combine_and_sort_transactions(transactions, token_transfers, internal_transactions):
    # Combine all transactions into one list
    all_transactions = transactions + token_transfers + internal_transactions

    # Convert the 'timestamp' field into a datetime object and sort by date
    all_transactions_sorted = sorted(all_transactions, key=lambda trx: datetime.strptime(trx['Date'], DATE_FORMAT))

    return all_transactions_sorted

def process_transactions(wallet_address, start_date_str=None, end_date_str=None):
    # Fetch and combine transactions
    transactions = fetch_transactions(wallet_address)
    token_transfers = fetch_token_transfers(wallet_address)
    internal_transactions = fetch_internal_transactions(wallet_address)

    # Extract transaction data
    extracted_regular_transactions = extract_transaction_data(transactions, 'transaction', wallet_address)
    extracted_token_transfers = extract_transaction_data(token_transfers, 'token_transfers', wallet_address)
    extracted_internal_transactions = extract_transaction_data(internal_transactions, 'internal_transaction', wallet_address)

    # Combine and sort all transactions by date
    all_sorted_transactions = combine_and_sort_transactions(
        extracted_regular_transactions,
        extracted_token_transfers,
        extracted_internal_transactions
    )

    # Filter transactions by date range if provided
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        all_sorted_transactions = [
            trx for trx in all_sorted_transactions
            if datetime.strptime(trx['Date'], DATE_FORMAT) >= start_date
        ]
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        all_sorted_transactions = [
            trx for trx in all_sorted_transactions
            if datetime.strptime(trx['Date'], DATE_FORMAT) <= end_date
        ]

    return all_sorted_transactions

# Main function
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch blockchain transaction data.')
    parser.add_argument('--wallet', type=str, help='Wallet address to fetch transactions for.')
    parser.add_argument('--start-date', type=str, help='Start date in YYYY-MM-DD format.')
    parser.add_argument('--end-date', type=str, help='End date in YYYY-MM-DD format.')
    parser.add_argument('--format', type=str, choices=['csv', 'json'], default='csv', help='Output format (csv or json).')
    args = parser.parse_args()
    # Get the wallet address from arguments or environment variable
    wallet_address = args.wallet if args.wallet else os.getenv('WALLET_ADDRESS')
    if not wallet_address:
        print("Error: No wallet address provided. Set it in the .env file or use the --wallet argument.")
        return

    # Process transactions
    all_sorted_transactions = process_transactions(wallet_address, args.start_date, args.end_date)
    # Define the output path based on the format
    output_file = f'output/blockchain_transactions.{args.format}'

    # Write the data to the selected format
    if args.format == 'csv':
        write_transaction_data_to_csv(output_file, all_sorted_transactions)
        print(f"CSV file has been written to {output_file}")
    elif args.format == 'json':
        write_transaction_data_to_json(output_file, all_sorted_transactions)
        print(f"JSON file has been written to {output_file}")

if __name__ == "__main__":
    main()
