"""
Speech Segmenter for Structured Pedagogical Explanations (Agent 5)
Splits speech into sequential timing segments for Agent 4 synchronization,
ensuring equations and mathematical formulas are never fragmented across boundaries.
"""

import re
from typing import List
from backend.avatar_voice.models.voice import SpeechSegment

class SpeechSegmenter:
    """
    Safely segments teacher explanations into sequenced chunks with timing cues.
    """

    # Protected mathematical tokens that must never be split across segment boundaries
    MATH_BLOCK_PATTERNS = [
        r"[Vv]\s*=\s*[Ii]\s*[×\*x]\s*[Rr]",
        r"[Ii]\s*=\s*[Vv]\s*[/÷]\s*[Rr]",
        r"[Rr]\s*=\s*[Vv]\s*[/÷]\s*[Ii]",
        r"[Ff]\s*=\s*[Mm][Aa]",
        r"[Ee]\s*=\s*[Mm][Cc][\^²2]",
        r"[Yy]\s*=\s*[Mm][Xx]\s*\+\s*[Cc]",
        r"[Aa][\^²2]\s*\+\s*[Bb][\^²2]\s*=\s*[Cc][\^²2]",
        r"∫\s*[a-zA-Z0-9\(\)]+\s*d[a-zA-Z]"
    ]

    def segment(self, text: str, total_duration: float = 0.0, speaking_rate: float = 1.0) -> List[SpeechSegment]:
        """
        Segments text into ordered SpeechSegment objects.
        If total_duration > 0, normalizes segment timestamps to span [0, total_duration].
        Otherwise estimates duration at ~2.5 words per second.
        """
        text = text.strip()
        if not text:
            return []

        # Mask math expressions temporarily with placeholder tokens to avoid punctuation splitting
        masks = {}
        masked_text = text
        for idx, pattern in enumerate(self.MATH_BLOCK_PATTERNS):
            matches = list(re.finditer(pattern, masked_text))
            for m_idx, match in enumerate(matches):
                placeholder = f"__MATH_UNIT_{idx}_{m_idx}__"
                masks[placeholder] = match.group(0)
                masked_text = masked_text.replace(match.group(0), placeholder)

        # Split on sentence boundaries (. ! ? \n or semicolon with pause)
        # Avoid splitting on decimals e.g. 1.5V
        raw_sentences = re.split(r"(?<=[.!?\n;])\s+(?=[A-Z0-9\"'__])", masked_text)
        
        # Unmask math placeholders
        segments_text = []
        for s in raw_sentences:
            cleaned = s.strip()
            if not cleaned:
                continue
            for placeholder, original in masks.items():
                cleaned = cleaned.replace(placeholder, original)
            segments_text.append(cleaned)

        if not segments_text:
            segments_text = [text]

        # Calculate word-count weighted durations
        word_counts = [max(1, len(s.split())) for s in segments_text]
        total_words = sum(word_counts)

        # Average speaking speed: 2.5 words/sec modified by speaking_rate
        if total_duration <= 0.0:
            words_per_sec = 2.5 * speaking_rate
            total_duration = max(1.0, total_words / words_per_sec)

        segments: List[SpeechSegment] = []
        current_time = 0.0

        for idx, seg_text in enumerate(segments_text):
            seg_duration = (word_counts[idx] / total_words) * total_duration
            start_sec = round(current_time, 2)
            end_sec = round(current_time + seg_duration, 2)
            
            # Detect educational emphasis keywords
            emphasis = any(w in seg_text.lower() for w in [
                "important", "dhyan", "remember", "key", "crucial", "voltage", "current", "resistance"
            ])

            segments.append(SpeechSegment(
                segment_id=f"seg_{idx+1:02d}",
                text=seg_text,
                display_text=seg_text,
                start_seconds=start_sec,
                end_seconds=end_sec,
                emphasis=emphasis
            ))
            current_time += seg_duration

        # Ensure exact end bound matches total duration
        if segments:
            segments[-1].end_seconds = round(total_duration, 2)

        return segments

speech_segmenter = SpeechSegmenter()
