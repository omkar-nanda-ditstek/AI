import React, { useState, useEffect } from 'react';
import './Interview.css';

const Interview = ({ questions, sessionId, resumeId, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [displayedText, setDisplayedText] = useState('');
  const [answerEnabled, setAnswerEnabled] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [lastResponse, setLastResponse] = useState('');
  const [dynamicQuestions, setDynamicQuestions] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [totalQuestions] = useState(15);
  const [isGeneratingQuestion, setIsGeneratingQuestion] = useState(false);
  const [isGreeting, setIsGreeting] = useState(true);
  const [timeRemaining, setTimeRemaining] = useState(30 * 60); // 30 minutes in seconds
  const [timerInterval, setTimerInterval] = useState(null);


  useEffect(() => {
    // Initialize with a warm, natural greeting
    if (currentQuestion === 0) {
      const greetingQuestion = {
        id: "greeting",
        type: "greeting",
        question: "Hello! I'm Sarah, and I'm excited to chat with you today. How are you doing?",
        duration: 5
      };
      setDynamicQuestions([greetingQuestion]);
      
      // Start 30-minute timer
      const interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(interval);
            // Auto-end interview when time runs out
            setTimeout(() => {
              speakAndTypeQuestion("Time's up! Thank you for the wonderful conversation.", true);
              setTimeout(() => onComplete([]), 3000);
            }, 1000);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      setTimerInterval(interval);
      
      setTimeout(() => {
        speakAndTypeQuestion(greetingQuestion.question, true);
      }, 1000);
    }
    
    return () => {
      if (timerInterval) clearInterval(timerInterval);
    };
  }, []);

  const speakAndTypeQuestion = (text, isGreeting = false) => {
    setIsTyping(true);
    setAnswerEnabled(false);
    setDisplayedText('');
    
    // Text-to-speech setup
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.85;
    utterance.pitch = 1.2;
    utterance.volume = 0.9;
    
    // Select female voice
    const voices = speechSynthesis.getVoices();
    const femaleVoice = voices.find(voice => 
      voice.name.includes('Female') || 
      voice.name.includes('Samantha') ||
      voice.name.includes('Karen') ||
      voice.name.includes('Moira') ||
      voice.gender === 'female'
    ) || voices.find(voice => voice.lang.startsWith('en'));
    
    if (femaleVoice) {
      utterance.voice = femaleVoice;
    }
    
    // Start speaking only if not muted
    if (!isMuted) {
      speechSynthesis.speak(utterance);
    }
    
    // Sync typing with speech
    let i = 0;
    const speed = 40;
    
    const typeInterval = setInterval(() => {
      if (i < text.length) {
        setDisplayedText(text.substring(0, i + 1));
        i++;
      } else {
        clearInterval(typeInterval);
        setIsTyping(false);
        setAnswerEnabled(true);
      }
    }, speed);
    
    // Stop typing when speech ends
    utterance.onend = () => {
      if (i < text.length) {
        setDisplayedText(text);
        clearInterval(typeInterval);
        setIsTyping(false);
        setAnswerEnabled(true);
      }
    };
  };

  const analyzeUserMood = (answer) => {
    const lowerAnswer = answer.toLowerCase();
    
    // Negative indicators
    if (lowerAnswer.includes('not good') || lowerAnswer.includes('bad') || 
        lowerAnswer.includes('terrible') || lowerAnswer.includes('awful') ||
        lowerAnswer.includes('stressed') || lowerAnswer.includes('tired') ||
        lowerAnswer.includes('sad') || lowerAnswer.includes('difficult') ||
        lowerAnswer.includes('anxious') || lowerAnswer.includes('nervous')) {
      return 'negative';
    }
    
    // Positive indicators
    if (lowerAnswer.includes('great') || lowerAnswer.includes('good') || 
        lowerAnswer.includes('excellent') || lowerAnswer.includes('wonderful') ||
        lowerAnswer.includes('amazing') || lowerAnswer.includes('fantastic') ||
        lowerAnswer.includes('happy') || lowerAnswer.includes('excited')) {
      return 'positive';
    }
    
    // Neutral/okay indicators
    if (lowerAnswer.includes('okay') || lowerAnswer.includes('fine') || 
        lowerAnswer.includes('alright') || lowerAnswer.includes('decent')) {
      return 'neutral';
    }
    
    return 'neutral';
  };

  const getEmpatheticResponse = (userAnswer, mood) => {
    const responses = {
      negative: [
        "I'm sorry to hear that. I hope our conversation can brighten your day a bit. I'm here to listen, and we can take this at whatever pace feels comfortable for you.",
        "That sounds challenging. I appreciate you sharing that with me. I want you to know that it's okay to have difficult days.",
        "I understand, some days are tougher than others. I'm grateful you're taking time to chat despite not feeling your best."
      ],
      positive: [
        "That's wonderful to hear! Your positive energy is already making this conversation better.",
        "I'm so glad you're having a great day! It's always a pleasure to talk with someone in such good spirits.",
        "That's fantastic! I love your enthusiasm - it's contagious!"
      ],
      neutral: [
        "I appreciate your honesty. I'm looking forward to getting to know you better.",
        "That's perfectly fine. I'm glad we can have this conversation together.",
        "Thanks for sharing. I'm excited to learn more about you!"
      ]
    };
    
    return responses[mood][Math.floor(Math.random() * responses[mood].length)];
  };

  const generateNextQuestion = async () => {
    if (currentQuestion >= totalQuestions - 1) {
      return null;
    }

    setIsGeneratingQuestion(true);
    
    try {
      const response = await fetch('/generate-next-question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          resume_id: resumeId,
          conversation_history: conversationHistory,
          current_question_index: currentQuestion + 1
        })
      });
      
      const result = await response.json();
      
      if (result.success && result.question) {
        return result.question;
      } else {
        return null;
      }
      
    } catch (error) {
      console.error('Network error generating question:', error);
      return null;
    } finally {
      setIsGeneratingQuestion(false);
    }
  };



  const nextQuestion = async () => {
    // Handle greeting response specially
    if (isGreeting && currentQuestion === 0) {
      const mood = analyzeUserMood(currentAnswer);
      const empathyResponse = getEmpatheticResponse(currentAnswer, mood);
      
      // Store greeting conversation
      const greetingHistory = [{
        question: "How are you doing today?",
        answer: currentAnswer.trim()
      }];
      
      setConversationHistory(greetingHistory);
      
      setAnswers([{
        question_id: "greeting",
        answer: currentAnswer
      }]);
      
      // Generate the first real interview question with empathy
      const firstQuestion = {
        id: "intro_1",
        type: "introduction",
        question: `${empathyResponse} Let's start with the basics - could you tell me about yourself and your background in software development?`,
        duration: 5
      };
      
      setDynamicQuestions(prev => [...prev, firstQuestion]);
      setCurrentAnswer('');
      setCurrentQuestion(1);
      setIsGreeting(false);
      
      setTimeout(() => {
        speakAndTypeQuestion(firstQuestion.question);
      }, 1500);
      
      return;
    }

    // Store the current Q&A in conversation history FIRST
    const currentQ = dynamicQuestions[currentQuestion];
    const updatedHistory = [...conversationHistory];
    
    if (currentQ && currentAnswer.trim()) {
      updatedHistory.push({
        question: currentQ.question,
        answer: currentAnswer.trim()
      });
      setConversationHistory(updatedHistory);
    }

    // Update answers
    const newAnswers = [
      ...answers,
      {
        question_id: currentQ?.id || `question_${currentQuestion + 1}`,
        answer: currentAnswer,
      },
    ];
    setAnswers(newAnswers);
    setLastResponse(currentAnswer);
    setCurrentAnswer('');

    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(currentQuestion + 1);
      
      // Generate the next question using AI
      const nextQ = await generateNextQuestion();
      if (nextQ) {
        setDynamicQuestions(prev => [...prev, nextQ]);
        setTimeout(() => {
          speakAndTypeQuestion(nextQ.question);
        }, 1500);
      } else {
        // End interview if AI fails to generate question
        setTimeout(() => {
          const endings = [
            "Thank you so much! This has been such a lovely conversation. I really enjoyed talking with you!",
            "That was wonderful! I had a great time chatting with you. Thanks for being so open!",
            "This was fantastic! I really appreciate you sharing so much with me. It was a pleasure!"
          ];
          const ending = endings[Math.floor(Math.random() * endings.length)];
          speakAndTypeQuestion(ending, true);
          setTimeout(() => onComplete(newAnswers), 3000);
        }, 1000);
      }
      
    } else {
      // Natural ending
      setTimeout(() => {
        const endings = [
          "Thank you so much! This has been such a lovely conversation. I really enjoyed talking with you!",
          "That was wonderful! I had a great time chatting with you. Thanks for being so open!",
          "This was fantastic! I really appreciate you sharing so much with me. It was a pleasure!"
        ];
        const ending = endings[Math.floor(Math.random() * endings.length)];
        speakAndTypeQuestion(ending, true);
        setTimeout(() => onComplete(newAnswers), 3000);
      }, 1000);
    }
  };

  const skipQuestion = async () => {
    const currentQ = dynamicQuestions[currentQuestion];
    
    // Store skip in conversation history
    const updatedHistory = [...conversationHistory];
    if (currentQ) {
      updatedHistory.push({
        question: currentQ.question,
        answer: "[Skipped - moved to next topic]"
      });
      setConversationHistory(updatedHistory);
    }

    const newAnswers = [
      ...answers,
      {
        question_id: currentQ?.id || `question_${currentQuestion + 1}`,
        answer: '',
      },
    ];
    setAnswers(newAnswers);
    setCurrentAnswer('');

    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(currentQuestion + 1);
      
      // Generate the next question using AI
      const nextQ = await generateNextQuestion();
      if (nextQ) {
        setDynamicQuestions(prev => [...prev, nextQ]);
        setTimeout(() => {
          speakAndTypeQuestion(nextQ.question);
        }, 1000);
      } else {
        // End interview if AI fails to generate question
        onComplete(newAnswers);
      }
    } else {
      onComplete(newAnswers);
    }
  };

  // Load voices and setup speech recognition when component mounts
  useEffect(() => {
    // Ensure right-click context menu is always enabled
    const enableRightClick = () => {
      document.oncontextmenu = null;
      document.onselectstart = null;
      document.ondragstart = null;
      return true;
    };
    enableRightClick();
    
    const loadVoices = () => {
      speechSynthesis.getVoices();
    };
    
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices;
    }
    loadVoices();
    
    // Setup speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';
      
      recognitionInstance.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setCurrentAnswer(prev => prev + ' ' + finalTranscript);
        }
      };
      
      recognitionInstance.onerror = () => {
        setIsListening(false);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      
      setRecognition(recognitionInstance);
    }
  }, []);

  if (dynamicQuestions.length === 0) {
    return (
      <div className="interview-container">
        <div className="loading-message">
          <div className="loading-spinner"></div>
          <p>Preparing your personalized interview experience...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-container">
      <div className="avatar-section">
        <div className={`realistic-avatar ${isTyping ? 'speaking' : ''}`}>
          <div className="avatar-face">
            <div className="hair"></div>
            <div className="face-shape">
              <div className="eyebrow left"></div>
              <div className="eyebrow right"></div>
              <div className="eye left">
                <div className="eyeball"></div>
                <div className="pupil"></div>
                <div className="highlight"></div>
              </div>
              <div className="eye right">
                <div className="eyeball"></div>
                <div className="pupil"></div>
                <div className="highlight"></div>
              </div>
              <div className="nose"></div>
              <div className={`mouth ${isTyping ? 'talking' : ''}`}>
                <div className="lips"></div>
                <div className="teeth"></div>
              </div>
              <div className="cheek left"></div>
              <div className="cheek right"></div>
            </div>
            <div className="neck"></div>
            <div className="shoulders">
              <div className="blazer"></div>
              <div className="collar"></div>
            </div>
          </div>
        </div>
        <div className="interviewer-name">Sarah Johnson</div>
        <div className="interviewer-title">Senior Technical Interviewer</div>
        <div className="interviewer-status">
          {isGeneratingQuestion ? (
            <div className="generating-indicator">
              🤔 Thinking about your response...
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          ) : isTyping ? (
            <div className="typing-indicator">
              💬 Sarah is chatting
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          ) : answerEnabled ? (
            "😊 Your turn to share..."
          ) : (
            "👋 Getting ready to chat..."
          )}
        </div>
        <button 
          className="mute-btn" 
          onClick={() => {
            setIsMuted(!isMuted);
            if (!isMuted) speechSynthesis.cancel();
          }}
          title={isMuted ? 'Unmute' : 'Mute'}
        >
          {isMuted ? '🔇' : '🔊'}
        </button>
        <div 
          className="progress-bar" 
          style={{ width: `${((currentQuestion + 1) / totalQuestions) * 100}%` }}
        ></div>
      </div>
      
      <div className="question-section">
        <div className="question-header">
          <div className="question-counter">
            Question {currentQuestion + 1} of {totalQuestions}
          </div>
          <div className={`timer ${timeRemaining < 300 ? 'warning' : ''}`}>
            ⏱️ {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}
          </div>
        </div>
        
        <div className="question-text">
          {displayedText}
          {isTyping && <span className="typing-cursor"></span>}
        </div>
        
        <div className="answer-section">
          <textarea 
            className="answer-input" 
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            placeholder={isGreeting ? "Share how you're feeling today..." : "Share your thoughts..."}
            disabled={!answerEnabled}
          />
          
          <div className="controls">
            <div className="conversation-controls">
              <button 
                className={`btn btn-speech ${isListening ? 'listening' : ''}`}
                onClick={() => {
                  if (recognition) {
                    if (isListening) {
                      recognition.stop();
                      setIsListening(false);
                    } else {
                      recognition.start();
                      setIsListening(true);
                    }
                  }
                }}
                disabled={!answerEnabled || !recognition}
                title={isListening ? 'Stop Speaking' : 'Speak Naturally'}
              >
                {isListening ? '🛑 Stop' : '🎤 Speak'}
              </button>
              <div className="conversation-hint">
                {isListening ? "I'm listening..." : "Speak naturally like a friend"}
              </div>
            </div>
            <div className="main-controls">
              <button 
                className="btn btn-primary" 
                onClick={nextQuestion} 
                disabled={!currentAnswer.trim() || !answerEnabled || isGeneratingQuestion}
              >
                {isGeneratingQuestion ? 'Generating...' : 
                 currentQuestion < totalQuestions - 1 ? 'Next Question' : 'Finish Interview'}
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={skipQuestion}
                disabled={!answerEnabled || isGeneratingQuestion}
              >
                Skip
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Interview;
