# explorer-mintchain-to-csv

A tool designed to streamline the process of exporting blockchain transaction data to a Koinly-compatible CSV file. By utilizing the Explorer MintChain API, this project automatically fetches transaction data, including transfers, fees, and token movements, and generates a CSV file that can be imported into Koinly for tax reporting and portfolio tracking.

## Features

- Fetches transactions, token transfers, and internal transactions from the MintChain Explorer API.
- Combines and sorts the data by timestamp.
- Exports the transaction data to a CSV file compatible with Koinly.
- Configurable wallet address and timeout settings for API requests.

## Requirements

- Python 3.6 or higher
- Requests library (`pip install requests`)

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

1. Create a `.env` file in the project root directory to store your wallet address:

   ```bash
   WALLET_ADDRESS=your_wallet_address_here
   ```

2. Modify the `main.py` file to read the wallet address from the `.env` file.

## Usage

To run the script and export the blockchain transaction data:

1. Ensure your wallet address is correctly configured in the `.env` file.
2. Run the script:

   ```bash
   python main.py
   ```

The script will fetch the data from the MintChain Explorer API, combine and sort the transactions, and then output a CSV file named `blockchain_transactions.csv` in the `output` folder.

## Example Output

The CSV file will include the following columns:

- Transaction hash
- From address
- To address
- Amount transferred
- Token symbol (if applicable)
- Gas fee
- Transaction timestamp
- Additional fields depending on transaction type

## Troubleshooting

- **Empty CSV file:** Ensure that the API response contains data for your wallet address. Check the logs for any error messages or missing data.
- **API request issues:** If you receive timeouts or errors, consider adjusting the `TIMEOUT` value in the script or checking the status of the MintChain Explorer API.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MintChain Explorer API](https://explorer.mintchain.io) for providing the blockchain data.
- [Koinly](https://koinly.io) for making tax reporting easier with a simple CSV import feature.
