"""
MongoDB database service for persistent storage of analyses and documents
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
from datetime import datetime
from app.core.config import settings
import uuid


class DatabaseService:
    """Service for MongoDB operations - stores analysis results and document metadata"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.documents_collection = None
        self.analyses_collection = None
        self.connected = False

    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongo_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[getattr(settings, 'MONGODB_DATABASE', 'biasdetector')]

            # Initialize collections
            self.documents_collection = self.db["documents"]
            self.analyses_collection = self.db["analyses"]

            # Create indexes
            await self.documents_collection.create_index("document_id", unique=True)
            await self.analyses_collection.create_index("document_id")
            await self.analyses_collection.create_index("analyzed_at")

            self.connected = True
            print("Connected to MongoDB successfully")

        except Exception as e:
            print(f"Warning: Could not connect to MongoDB: {str(e)}")
            print("Running without persistent storage - analyses will not be saved")
            self.connected = False

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.connected = False

    # ==================== Document Operations ====================

    async def save_document(self, document_data: Dict) -> Optional[str]:
        """
        Save document metadata to database

        Args:
            document_data: Document information to save

        Returns:
            Document ID if successful, None otherwise
        """
        if not self.connected:
            return document_data.get("document_id")

        try:
            document_data["created_at"] = datetime.utcnow()
            document_data["updated_at"] = datetime.utcnow()

            await self.documents_collection.update_one(
                {"document_id": document_data["document_id"]},
                {"$set": document_data},
                upsert=True
            )
            return document_data["document_id"]

        except Exception as e:
            print(f"Error saving document: {str(e)}")
            return None

    async def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document metadata by ID"""
        if not self.connected:
            return None

        try:
            document = await self.documents_collection.find_one(
                {"document_id": document_id}
            )
            if document:
                document["_id"] = str(document["_id"])
            return document

        except Exception as e:
            print(f"Error retrieving document: {str(e)}")
            return None

    async def get_all_documents(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """Get all documents with pagination"""
        if not self.connected:
            return []

        try:
            cursor = self.documents_collection.find().skip(skip).limit(limit).sort(
                "created_at", -1
            )
            documents = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(doc)
            return documents

        except Exception as e:
            print(f"Error retrieving documents: {str(e)}")
            return []

    async def delete_document(self, document_id: str) -> bool:
        """Delete document and its analyses"""
        if not self.connected:
            return True

        try:
            # Delete document
            await self.documents_collection.delete_one({"document_id": document_id})
            # Delete associated analyses
            await self.analyses_collection.delete_many({"document_id": document_id})
            return True

        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False

    # ==================== Analysis Operations ====================

    async def save_analysis(self, analysis_data: Dict) -> Optional[str]:
        """
        Save analysis result to database

        Args:
            analysis_data: Analysis result to save

        Returns:
            Analysis ID if successful, None otherwise
        """
        if not self.connected:
            return None

        try:
            analysis_id = str(uuid.uuid4())
            analysis_data["analysis_id"] = analysis_id
            analysis_data["created_at"] = datetime.utcnow()

            await self.analyses_collection.insert_one(analysis_data)

            # Update document to mark as analyzed
            await self.documents_collection.update_one(
                {"document_id": analysis_data.get("document_id")},
                {
                    "$set": {
                        "analyzed": True,
                        "last_analysis_id": analysis_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            return analysis_id

        except Exception as e:
            print(f"Error saving analysis: {str(e)}")
            return None

    async def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis by ID"""
        if not self.connected:
            return None

        try:
            analysis = await self.analyses_collection.find_one(
                {"analysis_id": analysis_id}
            )
            if analysis:
                analysis["_id"] = str(analysis["_id"])
            return analysis

        except Exception as e:
            print(f"Error retrieving analysis: {str(e)}")
            return None

    async def get_analyses_for_document(
        self,
        document_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get all analyses for a specific document"""
        if not self.connected:
            return []

        try:
            cursor = self.analyses_collection.find(
                {"document_id": document_id}
            ).sort("analyzed_at", -1).limit(limit)

            analyses = []
            async for analysis in cursor:
                analysis["_id"] = str(analysis["_id"])
                analyses.append(analysis)
            return analyses

        except Exception as e:
            print(f"Error retrieving analyses: {str(e)}")
            return []

    async def get_latest_analysis(self, document_id: str) -> Optional[Dict]:
        """Get the most recent analysis for a document"""
        if not self.connected:
            return None

        try:
            analysis = await self.analyses_collection.find_one(
                {"document_id": document_id},
                sort=[("analyzed_at", -1)]
            )
            if analysis:
                analysis["_id"] = str(analysis["_id"])
            return analysis

        except Exception as e:
            print(f"Error retrieving latest analysis: {str(e)}")
            return None

    async def get_all_analyses(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """Get all analyses with pagination"""
        if not self.connected:
            return []

        try:
            cursor = self.analyses_collection.find().skip(skip).limit(limit).sort(
                "analyzed_at", -1
            )
            analyses = []
            async for analysis in cursor:
                analysis["_id"] = str(analysis["_id"])
                analyses.append(analysis)
            return analyses

        except Exception as e:
            print(f"Error retrieving all analyses: {str(e)}")
            return []

    # ==================== Statistics ====================

    async def get_statistics(self) -> Dict:
        """Get overall statistics"""
        if not self.connected:
            return {
                "total_documents": 0,
                "total_analyses": 0,
                "database_connected": False
            }

        try:
            total_docs = await self.documents_collection.count_documents({})
            total_analyses = await self.analyses_collection.count_documents({})

            # Get bias type distribution
            pipeline = [
                {"$unwind": "$bias_instances"},
                {"$group": {"_id": "$bias_instances.type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            bias_distribution = []
            async for item in self.analyses_collection.aggregate(pipeline):
                bias_distribution.append({
                    "type": item["_id"],
                    "count": item["count"]
                })

            # Get average bias score
            avg_pipeline = [
                {"$group": {"_id": None, "avg_score": {"$avg": "$overall_score"}}}
            ]
            avg_result = await self.analyses_collection.aggregate(avg_pipeline).to_list(1)
            avg_score = avg_result[0]["avg_score"] if avg_result else 0

            return {
                "total_documents": total_docs,
                "total_analyses": total_analyses,
                "average_bias_score": round(avg_score, 3) if avg_score else 0,
                "bias_distribution": bias_distribution,
                "database_connected": True
            }

        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {
                "total_documents": 0,
                "total_analyses": 0,
                "database_connected": False,
                "error": str(e)
            }


# Singleton instance
database_service = DatabaseService()
