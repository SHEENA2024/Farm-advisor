#!/usr/bin/env python3
"""
Offline Agricultural Advisor - Main Flask Application
Provides voice-enabled farming guidance without internet dependency
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from threading import Thread
import time

# Import custom modules
try:
    from models.speech_handler import SpeechHandler
    from models.knowledge_base import KnowledgeBase
    from models.database import DatabaseManager
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some modules not available: {e}")
    MODELS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FarmAdvisor:
    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder='../frontend',
                        static_folder='../frontend/static')
        CORS(self.app)
        
        # Initialize components
        if MODELS_AVAILABLE:
            self.speech_handler = SpeechHandler()
            self.knowledge_base = KnowledgeBase()
            self.db_manager = DatabaseManager()
        else:
            self.speech_handler = None
            self.knowledge_base = None
            self.db_manager = None
            self._create_simple_responses()
        
        # Setup routes
        self.setup_routes()
        
        # Application state
        self.is_listening = False
    
    def _create_simple_responses(self):
        """Create simple fallback responses when knowledge base is not available"""
        self.simple_responses = {
            'en': {
                'rice': "Rice should be planted during monsoon season, typically June to July in most regions of India. For Kharif rice, plant after the first good rain when soil moisture is adequate. Transplant 20-25 day old seedlings in well-prepared, puddled fields.",
                'wheat': "Wheat is a Rabi crop, best sown from November to December. The ideal temperature for sowing is 18-25°C. Ensure adequate soil moisture and sow seeds at 2-3 cm depth with proper row spacing of 20-25 cm.",
                'soil': "Test your soil every 2-3 years. Collect samples from 6-8 inches depth from multiple spots. Test for pH, nitrogen, phosphorus, potassium, and organic matter. Contact your local agriculture extension office or use soil testing kits.",
                'water': "Best time for irrigation is early morning (5-7 AM) or evening (6-8 PM) to minimize evaporation. Check soil moisture by inserting finger 2-3 inches deep. Water when top soil feels dry but subsoil is still moist.",
                'pest': "Use Integrated Pest Management (IPM): Monitor regularly, encourage beneficial insects, use neem oil, practice crop rotation, maintain field hygiene. Use chemical pesticides only as last resort.",
                'fertilizer': "Organic fertilizers include compost, farmyard manure, vermicompost, bone meal, and green manures. They improve soil structure, retain moisture, and provide slow-release nutrients. Apply 5-10 tons per hectare based on soil test results.",
                'hello': "Hello! I'm your agricultural advisor. You can ask me about crop timing, soil management, irrigation, pest control, fertilizers, and weather-related farming questions. How can I help you today?",
                'help': "I can help you with:\n• Crop planting times and seasons\n• Soil management and testing\n• Irrigation and water management\n• Pest and disease control\n• Fertilizer recommendations\n• Weather adaptation strategies\n\nJust ask your question in English or Hindi!",
                'default': "I can help you with questions about crop planning, soil management, irrigation, pest control, fertilizers, and weather adaptation. Please ask your specific farming question!"
            },
            'hi': {
                'rice': "चावल मानसून के दौरान लगाना चाहिए, भारत के अधिकांश क्षेत्रों में आमतौर पर जून से जुलाई में। खरीफ चावल के लिए, जब मिट्टी में पर्याप्त नमी हो तो पहली अच्छी बारिश के बाद बोएं।",
                'wheat': "गेहूं एक रबी की फसल है, जो नवंबर से दिसंबर में बोई जाती है। बुआई के लिए आदर्श तापमान 18-25°C है।",
                'soil': "हर 2-3 साल में अपनी मिट्टी की जांच करवाएं। कई स्थानों से 6-8 इंच की गहराई से नमूने लें। pH, नाइट्रोजन, फास्फोरस, पोटेशियम और जैविक पदार्थ की जांच कराएं।",
                'water': "सिंचाई का सबसे अच्छा समय सुबह (5-7 बजे) या शाम (6-8 बजे) है ताकि वाष्पीकरण कम हो।",
                'pest': "एकीकृत कीट प्रबंधन (IPM) का उपयोग करें: नियमित निगरानी करें, लाभकारी कीटों को बढ़ावा दें, नीम का तेल उपयोग करें।",
                'fertilizer': "जैविक उर्वरकों में खाद, गोबर की खाद, वर्मी कंपोस्ट, हड्डी का चूर्ण, और हरी खाद शामिल हैं।",
                'hello': "नमस्ते! मैं आपका कृषि सलाहकार हूं। आप मुझसे फसल का समय, मिट्टी प्रबंधन, सिंचाई, कीट नियंत्रण, उर्वरक, और मौसम संबंधी खेती के प्रश्न पूछ सकते हैं।",
                'help': "मैं इन विषयों में आपकी सहायता कर सकता हूं:\n• फसल लगाने का समय और मौसम\n• मिट्टी प्रबंधन और परीक्षण\n• सिंचाई और जल प्रबंधन\n• कीट और रोग नियंत्रण\n• उर्वरक सिफारिशें\n• मौसम अनुकूलन रणनीतियां",
                'default': "मैं फसल योजना, मिट्टी प्रबंधन, सिंचाई, कीट नियंत्रण, उर्वरक, और मौसम अनुकूलन के बारे में प्रश्नों में सहायता कर सकता हूं। कृपया अपना विशिष्ट कृषि प्रश्न पूछें!"
            }
        }
    
    def _get_simple_answer(self, question: str, language: str = 'en') -> str:
        """Get answer using simple keyword matching"""
        question_lower = question.lower()
        responses = self.simple_responses.get(language, self.simple_responses['en'])
        
        # Check for greetings and help
        if any(word in question_lower for word in ['hello', 'hi', 'namaste', 'नमस्ते']):
            return responses.get('hello', responses['default'])
        
        if any(word in question_lower for word in ['help', 'what can you do', 'सहायता', 'मदद']):
            return responses.get('help', responses['default'])
        
        # Check for farming keywords
        keywords = ['rice', 'wheat', 'soil', 'water', 'pest', 'fertilizer', 'चावल', 'गेहूं', 'मिट्टी', 'पानी', 'कीट', 'खाद']
        
        for keyword in keywords:
            if keyword in question_lower:
                # Map Hindi keywords to English
                keyword_map = {
                    'चावल': 'rice', 'गेहूं': 'wheat', 'मिट्टी': 'soil', 
                    'पानी': 'water', 'कीट': 'pest', 'खाद': 'fertilizer'
                }
                lookup_key = keyword_map.get(keyword, keyword)
                
                if lookup_key in responses:
                    return responses[lookup_key]
        
        return responses['default']
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve main interface"""
            try:
                return render_template('index.html')
            except Exception as e:
                logger.error(f"Error serving index.html: {e}")
                return f'''
                <html>
                <head><title>Farm Advisor</title></head>
                <body>
                    <h1>🌱 Farm Advisor</h1>
                    <p>System is starting up...</p>
                    <p>Error: {str(e)}</p>
                </body>
                </html>
                ''', 200
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            try:
                return send_from_directory('../frontend/static', filename)
            except Exception as e:
                logger.error(f"Error serving static file {filename}: {e}")
                return "File not found", 404
        
        @self.app.route('/api/status')
        def status():
            """System status check"""
            return jsonify({
                'status': 'online',
                'speech_available': True,  # Always True for browser-based speech
                'database_loaded': self.knowledge_base.is_loaded() if self.knowledge_base else True,
                'timestamp': time.time(),
                'speech_method': 'browser',
                'models_available': MODELS_AVAILABLE
            })
        
        @self.app.route('/api/ask', methods=['POST'])
        def ask_question():
            """Process text-based questions"""
            try:
                data = request.get_json()
                question = data.get('question', '').strip()
                language = data.get('language', 'en')
                
                if not question:
                    return jsonify({'error': 'No question provided'}), 400
                
                # Get answer from knowledge base or simple responses
                if self.knowledge_base:
                    answer = self.knowledge_base.get_answer(question, language)
                else:
                    answer = self._get_simple_answer(question, language)
                
                # Log interaction if database available
                if self.db_manager:
                    self.db_manager.log_interaction(question, answer, 'text', language)
                
                return jsonify({
                    'question': question,
                    'answer': answer,
                    'language': language,
                    'timestamp': time.time()
                })
                
            except Exception as e:
                logger.error(f"Error processing question: {str(e)}")
                return jsonify({'error': 'Failed to process question'}), 500
        
        @self.app.route('/api/voice/start', methods=['POST'])
        def start_voice_recognition():
            """Start voice recognition - browser-based"""
            try:
                data = request.get_json() or {}
                language = data.get('language', 'en')
                
                logger.info(f"Voice recognition requested in {language}")
                
                return jsonify({
                    'status': 'listening_started',
                    'method': 'browser',
                    'language': language
                })
                
            except Exception as e:
                logger.error(f"Error starting voice recognition: {str(e)}")
                return jsonify({'error': 'Failed to start voice recognition'}), 500
        
        @self.app.route('/api/voice/stop', methods=['POST'])
        def stop_voice_recognition():
            """Stop voice recognition"""
            return jsonify({'status': 'listening_stopped'})
        
        @self.app.route('/api/voice/status')
        def voice_status():
            """Get voice recognition status"""
            return jsonify({
                'is_listening': self.is_listening,
                'speech_available': True,
                'method': 'browser'
            })
        
        @self.app.route('/api/speak', methods=['POST'])
        def speak_text():
            """Convert text to speech"""
            try:
                data = request.get_json()
                text = data.get('text', '').strip()
                language = data.get('language', 'en')
                
                if not text:
                    return jsonify({'error': 'No text provided'}), 400
                
                # Try local TTS, fallback to browser
                if self.speech_handler:
                    self.speech_handler.speak(text, language)
                
                return jsonify({
                    'status': 'speech_completed',
                    'method': 'browser'
                })
                
            except Exception as e:
                logger.error(f"Error in text-to-speech: {str(e)}")
                return jsonify({'error': 'Failed to convert text to speech'}), 500
        
        @self.app.route('/api/history')
        def get_history():
            """Get interaction history"""
            try:
                if self.db_manager:
                    limit = request.args.get('limit', 10, type=int)
                    history = self.db_manager.get_interaction_history(limit)
                    return jsonify({'history': history})
                else:
                    return jsonify({'history': []})
            except Exception as e:
                logger.error(f"Error fetching history: {str(e)}")
                return jsonify({'error': 'Failed to fetch history'}), 500
        
        @self.app.route('/api/categories')
        def get_categories():
            """Get available question categories"""
            try:
                if self.knowledge_base:
                    categories = self.knowledge_base.get_categories()
                    return jsonify({'categories': categories})
                else:
                    # Return simple categories
                    categories = [
                        {'id': 'crop_planning', 'name': {'en': 'Crop Planning', 'hi': 'फसल योजना'}},
                        {'id': 'soil_management', 'name': {'en': 'Soil Management', 'hi': 'मिट्टी प्रबंधन'}},
                        {'id': 'irrigation', 'name': {'en': 'Irrigation', 'hi': 'सिंचाई'}},
                        {'id': 'pest_disease', 'name': {'en': 'Pest Control', 'hi': 'कीट नियंत्रण'}},
                        {'id': 'fertilizers', 'name': {'en': 'Fertilizers', 'hi': 'उर्वरक'}},
                        {'id': 'weather_climate', 'name': {'en': 'Weather', 'hi': 'मौसम'}}
                    ]
                    return jsonify({'categories': categories})
            except Exception as e:
                logger.error(f"Error fetching categories: {str(e)}")
                return jsonify({'error': 'Failed to fetch categories'}), 500
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the Flask application"""
        logger.info(f"Starting Farm Advisor on http://{host}:{port}")
        logger.info(f"Speech method: browser-based")
        logger.info(f"Models available: {MODELS_AVAILABLE}")
        
        self.app.run(host=host, port=port, debug=debug)

def create_app():
    """Application factory"""
    advisor = FarmAdvisor()
    return advisor.app

if __name__ == '__main__':
    # Create and run the application
    advisor = FarmAdvisor()
    advisor.run(debug=True)