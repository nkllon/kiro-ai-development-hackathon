"""
Bot-Safe Headers Configuration

Provides headers that avoid triggering bot protection systems
while maintaining observatory functionality.
"""

import json
from typing import Dict, Any
from datetime import datetime


class BotSafeHeaders:
    """Manages bot-safe HTTP headers for polling requests."""
    
    # Base bot-safe headers that avoid triggering protection systems
    BOT_SAFE_HEADERS = {
        "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
        "X-Observatory-Client": "internal-polling",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "X-Polling-Reason": "websocket-fallback"
    }
    
    def __init__(self):
        self._log_action("init", "BotSafeHeaders initialized")
    
    def get_headers(self, endpoint: str = None, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """
        Get bot-safe headers for a request.
        
        Args:
            endpoint: The endpoint being polled (for context)
            additional_headers: Additional headers to include
            
        Returns:
            Dictionary of bot-safe headers
        """
        headers = self.BOT_SAFE_HEADERS.copy()
        
        # Add endpoint-specific context if provided
        if endpoint:
            headers["X-Target-Endpoint"] = endpoint
        
        # Add timestamp for request tracking
        headers["X-Request-Timestamp"] = datetime.utcnow().isoformat()
        
        # Merge additional headers if provided
        if additional_headers:
            headers.update(additional_headers)
        
        self._log_action("get_headers", "Headers generated", {
            "endpoint": endpoint,
            "header_count": len(headers)
        })
        
        return headers
    
    def get_retry_headers(self, retry_count: int, endpoint: str = None) -> Dict[str, str]:
        """
        Get headers for retry requests with backoff indicators.
        
        Args:
            retry_count: Number of retries attempted
            endpoint: The endpoint being retried
            
        Returns:
            Dictionary of headers with retry context
        """
        headers = self.get_headers(endpoint)
        headers["X-Retry-Count"] = str(retry_count)
        headers["X-Retry-Reason"] = "websocket-fallback-retry"
        
        self._log_action("get_retry_headers", "Retry headers generated", {
            "retry_count": retry_count,
            "endpoint": endpoint
        })
        
        return headers
    
    def _log_action(self, action: str, description: str, details: Dict[str, Any] = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "2.2",
            "component": "BotSafeHeaders",
            "action": action,
            "status": "completed",
            "description": description
        }
        
        if details:
            log_entry["details"] = details
            
        print(json.dumps(log_entry))