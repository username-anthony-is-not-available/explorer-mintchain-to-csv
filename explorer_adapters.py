import os
import requests
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from urllib.parse import urlencode

from pydantic import BaseModel

from config import EXPLORER_API_KEYS, EXPLORER_URLS, TIMEOUT
from fetch_blockchain_data import fetch_data
from models import RawTokenTransfer, RawTransaction

T = TypeVar("T", bound=BaseModel)


class ExplorerAdapter(ABC):
    def __init__(self, chain: str):
        self.chain = chain

    def _get_explorer_api_url(self, params: Dict[str, Any]) -> str:
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
                query_params["apikey"] = api_key

        encoded_params = urlencode(query_params)
        return f"{base_url}?{encoded_params}"

    def _fetch_all_pages(self, params: Dict[str, Any], model: Type[T]) -> List[T]:
        """Fetches all pages of data from the API."""
        all_data: List[T] = []
        page = 1
        offset = 10000  # Default max per page for Etherscan-like APIs

        while True:
            # Create a copy of params for this specific page request
            page_params = params.copy()
            page_params["page"] = page
            page_params["offset"] = offset

            url = self._get_explorer_api_url(page_params)
            data = fetch_data(url, model)
            all_data.extend(data)

            # If we fetched fewer items than the offset, it means we've reached the end
            if len(data) < offset:
                break
            page += 1

        return all_data

    @abstractmethod
    def get_transactions(
        self,
        wallet_address: str,
        startblock: int = 0,
        endblock: int = 99999999
    ) -> List[RawTransaction]:
        pass

    @abstractmethod
    def get_token_transfers(
        self,
        wallet_address: str,
        startblock: int = 0,
        endblock: int = 99999999
    ) -> List[RawTokenTransfer]:
        pass

    @abstractmethod
    def get_internal_transactions(
        self,
        wallet_address: str,
        startblock: int = 0,
        endblock: int = 99999999
    ) -> List[RawTransaction]:
        pass

    @abstractmethod
    def get_block_number_by_timestamp(self, timestamp: int, closest: str = "before") -> int:
        pass


class EtherscanAdapter(ExplorerAdapter):
    def get_transactions(
        self,
        wallet_address: str,
        startblock: int = 0,
        endblock: int = 99999999
    ) -> List[RawTransaction]:
        params = {
            "module": "account",
            "action": "txlist",
            "address": wallet_address,
            "startblock": startblock,
            "endblock": endblock,
            "sort": "asc",
        }
        return self._fetch_all_pages(params, RawTransaction)

    def get_token_transfers(
        self,
        wallet_address: str,
        startblock: int = 0,
        endblock: int = 99999999
    ) -> List[RawTokenTransfer]:
        params = {
            "module": "account",
            "action": "tokentx",
            "address": wallet_address,
            "startblock": startblock,
            "endblock": endblock,
            "sort": "asc",
        }
        return self._fetch_all_pages(params, RawTokenTransfer)

    def get_internal_transactions(
        self,
        wallet_address: str,
        startblock: int = 0,
        endblock: int = 99999999
    ) -> List[RawTransaction]:
        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": wallet_address,
            "startblock": startblock,
            "endblock": endblock,
            "sort": "asc",
        }
        return self._fetch_all_pages(params, RawTransaction)

    def get_block_number_by_timestamp(self, timestamp: int, closest: str = "before") -> int:
        params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": closest,
        }
        url = self._get_explorer_api_url(params)
        try:
            # Using a raw fetch here as we just want the block number string
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "1":
                return int(data.get("result"))
        except Exception:
            # Silently fall back to default block numbers on any error to ensure reliability
            pass
        return 0 if closest == "before" else 99999999


class BasescanAdapter(EtherscanAdapter):
    pass


class ArbiscanAdapter(EtherscanAdapter):
    pass


class MintchainAdapter(EtherscanAdapter):
    pass


class OptimismAdapter(EtherscanAdapter):
    pass


class PolygonAdapter(EtherscanAdapter):
    pass
