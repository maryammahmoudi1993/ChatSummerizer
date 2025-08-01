#!/usr/bin/env python3
"""
Startup script for Chat Summarizer System
Checks prerequisites and starts the application
"""

import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'redis', 'langchain', 'openai',
        'jinja2', 'transformers', 'torch', 'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
            return False
    
    return True

def check_env_file():
    """Check if environment file exists and has required variables"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("📝 Creating .env file from template...")
        
        if os.path.exists('env_example.txt'):
            with open('env_example.txt', 'r') as f:
                template = f.read()
            
            with open('.env', 'w') as f:
                f.write(template)
            
            print("✅ .env file created from template")
            print("⚠️ Please edit .env file with your OpenAI API key and Redis configuration")
            return False
        else:
            print("❌ env_example.txt not found")
            return False
    
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("⚠️ Please edit .env file with required values")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_redis():
    """Check if Redis server is accessible"""
    try:
        import redis
        r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), 
                       port=int(os.getenv('REDIS_PORT', 6379)))
        r.ping()
        print("✅ Redis server is accessible")
        return True
    except Exception as e:
        print(f"❌ Redis server is not accessible: {e}")
        print("💡 Please start Redis server:")
        print("   - On Linux/Mac: redis-server")
        print("   - On Windows: Use WSL or Docker")
        return False

def check_openai_api():
    """Check if OpenAI API key is valid"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API key not configured")
        print("💡 Please set your OpenAI API key in .env file")
        return False
    
    try:
        import openai
        openai.api_key = api_key
        # Try a simple API call
        response = openai.Model.list()
        print("✅ OpenAI API key is valid")
        return True
    except Exception as e:
        print(f"❌ OpenAI API key is invalid: {e}")
        print("💡 Please check your API key in .env file")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Chat Summarizer System...")
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, 'main.py'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main startup function"""
    print("🔍 Chat Summarizer System - Startup Check")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file),
        ("Redis Server", check_redis),
        ("OpenAI API", check_openai_api),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"\n❌ Startup checks failed: {', '.join(failed_checks)}")
        print("\n💡 Please fix the issues above and try again")
        return False
    
    print("\n✅ All startup checks passed!")
    print("\n🎯 System is ready to start")
    
    # Ask user if they want to start the server
    try:
        response = input("\n🚀 Start the server now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            start_server()
        else:
            print("👋 Server startup cancelled")
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled")
    
    return True

if __name__ == "__main__":
    main() 