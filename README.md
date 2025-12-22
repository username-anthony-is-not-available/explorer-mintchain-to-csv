# MintChain Transaction Exporter

[![Python CI](https://github.com/jules-dot-dev/explorer-mintchain-to-csv/actions/workflows/test.yml/badge.svg)](https://github.com/jules-dot-dev/explorer-mintchain-to-csv/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/jules-dot-dev/explorer-mintchain-to-csv/badge.svg?branch=main)](https://coveralls.io/github/jules-dot-dev/explorer-mintchain-to-csv?branch=main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tool designed to streamline the process of exporting blockchain transaction data to a Koinly-compatible CSV file. By utilizing the MintChain Explorer API, this project automatically fetches transaction data, including transfers, fees, and token movements, and generates a CSV or JSON file that can be imported into Koinly for tax reporting and portfolio tracking.

## Features

- Fetches transactions, token transfers, and internal transactions from the MintChain Explorer API.
- Combines and sorts the data by timestamp.
- Exports the transaction data to CSV (Koinly-compatible) or JSON format.
- Filters transactions by date range.
- Configurable wallet address via environment variable or command-line argument.

## Requirements

- Python 3.6 or higher
- Required packages:
  - `requests` - HTTP library for API requests
  - `python-dotenv` - Environment variable management

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jules-dot-dev/explorer-mintchain-to-csv.git
   ```

2. Navigate into the project directory:

   ```bash
   cd explorer-mintchain-to-csv
   ```

3. Install the necessary Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Development

To install the development dependencies, run:

```bash
pip install -r requirements-dev.txt
```

## Testing

To run the test suite, use the following command:

```bash
PYTHONPATH=. pytest
```

## Configuration

1. Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your wallet address:

   ```bash
   WALLET_ADDRESS=your_wallet_address_here
   ```

## Usage

### Basic Usage

Run the script with default settings (uses wallet from `.env`, outputs CSV):

```bash
python main.py
```

### Command-Line Options

| Option         | Description                                                     |
| -------------- | --------------------------------------------------------------- |
| `--wallet`     | Wallet address to fetch transactions for (overrides `.env`)     |
| `--start-date` | Filter transactions starting from this date (YYYY-MM-DD format) |
| `--end-date`   | Filter transactions up to this date (YYYY-MM-DD format)         |
| `--format`     | Output format: `csv` (default) or `json`                        |

### Examples

Export all transactions for a specific wallet:

```bash
python main.py --wallet 0xYourWalletAddressHere
```

Export transactions for a specific date range:

```bash
python main.py --start-date 2024-01-01 --end-date 2024-12-31
```

Export to JSON format:

```bash
python main.py --format json
```

The output file will be saved to the `output/` folder as `blockchain_transactions.csv` or `blockchain_transactions.json`.

## Troubleshooting

- **Empty CSV file:** Ensure that the API response contains data for your wallet address. Check the logs for any error messages or missing data.
- **API request issues:** If you receive timeouts or errors, consider adjusting the `TIMEOUT` value in `config.py` or checking the status of the MintChain Explorer API.
- **No wallet address:** If you see "No wallet address provided", ensure you've set `WALLET_ADDRESS` in your `.env` file or use the `--wallet` argument.

## Acknowledgments

- [MintChain Explorer API](https://api.routescan.io/v2/network/mainnet/evm/185/etherscan) for providing the blockchain data.
- [Koinly](https://koinly.io) for making tax reporting easier with a simple CSV import feature.
