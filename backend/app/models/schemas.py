"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class BiasType(str, Enum):
    """Types of bias that can be detected"""
    GENDER = "gender"
    POLITICAL = "political"
    CULTURAL = "cultural"
    CONFIRMATION = "confirmation"
    SELECTION = "selection"
    ANCHORING = "anchoring"
    OTHER = "other"


class BiasInstance(BaseModel):
    """A single instance of detected bias"""
    type: BiasType
    text: str = Field(..., description="The biased text passage")
    explanation: str = Field(..., description="Why this is considered biased")
    severity: float = Field(..., ge=0, le=1, description="Severity score from 0 to 1")
    start_position: int = Field(..., description="Start character position in document")
    end_position: int = Field(..., description="End character position in document")
    suggestions: Optional[str] = Field(None, description="Suggestions for improvement")


class BiasAnalysisResult(BaseModel):
    """Result of bias analysis"""
    document_id: str
    overall_score: float = Field(..., ge=0, le=1, description="Overall bias score from 0 to 1")
    bias_instances: List[BiasInstance]
    summary: str = Field(..., description="Summary of the analysis")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str
    filename: str
    file_size: int
    file_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentMetadata(BaseModel):
    """Metadata about an analyzed document"""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    analyzed: bool = False
    analysis_id: Optional[str] = None


class SearchQuery(BaseModel):
    """Search query for semantic search"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    filter: Optional[Dict] = None


class SearchResult(BaseModel):
    """Single search result"""
    document_id: str
    filename: str
    text_chunk: str
    relevance_score: float = Field(..., ge=0, le=1)
    metadata: Dict


class SearchResponse(BaseModel):
    """Response for semantic search"""
    results: List[SearchResult]
    query: str
    total_results: int


class AnalysisRequest(BaseModel):
    """Request to analyze a document"""
    document_id: str
    bias_types: Optional[List[BiasType]] = None  # If None, analyze all types


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
