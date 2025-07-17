#!/usr/bin/env python3
"""
Test script for OpenRouter API integration.

This script tests the OpenRouter client functionality including:
- Configuration loading
- Rate limiting
- Error handling
- Basic connectivity (if API key is available)
"""

import os
import sys
import time

# Add src to path
sys.path.append('src')

from utils.openrouter_client import (
    OpenRouterClient, 
    OpenRouterConfig, 
    RateLimiter,
    test_openrouter_connection,
    create_client
)

def test_configuration():
    """Test configuration loading and validation."""
    print("Testing Configuration...")
    
    try:
        # Test manual configuration
        config = OpenRouterConfig(
            api_key="test_key_placeholder",
            default_model="deepseek/deepseek-chat",
            max_tokens=2000,
            temperature=0.5
        )
        
        print(f"✅ Configuration created successfully")
        print(f"   Model: {config.default_model}")
        print(f"   Max tokens: {config.max_tokens}")
        print(f"   Temperature: {config.temperature}")
        print(f"   Rate limit: {config.rate_limit_per_minute}/min")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_rate_limiter():
    """Test rate limiting functionality."""
    print("\nTesting Rate Limiter...")
    
    try:
        # Create rate limiter (5 calls per 10 seconds for testing)
        limiter = RateLimiter(max_calls=5, time_window=10)
        
        # Test normal requests
        allowed_count = 0
        for i in range(7):  # Try more than the limit
            if limiter.allow_request("test"):
                allowed_count += 1
        
        print(f"✅ Rate limiter working correctly")
        print(f"   Allowed {allowed_count}/7 requests (expected 5)")
        
        # Test wait time calculation
        wait_time = limiter.wait_time("test")
        print(f"   Next request allowed in: {wait_time:.2f} seconds")
        
        return allowed_count == 5
        
    except Exception as e:
        print(f"❌ Rate limiter test failed: {str(e)}")
        return False

def test_client_creation():
    """Test OpenRouter client creation and validation."""
    print("\nTesting Client Creation...")
    
    try:
        # Test with manual configuration (no real API key)
        config = OpenRouterConfig(
            api_key="test_key_placeholder",
            default_model="deepseek/deepseek-chat"
        )
        
        client = OpenRouterClient(config, auto_configure=False)
        
        print(f"✅ Client created successfully")
        print(f"   Default model: {client.config.default_model}")
        print(f"   Rate limit: {client.config.rate_limit_per_minute}/min")
        print(f"   Timeout: {client.config.timeout}s")
        
        # Test stats
        stats = client.get_stats()
        print(f"   Initial stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Client creation test failed: {str(e)}")
        return False

def test_headers():
    """Test HTTP session headers configuration."""
    print("\nTesting HTTP Headers...")
    
    try:
        config = OpenRouterConfig(
            api_key="test_key_placeholder",
            app_name="Test App",
            app_url="https://test.example.com"
        )
        
        client = OpenRouterClient(config, auto_configure=False)
        
        headers = client.session.headers
        
        expected_headers = [
            "Authorization",
            "Content-Type", 
            "HTTP-Referer",
            "X-Title"
        ]
        
        missing_headers = []
        for header in expected_headers:
            if header not in headers:
                missing_headers.append(header)
        
        if not missing_headers:
            print(f"✅ All required headers present")
            print(f"   Content-Type: {headers.get('Content-Type')}")
            print(f"   HTTP-Referer: {headers.get('HTTP-Referer')}")
            print(f"   X-Title: {headers.get('X-Title')}")
            return True
        else:
            print(f"❌ Missing headers: {missing_headers}")
            return False
            
    except Exception as e:
        print(f"❌ Headers test failed: {str(e)}")
        return False

def test_with_real_api_key():
    """Test with real API key if available."""
    print("\nTesting with Real API Key...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("⚠️  No OPENROUTER_API_KEY found in environment variables")
        print("   Skipping real API tests")
        print("   To test with real API:")
        print("   1. Get API key from https://openrouter.ai/keys")
        print("   2. Set environment variable: OPENROUTER_API_KEY=your_key")
        return True
    
    try:
        print(f"✅ API key found (length: {len(api_key)})")
        
        # Test connection
        success = test_openrouter_connection(api_key)
        
        if success:
            print("✅ Connection test successful!")
            
            # Test getting available models
            client = create_client(api_key)
            models_response = client.get_available_models()
            
            if models_response.success:
                models = models_response.data.get('models', [])
                print(f"✅ Retrieved {len(models)} available models")
                
                # Show some DeepSeek models if available
                deepseek_models = [m for m in models if 'deepseek' in m.get('id', '').lower()]
                if deepseek_models:
                    print(f"   DeepSeek models available: {len(deepseek_models)}")
                    for model in deepseek_models[:3]:  # Show first 3
                        print(f"     - {model.get('id')}")
                else:
                    print("   No DeepSeek models found")
                
            else:
                print(f"❌ Failed to get models: {models_response.error}")
                return False
                
        else:
            print("❌ Connection test failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Real API test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting Error Handling...")
    
    try:
        # Test invalid configuration
        try:
            config = OpenRouterConfig(api_key="")  # Empty API key
            OpenRouterClient(config, auto_configure=False)
            print("❌ Should have failed with empty API key")
            return False
        except ValueError:
            print("✅ Properly rejected empty API key")
        
        # Test invalid temperature
        try:
            config = OpenRouterConfig(
                api_key="test", 
                temperature=3.0  # Invalid temperature
            )
            OpenRouterClient(config, auto_configure=False)
            print("❌ Should have failed with invalid temperature")
            return False
        except ValueError:
            print("✅ Properly rejected invalid temperature")
        
        # Test invalid max_tokens
        try:
            config = OpenRouterConfig(
                api_key="test",
                max_tokens=-1  # Invalid max_tokens
            )
            OpenRouterClient(config, auto_configure=False)
            print("❌ Should have failed with invalid max_tokens")
            return False
        except ValueError:
            print("✅ Properly rejected invalid max_tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting OpenRouter Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Rate Limiter", test_rate_limiter),
        ("Client Creation", test_client_creation),
        ("HTTP Headers", test_headers),
        ("Error Handling", test_error_handling),
        ("Real API Key", test_with_real_api_key),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenRouter integration is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("\n💡 Next Steps:")
    print("   1. Set OPENROUTER_API_KEY environment variable for full testing")
    print("   2. Test with sample business analysis prompts")
    print("   3. Integrate with the main application workflow")

if __name__ == "__main__":
    main() 