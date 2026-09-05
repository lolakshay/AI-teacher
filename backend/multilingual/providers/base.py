"""
Abstract Base Class for Translation and Pedagogical Adaptation Providers.
Conforms to Sections 23, 24.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class TranslationProvider(ABC):
    @abstractmethod
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[Dict[str, Any]] = None,
        terminology: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Translates raw educational text while respecting context and terminology."""
        pass

    @abstractmethod
    def adapt_teaching_step(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        topic: Optional[str] = None,
        concept_id: Optional[str] = None,
        learner_level: str = "beginner",
        teaching_style: str = "analogy_driven",
        terminology: Optional[List[str]] = None,
        example: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs pedagogical adaptation returning structured content:
        spoken_text, display_text, example, preserved_terms, notes.
        """
        pass
