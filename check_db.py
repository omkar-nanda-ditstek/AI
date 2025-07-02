#!/usr/bin/env python3

from database import SyncDatabaseManager

def check_database():
    """Check what's in the MongoDB database"""
    
    db_manager = SyncDatabaseManager()
    
    if db_manager.connect():
        try:
            # Get resumes collection
            collection = db_manager.db.resumes
            
            # Count documents
            count = collection.count_documents({})
            print(f"Total resumes in database: {count}")
            
            # Get all resumes
            resumes = list(collection.find().sort("created_at", -1))
            
            print("\nResumes in database:")
            for i, resume in enumerate(resumes, 1):
                print(f"{i}. ID: {resume['_id']}")
                print(f"   Filename: {resume['filename']}")
                print(f"   Session: {resume['session_id']}")
                print(f"   Name: {resume['parsed_data'].get('name', 'N/A')}")
                print(f"   Email: {resume['parsed_data'].get('email', 'N/A')}")
                print(f"   Created: {resume['created_at']}")
                print()
            
        except Exception as e:
            print(f"Error checking database: {e}")
        
        finally:
            db_manager.disconnect()
    else:
        print("Failed to connect to MongoDB")

if __name__ == "__main__":
    check_database()