#!/usr/bin/env python3
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

print("🌱 Starting Farm Advisor...")

try:
    from app import FarmAdvisor
    
    advisor = FarmAdvisor()
    
    print("🚀 Server starting on http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    
    # Simple run without deprecated parameters
    advisor.run(host='localhost', port=5000, debug=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Trying alternative...")
    
    # Fallback simple server
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return '''
        <h1>🌱 Farm Advisor</h1>
        <p>System is starting up...</p>
        <p><a href="/test">Test Page</a></p>
        '''
    
    @app.route('/test')
    def test():
        return '<h1>✅ Flask is working!</h1>'
    
    print("🚀 Running in simple mode...")
    app.run(host='localhost', port=5000, debug=True)