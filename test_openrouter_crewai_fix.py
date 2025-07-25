#!/usr/bin/env python3
"""
Test script to verify OpenRouter configuration with CrewAI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_openrouter_config():
    """Test OpenRouter configuration"""
    print("🔧 Testing OpenRouter Configuration for CrewAI")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    print(f"✅ OpenRouter API Key found: {api_key[:10]}...")
    
    try:
        # Test basic CrewAI LLM configuration
        from crewai import LLM
        
        # Test Method 1: Direct LLM configuration (recommended approach)
        print("\n🧪 Testing Method 1: Direct LLM Configuration")
        
        test_llm = LLM(
            model="qwen/qwen3-coder:free",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )
        
        print("✅ LLM object created successfully")
        
        # Test basic completion
        print("\n📡 Testing basic completion...")
        
        # Simple test message
        test_prompt = "Hello! Can you respond with just 'OpenRouter working with CrewAI'?"
        
        try:
            # Test the LLM call
            response = test_llm.call(test_prompt)
            print(f"✅ LLM Response: {response[:100]}...")
            return True
            
        except Exception as llm_error:
            print(f"❌ LLM call failed: {llm_error}")
            
            # Check specific error types
            if "AuthenticationError" in str(llm_error):
                print("🔍 Authentication issue detected - checking configuration...")
                print(f"   API Key starts with: {api_key[:15]}...")
                print(f"   API Base URL: https://openrouter.ai/api/v1")
                print(f"   Model: qwen/qwen3-coder:free")
                
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure CrewAI is installed: pip install crewai")
        return False
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🌍 Testing Environment Variables")
    print("-" * 30)
    
    # Set environment variables using Method 1 from the guide
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_MODEL_NAME"] = "qwen/qwen3-coder:free"
    
    print("✅ Environment variables set:")
    print(f"   OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'Not set')[:15]}...")
    print(f"   OPENAI_API_BASE: {os.environ.get('OPENAI_API_BASE', 'Not set')}")
    print(f"   OPENAI_MODEL_NAME: {os.environ.get('OPENAI_MODEL_NAME', 'Not set')}")
    
    return True

if __name__ == "__main__":
    print("🚀 OpenRouter + CrewAI Configuration Test")
    print("=" * 60)
    
    # Test environment setup
    env_success = test_environment_variables()
    
    # Test OpenRouter configuration
    config_success = test_openrouter_config()
    
    print("\n" + "=" * 60)
    if config_success:
        print("✅ SUCCESS: OpenRouter configuration is working with CrewAI!")
        print("💡 You can now use CrewAI with free OpenRouter models.")
    else:
        print("❌ FAILED: OpenRouter configuration needs adjustment.")
        print("💡 Check your API key and model availability.")
    
    print("=" * 60)
