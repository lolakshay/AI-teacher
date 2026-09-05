"""
Material Pipeline and Knowledge / RAG Subsystem
Responsible for:
1. Ingesting uploaded documents (PDF, DOCX, TXT)
2. Extracting text with metadata (page numbers, titles)
3. Chunking content with overlap
4. Storing chunks in searchable vector/keyword index
5. Providing grounded retrieval with source references
"""

import os
import uuid
import math
from typing import List, Dict, Any, Optional
from pathlib import Path
from pypdf import PdfReader
from backend.app.core.config import settings

class DocumentChunk:
    def __init__(self, chunk_id: str, doc_id: str, text: str, page: int, source_name: str):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.text = text
        self.page = page
        self.source_name = source_name

class MaterialPipeline:
    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunks: Dict[str, List[DocumentChunk]] = {}

    def ingest_file(self, file_path: Path, original_filename: str) -> str:
        """Ingests a file, extracts text, chunks it, and indexes it."""
        doc_id = str(uuid.uuid4())[:8]
        extracted_pages = []

        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            reader = PdfReader(str(file_path))
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    extracted_pages.append({"page": idx + 1, "text": text.strip()})
        elif suffix in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(str(file_path))
                full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                extracted_pages.append({"page": 1, "text": full_text})
            except Exception as e:
                extracted_pages.append({"page": 1, "text": f"Error extracting DOCX: {e}"})
        else:
            # Plain text / markdown
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                full_text = f.read()
                extracted_pages.append({"page": 1, "text": full_text})

        # Chunking
        doc_chunks: List[DocumentChunk] = []
        for page_info in extracted_pages:
            p_text = page_info["text"]
            p_num = page_info["page"]
            words = p_text.split()
            chunk_size = 120
            overlap = 20

            if not words:
                continue

            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                chunk_str = " ".join(chunk_words)
                chunk_id = f"{doc_id}_c{len(doc_chunks)}"
                doc_chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=chunk_str,
                    page=p_num,
                    source_name=original_filename
                ))

        self.documents[doc_id] = {
            "doc_id": doc_id,
            "filename": original_filename,
            "page_count": len(extracted_pages),
            "chunk_count": len(doc_chunks),
            "path": str(file_path)
        }
        self.chunks[doc_id] = doc_chunks
        return doc_id

    def retrieve(self, doc_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves most relevant chunks with keyword-relevance ranking and source attribution."""
        if doc_id not in self.chunks:
            return []

        doc_chunks = self.chunks[doc_id]
        query_words = set(query.lower().split())

        scored_chunks = []
        for chunk in doc_chunks:
            chunk_words = set(chunk.text.lower().split())
            intersection = query_words.intersection(chunk_words)
            # Basic TF overlap scoring
            score = len(intersection) / (math.sqrt(len(query_words)) * math.sqrt(len(chunk_words)) + 1e-5)
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, chunk in scored_chunks[:top_k]:
            results.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "page": chunk.page,
                "source_name": chunk.source_name,
                "score": round(score, 3)
            })
        return results

    def get_document_summary(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.documents.get(doc_id)

material_pipeline = MaterialPipeline()
