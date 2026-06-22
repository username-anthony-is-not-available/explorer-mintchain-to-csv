# Project Standards

This project follows the centralized standards managed by the [Intelligent Project Manager](https://github.com/username-anthony-is-not-available/intelligent-project-manager).

## Quick Reference

| Category          | Requirement                                                    |
| ----------------- | -------------------------------------------------------------- |
| **Test Coverage** | ≥80% for new code                                              |
| **Linting**       | Must pass before merge (flake8)                                |
| **Type Safety**   | Mandatory Python type hints (mypy)                             |
| **Commits**       | [Conventional Commits](https://conventionalcommits.org) format |
| **PRs**           | Require approval + passing CI                                  |
| **Secrets**       | Never committed; use env vars (.env)                           |

## Full Standards

For complete details, see:
→ [Global STANDARDS.md](https://github.com/username-anthony-is-not-available/intelligent-project-manager/blob/main/.agent/workflows/templates/STANDARDS.md)

## Local Overrides & Project-Specific Guidelines

- **Data Integrity**: Use Pydantic models (`models.py`) for all data structures passed between modules. Prefer `model_validate(dict)` over `**dict` when instantiating from API responses.
- **Precision**: Use `decimal.Decimal` for all currency and token amount calculations to avoid floating-point errors.
- **Concurrency**: Use `ThreadPoolExecutor` for network-bound tasks (e.g., fetching data for multiple wallets or different transaction types).
- **Network Resilience**: Always use the `fetch_data` utility in `fetch_blockchain_data.py` for API requests to ensure consistent retry logic and connection pooling.
- **Categorization**: Transaction labeling logic must reside in `transaction_categorization.py`. New contract addresses for swaps or bridges should be added to the configuration dictionaries there in **lowercase**.
- **User Feedback**: Use `tqdm` for progress bars in CLI operations, especially during long-running data fetches or processing batches.
- **Testing**: Mock all network requests using the `responses` library. Patch `fetch_blockchain_data.session.get` rather than `requests.get`.
