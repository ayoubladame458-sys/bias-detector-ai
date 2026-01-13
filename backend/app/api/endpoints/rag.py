"""
RAG (Retrieval Augmented Generation) endpoints for contextual bias analysis
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.services.rag_service import rag_service
from app.services.database_service import database_service
from app.core.config import settings

router = APIRouter()


class QuestionRequest(BaseModel):
    """Request model for asking questions about bias"""
    question: str = Field(..., min_length=5, max_length=500, description="Question about bias patterns")
    document_id: Optional[str] = Field(None, description="Optional document ID to focus on")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of context chunks to retrieve")


class QuestionResponse(BaseModel):
    """Response model for Q&A"""
    question: str
    answer: str
    sources: List[Dict]
    num_sources_used: int


class ContextRequest(BaseModel):
    """Request to get relevant context for a text"""
    text: str = Field(..., min_length=10, max_length=5000, description="Text to find similar content for")
    exclude_document_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=10)


class ContextResponse(BaseModel):
    """Response with relevant context chunks"""
    context_chunks: List[Dict]
    total_found: int


class StatisticsResponse(BaseModel):
    """Response with system statistics"""
    total_documents: int
    total_analyses: int
    average_bias_score: float
    bias_distribution: List[Dict]
    database_connected: bool
    rag_enabled: bool


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about bias patterns using RAG.

    This endpoint uses the knowledge base of previously analyzed documents
    to answer questions about bias patterns, common biases, and insights.

    Example questions:
    - "What types of gender bias are most common in the analyzed documents?"
    - "Are there any political biases in document X?"
    - "What suggestions are commonly given for reducing cultural bias?"
    """
    if not settings.RAG_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG feature is disabled"
        )

    try:
        result = await rag_service.semantic_qa(
            question=request.question,
            document_id=request.document_id,
            top_k=request.top_k
        )

        return QuestionResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            num_sources_used=result["num_sources_used"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/context", response_model=ContextResponse)
async def get_relevant_context(request: ContextRequest):
    """
    Get relevant context chunks for a piece of text.

    This is useful for understanding what similar content exists
    in the knowledge base before analyzing new documents.
    """
    if not settings.RAG_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG feature is disabled"
        )

    try:
        context_chunks = await rag_service.retrieve_relevant_context(
            query_text=request.text,
            exclude_document_id=request.exclude_document_id,
            top_k=request.top_k
        )

        return ContextResponse(
            context_chunks=context_chunks,
            total_found=len(context_chunks)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving context: {str(e)}"
        )


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    Get overall statistics about the bias detection system.

    Returns information about:
    - Total documents analyzed
    - Total analyses performed
    - Average bias score across all analyses
    - Distribution of bias types found
    """
    try:
        stats = await database_service.get_statistics()

        return StatisticsResponse(
            total_documents=stats.get("total_documents", 0),
            total_analyses=stats.get("total_analyses", 0),
            average_bias_score=stats.get("average_bias_score", 0),
            bias_distribution=stats.get("bias_distribution", []),
            database_connected=stats.get("database_connected", False),
            rag_enabled=settings.RAG_ENABLED
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.get("/status")
async def get_rag_status():
    """
    Get the current status of the RAG system (Ollama + ChromaDB).
    """
    from app.services.ollama_service import ollama_service

    ollama_status = await ollama_service.get_status()

    return {
        "rag_enabled": settings.RAG_ENABLED,
        "max_context_chunks": settings.RAG_MAX_CONTEXT_CHUNKS,
        "relevance_threshold": settings.RAG_RELEVANCE_THRESHOLD,
        "database_connected": database_service.connected,
        "ollama_status": ollama_status,
        "embedding_model": settings.OLLAMA_EMBEDDING_MODEL,
        "analysis_model": settings.OLLAMA_MODEL,
        "vector_db": "ChromaDB (local)"
    }
