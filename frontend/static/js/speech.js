/**
 * Enhanced Speech Handler - Optimized for Edge with TTS
 */

class SpeechHandler {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.currentLanguage = 'en';
        this.voices = [];
        
        console.log('🎤 Initializing Enhanced Speech Handler...');
        this.initializeSpeechRecognition();
        this.loadVoices();
        this.initializeTTS();
    }

    initializeSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.setupRecognition();
            console.log('✅ Speech Recognition initialized');
        } else {
            console.error('❌ Speech recognition not supported');
        }
    }

    initializeTTS() {
        if (this.synthesis) {
            console.log('✅ Text-to-Speech available');
            
            // Wait for voices to load
            if (this.synthesis.getVoices().length === 0) {
                this.synthesis.addEventListener('voiceschanged', () => {
                    this.loadVoices();
                });
            }
        } else {
            console.error('❌ Text-to-Speech not available');
        }
    }

    loadVoices() {
        if (this.synthesis) {
            this.voices = this.synthesis.getVoices();
            console.log('🔊 Loaded voices:', this.voices.length);
            
            // Log available voices for debugging
            this.voices.forEach((voice, index) => {
                console.log(`Voice ${index}: ${voice.name} (${voice.lang})`);
            });
        }
    }

    setupRecognition() {
        if (!this.recognition) return;

        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;
        this.recognition.lang = 'en-US';
        
        this.recognition.onstart = () => {
            console.log('🎤 Speech recognition started');
            this.isListening = true;
            this.updateVoiceUI(true);
            this.showToast('🎤 Listening... Speak now!', 'info');
        };

        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (interimTranscript) {
                this.updateStatus(`Hearing: "${interimTranscript}"`);
            }

            if (finalTranscript) {
                console.log('✅ Final transcript:', finalTranscript);
                this.handleVoiceResult(finalTranscript.trim());
            }
        };

        this.recognition.onerror = (event) => {
            console.error('🚫 Speech recognition error:', event.error);
            this.handleVoiceError(event.error);
        };

        this.recognition.onend = () => {
            console.log('🛑 Speech recognition ended');
            this.isListening = false;
            this.updateVoiceUI(false);
        };
    }

    startListening() {
        console.log('🎤 Attempting to start listening...');
        
        if (!this.recognition) {
            this.showBrowserError();
            return false;
        }

        if (this.isListening) {
            console.log('⚠️ Already listening');
            return false;
        }

        try {
            this.recognition.lang = this.currentLanguage === 'hi' ? 'hi-IN' : 'en-US';
            this.recognition.start();
            this.updateStatus('Starting... Please allow microphone access');
            return true;
        } catch (error) {
            console.error('❌ Failed to start recognition:', error);
            this.handleVoiceError('start_failed');
            return false;
        }
    }

    stopListening() {
        console.log('🛑 Stopping recognition...');
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        this.isListening = false;
        this.updateVoiceUI(false);
    }

    // Enhanced Text-to-Speech
    speak(text, language = 'en') {
        if (!this.synthesis || !text.trim()) {
            console.warn('🔇 Speech synthesis not available or no text provided');
            return false;
        }

        console.log('🔊 Speaking text:', text.substring(0, 50) + '...');

        // Stop any current speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        
        // Find appropriate voice
        const voice = this.findVoiceForLanguage(language);
        if (voice) {
            utterance.voice = voice;
            console.log('🔊 Using voice:', voice.name);
        }
        
        // Configure speech parameters
        utterance.rate = language === 'hi' ? 0.7 : 0.8;  // Slower for Hindi
        utterance.pitch = 1.0;
        utterance.volume = 0.9;
        utterance.lang = language === 'hi' ? 'hi-IN' : 'en-US';

        // Event handlers
        utterance.onstart = () => {
            console.log('🔊 Text-to-speech started');
            this.showToast('🔊 Speaking answer...', 'info');
        };
        
        utterance.onend = () => {
            console.log('✅ Text-to-speech completed');
        };
        
        utterance.onerror = (e) => {
            console.error('🚫 Text-to-speech error:', e);
            this.showToast('Speech playback failed', 'error');
        };

        // Speak the text
        this.synthesis.speak(utterance);
        return true;
    }

    findVoiceForLanguage(language) {
        if (!this.voices || this.voices.length === 0) {
            this.loadVoices();
            return null;
        }

        // Language preferences
        const preferences = {
            'en': ['en-US', 'en-GB', 'en'],
            'hi': ['hi-IN', 'hi']
        };

        const langPrefs = preferences[language] || preferences['en'];

        // Find best matching voice
        for (const pref of langPrefs) {
            const voice = this.voices.find(v => 
                v.lang.toLowerCase().startsWith(pref.toLowerCase())
            );
            if (voice) {
                return voice;
            }
        }

        // Fallback to first available voice
        return this.voices[0] || null;
    }

    handleVoiceResult(transcript) {
        console.log('✅ Processing voice result:', transcript);
        
        const questionInput = document.getElementById('questionInput');
        if (questionInput) {
            questionInput.value = transcript;
        }

        this.updateStatus(`✅ Recognized: "${transcript}"`);
        this.showToast(`Voice recognized: "${transcript}"`, 'success');
        
        setTimeout(() => {
            if (window.farmAdvisor) {
                console.log('🔄 Auto-processing question...');
                window.farmAdvisor.showTextSection();
                window.farmAdvisor.handleTextQuestion();
            }
        }, 1500);
    }

    handleVoiceError(error) {
        console.error('🚫 Speech Error:', error);
        
        let errorMessage = 'Speech recognition failed';
        let solution = '';
        
        switch (error) {
            case 'no-speech':
                errorMessage = 'No speech detected';
                solution = 'Please speak clearly and try again';
                break;
            case 'audio-capture':
                errorMessage = 'Microphone not accessible';
                solution = 'Check microphone connection';
                break;
            case 'not-allowed':
                errorMessage = 'Microphone permission denied';
                solution = 'Allow microphone access in browser';
                break;
            default:
                errorMessage = `Speech Error: ${error}`;
                solution = 'Try refreshing the page';
        }

        this.updateStatus(`❌ ${errorMessage}`);
        this.showToast(errorMessage, 'error');
        
        setTimeout(() => {
            this.updateStatus(`💡 ${solution}`);
        }, 2000);
    }

    updateVoiceUI(isListening) {
        const voiceSection = document.getElementById('voiceSection');
        const startBtn = document.getElementById('startVoiceBtn');
        const stopBtn = document.getElementById('stopVoiceBtn');

        if (isListening) {
            voiceSection?.classList.add('listening');
            if (startBtn) {
                startBtn.disabled = true;
                startBtn.textContent = 'Listening...';
            }
            if (stopBtn) {
                stopBtn.disabled = false;
            }
        } else {
            voiceSection?.classList.remove('listening');
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.innerHTML = '<i class="fas fa-play"></i> Start';
            }
            if (stopBtn) {
                stopBtn.disabled = true;
            }
        }
    }

    updateStatus(message) {
        const voiceStatus = document.getElementById('voiceStatus');
        if (voiceStatus) {
            voiceStatus.textContent = message;
        }
        console.log('📢 Status:', message);
    }

    showToast(message, type = 'info') {
        if (window.farmAdvisor) {
            window.farmAdvisor.showToast(message, type);
        }
        console.log(`📢 Toast [${type}]:`, message);
    }

    showBrowserError() {
        const message = 'Speech recognition not available in this browser';
        this.updateStatus(message);
        this.showToast('Voice not supported - use text input', 'warning');
    }

    setLanguage(language) {
        this.currentLanguage = language;
        console.log('🌐 Language set to:', language);
    }

    // Test TTS functionality
    testTTS() {
        const testText = this.currentLanguage === 'hi' ? 
            'नमस्ते, यह एक परीक्षण है।' : 
            'Hello, this is a test.';
        
        console.log('🧪 Testing TTS...');
        return this.speak(testText, this.currentLanguage);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Enhanced Speech Handler...');
    
    const speechHandler = new SpeechHandler();
    window.globalSpeechHandler = speechHandler;
    
    // Connect voice buttons
    const startVoiceBtn = document.getElementById('startVoiceBtn');
    const stopVoiceBtn = document.getElementById('stopVoiceBtn');
    
    if (startVoiceBtn) {
        startVoiceBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('🎤 Start button clicked');
            speechHandler.startListening();
        });
    }
    
    if (stopVoiceBtn) {
        stopVoiceBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('🛑 Stop button clicked');
            speechHandler.stopListening();
        });
    }
    
    // Test speech capabilities
    console.log('🔍 Speech Support Check:');
    console.log('  - Recognition:', !!(window.SpeechRecognition || window.webkitSpeechRecognition));
    console.log('  - Synthesis:', !!window.speechSynthesis);
    
    // Test TTS after 2 seconds
    setTimeout(() => {
        if (speechHandler.synthesis) {
            console.log('🧪 TTS test available - you can test by clicking the speaker icon');
        }
    }, 2000);
});