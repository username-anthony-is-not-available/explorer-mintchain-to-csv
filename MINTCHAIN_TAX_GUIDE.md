# MintChain Tax Guide

This guide explains how to use transaction data exported from MintChain for tax reporting, specifically with Koinly.

## Verifying Your Data

1.  **Export Transactions**: Run the tool with `--chain mintchain` to fetch all transactions for your wallet.
    ```bash
    python main.py --wallet YOUR_WALLET_ADDRESS --chain mintchain --format koinly
    ```
2.  **Check Transaction Labels**: Ensure transactions are correctly labeled as `bridge`, `swap`, `mint`, `staking`, etc. Use the `--format json` export to inspect raw transaction data.
3.  **Verify Balances**: Use the balance summary (printed to stderr) to confirm total token balances match your records.

## Identifying Bridge Transactions

MintChain bridge transactions are automatically labeled as `bridge` in exports. Key indicators:
- **Outgoing bridges**: Sent to `0x4200000000000000000000000000000000000010` (L2StandardBridge)
- **Incoming bridges**: Received from the same bridge address
- These transactions typically involve ETH or wrapped tokens moving between MintChain and Ethereum mainnet

## Uploading to Koinly

1.  **Export Format**: Use `--format koinly` to generate a Koinly-compatible CSV file.
2.  **Koinly Import**:
    - Log in to your Koinly account
    - Go to **Wallets** > **Add Wallet** > **Upload CSV**
    - Select "MintChain" as the blockchain
    - Upload the generated CSV file
3.  **Label Adjustments**: Koinly may auto-detect some labels, but review:
    - Bridge transactions: Ensure they are marked as "Transfer" or "Bridge" in Koinly
    - Swaps: Verify "Trade" label is applied
    - Staking rewards: Confirm "Staking" or "Reward" label

## Common Tax Scenarios

| Transaction Type | Tax Implication |
|-------------------|-----------------|
| Token Swaps       | Capital gain/loss on the disposed token |
| Bridge Out        | Not taxable (transfer of basis) |
| Bridge In         | Not taxable (receipt of existing assets) |
| Staking Rewards   | Ordinary income at time of receipt |
| NFT Mints         | Not taxable (creation of asset) |
| Gas Fees          | Deductible as investment expense (consult tax professional) |

## Support

For issues with the export tool, check the [GitHub Issues](https://github.com/yourusername/explorer-mintchain-to-csv/issues). For tax advice, consult a qualified crypto tax professional.
