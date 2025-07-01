#!/usr/bin/env python3

import requests
from resume_parser import ResumeParser

def test_pdf_from_url():
    url = "https://www.ongraph.com/wp-content/uploads/2018/02/Resume-Of-Node.js-Developer.docx.pdf"
    
    try:
        print("Downloading PDF...")
        response = requests.get(url)
        response.raise_for_status()
        
        print("Parsing resume...")
        parser = ResumeParser()
        result = parser.parse(response.content, "nodejs_resume.pdf")
        
        print("\n=== PARSED RESUME DATA ===")
        for key, value in result.items():
            print(f"{key.upper()}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pdf_from_url()