#!/usr/bin/env python3

import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8001/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_upload():
    """Test file upload with a simple text file"""
    try:
        # Create a simple test resume file
        test_content = """
John Doe
Email: john.doe@example.com
Phone: +1-555-0123

SKILLS:
- Python
- JavaScript
- MongoDB
- FastAPI

EXPERIENCE:
Software Developer - 3 years

EDUCATION:
Bachelor's in Computer Science
"""
        
        # Save to a temporary file
        with open("test_resume.txt", "w") as f:
            f.write(test_content)
        
        # Upload the file
        with open("test_resume.txt", "rb") as f:
            files = {"file": ("test_resume.txt", f, "text/plain")}
            response = requests.post("http://localhost:8001/upload-resume", files=files)
        
        print(f"Upload status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Session ID: {data.get('session_id')}")
            print(f"Resume ID: {data.get('resume_id')}")
            print(f"Interview ID: {data.get('interview_id')}")
            print(f"Parsed name: {data.get('parsed_resume', {}).get('name')}")
            print(f"Parsed email: {data.get('parsed_resume', {}).get('email')}")
        else:
            print(f"Upload failed: {response.text}")
        
        # Clean up
        import os
        if os.path.exists("test_resume.txt"):
            os.remove("test_resume.txt")
            
    except Exception as e:
        print(f"Upload test failed: {e}")

def test_get_resumes():
    """Test getting all resumes"""
    try:
        response = requests.get("http://localhost:8001/resumes?limit=5")
        print(f"Get resumes status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('count', 0)} resumes")
            for i, resume in enumerate(data.get('resumes', [])[:3]):
                name = resume.get('parsed_data', {}).get('name', 'Unknown')
                filename = resume.get('filename', 'Unknown')
                print(f"  {i+1}. {name} - {filename}")
    except Exception as e:
        print(f"Get resumes test failed: {e}")

if __name__ == "__main__":
    print("=== Testing API Endpoints ===")
    print()
    
    print("1. Testing health endpoint...")
    if test_health():
        print("Health check passed")
    else:
        print("Health check failed")
        exit(1)
    
    print()
    print("2. Testing file upload...")
    test_upload()
    
    print()
    print("3. Testing get resumes...")
    test_get_resumes()
    
    print()
    print("=== Test completed ===")