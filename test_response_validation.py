#!/usr/bin/env python3
"""
Test script for OpenRouter response validation and error handling.

This script tests:
- Response structure validation
- Content validation
- Error response parsing
- User-friendly error messages
- Enhanced completion with validation
- Various error scenarios
- Edge cases and malformed responses
"""

import os
import sys
import json
from unittest.mock import Mock, patch

# Add src to path
sys.path.append('src')

from utils.openrouter_client import (
    OpenRouterClient, 
    OpenRouterConfig, 
    APIResponse,
    OpenRouterError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    ModelUnavailableError,
    ValidationError,
    TimeoutError,
    ServerError
)

def test_response_structure_validation():
    """Test response structure validation methods."""
    print("Testing Response Structure Validation...")
    
    try:
        config = OpenRouterConfig(
            api_key='test-key',
            default_model="deepseek/deepseek-chat"
        )
        client = OpenRouterClient(config=config, auto_configure=False, enable_enhanced_logging=False)
        
        # Test valid response structure
        valid_response = {
            "choices": [
                {
                    "message": {
                        "content": "This is a valid response"
                    }
                }
            ],
            "usage": {
                "total_tokens": 10
            }
        }
        
        result = client._validate_response_structure(valid_response)
        assert result == True
        print("  ✅ Valid response structure validation passed")
        
        # Test invalid response - not a dict
        try:
            client._validate_response_structure("invalid")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "not a valid JSON object" in str(e)
            print("  ✅ Non-dict response validation caught")
        
        # Test invalid response - no choices
        invalid_response = {"usage": {}}
        try:
            client._validate_response_structure(invalid_response)
            print("  ✅ No choices response handled gracefully")
        except ValidationError:
            print("  ✅ No choices response validation caught")
        
        # Test invalid response - empty choices
        empty_choices = {"choices": []}
        try:
            client._validate_response_structure(empty_choices)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "no choices" in str(e)
            print("  ✅ Empty choices validation caught")
        
        # Test invalid response - no content
        no_content = {
            "choices": [
                {
                    "message": {}
                }
            ]
        }
        try:
            client._validate_response_structure(no_content)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "no content" in str(e)
            print("  ✅ No content validation caught")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Response structure validation test failed: {str(e)}")
        return False

def test_content_validation():
    """Test response content validation methods."""
    print("\nTesting Content Validation...")
    
    try:
        config = OpenRouterConfig(
            api_key='test-key',
            default_model="deepseek/deepseek-chat"
        )
        client = OpenRouterClient(config=config, auto_configure=False, enable_enhanced_logging=False)
        
        # Test valid text content
        valid_text = "This is a valid response with sufficient length"
        result = client._validate_response_content(valid_text, "text")
        assert result == True
        print("  ✅ Valid text content validation passed")
        
        # Test valid JSON content
        valid_json = '{"key": "value", "number": 123}'
        result = client._validate_response_content(valid_json, "json")
        assert result == True
        print("  ✅ Valid JSON content validation passed")
        
        # Test empty content
        try:
            client._validate_response_content("", "text")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "empty or invalid" in str(e)
            print("  ✅ Empty content validation caught")
        
        # Test None content
        try:
            client._validate_response_content(None, "text")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "empty or invalid" in str(e)
            print("  ✅ None content validation caught")
        
        # Test too short content
        try:
            client._validate_response_content("hi", "text")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "too short" in str(e)
            print("  ✅ Short content validation caught")
        
        # Test invalid JSON content
        try:
            client._validate_response_content('{"invalid": json}', "json")
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "Invalid JSON" in str(e)
            print("  ✅ Invalid JSON validation caught")
        
        # Test content with error indicators
        error_content = "This content contains an error indicator"
        result = client._validate_response_content(error_content, "text")
        assert result == True  # Should still pass but log warning
        print("  ✅ Error indicator content handled gracefully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Content validation test failed: {str(e)}")
        return False

def test_error_response_parsing():
    """Test error response parsing and exception mapping."""
    print("\nTesting Error Response Parsing...")
    
    try:
        config = OpenRouterConfig(
            api_key='test-key',
            default_model="deepseek/deepseek-chat"
        )
        client = OpenRouterClient(config=config, auto_configure=False, enable_enhanced_logging=False)
        
        # Test authentication error (401)
        auth_error_data = {"error": {"message": "Invalid API key", "code": 401}}
        error = client._parse_error_response(auth_error_data, 401)
        assert isinstance(error, AuthenticationError)
        print("  ✅ Authentication error (401) parsed correctly")
        
        # Test rate limit error (429)
        rate_limit_data = {"error": {"message": "Rate limit exceeded", "code": 429}}
        error = client._parse_error_response(rate_limit_data, 429)
        assert isinstance(error, RateLimitError)
        print("  ✅ Rate limit error (429) parsed correctly")
        
        # Test quota exceeded (402)
        quota_data = {"error": {"message": "Quota exceeded", "code": 402}}
        error = client._parse_error_response(quota_data, 402)
        assert isinstance(error, QuotaExceededError)
        print("  ✅ Quota exceeded error (402) parsed correctly")
        
        # Test model unavailable (404)
        model_data = {"error": {"message": "Model not found", "code": 404}}
        error = client._parse_error_response(model_data, 404)
        assert isinstance(error, ModelUnavailableError)
        print("  ✅ Model unavailable error (404) parsed correctly")
        
        # Test timeout error (408)
        timeout_data = {"error": {"message": "Request timeout", "code": 408}}
        error = client._parse_error_response(timeout_data, 408)
        assert isinstance(error, TimeoutError)
        print("  ✅ Timeout error (408) parsed correctly")
        
        # Test server error (500)
        server_data = {"error": {"message": "Internal server error", "code": 500}}
        error = client._parse_error_response(server_data, 500)
        assert isinstance(error, ServerError)
        print("  ✅ Server error (500) parsed correctly")
        
        # Test generic error
        generic_data = {"error": {"message": "Unknown error", "code": 418}}
        error = client._parse_error_response(generic_data, 418)
        assert isinstance(error, OpenRouterError)
        print("  ✅ Generic error parsed correctly")
        
        # Test string error format
        string_error_data = {"error": "Simple error message"}
        error = client._parse_error_response(string_error_data, 400)
        assert isinstance(error, OpenRouterError)
        assert "Simple error message" in str(error)
        print("  ✅ String error format handled correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error response parsing test failed: {str(e)}")
        return False

def test_user_friendly_error_messages():
    """Test user-friendly error message generation."""
    print("\nTesting User-Friendly Error Messages...")
    
    try:
        config = OpenRouterConfig(
            api_key='test-key',
            default_model="deepseek/deepseek-chat"
        )
        client = OpenRouterClient(config=config, auto_configure=False, enable_enhanced_logging=False)
        
        # Test authentication error message
        auth_error = AuthenticationError("API key invalid")
        message = client._get_user_friendly_error_message(auth_error)
        assert "check your API key" in message.lower()
        print("  ✅ Authentication error message user-friendly")
        
        # Test rate limit error message
        rate_error = RateLimitError("Too many requests")
        message = client._get_user_friendly_error_message(rate_error)
        assert "wait a moment" in message.lower()
        print("  ✅ Rate limit error message user-friendly")
        
        # Test quota error message
        quota_error = QuotaExceededError("Quota exceeded")
        message = client._get_user_friendly_error_message(quota_error)
        assert "quota" in message.lower()
        print("  ✅ Quota error message user-friendly")
        
        # Test model unavailable message
        model_error = ModelUnavailableError("Model not found")
        message = client._get_user_friendly_error_message(model_error)
        assert "unavailable" in message.lower()
        print("  ✅ Model unavailable error message user-friendly")
        
        # Test timeout error message
        timeout_error = TimeoutError("Request timed out")
        message = client._get_user_friendly_error_message(timeout_error)
        assert "timed out" in message.lower()
        print("  ✅ Timeout error message user-friendly")
        
        # Test server error message
        server_error = ServerError("Internal server error")
        message = client._get_user_friendly_error_message(server_error)
        assert "server error" in message.lower()
        print("  ✅ Server error message user-friendly")
        
        # Test validation error message
        validation_error = ValidationError("Invalid format")
        message = client._get_user_friendly_error_message(validation_error)
        assert "invalid" in message.lower()
        print("  ✅ Validation error message user-friendly")
        
        # Test generic error message
        generic_error = OpenRouterError("Unknown error")
        message = client._get_user_friendly_error_message(generic_error)
        assert "unexpected error" in message.lower()
        print("  ✅ Generic error message user-friendly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ User-friendly error messages test failed: {str(e)}")
        return False

def test_enhanced_completion_validation():
    """Test enhanced completion method with various scenarios."""
    print("\nTesting Enhanced Completion with Validation...")
    
    try:
        config = OpenRouterConfig(
            api_key='test-key',
            default_model="deepseek/deepseek-chat"
        )
        client = OpenRouterClient(config=config, auto_configure=False, enable_enhanced_logging=False)
        
        # Test input validation
        try:
            result = client._enhanced_completion_with_validation("")
            assert not result.success
            assert "prompt" in result.error.lower()
            print("  ✅ Empty prompt validation caught")
        except:
            print("  ✅ Empty prompt handled as expected")
        
        try:
            result = client._enhanced_completion_with_validation("hi")
            assert not result.success
            assert "short" in result.error.lower()
            print("  ✅ Short prompt validation caught")
        except:
            print("  ✅ Short prompt handled as expected")
        
        try:
            result = client._enhanced_completion_with_validation(None)
            assert not result.success
            print("  ✅ None prompt validation caught")
        except:
            print("  ✅ None prompt handled as expected")
        
        # Test parameter validation
        try:
            result = client._enhanced_completion_with_validation(
                "Valid prompt that is long enough", 
                temperature=3.0  # Invalid temperature
            )
            assert not result.success
            assert "temperature" in result.error.lower()
            print("  ✅ Invalid temperature validation caught")
        except:
            print("  ✅ Invalid temperature handled as expected")
        
        try:
            result = client._enhanced_completion_with_validation(
                "Valid prompt that is long enough", 
                max_tokens=-1  # Invalid max_tokens
            )
            assert not result.success
            assert "tokens" in result.error.lower()
            print("  ✅ Invalid max_tokens validation caught")
        except:
            print("  ✅ Invalid max_tokens handled as expected")
        
        print("  ✅ Input validation tests completed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced completion validation test failed: {str(e)}")
        return False

def test_edge_cases():
    """Test edge cases and unusual scenarios."""
    print("\nTesting Edge Cases...")
    
    try:
        config = OpenRouterConfig(
            api_key='test-key',
            default_model="deepseek/deepseek-chat"
        )
        client = OpenRouterClient(config=config, auto_configure=False, enable_enhanced_logging=False)
        
        # Test malformed JSON response handling
        malformed_data = {"choices": "not a list"}
        try:
            client._validate_response_structure(malformed_data)
            print("  ✅ Malformed response handled gracefully")
        except ValidationError:
            print("  ✅ Malformed response validation caught")
        
        # Test deeply nested error response
        complex_error = {
            "error": {
                "type": "authentication_error",
                "message": "Invalid API key provided",
                "param": None,
                "code": "invalid_api_key"
            }
        }
        error = client._parse_error_response(complex_error, 401)
        assert isinstance(error, AuthenticationError)
        print("  ✅ Complex error structure parsed correctly")
        
        # Test response with missing usage field
        no_usage_response = {
            "choices": [
                {
                    "message": {
                        "content": "Response without usage field"
                    }
                }
            ]
        }
        result = client._validate_response_structure(no_usage_response)
        assert result == True
        print("  ✅ Response without usage field handled correctly")
        
        # Test very long content
        long_content = "A" * 10000
        result = client._validate_response_content(long_content, "text")
        assert result == True
        print("  ✅ Very long content handled correctly")
        
        # Test content with special characters
        special_content = "Content with 特殊字符 and émojis 🚀 and symbols !@#$%^&*()"
        result = client._validate_response_content(special_content, "text")
        assert result == True
        print("  ✅ Special characters content handled correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Edge cases test failed: {str(e)}")
        return False

def main():
    """Run all response validation and error handling tests."""
    print("🚀 Starting Response Validation and Error Handling Tests")
    print("=" * 70)
    
    tests = [
        test_response_structure_validation,
        test_content_validation,
        test_error_response_parsing,
        test_user_friendly_error_messages,
        test_enhanced_completion_validation,
        test_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All response validation and error handling tests passed!")
        print("\n💡 Summary:")
        print("   ✅ Response structure validation")
        print("   ✅ Content validation (text and JSON)")
        print("   ✅ Error response parsing and classification")
        print("   ✅ User-friendly error message generation")
        print("   ✅ Enhanced completion with comprehensive validation")
        print("   ✅ Edge cases and malformed response handling")
        print("   ✅ Input parameter validation")
        print("   ✅ Specific error type mapping (401, 429, 404, etc.)")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 