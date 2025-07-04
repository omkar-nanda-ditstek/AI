import json
import os
from typing import Dict, List

class CustomInterviewTrainer:
    def __init__(self, training_data_path: str = "training_data.json"):
        self.training_data = self._load_training_data(training_data_path)
        
    def _load_training_data(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"interview_patterns": [], "response_patterns": []}
    
    def generate_custom_question(self, skills: List[str], conversation_history: List[Dict]) -> str:
        """Generate question based on your training data"""
        
        # Find matching skill patterns
        for skill in skills:
            for pattern in self.training_data["interview_patterns"]:
                if skill.lower() in pattern["skill"].lower():
                    questions = pattern["questions"]
                    if questions:
                        return questions[0]  # Return first question for now
        
        # Default question if no skill match
        return "Tell me about your technical experience and projects you've worked on."
    
    def generate_custom_response(self, user_answer: str) -> str:
        """Generate response based on your training data"""
        
        user_lower = user_answer.lower()
        
        # Check response patterns
        for pattern in self.training_data["response_patterns"]:
            for keyword in pattern["keywords"]:
                if keyword in user_lower:
                    responses = pattern["responses"]
                    if responses:
                        return responses[0]  # Return first response
        
        return "That's interesting! Can you tell me more about that?"
    
    def add_training_example(self, skill: str, question: str, keywords: List[str], response: str):
        """Add new training example"""
        
        # Add question pattern
        skill_pattern = None
        for pattern in self.training_data["interview_patterns"]:
            if pattern["skill"].lower() == skill.lower():
                skill_pattern = pattern
                break
        
        if not skill_pattern:
            skill_pattern = {"skill": skill, "questions": [], "follow_ups": []}
            self.training_data["interview_patterns"].append(skill_pattern)
        
        if question not in skill_pattern["questions"]:
            skill_pattern["questions"].append(question)
        
        # Add response pattern
        response_pattern = {
            "keywords": keywords,
            "responses": [response]
        }
        self.training_data["response_patterns"].append(response_pattern)
        
        # Save updated data
        self._save_training_data()
    
    def _save_training_data(self):
        with open("training_data.json", 'w') as f:
            json.dump(self.training_data, f, indent=2)

# Usage example
if __name__ == "__main__":
    trainer = CustomInterviewTrainer()
    
    # Add new training example
    trainer.add_training_example(
        skill="Python",
        question="What's your experience with Python frameworks like Django or Flask?",
        keywords=["python", "django", "flask"],
        response="That's great! Can you describe a Python project you're proud of?"
    )
    
    # Test generation
    question = trainer.generate_custom_question(["Node.js"], [])
    print(f"Generated question: {question}")