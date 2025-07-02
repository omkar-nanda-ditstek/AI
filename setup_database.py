#!/usr/bin/env python3

import asyncio
from database import DatabaseManager
from config import DatabaseConfig

async def setup_database_indexes():
    """Set up database indexes for better performance"""
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to MongoDB
        connected = await db_manager.connect()
        if not connected:
            print("Failed to connect to MongoDB")
            return
        
        print("Setting up database indexes...")
        
        # Resumes collection indexes
        resumes_collection = db_manager.db.resumes
        
        # Create indexes
        await resumes_collection.create_index("session_id")
        await resumes_collection.create_index("filename")
        await resumes_collection.create_index("created_at")
        await resumes_collection.create_index("parsed_data.email")
        await resumes_collection.create_index("parsed_data.name")
        await resumes_collection.create_index("parsed_data.skills")
        
        print("✓ Created indexes for resumes collection")
        
        # Interview sessions collection indexes
        sessions_collection = db_manager.db.interview_sessions
        
        await sessions_collection.create_index("session_id")
        await sessions_collection.create_index("resume_id")
        await sessions_collection.create_index("status")
        await sessions_collection.create_index("created_at")
        
        print("✓ Created indexes for interview_sessions collection")
        
        # List all indexes
        print("\\nCurrent indexes:")
        
        print("\\nResumes collection indexes:")
        async for index in resumes_collection.list_indexes():
            print(f"  - {index['name']}: {index.get('key', {})}")
        
        print("\\nInterview sessions collection indexes:")
        async for index in sessions_collection.list_indexes():
            print(f"  - {index['name']}: {index.get('key', {})}")
        
        print("\\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
    
    finally:
        await db_manager.disconnect()

async def create_sample_data():
    """Create some sample data for testing"""
    
    db_manager = DatabaseManager()
    
    try:
        connected = await db_manager.connect()
        if not connected:
            print("Failed to connect to MongoDB")
            return
        
        print("Creating sample data...")
        
        # Sample resume data
        sample_resumes = [
            {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB"],
                "experience": "3 years",
                "education": ["Bachelor's in Computer Science"],
                "projects": ["E-commerce Platform", "Task Management App"]
            },
            {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "+1-555-0456",
                "skills": ["Java", "Spring Boot", "MySQL", "Docker", "Kubernetes"],
                "experience": "5 years",
                "education": ["Master's in Software Engineering"],
                "projects": ["Microservices Architecture", "CI/CD Pipeline"]
            },
            {
                "name": "Mike Johnson",
                "email": "mike.johnson@example.com",
                "phone": "+1-555-0789",
                "skills": ["C#", ".NET", "Azure", "SQL Server", "Angular"],
                "experience": "4 years",
                "education": ["Bachelor's in Information Technology"],
                "projects": ["Cloud Migration", "Enterprise Web Application"]
            }
        ]
        
        # Save sample resumes
        for i, resume_data in enumerate(sample_resumes):
            resume_id = await db_manager.save_parsed_resume(
                resume_data=resume_data,
                filename=f"sample_resume_{i+1}.pdf",
                session_id=f"sample_session_{i+1}"
            )
            print(f"✓ Created sample resume {i+1} with ID: {resume_id}")
        
        print("\\nSample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
    
    finally:
        await db_manager.disconnect()

async def main():
    """Main setup function"""
    print("=== Database Setup ===")
    print(f"MongoDB URL: {DatabaseConfig.get_mongodb_url()}")
    print(f"Database Name: {DatabaseConfig.get_database_name()}")
    print()
    
    # Setup indexes
    await setup_database_indexes()
    
    print("\\n" + "="*50)
    
    # Create sample data
    create_samples = input("\\nDo you want to create sample data? (y/n): ").lower().strip()
    if create_samples == 'y':
        await create_sample_data()

if __name__ == "__main__":
    asyncio.run(main())