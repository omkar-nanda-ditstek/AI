#!/usr/bin/env python3

import asyncio
from database import DatabaseManager
from datetime import datetime

async def create_interview_collection():
    """Create interviews collection with proper schema and indexes"""
    
    print("=== Creating Interview Collection ===")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Connect to MongoDB
        print("1. Connecting to MongoDB...")
        connected = await db_manager.connect()
        if not connected:
            print("   Failed to connect to MongoDB")
            return
        print("   Connected successfully!")
        
        # Create interviews collection
        print("\n2. Creating interviews collection...")
        
        # Sample interview document structure
        sample_interview = {
            "session_id": "sample_session_001",
            "resume_id": None,  # ObjectId reference to resume
            "candidate_name": "John Doe",
            "candidate_email": "john.doe@example.com",
            "responses": [
                {
                    "question_id": "q1",
                    "question_text": "Tell me about yourself",
                    "question_type": "behavioral",
                    "answer": "I am a software developer with 3 years of experience...",
                    "answer_length": 65,
                    "time_taken": 120  # seconds
                },
                {
                    "question_id": "q2", 
                    "question_text": "What is your experience with Python?",
                    "question_type": "technical",
                    "answer": "I have been working with Python for 2 years...",
                    "answer_length": 45,
                    "time_taken": 90
                }
            ],
            "score": 85,
            "total_questions": 5,
            "answered_questions": 4,
            "completion_rate": 80.0,
            "total_time_taken": 900,  # seconds
            "interview_status": "completed",  # started, in_progress, completed, abandoned
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "submitted_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create the collection (it will be created when first document is inserted)
        collection = db_manager.db.interviews
        
        # Create indexes for better performance
        print("3. Creating indexes...")
        
        # Index on session_id for quick lookup
        await collection.create_index("session_id")
        print("   - Created index on session_id")
        
        # Index on resume_id for linking
        await collection.create_index("resume_id")
        print("   - Created index on resume_id")
        
        # Index on interview_status
        await collection.create_index("interview_status")
        print("   - Created index on interview_status")
        
        # Index on created_at for time-based queries
        await collection.create_index("created_at")
        print("   - Created index on created_at")
        
        # Compound index for resume and status
        await collection.create_index([("resume_id", 1), ("interview_status", 1)])
        print("   - Created compound index on resume_id + interview_status")
        
        print("\n4. Collection schema:")
        print("   - session_id: String (unique session identifier)")
        print("   - resume_id: ObjectId (reference to resume document)")
        print("   - candidate_name: String (candidate's name)")
        print("   - candidate_email: String (candidate's email)")
        print("   - responses: Array of response objects")
        print("     * question_id: String")
        print("     * question_text: String")
        print("     * question_type: String (technical, behavioral, etc.)")
        print("     * answer: String")
        print("     * answer_length: Number")
        print("     * time_taken: Number (seconds)")
        print("   - score: Number (0-100)")
        print("   - total_questions: Number")
        print("   - answered_questions: Number")
        print("   - completion_rate: Number (percentage)")
        print("   - total_time_taken: Number (seconds)")
        print("   - interview_status: String (started, in_progress, completed, abandoned)")
        print("   - started_at: DateTime")
        print("   - completed_at: DateTime")
        print("   - submitted_at: DateTime")
        print("   - created_at: DateTime")
        print("   - updated_at: DateTime")
        
        print("\n=== Interview Collection Created Successfully! ===")
        print("\nThe collection is ready to store interview data with:")
        print("✅ Proper document structure")
        print("✅ Performance indexes")
        print("✅ Resume linking capability")
        print("✅ Time tracking")
        print("✅ Status management")
        
    except Exception as e:
        print(f"Error creating collection: {e}")
    
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(create_interview_collection())