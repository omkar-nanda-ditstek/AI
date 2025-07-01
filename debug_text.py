#!/usr/bin/env python3

import requests
from resume_parser import ResumeParser

def debug_text():
    url = "https://www.ongraph.com/wp-content/uploads/2018/02/Resume-Of-Node.js-Developer.docx.pdf"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        parser = ResumeParser()
        text = parser._extract_text(response.content, "nodejs_resume.pdf")
        
        print("=== FIRST 1000 CHARACTERS ===")
        print(repr(text[:1000]))
        print("\n=== FIRST 20 LINES ===")
        lines = text.split('\n')[:20]
        for i, line in enumerate(lines):
            print(f"{i:2d}: {repr(line)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_text()