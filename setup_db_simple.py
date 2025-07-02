#!/usr/bin/env python3

import asyncio
from database import DatabaseManager

async def setup_database():
    """Simple database setup without special characters"""
    
    db_manager = DatabaseManager()
    
    try:
        connected = await db_manager.connect()
        if not connected:
            print("Failed to connect to MongoDB")
            return
        
        print("Setting up database indexes...")
        
        # Resumes collection indexes
        resumes_collection = db_manager.db.resumes
        await resumes_collection.create_index("session_id")
        await resumes_collection.create_index("filename")
        await resumes_collection.create_index("created_at")
        await resumes_collection.create_index("parsed_data.email")
        await resumes_collection.create_index("parsed_data.name")
        
        print("Created indexes for resumes collection")
        
        # Interview sessions collection indexes
        sessions_collection = db_manager.db.interview_sessions
        await sessions_collection.create_index("session_id")
        await sessions_collection.create_index("resume_id")
        await sessions_collection.create_index("status")
        await sessions_collection.create_index("created_at")
        
        print("Created indexes for interview_sessions collection")
        
        # Create sample data
        print("Creating sample data...")
        
        sample_resumes = [
            {
                "name": "Alice Johnson",
                "email": "alice.johnson@email.com",
                "phone": "+1-555-0101",
                "skills": ["Python", "FastAPI", "MongoDB", "React"],
                "experience": "2 years",
                "education": ["Bachelor in Computer Science"],
                "projects": ["Web Application", "API Development"]
            },
            {
                "name": "Bob Wilson",
                "email": "bob.wilson@email.com", 
                "phone": "+1-555-0202",
                "skills": ["JavaScript", "Node.js", "Express", "MySQL"],
                "experience": "4 years",
                "education": ["Master in Software Engineering"],
                "projects": ["E-commerce Platform", "Real-time Chat App"]
            }
        ]
        
        for i, resume_data in enumerate(sample_resumes):
            resume_id = await db_manager.save_parsed_resume(
                resume_data=resume_data,
                filename=f"sample_resume_{i+1}.pdf",
                session_id=f"sample_session_{i+1}"
            )
            print(f"Created sample resume {i+1} with ID: {resume_id}")
        
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_database())