# AGENTS.md

This document provides guidance for AI agents working on the `explorer-mintchain-to-csv` repository.

## Project Overview

This project is a Python-based tool for fetching blockchain transaction data from various Etherscan-like APIs (MintChain, Etherscan, Basescan, Arbiscan) and exporting it to multiple formats, including generic CSV, JSON, and several tax software-compatible formats (Koinly, CoinTracker, CryptoTaxCalculator).

The primary goal is to provide a simple, command-line-driven way to get tax-ready transaction reports for EVM-compatible wallets.

## Core Architecture

The application follows a modular architecture:

-   **`main.py`**: The entry point of the application. It handles command-line argument parsing, orchestrates the fetching and writing process, and uses a `ThreadPoolExecutor` to process multiple wallets concurrently.
-   **`explorer_adapters.py`**: Implements the Adapter Pattern to fetch data from different blockchain explorers. The `ExplorerAdapter` abstract base class defines the interface, and concrete implementations (e.g., `EtherscanAdapter`, `MintchainAdapter`) handle the specifics of each API.
-   **`fetch_blockchain_data.py`**: Contains a generic `fetch_data` function with robust retry logic (`tenacity`) that all adapters use to make HTTP requests.
-   **`models.py`**: Defines the Pydantic data models used throughout the application (e.g., `Transaction`, `RawTransaction`) to ensure data consistency and validation.
-   **`extract_transaction_data.py`**: Responsible for transforming the raw API response data into the standardized `Transaction` model.
-   **`transaction_categorization.py`**: Contains heuristics to categorize transactions (e.g., DeFi swaps, NFT transfers, bridge transactions) by inspecting transaction details and comparing them against known contract addresses.
-   **Writer Modules (`csv_writer.py`, `koinly_writer.py`, etc.)**: Each module is responsible for writing the processed transaction data to a specific output format.

## Key Workflows

### Adding a New Blockchain Explorer

1.  **Create a new Adapter**: In `explorer_adapters.py`, create a new class that inherits from `ExplorerAdapter`.
2.  **Add URL to config**: In `config.py`, add the new explorer's API URL to the `EXPLORER_URLS` dictionary.
3.  **Map in `main.py`**: In `main.py`, add the new chain and its adapter class to the `ADAPTERS` dictionary.
4.  **API Key (Optional)**: If the API requires a key, add it to `config.py` in the `EXPLORER_API_KEYS` dictionary and update the `.env.example` file.

### Adding a New Output Format

1.  **Create a new writer module**: Create a new file (e.g., `newformat_writer.py`) that contains a function to write data to the desired format. The function should accept a file path and a list of transaction dictionaries as arguments.
2.  **Integrate into `main.py`**:
    -   Import the new writer function.
    -   Add the new format as a choice in the `--format` `argparse` argument.
    -   Add a condition to the `if/elif` block at the end of `main` to call your new writer function when the format is selected.

## Testing

-   Tests are located in the `tests/` directory and are written using `pytest`.
-   The `responses` library is used to mock HTTP requests to blockchain explorer APIs.
-   To run the full test suite, use the command: `python -m pytest`
-   When adding new code, please add corresponding unit tests and ensure test coverage meets project standards (≥80%).

## Conventions and Standards

-   **Type Hinting**: All code should be fully type-hinted. `mypy` is used for static analysis. Run `mypy .` to check for type errors.
-   **Linting**: The project uses `flake8` for linting. The configuration is in `.flake8`. Run `flake8` to check for style issues.
-   **Commit Messages**: Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
-   **Pydantic Models**: Use Pydantic models for all data structures that are passed between modules to ensure data integrity. When instantiating models from dictionaries where field aliases are used, prefer `model_validate(dict)` over `**dict`.
-   **Environment Variables**: All secrets (like API keys) and configuration that might vary between environments should be managed via a `.env` file. Do not commit secrets to the repository.
-   **Dependencies**: Application dependencies are in `requirements.txt`. Development dependencies are in `requirements-dev.txt`.
