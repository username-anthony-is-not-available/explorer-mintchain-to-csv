import os
from datetime import datetime

from dotenv import load_dotenv

from csv_writer import write_transaction_data_to_csv
from extract_transaction_data import extract_transaction_data
from fetch_blockchain_data import (
    fetch_internal_transactions,
    fetch_token_transfers,
    fetch_transactions,
)

# Load environment variables from .env file
load_dotenv()

def combine_and_sort_transactions(transactions, token_transfers, internal_transactions):
    # Combine all transactions into one list
    all_transactions = transactions + token_transfers + internal_transactions

    # Convert the 'timestamp' field into a datetime object and sort by date
    all_transactions_sorted = sorted(all_transactions, key=lambda trx: datetime.strptime(trx['Date'], '%Y-%m-%dT%H:%M:%S.%fZ'))

    return all_transactions_sorted

# Main function
def main():
    # Get the wallet address from environment variable
    wallet_address = os.getenv('WALLET_ADDRESS')

    if not wallet_address:
        print("Error: WALLET_ADDRESS is not set in the .env file")
        return

    # Fetch and combine transactions
    transactions = fetch_transactions(wallet_address)
    token_transfers = fetch_token_transfers(wallet_address)
    internal_transactions = fetch_internal_transactions(wallet_address)

    # For regular transactions
    extracted_regular_transactions = extract_transaction_data(transactions, 'transaction', wallet_address)

    # For token transfers
    extracted_token_transfers = extract_transaction_data(token_transfers, 'token_transfers', wallet_address)

    # For internal transactions
    extracted_internal_transactions = extract_transaction_data(internal_transactions, 'internal_transaction', wallet_address)

    # Combine and sort all transactions by date
    all_sorted_transactions = combine_and_sort_transactions(extracted_regular_transactions, extracted_token_transfers, extracted_internal_transactions)

    # Define the output path for CSV
    output_file = 'output/blockchain_transactions.csv'

    # Write the data to CSV
    write_transaction_data_to_csv(output_file, all_sorted_transactions)
    print(f"CSV file has been written to {output_file}")

if __name__ == "__main__":
    main()
