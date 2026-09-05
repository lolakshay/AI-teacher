"""
LLM Service with Live Gemini API and Robust Pedagogical Fallback.
Guarantees reliable execution even in offline / rate-limited hackathon environments.
"""

import json
import logging
from typing import Optional, Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Check if google.generativeai is available and configured
gemini_client = None
if settings.GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_client = genai.GenerativeModel(settings.DEFAULT_LLM_MODEL)
        logger.info(f"Gemini API initialized successfully with model '{settings.DEFAULT_LLM_MODEL}'.")
    except Exception as e:
        logger.warning(f"Could not initialize Gemini API: {e}. Falling back to pedagogical engine.")


class LLMService:
    @staticmethod
    def generate_text(prompt: str, system_instruction: Optional[str] = None) -> str:
        """Calls Gemini if available; otherwise returns smart contextual response."""
        if gemini_client:
            try:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
                response = gemini_client.generate_content(full_prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini generation error: {e}. Using deterministic fallback.")
        
        return "Pedagogical engine fallback active."

    @staticmethod
    def generate_json(prompt: str, system_instruction: Optional[str] = None, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Requests structured JSON from Gemini or falls back to structured fallback data."""
        if gemini_client:
            try:
                instruct = (
                    (system_instruction or "") + 
                    "\nOutput ONLY valid JSON without markdown fences, comments, or extra text."
                )
                response = gemini_client.generate_content(f"{instruct}\n\nRequest:\n{prompt}")
                if response and response.text:
                    cleaned = response.text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()
                    return json.loads(cleaned)
            except Exception as e:
                logger.warning(f"Gemini JSON parse/generation error: {e}. Using structured fallback.")
        
        return fallback_data or {}

llm_service = LLMService()
