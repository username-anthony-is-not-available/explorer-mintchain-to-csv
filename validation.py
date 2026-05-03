import logging
from typing import Dict, List

from models import Transaction

logger = logging.getLogger(__name__)

class KoinlyValidationError:
    def __init__(self, tx_hash: str, issue: str):
        self.tx_hash = tx_hash
        self.issue = issue

    def __repr__(self):
        return f"Transaction {self.tx_hash}: {self.issue}"

def validate_transactions_for_koinly(transactions: List[Dict[str, str]]) -> List[KoinlyValidationError]:
    """
    Validates a list of transaction dictionaries for Koinly compatibility.
    
    Checks for:
    - Missing prices (Sent Amount/Received Amount without matching Currency)
    - Unknown transaction labels
    - Invalid fee information
    """
    errors = []
    valid_labels = {"", "bridge", "swap", "mint", "burn", "nft_transfer", "token_transfer",
                     "transfer", "staking", "airdrop", "mining", "cost"}
    
    for tx in transactions:
        tx_hash = tx.get("TxHash", "unknown")
        
        # Check for missing currencies
        if tx.get("Sent Amount") and not tx.get("Sent Currency"):
            errors.append(KoinlyValidationError(tx_hash, "Sent Amount present but Sent Currency missing"))
        if tx.get("Received Amount") and not tx.get("Received Currency"):
            errors.append(KoinlyValidationError(tx_hash, "Received Amount present but Received Currency missing"))
        
        # Check for unknown labels
        label = tx.get("Label", "")
        if label and label not in valid_labels:
            errors.append(KoinlyValidationError(tx_hash, f"Unknown transaction label: {label}"))
        
        # Check fee information
        if tx.get("Fee Amount") and not tx.get("Fee Currency"):
            errors.append(KoinlyValidationError(tx_hash, "Fee Amount present but Fee Currency missing"))
    
    return errors

def print_validation_report(errors: List[KoinlyValidationError]) -> None:
    """Prints a validation report to stderr."""
    if not errors:
        logger.info("✅ No Koinly validation errors found.")
        return
    
    logger.warning(f"Found {len(errors)} Koinly validation error(s):")
    for error in errors:
        logger.warning(f"  - {error}")
