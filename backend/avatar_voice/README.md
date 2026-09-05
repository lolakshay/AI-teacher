# Avatar + Voice Subsystem (Agent 5)
**Human-Like Synthetic Presentation Engine for the AI Teacher**

---

## 1. Overview
The **Avatar + Voice Subsystem** is the presentation layer for the AI Teacher. It transforms educational lesson content and teacher scripts into:
1. **Natural Spoken Audio (TTS)** with STEM formula normalization ($V = I \times R$, $\Omega$, exponents).
2. **Synchronized Teacher Avatar Video** with emotional expressions (patient, curious, encouraging, focused) and teacher gestures.
3. **Precise Timing Metadata** to enable **Agent 4 (Video Engine)** to synchronize visual graphics, equations, and circuit simulations.
4. **Deterministic Asset Caching** to prevent expensive re-generation.
5. **Multi-Tiered Fallbacks** ensuring lessons never crash when external APIs encounter issues.

---

## 2. Integration with Agent 4 (AI Teaching Video Engine)

Agent 4 receives structured scene requests and calls Agent 5 to generate the spoken and visual presentation assets.

### Direct Python Adapter
```python
from backend.avatar_voice.services.scene_service import scene_service
from backend.app.core.models import TeachingStep

# Pass any TeachingStep directly from Agent 1 or Agent 4
step = TeachingStep(
    step_id="step_ohm_01",
    spoken_script="Voltage equals current multiplied by resistance. In other words, V equals I times R.",
    language="Hinglish",
    avatar_emotion="explaining"
)

scene_result = scene_service.generate_scene_for_teaching_step(step)
print(scene_result.status)                # "ready"
print(scene_result.audio.duration_seconds) # 4.8
print(scene_result.avatar.video_url)      # "/api/avatar-voice/assets/video/..."
print(scene_result.timing.segments)       # Ordered timed segments for visual transitions
```

### Consuming the Data Contract (`AvatarVoiceSceneResult`)
```json
{
  "scene_id": "scene_step_ohm_01",
  "status": "ready",
  "spoken_text": "Voltage equals current multiplied by resistance. In other words, V equals I times R.",
  "display_text": "Voltage equals current multiplied by resistance. In other words, V equals I times R.",
  "language": "Hinglish",
  "audio": {
    "asset_id": "audio_mock_1a2b3c4d",
    "url": "/api/avatar-voice/assets/audio/audio_mock_1a2b3c4d",
    "local_path": "D:/.../backend/data/cache/voice/audio_mock_1a2b3c4d.wav",
    "duration_seconds": 4.8
  },
  "avatar": {
    "asset_id": "avatar_mock_9z8y7x6w",
    "url": "/api/avatar-voice/assets/video/avatar_mock_9z8y7x6w",
    "local_path": "D:/.../backend/data/cache/avatar/avatar_mock_9z8y7x6w.mp4",
    "duration_seconds": 4.8,
    "lip_synced": true
  },
  "timing": {
    "duration_seconds": 4.8,
    "drift_seconds": 0.0,
    "drift_acceptable": true,
    "segments": [
      {
        "segment_id": "seg_01",
        "text": "Voltage equals current multiplied by resistance.",
        "start_seconds": 0.0,
        "end_seconds": 2.5,
        "emphasis": true
      },
      {
        "segment_id": "seg_02",
        "text": "In other words, V equals I times R.",
        "start_seconds": 2.5,
        "end_seconds": 4.8,
        "emphasis": false
      }
    ]
  },
  "presentation": {
    "expression": "focused",
    "gesture": "explain",
    "position": "right",
    "scale": 1.0
  },
  "fallback": null,
  "error": null
}
```

---

## 3. Pedagogical Expression & Intent Mapping

| Teaching Context / Intent | Avatar Expression | Teacher Gesture | Pedagogical Purpose |
|---|---|---|---|
| `explanation` / `explaining` | `focused` / `friendly` | `explain` | Clear instructional focus |
| `demonstration` / `visual` | `engaged` | `point_visual` | Direct student focus to equation/graph |
| `question` / `assessment` | `curious` | `thinking` | Prompt active recall and contemplation |
| `re_explanation` / `reteaching` | `patient` | `explain` | Supportive, calming response to misconception |
| `encouraging` / `celebrating` | `encouraging` / `celebrating` | `welcome` | Positive reinforcement after correct answer |
| `summary` | `confident` | `emphasize` | Final concept synthesis |

---

## 4. Mathematical Pronunciation Normalization

STEM formulas are normalized automatically for TTS delivery while leaving `display_text` unaltered for visuals:
- $V = I \times R$ $\rightarrow$ `"V equals I multiplied by R"`
- $a^2 + b^2 = c^2$ $\rightarrow$ `"a squared plus b squared equals c squared"`
- $F = ma$ $\rightarrow$ `"F equals m a"`
- $5\Omega$ $\rightarrow$ `"5 ohms"`
- $10\text{V}$ $\rightarrow$ `"10 volts"`
- $\frac{a}{b}$ $\rightarrow$ `"a over b"`

---

## 5. Environment Configuration

```bash
# Provider selection (default: mock for zero-cost offline testing)
VOICE_PROVIDER=mock          # mock, openai, elevenlabs
AVATAR_PROVIDER=mock         # mock, did, heygen

# External API Keys (optional)
VOICE_API_KEY=your_tts_key
AVATAR_API_KEY=your_avatar_key

# Subsystem Controls
MAX_PROVIDER_RETRIES=2
MAX_DURATION_DRIFT_SECONDS=0.5
```
