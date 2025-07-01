#!/usr/bin/env python3

from resume_parser import ResumeParser
import os

def test_sample_resumes():
    parser = ResumeParser()
    samples_dir = "samples"
    
    for filename in os.listdir(samples_dir):
        if filename.endswith(('.pdf', '.docx')):
            filepath = os.path.join(samples_dir, filename)
            print(f"\n{'='*50}")
            print(f"Testing: {filename}")
            print('='*50)
            
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                # Extract text first to see structure
                text = parser._extract_text(content, filename)
                print(f"Text preview: {text[:300]}...")
                
                # Parse resume
                result = parser.parse(content, filename)
                print(f"\nNAME: {result['name']}")
                print(f"EMAIL: {result['email']}")
                print(f"PHONE: {result['phone']}")
                print(f"SKILLS: {result['skills'][:10]}...")  # First 10 skills
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    test_sample_resumes()