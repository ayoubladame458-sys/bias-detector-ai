"""
BiasDetector API - 100% Local AI with Ollama + ChromaDB
No API keys needed! RAG-powered bias detection system.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import analysis, documents, search, rag
from app.services.database_service import database_service
from app.services.ollama_service import ollama_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    print("\n" + "="*50)
    print("  BiasDetector API - 100% Local AI")
    print("="*50)
    print(f"  AI Model: {settings.OLLAMA_MODEL}")
    print(f"  Embeddings: {settings.OLLAMA_EMBEDDING_MODEL}")
    print(f"  Vector DB: ChromaDB (local)")
    print(f"  RAG Enabled: {settings.RAG_ENABLED}")
    print("="*50 + "\n")

    # Check Ollama status
    ollama_status = await ollama_service.get_status()
    if ollama_status["status"] == "online":
        print(f"Ollama: Connected")
        print(f"Available models: {', '.join(ollama_status.get('models_available', []))}")
    else:
        print(f"WARNING: Ollama is not running!")
        print(f"Start it with: ollama serve")
        print(f"Then pull models: ollama pull {settings.OLLAMA_MODEL}")
        print(f"                  ollama pull {settings.OLLAMA_EMBEDDING_MODEL}")

    # Connect to MongoDB
    await database_service.connect()

    yield

    # Shutdown
    print("\nShutting down BiasDetector API...")
    await database_service.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# BiasDetector API - 100% Local AI

AI-powered bias detection using **Ollama** (local LLM) and **ChromaDB** (local vector database).

## No API Keys Needed!

This system runs completely locally:
- **Ollama** for AI analysis (llama3.2, mistral, etc.)
- **ChromaDB** for vector storage and semantic search
- **MongoDB** for persistent analysis history

## Features

- Document upload (PDF, DOCX, TXT)
- RAG-enhanced bias analysis
- Semantic search across documents
- Q&A about bias patterns
- Analysis history and statistics

## Quick Start

1. Install Ollama: https://ollama.ai
2. Pull models: `ollama pull llama3.2 && ollama pull nomic-embed-text`
3. Start MongoDB
4. Run this API

    """,
    version="3.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["Analysis"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["Search"])
app.include_router(rag.router, prefix=f"{settings.API_V1_STR}/rag", tags=["RAG"])


@app.get("/")
async def root():
    """Root endpoint - API info and status"""
    ollama_status = await ollama_service.get_status()

    return {
        "message": "BiasDetector API - 100% Local AI",
        "version": "3.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
        "status": {
            "ollama": ollama_status["status"],
            "database": "connected" if database_service.connected else "disconnected",
            "rag_enabled": settings.RAG_ENABLED
        },
        "config": {
            "ai_model": settings.OLLAMA_MODEL,
            "embedding_model": settings.OLLAMA_EMBEDDING_MODEL,
            "vector_db": "ChromaDB (local)",
            "document_db": "MongoDB"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = await ollama_service.get_status()

    return {
        "status": "healthy" if ollama_status["status"] == "online" else "degraded",
        "ollama_status": ollama_status["status"],
        "database_connected": database_service.connected,
        "rag_enabled": settings.RAG_ENABLED
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
