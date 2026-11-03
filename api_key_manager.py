import logging
import os
import threading
from typing import Dict, List, Optional, Set


class APIKeyManager:
    """
    Manages API keys for services/chains with support for:
    - Multiple keys (e.g. comma-separated environment variables or list)
    - Periodic / round-robin rotation
    - Key invalidation and retirement
    - Thread-safe key access
    """

    def __init__(self, key_env_mapping: Optional[Dict[str, str]] = None) -> None:
        self._lock = threading.Lock()
        self._key_env_mapping: Dict[str, str] = key_env_mapping or {}
        # Stores keys per service/chain: chain -> list of keys
        self._keys: Dict[str, List[str]] = {}
        # Stores active index for round-robin rotation: chain -> int
        self._indices: Dict[str, int] = {}
        # Stores invalidated keys: chain -> set of invalid keys
        self._invalidated_keys: Dict[str, Set[str]] = {}

    def register_env_mapping(self, service: str, env_var: str) -> None:
        """Register the environment variable name for a given service/chain."""
        with self._lock:
            self._key_env_mapping[service.lower()] = env_var

    def set_keys(self, service: str, keys: List[str]) -> None:
        """Explicitly set the available keys for a service/chain."""
        service_clean = service.lower()
        cleaned_keys = [k.strip() for k in keys if k and k.strip()]
        with self._lock:
            self._keys[service_clean] = cleaned_keys
            self._indices[service_clean] = 0
            if service_clean not in self._invalidated_keys:
                self._invalidated_keys[service_clean] = set()

    def _load_keys_from_env_unlocked(self, service_clean: str) -> List[str]:
        """Loads keys from environment variable dynamically if not explicitly set."""
        env_var = self._key_env_mapping.get(service_clean)
        if not env_var:
            return self._keys.get(service_clean, [])

        val = os.getenv(f"{env_var}S") or os.getenv(env_var)
        if not val:
            # If environment variable is absent/empty and not explicitly set via set_keys, return empty
            if service_clean not in self._keys:
                return []
            return self._keys[service_clean]

        parsed_keys = [k.strip() for k in val.split(",") if k.strip()]
        if service_clean not in self._keys:
            self._indices.setdefault(service_clean, 0)
            self._invalidated_keys.setdefault(service_clean, set())
            return parsed_keys
        return self._keys[service_clean]

    def get_key(self, service: str, rotate: bool = False) -> Optional[str]:
        """
        Retrieves the current active API key for the given service/chain.
        If rotate is True, advances to the next key before returning.
        """
        service_clean = service.lower()
        with self._lock:
            all_keys = self._load_keys_from_env_unlocked(service_clean)
            invalid_set = self._invalidated_keys.get(service_clean, set())
            active_keys = [k for k in all_keys if k not in invalid_set]

            if not active_keys:
                return None

            idx = self._indices.get(service_clean, 0)
            if rotate:
                idx = (idx + 1) % len(active_keys)
                self._indices[service_clean] = idx
            else:
                idx = idx % len(active_keys)

            return active_keys[idx]

    def rotate_key(self, service: str) -> Optional[str]:
        """
        Advances to the next active API key for the given service/chain and returns it.
        """
        return self.get_key(service, rotate=True)

    def invalidate_key(self, service: str, key: str, reason: str = "") -> None:
        """
        Invalidates a specific API key for the service/chain so it is promptly removed
        from rotation.
        """
        service_clean = service.lower()
        clean_key = key.strip()
        with self._lock:
            if service_clean not in self._invalidated_keys:
                self._invalidated_keys[service_clean] = set()
            self._invalidated_keys[service_clean].add(clean_key)
            logging.warning(
                f"API key for {service} was invalidated. Reason: {reason or 'Not specified'}"
            )
            # Adjust index if necessary
            all_keys = self._load_keys_from_env_unlocked(service_clean)
            invalid_set = self._invalidated_keys[service_clean]
            active_keys = [k for k in all_keys if k not in invalid_set]
            if active_keys:
                self._indices[service_clean] = self._indices.get(service_clean, 0) % len(active_keys)
            else:
                self._indices[service_clean] = 0

    def get_active_keys(self, service: str) -> List[str]:
        """Returns the list of currently active (non-invalidated) keys for the service."""
        service_clean = service.lower()
        with self._lock:
            all_keys = self._load_keys_from_env_unlocked(service_clean)
            invalid_set = self._invalidated_keys.get(service_clean, set())
            return [k for k in all_keys if k not in invalid_set]

    def get_invalidated_keys(self, service: str) -> Set[str]:
        """Returns the set of invalidated keys for the service."""
        service_clean = service.lower()
        with self._lock:
            return set(self._invalidated_keys.get(service_clean, set()))

    def reset(self) -> None:
        """Resets all keys, indices, and invalidation states."""
        with self._lock:
            self._keys.clear()
            self._indices.clear()
            self._invalidated_keys.clear()


# Default global instance initialized with explorer config mapping
from config import EXPLORER_API_KEYS  # noqa: E402

api_key_manager = APIKeyManager(key_env_mapping=EXPLORER_API_KEYS)
