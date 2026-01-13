"""
Semantic search endpoints - Using Ollama + ChromaDB (100% Local)
"""
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import SearchQuery, SearchResponse, SearchResult
from app.services.ollama_service import ollama_service
from app.services.chroma_service import chroma_service

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def semantic_search(query: SearchQuery):
    """
    Perform semantic search across all analyzed documents

    Uses Ollama for embeddings and ChromaDB for vector search.
    100% local - no API keys needed!
    """
    try:
        # Generate embedding for the search query using Ollama
        query_embedding = await ollama_service.generate_embedding(query.query)

        if not query_embedding:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate embedding. Make sure Ollama is running."
            )

        # Search in ChromaDB
        results = await chroma_service.search(
            query_embedding=query_embedding,
            top_k=query.top_k,
            filter=query.filter
        )

        # Convert to response model
        search_results = [
            SearchResult(
                document_id=result["metadata"].get("document_id", ""),
                filename=result["metadata"].get("filename", ""),
                text_chunk=result["metadata"].get("text", ""),
                relevance_score=result["score"],
                metadata=result["metadata"]
            )
            for result in results
        ]

        return SearchResponse(
            results=search_results,
            query=query.query,
            total_results=len(search_results)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )


@router.get("/stats")
async def get_search_stats():
    """
    Get statistics about the vector database (ChromaDB)
    """
    try:
        stats = await chroma_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving stats: {str(e)}"
        )
