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
        print(f"Generating questions for resume data: {resume_data}")
        
        # Extract key info from resume
        name = resume_data.get('name', 'Candidate')
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', 'Not specified')
        
        print(f"Candidate: {name}, Skills: {skills}, Experience: {experience}")
        
        # Try AI first, fallback to demo questions
        if self.client:
            try:
                prompt = self._create_ai_prompt(name, skills, experience)
                print("Generated AI prompt, calling OpenAI...")
                ai_questions = self._generate_ai_questions(prompt)
                
                if ai_questions and len(ai_questions) >= 6:
                    print(f"Successfully generated {len(ai_questions)} AI questions")
                    return ai_questions
            except Exception as e:
                print(f"OpenAI API failed: {str(e)}")
                print("Falling back to demo questions...")
        
        # Fallback to demo questions
        return self._generate_demo_questions(resume_data)
    
    def _create_ai_prompt(self, name: str, skills: List[str], experience: str) -> str:
        """Create AI prompt for question generation"""
        skills_text = ", ".join(skills[:5]) if skills else "general programming"
        
        prompt = f"""
You are an experienced, friendly technical interviewer conducting a 30-minute interview with {name}. Generate 6 conversational, human-like questions that feel natural and engaging.

Candidate Profile:
- Name: {name}
- Skills: {skills_text}
- Experience: {experience}

Interview Flow (30 minutes total):
1. Warm Introduction (5 min) - 1 question: Personal, welcoming introduction
2. Technical Foundation (10 min) - 2 questions: Core concepts with personal touch
3. Practical Experience (10 min) - 2 questions: Real-world scenarios and projects
4. Problem Solving (5 min) - 1 question: Thoughtful challenge or design question

Question Style Requirements:
- Sound like a human interviewer, not robotic
- Use conversational language ("I'd love to hear about...", "That's interesting...", "Could you walk me through...")
- Show genuine interest and curiosity
- Reference their specific skills naturally
- Use their name appropriately
- Ask follow-up style questions
- Make them feel comfortable and engaged
- Avoid generic corporate speak

Return ONLY a JSON array with this exact format:
[
  {{"id": "intro_1", "type": "introduction", "question": "Hi {name}! Thanks for taking the time to speak with me today. I'm excited to learn more about you. Could you start by telling me about your journey into software development and what initially sparked your interest?", "duration": 5}},
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
                {"role": "system", "content": "You are a warm, experienced technical interviewer who makes candidates feel comfortable while asking insightful questions. Generate natural, conversational interview questions that sound human and engaging. Return only valid JSON array without markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
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
        """Generate human-like conversational questions when AI is not available"""
        skills = resume_data.get('skills', [])
        primary_skill = skills[0] if skills else "programming"
        secondary_skill = skills[1] if len(skills) > 1 else "development"
        name = resume_data.get('name', 'Candidate')
        experience = resume_data.get('experience', [])
        
        # Get years of experience if available
        exp_years = "a few years" 
        if experience and len(experience) > 0:
            exp_years = f"{len(experience)} years"
        
        questions = [
            {
                "id": "intro_1",
                "type": "introduction", 
                "question": f"Hi {name}! Thanks for taking the time to speak with me today. I'm excited to learn more about you. Could you start by telling me a bit about yourself and what drew you to software development? I'd love to hear about your journey so far.",
                "duration": 5
            },
            {
                "id": "basic_1",
                "type": "basics",
                "question": f"That's great! I can see from your resume that you have experience with {primary_skill}. What initially attracted you to this technology, and how has your relationship with it evolved over time? Are there particular aspects of {primary_skill} that you find most enjoyable or challenging?",
                "duration": 5
            },
            {
                "id": "basic_2", 
                "type": "basics",
                "question": "We all know that debugging can be both frustrating and rewarding. I'm curious about your approach - when you're faced with a particularly stubborn bug that's not immediately obvious, what's your thought process? Could you walk me through how you typically tackle these situations?",
                "duration": 5
            },
            {
                "id": "tech_1",
                "type": "technical",
                "question": f"I'd love to hear about a specific project you've worked on that you're particularly proud of. Could you tell me about something you built using {primary_skill} or {secondary_skill}? What made this project interesting or challenging for you, and how did you overcome any obstacles you encountered?",
                "duration": 5
            },
            {
                "id": "tech_2",
                "type": "technical", 
                "question": f"Performance optimization is always an interesting topic. Imagine you're working on a {primary_skill} application that's starting to slow down as it gains more users. What would be your systematic approach to identifying and addressing performance bottlenecks? What tools or techniques would you reach for first?",
                "duration": 5
            },
            {
                "id": "advanced_1",
                "type": "advanced",
                "question": "Here's a fun challenge to wrap up - let's say you're tasked with designing a system that needs to handle a million concurrent users. I'm not looking for a perfect solution, but I'm curious about your thought process. How would you approach this problem? What are the key considerations you'd think about first?",
                "duration": 5
            }
        ]
        
        print(f"Using personalized conversational questions for {name} ({exp_years} experience with {primary_skill})")
        return questions
    
