import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, TypeVar
from urllib.parse import urlencode

from pydantic import BaseModel

from config import EXPLORER_API_KEYS, EXPLORER_URLS
from fetch_blockchain_data import fetch_data
from models import RawTokenTransfer, RawTransaction

T = TypeVar('T', bound=BaseModel)


class ExplorerAdapter(ABC):
    def __init__(self, chain: str):
        self.chain = chain

    def _get_explorer_api_url(self, params: Dict[str, Any]) -> str:
        """Constructs the full API URL for a given chain and parameters."""
        base_url = EXPLORER_URLS.get(self.chain)
        if not base_url:
            raise ValueError(f"Unsupported chain: {self.chain}")

        query_params = params.copy()
        api_key_env_var = EXPLORER_API_KEYS.get(self.chain)
        if api_key_env_var:
            api_key = os.getenv(api_key_env_var)
            if api_key:
                query_params['apikey'] = api_key

        encoded_params = urlencode(query_params)
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

    def _fetch_all_pages(self, params: Dict[str, Any], model: Type[T]) -> List[T]:
        """Fetches all pages of data from the API."""
        all_data: List[T] = []
        page = 1
        offset = 10000
        params['offset'] = offset
        params['sort'] = 'asc'

        while True:
            params['page'] = page
            url = self._get_explorer_api_url(params)
            data = fetch_data(url, model)
            if not data:
                break
            all_data.extend(data)
            if len(data) < offset:
                break
            page += 1
        return all_data


class EtherscanAdapter(ExplorerAdapter):
    def get_transactions(self, wallet_address: str) -> List[RawTransaction]:
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
        }
        return self._fetch_all_pages(params, RawTransaction)

    def get_token_transfers(self, wallet_address: str) -> List[RawTokenTransfer]:
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
        }
        return self._fetch_all_pages(params, RawTokenTransfer)

    def get_internal_transactions(self, wallet_address: str) -> List[RawTransaction]:
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
        }
        return self._fetch_all_pages(params, RawTransaction)


class BasescanAdapter(EtherscanAdapter):
    pass


class ArbiscanAdapter(EtherscanAdapter):
    pass


class MintchainAdapter(EtherscanAdapter):
    pass
