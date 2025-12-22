import argparse
import logging
import os
import sys
from datetime import datetime
from typing import List, Optional, Sequence

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator

from csv_writer import write_transaction_data_to_csv
from extract_transaction_data import extract_transaction_data
from fetch_blockchain_data import (
    fetch_internal_transactions,
    fetch_token_transfers,
    fetch_transactions,
)
from json_writer import write_transaction_data_to_json
from models import Transaction

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')

class Args(BaseModel):
    wallet: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format: str

    @field_validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        return v

def combine_and_sort_transactions(
    transactions: List[Transaction],
    token_transfers: List[Transaction],
    internal_transactions: List[Transaction]
) -> List[Transaction]:
    # Combine all transactions into one list
    all_transactions: List[Transaction] = transactions + token_transfers + internal_transactions

    # Convert the 'timestamp' field into a datetime object and sort by date
    all_transactions_sorted: List[Transaction] = sorted(
        all_transactions, key=lambda trx: int(trx.date)
    )

    return all_transactions_sorted


def process_transactions(
    wallet_address: str,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None
) -> List[Transaction]:
    # Fetch and combine transactions
    transactions = fetch_transactions(wallet_address)
    token_transfers = fetch_token_transfers(wallet_address)
    internal_transactions = fetch_internal_transactions(wallet_address)

    # Extract transaction data
    extracted_regular_transactions = extract_transaction_data(
        transactions, 'transaction', wallet_address
    )
    extracted_token_transfers = extract_transaction_data(
        token_transfers, 'token_transfers', wallet_address
    )
    extracted_internal_transactions = extract_transaction_data(
        internal_transactions, 'internal_transaction', wallet_address
    )

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
            if datetime.fromtimestamp(int(trx.date)) >= start_date
        ]
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(
            hour=23, minute=59, second=59
        )
        all_sorted_transactions = [
            trx for trx in all_sorted_transactions
            if datetime.fromtimestamp(int(trx.date)) <= end_date
        ]

    return all_sorted_transactions


# Main function
def main() -> None:
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch blockchain transaction data.')
    parser.add_argument('--wallet', type=str, help='Wallet address to fetch transactions for.')
    parser.add_argument('--start-date', type=str, help='Start date in YYYY-MM-DD format.')
    parser.add_argument('--end-date', type=str, help='End date in YYYY-MM-DD format.')
    parser.add_argument('--format', type=str, choices=['csv', 'json'], default='csv', help='Output format (csv or json).')

    try:
        args = parser.parse_args()
        validated_args = Args.model_validate(vars(args))
    except ValidationError as e:
        logging.error(f"Argument validation error: {e}")
        return

    # Get the wallet address from arguments or environment variable
    wallet_address = validated_args.wallet if validated_args.wallet else os.getenv('WALLET_ADDRESS')
    if not wallet_address:
        logging.error("No wallet address provided. Set it in the .env file or use the --wallet argument.")
        return

    # Process transactions
    all_sorted_transactions = process_transactions(wallet_address, validated_args.start_date, validated_args.end_date)

    # Convert Pydantic models to dictionaries for writers
    output_data = [trx.model_dump(by_alias=True) for trx in all_sorted_transactions]

    # Define the output path based on the format
    output_file = f'output/blockchain_transactions.{validated_args.format}'

    # Write the a to the selected format
    if validated_args.format == 'csv':
        write_transaction_data_to_csv(output_file, output_data)
        print(f"CSV file has been written to {output_file}")
    elif validated_args.format == 'json':
        write_transaction_data_to_json(output_file, output_data)
        print(f"JSON file has been written to {output_file}")

if __name__ == "__main__":
    main()
