"""
Translation and Adaptation Caching Service.
Computes multi-attribute cryptographic cache keys and maintains in-memory TTL caching.
Conforms strictly to Section 43.
"""

import hashlib
import time
import threading
from typing import Dict, Any, Optional, Tuple, List

class CacheEntry:
    def __init__(self, value: Any, ttl_seconds: int = 3600):
        self.value = value
        self.expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else float("inf")

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class TranslationCacheService:
    def __init__(self, default_ttl: int = 3600, max_size: int = 2000):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    @staticmethod
    def generate_cache_key(
        source_text: str,
        source_language: str,
        target_language: str,
        terminology: Optional[List[str]] = None,
        teaching_style: str = "analogy_driven",
        learner_level: str = "beginner"
    ) -> str:
        """
        Builds a stable SHA-256 hash key based on all pedagogical context attributes.
        Crucial: The same sentence produces different keys for different styles and learner levels!
        """
        terms_str = ",".join(sorted([t.strip().lower() for t in (terminology or [])]))
        raw_key = (
            f"src_text:{source_text.strip()}|"
            f"src_lang:{source_language.strip().lower()}|"
            f"tgt_lang:{target_language.strip().lower()}|"
            f"terms:{terms_str}|"
            f"style:{teaching_style.strip().lower()}|"
            f"level:{learner_level.strip().lower()}"
        )
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self.misses += 1
                return None
            if entry.is_expired():
                del self._cache[key]
                self.misses += 1
                return None
            self.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            if len(self._cache) >= self.max_size:
                # Evict expired entries first
                expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
                for k in expired_keys:
                    del self._cache[k]
                # If still at max size, evict oldest 10%
                if len(self._cache) >= self.max_size:
                    keys_to_remove = list(self._cache.keys())[: max(1, self.max_size // 10)]
                    for k in keys_to_remove:
                        del self._cache[k]

            ttl_val = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, ttl_val)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(hit_rate, 3)
            }

cache_service = TranslationCacheService()
