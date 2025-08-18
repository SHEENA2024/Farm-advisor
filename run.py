#!/usr/bin/env python3
"""
Farm Advisor - Main Application Runner
Offline Agricultural Guidance System
"""

import sys
import os
import platform
import webbrowser
import time
import signal
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🌱 FARM ADVISOR - Offline Agricultural Guidance 🚜       ║
║                                                              ║
║    Professional farming guidance at your fingertips         ║
║    • Voice questions in English & Hindi                     ║
║    • Comprehensive agricultural knowledge                   ║
║    • Completely offline operation                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main application runner"""
    try:
        # Print banner
        print_banner()
        
        print("\n🔄 Starting Farm Advisor application...")
        
        try:
            from app import FarmAdvisor
        except ImportError as e:
            print(f"❌ Failed to import application: {e}")
            print("💡 Ensure you're in the correct directory")
            sys.exit(1)
        
        # Create application instance
        advisor = FarmAdvisor()
        
        print("\n" + "=" * 60)
        print("🚀 FARM ADVISOR IS RUNNING!")
        print("=" * 60)
        print("\n🌐 Access Information:")
        print("   Local URL:  http://127.0.0.1:5000")
        print("   Local URL:  http://localhost:5000")
        print("\n🎤 Features Available:")
        print("   • Voice questions in English & Hindi")
        print("   • Text-based agricultural guidance")
        print("   • Browse by farming categories")
        print("   • Completely offline operation")
        print("\n🛑 To Stop:")
        print("   Press Ctrl+C in this terminal")
        print("\n" + "=" * 60)
        
        # Start the application
        try:
            advisor.run(
                host='127.0.0.1',
                port=5000,
                debug=False,
                threaded=True
            )
        except OSError as e:
            if "Address already in use" in str(e):
                print("\n❌ Port 5000 is already in use")
                print("💡 Try stopping other applications using port 5000")
            else:
                print(f"❌ Network error: {e}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        print("👋 Thanks for using Farm Advisor!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Check the error details above")
        sys.exit(1)

if __name__ == '__main__':
    main()