"""
Structured Prompt Templates for Multilingual Adaptation.
Conforms strictly to Section 25.
"""

import json
from typing import List, Optional

SYSTEM_PEDAGOGICAL_TRANSLATION_PROMPT = """You are an expert multilingual educational adaptation engine for an AI Teacher.
Your sole mission is to adapt teaching content from a SOURCE LANGUAGE into a TARGET TEACHING LANGUAGE while preserving complete pedagogical fidelity.

CRITICAL PRESERVATION RULES:
1. MATHEMATICAL FORMULAS: Never alter, mutate, or rename equations (e.g. V = IR, I = V / R, LaTeX). Keep display notation identical.
2. NUMBERS & UNITS: Never change numerical constants, coefficients, or physical units (e.g. 10 V, 5 Ω, 24V, 4A, 3 L/s).
3. PROGRAMMING CODE: Any code blocks (```...```), keywords, functions, and identifiers must remain 100% byte-for-byte identical.
4. TECHNICAL TERMINOLOGY: Keep domain-specific terminology natural. In Hinglish or Hindi, technical terms (e.g. 'resistance', 'gradient descent', 'loss function') should remain in English/Latin script or follow standard Indian educational practice.
5. CONCEPT IDENTITY: Maintain exact conceptual meaning and pedagogical intent. Do NOT introduce unrelated facts or delete qualifiers.
6. HINGLISH MODE: If target language is 'hi-en' (Hinglish), produce natural conversational Indian classroom phrasing (e.g., "Resistance electrons ke flow ko oppose karta hai..."). Do not produce robotic or awkward literal translations.

OUTPUT FORMAT:
You MUST respond with valid JSON matching this schema:
{
    "spoken_text": "Natural spoken script tailored for TTS voice in target language",
    "display_text": "Visual slide text with formulas and code intact",
    "example": "Localized example or null",
    "preserved_terms": ["term1", "term2"],
    "notes": "Pedagogical alignment notes"
}
Output ONLY the raw JSON object without markdown fences, explanation, or conversational fillers.
"""

def build_adaptation_prompt(
    source_text: str,
    source_language: str,
    target_language: str,
    topic: Optional[str] = None,
    concept_id: Optional[str] = None,
    learner_level: str = "beginner",
    teaching_style: str = "analogy_driven",
    terminology: Optional[List[str]] = None,
    example: Optional[str] = None
) -> str:
    """Builds the structured user prompt enforcing pedagogical constraints."""
    prompt_payload = {
        "source_language": source_language,
        "target_teaching_language": target_language,
        "topic": topic or "General STEM",
        "canonical_concept_id": concept_id or "unspecified",
        "learner_level": learner_level,
        "teaching_style": teaching_style,
        "technical_terms_to_preserve": terminology or [],
        "source_text": source_text,
        "source_example": example or ""
    }
    return (
        f"ADAPTATION TASK SPECIFICATION:\n"
        f"{json.dumps(prompt_payload, indent=2)}\n\n"
        f"Execute pedagogical transformation adhering strictly to all preservation rules."
    )
