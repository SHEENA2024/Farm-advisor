#!/usr/bin/env python3
"""
Speech Handler - Manages voice recognition and text-to-speech
Browser-based speech recognition with optional TTS fallback
"""

import os
import json
import logging
import threading
import time
from typing import Optional, Dict

# Try importing TTS, but don't require it
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("🔊 Text-to-speech not available - using browser fallback")

# Set speech recognition as browser-based
VOSK_AVAILABLE = False  # We'll use browser speech recognition

logger = logging.getLogger(__name__)

class SpeechHandler:
    def __init__(self):
        self.tts_engine = None
        self.is_listening = False
        self.stop_listening_flag = threading.Event()
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize speech components - browser-based approach"""
        
        # Try to initialize TTS if available
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
                logger.info("Text-to-Speech engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize TTS: {str(e)}")
                self.tts_engine = None
        
        logger.info("Speech handler initialized for browser-based recognition")
    
    def _configure_tts(self):
        """Configure TTS engine settings"""
        if not self.tts_engine:
            return
        
        try:
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Set voice properties
            self.tts_engine.setProperty('rate', 150)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            # Try to set English voice as default
            if voices:
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            logger.error(f"Error configuring TTS: {e}")
    
    def is_available(self) -> bool:
        """Check if speech functionality is available"""
        # Always return True for browser-based speech recognition
        return True
    
    def speak(self, text: str, language: str = 'en') -> bool:
        """Convert text to speech"""
        if not text.strip():
            return False
        
        # Try local TTS first, fallback to browser
        if self.tts_engine:
            try:
                # Configure voice for language if possible
                self._set_voice_for_language(language)
                
                # Speak the text
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
                logger.info(f"Spoke text in {language}: {text[:50]}...")
                return True
                
            except Exception as e:
                logger.error(f"Error in text-to-speech: {str(e)}")
        
        # If local TTS fails, log for browser handling
        logger.info(f"Browser TTS requested for: {text[:50]}...")
        return True  # Let browser handle it
    
    def _set_voice_for_language(self, language: str):
        """Set appropriate voice for language"""
        if not self.tts_engine:
            return
        
        voices = self.tts_engine.getProperty('voices')
        if not voices:
            return
        
        # Language preferences
        language_keywords = {
            'en': ['english', 'en-us', 'en-gb'],
            'hi': ['hindi', 'hi-in', 'indian']
        }
        
        target_keywords = language_keywords.get(language, ['english'])
        
        for voice in voices:
            voice_name = voice.name.lower()
            if any(keyword in voice_name for keyword in target_keywords):
                self.tts_engine.setProperty('voice', voice.id)
                break
    
    def listen(self, language: str = 'en', timeout: int = 10) -> Optional[str]:
        """Listen for voice input - delegated to browser"""
        logger.info(f"Voice recognition requested in {language} - handled by browser")
        
        # This is handled by browser, so we return a placeholder
        # The actual recognition happens in the frontend JavaScript
        return None
    
    def stop_listening(self):
        """Stop current listening session"""
        self.stop_listening_flag.set()
        self.is_listening = False
        logger.info("Voice recognition stop requested")
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return ['en', 'hi']  # Browser supports these
    
    def test_speech_functionality(self) -> Dict[str, bool]:
        """Test speech functionality"""
        results = {
            'tts_available': self.tts_engine is not None,
            'speech_recognition_available': True,  # Browser-based
            'microphone_available': True,  # Browser will check
            'vosk_models_loaded': False,  # Not using Vosk
            'supported_languages': ['en', 'hi'],
            'method': 'browser-based'
        }
        
        return results

# Test function
if __name__ == "__main__":
    handler = SpeechHandler()
    
    # Test TTS if available
    if handler.tts_engine:
        print("Testing TTS...")
        handler.speak("Hello, this is a test of the speech system.", 'en')
    
    print("Speech functionality test results:")
    results = handler.test_speech_functionality()
    for key, value in results.items():
        print(f"  {key}: {value}")