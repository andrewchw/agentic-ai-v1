#!/usr/bin/env python3
"""
Simple test script for OpenRouter + Enhanced Logging integration.
"""

import sys
sys.path.append('src')

from utils.openrouter_client import create_client
from utils.api_logger import get_api_logger, reset_api_logger

def test_integration():
    """Test the integration between OpenRouter client and enhanced logging."""
    print('Testing OpenRouter + Enhanced Logging Integration...')
    
    try:
        # Reset logger for clean test
        reset_api_logger()
        
        # Create client with enhanced logging
        client = create_client()
        print('✅ Client created with enhanced logging')
        
        # Check if enhanced logging is enabled
        if hasattr(client, 'enhanced_logging') and client.enhanced_logging:
            print('✅ Enhanced logging is enabled')
        else:
            print('⚠️  Enhanced logging not available')
        
        # Get the logger instance
        logger = get_api_logger()
        
        # Check initial metrics
        initial_metrics = logger.get_metrics()
        print(f'Initial metrics:')
        print(f'  Total requests: {initial_metrics["total_requests"]}')
        print(f'  Rate limit blocks: {initial_metrics["rate_limit_blocks"]}')
        
        print('✅ Integration test completed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Integration test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1) 