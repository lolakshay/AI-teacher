"""
External Cloud Avatar Provider (Agent 5 - Avatar + Voice Engine)
Integrates with external synthetic avatar video APIs (D-ID, HeyGen) with async status checking and bounded retries.
"""

import time
import httpx
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

from backend.app.core.config import settings
from backend.avatar_voice.providers.base_avatar import AvatarProvider
from backend.avatar_voice.models.assets import AvatarAsset, AudioAsset
from backend.avatar_voice.models.avatar import AvatarConfig, AvatarError

class ExternalAvatarProvider(AvatarProvider):
    """
    Adapter for external AI avatar video APIs (D-ID / HeyGen).
    """

    def __init__(self, service_type: str = "did", api_key: str = None):
        self.service_type = service_type.lower()
        self.api_key = api_key or settings.AVATAR_API_KEY

    @property
    def provider_name(self) -> str:
        return f"external_{self.service_type}"

    def generate_avatar_scene(
        self,
        spoken_text: str,
        audio_asset: AudioAsset,
        language: str = "en",
        avatar_config: Optional[AvatarConfig] = None,
        expression: str = "friendly",
        duration: Optional[float] = None
    ) -> AvatarAsset:
        if not self.api_key:
            raise AvatarError(
                f"API Key for {self.service_type} avatar provider is not configured.",
                code="AVATAR_AUTH_FAILED",
                retryable=False
            )

        config = avatar_config or AvatarConfig(expression=expression)
        max_retries = getattr(settings, "MAX_PROVIDER_RETRIES", 2)
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                if self.service_type == "did":
                    # D-ID Talks API
                    headers = {
                        "Authorization": f"Basic {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "script": {
                            "type": "text",
                            "input": spoken_text,
                            "provider": {
                                "type": "microsoft",
                                "voice_id": "en-US-JennyNeural"
                            }
                        },
                        "config": {
                            "fluent": True,
                            "pad_audio": 0.0
                        }
                    }
                    with httpx.Client(timeout=20.0) as client:
                        resp = client.post("https://api.d-id.com/talks", json=payload, headers=headers)
                        if resp.status_code == 401:
                            raise AvatarError("Unauthorized: Invalid D-ID API key", code="AVATAR_AUTH_FAILED", retryable=False)
                        if resp.status_code == 400:
                            raise AvatarError(f"Bad Request: {resp.text}", code="AVATAR_INVALID_REQUEST", retryable=False)
                        resp.raise_for_status()
                        data = resp.json()
                        talk_id = data.get("id")

                        # Poll for video completion (up to 30s)
                        video_url = None
                        for _ in range(6):
                            time.sleep(5.0)
                            status_resp = client.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
                            if status_resp.status_code == 200:
                                status_data = status_resp.json()
                                if status_data.get("status") == "done":
                                    video_url = status_data.get("result_url")
                                    break
                                elif status_data.get("status") == "error":
                                    raise AvatarError(f"D-ID generation failed: {status_data}", code="AVATAR_GENERATION_FAILED")

                        asset_id = f"avatar_did_{uuid.uuid4().hex[:8]}"
                        return AvatarAsset(
                            asset_id=asset_id,
                            video_url=video_url or f"https://api.d-id.com/talks/{talk_id}",
                            duration_seconds=audio_asset.duration_seconds,
                            language=language,
                            avatar_id=config.avatar_id,
                            provider=self.provider_name,
                            lip_synced=True,
                            metadata={"talk_id": talk_id, "provider": self.service_type}
                        )

                elif self.service_type == "heygen":
                    # HeyGen API
                    headers = {
                        "X-Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "video_inputs": [{
                            "character": {"type": "avatar", "avatar_id": config.avatar_id},
                            "voice": {"type": "text", "input_text": spoken_text}
                        }]
                    }
                    with httpx.Client(timeout=20.0) as client:
                        resp = client.post("https://api.heygen.com/v2/video/generate", json=payload, headers=headers)
                        if resp.status_code == 401:
                            raise AvatarError("Unauthorized: Invalid HeyGen API key", code="AVATAR_AUTH_FAILED", retryable=False)
                        resp.raise_for_status()
                        data = resp.json().get("data", {})
                        video_id = data.get("video_id")

                        asset_id = f"avatar_heygen_{uuid.uuid4().hex[:8]}"
                        return AvatarAsset(
                            asset_id=asset_id,
                            video_url=f"https://api.heygen.com/v2/video/{video_id}",
                            duration_seconds=audio_asset.duration_seconds,
                            language=language,
                            avatar_id=config.avatar_id,
                            provider=self.provider_name,
                            lip_synced=True,
                            metadata={"video_id": video_id}
                        )
                else:
                    raise AvatarError(f"Unsupported avatar provider: {self.service_type}", code="AVATAR_INVALID_REQUEST")

            except AvatarError:
                raise
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(0.5 * (2 ** attempt))
                else:
                    break

        raise AvatarError(
            f"External avatar provider failed after {max_retries} retries: {str(last_exception)}",
            code="AVATAR_PROVIDER_UNAVAILABLE",
            retryable=True
        )

    def get_supported_avatars(self) -> List[Dict[str, Any]]:
        return [
            {"avatar_id": "default_cloud_teacher", "name": "Cloud Teacher", "styles": ["professional"]}
        ]
