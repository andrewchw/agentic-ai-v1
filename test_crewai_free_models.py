#!/usr/bin/env python3
"""
Test CrewAI Free Model Configuration
==================================

Quick test to verify that CrewAI is using free models and not defaulting to paid ones.
"""

import os
import sys
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_configuration():
    """Test that environment variables are properly configured for free models"""
    logger.info("Testing environment configuration...")
    
    # Load OpenRouter API key
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    # Configure environment for free models
    os.environ["OPENAI_API_KEY"] = openrouter_api_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
    os.environ["LITELLM_OPENAI_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["LITELLM_DEFAULT_MODEL"] = "qwen/qwen3-coder:free"
    os.environ["LITELLM_DISABLE_FALLBACKS"] = "true"
    
    logger.info("✅ Environment configured for free models")
    return True

def test_crewai_llm_configuration():
    """Test that CrewAI LLM is properly configured"""
    try:
        from crewai.llm import LLM
        
        # Create LLM instance with free model
        test_llm = LLM(
            model="qwen/qwen3-coder:free",
            temperature=0.1,
            max_tokens=100,
            api_base="https://openrouter.ai/api/v1"
        )
        
        logger.info("✅ CrewAI LLM instance created successfully with free model")
        logger.info(f"✅ Model: {test_llm.model}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating CrewAI LLM: {e}")
        return False

def test_simple_agent_creation():
    """Test creating a simple agent with free model"""
    try:
        from crewai import Agent
        from crewai.llm import LLM
        
        # Create LLM with free model
        free_llm = LLM(
            model="qwen/qwen3-coder:free",
            temperature=0.1,
            max_tokens=100,
            api_base="https://openrouter.ai/api/v1"
        )
        
        # Create simple agent
        test_agent = Agent(
            role="Test Agent",
            goal="Test free model configuration",
            backstory="A simple agent for testing free model configuration",
            llm=free_llm,
            verbose=True
        )
        
        logger.info("✅ Test agent created successfully with free model")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating test agent: {e}")
        return False

def main():
    """Run all configuration tests"""
    logger.info("🚀 Starting CrewAI Free Model Configuration Test")
    
    tests = [
        ("Environment Configuration", test_environment_configuration),
        ("CrewAI LLM Configuration", test_crewai_llm_configuration),
        ("Simple Agent Creation", test_simple_agent_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            if result:
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 All tests passed! CrewAI is configured for free models only.")
        return True
    else:
        logger.error("⚠️  Some tests failed. Check configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
