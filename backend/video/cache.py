"""
Asset Cache Subsystem (Agent 4)
Provides deterministic SHA-256 caching for visual frames, audio metadata,
and rendered scenes to avoid regenerating identical assets.
Conforms to Sections 46 and 51 of Agent 4 specification.
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Any, Dict


class AssetCache:
    """
    Disk and memory cache for educational visual and video assets.
    Keys are computed using cryptographic SHA-256 hashes of immutable inputs.
    """
    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            from backend.app.core.config import settings
            self.cache_dir = settings.UPLOAD_DIR / "video_assets" / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}

    @staticmethod
    def generate_cache_key(
        spoken_text: str,
        language: str,
        visual_spec: Dict[str, Any],
        avatar_expression: str = "explaining"
    ) -> str:
        """
        Generates stable SHA-256 hash from composite scene inputs.
        """
        raw_spec = json.dumps(visual_spec, sort_keys=True)
        composite = f"{spoken_text.strip()}|{language.strip().lower()}|{avatar_expression.strip().lower()}|{raw_spec}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    def get_cached_asset(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached metadata if present."""
        if key in self._memory_cache:
            return self._memory_cache[key]

        manifest_path = self.cache_dir / f"{key}.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memory_cache[key] = data
                    return data
            except Exception:
                return None
        return None

    def store_cached_asset(self, key: str, data: Dict[str, Any]):
        """Persists asset cache metadata."""
        self._memory_cache[key] = data
        manifest_path = self.cache_dir / f"{key}.json"
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


asset_cache = AssetCache()
