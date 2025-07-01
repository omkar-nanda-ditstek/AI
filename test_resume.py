#!/usr/bin/env python3

from resume_parser import ResumeParser
import sys

def test_resume_parser():
    parser = ResumeParser()
    
    # Test with a sample resume file
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            
            print(f"Testing with file: {filename}")
            result = parser.parse(content, filename)
            print(f"Parsed result: {result}")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python test_resume.py <resume_file_path>")

if __name__ == "__main__":
    test_resume_parser()