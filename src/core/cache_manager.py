"""Parquet/JSON cache manager with TTL-based expiration."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.core.config import PROJECT_ROOT
from src.core.logger import get_logger

logger = get_logger(__name__)

CACHE_DIR = PROJECT_ROOT / "data" / "cache"
METADATA_PATH = CACHE_DIR / "_metadata.json"


class CacheManager:
    """File-based cache using Parquet for DataFrames and JSON for metadata.

    Cache keys map to Parquet files under ``data/cache/<category>/<key>.parquet``.
    Expiration is tracked in ``data/cache/_metadata.json``.
    """

    def __init__(self, ttl_hours: int = 4, no_cache: bool = False) -> None:
        self._ttl = timedelta(hours=ttl_hours)
        self._no_cache = no_cache
        self._metadata: dict[str, Any] = {}
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._load_metadata()

    def get(self, category: str, key: str) -> pd.DataFrame | None:
        """Retrieve a cached DataFrame if it exists and is not expired.

        Args:
            category: Cache subdirectory (e.g., "indices", "stocks").
            key: Unique key within the category.

        Returns:
            DataFrame if cache hit, None otherwise.
        """
        if self._no_cache:
            return None

        cache_key = f"{category}/{key}"
        parquet_path = CACHE_DIR / category / f"{key}.parquet"

        if not parquet_path.exists():
            return None

        meta = self._metadata.get(cache_key)
        if meta is None:
            return None

        expires_at = datetime.fromisoformat(meta["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            logger.debug("cache_expired", key=cache_key)
            return None

        try:
            df = pd.read_parquet(parquet_path)
            logger.debug("cache_hit", key=cache_key, rows=len(df))
            return df
        except Exception as e:
            logger.warning("cache_read_failed", key=cache_key, error=str(e))
            return None

    def put(self, category: str, key: str, df: pd.DataFrame) -> None:
        """Store a DataFrame in the cache.

        Args:
            category: Cache subdirectory.
            key: Unique key within the category.
            df: DataFrame to cache.
        """
        cache_key = f"{category}/{key}"
        category_dir = CACHE_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        parquet_path = category_dir / f"{key}.parquet"

        try:
            df.to_parquet(parquet_path)
            now = datetime.now(timezone.utc)
            self._metadata[cache_key] = {
                "created_at": now.isoformat(),
                "expires_at": (now + self._ttl).isoformat(),
            }
            self._save_metadata()
            logger.debug("cache_stored", key=cache_key, rows=len(df))
        except Exception as e:
            logger.warning("cache_write_failed", key=cache_key, error=str(e))

    def invalidate(self, category: str, key: str) -> None:
        """Remove a specific cache entry.

        Args:
            category: Cache subdirectory.
            key: Unique key within the category.
        """
        cache_key = f"{category}/{key}"
        parquet_path = CACHE_DIR / category / f"{key}.parquet"
        if parquet_path.exists():
            parquet_path.unlink()
        self._metadata.pop(cache_key, None)
        self._save_metadata()

    def _load_metadata(self) -> None:
        """Load cache metadata from JSON file."""
        if METADATA_PATH.exists():
            try:
                with open(METADATA_PATH, encoding="utf-8") as f:
                    self._metadata = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._metadata = {}
        else:
            self._metadata = {}

    def _save_metadata(self) -> None:
        """Persist cache metadata to JSON file."""
        try:
            with open(METADATA_PATH, "w", encoding="utf-8") as f:
                json.dump(self._metadata, f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.warning("metadata_save_failed", error=str(e))
