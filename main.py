import argparse
import csv
import logging
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Type

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator, model_validator

from cointracker_writer import write_transaction_data_to_cointracker_csv
from cryptotaxcalculator_writer import write_transaction_data_to_cryptotaxcalculator_csv
from csv_writer import write_transaction_data_to_csv
from extract_transaction_data import extract_transaction_data
from explorer_adapters import (
    ArbiscanAdapter,
    BasescanAdapter,
    EtherscanAdapter,
    ExplorerAdapter,
    MintchainAdapter,
)
from json_writer import write_transaction_data_to_json
from koinly_writer import write_transaction_data_to_koinly_csv
from models import Transaction
from config import EXPLORER_URLS

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')

# Adapter mapping
ADAPTERS: Dict[str, Type[ExplorerAdapter]] = {
    'mintchain': MintchainAdapter,
    'etherscan': EtherscanAdapter,
    'basescan': BasescanAdapter,
    'arbiscan': ArbiscanAdapter,
}

class Args(BaseModel):
    wallet: Optional[str] = None
    address_file: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format: str
    chain: str = 'mintchain'

    @field_validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        return v

    @model_validator(mode='after')
    def check_at_least_one_address_source(self):
        if not self.wallet and not self.address_file and not os.getenv('WALLET_ADDRESS') and not os.getenv('WALLET_ADDRESSES'):
            raise ValueError("No wallet addresses provided. Use --wallet, --address-file, or set WALLET_ADDRESS/WALLET_ADDRESSES in your .env file.")
        return self

def is_valid_evm_address(address: str) -> bool:
    """
    Checks if a string is a valid EVM address.
    """
    return bool(re.match(r'^0x[0-9a-fA-F]{40}$', address))


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


def get_addresses_from_file(file_path: str) -> List[str]:
    """
    Reads wallet addresses from a TXT or CSV file.
    """
    addresses = []
    try:
        with open(file_path, 'r', newline='') as f:
            if file_path.endswith('.csv'):
                reader = csv.reader(f)
                for row in reader:
                    for cell in row:
                        clean_cell = cell.strip()
                        if is_valid_evm_address(clean_cell):
                            addresses.append(clean_cell)
            else:
                # Treat as TXT, one address per line
                for line in f:
                    clean_line = line.strip()
                    if is_valid_evm_address(clean_line):
                        addresses.append(clean_line)
                    elif clean_line:
                        # Fallback for lines that might not be perfectly formatted
                        # but could contain an address
                        parts = clean_line.split()
                        for part in parts:
                            if is_valid_evm_address(part):
                                addresses.append(part)
    except Exception as e:
        logging.error(f"Error reading address file {file_path}: {e}")
    return addresses


def process_transactions(
    wallet_address: str,
    chain: str,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None
) -> List[Transaction]:
    # Get the adapter for the selected chain
    adapter_class = ADAPTERS.get(chain)
    if not adapter_class:
        raise ValueError(f"Unsupported chain: {chain}")
    adapter = adapter_class(chain)

    # Fetch and combine transactions
    transactions = adapter.get_transactions(wallet_address)
    token_transfers = adapter.get_token_transfers(wallet_address)
    internal_transactions = adapter.get_internal_transactions(wallet_address)

    # Extract transaction data
    extracted_regular_transactions = extract_transaction_data(
        transactions, 'transaction', wallet_address, chain
    )
    extracted_token_transfers = extract_transaction_data(
        token_transfers, 'token_transfers', wallet_address, chain
    )
    extracted_internal_transactions = extract_transaction_data(
        internal_transactions, 'internal_transaction', wallet_address, chain
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


def process_single_wallet(
    wallet_address: str,
    chain: str,
    output_format: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    index: int = 0,
    total_count: int = 1
) -> None:
    """
    Processes a single wallet address.
    """
    try:
        all_sorted_transactions = process_transactions(
            wallet_address,
            chain,
            start_date,
            end_date
        )

        # Convert Pydantic models to dictionaries for writers
        output_data = [trx.model_dump(by_alias=True) for trx in all_sorted_transactions]

        # Define the output path based on the format
        output_file = f'output/{wallet_address}_transactions.{output_format}'

        # Write the data to the selected format
        if output_format == 'csv':
            write_transaction_data_to_csv(output_file, output_data)
        elif output_format == 'json':
            write_transaction_data_to_json(output_file, output_data)
        elif output_format == 'cointracker':
            write_transaction_data_to_cointracker_csv(output_file, output_data)
        elif output_format == 'cryptotaxcalculator':
            write_transaction_data_to_cryptotaxcalculator_csv(output_file, output_data)
        elif output_format == 'koinly':
            write_transaction_data_to_koinly_csv(output_file, output_data, chain=chain)

        logging.info(f"({index + 1}/{total_count}) "
                     f"Successfully wrote {len(output_data)} transactions to {output_file} for wallet {wallet_address}")

    except Exception as e:
        logging.error(f"Failed to process address {wallet_address}: {e}")
        raise


def process_batch_transactions(
    addresses: List[str],
    chain: str,
    output_format: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> None:
    """
    Processes multiple wallet addresses concurrently.
    """
    total = len(addresses)
    logging.info(f"Starting batch process for {total} wallet(s) on {chain}...")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(
                process_single_wallet,
                wallet_address,
                chain,
                output_format,
                start_date,
                end_date,
                i,
                len(addresses)
            ): wallet_address
            for i, wallet_address in enumerate(addresses)
        }

        for future in as_completed(futures):
            wallet_address = futures[future]
            try:
                future.result()
            except Exception as e:
                # Error is already logged in process_single_wallet
                pass


# Main function
def main() -> None:
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch blockchain transaction data.')
    parser.add_argument('--wallet', type=str, help='Comma-separated wallet addresses to fetch transactions for.')
    parser.add_argument('--address-file', type=str, help='File containing a list of wallet addresses.')
    parser.add_argument('--start-date', type=str, help='Start date in YYYY-MM-DD format.')
    parser.add_argument('--end-date', type=str, help='End date in YYYY-MM-DD format.')
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'json', 'cointracker', 'cryptotaxcalculator', 'koinly'],
        default='csv',
        help='Output format (csv, json, cointracker, cryptotaxcalculator, or koinly).'
    )
    parser.add_argument('--chain', type=str, choices=list(EXPLORER_URLS.keys()), default='mintchain', help='Blockchain explorer to use.')

    try:
        args = parser.parse_args()
        validated_args = Args.model_validate(vars(args))
    except ValidationError as e:
        logging.error(f"Argument validation error: {e}")
        return

    # Collect wallet addresses from all sources
    wallet_addresses = []
    if validated_args.wallet:
        wallet_addresses.extend([addr.strip() for addr in validated_args.wallet.split(',') if addr.strip()])
    if validated_args.address_file:
        wallet_addresses.extend(get_addresses_from_file(validated_args.address_file))

    # Fallback to environment variables if no addresses are provided via arguments
    if not wallet_addresses:
        env_addresses = os.getenv('WALLET_ADDRESSES')
        if env_addresses is not None:
            wallet_addresses.extend([addr.strip() for addr in env_addresses.split(',') if addr.strip()])
        else:
            env_wallet = os.getenv('WALLET_ADDRESS')
            if env_wallet is not None:
                wallet_addresses.append(env_wallet.strip())

    # Ensure there are unique addresses to process (lowercased for deduplication)
    unique_addresses = sorted(list(set(
        addr.lower() for addr in wallet_addresses
        if addr and is_valid_evm_address(addr)
    )))

    if not unique_addresses:
        logging.error(
            "No wallet addresses provided. Use --wallet, --address-file, "
            "or set WALLET_ADDRESS/WALLET_ADDRESSES in your .env file."
        )
        return

    # Process all wallet addresses in batch (sequentially)
    process_batch_transactions(
        unique_addresses,
        validated_args.chain,
        validated_args.format,
        validated_args.start_date,
        validated_args.end_date
    )

if __name__ == "__main__":
    main()
