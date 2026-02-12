import os
from abc import ABC, abstractmethod
from typing import Dict, List, Type, TypeVar
from urllib.parse import urlencode

from pydantic import BaseModel

from config import EXPLORER_API_KEYS, EXPLORER_URLS
from fetch_blockchain_data import fetch_data
from models import RawTokenTransfer, RawTransaction

T = TypeVar('T', bound=BaseModel)


class ExplorerAdapter(ABC):
    def __init__(self, chain: str):
        self.chain = chain

    def _get_explorer_api_url(self, params: Dict[str, any]) -> str:
        """Constructs the full API URL for a given chain and parameters."""
        base_url = EXPLORER_URLS.get(self.chain)
        if not base_url:
            raise ValueError(f"Unsupported chain: {self.chain}")

        # Create a copy to avoid mutating the original params dictionary
        query_params = params.copy()

        api_key_env_var = EXPLORER_API_KEYS.get(self.chain)
        if api_key_env_var:
            api_key = os.getenv(api_key_env_var)
            if api_key:
                query_params['apikey'] = api_key

        encoded_params = urlencode(query_params)
        return f"{base_url}?{encoded_params}"

    def _fetch_all_pages(self, params: Dict[str, any], model: Type[T]) -> List[T]:
        """Fetches all pages of data from the API."""
        all_data: List[T] = []
        page = 1
        offset = 10000  # Default max per page for Etherscan-like APIs

        while True:
            # Create a copy of params for this specific page request
            page_params = params.copy()
            page_params['page'] = page
            page_params['offset'] = offset

            url = self._get_explorer_api_url(page_params)
            data = fetch_data(url, model)
            all_data.extend(data)

            # If we fetched fewer items than the offset, it means we've reached the end
            if len(data) < offset:
                break
            page += 1

        return all_data

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
        return self._fetch_all_pages(params, RawTransaction)

    def get_token_transfers(self, wallet_address: str) -> List[RawTokenTransfer]:
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
        }
        return self._fetch_all_pages(params, RawTokenTransfer)

    def get_internal_transactions(self, wallet_address: str) -> List[RawTransaction]:
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
        }
        return self._fetch_all_pages(params, RawTransaction)


class BasescanAdapter(EtherscanAdapter):
    pass


class ArbiscanAdapter(EtherscanAdapter):
    pass


class MintchainAdapter(EtherscanAdapter):
    pass
