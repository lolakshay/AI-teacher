"""
ConceptNode Data Contract conforming to Section 5.2.
"""

from typing import List, Any
from pydantic import BaseModel, Field

class ConceptNode(BaseModel):
    concept_id: str
    name: str
    description: str
    importance: float = Field(default=0.8, ge=0.0, le=1.0)
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    prerequisites: List[str] = Field(default_factory=list)
    estimated_minutes: float = Field(default=5.0, gt=0.0)
    learning_objective: str = ""
    must_teach: bool = True
    source_references: List[Any] = Field(default_factory=list)
