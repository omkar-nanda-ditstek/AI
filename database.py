from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional
import os
from config import DatabaseConfig

class DatabaseManager:
    def __init__(self, connection_string: str = None, database_name: str = None):
        # Use config or provided values
        self.connection_string = connection_string or DatabaseConfig.get_mongodb_url()
        self.database_name = database_name or DatabaseConfig.get_database_name()
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            await self.client.admin.command('ping')
            print("Connected to MongoDB successfully!")
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
    
    async def save_parsed_resume(self, resume_data: Dict, filename: str, session_id: str = None) -> str:
        """Save parsed resume data to MongoDB"""
        try:
            collection = self.db.resumes
            
            # Prepare document
            document = {
                "filename": filename,
                "session_id": session_id,
                "parsed_data": resume_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert document
            result = await collection.insert_one(document)
            print(f"Resume data saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error saving resume data: {e}")
            raise e
    
    async def get_resume_by_id(self, resume_id: str) -> Optional[Dict]:
        """Get resume data by ID"""
        try:
            from bson import ObjectId
            collection = self.db.resumes
            
            result = await collection.find_one({"_id": ObjectId(resume_id)})
            if result:
                result["_id"] = str(result["_id"])
            return result
            
        except Exception as e:
            print(f"Error retrieving resume: {e}")
            return None
    
    async def get_resumes_by_session(self, session_id: str) -> List[Dict]:
        """Get all resumes for a session"""
        try:
            collection = self.db.resumes
            cursor = collection.find({"session_id": session_id})
            
            results = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                results.append(document)
            
            return results
            
        except Exception as e:
            print(f"Error retrieving resumes by session: {e}")
            return []
    
    async def save_interview_session(self, session_data: Dict) -> str:
        """Save interview session data"""
        try:
            collection = self.db.interview_sessions
            
            document = {
                **session_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await collection.insert_one(document)
            print(f"Interview session saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error saving interview session: {e}")
            raise e
    
    async def update_interview_session(self, session_id: str, update_data: Dict) -> bool:
        """Update interview session"""
        try:
            from bson import ObjectId
            collection = self.db.interview_sessions
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating interview session: {e}")
            return False
    
    async def get_all_resumes(self, limit: int = 50, skip: int = 0) -> List[Dict]:
        """Get all resumes with pagination"""
        try:
            collection = self.db.resumes
            cursor = collection.find().skip(skip).limit(limit).sort("created_at", -1)
            
            results = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                results.append(document)
            
            return results
            
        except Exception as e:
            print(f"Error retrieving all resumes: {e}")
            return []
    
    async def search_resumes(self, search_criteria: Dict) -> List[Dict]:
        """Search resumes based on criteria"""
        try:
            collection = self.db.resumes
            
            # Build search query
            query = {}
            
            if "name" in search_criteria:
                query["parsed_data.name"] = {"$regex": search_criteria["name"], "$options": "i"}
            
            if "skills" in search_criteria:
                query["parsed_data.skills"] = {"$in": search_criteria["skills"]}
            
            if "email" in search_criteria:
                query["parsed_data.email"] = {"$regex": search_criteria["email"], "$options": "i"}
            
            cursor = collection.find(query).sort("created_at", -1)
            
            results = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                results.append(document)
            
            return results
            
        except Exception as e:
            print(f"Error searching resumes: {e}")
            return []

# Synchronous version for non-async contexts
class SyncDatabaseManager:
    def __init__(self, connection_string: str = None, database_name: str = None):
        # Use config or provided values
        self.connection_string = connection_string or DatabaseConfig.get_mongodb_url()
        self.database_name = database_name or DatabaseConfig.get_database_name()
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            print("Connected to MongoDB successfully!")
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
    
    def save_parsed_resume(self, resume_data: Dict, filename: str, session_id: str = None) -> str:
        """Save parsed resume data to MongoDB"""
        try:
            collection = self.db.resumes
            
            document = {
                "filename": filename,
                "session_id": session_id,
                "parsed_data": resume_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = collection.insert_one(document)
            print(f"Resume data saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error saving resume data: {e}")
            raise e