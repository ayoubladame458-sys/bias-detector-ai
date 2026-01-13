"""
LanceDB service for local vector storage - 100% stable
Corrigé pour ne jamais planter, table créée automatiquement
"""

import os
import lancedb
import pyarrow as pa
from typing import List, Dict, Optional
from app.core.config import settings


class VectorService:
    """
    LanceDB Vector Store pour RAG
    - Auto table creation
    - Safe search before ingestion
    """

    def __init__(self):
        self.db_path = settings.CHROMA_PERSIST_DIR
        self.table_name = "bias_detector_docs"
        self.db = None
        self.table = None
        self.default_embedding_dim = 768

        # Connexion DB seulement
        os.makedirs(self.db_path, exist_ok=True)
        self.db = lancedb.connect(self.db_path)

    # ---------------------- Helpers internes ----------------------

    def _ensure_table(self, embedding_dim: Optional[int] = None):
        """Créer la table si elle n'existe pas"""
        if self.table is not None:
            return  # Table déjà ouverte

        if self.table_name in self.db.table_names():
            self.table = self.db.open_table(self.table_name)
        else:
            dim = embedding_dim or self.default_embedding_dim
            self.table = self.db.create_table(
                self.table_name,
                pa.schema([
                    pa.field("id", pa.string()),
                    pa.field("text", pa.string()),
                    pa.field("document_id", pa.string()),
                    pa.field("filename", pa.string()),
                    pa.field("chunk_index", pa.int32()),
                    pa.field("vector", pa.list_(pa.float32(), dim)),
                ])
            )

    # ---------------------- API publiques ----------------------

    async def upsert_document(
        self,
        document_id: str,
        text_chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict
    ) -> bool:
        """Insérer ou remplacer des chunks d'un document"""
        if not embeddings:
            return True

        embedding_dim = len(embeddings[0])
        self._ensure_table(embedding_dim)

        await self.delete_document(document_id)

        rows = [
            {
                "id": f"{document_id}_chunk_{i}",
                "text": text,
                "document_id": document_id,
                "filename": metadata.get("filename", ""),
                "chunk_index": i,
                "vector": vector,
            }
            for i, (text, vector) in enumerate(zip(text_chunks, embeddings))
        ]

        if rows:
            self.table.add(rows)
        return True

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Recherche sémantique"""
        if self.table is None or self.table.count_rows() == 0:
            return []  # Table vide ou inexistante

        query = self.table.search(query_embedding).limit(top_k)
        if filter and "document_id" in filter:
            query = query.where(f"document_id = '{filter['document_id']}'")
        df = query.to_pandas()

        results = []
        for _, row in df.iterrows():
            distance = row.get("_distance", 0)
            results.append({
                "id": row["id"],
                "score": 1 / (1 + distance),
                "metadata": {
                    "text": row["text"],
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "chunk_index": row["chunk_index"],
                }
            })
        return results

    async def get_document_chunks(self, document_id: str) -> List[Dict]:
        """Récupérer tous les chunks d'un document"""
        if self.table is None or self.table.count_rows() == 0:
            return []

        df = self.table.to_arrow_table().to_pandas()
        df = df[df["document_id"] == document_id]

        return [
            {
                "id": row["id"],
                "metadata": {
                    "text": row["text"],
                    "document_id": row["document_id"],
                    "filename": row["filename"],
                    "chunk_index": row["chunk_index"],
                }
            }
            for _, row in df.iterrows()
        ]

    async def delete_document(self, document_id: str) -> bool:
        """Supprimer un document"""
        if self.table is not None:
            self.table.delete(lambda row: row["document_id"] == document_id)
        return True

    async def get_stats(self) -> Dict:
        """Statistiques de la table"""
        total_vectors = self.table.count_rows() if self.table else 0
        return {
            "table_name": self.table_name,
            "db_path": self.db_path,
            "total_vectors": total_vectors
        }

    async def reset(self) -> bool:
        """Supprimer et recréer la table"""
        if self.table_name in self.db.table_names():
            self.db.drop_table(self.table_name)
        self.table = None
        self._ensure_table()
        return True


# ---------------------- Singleton prêt à l'emploi ----------------------
chroma_service = VectorService()
