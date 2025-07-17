"""
OpenRouter API Integration for Agentic AI Revenue Assistant

This module provides a comprehensive client for integrating with OpenRouter API
to access DeepSeek and other LLM capabilities for business analysis tasks.

Key Features:
- Secure API key authentication
- Configurable HTTP client with proper headers
- Error handling and retries
- Rate limiting protection
- Request/response logging
- DeepSeek model configuration
- Business analysis prompt formatting
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from collections import defaultdict

# Import enhanced logging
try:
    from .api_logger import get_api_logger
    ENHANCED_LOGGING_AVAILABLE = True
except ImportError:
    ENHANCED_LOGGING_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Enhanced error types for better error handling
class OpenRouterError(Exception):
    """Base exception for OpenRouter API errors."""
    pass

class AuthenticationError(OpenRouterError):
    """Authentication failed - invalid API key or credentials."""
    pass

class RateLimitError(OpenRouterError):
    """Rate limit exceeded."""
    pass

class QuotaExceededError(OpenRouterError):
    """API quota exceeded."""
    pass

class ModelUnavailableError(OpenRouterError):
    """Requested model is not available."""
    pass

class ValidationError(OpenRouterError):
    """Request or response validation failed."""
    pass

class TimeoutError(OpenRouterError):
    """Request timed out."""
    pass

class ServerError(OpenRouterError):
    """Server-side error occurred."""
    pass


@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter API client."""
    
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "deepseek/deepseek-chat"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    rate_limit_per_minute: int = 60
    app_name: str = "Agentic AI Revenue Assistant"
    app_url: str = "https://github.com/agentic-ai/revenue-assistant"


@dataclass
class APIResponse:
    """Standardized API response wrapper."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    request_id: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class RateLimiter:
    """Thread-safe rate limiter using token bucket algorithm."""
    
    def __init__(self, max_calls: int, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds (default: 60 for per-minute limiting)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)
        self.lock = threading.Lock()
    
    def allow_request(self, identifier: str = "default") -> bool:
        """
        Check if request is allowed within rate limits.
        
        Args:
            identifier: Unique identifier for rate limiting (default: "default")
            
        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            
            # Ensure identifier exists
            if identifier not in self.calls:
                self.calls[identifier] = []
            
            # Clean old entries more efficiently
            cutoff_time = now - self.time_window
            self.calls[identifier] = [
                call_time for call_time in self.calls[identifier]
                if call_time > cutoff_time
            ]
            
            # Check if we can make another call
            current_count = len(self.calls[identifier])
            if current_count < self.max_calls:
                self.calls[identifier].append(now)
                return True
            
            return False
    
    def wait_time(self, identifier: str = "default") -> float:
        """
        Get the time to wait before next request is allowed.
        
        Args:
            identifier: Unique identifier for rate limiting
            
        Returns:
            Time to wait in seconds
        """
        with self.lock:
            if not self.calls[identifier]:
                return 0.0
            
            oldest_call = min(self.calls[identifier])
            wait_time = self.time_window - (time.time() - oldest_call)
            return max(0.0, wait_time)


class OpenRouterClient:
    """
    OpenRouter API client for business analysis tasks.
    
    Provides secure, rate-limited access to DeepSeek and other LLMs
    through OpenRouter's unified API interface.
    """
    
    def __init__(self, config: Optional[OpenRouterConfig] = None, auto_configure: bool = True, enable_enhanced_logging: bool = True):
        """
        Initialize OpenRouter client.
        
        Args:
            config: Custom configuration (will auto-detect from env if None)
            auto_configure: Whether to automatically configure from environment
            enable_enhanced_logging: Whether to use enhanced API logging
        """
        if config is None and auto_configure:
            config = self._load_config_from_env()
        elif config is None:
            raise ValueError("Configuration must be provided or auto_configure must be True")
        
        self.config = config
        
        # Validate configuration
        self._validate_config()
        
        # Initialize components
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(
            max_calls=self.config.rate_limit_per_minute,
            time_window=60
        )
        
        # Enhanced logging setup
        self.enhanced_logging = enable_enhanced_logging and ENHANCED_LOGGING_AVAILABLE
        if self.enhanced_logging:
            self.api_logger = get_api_logger()
            logger.info("Enhanced API logging enabled")
        else:
            self.api_logger = None
            if enable_enhanced_logging:
                logger.warning("Enhanced logging requested but not available")
        
        # Request tracking
        self.request_count = 0
        self.total_tokens_used = 0
        
        logger.info(f"OpenRouter client initialized for model: {self.config.default_model}")
    
    def _load_config_from_env(self) -> OpenRouterConfig:
        """Load configuration from environment variables."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required. "
                "Get your API key from https://openrouter.ai/keys"
            )
        
        return OpenRouterConfig(
            api_key=api_key,
            default_model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat"),
            max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.7")),
            timeout=int(os.getenv("OPENROUTER_TIMEOUT", "30")),
            max_retries=int(os.getenv("OPENROUTER_MAX_RETRIES", "3")),
            rate_limit_per_minute=int(os.getenv("OPENROUTER_RATE_LIMIT", "60")),
            app_name=os.getenv("OPENROUTER_APP_NAME", "Agentic AI Revenue Assistant"),
            app_url=os.getenv("OPENROUTER_APP_URL", "https://github.com/agentic-ai/revenue-assistant")
        )
    
    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        if not self.config.api_key:
            raise ValueError("API key is required")
        
        if not self.config.base_url:
            raise ValueError("Base URL is required")
        
        if self.config.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        
        if not 0 <= self.config.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
    
    def _create_session(self) -> requests.Session:
        """Create configured HTTP session with retries and proper headers."""
        session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.app_url,
            "X-Title": self.config.app_name
        })
        
        return session
    
    def _wait_for_rate_limit(self) -> None:
        """Wait if rate limit is exceeded."""
        if not self.rate_limiter.allow_request():
            wait_time = self.rate_limiter.wait_time()
            if wait_time > 0:
                # Enhanced logging - log rate limit event
                if self.enhanced_logging and self.api_logger:
                    self.api_logger.log_rate_limit_event(
                        event_type="blocked",
                        identifier="default",
                        requests_in_window=self.config.rate_limit_per_minute,
                        max_requests=self.config.rate_limit_per_minute,
                        wait_time=wait_time
                    )
                
                logger.warning(f"Rate limit exceeded. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        else:
            # Enhanced logging - log allowed request
            if self.enhanced_logging and self.api_logger:
                # Get current window usage (approximation)
                current_requests = min(self.request_count, self.config.rate_limit_per_minute)
                self.api_logger.log_rate_limit_event(
                    event_type="allowed",
                    identifier="default",
                    requests_in_window=current_requests,
                    max_requests=self.config.rate_limit_per_minute
                )
    
    def test_connection(self) -> APIResponse:
        """
        Test connection to OpenRouter API.
        
        Returns:
            APIResponse indicating success or failure
        """
        try:
            self._wait_for_rate_limit()
            
            # Make a simple test request to get available models
            response = self.session.get(
                f"{self.config.base_url}/models",
                timeout=self.config.timeout
            )
            
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Connection test successful. Available models: {len(data.get('data', []))}")
                
                return APIResponse(
                    success=True,
                    data={"models_available": len(data.get('data', []))},
                    request_id=response.headers.get('x-request-id')
                )
            else:
                error_msg = f"Connection test failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                return APIResponse(
                    success=False,
                    error=error_msg,
                    request_id=response.headers.get('x-request-id')
                )
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection test failed: {str(e)}"
            logger.error(error_msg)
            
            return APIResponse(
                success=False,
                error=error_msg
            )
    
    def get_available_models(self) -> APIResponse:
        """
        Get list of available models from OpenRouter.
        
        Returns:
            APIResponse with model information
        """
        try:
            self._wait_for_rate_limit()
            
            response = self.session.get(
                f"{self.config.base_url}/models",
                timeout=self.config.timeout
            )
            
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                
                logger.info(f"Retrieved {len(models)} available models")
                
                return APIResponse(
                    success=True,
                    data={"models": models},
                    request_id=response.headers.get('x-request-id')
                )
            else:
                error_msg = f"Failed to get models: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                return APIResponse(
                    success=False,
                    error=error_msg,
                    request_id=response.headers.get('x-request-id')
                )
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get models: {str(e)}"
            logger.error(error_msg)
            
            return APIResponse(
                success=False,
                error=error_msg
            )
    
    def completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> APIResponse:
        """
        Generate text completion using OpenRouter API.
        
        Args:
            prompt: Input text prompt
            model: Model to use (defaults to configured model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters for the API
        
        Returns:
            APIResponse with completion result
        """
        request_id = None
        
        try:
            self._wait_for_rate_limit()
            
            # Prepare request payload
            payload = {
                "model": model or self.config.default_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature if temperature is not None else self.config.temperature,
                **kwargs
            }
            
            url = f"{self.config.base_url}/chat/completions"
            
            # Enhanced logging - log request
            if self.enhanced_logging and self.api_logger:
                # Convert headers to string dict for logging
                headers_dict = {k: str(v) for k, v in self.session.headers.items()}
                request_id = self.api_logger.log_request(
                    method="POST",
                    url=url,
                    headers=headers_dict,
                    payload=payload
                )
            
            # Log request (without sensitive data)
            logger.info(f"Making completion request to model: {payload['model']}")
            logger.debug(f"Request payload: {json.dumps({k: v for k, v in payload.items() if k != 'messages'})}")
            
            # Make API request
            response = self.session.post(
                url,
                json=payload,
                timeout=self.config.timeout
            )
            
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response information
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                usage = data.get('usage', {})
                tokens_used = usage.get('total_tokens', 0)
                
                self.total_tokens_used += tokens_used
                
                # Enhanced logging - log response
                if self.enhanced_logging and self.api_logger and request_id:
                    self.api_logger.log_response(
                        request_id=request_id,
                        status_code=response.status_code,
                        response_data=data
                    )
                
                logger.info(f"Completion successful. Tokens used: {tokens_used}")
                
                return APIResponse(
                    success=True,
                    data={
                        "content": content,
                        "usage": usage,
                        "model": data.get('model'),
                        "full_response": data
                    },
                    model_used=data.get('model'),
                    tokens_used=tokens_used,
                    request_id=response.headers.get('x-request-id')
                )
            else:
                error_msg = f"Completion failed: {response.status_code} - {response.text}"
                
                # Enhanced logging - log error response
                if self.enhanced_logging and self.api_logger and request_id:
                    self.api_logger.log_response(
                        request_id=request_id,
                        status_code=response.status_code,
                        error_message=error_msg
                    )
                
                logger.error(error_msg)
                
                return APIResponse(
                    success=False,
                    error=error_msg,
                    request_id=response.headers.get('x-request-id')
                )
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Completion request failed: {str(e)}"
            
            # Enhanced logging - log exception
            if self.enhanced_logging and self.api_logger and request_id:
                self.api_logger.log_response(
                    request_id=request_id,
                    status_code=0,  # Use 0 for connection errors
                    error_message=error_msg
                )
            
            logger.error(error_msg)
            
            return APIResponse(
                success=False,
                error=error_msg
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client usage statistics.
        
        Returns:
            Dictionary with usage stats
        """
        return {
            "requests_made": self.request_count,
            "total_tokens_used": self.total_tokens_used,
            "configured_model": self.config.default_model,
            "rate_limit_per_minute": self.config.rate_limit_per_minute
        }

    # Response Validation and Error Handling Methods
    
    def _validate_response_structure(self, response_data: Dict[str, Any]) -> bool:
        """
        Validate the basic structure of an OpenRouter API response.
        
        Args:
            response_data: Raw response data from API
            
        Returns:
            True if structure is valid, False otherwise
            
        Raises:
            ValidationError: If response structure is invalid
        """
        try:
            # Check for required top-level fields
            if not isinstance(response_data, dict):
                raise ValidationError("Response is not a valid JSON object")
            
            # For chat completions, validate required structure
            if 'choices' in response_data:
                choices = response_data.get('choices', [])
                if not isinstance(choices, list) or len(choices) == 0:
                    raise ValidationError("Response contains no choices")
                
                # Validate first choice structure
                first_choice = choices[0]
                if not isinstance(first_choice, dict):
                    raise ValidationError("Choice is not a valid object")
                
                # Check for message content
                message = first_choice.get('message', {})
                if not isinstance(message, dict):
                    raise ValidationError("Choice message is not a valid object")
                
                # Validate content exists
                content = message.get('content')
                if content is None:
                    raise ValidationError("Response contains no content")
                
                logger.debug("Response structure validation passed")
                return True
                
            # For other response types, check for error field
            elif 'error' in response_data:
                return False  # Error responses are handled separately
                
            else:
                logger.warning("Unknown response structure, proceeding with caution")
                return True
                
        except Exception as e:
            logger.error(f"Response validation failed: {str(e)}")
            raise ValidationError(f"Response validation failed: {str(e)}")
    
    def _validate_response_content(self, content: Optional[str], expected_format: Optional[str] = None) -> bool:
        """
        Validate the content of a response.
        
        Args:
            content: The response content to validate
            expected_format: Expected format (e.g., 'json', 'text')
            
        Returns:
            True if content is valid
            
        Raises:
            ValidationError: If content validation fails
        """
        try:
            if not content or not isinstance(content, str):
                raise ValidationError("Response content is empty or invalid")
            
            # Check for minimum content length
            if len(content.strip()) < 3:
                raise ValidationError("Response content is too short")
            
            # Validate JSON format if expected
            if expected_format == 'json':
                try:
                    json.loads(content)
                    logger.debug("JSON content validation passed")
                except json.JSONDecodeError as e:
                    raise ValidationError(f"Invalid JSON content: {str(e)}")
            
            # Check for obvious error indicators in content
            error_indicators = ['error', 'failed', 'invalid', 'unauthorized']
            content_lower = content.lower()
            
            for indicator in error_indicators:
                if indicator in content_lower and len(content) < 100:
                    logger.warning(f"Content contains potential error indicator: {indicator}")
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Content validation failed: {str(e)}")
    
    def _parse_error_response(self, response_data: Dict[str, Any], status_code: int) -> OpenRouterError:
        """
        Parse error response and return appropriate exception.
        
        Args:
            response_data: Error response data
            status_code: HTTP status code
            
        Returns:
            Appropriate OpenRouterError subclass
        """
        try:
            # Extract error information
            error_info = response_data.get('error', {})
            if isinstance(error_info, str):
                error_message = error_info
                error_code = status_code
            else:
                error_message = error_info.get('message', 'Unknown error')
                error_code = error_info.get('code', status_code)
            
            # Map status codes to specific exceptions
            if status_code == 401:
                return AuthenticationError(f"Authentication failed: {error_message}")
            elif status_code == 429:
                return RateLimitError(f"Rate limit exceeded: {error_message}")
            elif status_code == 402 or status_code == 403:
                return QuotaExceededError(f"Quota exceeded: {error_message}")
            elif status_code == 404:
                return ModelUnavailableError(f"Model not found: {error_message}")
            elif status_code == 408 or status_code == 504:
                return TimeoutError(f"Request timed out: {error_message}")
            elif status_code >= 500:
                return ServerError(f"Server error ({status_code}): {error_message}")
            else:
                return OpenRouterError(f"API error ({status_code}): {error_message}")
                
        except Exception as e:
            logger.error(f"Error parsing failed: {str(e)}")
            return OpenRouterError(f"Unknown error (status {status_code})")
    
    def _get_user_friendly_error_message(self, error: OpenRouterError) -> str:
        """
        Convert technical error into user-friendly message.
        
        Args:
            error: The OpenRouter error
            
        Returns:
            User-friendly error message
        """
        if isinstance(error, AuthenticationError):
            return "Authentication failed. Please check your API key and try again."
        elif isinstance(error, RateLimitError):
            return "Too many requests. Please wait a moment and try again."
        elif isinstance(error, QuotaExceededError):
            return "API quota exceeded. Please check your usage limits."
        elif isinstance(error, ModelUnavailableError):
            return "The requested AI model is currently unavailable. Please try again later."
        elif isinstance(error, TimeoutError):
            return "Request timed out. Please check your connection and try again."
        elif isinstance(error, ServerError):
            return "Server error occurred. Please try again later."
        elif isinstance(error, ValidationError):
            return "Invalid request or response format. Please check your input."
        else:
            return "An unexpected error occurred. Please try again later."
    
    def _enhanced_completion_with_validation(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        expected_format: Optional[str] = None,
        **kwargs
    ) -> APIResponse:
        """
        Enhanced completion method with comprehensive validation and error handling.
        
        Args:
            prompt: Input text prompt
            model: Model to use (defaults to configured model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            expected_format: Expected response format ('json', 'text')
            **kwargs: Additional parameters for the API
        
        Returns:
            APIResponse with enhanced validation and error handling
        """
        request_id = None
        
        try:
            # Input validation
            if not prompt or not isinstance(prompt, str):
                raise ValidationError("Prompt must be a non-empty string")
            
            if len(prompt.strip()) < 3:
                raise ValidationError("Prompt is too short")
            
            # Wait for rate limit
            self._wait_for_rate_limit()
            
            # Prepare request payload with validation
            payload = {
                "model": model or self.config.default_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature if temperature is not None else self.config.temperature,
                **kwargs
            }
            
            # Validate temperature and max_tokens
            if not (0 <= payload["temperature"] <= 2):
                raise ValidationError("Temperature must be between 0 and 2")
            
            if payload["max_tokens"] <= 0:
                raise ValidationError("Max tokens must be positive")
            
            url = f"{self.config.base_url}/chat/completions"
            
            # Enhanced logging - log request
            if self.enhanced_logging and self.api_logger:
                headers_dict = {k: str(v) for k, v in self.session.headers.items()}
                request_id = self.api_logger.log_request(
                    method="POST",
                    url=url,
                    headers=headers_dict,
                    payload=payload
                )
            
            logger.info(f"Making validated completion request to model: {payload['model']}")
            
            # Make API request
            response = self.session.post(
                url,
                json=payload,
                timeout=self.config.timeout
            )
            
            self.request_count += 1
            
            # Enhanced response handling
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validate response structure
                    self._validate_response_structure(data)
                    
                    # Extract response information
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    usage = data.get('usage', {})
                    tokens_used = usage.get('total_tokens', 0)
                    
                    # Validate content
                    self._validate_response_content(content, expected_format)
                    
                    self.total_tokens_used += tokens_used
                    
                    # Enhanced logging - log successful response
                    if self.enhanced_logging and self.api_logger and request_id:
                        self.api_logger.log_response(
                            request_id=request_id,
                            status_code=response.status_code,
                            response_data=data
                        )
                    
                    logger.info(f"Validated completion successful. Tokens used: {tokens_used}")
                    
                    return APIResponse(
                        success=True,
                        data={
                            "content": content,
                            "usage": usage,
                            "model": data.get('model'),
                            "full_response": data,
                            "validated": True
                        },
                        model_used=data.get('model'),
                        tokens_used=tokens_used,
                        request_id=response.headers.get('x-request-id')
                    )
                    
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON response: {str(e)}"
                    logger.error(error_msg)
                    
                    if self.enhanced_logging and self.api_logger and request_id:
                        self.api_logger.log_response(
                            request_id=request_id,
                            status_code=response.status_code,
                            error_message=error_msg
                        )
                    
                    raise ValidationError(error_msg)
                    
                except ValidationError as e:
                    logger.error(f"Response validation failed: {str(e)}")
                    
                    if self.enhanced_logging and self.api_logger and request_id:
                        self.api_logger.log_response(
                            request_id=request_id,
                            status_code=response.status_code,
                            error_message=str(e)
                        )
                    
                    return APIResponse(
                        success=False,
                        error=self._get_user_friendly_error_message(e),
                        request_id=response.headers.get('x-request-id')
                    )
            else:
                # Handle error responses
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    error_data = {"error": response.text}
                
                api_error = self._parse_error_response(error_data, response.status_code)
                user_friendly_msg = self._get_user_friendly_error_message(api_error)
                
                # Enhanced logging - log error response
                if self.enhanced_logging and self.api_logger and request_id:
                    self.api_logger.log_response(
                        request_id=request_id,
                        status_code=response.status_code,
                        error_message=str(api_error)
                    )
                
                logger.error(f"API error: {api_error}")
                
                return APIResponse(
                    success=False,
                    error=user_friendly_msg,
                    request_id=response.headers.get('x-request-id')
                )
                
        except requests.exceptions.Timeout as e:
            timeout_error = TimeoutError(f"Request timed out: {str(e)}")
            user_friendly_msg = self._get_user_friendly_error_message(timeout_error)
            
            if self.enhanced_logging and self.api_logger and request_id:
                self.api_logger.log_response(
                    request_id=request_id,
                    status_code=0,
                    error_message=str(timeout_error)
                )
            
            logger.error(f"Timeout error: {timeout_error}")
            
            return APIResponse(
                success=False,
                error=user_friendly_msg
            )
            
        except requests.exceptions.RequestException as e:
            connection_error = OpenRouterError(f"Connection failed: {str(e)}")
            user_friendly_msg = "Connection failed. Please check your internet connection and try again."
            
            if self.enhanced_logging and self.api_logger and request_id:
                self.api_logger.log_response(
                    request_id=request_id,
                    status_code=0,
                    error_message=str(connection_error)
                )
            
            logger.error(f"Connection error: {connection_error}")
            
            return APIResponse(
                success=False,
                error=user_friendly_msg
            )
            
        except (ValidationError, OpenRouterError) as e:
            user_friendly_msg = self._get_user_friendly_error_message(e)
            
            if self.enhanced_logging and self.api_logger and request_id:
                self.api_logger.log_response(
                    request_id=request_id,
                    status_code=0,
                    error_message=str(e)
                )
            
            logger.error(f"Validation/API error: {e}")
            
            return APIResponse(
                success=False,
                error=user_friendly_msg
            )
            
        except Exception as e:
            unexpected_error = OpenRouterError(f"Unexpected error: {str(e)}")
            user_friendly_msg = self._get_user_friendly_error_message(unexpected_error)
            
            if self.enhanced_logging and self.api_logger and request_id:
                self.api_logger.log_response(
                    request_id=request_id,
                    status_code=0,
                    error_message=str(unexpected_error)
                )
            
            logger.error(f"Unexpected error: {unexpected_error}")
            
            return APIResponse(
                success=False,
                error=user_friendly_msg
            )

    # Business Analysis Methods for Revenue Assistant
    
    def analyze_customer_patterns(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        additional_context: str = ""
    ) -> APIResponse:
        """
        Analyze customer purchase patterns for lead generation.
        
        Args:
            customer_data: Customer profile information (pseudonymized)
            purchase_history: List of customer purchase records
            additional_context: Optional additional context for analysis
            
        Returns:
            APIResponse with pattern analysis results
        """
        prompt = self._format_customer_pattern_prompt(
            customer_data, purchase_history, additional_context
        )
        
        return self._enhanced_completion_with_validation(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=1500,
            expected_format="json"
        )
    
    def score_lead_priority(
        self,
        customer_profile: Dict[str, Any],
        engagement_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]]
    ) -> APIResponse:
        """
        Generate lead priority scoring based on customer data.
        
        Args:
            customer_profile: Customer profile information
            engagement_data: Customer engagement metrics
            purchase_history: Historical purchase data
            
        Returns:
            APIResponse with priority scoring and reasoning
        """
        prompt = self._format_lead_scoring_prompt(
            customer_profile, engagement_data, purchase_history
        )
        
        return self._enhanced_completion_with_validation(
            prompt=prompt,
            temperature=0.2,  # Very low temperature for consistent scoring
            max_tokens=1000,
            expected_format="json"
        )
    
    def generate_sales_recommendations(
        self,
        customer_analysis: Dict[str, Any],
        available_offers: List[Dict[str, Any]],
        context: str = "Three HK telecom offerings"
    ) -> APIResponse:
        """
        Generate actionable sales recommendations based on customer analysis.
        
        Args:
            customer_analysis: Results from customer pattern analysis
            available_offers: List of available Three HK offers
            context: Business context for recommendations
            
        Returns:
            APIResponse with sales recommendations
        """
        prompt = self._format_sales_recommendations_prompt(
            customer_analysis, available_offers, context
        )
        
        return self._enhanced_completion_with_validation(
            prompt=prompt,
            temperature=0.4,  # Moderate temperature for creative recommendations
            max_tokens=2000,
            expected_format="json"
        )
    
    # Private prompt formatting methods
    
    def _format_customer_pattern_prompt(
        self,
        customer_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]],
        additional_context: str = ""
    ) -> str:
        """Format prompt for customer pattern analysis."""
        
        prompt = f"""# Customer Pattern Analysis for Lead Generation

## Task
Analyze the customer data and purchase history to identify key patterns, behaviors, and opportunities for revenue growth in the Hong Kong telecom market.

## Customer Profile
{self._format_data_for_prompt(customer_data)}

## Purchase History
{self._format_purchase_history_for_prompt(purchase_history)}

{f"## Additional Context\\n{additional_context}\\n" if additional_context else ""}

## Analysis Requirements
Please provide a comprehensive analysis including:

1. **Purchase Patterns**: Identify key trends in customer spending, frequency, and product preferences
2. **Behavioral Insights**: Analyze customer engagement and loyalty indicators
3. **Market Segment**: Classify customer into relevant telecom market segments
4. **Growth Opportunities**: Identify potential upsell/cross-sell opportunities
5. **Risk Assessment**: Evaluate churn risk and retention factors
6. **Recommendation Priority**: Suggest priority level for sales outreach

## Response Format
Provide your analysis in JSON format with the following structure:
```json
{{
    "customer_segment": "string",
    "purchase_patterns": {{
        "frequency": "string",
        "average_spend": "string",
        "preferred_categories": ["array of strings"],
        "seasonality": "string"
    }},
    "behavioral_insights": {{
        "engagement_level": "high/medium/low",
        "loyalty_indicators": ["array of indicators"],
        "communication_preferences": "string"
    }},
    "opportunities": {{
        "upsell_potential": "high/medium/low",
        "cross_sell_categories": ["array of strings"],
        "estimated_value": "string"
    }},
    "risk_factors": {{
        "churn_risk": "high/medium/low",
        "retention_strategies": ["array of strategies"]
    }},
    "priority_score": "1-10 scale",
    "key_insights": ["array of key insights"],
    "next_actions": ["array of recommended actions"]
}}
```

Focus on actionable insights relevant to Hong Kong telecom market dynamics and Three HK's service offerings."""
        
        return prompt
    
    def _format_lead_scoring_prompt(
        self,
        customer_profile: Dict[str, Any],
        engagement_data: Dict[str, Any],
        purchase_history: List[Dict[str, Any]]
    ) -> str:
        """Format prompt for lead priority scoring."""
        
        prompt = f"""# Lead Priority Scoring for Revenue Assistant

## Task
Calculate a comprehensive lead priority score (1-100) based on customer profile, engagement metrics, and purchase history for Hong Kong telecom sales optimization.

## Customer Profile
{self._format_data_for_prompt(customer_profile)}

## Engagement Data
{self._format_data_for_prompt(engagement_data)}

## Purchase History Summary
{self._format_purchase_history_for_prompt(purchase_history)}

## Scoring Criteria
Consider the following factors in your scoring:

### Revenue Potential (30%)
- Historical spend patterns
- Account value growth trends
- Upsell/cross-sell opportunities

### Engagement Level (25%)
- Recent interaction frequency
- Response rates to communications
- Service usage patterns

### Buying Propensity (20%)
- Purchase recency and frequency
- Product adoption rate
- Decision-making timeline

### Account Health (15%)
- Payment history
- Service satisfaction indicators
- Support ticket patterns

### Market Fit (10%)
- Alignment with Three HK target segments
- Geographic and demographic factors
- Competitive positioning

## Response Format
Provide your scoring in JSON format:
```json
{{
    "overall_score": 0-100,
    "component_scores": {{
        "revenue_potential": 0-30,
        "engagement_level": 0-25,
        "buying_propensity": 0-20,
        "account_health": 0-15,
        "market_fit": 0-10
    }},
    "priority_tier": "High/Medium/Low",
    "confidence_level": "High/Medium/Low",
    "key_factors": ["array of primary scoring factors"],
    "risk_factors": ["array of potential concerns"],
    "recommended_timeline": "Immediate/Short-term/Long-term",
    "sales_approach": "string describing recommended approach"
}}
```

Ensure scoring is calibrated for Hong Kong telecom market conditions and Three HK's business model."""
        
        return prompt
    
    def _format_sales_recommendations_prompt(
        self,
        customer_analysis: Dict[str, Any],
        available_offers: List[Dict[str, Any]],
        context: str
    ) -> str:
        """Format prompt for sales recommendations."""
        
        prompt = f"""# Sales Recommendations for {context}

## Task
Generate specific, actionable sales recommendations based on customer analysis and available offers for maximum revenue impact.

## Customer Analysis Results
{self._format_data_for_prompt(customer_analysis)}

## Available Offers
{self._format_offers_for_prompt(available_offers)}

## Recommendation Requirements
Create targeted recommendations that:

1. **Match Customer Needs**: Align with identified patterns and preferences
2. **Maximize Revenue**: Prioritize high-value opportunities
3. **Ensure Feasibility**: Consider customer's capacity and willingness
4. **Minimize Risk**: Account for potential objections or concerns
5. **Support Retention**: Strengthen long-term customer relationship

## Response Format
Provide recommendations in JSON format:
```json
{{
    "primary_recommendations": [
        {{
            "offer_id": "string",
            "offer_name": "string",
            "recommendation_type": "upsell/cross-sell/retention/new",
            "priority": "high/medium/low",
            "expected_value": "estimated revenue impact",
            "confidence": "high/medium/low",
            "reasoning": "why this offer fits the customer",
            "presentation_strategy": "how to present this offer",
            "objection_handling": "potential objections and responses",
            "timing": "when to approach (immediate/short-term/long-term)"
        }}
    ],
    "alternative_options": [
        {{
            "offer_id": "string",
            "offer_name": "string",
            "conditions": "when to consider this alternative"
        }}
    ],
    "personalization_notes": {{
        "communication_style": "preferred approach based on customer profile",
        "key_value_propositions": ["array of relevant benefits"],
        "customization_opportunities": ["ways to tailor the offer"]
    }},
    "success_metrics": {{
        "primary_kpis": ["metrics to track"],
        "success_indicators": ["signs of positive response"],
        "follow_up_triggers": ["when to follow up"]
    }},
    "overall_strategy": "comprehensive approach summary",
    "estimated_close_probability": "percentage likelihood of success"
}}
```

Focus on practical, executable recommendations that sales teams can implement immediately in the Hong Kong telecom market."""
        
        return prompt
    
    def _format_data_for_prompt(self, data: Dict[str, Any]) -> str:
        """Format dictionary data for inclusion in prompts."""
        if not data:
            return "No data provided"
        
        formatted_lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                formatted_lines.append(f"- {key}: {json.dumps(value, indent=2)}")
            else:
                formatted_lines.append(f"- {key}: {value}")
        
        return "\n".join(formatted_lines)
    
    def _format_purchase_history_for_prompt(self, purchase_history: List[Dict[str, Any]]) -> str:
        """Format purchase history for inclusion in prompts."""
        if not purchase_history:
            return "No purchase history available"
        
        formatted_history = []
        for i, purchase in enumerate(purchase_history[:10], 1):  # Limit to last 10 purchases
            formatted_history.append(f"Purchase {i}: {json.dumps(purchase, indent=2)}")
        
        if len(purchase_history) > 10:
            formatted_history.append(f"... and {len(purchase_history) - 10} more purchases")
        
        return "\n".join(formatted_history)
    
    def _format_offers_for_prompt(self, offers: List[Dict[str, Any]]) -> str:
        """Format available offers for inclusion in prompts."""
        if not offers:
            return "No offers provided"
        
        formatted_offers = []
        for i, offer in enumerate(offers, 1):
            formatted_offers.append(f"Offer {i}: {json.dumps(offer, indent=2)}")
        
        return "\n".join(formatted_offers)

    # Enhanced DeepSeek-specific configuration methods
    
    def configure_for_business_analysis(self) -> None:
        """Configure client specifically for business analysis tasks."""
        # Adjust settings for business analysis
        self.config.temperature = 0.3  # Lower temperature for consistent analysis
        self.config.max_tokens = 2000   # Increased tokens for detailed analysis
        
        logger.info("Client configured for business analysis with optimized parameters")
    
    def validate_deepseek_model(self) -> bool:
        """Validate that DeepSeek model is properly configured and accessible."""
        try:
            test_response = self._enhanced_completion_with_validation(
                prompt="Respond with 'DeepSeek model test successful' if you can see this message.",
                max_tokens=50,
                temperature=0.1,
                expected_format="text"
            )
            
            if test_response.success:
                logger.info("DeepSeek model validation successful")
                return True
            else:
                logger.warning(f"DeepSeek model validation failed: {test_response.error}")
                return False
                
        except Exception as e:
            logger.error(f"DeepSeek model validation error: {str(e)}")
            return False


# Convenience functions for quick access
def create_client(api_key: Optional[str] = None, model: Optional[str] = None) -> OpenRouterClient:
    """
    Create a configured OpenRouter client.
    
    Args:
        api_key: API key (will use environment variable if None)
        model: Default model to use
    
    Returns:
        Configured OpenRouterClient instance
    """
    config = None
    if api_key or model:
        config = OpenRouterConfig(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY", ""),
            default_model=model or "deepseek/deepseek-chat"
        )
    
    return OpenRouterClient(config)


def test_openrouter_connection(api_key: Optional[str] = None) -> bool:
    """
    Quick test of OpenRouter connection.
    
    Args:
        api_key: API key to test (uses environment if None)
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = create_client(api_key)
        result = client.test_connection()
        return result.success
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False 