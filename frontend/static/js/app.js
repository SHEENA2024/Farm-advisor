/**
 * Farm Advisor - Main Application JavaScript
 * Handles UI interactions, API calls, and application state
 */

class FarmAdvisor {
    constructor() {
        this.currentLanguage = 'en';
        this.isListening = false;
        this.speechHandler = null;
        this.apiBaseUrl = window.location.origin;
        
        // Initialize application
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTranslations();
        this.checkSystemStatus();
        this.loadRecentQuestions();
        this.initializeSpeechHandler();
    }

    // Event Binding
    bindEvents() {
        console.log('🔗 Binding events...');

        // Language toggle
        const langToggle = document.getElementById('langToggle');
        if (langToggle) {
            langToggle.addEventListener('click', () => {
                this.toggleLanguage();
            });
        }

        // Action buttons
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                this.showVoiceSection();
            });
        }

        const textBtn = document.getElementById('textBtn');
        if (textBtn) {
            textBtn.addEventListener('click', () => {
                this.showTextSection();
            });
        }

        // Text input
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.handleTextQuestion();
            });
        }

        const questionInput = document.getElementById('questionInput');
        if (questionInput) {
            questionInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleTextQuestion();
                }
            });
        }

        // Voice controls
        const startVoiceBtn = document.getElementById('startVoiceBtn');
        if (startVoiceBtn) {
            startVoiceBtn.addEventListener('click', () => {
                this.startVoiceRecognition();
            });
        }

        const stopVoiceBtn = document.getElementById('stopVoiceBtn');
        if (stopVoiceBtn) {
            stopVoiceBtn.addEventListener('click', () => {
                this.stopVoiceRecognition();
            });
        }

        // Answer controls - Enhanced speaker button
        const speakBtn = document.getElementById('speakBtn');
        if (speakBtn) {
            speakBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🔊 Speaker button clicked');
                this.speakAnswer();
            });
            console.log('✅ Speaker button event bound');
        } else {
            console.error('❌ Speaker button not found');
        }

        const copyBtn = document.getElementById('copyBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                this.copyAnswer();
            });
        }

        const newQuestionBtn = document.getElementById('newQuestionBtn');
        if (newQuestionBtn) {
            newQuestionBtn.addEventListener('click', () => {
                this.resetToHome();
            });
        }

        // Category cards
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', () => {
                const category = card.dataset.category;
                this.handleCategoryClick(category);
            });
        });

        console.log('✅ All events bound successfully');
    }

    // Initialize Speech Handler
    initializeSpeechHandler() {
        if (window.globalSpeechHandler) {
            this.speechHandler = window.globalSpeechHandler;
            this.speechHandler.setLanguage(this.currentLanguage);
            console.log('✅ Speech handler connected');
        } else {
            console.warn('⚠️ Speech handler not available');
        }
    }

    // Language Management
    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'en' ? 'hi' : 'en';
        this.updateLanguageUI();
        this.loadTranslations();
        
        // Update speech handler language
        if (this.speechHandler) {
            this.speechHandler.setLanguage(this.currentLanguage);
        }
    }

    updateLanguageUI() {
        const langText = document.getElementById('langText');
        if (langText) {
            langText.textContent = this.currentLanguage === 'en' ? 'हिंदी' : 'English';
        }
    }

    loadTranslations() {
        const translations = this.getTranslations();
        const elements = document.querySelectorAll('[id]');
        
        elements.forEach(element => {
            const key = element.id;
            if (translations[this.currentLanguage][key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translations[this.currentLanguage][key];
                } else {
                    element.textContent = translations[this.currentLanguage][key];
                }
            }
        });
    }

    getTranslations() {
        return {
            en: {
                welcomeTitle: "Welcome to Farm Advisor",
                welcomeSubtitle: "Get instant agricultural guidance using voice or text - completely offline!",
                quickActionsTitle: "Ask Your Question",
                voiceBtnText: "Ask by Voice",
                textBtnText: "Type Question",
                answerTitle: "Answer",
                questionLabel: "Question:",
                newQuestionText: "Ask Another Question",
                categoriesTitle: "Browse Topics",
                cropPlanningTitle: "Crop Planning",
                cropPlanningDesc: "Planting times and seasons",
                soilTitle: "Soil Management",
                soilDesc: "Testing and improvement",
                irrigationTitle: "Irrigation",
                irrigationDesc: "Water management",
                pestTitle: "Pest Control",
                pestDesc: "Disease management",
                fertilizerTitle: "Fertilizers",
                fertilizerDesc: "Nutrient management",
                weatherTitle: "Weather",
                weatherDesc: "Climate adaptation",
                recentTitle: "Recent Questions",
                recentPlaceholder: "Your recent questions will appear here",
                footerText: "© 2025 Farm Advisor - Offline Agricultural Guidance System",
                loadingText: "Processing your question...",
                questionInput: "Type your farming question here..."
            },
            hi: {
                welcomeTitle: "फार्म एडवाइजर में आपका स्वागत है",
                welcomeSubtitle: "आवाज या टेक्स्ट का उपयोग करके तुरंत कृषि मार्गदर्शन प्राप्त करें - पूरी तरह से ऑफलाइन!",
                quickActionsTitle: "अपना प्रश्न पूछें",
                voiceBtnText: "आवाज से पूछें",
                textBtnText: "प्रश्न टाइप करें",
                answerTitle: "उत्तर",
                questionLabel: "प्रश्न:",
                newQuestionText: "दूसरा प्रश्न पूछें",
                categoriesTitle: "विषय ब्राउज़ करें",
                cropPlanningTitle: "फसल योजना",
                cropPlanningDesc: "रोपण समय और मौसम",
                soilTitle: "मिट्टी प्रबंधन",
                soilDesc: "परीक्षण और सुधार",
                irrigationTitle: "सिंचाई",
                irrigationDesc: "जल प्रबंधन",
                pestTitle: "कीट नियंत्रण",
                pestDesc: "रोग प्रबंधन",
                fertilizerTitle: "उर्वरक",
                fertilizerDesc: "पोषक तत्व प्रबंधन",
                weatherTitle: "मौसम",
                weatherDesc: "जलवायु अनुकूलन",
                recentTitle: "हाल के प्रश्न",
                recentPlaceholder: "आपके हाल के प्रश्न यहाँ दिखाई देंगे",
                footerText: "© 2025 फार्म एडवाइजर - ऑफलाइन कृषि मार्गदर्शन प्रणाली",
                loadingText: "आपके प्रश्न को संसाधित कर रहे हैं...",
                questionInput: "यहाँ अपना कृषि प्रश्न टाइप करें..."
            }
        };
    }

    // System Status
    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/status`);
            const data = await response.json();
            
            this.updateStatusIndicator(data.status === 'online');
            console.log('System status:', data);
            
        } catch (error) {
            console.warn('System status check failed:', error);
            this.updateStatusIndicator(true); // Allow offline operation
        }
    }

    updateStatusIndicator(isOnline) {
        const statusText = document.getElementById('statusText');
        if (statusText) {
            const statusClass = isOnline ? 'status-online' : 'status-offline';
            const statusMessage = isOnline ? 'System Ready' : 'System Offline';
            
            statusText.className = statusClass;
            statusText.innerHTML = `<i class="fas fa-circle"></i> ${statusMessage}`;
        }
    }

    // UI Section Management
    showTextSection() {
        this.hideAllSections();
        const textSection = document.getElementById('textSection');
        if (textSection) {
            textSection.classList.remove('hidden');
        }
        const questionInput = document.getElementById('questionInput');
        if (questionInput) {
            questionInput.focus();
        }
    }

    showVoiceSection() {
        this.hideAllSections();
        const voiceSection = document.getElementById('voiceSection');
        if (voiceSection) {
            voiceSection.classList.remove('hidden');
        }
    }

    showAnswerSection() {
        this.hideAllSections();
        const answerSection = document.getElementById('answerSection');
        if (answerSection) {
            answerSection.classList.remove('hidden');
        }
    }

    hideAllSections() {
        const sections = ['textSection', 'voiceSection', 'answerSection'];
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.add('hidden');
            }
        });
    }

    resetToHome() {
        this.hideAllSections();
        const questionInput = document.getElementById('questionInput');
        if (questionInput) {
            questionInput.value = '';
        }
        this.stopVoiceRecognition();
    }

    // Question Handling
    async handleTextQuestion() {
        const questionInput = document.getElementById('questionInput');
        if (!questionInput) {
            console.error('Question input not found');
            return;
        }

        const question = questionInput.value.trim();
        
        if (!question) {
            this.showToast('Please enter a question', 'warning');
            return;
        }

        this.showLoading(true);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    language: this.currentLanguage
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get answer');
            }

            const data = await response.json();
            this.displayAnswer(data.question, data.answer);
            this.loadRecentQuestions();
            
        } catch (error) {
            console.error('Error asking question:', error);
            this.showToast('Failed to get answer. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async handleCategoryClick(category) {
        const categoryQuestions = {
            crop_planning: {
                en: "When should I plant rice?",
                hi: "मुझे चावल कब लगाना चाहिए?"
            },
            soil_management: {
                en: "How do I test my soil?",
                hi: "मैं अपनी मिट्टी की जांच कैसे करूं?"
            },
            irrigation: {
                en: "What are the benefits of drip irrigation?",
                hi: "ड्रिप सिंचाई के क्या फायदे हैं?"
            },
            pest_disease: {
                en: "How can I control pests naturally?",
                hi: "मैं प्राकृतिक रूप से कीटों को कैसे नियंत्रित कर सकता हूं?"
            },
            fertilizers: {
                en: "What organic fertilizers should I use?",
                hi: "मुझे कौन से जैविक उर्वरक का उपयोग करना चाहिए?"
            },
            weather_climate: {
                en: "How do I protect crops from drought?",
                hi: "मैं सूखे से फसलों की रक्षा कैसे करूं?"
            }
        };

        const question = categoryQuestions[category]?.[this.currentLanguage];
        if (question) {
            const questionInput = document.getElementById('questionInput');
            if (questionInput) {
                questionInput.value = question;
                this.showTextSection();
            }
        }
    }

    // Voice Recognition
    async startVoiceRecognition() {
        if (this.isListening) return;

        try {
            this.isListening = true;
            this.updateVoiceUI(true);
            
            // Use browser speech recognition
            if (this.speechHandler) {
                const success = this.speechHandler.startListening();
                if (success) {
                    this.showToast('🎤 Listening... Please speak now', 'info');
                } else {
                    throw new Error('Failed to start speech recognition');
                }
            } else {
                throw new Error('Speech handler not available');
            }
            
        } catch (error) {
            console.error('Voice recognition error:', error);
            this.showToast('Voice recognition failed', 'error');
            this.stopVoiceRecognition();
        }
    }

    async stopVoiceRecognition() {
        if (!this.isListening) return;

        try {
            if (this.speechHandler) {
                this.speechHandler.stopListening();
            }
        } catch (error) {
            console.warn('Error stopping voice recognition:', error);
        } finally {
            this.isListening = false;
            this.updateVoiceUI(false);
        }
    }

    updateVoiceUI(isListening) {
        const voiceSection = document.getElementById('voiceSection');
        const startBtn = document.getElementById('startVoiceBtn');
        const stopBtn = document.getElementById('stopVoiceBtn');
        const voiceStatus = document.getElementById('voiceStatus');

        if (isListening) {
            voiceSection?.classList.add('listening');
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
            if (voiceStatus) {
                voiceStatus.textContent = this.currentLanguage === 'en' 
                    ? 'Listening... Speak now!' 
                    : 'सुन रहे हैं... अब बोलें!';
            }
        } else {
            voiceSection?.classList.remove('listening');
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
            if (voiceStatus) {
                voiceStatus.textContent = this.currentLanguage === 'en' 
                    ? 'Click to start speaking...' 
                    : 'बोलना शुरू करने के लिए क्लिक करें...';
            }
        }
    }

    // Answer Display
    displayAnswer(question, answer) {
        const questionDisplay = document.getElementById('questionDisplay');
        const answerDisplay = document.getElementById('answerDisplay');
        
        if (questionDisplay) {
            questionDisplay.textContent = question;
        }
        if (answerDisplay) {
            answerDisplay.textContent = answer;
        }
        
        this.showAnswerSection();
        
        console.log('✅ Answer displayed:', {
            question: question,
            answer: answer.substring(0, 100) + '...'
        });
    }

    // Enhanced Speaker Function
    async speakAnswer() {
        console.log('🔊 speakAnswer() called');
        
        const answerDisplay = document.getElementById('answerDisplay');
        if (!answerDisplay) {
            console.error('❌ Answer display element not found');
            this.showToast('Answer display not found', 'error');
            return;
        }
        
        const answer = answerDisplay.textContent || answerDisplay.innerText || '';
        console.log('🔊 Answer text length:', answer.length);
        console.log('🔊 Answer text preview:', answer.substring(0, 100) + '...');
        
        if (!answer || answer.trim().length === 0) {
            console.warn('⚠️ No answer text to speak');
            this.showToast('No answer to speak', 'warning');
            return;
        }

        // Method 1: Try browser speech synthesis directly
        if (window.speechSynthesis) {
            try {
                console.log('🔊 Attempting browser speech synthesis...');
                
                // Stop any current speech
                window.speechSynthesis.cancel();
                
                // Wait a moment for cancel to complete
                setTimeout(() => {
                    const utterance = new SpeechSynthesisUtterance(answer);
                    
                    // Configure for better speech
                    utterance.rate = this.currentLanguage === 'hi' ? 0.7 : 0.8;
                    utterance.pitch = 1.0;
                    utterance.volume = 0.9;
                    utterance.lang = this.currentLanguage === 'hi' ? 'hi-IN' : 'en-US';
                    
                    // Event handlers
                    utterance.onstart = () => {
                        console.log('✅ Speech synthesis started');
                        this.showToast('🔊 Speaking answer...', 'info');
                    };
                    
                    utterance.onend = () => {
                        console.log('✅ Speech synthesis completed');
                    };
                    
                    utterance.onerror = (e) => {
                        console.error('❌ Speech synthesis error:', e);
                        this.showToast('Speech failed: ' + e.error, 'error');
                    };
                    
                    // Speak the answer
                    window.speechSynthesis.speak(utterance);
                    console.log('🔊 Speech synthesis command issued');
                    
                }, 100);
                
                return;
                
            } catch (error) {
                console.error('❌ Browser speech synthesis failed:', error);
            }
        }

        // Method 2: Try speech handler
        if (this.speechHandler && this.speechHandler.speak) {
            try {
                console.log('🔊 Attempting speech handler...');
                const success = this.speechHandler.speak(answer, this.currentLanguage);
                if (success) {
                    console.log('✅ Speech handler succeeded');
                    return;
                }
            } catch (error) {
                console.error('❌ Speech handler failed:', error);
            }
        }

        // Method 3: Fallback to API
        try {
            console.log('🔊 Attempting API speech...');
            const response = await fetch(`${this.apiBaseUrl}/api/speak`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: answer,
                    language: this.currentLanguage
                })
            });

            if (response.ok) {
                console.log('✅ API speech completed');
                this.showToast('🔊 Speaking via API...', 'info');
            } else {
                throw new Error('API speech failed');
            }
        } catch (error) {
            console.error('❌ API speech failed:', error);
            this.showToast('All speech methods failed', 'error');
        }
    }

    async copyAnswer() {
        const answerDisplay = document.getElementById('answerDisplay');
        if (!answerDisplay) return;

        const answer = answerDisplay.textContent || answerDisplay.innerText || '';
        if (!answer) return;

        try {
            await navigator.clipboard.writeText(answer);
            this.showToast('Answer copied to clipboard', 'success');
        } catch (error) {
            console.error('Copy failed:', error);
            this.showToast('Failed to copy answer', 'error');
        }
    }

    // Recent Questions
    async loadRecentQuestions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/history?limit=5`);
            if (!response.ok) return;

            const data = await response.json();
            this.displayRecentQuestions(data.history);
        } catch (error) {
            console.warn('Failed to load recent questions:', error);
        }
    }

    displayRecentQuestions(questions) {
        const container = document.getElementById('recentQuestions');
        if (!container) return;
        
        if (!questions || questions.length === 0) {
            container.innerHTML = `
                <div class="recent-placeholder">
                    <i class="fas fa-history"></i>
                    <p>${this.currentLanguage === 'en' ? 'Your recent questions will appear here' : 'आपके हाल के प्रश्न यहाँ दिखाई देंगे'}</p>
                </div>
            `;
            return;
        }

        container.innerHTML = questions.map(q => `
            <div class="recent-question" onclick="farmAdvisor.selectRecentQuestion('${q.question.replace(/'/g, "\\'")}')">
                <div class="recent-question-text">${q.question}</div>
                <div class="recent-question-meta">
                    <span class="recent-language">${q.language.toUpperCase()}</span>
                    <span class="recent-method">${q.input_method}</span>
                    <span class="recent-time">${this.formatTime(q.timestamp)}</span>
                </div>
            </div>
        `).join('');
    }

    selectRecentQuestion(question) {
        const questionInput = document.getElementById('questionInput');
        if (questionInput) {
            questionInput.value = question;
            this.showTextSection();
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString(this.currentLanguage === 'en' ? 'en-US' : 'hi-IN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // UI Helpers
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }

    showToast(message, type = 'info') {
        console.log(`📢 Toast [${type}]: ${message}`);
        
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slide-out 0.3s ease-out forwards';
                setTimeout(() => {
                    if (toast.parentNode) {
                        container.removeChild(toast);
                    }
                }, 300);
            }
        }, 3000);
    }
}

// Additional CSS for enhanced functionality
const additionalStyles = `
<style>
.recent-question {
    background: rgba(93, 138, 58, 0.05);
    border: 1px solid rgba(93, 138, 58, 0.1);
    border-radius: var(--border-radius-sm);
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: var(--transition);
}

.recent-question:hover {
    background: rgba(93, 138, 58, 0.1);
    transform: translateX(5px);
}

.recent-question-text {
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.recent-question-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    color: var(--text-light);
}

.recent-language,
.recent-method {
    background: var(--leaf-green);
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}

.toast-success { background: var(--success-color); }
.toast-warning { background: var(--warning-color); }
.toast-error { background: var(--danger-color); }
.toast-info { background: var(--info-color); }

@keyframes slide-out {
    to {
        opacity: 0;
        transform: translateX(100%);
    }
}

/* Enhanced speaker button */
.control-btn:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(93, 138, 58, 0.3);
}
</style>
`;

// Inject additional styles
document.head.insertAdjacentHTML('beforeend', additionalStyles);

// Enhanced initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Farm Advisor...');
    
    // Create global instance
    window.farmAdvisor = new FarmAdvisor();
    
    // Test speech synthesis availability
    if (window.speechSynthesis) {
        console.log('✅ Speech synthesis available');
        
        // Test function for debugging
        window.testSpeech = function(text = "Test speech synthesis") {
            console.log('🧪 Testing speech with:', text);
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.8;
            utterance.volume = 0.9;
            utterance.onstart = () => console.log('✅ Test speech started');
            utterance.onend = () => console.log('✅ Test speech ended');
            utterance.onerror = (e) => console.error('❌ Test speech error:', e);
            window.speechSynthesis.speak(utterance);
        };
        
        console.log('🧪 Test function available: window.testSpeech()');
    } else {
        console.error('❌ Speech synthesis not available');
    }
    
    console.log('✅ Farm Advisor initialized successfully');
});

// Service Worker registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}