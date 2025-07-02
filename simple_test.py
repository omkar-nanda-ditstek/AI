#!/usr/bin/env python3

import requests
import PyPDF2
from io import BytesIO

def simple_pdf_test():
    url = "https://www.ongraph.com/wp-content/uploads/2018/02/Resume-Of-Node.js-Developer.docx.pdf"
    
    try:
        print("Downloading PDF...")
        response = requests.get(url)
        response.raise_for_status()
        
        print("Extracting text from PDF...")
        reader = PyPDF2.PdfReader(BytesIO(response.content))
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        
        # Clean text for display
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        
        print("\n=== EXTRACTED TEXT ===")
        print(clean_text[:1000])  # First 1000 characters
        
        print("\n=== BASIC PARSING ===")
        
        # Extract email
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, clean_text)
        print(f"EMAIL: {emails[0] if emails else 'Not found'}")
        
        # Extract phone
        phone_pattern = r'\+?\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}'
        phones = re.findall(phone_pattern, clean_text)
        print(f"PHONE: {phones[0] if phones else 'Not found'}")
        
        # Look for skills
        skills_section = re.search(r'(?:skills?|technologies?)[:\s]*(.*?)(?:experience|education|$)', clean_text, re.IGNORECASE | re.DOTALL)
        if skills_section:
            skills_text = skills_section.group(1)[:200]
            print(f"SKILLS SECTION: {skills_text}")
        
        print("\nPDF parsing completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_pdf_test()