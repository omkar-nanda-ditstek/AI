from typing import Dict, List
from openai import OpenAI
import os
from datetime import datetime

class QuestionGenerator:
    def __init__(self):
        # Initialize OpenAI client with API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your-api-key-here':
            self.client = OpenAI(api_key=api_key)
            print("OpenAI API key loaded successfully")
        else:
            print("ERROR: No OpenAI API key found! Please set OPENAI_API_KEY environment variable.")
            self.client = None
        
        # 30-minute interview structure (6 questions, 5 minutes each)
        self.interview_structure = [
            {"phase": "introduction", "duration": 5, "count": 1},
            {"phase": "basics", "duration": 10, "count": 2}, 
            {"phase": "technical", "duration": 10, "count": 2},
            {"phase": "advanced", "duration": 5, "count": 1}
        ]
    
    def generate_questions(self, resume_data: Dict) -> List[Dict]:
        """Generate AI-powered dynamic questions for 30-minute interview"""
        print(f"Generating AI questions for resume data: {resume_data}")
        
        # Check if client is available
        if not self.client:
            raise Exception("OpenAI API key is required. Please set OPENAI_API_KEY environment variable.")
        
        # Extract key info from resume
        name = resume_data.get('name', 'Candidate')
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', 'Not specified')
        
        print(f"Candidate: {name}, Skills: {skills}, Experience: {experience}")
        
        # Create AI prompt
        prompt = self._create_ai_prompt(name, skills, experience)
        print("Generated AI prompt, calling OpenAI...")
        
        # Generate questions using AI only
        ai_questions = self._generate_ai_questions(prompt)
        
        if ai_questions and len(ai_questions) >= 6:
            print(f"Successfully generated {len(ai_questions)} AI questions")
            return ai_questions
        else:
            raise Exception("Failed to generate sufficient AI questions. Please check your OpenAI API key and try again.")
    
    def _create_ai_prompt(self, name: str, skills: List[str], experience: str) -> str:
        """Create AI prompt for question generation"""
        skills_text = ", ".join(skills[:5]) if skills else "general programming"
        
        prompt = f"""
Generate 6 interview questions for a 30-minute technical interview with {name}.

Candidate Profile:
- Skills: {skills_text}
- Experience: {experience}

Interview Structure (30 minutes total):
1. Introduction (5 min) - 1 question: Personal introduction and background
2. Basics (10 min) - 2 questions: Fundamental concepts and basic technical knowledge
3. Technical (10 min) - 2 questions: Specific to their tech stack and practical scenarios
4. Advanced (5 min) - 1 question: Problem-solving or system design

Requirements:
- Start with introduction question
- Progress from basic to advanced
- Focus on their specific skills: {skills_text}
- Each question should take about 5 minutes to answer
- Make questions practical and scenario-based

Return ONLY a JSON array with this exact format:
[
  {{"id": "intro_1", "type": "introduction", "question": "Tell me about yourself and your background in software development.", "duration": 5}},
  {{"id": "basic_1", "type": "basics", "question": "...", "duration": 5}},
  {{"id": "basic_2", "type": "basics", "question": "...", "duration": 5}},
  {{"id": "tech_1", "type": "technical", "question": "...", "duration": 5}},
  {{"id": "tech_2", "type": "technical", "question": "...", "duration": 5}},
  {{"id": "advanced_1", "type": "advanced", "question": "...", "duration": 5}}
]
"""
        return prompt
    
    def _generate_ai_questions(self, prompt: str) -> List[Dict]:
        """Generate questions using OpenAI API"""
        print("Calling OpenAI API...")
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer. Generate structured interview questions in JSON format only. Return valid JSON array without any markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        print("OpenAI API response received")
        
        # Extract and parse JSON response
        content = response.choices[0].message.content.strip()
        print(f"Raw AI response: {content}")
        
        # Clean up response (remove markdown formatting if present)
        if content.startswith('```json'):
            content = content[7:-3].strip()
        elif content.startswith('```'):
            content = content[3:-3].strip()
        
        import json
        questions = json.loads(content)
        
        # Validate questions format
        if not isinstance(questions, list) or len(questions) < 6:
            raise Exception(f"Invalid AI response: expected 6 questions, got {len(questions) if isinstance(questions, list) else 'invalid format'}")
        
        # Validate each question has required fields
        for i, q in enumerate(questions):
            if not all(key in q for key in ['id', 'type', 'question', 'duration']):
                raise Exception(f"Question {i+1} missing required fields: {q}")
        
        print(f"Successfully validated {len(questions)} AI questions")
        return questions
    
    def _generate_demo_questions(self, resume_data: Dict) -> List[Dict]:
        """Generate demo questions when AI is not available"""
        skills = resume_data.get('skills', [])
        primary_skill = skills[0] if skills else "programming"
        name = resume_data.get('name', 'Candidate')
        
        questions = [
            {
                "id": "intro_1",
                "type": "introduction", 
                "question": f"Hi {name}, tell me about yourself and your background in software development.",
                "duration": 5
            },
            {
                "id": "basic_1",
                "type": "basics",
                "question": "What programming languages are you most comfortable with and why?",
                "duration": 5
            },
            {
                "id": "basic_2", 
                "type": "basics",
                "question": "How do you approach debugging when you encounter an error in your code?",
                "duration": 5
            },
            {
                "id": "tech_1",
                "type": "technical",
                "question": f"Can you walk me through a project where you used {primary_skill}? What challenges did you face?",
                "duration": 5
            },
            {
                "id": "tech_2",
                "type": "technical", 
                "question": f"How would you optimize the performance of a {primary_skill} application?",
                "duration": 5
            },
            {
                "id": "advanced_1",
                "type": "advanced",
                "question": "Design a system that can handle 1 million users. What would be your approach?",
                "duration": 5
            }
        ]
        
        print(f"Using demo questions (personalized for {name} with {primary_skill})")
        return questions
    
