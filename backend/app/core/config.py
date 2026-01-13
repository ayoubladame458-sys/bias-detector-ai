"""
Application configuration settings
BiasDetector - 100% Local AI with Ollama (No API keys needed!)
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "BiasDetector"
    DEBUG: bool = True

    # Ollama Configuration (Local AI - No API keys needed!)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"  # Fast and capable - alternatives: mistral, phi3
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"  # Best local embedding model

    # ChromaDB Configuration (Local Vector Database - No API key needed!)
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_DIMENSION: int = 768  # nomic-embed-text produces 768-dim vectors

    # MongoDB Configuration (local)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "biasdetector"

    # RAG Configuration
    RAG_ENABLED: bool = True
    RAG_MAX_CONTEXT_CHUNKS: int = 5
    RAG_RELEVANCE_THRESHOLD: float = 0.7

    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # These are hardcoded to avoid .env parsing issues
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """CORS allowed origins"""
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001"
        ]

    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        """Allowed file extensions for upload"""
        return ["pdf", "txt", "docx"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
