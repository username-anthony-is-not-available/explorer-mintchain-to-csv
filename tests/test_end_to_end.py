
import json
from pathlib import Path
from unittest.mock import patch
import main as main_module

MINTCHAIN_API_URL = "https://api.routescan.io/v2/network/mainnet/evm/185/etherscan"
TEST_WALLET_ADDRESS = "0x1111111111111111111111111111111111111111"


def test_cli_json_output(responses):
    """
    Tests the CLI tool's JSON output by mocking API calls.
    The 'responses' argument is a fixture provided by the pytest-responses library.
    """
    # Mock the API calls for normal transactions and token transactions
    responses.add(
        responses.GET,
        f"{MINTCHAIN_API_URL}?module=account&action=txlist&address={TEST_WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={
            "result": [
                {
                    "blockNumber": "1",
                    "timeStamp": "1672531200",
                    "hash": "0xTestHash",
                    "nonce": "0",
                    "blockHash": "0xBlockHash",
                    "transactionIndex": "0",
                    "from": {"hash": TEST_WALLET_ADDRESS},
                    "to": {"hash": "0x2222222222222222222222222222222222222222"},
                    "value": "1000000000000000000",  # 1 ETH
                    "gasUsed": "21000",
                    "gasPrice": "1000000000",  # 1 Gwei
                    "isError": "0",
                    "txreceipt_status": "1",
                    "input": "0x",
                    "contractAddress": "",
                    "cumulativeGasUsed": "21000",
                    "confirmations": "1",
                }
            ]
        },
        status=200,
    )
    responses.add(
        responses.GET,
        f"{MINTCHAIN_API_URL}?module=account&action=tokentx&address={TEST_WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={"result": []},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{MINTCHAIN_API_URL}?module=account&action=txlistinternal&address={TEST_WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={"result": []},
        status=200,
    )

    # Command to run the CLI tool
    test_args = [
        "main.py",
        "--wallet",
        TEST_WALLET_ADDRESS,
        "--format",
        "json",
        "--chain",
        "mintchain",
    ]

    with patch("sys.argv", test_args):
        main_module.main()

    output_file = Path("output") / f"{TEST_WALLET_ADDRESS}_transactions.json"

    try:
        # Assert that the output file was created
        assert output_file.exists(), f"Output file was not created: {output_file}"

        with open(output_file, "r") as f:
            data = json.load(f)

        # The current output of main.py for JSON is a dump of the Transaction models.
        # Based on extract_transaction_data.py, for a simple ETH transfer it should look like this:
        expected_data = [
            {
                "Date": "1672531200",
                "Sent Amount": "1",
                "Sent Currency": "ETH",
                "Received Amount": None,
                "Received Currency": None,
                "Fee Amount": "0.000021",
                "Fee Currency": "ETH",
                "Net Worth Amount": "",
                "Net Worth Currency": "",
                "Label": "transfer",
                "Description": "transaction",
                "TxHash": "0xTestHash",
            }
        ]

        # Assert that the content of the output file is correct
        assert data == expected_data, f"The output JSON data does not match the expected data. Actual: {data}"

    finally:
        # Clean up the created file
        if output_file.exists():
            output_file.unlink()
