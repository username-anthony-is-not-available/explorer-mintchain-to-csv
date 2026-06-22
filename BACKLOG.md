# Project Backlog

This backlog tracks the progress of the `explorer-mintchain-to-csv` project.

## 🏆 Milestones

### Core Infrastructure
- [x] Basic Etherscan-like API integration
- [x] MintChain (Routescan V2) support
- [x] Standardized `Transaction` model with Pydantic
- [x] Multi-wallet batch processing
- [x] Date range filtering via block numbers

### Categorization & Labels
- [x] DeFi swap detection from transfers
- [x] NFT (ERC-721/1155) transfer support
- [x] Bridge transaction identification
- [x] Koinly-compatible label mapping
- [ ] Refine internal transaction categorization for complex smart contracts

### Export Formats
- [x] Generic CSV & JSON
- [x] Koinly Universal CSV
- [x] CoinTracker CSV
- [x] CryptoTaxCalculator CSV
- [ ] ZenLedger CSV support (Initial implementation exists, needs verification)

### Operations & Maintenance
- [x] Dockerization for scheduled runs
- [x] CI/CD with GitHub Actions (Tests & Security Audit)
- [ ] Automated weekly regression testing against "Golden Master" hashes
- [ ] Documentation: Comprehensive API adapter guide

## 📅 Upcoming Tasks
- [ ] Verify ZenLedger writer compatibility with latest template
- [ ] Implement automated regression test scheduling
- [ ] Update documentation for adding new explorer adapters
