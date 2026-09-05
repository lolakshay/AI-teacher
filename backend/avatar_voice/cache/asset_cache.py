"""
Deterministic File and Metadata Asset Cache (Agent 5 - Avatar + Voice Engine)
Prevents redundant generation of audio and synthetic avatar videos.
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from backend.app.core.config import settings
from backend.avatar_voice.models.assets import AudioAsset, AvatarAsset
from backend.avatar_voice.models.voice import VoiceConfig
from backend.avatar_voice.models.avatar import AvatarConfig

class AssetCache:
    """
    Manages deterministic hashed storage and retrieval of TTS audio and avatar video assets.
    """

    def __init__(
        self,
        voice_cache_dir: Optional[Path] = None,
        avatar_cache_dir: Optional[Path] = None
    ):
        self.voice_dir = Path(voice_cache_dir or settings.VOICE_CACHE_DIR)
        self.avatar_dir = Path(avatar_cache_dir or settings.AVATAR_CACHE_DIR)
        self.voice_dir.mkdir(parents=True, exist_ok=True)
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory index for rapid lookups
        self._voice_memory: Dict[str, AudioAsset] = {}
        self._avatar_memory: Dict[str, AvatarAsset] = {}

    @staticmethod
    def compute_voice_key(
        normalized_text: str,
        language: str,
        voice_id: Optional[str],
        speaking_rate: float,
        pitch: float,
        provider: str
    ) -> str:
        """
        hash(normalized_text + language + voice_id + speaking_rate + pitch + provider)
        """
        raw = f"{normalized_text}|{language}|{voice_id or 'default'}|{speaking_rate:.2f}|{pitch:.2f}|{provider}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_avatar_key(
        audio_asset_id: str,
        avatar_id: str,
        expression: str,
        language: str,
        provider: str
    ) -> str:
        """
        hash(audio_asset_id + avatar_id + expression + language + provider)
        """
        raw = f"{audio_asset_id}|{avatar_id}|{expression}|{language}|{provider}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_voice(self, key: str) -> Optional[AudioAsset]:
        """Retrieves cached AudioAsset if present in memory or disk."""
        if key in self._voice_memory:
            return self._voice_memory[key]

        meta_file = self.voice_dir / f"{key}.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                asset = AudioAsset(**data)
                # Verify that local file actually exists
                if asset.local_path and Path(asset.local_path).exists():
                    self._voice_memory[key] = asset
                    return asset
            except Exception:
                pass
        return None

    def put_voice(self, key: str, asset: AudioAsset) -> None:
        """Persists AudioAsset and metadata into cache."""
        self._voice_memory[key] = asset
        meta_file = self.voice_dir / f"{key}.json"
        try:
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(asset.model_dump_json(indent=2))
        except Exception:
            pass

    def get_avatar(self, key: str) -> Optional[AvatarAsset]:
        """Retrieves cached AvatarAsset if present in memory or disk."""
        if key in self._avatar_memory:
            return self._avatar_memory[key]

        meta_file = self.avatar_dir / f"{key}.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                asset = AvatarAsset(**data)
                if asset.local_path and Path(asset.local_path).exists():
                    self._avatar_memory[key] = asset
                    return asset
            except Exception:
                pass
        return None

    def put_avatar(self, key: str, asset: AvatarAsset) -> None:
        """Persists AvatarAsset and metadata into cache."""
        self._avatar_memory[key] = asset
        meta_file = self.avatar_dir / f"{key}.json"
        try:
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(asset.model_dump_json(indent=2))
        except Exception:
            pass

    def clear(self, clear_disk: bool = True) -> None:
        """Clears in-memory cache and optionally disk files for isolated testing."""
        self._voice_memory.clear()
        self._avatar_memory.clear()
        if clear_disk:
            for p in self.voice_dir.glob("*.*"):
                try:
                    p.unlink()
                except Exception:
                    pass
            for p in self.avatar_dir.glob("*.*"):
                try:
                    p.unlink()
                except Exception:
                    pass

asset_cache = AssetCache()
