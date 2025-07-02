#!/usr/bin/env python3

import requests
import json
import time

def test_api_endpoints():
    """Test the FastAPI endpoints with MongoDB integration"""
    
    base_url = "http://localhost:8000"
    
    print("=== Testing API Endpoints ===")
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"   Health check: {response.json()}")
        else:
            print(f"   Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   Health check error: {e}")
    
    # Test get all resumes
    print("\\n2. Testing get all resumes...")
    try:
        response = requests.get(f"{base_url}/resumes?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['count']} resumes")
            if data['resumes']:
                print(f"   First resume: {data['resumes'][0]['parsed_data']['name']}")
        else:
            print(f"   Get resumes failed: {response.status_code}")
    except Exception as e:
        print(f"   Get resumes error: {e}")
    
    # Test search resumes
    print("\\n3. Testing search resumes...")
    try:
        search_data = {
            "name": "Alice",
            "skills": ["Python"]
        }
        response = requests.post(
            f"{base_url}/search-resumes",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   Search results: {data['count']} found")
            if data['resumes']:
                print(f"   First result: {data['resumes'][0]['parsed_data']['name']}")
        else:
            print(f"   Search failed: {response.status_code}")
    except Exception as e:
        print(f"   Search error: {e}")
    
    # Test file upload (simulate)
    print("\\n4. Testing file upload simulation...")
    print("   Note: Actual file upload requires a running server")
    print("   Use: curl -X POST 'http://localhost:8000/upload-resume' -F 'file=@resume.pdf'")
    
    print("\\n=== API Test Completed ===")

if __name__ == "__main__":
    print("Make sure the FastAPI server is running on localhost:8000")
    print("Start server with: python main.py")
    print()
    
    # Wait a moment for user to start server if needed
    input("Press Enter when server is ready...")
    
    test_api_endpoints()