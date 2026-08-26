"""Pydantic models for document processing results."""
from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ContentType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    IMAGE = "image"
    FORMULA = "formula"
    UNKNOWN = "unknown"


class ExtractedBlock(BaseModel):
    """A single extracted content block from a document page."""
    block_id: str
    page: int
    content_type: ContentType
    text: str
    confidence: float = 1.0
    bounding_box: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = {}


class PageResult(BaseModel):
    """All extracted blocks from a single document page."""
    page_number: int
    blocks: List[ExtractedBlock] = []
    raw_text: str = ""
    has_images: bool = False
    has_tables: bool = False
    has_charts: bool = False


class DocumentResult(BaseModel):
    """Complete extraction result for an entire document."""
    document_id: str
    filename: str
    total_pages: int
    pages: List[PageResult] = []
    full_text: str = ""
    tables: List[Dict] = []
    images_count: int = 0
    processing_time_ms: float = 0.0
    model_used: str = "heuristic"
    status: str = "processed"
