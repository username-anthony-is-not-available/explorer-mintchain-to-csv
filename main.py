import argparse
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator, model_validator

from csv_writer import write_transaction_data_to_csv
from extract_transaction_data import extract_transaction_data
from fetch_blockchain_data import (
    fetch_internal_transactions,
    fetch_token_transfers,
    fetch_transactions,
)
from json_writer import write_transaction_data_to_json
from koinly_writer import write_transaction_data_to_koinly_csv
from models import Transaction
from config import EXPLORER_URLS

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')

class Args(BaseModel):
    wallet: Optional[str] = None
    address_file: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format: str
    chain: str = 'mintchain'

    @model_validator(mode='before')
    def validate_wallet_or_address_file(cls, values):
        wallet = values.get('wallet')
        address_file = values.get('address_file')

        # Get wallet from environment if not provided in args
        if not wallet and not address_file:
            wallet = os.getenv('WALLET_ADDRESS')

        if not wallet and not address_file:
            raise ValueError('Either --wallet, --address-file, or WALLET_ADDRESS environment variable must be provided.')

        if wallet and address_file:
            raise ValueError('Provide either --wallet or --address-file, but not both.')

        return values

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
    chain: str,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None
) -> List[Transaction]:
    # Fetch and combine transactions
    transactions = fetch_transactions(wallet_address, chain)
    token_transfers = fetch_token_transfers(wallet_address, chain)
    internal_transactions = fetch_internal_transactions(wallet_address, chain)

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


def process_batch_transactions(
    address_file: str,
    chain: str,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
) -> List[Transaction]:
    """
    Processes transactions for a batch of wallet addresses from a file.
    """
    try:
        with open(address_file, 'r') as f:
            wallet_addresses = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"Address file not found: {address_file}")
        return []

    all_transactions: List[Transaction] = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(
                process_transactions,
                wallet_address,
                chain,
                start_date_str,
                end_date_str
            ): wallet_address
            for wallet_address in wallet_addresses
        }

        for i, future in enumerate(as_completed(futures)):
            wallet_address = futures[future]
            try:
                transactions = future.result()
                all_transactions.extend(transactions)
                logging.info(
                    f"Successfully processed address "
                    f"{i + 1}/{len(wallet_addresses)}: {wallet_address}"
                )
            except Exception as e:
                logging.error(
                    f"Failed to process address {wallet_address}: {e}"
                )

            # Rate limiting
            time.sleep(0.2)  # 5 requests per second

    # Sort all collected transactions by date
    all_transactions_sorted: List[Transaction] = sorted(
        all_transactions, key=lambda trx: int(trx.date)
    )

    return all_transactions_sorted


# Main function
def main() -> None:
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch blockchain transaction data.')
    parser.add_argument('--wallet', type=str, help='Wallet address to fetch transactions for.')
    parser.add_argument('--address-file', type=str, help='File containing a list of wallet addresses.')
    parser.add_argument('--start-date', type=str, help='Start date in YYYY-MM-DD format.')
    parser.add_argument('--end-date', type=str, help='End date in YYYY-MM-DD format.')
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'koinly'], default='csv', help='Output format (csv, json, or koinly).')
    parser.add_argument('--chain', type=str, choices=list(EXPLORER_URLS.keys()), default='mintchain', help='Blockchain explorer to use.')

    try:
        args = parser.parse_args()
        validated_args = Args.model_validate(vars(args))
    except ValidationError as e:
        logging.error(f"Argument validation error: {e}")
        return

    # Determine whether to run in batch mode or single address mode
    if validated_args.address_file:
        all_sorted_transactions = process_batch_transactions(
            validated_args.address_file,
            validated_args.chain,
            validated_args.start_date,
            validated_args.end_date,
        )
    else:
        wallet_address = validated_args.wallet or os.getenv('WALLET_ADDRESS')
        if not wallet_address:
            logging.error(
                "No wallet address provided. "
                "Set it in the .env file or use the --wallet argument."
            )
            return

        all_sorted_transactions = process_transactions(
            wallet_address,
            validated_args.chain,
            validated_args.start_date,
            validated_args.end_date
        )

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
    elif validated_args.format == 'koinly':
        output_file = f'output/blockchain_transactions.{validated_args.format}'
        write_transaction_data_to_koinly_csv(output_file, output_data)
        print(f"Koinly CSV file has been written to {output_file}")

if __name__ == "__main__":
    main()
