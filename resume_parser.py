import PyPDF2
import docx
import re
import spacy
from pyresparser import ResumeParser as PyResumeParser
from typing import Dict, List
import tempfile
import os
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract
import pdfplumber


class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
    
    def parse(self, content: bytes, filename: str) -> Dict:
        text = self._extract_text(content, filename)
        
        # Use pyresparser for structured extraction
        parsed_data = self._parse_with_pyresparser(content, filename)
        
        # Enhance with spaCy NLP
        enhanced_data = self._enhance_with_spacy(text, parsed_data)
        
        return enhanced_data
    
    def _extract_text(self, content: bytes, filename: str) -> str:
        if filename.endswith('.pdf'):
            return self._extract_from_pdf(content)
        elif filename.endswith('.docx'):
            return self._extract_from_docx(content)
        return content.decode('utf-8')
    
    def _extract_from_pdf(self, content: bytes) -> str:
        from io import BytesIO
        
        # Method 1: PyPDF2
        try:
            reader = PyPDF2.PdfReader(BytesIO(content))
            text = ''.join(page.extract_text() for page in reader.pages)
            if text.strip():
                print("PDF extracted with PyPDF2")
                return text
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
        
        # Method 2: PyMuPDF (fitz)
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            if text.strip():
                print("PDF extracted with PyMuPDF")
                return text
        except Exception as e:
            print(f"PyMuPDF failed: {e}")
        
        # Method 3: pdfminer
        try:
            text = pdfminer_extract(BytesIO(content))
            if text.strip():
                print("PDF extracted with pdfminer")
                return text
        except Exception as e:
            print(f"pdfminer failed: {e}")
        
        # Method 4: pdfplumber
        try:
            with pdfplumber.open(BytesIO(content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if text.strip():
                print("PDF extracted with pdfplumber")
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")
        
        print("All PDF extraction methods failed")
        return ""
    
    def _extract_from_docx(self, content: bytes) -> str:
        from io import BytesIO
        doc = docx.Document(BytesIO(content))
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)
    
    def _parse_with_pyresparser(self, content: bytes, filename: str) -> Dict:
        try:
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp:
                tmp.write(content)
                tmp.flush()
                pyresparser = PyResumeParser(tmp.name)
                data = pyresparser.get_extracted_data()
                os.unlink(tmp.name)
                print(f"Pyresparser extracted: {data}")
                return data or {}
        except Exception as e:
            print(f"Pyresparser error: {e}")
            return {}
    
    def _enhance_with_spacy(self, text: str, base_data: Dict) -> Dict:
        print(f"Raw text preview: {text[:200]}...")
        enhanced = {
            "name": base_data.get('name') or self._extract_name_spacy(text),
            "email": base_data.get('email') or self._extract_email(text),
            "phone": base_data.get('mobile_number', '') or self._extract_phone(text),
            "skills": base_data.get('skills', []) or self._extract_skills_spacy(text),
            "experience": base_data.get('total_experience') or self._extract_experience(text),
            "education": base_data.get('degree', []) or self._extract_education(text),
            "projects": self._extract_projects_spacy(text)
        }
        print(f"Final enhanced data: {enhanced}")
        return enhanced
    
    def _extract_name_spacy(self, text: str) -> str:
        # Try multiple extraction methods
        
        # Method 1: spaCy NER
        if self.nlp:
            doc = self.nlp(text[:1000])
            for ent in doc.ents:
                if (ent.label_ == "PERSON" and 
                    len(ent.text.split()) >= 2 and 
                    self._is_valid_name(ent.text)):
                    return ent.text.strip()
        
        # Method 2: Pattern-based extraction
        name = self._extract_name_patterns(text)
        if name and name != "Unknown" and name != "Name not found in PDF":
            return name
        
        # Method 3: Fallback
        return self._extract_name_fallback(text)
    
    def _extract_name_patterns(self, text: str) -> str:
        # Method 1: Look for names at the very beginning (first few lines)
        lines = text.split('\n')
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            # Clean line of special characters but keep spaces
            clean_line = re.sub(r'[^a-zA-Z\s]', ' ', line).strip()
            clean_line = ' '.join(clean_line.split())  # Remove extra spaces
            
            if clean_line and self._is_valid_name(clean_line):
                return clean_line
        
        # Method 2: Look for "FIRSTNAME\nLASTNAME" pattern (like ELIANA\nSAUNDERS)
        for i in range(len(lines) - 1):
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip()
            
            # Clean both lines
            clean1 = re.sub(r'[^a-zA-Z]', '', line1)
            clean2 = re.sub(r'[^a-zA-Z]', '', line2)
            
            if (clean1 and clean2 and 
                clean1.isalpha() and clean2.isalpha() and
                clean1[0].isupper() and clean2[0].isupper() and
                3 <= len(clean1) <= 15 and 3 <= len(clean2) <= 15):
                
                full_name = f"{clean1} {clean2}"
                if self._is_valid_name(full_name):
                    return full_name
        
        # Method 3: Traditional patterns
        name_patterns = [
            r'Name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n.*(?:Developer|Engineer|Manager|Analyst)',
            r'I am ([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'My name is ([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if self._is_valid_name(match):
                    return match.strip()
        
        return self._extract_name_fallback(text)
    
    def _is_valid_name(self, name: str) -> bool:
        """Validate if text looks like a person's name"""
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        words = name.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # Each word should start with capital and be mostly alphabetic
        for word in words:
            if not word or not word[0].isupper() or not word.replace('.', '').isalpha():
                return False
        
        # Avoid common non-name patterns
        avoid_words = {
            'About', 'Profile', 'Summary', 'Resume', 'Developer', 'Engineer', 'Manager',
            'Technical', 'Skills', 'Personal', 'Professional', 'Experience', 'Education',
            'JavaScript', 'Angular', 'Node', 'HTML', 'CSS', 'Communication', 'Organization',
            'Senior', 'Junior', 'Lead', 'Principal', 'Staff', 'Contact', 'Information',
            'College', 'University', 'Bachelor', 'Master', 'Science', 'Arts', 'Commerce'
        }
        if any(word in avoid_words for word in words):
            return False
        
        # Avoid technical skill combinations and multi-line text
        if '\n' in name or '\xa0' in name:
            return False
        
        tech_combinations = ['Node JS', 'Angular JS', 'HTML CSS', 'JavaScript HTML', 'CSS JavaScript']
        if name in tech_combinations:
            return False
        
        # Check if it contains only technical terms
        tech_terms = {'JavaScript', 'HTML', 'CSS', 'Node', 'Angular', 'React', 'Python', 'Java'}
        name_words = set(words)
        if name_words.issubset(tech_terms):
            return False
        
        return True
    
    def _extract_name_fallback(self, text: str) -> str:
        # For this specific PDF format, try to find name in different sections
        
        # Look for patterns like "Name: John Doe" or similar
        name_indicators = ['name', 'candidate', 'applicant']
        for indicator in name_indicators:
            pattern = rf'{indicator}[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match and self._is_valid_name(match.group(1)):
                return match.group(1)
        
        # If still no name found, return a clear message
        return "[Name not clearly visible in PDF]"
    
    def _extract_email(self, text: str) -> str:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        if emails:
            # Prefer personal emails over company emails
            personal_emails = [email for email in emails if not any(domain in email.lower() for domain in ['company', 'corp', 'inc', 'ltd', 'ongraph', 'sales', 'info', 'contact'])]
            return personal_emails[0] if personal_emails else emails[0]
        
        return ""
    
    def _extract_skills_spacy(self, text: str) -> List[str]:
        # Technical skill indicators
        tech_indicators = {
            'languages': ['python', 'java', 'javascript', 'typescript', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'scala'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel', 'rails', 'express'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra', 'dynamodb'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'tools': ['git', 'jenkins', 'jira', 'postman', 'webpack']
        }
        
        found_skills = set()
        text_lower = text.lower()
        
        # 1. Extract specific patterns
        patterns = [
            r'\b\w+\.js\b',     # Framework.js
            r'\b\w+\.io\b',     # socket.io
            r'\b[A-Z]{2,5}\b',  # Acronyms
            r'\b\w*SQL\b',      # SQL variants
            r'\b\w*DB\b',       # Database names
            r'\bC\+\+\b',       # C++
            r'\bC#\b'           # C#
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                clean = match.lower().strip()
                if self._is_valid_tech_skill(clean):
                    found_skills.add(clean)
        
        # 2. Search for known technical terms
        all_tech_terms = []
        for category in tech_indicators.values():
            all_tech_terms.extend(category)
        
        for term in all_tech_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                found_skills.add(term)
        
        # 3. Extract from context (skills sections)
        skill_contexts = re.findall(
            r'(?:skills?|technologies?|tools?)[:\s]*([^\n.]+)', 
            text, re.IGNORECASE
        )
        
        for context in skill_contexts:
            items = re.split(r'[,;|•\-]', context)
            for item in items:
                clean_item = item.strip().lower()
                if self._is_valid_tech_skill(clean_item):
                    found_skills.add(clean_item)
        
        return sorted(list(found_skills))
    
    def _is_valid_tech_skill(self, skill: str) -> bool:
        """Validate if a term is likely a technical skill"""
        if not skill or len(skill) < 2 or len(skill) > 25:
            return False
        
        # Skip common English words
        common_words = {
            'and', 'the', 'with', 'for', 'in', 'on', 'at', 'to', 'of', 'is', 'are', 'was', 'were',
            'have', 'has', 'had', 'will', 'would', 'could', 'should', 'can', 'may', 'might',
            'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'our', 'their',
            'me', 'you', 'him', 'her', 'us', 'them', 'all', 'any', 'some', 'many', 'much',
            'years', 'experience', 'work', 'job', 'role', 'team', 'project', 'company',
            'about', 'also', 'very', 'well', 'good', 'great', 'best', 'high', 'low', 'fast'
        }
        
        if skill in common_words:
            return False
        
        # Must contain letters
        if not re.search(r'[a-zA-Z]', skill):
            return False
        
        # Skip pure numbers or dates
        if skill.isdigit() or re.match(r'^\d{4}$', skill):
            return False
        
        # Technical patterns that are likely valid
        tech_patterns = [
            r'\w+\.js$',      # Framework.js
            r'\w+\.io$',      # socket.io
            r'^[A-Z]{2,5}$',  # Acronyms
            r'\w*sql$',       # SQL variants
            r'\w*db$',        # Databases
        ]
        
        for pattern in tech_patterns:
            if re.match(pattern, skill, re.IGNORECASE):
                return True
        
        # If it contains dots or special chars, likely technical
        if '.' in skill or '+' in skill or '#' in skill:
            return True
        
        # Single word, reasonable length, mixed case or all lowercase
        if len(skill.split()) == 1 and 2 <= len(skill) <= 15:
            return True
        
        return False
    
    def _extract_experience(self, text: str) -> str:
        exp_patterns = [
            r'(\d+)\s*years?\s*experience',
            r'experience.*?(\d+)\s*years?',
            r'(\d{4})\s*-\s*(\d{4})',  # Date ranges like 2020-2024
            r'(\d+)\+?\s*years?\s*of\s*experience'
        ]
        
        # Try to find year ranges first
        date_matches = re.findall(r'(\d{4})\s*-\s*(\d{4})', text)
        if date_matches:
            total_years = 0
            for start, end in date_matches:
                years = int(end) - int(start)
                total_years += years
            if total_years > 0:
                return f"{total_years} years"
        
        # Try other patterns
        for pattern in exp_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return f"{match.group(1)} years"
        
        return "Not specified"
    
    def _extract_projects_spacy(self, text: str) -> List[str]:
        projects = []
        
        # Look for project sections with various headers
        project_patterns = [
            r'projects?:?\s*(.*?)(?:experience|education|skills|certifications?|awards?|$)',
            r'personal\s+projects?:?\s*(.*?)(?:experience|education|skills|$)',
            r'key\s+projects?:?\s*(.*?)(?:experience|education|skills|$)'
        ]
        
        for pattern in project_patterns:
            match = re.search(pattern, text.lower(), re.DOTALL)
            if match:
                project_text = match.group(1)
                # Extract bullet points or numbered items
                project_items = re.findall(r'[•\-\*\d+\.]\s*([^\n•\-\*]+)', project_text)
                projects.extend([p.strip() for p in project_items if len(p.strip()) > 10])
        
        # Also look for standalone project descriptions
        if not projects:
            # Look for lines that might be project titles
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in ['developed', 'built', 'created', 'designed', 'implemented']):
                    if len(line.strip()) > 20:
                        projects.append(line.strip())
        
        return projects[:5]  # Return top 5 projects
    
    def _extract_phone(self, text: str) -> str:
        phone_patterns = [
            r'\+?\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',
            r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',
            r'\d{10}'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return ""
    
    def _extract_education(self, text: str) -> List[str]:
        education = []
        edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'institute']
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in edu_keywords):
                if len(line.strip()) > 10:
                    education.append(line.strip())
        
        return education[:3]