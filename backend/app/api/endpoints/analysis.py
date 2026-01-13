"""
Bias analysis endpoints with RAG - 100% Local with Ollama + ChromaDB
No API keys needed!
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Query
from pydantic import BaseModel, Field
from app.models.schemas import (
    AnalysisRequest,
    BiasAnalysisResult,
    BiasInstance,
    BiasType
)
from app.services.document_service import document_service
from app.services.ollama_service import ollama_service
from app.services.chroma_service import chroma_service
from app.services.rag_service import rag_service
from app.services.database_service import database_service
from app.core.config import settings
from pathlib import Path
from datetime import datetime
from typing import List, Optional

router = APIRouter()


class RAGAnalysisRequest(BaseModel):
    """Extended analysis request with RAG options"""
    document_id: str
    bias_types: Optional[List[BiasType]] = None
    use_rag: bool = Field(default=True, description="Enable RAG for contextual analysis")


class RAGAnalysisResult(BiasAnalysisResult):
    """Extended analysis result with RAG metadata"""
    rag_metadata: Optional[dict] = None
    comparative_insights: Optional[str] = None


class AnalysisHistoryResponse(BaseModel):
    """Response containing analysis history"""
    document_id: str
    analyses: List[dict]
    total_count: int


async def process_embeddings(
    document_id: str,
    file_path: Path,
    file_type: str
):
    """
    Background task to process and store document embeddings in ChromaDB
    Uses Ollama for local embedding generation
    """
    try:
        # Extract text from document
        text = await document_service.extract_text(str(file_path), file_type)

        # Chunk the text
        chunks = document_service.chunk_text(text)

        # Generate embeddings for all chunks using Ollama
        embeddings = []
        for chunk in chunks:
            try:
                embedding = await ollama_service.generate_embedding(chunk)
                if embedding:
                    embeddings.append(embedding)
                else:
                    print(f"Warning: Empty embedding for chunk")
            except Exception as e:
                print(f"Error generating embedding: {e}")
                continue

        if embeddings and len(embeddings) == len(chunks):
            # Store in ChromaDB
            await chroma_service.upsert_document(
                document_id=document_id,
                text_chunks=chunks,
                embeddings=embeddings,
                metadata={
                    "filename": file_path.name,
                    "file_type": file_type,
                    "uploaded_at": datetime.utcnow().isoformat()
                }
            )
            print(f"Successfully stored {len(chunks)} chunks for document {document_id}")
        else:
            print(f"Warning: Embedding count mismatch. Chunks: {len(chunks)}, Embeddings: {len(embeddings)}")

    except Exception as e:
        print(f"Error in background embedding processing: {str(e)}")


@router.post("/analyze", response_model=RAGAnalysisResult)
async def analyze_document(
    request: RAGAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a document for bias using local RAG (Ollama + ChromaDB)

    This endpoint performs bias detection using:
    1. Ollama for AI analysis (no API key needed)
    2. ChromaDB for vector storage (local)
    3. RAG context retrieval from previously analyzed documents

    The analysis is saved to MongoDB for history tracking.
    """
    # Find the document file
    upload_dir = Path(settings.UPLOAD_DIR)
    matching_files = list(upload_dir.glob(f"{request.document_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    file_path = matching_files[0]
    file_type = file_path.suffix[1:]

    try:
        # Extract text from document
        text = await document_service.extract_text(str(file_path), file_type)

        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text could be extracted from the document"
            )

        # Use RAG-enhanced analysis if enabled
        use_rag = request.use_rag and settings.RAG_ENABLED

        if use_rag:
            analysis_result = await rag_service.analyze_with_rag(
                text=text,
                document_id=request.document_id,
                bias_types=request.bias_types,
                use_context=True
            )
        else:
            # Standard analysis without RAG context
            analysis_result = await ollama_service.analyze_bias(
                text,
                [bt.value for bt in request.bias_types] if request.bias_types else None
            )
            analysis_result["rag_metadata"] = {"context_used": False, "num_reference_chunks": 0, "reference_documents": []}

        # Convert to response model
        bias_instances = []
        for instance in analysis_result.get("bias_instances", []):
            try:
                bias_type = instance.get("type", "other").lower()
                # Map to valid BiasType
                if bias_type not in [bt.value for bt in BiasType]:
                    bias_type = "other"

                bias_instances.append(
                    BiasInstance(
                        type=BiasType(bias_type),
                        text=instance.get("text", ""),
                        explanation=instance.get("explanation", ""),
                        severity=float(instance.get("severity", 0.5)),
                        start_position=int(instance.get("start_position", 0)),
                        end_position=int(instance.get("end_position", 0)),
                        suggestions=instance.get("suggestions", "")
                    )
                )
            except Exception as e:
                print(f"Error processing bias instance: {e}")
                continue

        analyzed_at = datetime.utcnow()

        result = RAGAnalysisResult(
            document_id=request.document_id,
            overall_score=float(analysis_result.get("overall_score", 0.0)),
            bias_instances=bias_instances,
            summary=analysis_result.get("summary", "Analysis complete"),
            analyzed_at=analyzed_at,
            rag_metadata=analysis_result.get("rag_metadata"),
            comparative_insights=analysis_result.get("comparative_insights")
        )

        # Save analysis to database
        analysis_data = {
            "document_id": request.document_id,
            "filename": file_path.name,
            "overall_score": result.overall_score,
            "bias_instances": [bi.model_dump() for bi in bias_instances],
            "summary": result.summary,
            "analyzed_at": analyzed_at,
            "rag_metadata": result.rag_metadata,
            "comparative_insights": result.comparative_insights,
            "bias_types_requested": [bt.value for bt in request.bias_types] if request.bias_types else None
        }
        await database_service.save_analysis(analysis_data)

        # Process and store embeddings in background
        background_tasks.add_task(
            process_embeddings,
            request.document_id,
            file_path,
            file_type
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing document: {str(e)}"
        )


@router.get("/history/{document_id}", response_model=AnalysisHistoryResponse)
async def get_analysis_history(
    document_id: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get the analysis history for a specific document"""
    try:
        analyses = await database_service.get_analyses_for_document(
            document_id=document_id,
            limit=limit
        )

        for analysis in analyses:
            if "analyzed_at" in analysis and hasattr(analysis["analyzed_at"], "isoformat"):
                analysis["analyzed_at"] = analysis["analyzed_at"].isoformat()
            if "created_at" in analysis and hasattr(analysis["created_at"], "isoformat"):
                analysis["created_at"] = analysis["created_at"].isoformat()

        return AnalysisHistoryResponse(
            document_id=document_id,
            analyses=analyses,
            total_count=len(analyses)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis history: {str(e)}"
        )


@router.get("/latest/{document_id}")
async def get_latest_analysis(document_id: str):
    """Get the most recent analysis for a document"""
    try:
        analysis = await database_service.get_latest_analysis(document_id)

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analysis found for this document"
            )

        if "analyzed_at" in analysis and hasattr(analysis["analyzed_at"], "isoformat"):
            analysis["analyzed_at"] = analysis["analyzed_at"].isoformat()
        if "created_at" in analysis and hasattr(analysis["created_at"], "isoformat"):
            analysis["created_at"] = analysis["created_at"].isoformat()

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving latest analysis: {str(e)}"
        )


@router.get("/all")
async def get_all_analyses(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get all analyses with pagination"""
    try:
        analyses = await database_service.get_all_analyses(skip=skip, limit=limit)

        for analysis in analyses:
            if "analyzed_at" in analysis and hasattr(analysis["analyzed_at"], "isoformat"):
                analysis["analyzed_at"] = analysis["analyzed_at"].isoformat()
            if "created_at" in analysis and hasattr(analysis["created_at"], "isoformat"):
                analysis["created_at"] = analysis["created_at"].isoformat()

        return {
            "analyses": analyses,
            "skip": skip,
            "limit": limit,
            "count": len(analyses)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analyses: {str(e)}"
        )
