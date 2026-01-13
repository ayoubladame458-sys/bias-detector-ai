"""
Pinecone service for vector storage and semantic search
"""
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
from typing import List, Dict, Optional
import uuid


class PineconeService:
    """Service for interacting with Pinecone vector database"""

    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if not"""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]

            if self.index_name not in existing_indexes:
                # Create index with text-embedding-3-small dimension (1536)
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )

            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            raise Exception(f"Error initializing Pinecone index: {str(e)}")

    async def upsert_document(
        self,
        document_id: str,
        text_chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict
    ) -> bool:
        """
        Store document chunks with their embeddings in Pinecone

        Args:
            document_id: Unique identifier for the document
            text_chunks: List of text chunks from the document
            embeddings: List of embedding vectors corresponding to chunks
            metadata: Metadata about the document

        Returns:
            True if successful
        """
        try:
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
                vector_id = f"{document_id}_chunk_{i}"
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        **metadata,
                        "document_id": document_id,
                        "chunk_index": i,
                        "text": chunk
                    }
                })

            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)

            return True

        except Exception as e:
            raise Exception(f"Error upserting document to Pinecone: {str(e)}")

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform semantic search using query embedding

        Args:
            query_embedding: Embedding vector of the search query
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of search results with scores and metadata
        """
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )

            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]

        except Exception as e:
            raise Exception(f"Error searching in Pinecone: {str(e)}")

    async def get_document_chunks(self, document_id: str) -> List[Dict]:
        """
        Retrieve all chunks for a specific document

        Args:
            document_id: The document identifier

        Returns:
            List of document chunks with metadata
        """
        try:
            # Query with a dummy vector, filtering by document_id
            results = self.index.query(
                vector=[0.0] * 1536,  # Dummy vector
                top_k=10000,  # Get all chunks
                filter={"document_id": document_id},
                include_metadata=True
            )

            return [
                {
                    "id": match.id,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]

        except Exception as e:
            raise Exception(f"Error retrieving document chunks: {str(e)}")

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete all vectors associated with a document

        Args:
            document_id: The document identifier

        Returns:
            True if successful
        """
        try:
            self.index.delete(filter={"document_id": document_id})
            return True

        except Exception as e:
            raise Exception(f"Error deleting document from Pinecone: {str(e)}")

    async def get_stats(self) -> Dict:
        """
        Get index statistics

        Returns:
            Dictionary with index stats
        """
        try:
            return self.index.describe_index_stats()
        except Exception as e:
            raise Exception(f"Error getting Pinecone stats: {str(e)}")


# Singleton instance
pinecone_service = PineconeService()
