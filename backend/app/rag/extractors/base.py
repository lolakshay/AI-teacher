"""
Base Document Extractor Interface
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple
from backend.app.rag.models import ExtractedBlock


class DocumentExtractor(ABC):
    @abstractmethod
    def can_handle(self, file_path: Path, mime_type: str = "") -> bool:
        """Determines whether this extractor can parse the given file."""
        pass

    @abstractmethod
    def extract(self, file_path: Path) -> Tuple[List[ExtractedBlock], bool]:
        """
        Extracts content into structured blocks.
        Returns:
            Tuple[List[ExtractedBlock], bool]:
                - List of normalized extracted blocks.
                - requires_ocr: True if scanned or text-poor pages detected.
        """
        pass
