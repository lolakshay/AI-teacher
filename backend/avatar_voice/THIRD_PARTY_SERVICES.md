# Third-Party Service Disclosure & Technology Architecture (Agent 5)

In accordance with Hackathon guidelines and Section 29 of the project architecture, this document discloses all third-party libraries, local tools, and external cloud AI services integrated into the **Avatar + Voice Subsystem (Agent 5)**.

---

## 1. Mock Providers (Offline / Local Default)

### 1.1 MockVoiceProvider
- **Category**: Local Built-in Python Standard Library
- **Purpose**: Generates deterministic, genuine 24kHz / 16-bit PCM WAV audio files for automated tests, offline development, and zero-cost demonstrations.
- **Input**: Spoken text string, language identifier, voice configuration parameters (rate, pitch, volume).
- **Output**: Binary PCM `.wav` file on local disk with duration matching pedagogical speech cadence.
- **Authentication**: None required.
- **Pricing / Dependency**: 100% Free, zero external network calls, zero API keys. Uses Python's standard `wave`, `struct`, and `math` modules.
- **Fallback**: Self-contained primary fallback.
- **Data Handling Considerations**: Audio is synthesized entirely in-memory and written locally to `backend/data/cache/voice`. No external telemetry or logging.

### 1.2 MockAvatarProvider
- **Category**: Local Open-Source Media Synthesis (`OpenCV` + `Pillow` + `NumPy`)
- **Purpose**: Generates valid animated teacher avatar `.mp4` video files with natural eye-blinking, speech-synced mouth opening/closing, teacher attire, and pedagogical HUD badges.
- **Input**: Spoken text string, audio asset, language, avatar configuration (expression, gesture, scale, position).
- **Output**: Valid `.mp4` video file on local disk with duration matching audio duration.
- **Authentication**: None required.
- **Pricing / Dependency**: Free, open-source (`opencv-python` / `pillow`).
- **Fallback**: If MP4 codec is unavailable on minimal server builds, falls back gracefully to deterministic lightweight video asset.
- **Data Handling Considerations**: Video frames are rendered locally in memory and saved to `backend/data/cache/avatar`.

---

## 2. External Voice Providers (Optional Cloud TTS)

### 2.1 OpenAI Audio Speech API (`tts-1`)
- **Category**: External Cloud API (Hosted AI Service)
- **Purpose**: High-fidelity natural neural TTS voice synthesis.
- **Input**: Normalized spoken text, voice model identifier (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`), speaking speed multiplier.
- **Output**: Compressed MP3 audio stream.
- **Authentication**: Environment variable `VOICE_API_KEY` (Bearer token).
- **Pricing / Dependency**: Paid per-character pricing (OpenAI API).
- **Fallback**: Automatic bounded retry (up to 2 retries with exponential backoff). If credentials fail or quota is exhausted, automatically falls back to `MockVoiceProvider`.
- **Data Handling Considerations**: Only educational explanation text is transmitted. No student personal identification or confidential test material is passed.

### 2.2 ElevenLabs Multilingual TTS API (`eleven_multilingual_v2`)
- **Category**: External Cloud API (Hosted AI Service)
- **Purpose**: Ultra-realistic multilingual educator voice synthesis with native Hindi and Hinglish accent nuances.
- **Input**: Spoken script, multilingual voice ID.
- **Output**: High-resolution MP3 audio stream.
- **Authentication**: Environment variable `VOICE_API_KEY` (`xi-api-key`).
- **Pricing / Dependency**: Paid subscription / character billing.
- **Fallback**: Graceful fallback to `MockVoiceProvider`.
- **Data Handling Considerations**: Transmits normalized educational lecture scripts over TLS.

---

## 3. External Avatar Providers (Optional Cloud Video)

### 3.1 D-ID Talks API
- **Category**: External Cloud API (Hosted AI Service)
- **Purpose**: Lip-synchronized talking human avatar video synthesis from educational scripts.
- **Input**: Spoken text or audio asset URL, avatar persona template.
- **Output**: Rendered MP4 talking educator video URL.
- **Authentication**: Environment variable `AVATAR_API_KEY` (`Authorization: Basic ...`).
- **Pricing / Dependency**: Paid per-video credit pricing.
- **Fallback**: If unavailable or times out, system degrades to **Level 3 Fallback (Audio-Only Presentation)**, returning the valid audio asset with `fallback: "audio_only"`.
- **Data Handling Considerations**: Content sent via encrypted HTTPS.

### 3.2 HeyGen Avatar Video API (v2)
- **Category**: External Cloud API (Hosted AI Service)
- **Purpose**: Photorealistic synthetic educator avatars with teacher gestures.
- **Input**: Character ID, voice input, lecture script.
- **Output**: MP4 video URL.
- **Authentication**: Environment variable `AVATAR_API_KEY` (`X-Api-Key`).
- **Pricing / Dependency**: Paid per-minute video credits.
- **Fallback**: Degrades to `MockAvatarProvider` or Level 3 Audio-Only.

---

## 4. Multi-Tiered Graceful Fallback Strategy

The system guarantees that an avatar or voice provider failure **never crashes the teaching session**:

1. **Level 1 (Full Presentation)**: Both voice and synthetic avatar video succeed with full lip-sync.
2. **Level 2 (Retried Presentation)**: Voice or avatar recovered through bounded exponential backoff retries.
3. **Level 3 (Audio-Only Presentation)**: Voice succeeds but avatar generation fails/unavailable. System returns `avatar: null`, `fallback: "audio_only"`, and Agent 4 renders the educational visuals and equations alongside the teacher's voice.
4. **Level 4 (Text & Visual Presentation)**: External voice and avatar are unavailable. System returns `fallback: "text_only"`, delivering display text, equations, and visual diagrams to the student.
