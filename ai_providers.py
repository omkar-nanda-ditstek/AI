import os
import requests
from typing import List, Dict, Any
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, context: str = "") -> str:
        pass

class OllamaProvider(AIProvider):
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            return response.json().get("response", "")
        except Exception as e:
            return f"Error: {str(e)}"

class HuggingFaceProvider(AIProvider):
    def __init__(self, model: str = "microsoft/DialoGPT-medium"):
        try:
            from transformers import pipeline
            self.generator = pipeline("text-generation", model=model)
        except ImportError:
            raise ImportError("Install transformers: pip install transformers torch")
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            result = self.generator(full_prompt, max_length=200, num_return_sequences=1)
            return result[0]["generated_text"].replace(full_prompt, "").strip()
        except Exception as e:
            return f"Error: {str(e)}"

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str = None):
        try:
            import google.generativeai as genai
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("Gemini API key required")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.available = True
        except ImportError:
            print("⚠️  Google Generative AI not installed, using simple fallback")
            self.available = False
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        if not self.available:
            return self._fallback_response(prompt)
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Simple fallback when Gemini is not available"""
        if "question" in prompt.lower():
            return "Can you tell me about your experience with the technologies mentioned in your resume?"
        elif "score" in prompt.lower():
            return "Good response with relevant technical details."
        else:
            return "Thank you for your response. Can you elaborate on that?"

class SimpleProvider(AIProvider):
    """Simple fallback provider when others fail"""
    def generate_response(self, prompt: str, context: str = "") -> str:
        if "question" in prompt.lower():
            return "Can you tell me about your experience and what interests you most about this role?"
        elif "score" in prompt.lower():
            return "Good response showing relevant experience."
        else:
            return "That's interesting. Can you tell me more about that?"

class AIManager:
    def __init__(self, provider_type: str = "ollama"):
        self.provider = self._create_provider(provider_type)
    
    def _create_provider(self, provider_type: str) -> AIProvider:
        try:
            if provider_type == "ollama":
                return OllamaProvider()
            elif provider_type == "huggingface":
                return HuggingFaceProvider()
            elif provider_type == "gemini":
                return GeminiProvider()
            else:
                raise ValueError(f"Unknown provider: {provider_type}")
        except Exception as e:
            print(f"⚠️  Failed to initialize {provider_type}, using simple fallback")
            return SimpleProvider()
    
    def generate_questions(self, resume_text: str, num_questions: int = 5) -> List[str]:
        prompt = f"""Based on this resume, generate {num_questions} interview questions:

Resume: {resume_text}

Generate questions that are:
1. Relevant to the candidate's experience
2. Technical and behavioral mix
3. Appropriate difficulty level

Return only the questions, one per line."""
        
        response = self.provider.generate_response(prompt)
        questions = [q.strip() for q in response.split('\n') if q.strip()]
        return questions[:num_questions]
    
    def generate_contextual_question(self, prompt: str) -> str:
        """Generate contextual question based on resume skills and conversation"""
        response = self.provider.generate_response(prompt)
        # Clean up the response to return just the question
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if lines:
            # Return the first non-empty line as the question
            return lines[0].replace('"', '').strip()
        return "Can you tell me about your experience with the technologies in your resume?"
    
    def analyze_response(self, question: str, answer: str, resume_context: str = "") -> Dict[str, Any]:
        prompt = f"""Analyze this interview response:

Question: {question}
Answer: {answer}
Resume Context: {resume_context}

Provide a score (1-10) and brief feedback focusing on:
- Relevance to question
- Technical accuracy
- Communication clarity

Format: Score: X/10
Feedback: [brief feedback]"""
        
        response = self.provider.generate_response(prompt)
        
        # Parse response
        lines = response.split('\n')
        score = 7  # default
        feedback = "Good response"
        
        for line in lines:
            if 'Score:' in line:
                try:
                    score = int(line.split(':')[1].split('/')[0].strip())
                except:
                    pass
            elif 'Feedback:' in line:
                feedback = line.split(':', 1)[1].strip()
        
        return {
            "score": min(10, max(1, score)),
            "feedback": feedback,
            "max_score": 10
        }