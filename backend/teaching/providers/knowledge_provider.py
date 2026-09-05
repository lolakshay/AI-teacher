"""
Knowledge Retriever Adapter conforming to Section 26.
Interfaces cleanly with Agent 2 (RAG Subsystem) or falls back gracefully.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class KnowledgeRetriever(ABC):
    @abstractmethod
    def retrieve_context(
        self,
        query: str,
        material_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        pass


class DefaultKnowledgeRetriever(KnowledgeRetriever):
    def retrieve_context(
        self,
        query: str,
        material_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        if not material_id:
            return []

        try:
            from backend.app.services.material_pipeline import material_pipeline
            chunks = material_pipeline.retrieve(material_id, query, top_k=top_k)
            results = []
            for c in chunks:
                results.append({
                    "source": c.get("source_name", "Uploaded Material"),
                    "page": c.get("page", 1),
                    "chunk_id": c.get("chunk_id", ""),
                    "text": c.get("text", ""),
                    "score": c.get("score", 1.0)
                })
            return results
        except Exception as e:
            logger.warning(f"Error retrieving knowledge context: {e}")
            return []

knowledge_retriever = DefaultKnowledgeRetriever()
