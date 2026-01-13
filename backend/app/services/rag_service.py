"""
RAG (Retrieval Augmented Generation) service for context-aware bias detection
Uses Ollama (local) + ChromaDB (local) - No API keys needed!
"""
from typing import List, Dict, Optional
from app.services.ollama_service import ollama_service
from app.services.chroma_service import chroma_service
from app.models.schemas import BiasType
import json


class RAGService:
    """
    Service implementing RAG pattern for enhanced bias detection.
    100% Local - Uses Ollama for AI and ChromaDB for vectors.

    RAG Flow:
    1. Retrieve relevant context from ChromaDB (similar documents/chunks)
    2. Augment the analysis prompt with retrieved context
    3. Generate bias analysis with Ollama (contextual awareness)
    """

    def __init__(self):
        self.max_context_chunks = 5
        self.context_relevance_threshold = 0.3  # Lower threshold for local embeddings

    async def retrieve_relevant_context(
        self,
        query_text: str,
        exclude_document_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant context from ChromaDB.

        Args:
            query_text: The text to find similar content for
            exclude_document_id: Document ID to exclude from results
            top_k: Number of relevant chunks to retrieve

        Returns:
            List of relevant context chunks with metadata
        """
        try:
            # Generate embedding for the query using Ollama
            query_embedding = await ollama_service.generate_embedding(query_text[:4000])

            if not query_embedding:
                return []

            # Search for similar content in ChromaDB
            results = await chroma_service.search(
                query_embedding=query_embedding,
                top_k=top_k * 2  # Get more results to filter
            )

            # Filter out chunks from the same document
            relevant_chunks = []
            for result in results:
                doc_id = result.get("metadata", {}).get("document_id", "")
                score = result.get("score", 0)

                # Skip if same document or low relevance
                if exclude_document_id and doc_id == exclude_document_id:
                    continue
                if score < self.context_relevance_threshold:
                    continue

                relevant_chunks.append({
                    "text": result.get("metadata", {}).get("text", ""),
                    "filename": result.get("metadata", {}).get("filename", "Unknown"),
                    "relevance_score": score,
                    "document_id": doc_id
                })

                if len(relevant_chunks) >= top_k:
                    break

            return relevant_chunks

        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return []

    def build_context_prompt(self, context_chunks: List[Dict]) -> str:
        """Build a context section from retrieved chunks."""
        if not context_chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(
                f"[Reference {i} - {chunk['filename']}]:\n"
                f"{chunk['text'][:400]}..."
            )

        return "\n\n".join(context_parts)

    async def analyze_with_rag(
        self,
        text: str,
        document_id: str,
        bias_types: List[BiasType] = None,
        use_context: bool = True
    ) -> Dict:
        """
        Perform RAG-enhanced bias analysis using Ollama.

        Args:
            text: The text to analyze
            document_id: Current document ID to exclude from context
            bias_types: Specific bias types to check for
            use_context: Whether to use RAG context

        Returns:
            Analysis results with RAG enhancement
        """
        context_chunks = []
        context_prompt = ""

        if use_context:
            try:
                context_chunks = await self.retrieve_relevant_context(
                    query_text=text[:2000],
                    exclude_document_id=document_id,
                    top_k=self.max_context_chunks
                )
                context_prompt = self.build_context_prompt(context_chunks)
            except Exception as e:
                print(f"Could not retrieve context: {e}")

        bias_types_str = ", ".join([bt.value for bt in bias_types]) if bias_types else "all types"

        # Build the analysis prompt
        if context_prompt:
            full_text = f"""REFERENCE CONTEXT FROM OTHER DOCUMENTS:
{context_prompt}

DOCUMENT TO ANALYZE:
{text[:5000]}

Analyze for {bias_types_str} of bias. Consider patterns from reference documents."""
        else:
            full_text = f"""DOCUMENT TO ANALYZE:
{text[:5000]}

Analyze for {bias_types_str} of bias."""

        try:
            # Use Ollama for analysis
            result = await ollama_service.analyze_bias(full_text, bias_types_str.split(", ") if bias_types else None)

            # Add RAG metadata
            result["rag_metadata"] = {
                "context_used": len(context_chunks) > 0,
                "num_reference_chunks": len(context_chunks),
                "reference_documents": list(set(
                    chunk.get("filename", "Unknown")
                    for chunk in context_chunks
                ))
            }

            return result

        except Exception as e:
            raise Exception(f"Error in RAG analysis: {str(e)}")

    async def semantic_qa(
        self,
        question: str,
        document_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Answer questions about bias using RAG with Ollama.

        Args:
            question: User's question about bias
            document_id: Optional document to focus on
            top_k: Number of relevant chunks to use

        Returns:
            Answer with supporting evidence
        """
        try:
            # Generate embedding for the question
            query_embedding = await ollama_service.generate_embedding(question)

            if not query_embedding:
                return {
                    "question": question,
                    "answer": "Could not generate embedding for search.",
                    "sources": [],
                    "num_sources_used": 0
                }

            # Build filter
            filter_dict = {"document_id": document_id} if document_id else None

            # Search in ChromaDB
            results = await chroma_service.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter=filter_dict
            )

            # Build context from results
            context_parts = []
            sources = []
            for result in results:
                text = result.get("metadata", {}).get("text", "")
                filename = result.get("metadata", {}).get("filename", "Unknown")
                context_parts.append(f"From {filename}:\n{text}")
                sources.append({
                    "filename": filename,
                    "document_id": result.get("metadata", {}).get("document_id"),
                    "relevance": result.get("score", 0)
                })

            context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

            # Generate answer using Ollama
            system_prompt = """You are a bias detection expert. Answer questions about bias patterns
using the provided context. Be specific and helpful. If no relevant context is available, say so."""

            user_prompt = f"""Context from analyzed documents:
{context}

Question: {question}

Provide a helpful answer based on the context above."""

            answer = await ollama_service.generate(user_prompt, system_prompt)

            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "num_sources_used": len(sources)
            }

        except Exception as e:
            raise Exception(f"Error in semantic QA: {str(e)}")


# Singleton instance
rag_service = RAGService()
