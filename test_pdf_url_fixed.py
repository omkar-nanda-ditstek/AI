#!/usr/bin/env python3

import requests
from resume_parser import ResumeParser
import unicodedata

def clean_text_for_print(text):
    """Clean text to handle encoding issues for printing"""
    replacements = {
        '\u25cf': '•',  # bullet point
        '\u2022': '•',  # bullet point
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2019': "'",  # right single quotation mark
        '\u201c': '"',  # left double quotation mark
        '\u201d': '"',  # right double quotation mark
        '\xa0': ' ',    # non-breaking space
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Keep only printable ASCII characters
    cleaned = ''.join(char for char in text if ord(char) < 127)
    return cleaned

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
            if isinstance(value, str):
                clean_value = clean_text_for_print(value)
                print(f"{key.upper()}: {clean_value}")
            else:
                print(f"{key.upper()}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pdf_from_url()