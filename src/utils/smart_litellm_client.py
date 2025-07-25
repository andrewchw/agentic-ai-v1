"""
Smart LiteLLM Client with Free Models Management
==============================================

A wrapper around LiteLLM that automatically handles:
- Free model selection and failover
- Rate limit handling with automatic model switching
- Error recovery and retry logic
- Model health monitoring
"""

import os
import time
import logging
from typing import Any, Dict, Optional, List
import litellm
from litellm import completion
from .free_models_manager import get_free_models_manager, handle_api_failure, handle_api_success

logger = logging.getLogger(__name__)

class SmartLiteLLMClient:
    """Smart LiteLLM client with automatic free model management"""
    
    def __init__(self):
        """Initialize the smart LiteLLM client"""
        self.models_manager = get_free_models_manager()
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # Configure LiteLLM
        litellm.set_verbose = os.getenv("DEBUG", "False").lower() == "true"
        
        # Set OpenRouter API key
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = openrouter_key
        
        logger.info("SmartLiteLLMClient initialized with free models management")
    
    def completion(self, 
                  messages: List[Dict[str, str]], 
                  use_case: str = "general",
                  **kwargs) -> Any:
        """
        Smart completion with automatic model selection and failover
        
        Args:
            messages: List of message dictionaries
            use_case: Type of task ("code", "analysis", "creative", "general", etc.)
            **kwargs: Additional arguments for LiteLLM completion
        
        Returns:
            LiteLLM completion response
        """
        
        # Remove model from kwargs if provided (we'll manage it)
        kwargs.pop('model', None)
        
        last_error = None
        attempted_models = set()
        
        for attempt in range(self.max_retries):
            try:
                # Get the best available model for this use case
                model_id = self.models_manager.get_model_for_litellm(use_case)
                
                # Skip if we've already tried this model in this request
                if model_id in attempted_models:
                    # Force get a different model from working models only
                    working_models = self.models_manager.get_working_models()
                    for key, model in working_models.items():
                        candidate_id = f"openrouter/{model.id}"
                        if candidate_id not in attempted_models:
                            model_id = candidate_id
                            break
                    else:
                        # No more working models to try
                        logger.error("No more working models available to try")
                        break
                
                attempted_models.add(model_id)
                
                logger.debug(f"Attempting completion with model: {model_id} (attempt {attempt + 1})")
                
                # Prepare completion arguments
                completion_args = {
                    'model': model_id,
                    'messages': messages,
                    **kwargs
                }
                
                # Make the API call
                response = completion(**completion_args)
                
                # Success! Update model statistics
                handle_api_success(model_id)
                
                return response
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                logger.warning(f"Model {model_id} failed: {e}")
                
                # Determine error type for better handling
                if "rate" in error_str or "limit" in error_str or "429" in error_str:
                    error_type = "rate_limit"
                elif "auth" in error_str or "401" in error_str or "403" in error_str:
                    error_type = "auth_error"
                elif "timeout" in error_str or "connection" in error_str:
                    error_type = "connection_error"
                else:
                    error_type = "unknown"
                
                # Handle the failure and get next model
                next_model = handle_api_failure(model_id, error_type)
                
                # If this was a rate limit error, wait a bit before retrying
                if error_type == "rate_limit" and attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.info(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                
                # If we've tried all working models, break
                working_models = self.models_manager.get_working_models()
                if len(attempted_models) >= len(working_models):
                    logger.error("All working models have been tried and failed")
                    break
        
        # If we get here, all retries failed
        logger.error(f"All completion attempts failed. Last error: {last_error}")
        raise last_error if last_error else Exception("All free models failed")
    
    def async_completion(self, 
                        messages: List[Dict[str, str]], 
                        use_case: str = "general",
                        **kwargs) -> Any:
        """
        Async completion with smart model selection
        
        Args:
            messages: List of message dictionaries
            use_case: Type of task ("code", "analysis", "creative", "general", etc.)
            **kwargs: Additional arguments for LiteLLM acompletion
        
        Returns:
            LiteLLM async completion response
        """
        # For now, use sync completion
        # TODO: Implement proper async version with acompletion
        return self.completion(messages, use_case, **kwargs)
    
    def get_model_info(self) -> Dict:
        """Get information about current model configuration"""
        current_model = self.models_manager.get_current_model()
        return {
            "current_model": current_model.name,
            "model_id": current_model.id,
            "provider": current_model.provider,
            "description": current_model.description,
            "context_window": current_model.context_window,
            "max_tokens": current_model.max_tokens,
            "failure_count": current_model.failure_count,
            "is_available": self.models_manager._is_model_available(current_model)
        }
    
    def get_all_models_status(self) -> Dict:
        """Get status of all available models"""
        return self.models_manager.get_model_status_summary()
    
    def set_preferred_model(self, model_key: str):
        """Set user's preferred model"""
        self.models_manager.save_user_preference(model_key)
    
    def reset_model_failures(self, model_key: str = None):
        """Reset failure counts for models"""
        self.models_manager.reset_model_failures(model_key)


# Global smart client instance
_smart_client = None

def get_smart_litellm_client() -> SmartLiteLLMClient:
    """Get the global smart LiteLLM client instance"""
    global _smart_client
    if _smart_client is None:
        _smart_client = SmartLiteLLMClient()
    return _smart_client

def smart_completion(messages: List[Dict[str, str]], 
                    use_case: str = "general",
                    **kwargs) -> Any:
    """Convenience function for smart completion"""
    return get_smart_litellm_client().completion(messages, use_case, **kwargs)


# Monkey patch for existing code compatibility
def patch_litellm_for_smart_client():
    """
    Monkey patch litellm.completion to use our smart client
    This allows existing code to benefit from smart model management
    without changes
    """
    original_completion = litellm.completion
    
    def smart_completion_wrapper(*args, **kwargs):
        try:
            # Extract messages - handle both positional and keyword arguments
            messages = None
            
            # Check if messages are in args
            if args and len(args) > 0 and isinstance(args[0], list):
                messages = args[0]
            elif 'messages' in kwargs:
                messages = kwargs['messages']
            
            if messages:
                # Remove 'messages' from kwargs to avoid duplicate argument error
                kwargs_clean = kwargs.copy()
                kwargs_clean.pop('messages', None)
                
                # Use our smart client
                return get_smart_litellm_client().completion(messages, **kwargs_clean)
            else:
                # No messages found, use original
                return original_completion(*args, **kwargs)
            
        except Exception as e:
            # Fallback to original implementation
            logger.warning(f"Smart completion failed, falling back to original: {e}")
            return original_completion(*args, **kwargs)
    
    # Replace the function
    litellm.completion = smart_completion_wrapper
    logger.info("LiteLLM completion patched with smart model management")

# Auto-patch when module is imported (can be disabled by setting environment variable)
if os.getenv("DISABLE_SMART_LITELLM_PATCH", "true").lower() != "true":  # Default to disabled for debugging
    patch_litellm_for_smart_client()
else:
    logger.info("Smart LiteLLM patching disabled via DISABLE_SMART_LITELLM_PATCH=true")
