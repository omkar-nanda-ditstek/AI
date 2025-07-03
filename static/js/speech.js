class SpeechManager {
    constructor() {
        this.synthesis = window.speechSynthesis;
        this.recognition = null;
        this.isListening = false;
        this.currentUtterance = null;
        
        // Initialize speech recognition if available
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
        }
    }

    // Text to Speech for Questions
    speakQuestion(text, callback = null) {
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }

        this.currentUtterance = new SpeechSynthesisUtterance(text);
        this.currentUtterance.rate = 0.9;
        this.currentUtterance.pitch = 1;
        this.currentUtterance.volume = 0.8;
        
        this.currentUtterance.onend = () => {
            if (callback) callback();
        };

        this.synthesis.speak(this.currentUtterance);
    }

    // Speech to Text for Answers
    startListening(onResult, onError = null) {
        if (!this.recognition) {
            if (onError) onError('Speech recognition not supported');
            return;
        }

        if (this.isListening) {
            this.stopListening();
            return;
        }

        this.isListening = true;
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (onResult) onResult(transcript);
        };

        this.recognition.onerror = (event) => {
            this.isListening = false;
            if (onError) onError(event.error);
        };

        this.recognition.onend = () => {
            this.isListening = false;
        };

        this.recognition.start();
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }

    stopSpeaking() {
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }
    }

    // Get available voices
    getVoices() {
        return this.synthesis.getVoices();
    }

    // Set voice for questions
    setVoice(voiceIndex) {
        const voices = this.getVoices();
        if (voices[voiceIndex]) {
            this.selectedVoice = voices[voiceIndex];
        }
    }
}

// Initialize global speech manager
window.speechManager = new SpeechManager();