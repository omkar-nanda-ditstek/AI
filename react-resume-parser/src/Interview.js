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
  const [conversationMode, setConversationMode] = useState(true);
  const [lastResponse, setLastResponse] = useState('');

  useEffect(() => {
    if (questions && questions.length > 0) {
      if (currentQuestion === 0) {
        // Start with natural greeting
        setTimeout(() => {
          const greetings = [
            "Hello! How are you doing today?",
            "Hi there! Hope you're having a great day!",
            "Hey! Nice to meet you! How's everything going?"
          ];
          const greeting = greetings[Math.floor(Math.random() * greetings.length)];
          speakAndTypeQuestion(greeting, true);
        }, 1000);
      } else {
        speakAndTypeQuestion(questions[currentQuestion]?.question || '');
      }
    }
  }, [currentQuestion, questions]);

  const speakAndTypeQuestion = (text, isGreeting = false) => {
    setIsTyping(true);
    setAnswerEnabled(false);
    setDisplayedText('');
    
    let conversationalText = text;
    
    // Add intelligent responses based on previous answer content
    if (currentQuestion > 0 && lastResponse && !isGreeting) {
      const lowerResponse = lastResponse.toLowerCase();
      let responses;
      
      // Analyze the content of the previous response
      if (lowerResponse.includes('challenge') || lowerResponse.includes('difficult') || lowerResponse.includes('problem')) {
        responses = [
          "That sounds like quite a challenge. I admire how you handled it. ",
          "Difficulties can really teach us a lot. Thanks for sharing that experience. ",
          "It takes strength to work through challenges like that. "
        ];
      } else if (lowerResponse.includes('enjoy') || lowerResponse.includes('love') || lowerResponse.includes('passion')) {
        responses = [
          "I can hear the passion in your voice! That's wonderful. ",
          "It's so great when you find something you truly enjoy. ",
          "Your enthusiasm really comes through! "
        ];
      } else if (lowerResponse.includes('team') || lowerResponse.includes('collaborate') || lowerResponse.includes('work with')) {
        responses = [
          "Teamwork is so important. It sounds like you value collaboration. ",
          "Working well with others is such a valuable skill. ",
          "I can tell you're someone who works well with people. "
        ];
      } else if (lowerResponse.includes('learn') || lowerResponse.includes('grow') || lowerResponse.includes('develop')) {
        responses = [
          "I love that you're focused on learning and growth! ",
          "Continuous learning is so important. That's a great mindset. ",
          "Your commitment to development really shows. "
        ];
      } else {
        responses = [
          "That's really interesting! ",
          "I see, that makes perfect sense. ",
          "Thanks for sharing that with me. ",
          "That's a wonderful perspective. ",
          "I appreciate you telling me that. "
        ];
      }
      
      conversationalText = responses[Math.floor(Math.random() * responses.length)] + text;
    }
    
    // Text-to-speech setup
    const utterance = new SpeechSynthesisUtterance(conversationalText);
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
      if (i < conversationalText.length) {
        setDisplayedText(conversationalText.substring(0, i + 1));
        i++;
      } else {
        clearInterval(typeInterval);
        setIsTyping(false);
        setAnswerEnabled(true);
      }
    }, speed);
    
    // Stop typing when speech ends
    utterance.onend = () => {
      if (i < conversationalText.length) {
        setDisplayedText(conversationalText);
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
        lowerAnswer.includes('sad') || lowerAnswer.includes('difficult')) {
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

  const getAdaptiveResponse = (userAnswer, mood) => {
    if (mood === 'negative') {
      return [
        "Oh, I'm sorry to hear that. I hope our conversation can brighten your day a bit. I'm Sarah, and I'm here to listen. ",
        "I understand, some days are tougher than others. I'm Sarah, and I appreciate you taking the time to chat despite not feeling your best. ",
        "That sounds challenging. I'm Sarah, and I want you to know that it's okay to have difficult days. Let's take this conversation at your pace. "
      ];
    } else if (mood === 'positive') {
      return [
        "That's wonderful to hear! Your positive energy is contagious. I'm Sarah, and I'm excited to chat with someone in such great spirits! ",
        "That's fantastic! I love talking with people who are having a great day. I'm Sarah, and your enthusiasm is already making this conversation better! ",
        "That's amazing! It's so refreshing to meet someone with such positive energy. I'm Sarah, and I'm thrilled to be chatting with you! "
      ];
    } else {
      return [
        "That's perfectly fine! I'm Sarah, and I'm glad we can have this conversation together. ",
        "Fair enough! I'm Sarah, and I appreciate your honesty. Let's have a nice chat. ",
        "I understand! I'm Sarah, and I'm looking forward to getting to know you better. "
      ];
    }
  };

  const adaptQuestionBasedOnMood = (originalQuestion, mood, userAnswer) => {
    if (mood === 'negative') {
      // Make questions more gentle and supportive
      if (originalQuestion.includes('tell me about yourself')) {
        return "When you're ready, could you share a bit about yourself? Take your time, there's no pressure.";
      }
      if (originalQuestion.includes('background') || originalQuestion.includes('experience')) {
        return "I'd love to hear about your background when you feel comfortable sharing. What aspects of your experience bring you some satisfaction?";
      }
    } else if (mood === 'positive') {
      // Make questions more energetic
      if (originalQuestion.includes('tell me about yourself')) {
        return "I can tell you're in great spirits! I'd love to hear all about yourself and what makes you so enthusiastic!";
      }
      if (originalQuestion.includes('background') || originalQuestion.includes('experience')) {
        return "With that positive energy, I'm excited to hear about your background! What experiences have you enjoyed most?";
      }
    }
    
    return originalQuestion;
  };

  const nextQuestion = () => {
    // Handle greeting response with mood analysis
    if (currentQuestion === 0 && displayedText.includes('How are you')) {
      const mood = analyzeUserMood(currentAnswer);
      const responses = getAdaptiveResponse(currentAnswer, mood);
      const response = responses[Math.floor(Math.random() * responses.length)];
      
      // Adapt the first interview question based on mood
      const adaptedQuestion = adaptQuestionBasedOnMood(questions[0]?.question || '', mood, currentAnswer);
      
      setTimeout(() => {
        speakAndTypeQuestion(response + adaptedQuestion, true);
      }, 1000);
      
      setCurrentAnswer('');
      return;
    }
    
    const newAnswers = [
      ...answers,
      {
        question_id: questions[currentQuestion].id,
        answer: currentAnswer,
      },
    ];
    setAnswers(newAnswers);
    setLastResponse(currentAnswer);
    setCurrentAnswer('');

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
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

  const skipQuestion = () => {
    const newAnswers = [
      ...answers,
      {
        question_id: questions[currentQuestion].id,
        answer: '',
      },
    ];
    setAnswers(newAnswers);
    setCurrentAnswer('');

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      onComplete(newAnswers);
    }
  };

  // Load voices and setup speech recognition when component mounts
  useEffect(() => {
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
  
  if (!questions || questions.length === 0) {
    return <div>Loading questions...</div>;
  }

  return (
    <div className="interview-container">
      <div className="avatar-section">
        <div className={`video-avatar ${isTyping ? 'speaking' : ''}`}>
          <div className="video-frame">
            <div className="face-container">
              <div className="face">
                <div className="hair"></div>
                <div className="forehead"></div>
                <div className="eyebrow left"></div>
                <div className="eyebrow right"></div>
                <div className="eye left">
                  <div className="eyeball"></div>
                  <div className="pupil"></div>
                </div>
                <div className="eye right">
                  <div className="eyeball"></div>
                  <div className="pupil"></div>
                </div>
                <div className="nose"></div>
                <div className="cheek left"></div>
                <div className="cheek right"></div>
                <div className={`mouth ${isTyping ? 'talking' : ''}`}>
                  <div className="upper-lip"></div>
                  <div className="lower-lip"></div>
                  <div className="teeth"></div>
                </div>
                <div className="chin"></div>
              </div>
              <div className="neck"></div>
              <div className="shoulders">
                <div className="blazer"></div>
                <div className="shirt"></div>
              </div>
            </div>
          </div>
          <div className="video-controls">
            <div className="recording-indicator ${isTyping ? 'active' : ''}"></div>
          </div>
        </div>
        <div className="interviewer-name">Sarah Johnson</div>
        <div className="interviewer-title">Senior Technical Interviewer</div>
        <div className="interviewer-status">
          {isTyping ? (
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
          style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
        ></div>
      </div>
      
      <div className="question-section">
        <div className="question-header">
          <div className="question-counter">
            Question {currentQuestion + 1} of {questions.length}
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
            placeholder={currentQuestion === 0 && displayedText.includes('How are you') ? "Type how you're doing..." : "Share your thoughts..."}
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
                disabled={!currentAnswer.trim() || !answerEnabled}
              >
                {currentQuestion < questions.length - 1 ? 'Next Question' : 'Finish Interview'}
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={skipQuestion}
                disabled={!answerEnabled}
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