import sqlite3
import json
import hashlib
from typing import Optional, Any

class CacheManager:
    def __init__(self, db_path: str = "cache/api_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS api_responses ("
                "key TEXT PRIMARY KEY, "
                "response TEXT, "
                "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
                ")"
            )

    def _get_key(self, endpoint: str) -> str:
        return hashlib.sha256(endpoint.encode()).hexdigest()

    def get_response(self, endpoint: str) -> Optional[Any]:
        key = self._get_key(endpoint)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT response FROM api_responses WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
        except Exception:
            pass
        return None

    def set_response(self, endpoint: str, response: Any):
        key = self._get_key(endpoint)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO api_responses (key, response) VALUES (?, ?)",
                    (key, json.dumps(response))
                )
        except Exception:
            pass

import os
# Singleton instance
cache_manager = CacheManager()
