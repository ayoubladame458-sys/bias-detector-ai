"""
Document upload and management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse
from app.models.schemas import DocumentUploadResponse, DocumentMetadata
from app.services.document_service import document_service
from app.services.chroma_service import chroma_service
from app.services.database_service import database_service
from app.core.config import settings
from pathlib import Path
import aiofiles
from datetime import datetime
from typing import List

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for bias analysis

    Accepts PDF, TXT, and DOCX files up to 10MB.
    The document will be stored locally and metadata saved to MongoDB.
    """
    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Accepted types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Read file content to check size
    content = await file.read()
    file_size = len(content)

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )

    # Generate document ID and save file
    document_id = document_service.generate_document_id()
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{document_id}.{file_extension}"

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    uploaded_at = datetime.utcnow()

    # Save document metadata to database
    await database_service.save_document({
        "document_id": document_id,
        "filename": file.filename,
        "file_size": file_size,
        "file_type": file_extension,
        "uploaded_at": uploaded_at,
        "analyzed": False
    })

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        file_size=file_size,
        file_type=file_extension,
        uploaded_at=uploaded_at
    )


@router.get("/list")
async def list_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    List all uploaded documents with pagination
    """
    try:
        documents = await database_service.get_all_documents(skip=skip, limit=limit)

        # Convert datetime objects
        for doc in documents:
            if "uploaded_at" in doc and hasattr(doc["uploaded_at"], "isoformat"):
                doc["uploaded_at"] = doc["uploaded_at"].isoformat()
            if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
                doc["created_at"] = doc["created_at"].isoformat()
            if "updated_at" in doc and hasattr(doc["updated_at"], "isoformat"):
                doc["updated_at"] = doc["updated_at"].isoformat()

        return {
            "documents": documents,
            "skip": skip,
            "limit": limit,
            "count": len(documents)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document_metadata(document_id: str):
    """
    Get metadata for a specific document
    """
    # First try to get from database
    db_doc = await database_service.get_document(document_id)

    if db_doc:
        return DocumentMetadata(
            document_id=document_id,
            filename=db_doc.get("filename", "unknown"),
            file_type=db_doc.get("file_type", "unknown"),
            file_size=db_doc.get("file_size", 0),
            uploaded_at=db_doc.get("uploaded_at", datetime.utcnow()),
            analyzed=db_doc.get("analyzed", False),
            analysis_id=db_doc.get("last_analysis_id")
        )

    # Fallback to file system
    upload_dir = Path(settings.UPLOAD_DIR)
    matching_files = list(upload_dir.glob(f"{document_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    file_path = matching_files[0]
    file_stats = file_path.stat()

    return DocumentMetadata(
        document_id=document_id,
        filename=file_path.name,
        file_type=file_path.suffix[1:],
        file_size=file_stats.st_size,
        uploaded_at=datetime.fromtimestamp(file_stats.st_ctime),
        analyzed=False
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """
    Delete a document and all associated data

    This will:
    1. Delete the file from local storage
    2. Delete document metadata and analyses from MongoDB
    3. Delete embeddings from Pinecone vector database
    """
    upload_dir = Path(settings.UPLOAD_DIR)

    # Find the file
    matching_files = list(upload_dir.glob(f"{document_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    errors = []

    # 1. Delete files from local storage
    try:
        for file_path in matching_files:
            file_path.unlink()
    except Exception as e:
        errors.append(f"File deletion error: {str(e)}")

    # 2. Delete from MongoDB
    try:
        await database_service.delete_document(document_id)
    except Exception as e:
        errors.append(f"Database deletion error: {str(e)}")

    # 3. Delete embeddings from Pinecone
    try:
        await chroma_service.delete_document(document_id)
    except Exception as e:
        errors.append(f"Pinecone deletion error: {str(e)}")

    if errors and len(errors) == 3:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {'; '.join(errors)}"
        )

    return None
