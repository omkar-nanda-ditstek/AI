from typing import List, Dict
import re

class ResponseAnalyzer:
    def analyze_responses(self, responses: List[Dict]) -> Dict:
        total_score = 0
        detailed_scores = {}
        
        for response in responses:
            answer = response['answer'].strip()
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
        if len(answer) < 10:
            return 2.0  # Very short answers
        
        # Basic scoring based on answer length and keywords
        base_score = min(5.0, len(answer) / 50)  # Length-based scoring
        
        # Keyword-based scoring
        technical_keywords = ['implement', 'design', 'develop', 'optimize', 'debug', 'test']
        keyword_score = sum(1 for keyword in technical_keywords if keyword.lower() in answer.lower())
        
        # Sentence structure scoring
        sentences = len(re.findall(r'[.!?]+', answer))
        structure_score = min(2.0, sentences * 0.5)
        
        final_score = min(10.0, base_score + keyword_score + structure_score)
        return final_score
    
    def _get_rating(self, score: float) -> str:
        if score >= 8.0:
            return "Excellent"
        elif score >= 6.0:
            return "Good"
        elif score >= 4.0:
            return "Average"
        else:
            return "Needs Improvement"
    
    def _generate_feedback(self, score: float) -> str:
        if score >= 8.0:
            return "Strong technical knowledge and communication skills demonstrated."
        elif score >= 6.0:
            return "Good understanding with room for more detailed explanations."
        elif score >= 4.0:
            return "Basic knowledge shown, consider providing more specific examples."
        else:
            return "Responses need more depth and technical detail."