import csv
import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Union, Any, Optional
from models import TransactionType

class BaseWriter(ABC):
    @abstractmethod
    def write(self, output_file: str, transaction_data: List[Dict[str, Any]], **kwargs) -> None:
        pass

    def _ensure_dir(self, output_file: str):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

class CSVWriter(BaseWriter):
    def write(self, output_file: str, transaction_data: List[Dict[str, Any]], **kwargs) -> None:
        self._ensure_dir(output_file)
        fieldnames = ['Date', 'Sent Amount', 'Sent Currency', 'Received Amount', 'Received Currency',
                      'Fee Amount', 'Fee Currency', 'Net Worth Amount', 'Net Worth Currency',
                      'Label', 'Description', 'TxHash']
        
        if transaction_data and 'Wallet' in transaction_data[0]:
            fieldnames.insert(0, 'Wallet')

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(transaction_data)

class JSONWriter(BaseWriter):
    def write(self, output_file: str, transaction_data: List[Dict[str, Any]], **kwargs) -> None:
        self._ensure_dir(output_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transaction_data, f, indent=4)

class KoinlyWriter(BaseWriter):
    KOINLY_LABEL_MAP = {
        TransactionType.STAKING.value: "staking",
        TransactionType.AIRDROP.value: "airdrop",
        TransactionType.MINING.value: "mining",
        TransactionType.BRIDGE.value: "Bridge",
        TransactionType.MINT.value: "reward",
        TransactionType.BURN.value: "lost",
        TransactionType.COST.value: "cost",
    }
    MINTCHAIN_LABEL_MAP = {
        TransactionType.TRANSFER.value: "",
        TransactionType.TOKEN_TRANSFER.value: "",
        TransactionType.STAKING.value: "reward",
    }

    def write(self, output_file: str, transaction_data: List[Dict[str, Any]], **kwargs) -> None:
        self._ensure_dir(output_file)
        chain = kwargs.get("chain", "mintchain")
        
        processed_transactions = []
        for tx in transaction_data:
            processed_tx = tx.copy()
            label = processed_tx.get("Label")
            if chain == 'mintchain' and label in self.MINTCHAIN_LABEL_MAP:
                processed_tx["Label"] = self.MINTCHAIN_LABEL_MAP[label]
            elif label and label in self.KOINLY_LABEL_MAP:
                processed_tx["Label"] = self.KOINLY_LABEL_MAP[label]
            processed_transactions.append(processed_tx)

        fieldnames = ['Date', 'Sent Amount', 'Sent Currency', 'Received Amount', 'Received Currency',
                      'Fee Amount', 'Fee Currency', 'Net Worth Amount', 'Net Worth Currency',
                      'Label', 'Description', 'TxHash']
        
        if transaction_data and 'Wallet' in transaction_data[0]:
            fieldnames.insert(0, 'Wallet')

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_transactions)

class ZenLedgerWriter(BaseWriter):
    def _map_type(self, tx: Dict[str, Any]) -> str:
        sent_amount = tx.get("Sent Amount")
        received_amount = tx.get("Received Amount")
        label = tx.get("Label")
        if label == "swap": return "trade"
        if sent_amount and received_amount: return "trade"
        if sent_amount: return "send"
        if received_amount: return "receive"
        return "send"

    def write(self, output_file: str, transaction_data: List[Dict[str, Any]], **kwargs) -> None:
        self._ensure_dir(output_file)
        zenledger_data = []
        for tx in transaction_data:
            zenledger_data.append({
                "Timestamp": tx.get("Date"),
                "Type": self._map_type(tx),
                "IN Amount": tx.get("Received Amount"),
                "IN Currency": tx.get("Received Currency"),
                "OUT Amount": tx.get("Sent Amount"),
                "OUT Currency": tx.get("Sent Currency"),
                "Fee Amount": tx.get("Fee Amount"),
                "Fee Currency": tx.get("Fee Currency"),
            })
        
        fieldnames = ["Timestamp", "Type", "IN Amount", "IN Currency", "OUT Amount", "OUT Currency", "Fee Amount", "Fee Currency"]
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(zenledger_data)

class CoinTrackerWriter(BaseWriter):
    def write(self, output_file: str, transaction_data: List[Dict[str, Any]], **kwargs) -> None:
        self._ensure_dir(output_file)
        fieldnames = ['Date', 'Received Quantity', 'Received Currency', 'Sent Quantity', 'Sent Currency', 'Fee Amount', 'Fee Currency', 'Tag']
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for trx in transaction_data:
                writer.writerow({
                    'Date': trx.get('Date'),
                    'Received Quantity': trx.get('Received Amount'),
                    'Received Currency': trx.get('Received Currency'),
                    'Sent Quantity': trx.get('Sent Amount'),
                    'Sent Currency': trx.get('Sent Currency'),
                    'Fee Amount': trx.get('Fee Amount'),
                    'Fee Currency': trx.get('Fee Currency'),
                    'Tag': trx.get('Label')
                })

class CryptoTaxCalculatorWriter(BaseWriter):
    def _map_type(self, trx: Dict[str, Any]) -> str:
        label = trx.get('Label')
        sent_amount = trx.get('Sent Amount')
        received_amount = trx.get('Received Amount')
        sent_currency = trx.get('Sent Currency')
        received_currency = trx.get('Received Currency')

        if label == 'swap':
            if received_currency in ['USD', 'EUR', 'GBP']: return 'sell'
            if sent_currency in ['USD', 'EUR', 'GBP']: return 'buy'
            return 'sell'
        if label == 'simple_transfer':
            return 'send' if sent_amount else 'receive'
        if label == 'nft_transfer':
            return 'send' if sent_amount else 'receive'
        
        # Fallback logic
        if sent_amount and received_amount: return 'sell'
        if sent_amount: return 'send'
        if received_amount: return 'receive'
        return 'send'

    def write(self, output_file: str, transaction_data: List[Dict[str, Any]], **kwargs) -> None:
        self._ensure_dir(output_file)
        fieldnames = ['Timestamp (UTC)', 'Type', 'Base Currency', 'Base Amount', 'Quote Currency', 'Quote Amount', 'Fee Currency', 'Fee Amount', 'ID']
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for trx in transaction_data:
                tx_type = self._map_type(trx)
                
                if tx_type in ['buy', 'sell']:
                    base_currency = trx.get('Received Currency') if tx_type == 'buy' else trx.get('Sent Currency')
                    base_amount = trx.get('Received Amount') if tx_type == 'buy' else trx.get('Sent Amount')
                    quote_currency = trx.get('Sent Currency') if tx_type == 'buy' else trx.get('Received Currency')
                    quote_amount = trx.get('Sent Amount') if tx_type == 'buy' else trx.get('Received Amount')
                else:
                    base_currency = trx.get('Sent Currency') if trx.get('Sent Amount') else trx.get('Received Currency')
                    base_amount = trx.get('Sent Amount') if trx.get('Sent Amount') else trx.get('Received Amount')
                    quote_currency = ''
                    quote_amount = ''

                writer.writerow({
                    'Timestamp (UTC)': trx.get('Date'),
                    'Type': tx_type,
                    'Base Currency': base_currency,
                    'Base Amount': base_amount,
                    'Quote Currency': quote_currency,
                    'Quote Amount': quote_amount,
                    'Fee Currency': trx.get('Fee Currency'),
                    'Fee Amount': trx.get('Fee Amount'),
                    'ID': trx.get('TxHash')
                })

class WriterFactory:
    _writers = {
        "csv": CSVWriter,
        "json": JSONWriter,
        "koinly": KoinlyWriter,
        "zenledger": ZenLedgerWriter,
        "cointracker": CoinTrackerWriter,
        "cryptotaxcalculator": CryptoTaxCalculatorWriter,
    }

    @classmethod
    def get_writer(cls, format_name: str) -> BaseWriter:
        writer_class = cls._writers.get(format_name.lower())
        if not writer_class:
            raise ValueError(f"Unsupported format: {format_name}")
        return writer_class()
