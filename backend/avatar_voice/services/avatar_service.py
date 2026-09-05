"""
Avatar Service Orchestration Layer (Agent 5 - Avatar + Voice Engine)
Manages synthetic teacher avatar generation, pedagogical expression mapping, lip-sync validation, and caching.
"""

from typing import Dict, Any, Optional, List
from backend.app.core.config import settings
from backend.avatar_voice.models.assets import AvatarAsset, AudioAsset
from backend.avatar_voice.models.avatar import AvatarConfig, AvatarError, AvatarExpressionType, TeacherGestureType
from backend.avatar_voice.providers.base_avatar import AvatarProvider
from backend.avatar_voice.providers.mock_avatar import MockAvatarProvider
from backend.avatar_voice.providers.external_avatar import ExternalAvatarProvider
from backend.avatar_voice.cache.asset_cache import asset_cache

class AvatarService:
    """
    Core service managing avatar video synthesis, emotional expression states, and caching.
    """

    # Pedagogical mapping from teaching intent / step_type to teacher facial expression
    EXPRESSION_MAP = {
        "introduction": "friendly",
        "explanation": "focused",
        "demonstration": "engaged",
        "example": "engaged",
        "visual": "focused",
        "question": "curious",
        "assessment": "curious",
        "re_explanation": "patient",
        "reteaching": "patient",
        "summary": "confident",
        # Direct emotion keywords
        "explaining": "focused",
        "encouraging": "encouraging",
        "thoughtful": "thoughtful",
        "celebrating": "celebrating",
        "attentive": "focused",
        "supportive": "supportive",
        "patient": "patient",
        "neutral": "friendly"
    }

    # Pedagogical gesture mapping
    GESTURE_MAP = {
        "re_explanation": "explain",
        "reteaching": "explain",
        "patient": "explain",
        "explaining": "explain",
        "explanation": "explain",
        "demonstration": "point_visual",
        "visual": "point_visual",
        "question": "thinking",
        "curious": "thinking",
        "introduction": "welcome",
        "summary": "emphasize"
    }

    def __init__(self):
        self._providers: Dict[str, AvatarProvider] = {
            "mock": MockAvatarProvider(),
            "did": ExternalAvatarProvider("did"),
            "heygen": ExternalAvatarProvider("heygen")
        }

    def register_provider(self, name: str, provider: AvatarProvider) -> None:
        """Dynamically registers or overrides an avatar provider."""
        self._providers[name.lower()] = provider

    def get_provider(self, name: Optional[str] = None) -> AvatarProvider:
        """Resolves active provider based on request, config, or fallback to mock."""
        target = (name or getattr(settings, "AVATAR_PROVIDER", "mock")).lower()
        if target in self._providers:
            return self._providers[target]
        return self._providers["mock"]

    def map_pedagogy_to_expression(self, intent_or_emotion: Optional[str]) -> AvatarExpressionType:
        """Translates pedagogical context (step type or avatar_emotion) into teacher facial expression."""
        if not intent_or_emotion:
            return "friendly"
        return self.EXPRESSION_MAP.get(intent_or_emotion.lower(), "friendly")

    def map_pedagogy_to_gesture(self, intent_or_step_type: Optional[str]) -> Optional[TeacherGestureType]:
        """Translates teaching action into natural teacher hand/body gesture."""
        if not intent_or_step_type:
            return None
        return self.GESTURE_MAP.get(intent_or_step_type.lower(), None)

    def generate_avatar(
        self,
        spoken_text: str,
        audio_asset: AudioAsset,
        language: str = "en",
        avatar_config: Optional[AvatarConfig] = None,
        pedagogical_intent: Optional[str] = None,
        duration: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generates avatar video:
        1. Resolves expression & gesture from pedagogical intent if not explicitly set.
        2. Computes stable SHA-256 cache key.
        3. Checks asset cache.
        4. Synthesizes via provider if cache miss.
        5. Caches and returns result.
        """
        config = avatar_config or AvatarConfig()
        
        # Apply pedagogical mapping if config has default expression
        if pedagogical_intent:
            resolved_expr = self.map_pedagogy_to_expression(pedagogical_intent)
            resolved_gesture = self.map_pedagogy_to_gesture(pedagogical_intent)
            config.expression = resolved_expr
            if not config.gesture and resolved_gesture:
                config.gesture = resolved_gesture

        provider = self.get_provider(config.provider)

        # Check Cache
        cache_key = asset_cache.compute_avatar_key(
            audio_asset_id=audio_asset.asset_id,
            avatar_id=config.avatar_id,
            expression=config.expression,
            language=language,
            provider=provider.provider_name
        )

        cached_asset = asset_cache.get_avatar(cache_key)
        if cached_asset:
            return {
                "avatar_asset": cached_asset,
                "expression": config.expression,
                "gesture": config.gesture,
                "cache_hit": True
            }

        # Generate Avatar Video
        try:
            avatar_asset = provider.generate_avatar_scene(
                spoken_text=spoken_text,
                audio_asset=audio_asset,
                language=language,
                avatar_config=config,
                expression=config.expression,
                duration=duration or audio_asset.duration_seconds
            )
        except AvatarError:
            raise
        except Exception as e:
            raise AvatarError(f"Unexpected avatar generation failure: {str(e)}", code="AVATAR_GENERATION_FAILED", retryable=True)

        # Store in Cache
        asset_cache.put_avatar(cache_key, avatar_asset)

        return {
            "avatar_asset": avatar_asset,
            "expression": config.expression,
            "gesture": config.gesture,
            "cache_hit": False
        }

    def get_supported_avatars(self) -> List[Dict[str, Any]]:
        provider = self.get_provider()
        return provider.get_supported_avatars()

avatar_service = AvatarService()
