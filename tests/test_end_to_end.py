
import json
import shutil
import subprocess
from pathlib import Path

MINTCHAIN_API_URL = "https://explorer.mintchain.io/api"
TEST_WALLET_ADDRESS = "0x1111111111111111111111111111111111111111"


def test_cli_json_output(responses):
    """
    Tests the CLI tool's JSON output by mocking API calls.
    The 'responses' argument is a fixture provided by the pytest-responses library.
    """
    # Mock the API calls for normal transactions and token transactions
    responses.add(
        responses.GET,
        f"{MINTCHAIN_API_URL}?module=account&action=txlist&address={TEST_WALLET_ADDRESS}",
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
                    "gas": "21000",
                    "gasPrice": "1000000000",  # 1 Gwei
                    "isError": "0",
                    "txreceipt_status": "1",
                    "input": "0x",
                    "contractAddress": "",
                    "cumulativeGasUsed": "21000",
                    "gasUsed": "21000",
                    "confirmations": "1",
                }
            ]
        },
        status=200,
    )
    responses.add(
        responses.GET,
        f"{MINTCHAIN_API_URL}?module=account&action=tokentx&address={TEST_WALLET_ADDRESS}",
        json={"result": []},
        status=200,
    )

    # Command to run the CLI tool
    command = [
        "python",
        "main.py",
        "--wallet",
        TEST_WALLET_ADDRESS,
        "--format",
        "json",
        "--chain",
        "mintchain",
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    # Assert that the command executed successfully
    assert result.returncode == 0, f"CLI command failed with error: {result.stderr}"

    output_dir = Path(TEST_WALLET_ADDRESS)
    output_file = output_dir / "all_transactions.json"

    try:
        # Assert that the output file was created
        assert output_file.exists(), f"Output file was not created: {output_file}"

        with open(output_file, "r") as f:
            data = json.load(f)

        expected_data = [
            {
                "ID": "0xTestHash",
                "Date": "2023-01-01 00:00:00",
                "Sent Amount": "1.0",
                "Sent Currency": "ETH",
                "Received Amount": None,
                "Received Currency": None,
                "Fee Amount": "0.000021",
                "Fee Currency": "ETH",
                "Label": "transfer",
                "Description": f"From {TEST_WALLET_ADDRESS} to 0x2222222222222222222222222222222222222222",
                "TxHash": "0xTestHash",
            }
        ]

        # Assert that the content of the output file is correct
        assert data == expected_data, "The output JSON data does not match the expected data."

    finally:
        # Clean up the created directory and file
        if output_dir.exists():
            shutil.rmtree(output_dir)
