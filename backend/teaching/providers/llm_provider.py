"""
LLM Provider Abstraction conforming to Section 27 and 28.
Supports Gemini API with structured JSON output and robust deterministic pedagogical fallbacks.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass


class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.client = genai.GenerativeModel(settings.DEFAULT_LLM_MODEL)
                logger.info("Gemini LLM Provider initialized.")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}. Fallback provider will be used.")

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if self.client:
            try:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
                res = self.client.generate_content(full_prompt)
                if res and res.text:
                    return res.text.strip()
            except Exception as e:
                logger.warning(f"Gemini text generation failed: {e}")
        return "Deterministic pedagogical response."

    def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if self.client:
            try:
                instruct = (
                    (system_instruction or "") +
                    "\nOutput ONLY valid JSON without markdown fences, comments, or extra text."
                )
                res = self.client.generate_content(f"{instruct}\n\nRequest:\n{prompt}")
                if res and res.text:
                    cleaned = res.text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()
                    return json.loads(cleaned)
            except Exception as e:
                logger.warning(f"Gemini structured JSON generation failed: {e}. Using fallback data.")

        return fallback_data or {}

# Default singleton instance
llm_provider = GeminiLLMProvider()
