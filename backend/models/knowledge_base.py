#!/usr/bin/env python3
"""
Knowledge Base - Agricultural knowledge processing and retrieval
Handles multilingual queries and provides contextual farming advice
"""

import json
import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import unicodedata

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self):
        self.data = {}
        self.categories = []
        self.keywords_index = {}
        self.load_data()
        self.build_search_index()
    
    def load_data(self):
        """Load agricultural knowledge base from JSON file"""
        data_file = os.path.join(os.path.dirname(__file__), '../data/agricultural_data.json')
        
        try:
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded knowledge base with {len(self.data.get('categories', []))} categories")
            else:
                # Create default knowledge base
                self.create_default_knowledge_base(data_file)
                logger.info("Created default knowledge base")
            
            # Extract categories
            self.categories = list(self.data.get('categories', {}).keys())
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            self.data = {}
            self.categories = []
    
    def create_default_knowledge_base(self, file_path: str):
        """Create a comprehensive default agricultural knowledge base"""
        default_data = {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-15",
                "languages": ["en", "hi"],
                "total_entries": 200
            },
            "categories": {
                "crop_planning": {
                    "name": {
                        "en": "Crop Planning and Timing",
                        "hi": "फसल योजना और समय"
                    },
                    "entries": [
                        {
                            "id": "rice_planting_time",
                            "question": {
                                "en": ["when to plant rice", "rice planting season", "best time for rice cultivation"],
                                "hi": ["चावल कब लगाएं", "चावल बोने का समय", "धान की खेती का समय"]
                            },
                            "answer": {
                                "en": "Rice should be planted during monsoon season, typically June to July in most regions of India. For Kharif rice, plant after the first good rain when soil moisture is adequate. Transplant 20-25 day old seedlings in well-prepared, puddled fields.",
                                "hi": "चावल मानसून के दौरान लगाना चाहिए, भारत के अधिकांश क्षेत्रों में आमतौर पर जून से जुलाई में। खरीफ चावल के लिए, जब मिट्टी में पर्याप्त नमी हो तो पहली अच्छी बारिश के बाद बोएं। 20-25 दिन पुराने पौधों को तैयार खेत में रोपें।"
                            },
                            "keywords": ["rice", "paddy", "monsoon", "kharif", "चावल", "धान", "खरीफ", "मानसून"]
                        },
                        {
                            "id": "wheat_cultivation",
                            "question": {
                                "en": ["when to sow wheat", "wheat planting time", "rabi wheat season"],
                                "hi": ["गेहूं कब बोएं", "गेहूं बोने का समय", "रबी गेहूं का मौसम"]
                            },
                            "answer": {
                                "en": "Wheat is a Rabi crop, best sown from November to December. The ideal temperature for sowing is 18-25°C. Ensure adequate soil moisture and sow seeds at 2-3 cm depth with proper row spacing of 20-25 cm.",
                                "hi": "गेहूं एक रबी की फसल है, जो नवंबर से दिसंबर में बोई जाती है। बुआई के लिए आदर्श तापमान 18-25°C है। पर्याप्त मिट्टी की नमी सुनिश्चित करें और बीजों को 2-3 सेमी गहराई में 20-25 सेमी की उचित पंक्ति दूरी के साथ बोएं।"
                            },
                            "keywords": ["wheat", "rabi", "november", "december", "गेहूं", "रबी", "नवंबर", "दिसंबर"]
                        }
                    ]
                },
                "soil_management": {
                    "name": {
                        "en": "Soil Management",
                        "hi": "मिट्टी प्रबंधन"
                    },
                    "entries": [
                        {
                            "id": "soil_testing",
                            "question": {
                                "en": ["how to test soil", "soil testing methods", "check soil quality"],
                                "hi": ["मिट्टी की जांच कैसे करें", "भूमि परीक्षण", "मिट्टी की गुणवत्ता"]
                            },
                            "answer": {
                                "en": "Test your soil every 2-3 years. Collect samples from 6-8 inches depth from multiple spots. Test for pH, nitrogen, phosphorus, potassium, and organic matter. Contact your local agriculture extension office or use soil testing kits.",
                                "hi": "हर 2-3 साल में अपनी मिट्टी की जांच करवाएं। कई स्थानों से 6-8 इंच की गहराई से नमूने लें। pH, नाइट्रोजन, फास्फोरस, पोटेशियम और जैविक पदार्थ की जांच कराएं। स्थानीय कृषि विस्तार कार्यालय से संपर्क करें।"
                            },
                            "keywords": ["soil test", "pH", "nitrogen", "phosphorus", "potassium", "मिट्टी जांच", "नाइट्रोजन", "फास्फोरस", "पोटेशियम"]
                        }
                    ]
                }
            },
            "common_questions": {
                "greetings": {
                    "en": ["hello", "hi", "good morning", "good evening", "namaste"],
                    "hi": ["नमस्ते", "नमस्कार", "हैलो", "सुप्रभात", "शुभ संध्या"]
                },
                "help": {
                    "en": ["help", "what can you do", "how to use", "assistance"],
                    "hi": ["सहायता", "मदद", "आप क्या कर सकते हैं", "कैसे उपयोग करें"]
                }
            },
            "responses": {
                "greetings": {
                    "en": "Hello! I'm your agricultural advisor. You can ask me about crop timing, soil management, irrigation, pest control, fertilizers, and weather-related farming questions. How can I help you today?",
                    "hi": "नमस्ते! मैं आपका कृषि सलाहकार हूं। आप मुझसे फसल का समय, मिट्टी प्रबंधन, सिंचाई, कीट नियंत्रण, उर्वरक, और मौसम संबंधी खेती के प्रश्न पूछ सकते हैं। आज मैं आपकी कैसे सहायता कर सकता हूं?"
                },
                "help": {
                    "en": "I can help you with:\n• Crop planting times and seasons\n• Soil management and testing\n• Irrigation and water management\n• Pest and disease control\n• Fertilizer recommendations\n• Weather adaptation strategies\n\nJust ask your question in English or Hindi!",
                    "hi": "मैं इन विषयों में आपकी सहायता कर सकता हूं:\n• फसल लगाने का समय और मौसम\n• मिट्टी प्रबंधन और परीक्षण\n• सिंचाई और जल प्रबंधन\n• कीट और रोग नियंत्रण\n• उर्वरक सिफारिशें\n• मौसम अनुकूलन रणनीतियां\n\nअपना प्रश्न अंग्रेजी या हिंदी में पूछें!"
                },
                "not_found": {
                    "en": "I'm sorry, I don't have specific information about that topic in my knowledge base. Could you please rephrase your question or ask about crop planning, soil management, irrigation, pest control, fertilizers, or weather-related farming topics?",
                    "hi": "क्षमा करें, मेरे ज्ञान आधार में उस विषय के बारे में विशिष्ट जानकारी नहीं है। कृपया अपना प्रश्न दूसरे तरीके से पूछें या फसल योजना, मिट्टी प्रबंधन, सिंचाई, कीट नियंत्रण, उर्वरक, या मौसम संबंधी खेती के विषयों के बारे में पूछें।"
                }
            }
        }
        
        # Save to file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        
        self.data = default_data
    
    def build_search_index(self):
        """Build keyword search index for fast retrieval"""
        self.keywords_index = {}
        
        if not self.data or 'categories' not in self.data:
            return
        
        for category_id, category_data in self.data['categories'].items():
            for entry in category_data.get('entries', []):
                entry_id = entry['id']
                keywords = entry.get('keywords', [])
                
                # Index all keywords for this entry
                for keyword in keywords:
                    keyword_clean = self.normalize_text(keyword.lower())
                    if keyword_clean not in self.keywords_index:
                        self.keywords_index[keyword_clean] = []
                    self.keywords_index[keyword_clean].append({
                        'category': category_id,
                        'entry_id': entry_id,
                        'entry': entry
                    })
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        # Remove diacritics and normalize unicode
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Remove punctuation and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()
    
    def get_answer(self, question: str, language: str = 'en') -> str:
        """Get answer for a given question"""
        if not question.strip():
            return self.get_response('not_found', language)
        
        question_normalized = self.normalize_text(question)
        
        # Check for greetings
        if self.is_greeting(question_normalized, language):
            return self.get_response('greetings', language)
        
        # Check for help requests
        if self.is_help_request(question_normalized, language):
            return self.get_response('help', language)
        
        # Search for matching entries
        matches = self.search_entries(question_normalized, language)
        
        if matches:
            # Return the best match
            best_match = matches[0]
            return best_match['entry']['answer'].get(language, 
                   best_match['entry']['answer'].get('en', ''))
        
        return self.get_response('not_found', language)
    
    def search_entries(self, question: str, language: str) -> List[Dict]:
        """Search for entries matching the question"""
        matches = []
        question_words = question.split()
        
        # Keyword-based search
        for word in question_words:
            if word in self.keywords_index:
                for match in self.keywords_index[word]:
                    if match not in matches:
                        matches.append(match)
        
        # Question pattern matching
        if not matches:
            matches = self.search_by_patterns(question, language)
        
        return matches
    
    def search_by_patterns(self, question: str, language: str) -> List[Dict]:
        """Search by matching question patterns"""
        matches = []
        
        for category_id, category_data in self.data.get('categories', {}).items():
            for entry in category_data.get('entries', []):
                entry_questions = entry.get('question', {}).get(language, [])
                
                for pattern in entry_questions:
                    pattern_normalized = self.normalize_text(pattern)
                    similarity = SequenceMatcher(None, question, pattern_normalized).ratio()
                    
                    if similarity > 0.3:  # Threshold for similarity
                        matches.append({
                            'category': category_id,
                            'entry_id': entry['id'],
                            'entry': entry,
                            'similarity': similarity
                        })
        
        return matches
    
    def is_greeting(self, text: str, language: str) -> bool:
        """Check if text is a greeting"""
        greetings = self.data.get('common_questions', {}).get('greetings', {})
        greeting_words = greetings.get(language, []) + greetings.get('en', [])
        
        for greeting in greeting_words:
            if self.normalize_text(greeting) in text:
                return True
        return False
    
    def is_help_request(self, text: str, language: str) -> bool:
        """Check if text is a help request"""
        help_words = self.data.get('common_questions', {}).get('help', {})
        help_patterns = help_words.get(language, []) + help_words.get('en', [])
        
        for pattern in help_patterns:
            if self.normalize_text(pattern) in text:
                return True
        return False
    
    def get_response(self, response_type: str, language: str) -> str:
        """Get predefined response"""
        responses = self.data.get('responses', {})
        response_data = responses.get(response_type, {})
        return response_data.get(language, response_data.get('en', 'I apologize, but I cannot help with that right now.'))
    
    def get_categories(self) -> List[Dict]:
        """Get all available categories"""
        categories = []
        for category_id, category_data in self.data.get('categories', {}).items():
            categories.append({
                'id': category_id,
                'name': category_data.get('name', {}),
                'entry_count': len(category_data.get('entries', []))
            })
        return categories
    
    def is_loaded(self) -> bool:
        """Check if knowledge base is loaded"""
        return bool(self.data and 'categories' in self.data)