# Blockchain Transaction Exporter

[![Python CI](https://github.com/jules-dot-dev/explorer-mintchain-to-csv/actions/workflows/test.yml/badge.svg)](https://github.com/jules-dot-dev/explorer-mintchain-to-csv/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/jules-dot-dev/explorer-mintchain-to-csv/badge.svg?branch=main)](https://coveralls.io/github/jules-dot-dev/explorer-mintchain-to-csv?branch=main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tool designed to streamline the process of exporting blockchain transaction data to various tax-software-compatible formats. By utilizing APIs from multiple blockchain explorers, this project automatically fetches transaction data, including transfers, fees, and token movements, and generates a file that can be imported into Koinly, CoinTracker, and other services for tax reporting and portfolio tracking.

## Features

- Fetches transactions, token transfers, and internal transactions from multiple blockchain explorer APIs.
- Supports multiple blockchains: Etherscan (Ethereum), Basescan (Base), Arbiscan (Arbitrum), and MintChain.
- Combines and sorts all transaction data by timestamp.
- Exports the transaction data to multiple formats: generic CSV, JSON, Koinly, CoinTracker, and CryptoTaxCalculator.
- Filters transactions by date range.
- Supports single wallet addresses or a file containing multiple addresses.
- Configurable via environment variables or command-line arguments.

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

3. Install the necessary Python dependencies for both running the application and development:

   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
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

2. Edit the `.env` file to add your wallet address and any optional API keys:

   ```bash
   # Your EVM wallet address for fetching transactions
   WALLET_ADDRESS=your_wallet_address_here

   # API keys for blockchain explorers (optional, but recommended for higher rate limits)
   ETHERSCAN_API_KEY=
   BASESCAN_API_KEY=
   ARBISCAN_API_KEY=
   ```

   **Note:** While API keys are optional, it is highly recommended to generate and use them to avoid rate-limiting issues with the public API endpoints.

## Usage

### Basic Usage

Run the script with default settings (uses wallet from `.env`, chain `mintchain`, outputs CSV):

```bash
python main.py
```

### Command-Line Options

| Option         | Description                                                                          |
| -------------- | ------------------------------------------------------------------------------------ |
| `--wallet`     | Wallet address to fetch transactions for (overrides `.env`).                           |
| `--address-file`| File containing a list of wallet addresses.                                          |
| `--start-date` | Filter transactions starting from this date (YYYY-MM-DD format).                     |
| `--end-date`   | Filter transactions up to this date (YYYY-MM-DD format).                             |
| `--format`     | Output format: `csv`, `json`, `koinly`, `cointracker`, `cryptotaxcalculator`.          |
| `--chain`      | Blockchain explorer to use: `mintchain` (default), `etherscan`, `basescan`, `arbiscan`. |

### Examples

Export all transactions for a specific wallet from Etherscan:

```bash
python main.py --wallet 0xYourWalletAddressHere --chain etherscan
```

Export transactions for a specific date range from Base:

```bash
python main.py --wallet 0xYourWalletAddressHere --chain basescan --start-date 2024-01-01 --end-date 2024-12-31
```

Export transactions for multiple wallets from Arbitrum to the Koinly format:

```bash
python main.py --address-file my_wallets.txt --chain arbiscan --format koinly
```

The output file will be saved to the `output/` folder (e.g., `output/blockchain_transactions.csv`).

## Troubleshooting

- **Empty output file:** Ensure that the API response contains data for your wallet address on the selected blockchain. Check the logs for any error messages.
- **API request issues:** If you receive timeouts or errors, you may be getting rate-limited. Consider adding API keys to your `.env` file. You can also adjust the `TIMEOUT` value in `config.py`.
- **No wallet address:** If you see "No wallet address provided", ensure you've set `WALLET_ADDRESS` in your `.env` file or use the `--wallet` or `--address-file` argument.

## Acknowledgments

- Blockchain Explorer APIs (Etherscan, Basescan, Arbiscan, MintChain) for providing the blockchain data.
- Tax software platforms like [Koinly](https://koinly.io) for making tax reporting easier with simple CSV import features.
