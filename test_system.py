#!/usr/bin/env python3
"""
Test script for Chat Summarizer System
This script tests all major components of the system
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_health():
    """Test system health"""
    print("🔍 Testing system health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data['status']}")
            for component, status in health_data['components'].items():
                print(f"   {component}: {'✅' if status else '❌'}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_functionality():
    """Test chat functionality"""
    print("\n💬 Testing chat functionality...")
    
    session_id = f"test_session_{int(time.time())}"
    
    # Test sending messages
    test_messages = [
        {"role": "user", "content": "Hello, I have a question about your product."},
        {"role": "assistant", "content": "Hello! I'd be happy to help you with any questions about our product."},
        {"role": "user", "content": "What are the main features?"},
        {"role": "assistant", "content": "Our product offers advanced analytics, real-time monitoring, and seamless integration with existing systems."},
        {"role": "user", "content": "That sounds great! I'm very interested in purchasing."}
    ]
    
    for i, message in enumerate(test_messages):
        try:
            response = requests.post(f"{BASE_URL}/chat/send", data={
                'session_id': session_id,
                'role': message['role'],
                'content': message['content']
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Message {i+1} sent successfully")
                print(f"   Sentiment: {result['sentiment']} ({result['confidence']['sentiment']:.2f})")
                print(f"   Topic: {result['topic']} ({result['confidence']['topic']:.2f})")
            else:
                print(f"❌ Failed to send message {i+1}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message {i+1}: {e}")
            return False
    
    # Test getting session messages
    try:
        response = requests.get(f"{BASE_URL}/chat/session/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data['messages'])} messages from session")
        else:
            print(f"❌ Failed to get session messages: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting session messages: {e}")
        return False
    
    return session_id

def test_summarization(session_id):
    """Test summarization functionality"""
    print(f"\n📝 Testing summarization for session: {session_id}")
    
    try:
        # Test comprehensive summary
        response = requests.post(f"{BASE_URL}/summary/generate", json={
            'session_id': session_id,
            'max_length': 300
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Comprehensive summary generated ({result['message_count']} messages)")
            print(f"   Summary: {result['summary'][:100]}...")
        else:
            print(f"❌ Failed to generate summary: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return False
    
    try:
        # Test brief summary
        response = requests.get(f"{BASE_URL}/summary/brief/{session_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Brief summary generated")
            print(f"   Summary: {result['summary'][:100]}...")
        else:
            print(f"❌ Failed to generate brief summary: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating brief summary: {e}")
        return False
    
    return True

def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("\n😊 Testing sentiment analysis...")
    
    test_texts = [
        "I love this product! It's amazing!",
        "This is terrible, I hate it.",
        "The product is okay, nothing special."
    ]
    
    for i, text in enumerate(test_texts):
        try:
            response = requests.post(f"{BASE_URL}/sentiment/analyze", json={
                'text': text
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sentiment analysis {i+1}: {result['sentiment']} ({result['confidence']:.2f})")
                print(f"   Text: {text}")
            else:
                print(f"❌ Failed sentiment analysis {i+1}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in sentiment analysis {i+1}: {e}")
            return False
    
    return True

def test_topic_classification():
    """Test topic classification"""
    print("\n🏷️ Testing topic classification...")
    
    test_texts = [
        "I have a complaint about the service quality",
        "Can you help me with technical support?",
        "I want to buy your premium package",
        "What are your pricing options?",
        "Thank you for the great customer service!"
    ]
    
    for i, text in enumerate(test_texts):
        try:
            response = requests.post(f"{BASE_URL}/topic/classify", json={
                'text': text
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Topic classification {i+1}: {result['topic']} ({result['confidence']:.2f})")
                print(f"   Text: {text}")
            else:
                print(f"❌ Failed topic classification {i+1}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in topic classification {i+1}: {e}")
            return False
    
    return True

def test_statistics(session_id):
    """Test statistics functionality"""
    print(f"\n📊 Testing statistics for session: {session_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/stats/session/{session_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Session statistics retrieved")
            print(f"   Total messages: {result['total_messages']}")
            print(f"   User messages: {result['user_messages']}")
            print(f"   Assistant messages: {result['assistant_messages']}")
            
            if result.get('sentiment_distribution'):
                print(f"   Sentiment distribution: {result['sentiment_distribution']}")
            
            if result.get('topic_distribution'):
                print(f"   Topic distribution: {result['topic_distribution']}")
        else:
            print(f"❌ Failed to get session statistics: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting session statistics: {e}")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/stats/overview")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Overview statistics retrieved")
            print(f"   Total sessions: {result['total_sessions']}")
            print(f"   Total messages: {result['total_messages']}")
            print(f"   Avg messages per session: {result['avg_messages_per_session']:.2f}")
        else:
            print(f"❌ Failed to get overview statistics: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting overview statistics: {e}")
        return False
    
    return True

def test_api_documentation():
    """Test API documentation access"""
    print("\n📚 Testing API documentation...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API documentation not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing API documentation: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Chat Summarizer System Tests")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first:")
        print("   python main.py")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Chat Functionality", test_chat_functionality),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Topic Classification", test_topic_classification),
        ("API Documentation", test_api_documentation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if test_name == "Chat Functionality":
                result = test_func()
                if result:
                    results[test_name] = True
                    session_id = result
                else:
                    results[test_name] = False
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Test summarization and statistics if chat test passed
    if results.get("Chat Functionality"):
        results["Summarization"] = test_summarization(session_id)
        results["Statistics"] = test_statistics(session_id)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the configuration and try again.")
    
    print("\n💡 Tips:")
    print("- Make sure Redis server is running")
    print("- Ensure OpenAI API key is set in .env file")
    print("- Check that all required models are downloaded")
    print("- Verify internet connection for model downloads")

if __name__ == "__main__":
    main() 