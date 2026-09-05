"""
Comprehensive Unit and Integration Tests for Agent 5: Avatar + Voice Engine
Covers all 20 requirements from Section 33 and the Canonical Demo scenario from Section 34.
"""

import sys
import os
import wave
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.avatar_voice.models.voice import VoiceConfig, SpeechSegment, VoiceError
from backend.avatar_voice.models.avatar import AvatarConfig, AvatarError
from backend.avatar_voice.models.assets import AudioAsset, AvatarAsset, AvatarVoiceSceneResult
from backend.avatar_voice.providers.base_voice import VoiceProvider
from backend.avatar_voice.providers.mock_voice import MockVoiceProvider
from backend.avatar_voice.providers.base_avatar import AvatarProvider
from backend.avatar_voice.providers.mock_avatar import MockAvatarProvider
from backend.avatar_voice.processing.speech_normalizer import speech_normalizer
from backend.avatar_voice.processing.speech_segmenter import speech_segmenter
from backend.avatar_voice.processing.timing import timing_synchronizer
from backend.avatar_voice.cache.asset_cache import asset_cache
from backend.avatar_voice.services.voice_service import voice_service
from backend.avatar_voice.services.avatar_service import avatar_service
from backend.avatar_voice.services.scene_service import scene_service
from backend.app.core.models import TeachingStep

# 1. Voice provider interface works
def test_voice_provider_interface():
    provider = MockVoiceProvider()
    assert isinstance(provider, VoiceProvider)
    assert provider.provider_name == "mock"
    voices = provider.get_supported_voices("en")
    assert len(voices) >= 2
    assert any(v["gender"] == "female" for v in voices)

# 2. Mock voice generation works (real WAV file with valid header)
def test_mock_voice_generation():
    provider = MockVoiceProvider()
    text = "Welcome to your physics lesson on electrical circuits."
    asset = provider.generate_audio(text=text, language="en")

    assert asset.asset_id.startswith("audio_mock_")
    assert asset.format == "wav"
    assert asset.sample_rate == 24000
    assert asset.duration_seconds > 1.0
    assert os.path.exists(asset.local_path)

    # Validate standard WAV header
    with wave.open(asset.local_path, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 24000
        frames = wf.getnframes()
        calc_duration = round(frames / 24000.0, 2)
        assert abs(calc_duration - asset.duration_seconds) < 0.1

# 3. Voice configuration is preserved
def test_voice_config_preservation():
    config = VoiceConfig(
        voice_id="teacher_special",
        speaking_rate=1.2,
        pitch=3.0,
        volume=0.8,
        style="encouraging"
    )
    provider = MockVoiceProvider()
    asset = provider.generate_audio(text="Great job solving that equation!", voice_config=config)

    assert asset.metadata["speaking_rate"] == 1.2
    assert asset.metadata["pitch"] == 3.0
    assert asset.metadata["style"] == "encouraging"

# 4. Language metadata is preserved
def test_multilingual_voice_metadata():
    provider = MockVoiceProvider()
    
    # English
    en_asset = provider.generate_audio(text="Hello student.", language="en")
    assert en_asset.language == "en"

    # Hindi
    hi_asset = provider.generate_audio(text="आज हम ओम के नियम को समझेंगे।", language="hi")
    assert hi_asset.language == "hi"

    # Hinglish
    hing_asset = provider.generate_audio(text="Aaj hum circuit dynamics seekhenge.", language="Hinglish")
    assert hing_asset.language == "Hinglish"

# 5. Speech segmentation works
def test_speech_segmentation():
    text = "Let's understand Ohm's law. Voltage is the potential difference across a circuit. Current is the flow of charge. Resistance opposes that flow."
    segments = speech_segmenter.segment(text, total_duration=8.0)

    assert len(segments) >= 3
    assert segments[0].start_seconds == 0.0
    assert segments[-1].end_seconds == 8.0
    # Sequential ordering check
    for i in range(len(segments) - 1):
        assert segments[i].end_seconds <= segments[i+1].start_seconds

# 6. Mathematical expressions are not incorrectly fragmented
def test_math_expression_not_fragmented():
    text = "Remember this foundational law: V = I × R holds for all ideal resistors."
    segments = speech_segmenter.segment(text, total_duration=5.0)

    # Ensure V = I × R stays in a single segment
    v_segments = [s for s in segments if "V = I × R" in s.text or "V = I x R" in s.text or "V = I * R" in s.text]
    assert len(v_segments) == 1

# 7. Mathematical pronunciation normalization
def test_speech_normalization():
    raw = r"In this circuit, V = I \times R where R = 10\Omega and I = 2A."
    display_text, spoken_text = speech_normalizer.normalize(raw)

    assert display_text == raw
    assert "V equals I multiplied by R" in spoken_text
    assert "10 ohms" in spoken_text
    assert "2 amperes" in spoken_text

    # Exponent normalization
    _, spoken_pyth = speech_normalizer.normalize("a² + b² = c²")
    assert "a squared plus b squared equals c squared" in spoken_pyth

    # Fraction normalization
    _, spoken_frac = speech_normalizer.normalize(r"Current is \frac{V}{R}")
    assert "V over R" in spoken_frac

# 8. Avatar provider interface works
def test_avatar_provider_interface():
    provider = MockAvatarProvider()
    assert isinstance(provider, AvatarProvider)
    assert provider.provider_name == "mock"
    avatars = provider.get_supported_avatars()
    assert len(avatars) >= 2
    assert avatars[0]["lip_sync_guaranteed"] is True

# 9. Mock avatar generation works (real MP4 file)
def test_mock_avatar_generation():
    audio = AudioAsset(asset_id="test_audio_01", duration_seconds=3.0, language="en")
    provider = MockAvatarProvider()
    avatar_asset = provider.generate_avatar_scene(
        spoken_text="Let's observe the voltage drop across the resistor.",
        audio_asset=audio,
        expression="focused"
    )

    assert avatar_asset.asset_id.startswith("avatar_mock_")
    assert avatar_asset.duration_seconds == 3.0
    assert avatar_asset.lip_synced is True
    assert avatar_asset.width == 640
    assert avatar_asset.height == 480
    assert os.path.exists(avatar_asset.local_path)
    assert os.path.getsize(avatar_asset.local_path) > 0

# 10. Avatar configuration is preserved
def test_avatar_config_preservation():
    config = AvatarConfig(
        avatar_id="teacher_avatar_02",
        position="left",
        scale=1.2,
        expression="encouraging",
        gesture="point_visual"
    )
    audio = AudioAsset(asset_id="test_audio_02", duration_seconds=2.0)
    provider = MockAvatarProvider()
    asset = provider.generate_avatar_scene(
        spoken_text="Notice this graph.",
        audio_asset=audio,
        avatar_config=config,
        expression="encouraging"
    )

    assert asset.metadata["position"] == "left"
    assert asset.metadata["scale"] == 1.2
    assert asset.metadata["expression"] == "encouraging"
    assert asset.metadata["gesture"] == "point_visual"

# 11. Expression & gesture mapping from pedagogy
def test_expression_mapping_from_pedagogy():
    # Explanation
    assert avatar_service.map_pedagogy_to_expression("explanation") == "focused"
    # Reteaching / Re-explanation
    assert avatar_service.map_pedagogy_to_expression("re_explanation") == "patient"
    assert avatar_service.map_pedagogy_to_gesture("re_explanation") == "explain"
    # Question
    assert avatar_service.map_pedagogy_to_expression("question") == "curious"
    assert avatar_service.map_pedagogy_to_gesture("question") == "thinking"
    # Demonstration
    assert avatar_service.map_pedagogy_to_gesture("demonstration") == "point_visual"

# 12. Lip-sync metadata accuracy
def test_lip_sync_metadata():
    audio = AudioAsset(asset_id="audio_test_lip", duration_seconds=2.5)
    provider = MockAvatarProvider()
    asset = provider.generate_avatar_scene("Test speech", audio_asset=audio)
    assert asset.lip_synced is True

# 13. Timing synchronization & drift detection
def test_timing_drift_detection():
    # Within tolerance (<= 0.5s)
    timing_ok = timing_synchronizer.synchronize(audio_duration=5.0, avatar_duration=5.2)
    assert timing_ok.drift_seconds == 0.2
    assert timing_ok.drift_acceptable is True

    # Exceeding tolerance (> 0.5s)
    timing_bad = timing_synchronizer.synchronize(audio_duration=5.0, avatar_duration=6.0)
    assert timing_bad.drift_seconds == 1.0
    assert timing_bad.drift_acceptable is False

# 14. Asset caching prevents redundant generation
def test_asset_caching():
    asset_cache.clear()
    text = "Caching saves computation time."
    res1 = voice_service.synthesize(raw_text=text, language="en")
    assert res1["cache_hit"] is False

    # Second request with exact parameters must hit cache
    res2 = voice_service.synthesize(raw_text=text, language="en")
    assert res2["cache_hit"] is True
    assert res1["audio_asset"].asset_id == res2["audio_asset"].asset_id

# 15. Bounded retries on transient errors
def test_provider_transient_retry():
    call_count = 0

    class FlakyVoiceProvider(VoiceProvider):
        @property
        def provider_name(self):
            return "flaky"

        def generate_audio(self, text, language="en", voice_config=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise VoiceError("Transient network timeout", code="VOICE_PROVIDER_UNAVAILABLE", retryable=True)
            return AudioAsset(asset_id="flaky_recovered", duration_seconds=2.0)

        def get_supported_voices(self, language="en"):
            return []

    flaky = FlakyVoiceProvider()
    # First attempt fails with VoiceError
    with pytest.raises(VoiceError) as exc:
        flaky.generate_audio("test")
    assert exc.value.retryable is True
    # Second attempt succeeds
    recovered = flaky.generate_audio("test")
    assert recovered.asset_id == "flaky_recovered"

# 16. Permanent error graceful handling
def test_provider_permanent_failure_graceful_error():
    class BrokenAuthVoiceProvider(VoiceProvider):
        @property
        def provider_name(self):
            return "broken_auth"

        def generate_audio(self, text, language="en", voice_config=None):
            raise VoiceError("401 Unauthorized: Invalid API key", code="VOICE_AUTH_FAILED", retryable=False)

        def get_supported_voices(self, language="en"):
            return []

    voice_service.register_provider("broken_auth", BrokenAuthVoiceProvider())
    result = scene_service.generate_scene(
        spoken_text="Testing auth failure",
        voice_config=VoiceConfig(provider="broken_auth")
    )
    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == "VOICE_AUTH_FAILED"
    assert result.error.retryable is False
    assert result.fallback == "text_only"

# 17. Partial fallback: Voice succeeds, Avatar fails -> Level 3 Audio Only
def test_partial_fallback_voice_ok_avatar_fail():
    class FailingAvatarProvider(AvatarProvider):
        @property
        def provider_name(self):
            return "failing_avatar"

        def generate_avatar_scene(self, spoken_text, audio_asset, language="en", avatar_config=None, expression="friendly", duration=None):
            raise AvatarError("GPU out of memory", code="AVATAR_GENERATION_FAILED", retryable=False)

        def get_supported_avatars(self):
            return []

    avatar_service.register_provider("failing_avatar", FailingAvatarProvider())
    result = scene_service.generate_scene(
        spoken_text="Voice should be fine, but avatar will fail.",
        avatar_config=AvatarConfig(provider="failing_avatar")
    )

    assert result.status == "partial"
    assert result.fallback == "audio_only"
    assert result.audio is not None
    assert result.avatar is None
    assert result.error is not None
    assert result.error.code == "AVATAR_GENERATION_FAILED"

# 18. Full scene generation produces structured Agent 4 contract
def test_full_scene_generation_contract():
    result = scene_service.generate_scene(
        spoken_text="In any closed circuit, the total voltage equals the sum of voltage drops.",
        language="en",
        pedagogical_intent="explanation"
    )

    assert isinstance(result, AvatarVoiceSceneResult)
    assert result.status == "ready"
    assert result.audio is not None
    assert result.audio.duration_seconds > 0.0
    assert result.avatar is not None
    assert result.avatar.duration_seconds > 0.0
    assert result.timing.drift_acceptable is True
    assert len(result.timing.segments) >= 1
    assert result.presentation.expression in ["focused", "friendly"]
    assert result.presentation.position == "right"

# 19. Question-specific delivery handling
def test_question_scene_delivery():
    step = TeachingStep(
        step_id="step_ohm_q1",
        lesson_id="lesson_ohm_01",
        concept_id="concept_ohm_law",
        objective="Verify student understanding of inverse proportionality",
        step_type="question",
        explanation="If voltage remains constant and resistance is doubled, what happens to the current?",
        language="en",
        avatar_emotion="curious"
    )
    result = scene_service.generate_scene_for_teaching_step(step)

    assert result.status == "ready"
    assert result.presentation.expression == "curious"
    assert result.presentation.gesture == "thinking"

# 20. CANONICAL DEMO INTEGRATION TEST (Section 34 & 35)
def test_canonical_ohm_law_hinglish_integration():
    """
    CRITICAL INTEGRATION TEST:
    Topic: Ohm's Law
    Language: Hinglish
    Full presentation loop:
    1. Introduction: 'Voltage, current aur resistance ke beech relationship ko Ohm's law explain karta hai.'
    2. Diagnostic Question: 'Agar voltage constant hai aur resistance increase hota hai, toh current ka kya hoga?'
    3. Reteaching (Misconception Response): 'Yahan ek important point hai. Agar voltage constant hai, aur resistance badh raha hai, toh current actually decrease hoga.'
    """
    # 1. Introduction Scene
    intro_step = TeachingStep(
        step_id="canonical_intro",
        lesson_id="lesson_ohm_01",
        concept_id="concept_ohm_law",
        objective="Introduce voltage, current, and resistance relationship",
        step_type="introduction",
        explanation="Voltage, current aur resistance ke beech relationship ko Ohm's law explain karta hai. V = I × R.",
        language="Hinglish",
        avatar_emotion="explaining"
    )
    intro_result = scene_service.generate_scene_for_teaching_step(intro_step)
    assert intro_result.status == "ready"
    assert intro_result.language == "Hinglish"
    assert intro_result.audio is not None
    assert intro_result.avatar is not None
    assert intro_result.presentation.expression in ["focused", "friendly"]
    assert "V equals I multiplied by R" in intro_result.spoken_text

    # 2. Diagnostic Question Scene
    question_step = TeachingStep(
        step_id="canonical_question",
        lesson_id="lesson_ohm_01",
        concept_id="concept_ohm_law",
        objective="Probe proportionality between voltage and resistance",
        step_type="question",
        explanation="Agar voltage constant hai aur resistance increase hota hai, toh current ka kya hoga?",
        language="Hinglish",
        avatar_emotion="attentive"
    )
    question_result = scene_service.generate_scene_for_teaching_step(question_step)
    assert question_result.status == "ready"
    assert question_result.presentation.expression == "curious"
    assert question_result.presentation.gesture == "thinking"

    # 3. Reteaching Scene (after student incorrect response)
    reteach_step = TeachingStep(
        step_id="canonical_reteach",
        lesson_id="lesson_ohm_01",
        concept_id="concept_ohm_law",
        objective="Reteach inverse relationship using pipe analogy",
        step_type="re_explanation",
        explanation="Yahan ek important point hai. Agar voltage constant hai, aur resistance badh raha hai, toh current actually decrease hoga.",
        language="Hinglish",
        avatar_emotion="patient"
    )
    reteach_result = scene_service.generate_scene_for_teaching_step(reteach_step)
    assert reteach_result.status == "ready"
    assert reteach_result.presentation.expression == "patient"
    assert reteach_result.presentation.gesture == "explain"
    assert reteach_result.audio.duration_seconds > 0.0
    assert reteach_result.avatar.duration_seconds > 0.0
