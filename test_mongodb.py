#!/usr/bin/env python3

import asyncio
import requests
from database import DatabaseManager, SyncDatabaseManager
from resume_parser import ResumeParser

async def test_mongodb_integration():
    """Test MongoDB integration with resume parsing"""
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Connect to MongoDB
    connected = await db_manager.connect()
    if not connected:
        print("Failed to connect to MongoDB. Make sure MongoDB is running.")
        return
    
    try:
        # Test with the PDF URL
        url = "https://www.ongraph.com/wp-content/uploads/2018/02/Resume-Of-Node.js-Developer.docx.pdf"
        
        print("Downloading PDF...")
        response = requests.get(url)
        response.raise_for_status()
        
        print("Parsing resume...")
        parser = ResumeParser()
        
        # Clean the content to avoid encoding issues
        def clean_text_for_parsing(text):
            replacements = {
                '\u25cf': '•',
                '\u2022': '•',
                '\u2013': '-',
                '\u2014': '-',
                '\u2019': "'",
                '\u201c': '"',
                '\u201d': '"',
                '\xa0': ' ',
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return ''.join(char for char in text if ord(char) < 127)
        
        # Parse the resume
        try:
            parsed_data = parser.parse(response.content, "nodejs_resume.pdf")
            
            # Clean the parsed data for MongoDB storage
            if isinstance(parsed_data.get('name'), str):
                parsed_data['name'] = clean_text_for_parsing(parsed_data['name'])
            
            print("\\n=== PARSED DATA ===")
            for key, value in parsed_data.items():
                if isinstance(value, str):
                    clean_value = clean_text_for_parsing(value)
                    print(f"{key.upper()}: {clean_value}")
                else:
                    print(f"{key.upper()}: {value}")
            
            # Save to MongoDB
            print("\\nSaving to MongoDB...")
            resume_id = await db_manager.save_parsed_resume(
                resume_data=parsed_data,
                filename="nodejs_resume.pdf",
                session_id="test_session_001"
            )
            
            print(f"Resume saved with ID: {resume_id}")
            
            # Retrieve the saved resume
            print("\\nRetrieving saved resume...")
            saved_resume = await db_manager.get_resume_by_id(resume_id)
            
            if saved_resume:
                print("Successfully retrieved resume from MongoDB:")
                print(f"ID: {saved_resume['_id']}")
                print(f"Filename: {saved_resume['filename']}")
                print(f"Session ID: {saved_resume['session_id']}")
                print(f"Created at: {saved_resume['created_at']}")
                print(f"Name: {saved_resume['parsed_data'].get('name', 'N/A')}")
                print(f"Email: {saved_resume['parsed_data'].get('email', 'N/A')}")
                print(f"Skills: {saved_resume['parsed_data'].get('skills', [])}")
            
            # Test search functionality
            print("\\nTesting search functionality...")
            search_results = await db_manager.search_resumes({"name": "Node"})
            print(f"Search results for 'Node': {len(search_results)} found")
            
            # Get all resumes
            print("\\nGetting all resumes...")
            all_resumes = await db_manager.get_all_resumes(limit=10)
            print(f"Total resumes in database: {len(all_resumes)}")
            
        except Exception as parse_error:
            print(f"Error during parsing: {parse_error}")
            
            # Save a simple test document instead
            test_data = {
                "name": "Test User",
                "email": "test@example.com",
                "phone": "+1234567890",
                "skills": ["Python", "MongoDB", "FastAPI"],
                "experience": "2 years",
                "education": ["Bachelor's Degree"],
                "projects": ["Resume Parser Project"]
            }
            
            print("Saving test data to MongoDB...")
            resume_id = await db_manager.save_parsed_resume(
                resume_data=test_data,
                filename="test_resume.pdf",
                session_id="test_session_002"
            )
            print(f"Test data saved with ID: {resume_id}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Disconnect from MongoDB
        await db_manager.disconnect()

def test_sync_mongodb():
    """Test synchronous MongoDB operations"""
    print("\\n=== Testing Synchronous MongoDB Operations ===")
    
    db_manager = SyncDatabaseManager()
    
    if db_manager.connect():
        try:
            # Save test data
            test_data = {
                "name": "Sync Test User",
                "email": "sync@example.com",
                "phone": "+9876543210",
                "skills": ["JavaScript", "Node.js", "Express"],
                "experience": "3 years",
                "education": ["Master's Degree"],
                "projects": ["E-commerce Platform"]
            }
            
            resume_id = db_manager.save_parsed_resume(
                resume_data=test_data,
                filename="sync_test_resume.pdf",
                session_id="sync_test_session"
            )
            
            print(f"Sync test data saved with ID: {resume_id}")
            
        except Exception as e:
            print(f"Sync test error: {e}")
        
        finally:
            db_manager.disconnect()

if __name__ == "__main__":
    print("=== MongoDB Integration Test ===")
    print("Make sure MongoDB is running on localhost:27017")
    print()
    
    # Test async operations
    asyncio.run(test_mongodb_integration())
    
    # Test sync operations
    test_sync_mongodb()
    
    print("\\nMongoDB integration test completed!")