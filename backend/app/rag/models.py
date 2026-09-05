"""
Data Models and Contracts for Document Intelligence and RAG Pipeline
Strictly adheres to Part 2 specifications:
- DocumentLifecycleState & DocumentMetadata (Sections 5 & 6)
- ExtractedBlock (Section 8)
- DocumentChunk (Section 18)
- GroundedContext & SourceReference (Sections 22, 26, 27, 31)
- DocumentStructureSummary (Section 32)
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class DocumentLifecycleState(str, Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    EXTRACTING = "EXTRACTING"
    STRUCTURING = "STRUCTURING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"
    DELETED = "DELETED"


class GroundingStatus(str, Enum):
    GROUNDED = "grounded"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class ExtractedBlock(BaseModel):
    block_id: str = Field(default_factory=lambda: f"blk_{uuid.uuid4().hex[:8]}")
    text: str
    block_type: str = "paragraph"  # heading, paragraph, table, list, equation
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    section: Optional[str] = None
    heading_level: Optional[int] = None
    confidence: float = 1.0


class DocumentMetadata(BaseModel):
    document_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    filename: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    file_hash: str  # SHA-256
    title: Optional[str] = None
    author: Optional[str] = None
    language: str = "en"
    page_count: int = 0
    slide_count: int = 0
    processing_status: DocumentLifecycleState = DocumentLifecycleState.UPLOADED
    progress: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    processed_at: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    failed_stage: Optional[str] = None
    requires_ocr: bool = False
    chunk_count: int = 0


class DocumentChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    document_id: str
    text: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    slide_start: Optional[int] = None
    slide_end: Optional[int] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None
    chunk_index: int = 0
    language: str = "en"
    content_type: str = "educational"
    source_type: str = "pdf"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SourceReference(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    slide_start: Optional[int] = None
    slide_end: Optional[int] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    score: float
    text: str
    source_type: str = "pdf"


class GroundedContext(BaseModel):
    status: str = GroundingStatus.NOT_FOUND.value  # grounded, partial, not_found, unavailable
    query: str
    sources: List[SourceReference] = Field(default_factory=list)
    context_text: str = ""
    relevance_score: float = 0.0


class ProcessingStatusResponse(BaseModel):
    status: str
    progress: int
    stage: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class ChapterSummary(BaseModel):
    name: str
    sections: List[str] = Field(default_factory=list)


class DocumentStructureSummary(BaseModel):
    document_id: str
    title: str
    chapters: List[ChapterSummary] = Field(default_factory=list)


class DocumentSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None


class RAGRetrieveRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None
