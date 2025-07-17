"""
API Request/Response Logging System for OpenRouter Integration

This module provides comprehensive logging and monitoring for API requests
with security-safe practices and detailed metrics tracking.

Key Features:
- Structured request/response logging
- Performance metrics tracking
- Security-safe logging (no API keys/sensitive data)
- Request/response timing
- Error categorization and tracking
- Rate limiting monitoring
- Export capabilities for analysis
"""

import os
import json
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from collections import defaultdict, deque

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class APIRequestLog:
    """Structured log entry for API requests."""
    
    timestamp: str
    request_id: str
    method: str
    url: str
    model: str
    prompt_hash: str  # Hash of prompt for privacy
    prompt_length: int
    max_tokens: int
    temperature: float
    headers_hash: str  # Hash of headers for security
    user_agent: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class APIResponseLog:
    """Structured log entry for API responses."""
    
    timestamp: str
    request_id: str
    status_code: int
    success: bool
    response_time_ms: float
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    content_length: Optional[int] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class RateLimitLog:
    """Log entry for rate limiting events."""
    
    timestamp: str
    event_type: str  # 'allowed', 'blocked', 'wait'
    identifier: str
    requests_in_window: int
    max_requests: int
    wait_time_seconds: float = 0.0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class APIMetrics:
    """Aggregated metrics for API usage."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_response_time_ms: float = 0.0
    average_response_time_ms: float = 0.0
    requests_per_minute: float = 0.0
    error_rate: float = 0.0
    rate_limit_blocks: int = 0
    models_used: Dict[str, int] = field(default_factory=dict)
    error_types: Dict[str, int] = field(default_factory=dict)
    hourly_requests: Dict[str, int] = field(default_factory=dict)
    
    def update_averages(self):
        """Update calculated averages."""
        if self.total_requests > 0:
            self.average_response_time_ms = self.total_response_time_ms / self.total_requests
            self.error_rate = self.failed_requests / self.total_requests
        else:
            self.average_response_time_ms = 0.0
            self.error_rate = 0.0


class APILogger:
    """
    Comprehensive API request/response logger with metrics tracking.
    
    Provides structured logging, performance metrics, and security-safe
    practices for monitoring OpenRouter API usage.
    """
    
    def __init__(
        self,
        log_directory: str = "logs/api",
        max_log_files: int = 10,
        log_rotation_size_mb: int = 10,
        enable_console_logging: bool = True,
        log_level: str = "INFO"
    ):
        """
        Initialize API logger.
        
        Args:
            log_directory: Directory for log files
            max_log_files: Maximum number of log files to keep
            log_rotation_size_mb: Size limit for log rotation
            enable_console_logging: Whether to log to console
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_directory = Path(log_directory)
        self.max_log_files = max_log_files
        self.log_rotation_size_mb = log_rotation_size_mb
        self.enable_console_logging = enable_console_logging
        
        # Create log directory
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        self._setup_logging(log_level)
        
        # In-memory logs for quick access (thread-safe)
        self._lock = threading.Lock()
        self._request_logs = deque(maxlen=1000)  # Keep last 1000 requests
        self._response_logs = deque(maxlen=1000)
        self._rate_limit_logs = deque(maxlen=1000)
        
        # Metrics tracking
        self._metrics = APIMetrics()
        self._session_start = datetime.now()
        
        # Request timing tracking
        self._active_requests = {}  # request_id -> start_time
        
        logger.info(f"API Logger initialized. Log directory: {self.log_directory}")
    
    def _setup_logging(self, log_level: str) -> None:
        """Setup file and console logging."""
        # Create file handler
        log_file = self.log_directory / f"api_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Configure logger
        api_logger = logging.getLogger('api_requests')
        api_logger.setLevel(getattr(logging, log_level.upper()))
        api_logger.addHandler(file_handler)
        
        if self.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            api_logger.addHandler(console_handler)
        
        self.api_logger = api_logger
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return f"req_{int(time.time() * 1000)}_{hash(threading.current_thread()) % 10000}"
    
    def _hash_sensitive_data(self, data: str) -> str:
        """Create hash of sensitive data for logging."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers."""
        sanitized = {}
        sensitive_keys = ['authorization', 'api-key', 'x-api-key', 'token']
        
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = f"***{value[-4:]}" if len(value) > 4 else "***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def log_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> str:
        """
        Log an API request.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            payload: Request payload
            request_id: Optional request ID (generated if None)
        
        Returns:
            Request ID for correlation
        """
        if request_id is None:
            request_id = self._generate_request_id()
        
        # Extract relevant information
        model = payload.get('model', 'unknown')
        messages = payload.get('messages', [])
        prompt = ' '.join([msg.get('content', '') for msg in messages])
        
        # Create log entry
        log_entry = APIRequestLog(
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            method=method,
            url=url,
            model=model,
            prompt_hash=self._hash_sensitive_data(prompt),
            prompt_length=len(prompt),
            max_tokens=payload.get('max_tokens', 0),
            temperature=payload.get('temperature', 0.0),
            headers_hash=self._hash_sensitive_data(json.dumps(self._sanitize_headers(headers))),
            user_agent=headers.get('User-Agent', '')
        )
        
        # Store in memory and log to file
        with self._lock:
            self._request_logs.append(log_entry)
            self._active_requests[request_id] = time.time()
            self._metrics.total_requests += 1
            
            # Update hourly metrics
            hour_key = datetime.now().strftime('%Y-%m-%d-%H')
            self._metrics.hourly_requests[hour_key] = self._metrics.hourly_requests.get(hour_key, 0) + 1
        
        # Log to file
        self.api_logger.info(f"REQUEST {request_id}: {method} {url} | Model: {model} | Prompt length: {len(prompt)} | Max tokens: {payload.get('max_tokens')}")
        
        return request_id
    
    def log_response(
        self,
        request_id: str,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log an API response.
        
        Args:
            request_id: Request ID for correlation
            status_code: HTTP status code
            response_data: Response data (optional)
            error_message: Error message if failed (optional)
        """
        # Calculate response time
        response_time_ms = 0.0
        with self._lock:
            if request_id in self._active_requests:
                start_time = self._active_requests.pop(request_id)
                response_time_ms = (time.time() - start_time) * 1000
        
        # Determine success
        success = 200 <= status_code < 300
        
        # Extract response information
        model_used = None
        tokens_used = None
        completion_tokens = None
        prompt_tokens = None
        content_length = None
        error_type = None
        
        if response_data:
            model_used = response_data.get('model')
            usage = response_data.get('usage', {})
            tokens_used = usage.get('total_tokens')
            completion_tokens = usage.get('completion_tokens')
            prompt_tokens = usage.get('prompt_tokens')
            content_length = len(json.dumps(response_data))
        
        if error_message:
            error_type = self._categorize_error(status_code, error_message)
        
        # Create log entry
        log_entry = APIResponseLog(
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            status_code=status_code,
            success=success,
            response_time_ms=response_time_ms,
            model_used=model_used,
            tokens_used=tokens_used,
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
            error_type=error_type,
            error_message=error_message,
            content_length=content_length
        )
        
        # Update metrics
        with self._lock:
            self._response_logs.append(log_entry)
            self._metrics.total_response_time_ms += response_time_ms
            
            if success:
                self._metrics.successful_requests += 1
                if tokens_used:
                    self._metrics.total_tokens += tokens_used
                if model_used:
                    self._metrics.models_used[model_used] = self._metrics.models_used.get(model_used, 0) + 1
            else:
                self._metrics.failed_requests += 1
                if error_type:
                    self._metrics.error_types[error_type] = self._metrics.error_types.get(error_type, 0) + 1
            
            self._metrics.update_averages()
        
        # Log to file
        if success:
            self.api_logger.info(
                f"RESPONSE {request_id}: {status_code} | "
                f"Time: {response_time_ms:.1f}ms | "
                f"Tokens: {tokens_used} | "
                f"Model: {model_used}"
            )
        else:
            self.api_logger.error(
                f"RESPONSE {request_id}: {status_code} | "
                f"Time: {response_time_ms:.1f}ms | "
                f"Error: {error_type} | "
                f"Message: {error_message}"
            )
    
    def log_rate_limit_event(
        self,
        event_type: str,
        identifier: str,
        requests_in_window: int,
        max_requests: int,
        wait_time: float = 0.0
    ) -> None:
        """
        Log a rate limiting event.
        
        Args:
            event_type: Type of event ('allowed', 'blocked', 'wait')
            identifier: Rate limit identifier
            requests_in_window: Current requests in time window
            max_requests: Maximum allowed requests
            wait_time: Wait time in seconds if blocked
        """
        log_entry = RateLimitLog(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            identifier=identifier,
            requests_in_window=requests_in_window,
            max_requests=max_requests,
            wait_time_seconds=wait_time
        )
        
        with self._lock:
            self._rate_limit_logs.append(log_entry)
            
            if event_type == 'blocked':
                self._metrics.rate_limit_blocks += 1
        
        if event_type == 'blocked':
            self.api_logger.warning(
                f"RATE_LIMIT {identifier}: Blocked | "
                f"Requests: {requests_in_window}/{max_requests} | "
                f"Wait: {wait_time:.1f}s"
            )
        elif event_type == 'wait':
            self.api_logger.info(
                f"RATE_LIMIT {identifier}: Waiting {wait_time:.1f}s"
            )
    
    def _categorize_error(self, status_code: int, error_message: str) -> str:
        """Categorize error based on status code and message."""
        if status_code == 401:
            return "authentication"
        elif status_code == 403:
            return "authorization"
        elif status_code == 404:
            return "not_found"
        elif status_code == 429:
            return "rate_limit"
        elif 500 <= status_code < 600:
            return "server_error"
        elif "timeout" in error_message.lower():
            return "timeout"
        elif "connection" in error_message.lower():
            return "connection"
        else:
            return "unknown"
    
    def get_metrics(self, include_recent: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive API usage metrics.
        
        Args:
            include_recent: Include recent logs and timing data
        
        Returns:
            Dictionary with metrics and statistics
        """
        with self._lock:
            metrics_dict = asdict(self._metrics)
            
            # Calculate requests per minute
            elapsed_minutes = (datetime.now() - self._session_start).total_seconds() / 60
            if elapsed_minutes > 0:
                metrics_dict['requests_per_minute'] = self._metrics.total_requests / elapsed_minutes
            
            if include_recent:
                # Recent response times (last 10 requests)
                recent_times = [log.response_time_ms for log in list(self._response_logs)[-10:]]
                metrics_dict['recent_response_times'] = recent_times
                
                # Recent error summary
                recent_errors = [log.error_type for log in list(self._response_logs)[-50:] if log.error_type]
                metrics_dict['recent_errors'] = recent_errors
                
                # Active requests
                metrics_dict['active_requests'] = len(self._active_requests)
        
        return metrics_dict
    
    def export_logs(
        self,
        output_file: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """
        Export logs to JSON file.
        
        Args:
            output_file: Output file path (auto-generated if None)
            start_time: Filter start time
            end_time: Filter end time
        
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.log_directory / f"api_logs_export_{timestamp}.json"
        
        # Filter logs by time if specified
        with self._lock:
            request_logs = list(self._request_logs)
            response_logs = list(self._response_logs)
            rate_limit_logs = list(self._rate_limit_logs)
        
        if start_time or end_time:
            def time_filter(log_entry):
                log_time = datetime.fromisoformat(log_entry.timestamp)
                if start_time and log_time < start_time:
                    return False
                if end_time and log_time > end_time:
                    return False
                return True
            
            request_logs = [log for log in request_logs if time_filter(log)]
            response_logs = [log for log in response_logs if time_filter(log)]
            rate_limit_logs = [log for log in rate_limit_logs if time_filter(log)]
        
        # Prepare export data
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'session_start': self._session_start.isoformat(),
            'metrics': self.get_metrics(include_recent=False),
            'request_logs': [asdict(log) for log in request_logs],
            'response_logs': [asdict(log) for log in response_logs],
            'rate_limit_logs': [asdict(log) for log in rate_limit_logs]
        }
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Logs exported to: {output_file}")
        return str(output_file)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of API performance metrics."""
        metrics = self.get_metrics()
        
        return {
            'total_requests': metrics['total_requests'],
            'success_rate': f"{(1 - metrics['error_rate']) * 100:.1f}%",
            'average_response_time': f"{metrics['average_response_time_ms']:.1f}ms",
            'requests_per_minute': f"{metrics['requests_per_minute']:.1f}",
            'total_tokens_used': metrics['total_tokens'],
            'rate_limit_blocks': metrics['rate_limit_blocks'],
            'top_models': dict(sorted(metrics['models_used'].items(), key=lambda x: x[1], reverse=True)[:5]),
            'error_breakdown': metrics['error_types']
        }


# Global logger instance
_global_logger = None

def get_api_logger(**kwargs) -> APILogger:
    """Get or create global API logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = APILogger(**kwargs)
    return _global_logger

def reset_api_logger():
    """Reset global API logger (useful for testing)."""
    global _global_logger
    _global_logger = None 