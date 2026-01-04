import os
from abc import ABC, abstractmethod
from typing import Dict, List
from urllib.parse import urlencode

from config import EXPLORER_API_KEYS, EXPLORER_URLS
from fetch_blockchain_data import fetch_data
from models import RawTokenTransfer, RawTransaction


class ExplorerAdapter(ABC):
    def __init__(self, chain: str):
        self.chain = chain

    def _get_explorer_api_url(self, params: Dict[str, any]) -> str:
        """Constructs the full API URL for a given chain and parameters."""
        base_url = EXPLORER_URLS.get(self.chain)
        if not base_url:
            raise ValueError(f"Unsupported chain: {self.chain}")

        api_key_env_var = EXPLORER_API_KEYS.get(self.chain)
        if api_key_env_var:
            api_key = os.getenv(api_key_env_var)
            if api_key:
                params['apikey'] = api_key

        encoded_params = urlencode(params)
        return f"{base_url}?{encoded_params}"

    @abstractmethod
    def get_transactions(self, wallet_address: str) -> List[RawTransaction]:
        pass

    @abstractmethod
    def get_token_transfers(self, wallet_address: str) -> List[RawTokenTransfer]:
        pass

    @abstractmethod
    def get_internal_transactions(self, wallet_address: str) -> List[RawTransaction]:
        pass


class EtherscanAdapter(ExplorerAdapter):
    def get_transactions(self, wallet_address: str) -> List[RawTransaction]:
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
        }
        url = self._get_explorer_api_url(params)
        return fetch_data(url, RawTransaction)

    def get_token_transfers(self, wallet_address: str) -> List[RawTokenTransfer]:
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
        }
        url = self._get_explorer_api_url(params)
        return fetch_data(url, RawTokenTransfer)

    def get_internal_transactions(self, wallet_address: str) -> List[RawTransaction]:
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
        }
        url = self._get_explorer_api_url(params)
        return fetch_data(url, RawTransaction)


class BasescanAdapter(EtherscanAdapter):
    pass


class ArbiscanAdapter(EtherscanAdapter):
    pass


class MintchainAdapter(EtherscanAdapter):
    pass
