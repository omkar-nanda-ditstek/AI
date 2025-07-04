from typing import List, Dict
import re
import os

class ResponseAnalyzer:
    def __init__(self, ai_manager=None):
        self.ai_manager = ai_manager
        if not ai_manager:
            # Fallback for backward compatibility
            from ai_providers import AIManager
            provider = os.getenv('AI_PROVIDER', 'ollama')
            self.ai_manager = AIManager(provider)
            print(f"Initialized AI provider for analysis: {provider}")
        else:
            print("Using provided AI manager for analysis")
    def analyze_responses(self, responses: List[Dict]) -> Dict:
        total_score = 0
        detailed_scores = {}
        
        for response in responses:
            question = response.get('question', '')
            answer = response['answer'].strip()
            
            # Use AI for analysis if available
            if self.ai_manager:
                try:
                    analysis = self.ai_manager.analyze_response(question, answer)
                    score = analysis['score']
                except Exception as e:
                    print(f"AI analysis failed, using fallback: {e}")
                    score = self._score_answer(answer, response['question_id'])
            else:
                score = self._score_answer(answer, response['question_id'])
            
            detailed_scores[response['question_id']] = score
            total_score += score
        
        avg_score = total_score / len(responses) if responses else 0
        
        return {
            "overall_score": round(avg_score, 2),
            "detailed_scores": detailed_scores,
            "rating": self._get_rating(avg_score),
            "feedback": self._generate_feedback(avg_score)
        }
    
    def _score_answer(self, answer: str, question_id: str) -> float:
        """Fallback scoring method when AI is not available"""
        if len(answer) < 10:
            return 2.0
        
        base_score = min(5.0, len(answer) / 50)
        technical_keywords = ['implement', 'design', 'develop', 'optimize', 'debug', 'test']
        keyword_score = sum(1 for keyword in technical_keywords if keyword.lower() in answer.lower())
        sentences = len(re.findall(r'[.!?]+', answer))
        structure_score = min(2.0, sentences * 0.5)
        
        return min(10.0, base_score + keyword_score + structure_score)
    
