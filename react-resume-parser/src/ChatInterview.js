import React, { useState, useEffect } from 'react';
import './ChatInterview.css';

const ChatInterview = ({ questions, sessionId, resumeId, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [answerEnabled, setAnswerEnabled] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [isTypingMessage, setIsTypingMessage] = useState(false);
  const [lastResponse, setLastResponse] = useState('');

  useEffect(() => {
    if (questions && questions.length > 0) {
      setTimeout(() => {
        addChatMessage("Hi! I'm Sarah, and I'm excited to chat with you today. Let's start with our first question.", 'sarah');
        setTimeout(() => {
          speakAndTypeQuestion(questions[currentQuestion]?.question || '');
        }, 1000);
      }, 500);
    }
  }, [questions]);

  const addChatMessage = (message, sender) => {
    const newMessage = {
      id: Date.now(),
      text: message,
      sender: sender,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, newMessage]);
    
    if (sender === 'sarah') {
      speakMessage(message);
    }
  };

  const speakAndTypeQuestion = (text) => {
    setIsTyping(true);
    setAnswerEnabled(false);
    
    if (currentQuestion > 0 && lastResponse) {
      const responses = [
        "That's really interesting!",
        "I see, that makes perfect sense.",
        "Great perspective!",
        "Thanks for sharing that with me."
      ];
      const ack = responses[Math.floor(Math.random() * responses.length)];
      addChatMessage(ack, 'sarah');
      
      setTimeout(() => {
        setIsTypingMessage(true);
        setTimeout(() => {
          setIsTypingMessage(false);
          addChatMessage(text, 'sarah');
        }, 1500);
      }, 1000);
    } else {
      addChatMessage(text, 'sarah');
    }
  };
  
  const speakMessage = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.2;
    utterance.volume = 0.9;
    
    const voices = speechSynthesis.getVoices();
    const femaleVoice = voices.find(voice => 
      voice.name.includes('Female') || 
      voice.name.includes('Samantha') ||
      voice.name.includes('Karen') ||
      voice.gender === 'female'
    ) || voices.find(voice => voice.lang.startsWith('en'));
    
    if (femaleVoice) {
      utterance.voice = femaleVoice;
    }
    
    if (!isMuted) {
      speechSynthesis.speak(utterance);
    }
    
    utterance.onend = () => {
      setIsTyping(false);
      setAnswerEnabled(true);
    };
  };

  const sendUserMessage = () => {
    if (!currentAnswer.trim()) return;
    
    addChatMessage(currentAnswer, 'user');
    
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
    setAnswerEnabled(false);

    if (currentQuestion < questions.length - 1) {
      setTimeout(() => {
        setCurrentQuestion(currentQuestion + 1);
      }, 500);
    } else {
      setTimeout(() => {
        addChatMessage("Thank you so much! That was a great conversation. I'll review everything and get back to you soon. 😊", 'sarah');
        setTimeout(() => onComplete(newAnswers), 2000);
      }, 1000);
    }
  };

  useEffect(() => {
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
      
      recognitionInstance.onerror = () => setIsListening(false);
      recognitionInstance.onend = () => setIsListening(false);
      
      setRecognition(recognitionInstance);
    }
  }, []);

  if (!questions || questions.length === 0) {
    return <div>Loading questions...</div>;
  }

  return (
    <div className="chat-interview-container">
      <div className="chat-header">
        <div className="interviewer-info">
          <div className={`avatar-mini ${isTyping ? 'speaking' : ''}`}>
            <div className="face-mini">
              <div className="hair-mini"></div>
              <div className="eyes-mini"></div>
              <div className={`mouth-mini ${isTyping ? 'talking' : ''}`}></div>
            </div>
          </div>
          <div className="interviewer-details">
            <div className="name">Sarah Johnson</div>
            <div className="status">
              {isTypingMessage ? (
                <span className="typing-status">typing...</span>
              ) : isTyping ? (
                <span className="speaking-status">🎙️ speaking</span>
              ) : (
                <span className="online-status">🟢 online</span>
              )}
            </div>
          </div>
        </div>
        <div className="chat-controls">
          <button className="mute-btn-mini" onClick={() => setIsMuted(!isMuted)}>
            {isMuted ? '🔇' : '🔊'}
          </button>
          <div className="progress-mini">
            {currentQuestion + 1}/{questions.length}
          </div>
        </div>
      </div>
      
      <div className="chat-messages">
        {chatMessages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div className="message-bubble">
              {msg.text}
            </div>
            <div className="message-time">
              {msg.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </div>
          </div>
        ))}
        {isTypingMessage && (
          <div className="message sarah">
            <div className="message-bubble typing-bubble">
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="chat-input-section">
        <div className="input-container">
          <textarea 
            className="chat-input" 
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            placeholder="Type your response..."
            disabled={!answerEnabled}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendUserMessage();
              }
            }}
          />
          <div className="input-controls">
            <button 
              className={`voice-btn ${isListening ? 'listening' : ''}`}
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
            >
              {isListening ? '🛑' : '🎤'}
            </button>
            <button 
              className="send-btn" 
              onClick={sendUserMessage}
              disabled={!currentAnswer.trim() || !answerEnabled}
            >
              ➤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterview;