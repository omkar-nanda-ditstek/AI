from typing import Dict, List
import random

class QuestionGenerator:
    def __init__(self):
        self.tech_questions = {
            'python': [
                "Explain the difference between list and tuple in Python.",
                "How do you handle exceptions in Python?",
                "What are Python decorators and how do you use them?"
            ],
            'javascript': [
                "What is the difference between let, const, and var?",
                "Explain closures in JavaScript.",
                "How does async/await work in JavaScript?"
            ],
            'react': [
                "What are React hooks and why are they useful?",
                "Explain the component lifecycle in React.",
                "How do you manage state in a React application?"
            ]
        }
        
        self.experience_questions = [
            "Tell me about your most challenging project.",
            "How do you approach debugging complex issues?",
            "Describe a time when you had to learn a new technology quickly."
        ]
    
    def generate_questions(self, resume_data: Dict) -> List[Dict]:
        questions = []
        
        # Add experience-based questions
        questions.extend([
            {"id": f"exp_{i}", "type": "experience", "question": q}
            for i, q in enumerate(self.experience_questions[:2])
        ])
        
        # Add tech-specific questions based on skills
        for skill in resume_data.get('skills', [])[:2]:
            skill_lower = skill.lower()
            if skill_lower in self.tech_questions:
                tech_q = random.choice(self.tech_questions[skill_lower])
                questions.append({
                    "id": f"tech_{skill_lower}",
                    "type": "technical",
                    "question": f"Regarding {skill}: {tech_q}"
                })
        
        # Add project-based questions
        projects = resume_data.get('projects', [])
        if projects:
            questions.append({
                "id": "project_1",
                "type": "project",
                "question": f"Can you explain the project: {projects[0]}?"
            })
        
        return questions[:5]  # Limit to 5 questions