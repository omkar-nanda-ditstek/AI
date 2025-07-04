from typing import Dict, List
import os
from datetime import datetime
from custom_trainer import CustomInterviewTrainer

class QuestionGenerator:
    def __init__(self, ai_manager=None):
        self.ai_manager = ai_manager
        self.custom_trainer = CustomInterviewTrainer()
        if not ai_manager:
            # Fallback for backward compatibility
            from ai_providers import AIManager
            provider = os.getenv('AI_PROVIDER', 'ollama')
            self.ai_manager = AIManager(provider)
            print(f"Initialized AI provider: {provider}")
        else:
            print("Using provided AI manager")
        
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
        
        try:
            questions = self.ai_manager.generate_questions(
                f"Name: {name}\nSkills: {', '.join(skills)}\nExperience: {experience}", 
                num_questions=6
            )
            
            # Format questions for the interview system
            formatted_questions = []
            phases = ["introduction", "basics", "basics", "technical", "technical", "advanced"]
            
            for i, question in enumerate(questions):
                formatted_questions.append({
                    "id": f"{phases[i]}_{i+1}",
                    "type": phases[i],
                    "question": question,
                    "duration": 5
                })
            
            print(f"Successfully generated {len(formatted_questions)} AI questions")
            return formatted_questions
                
        except Exception as e:
            print(f"AI generation failed: {str(e)}")
            raise Exception(f"Failed to generate AI questions: {str(e)}")
    
    

    

    
    def generate_next_question(self, resume_data: Dict, conversation_history: List[Dict], current_question_index: int) -> Dict:
        """Generate the next question based on conversation history and resume skills"""
        
        try:
            skills = resume_data.get('skills', [])
            name = resume_data.get('name', 'Candidate')
            phase = self._determine_interview_phase(current_question_index)
            
            # Try custom training data first
            custom_question = self.custom_trainer.generate_custom_question(skills, conversation_history)
            
            # If custom training has specific question, use it
            if custom_question != "Tell me about your technical experience and projects you've worked on.":
                return {
                    "id": f"{phase}_{current_question_index + 1}",
                    "type": phase,
                    "question": custom_question,
                    "duration": 5
                }
            
            # Otherwise use AI generation
            context = self._build_conversation_context(resume_data, conversation_history)
            prompt = self._create_skill_focused_prompt(name, skills, context, phase, current_question_index)
            ai_response = self.ai_manager.generate_contextual_question(prompt)
            
            return {
                "id": f"{phase}_{current_question_index + 1}",
                "type": phase,
                "question": ai_response,
                "duration": 5
            }
            
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            raise Exception(f"Failed to generate question: {str(e)}")
    
    def _create_skill_focused_prompt(self, name: str, skills: List[str], context: str, phase: str, question_index: int) -> str:
        """Create AI prompt focused on resume skills and projects"""
        
        skills_text = ', '.join(skills) if skills else 'general programming'
        
        phase_focus = {
            "introduction": "basic background and introduction to their skills",
            "basics": f"fundamental concepts in {skills_text}",
            "technical": f"practical experience and projects using {skills_text}",
            "advanced": f"advanced problem-solving and system design with {skills_text}"
        }
        
        prompt = f"""
You are Sarah, a friendly technical interviewer. Generate ONE natural conversational question for {name}.

RESUME SKILLS: {skills_text}

CONVERSATION CONTEXT:
{context}

CURRENT PHASE: {phase_focus.get(phase, phase)} (Question {question_index + 1})

QUESTION REQUIREMENTS:
1. Focus on their resume skills: {skills_text}
2. Ask about specific projects they've worked on
3. Be conversational and friendly
4. Reference their previous answers naturally
5. Ask for concrete examples and experiences

EXAMPLE QUESTION TYPES:
- "Can you tell me about a project where you used [specific skill]?"
- "What challenges did you face when working with [technology from resume]?"
- "How did you implement [feature] in your [project type] projects?"
- "What's your experience with [skill from resume]?"

Generate only the question text, no JSON or formatting.
"""
        return prompt
    
    def _get_fallback_question(self, index: int) -> Dict:
        """Fallback questions when generation fails"""
        fallback_questions = [
            "What technologies are you most passionate about working with?",
            "Can you describe a challenging problem you've solved recently?",
            "How do you stay updated with new technologies and trends?",
            "What's your approach to collaborating with team members?",
            "Where do you see yourself growing as a developer?"
        ]
        
        question = fallback_questions[min(index, len(fallback_questions)-1)]
        
        return {
            "id": f"fallback_{index + 1}",
            "type": "general",
            "question": question,
            "duration": 5
        }
    
    
    def _build_conversation_context(self, resume_data: Dict, conversation_history: List[Dict]) -> str:
        """Build conversation context from previous Q&A"""
        context = f"Candidate: {resume_data.get('name', 'Candidate')}\n"
        context += f"Skills: {', '.join(resume_data.get('skills', []))}\n\n"
        
        context += "Previous conversation:\n"
        for item in conversation_history:
            context += f"Q: {item['question']}\n"
            context += f"A: {item['answer']}\n\n"
        
        return context
    
    def _determine_interview_phase(self, question_index: int) -> str:
        """Determine which phase of the interview we're in for 30-minute interview"""
        if question_index <= 2:
            return "introduction"
        elif question_index <= 6:
            return "basics"
        elif question_index <= 11:
            return "technical"
        else:
            return "advanced"
    
    def _create_dynamic_question_prompt(self, resume_data: Dict, conversation_context: str, phase: str, question_index: int, detected_mood: str = "neutral") -> str:
        """Create prompt for dynamic question generation with enhanced emotional intelligence"""
        name = resume_data.get('name', 'Candidate')
        
        phase_descriptions = {
            "introduction": "warm introduction and getting to know the candidate personally",
            "basics": "fundamental technical concepts and their background", 
            "technical": "practical experience and real-world applications",
            "advanced": "problem-solving and system design thinking"
        }
        
        # Mood-specific response guidelines
        mood_guidelines = {
            "negative": "Be gentle, supportive, and understanding. Show empathy and try to lift their spirits without being insensitive.",
            "positive": "Share their enthusiasm! Be warm and encouraging. Match their positive energy.",
            "nervous": "Be reassuring and calm. Create a safe space. Use encouraging language.",
            "neutral": "Be warm and professional. Show genuine interest.",
            "proud": "Acknowledge their achievement! Show genuine appreciation for their work.",
            "uncertain": "Be patient and supportive. No pressure. Make them feel comfortable."
        }
        
        prompt = f"""
You are Sarah, a warm, empathetic, and experienced technical interviewer. You're having a natural conversation with {name}. 

CRITICAL MOOD CONTEXT: The candidate's mood appears to be {detected_mood.upper()}.
{mood_guidelines.get(detected_mood, mood_guidelines["neutral"])}

Current Context:
{conversation_context}

Interview Phase: {phase_descriptions.get(phase, phase)} (Question {question_index + 1})

MANDATORY EMOTIONAL MATCHING RULES:
1. If mood is NEGATIVE/SAD: Start with empathy ("I'm sorry to hear that", "That sounds challenging")
2. If mood is POSITIVE/HAPPY: Share enthusiasm ("That's wonderful!", "I can hear your excitement")
3. If mood is NERVOUS/ANXIOUS: Be reassuring ("That's completely normal", "Take your time")
4. If mood is PROUD: Celebrate with them ("That's impressive!", "You should be proud")
5. If mood is UNCERTAIN: Be supportive ("That's perfectly okay", "No pressure at all")

HUMAN CONVERSATION RULES:
1. ALWAYS acknowledge their previous response first with appropriate emotion
2. Show appropriate emotional response based on detected mood: {detected_mood}
3. Ask follow-up questions that feel natural and caring
4. Use their name occasionally but not excessively
5. Mirror their emotional tone appropriately
6. Be genuinely interested in their story
7. Make it feel like talking to a friend who cares

NATURAL CONVERSATION STARTERS (choose based on mood):
- Empathetic: "I can tell that...", "That sounds like...", "I understand..."
- Enthusiastic: "That's amazing!", "I love that!", "How exciting!"
- Reassuring: "That's perfectly normal", "Take your time", "No worries at all"
- Appreciative: "That's impressive", "Great work", "You should be proud"

Response Format (JSON only):
{{
  "id": "{phase}_{question_index + 1}",
  "type": "{phase}",
  "question": "Your natural, emotionally appropriate response that acknowledges their mood + your follow-up question",
  "duration": 5
}}

Remember: This is a CONVERSATION, not an interrogation. Match their emotional state appropriately!
"""
        return prompt
    
    def _detect_user_mood(self, conversation_history: List[Dict]) -> str:
        """Detect user's mood from their last answer using keyword analysis"""
        if not conversation_history:
            return "neutral"
        
        last_answer = conversation_history[-1].get('answer', '').lower()
        
        # Define mood indicators
        mood_keywords = {
            "negative": [
                'not good', 'bad', 'terrible', 'awful', 'stressed', 'tired', 'sad', 
                'difficult', 'struggling', 'hard', 'tough', 'challenging', 'problem', 
                'issue', 'disappointed', 'frustrated', 'overwhelmed', 'worried', 'down',
                'horrible', 'worst', 'failed', 'failing', 'can\'t', 'unable', 'stuck',
                'depressed', 'miserable', 'upset', 'angry', 'annoyed'
            ],
            "positive": [
                'great', 'good', 'excellent', 'wonderful', 'amazing', 'fantastic', 
                'happy', 'excited', 'love', 'passionate', 'enjoy', 'brilliant', 
                'awesome', 'perfect', 'incredible', 'outstanding', 'thrilled',
                'delighted', 'pleased', 'satisfied', 'proud', 'accomplished',
                'successful', 'achieved', 'built', 'created'
            ],
            "nervous": [
                'nervous', 'anxious', 'worried', 'scared', 'uncertain', 'unsure',
                'hesitant', 'doubtful', 'concerned', 'apprehensive', 'intimidated',
                'overwhelmed', 'pressure', 'stress', 'tense'
            ],
            "proud": [
                'proud', 'accomplished', 'achieved', 'success', 'successful', 
                'built', 'created', 'developed', 'implemented', 'delivered',
                'completed', 'finished', 'solved', 'improved', 'optimized'
            ],
            "uncertain": [
                'maybe', 'not sure', 'i think', 'probably', 'might', 'could be',
                'perhaps', 'i guess', 'sort of', 'kind of', 'i suppose',
                'not really', 'somewhat', 'partially'
            ]
        }
        
        # Count mood indicators
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in last_answer)
            if score > 0:
                mood_scores[mood] = score
        
        # Return the mood with highest score, or neutral if no clear mood
        if mood_scores:
            detected_mood = max(mood_scores, key=mood_scores.get)
            print(f"Mood analysis: {mood_scores} -> {detected_mood}")
            return detected_mood
        
        return "neutral"

    def _validate_emotional_response(self, ai_question: str, detected_mood: str) -> bool:
        """Validate that the AI's response matches the detected mood appropriately"""
        question_lower = ai_question.lower()
        
        # Define inappropriate response patterns for each mood
        inappropriate_patterns = {
            "negative": [
                'fantastic', 'amazing', 'wonderful', 'excellent', 'great!', 
                'awesome', 'brilliant', 'perfect', 'incredible', 'outstanding',
                'thrilled', 'excited', 'love that', 'how exciting'
            ],
            "nervous": [
                'that\'s fantastic', 'amazing', 'incredible', 'outstanding',
                'you must be', 'definitely', 'obviously', 'clearly you'
            ],
            "uncertain": [
                'obviously', 'clearly', 'definitely', 'you must', 'surely',
                'of course you', 'certainly'
            ]
        }
        
        # Define required empathetic patterns for negative moods
        required_empathy = {
            "negative": [
                'sorry to hear', 'understand', 'that sounds', 'i can tell',
                'that must', 'i appreciate', 'no pressure', 'take your time',
                'thank you for sharing', 'thank you for being open', 'thanks for sharing',
                'i appreciate you', 'let\'s focus on', 'let\'s talk about',
                'can you tell me about', 'would you like to share', 'how about we',
                'what motivates you', 'what interests you', 'what drives you'
            ],
            "nervous": [
                'no pressure', 'take your time', 'no worries', 'that\'s okay',
                'perfectly normal', 'don\'t worry', 'no rush', 'at your own pace',
                'no right or wrong', 'however you feel', 'whatever you\'re comfortable'
            ],
            "uncertain": [
                'no pressure', 'take your time', 'no worries', 'that\'s okay',
                'perfectly normal', 'don\'t worry', 'no rush', 'at your own pace',
                'no right or wrong', 'however you feel', 'whatever you\'re comfortable',
                'that\'s perfectly fine', 'completely understandable'
            ]
        }
        
        # Check for inappropriate responses
        if detected_mood in inappropriate_patterns:
            for pattern in inappropriate_patterns[detected_mood]:
                if pattern in question_lower:
                    print(f"Emotional validation failed: Found inappropriate '{pattern}' for {detected_mood} mood")
                    return False
        
        # Check for required empathy in negative situations
        if detected_mood in required_empathy:
            has_empathy = any(pattern in question_lower for pattern in required_empathy[detected_mood])
            if not has_empathy:
                print(f"Emotional validation failed: Missing empathy for {detected_mood} mood")
                return False
        
        print(f"Emotional validation passed for {detected_mood} mood")
        return True

