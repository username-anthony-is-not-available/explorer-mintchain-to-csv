# explorer-mintchain-to-csv

A tool designed to streamline the process of exporting blockchain transaction data to a Koinly-compatible CSV file. By utilizing the Explorer MintChain API, this project automatically fetches transaction data, including transfers, fees, and token movements, and generates a CSV or JSON file that can be imported into Koinly for tax reporting and portfolio tracking.

## Features

- Fetches transactions, token transfers, and internal transactions from the MintChain Explorer API.
- Combines and sorts the data by timestamp.
- Exports the transaction data to CSV (Koinly-compatible) or JSON format.
- Filter transactions by date range.
- Configurable wallet address via environment variable or command-line argument.

## Requirements

- Python 3.6 or higher
- Required packages:
  - `requests` - HTTP library for API requests
  - `python-dotenv` - Environment variable management

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/explorer-mintchain-to-csv.git
   ```

2. Navigate into the project directory:

   ```bash
   cd explorer-mintchain-to-csv
   ```

3. Install the necessary Python dependencies:

   ```bash
   pip install -r requirements.txt
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

## Example Output

The CSV file follows the Koinly Universal Format and includes the following columns:

| Column               | Description                                                      |
| -------------------- | ---------------------------------------------------------------- |
| `Date`               | Unix timestamp of the transaction                                |
| `Sent Amount`        | Amount sent (if outgoing transaction)                            |
| `Sent Currency`      | Currency/token symbol for sent amount                            |
| `Received Amount`    | Amount received (if incoming transaction)                        |
| `Received Currency`  | Currency/token symbol for received amount                        |
| `Fee Amount`         | Transaction fee (gas used × gas price)                           |
| `Fee Currency`       | Currency for the fee (ETH)                                       |
| `Net Worth Amount`   | Net worth amount (optional)                                      |
| `Net Worth Currency` | Net worth currency (optional)                                    |
| `Label`              | Transaction label (optional)                                     |
| `Description`        | Transaction type: `transaction`, `internal`, or `token_transfer` |
| `TxHash`             | Transaction hash                                                 |

## Troubleshooting

- **Empty CSV file:** Ensure that the API response contains data for your wallet address. Check the logs for any error messages or missing data.
- **API request issues:** If you receive timeouts or errors, consider adjusting the `TIMEOUT` value in `config.py` or checking the status of the MintChain Explorer API.
- **No wallet address:** If you see "No wallet address provided", ensure you've set `WALLET_ADDRESS` in your `.env` file or use the `--wallet` argument.

## Acknowledgments

- [MintChain Explorer API](https://explorer.mintchain.io) for providing the blockchain data.
- [Koinly](https://koinly.io) for making tax reporting easier with a simple CSV import feature.
