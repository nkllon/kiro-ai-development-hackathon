"""
Bot-Safe Headers and Request Patterns

This module provides bot-safe HTTP headers and request patterns to avoid
triggering security systems and bot protection mechanisms.
"""

import random
import time
from typing import Dict, List, Optional
from dataclasses import dataclass


# Bot-safe headers that mimic legitimate browser behavior
BOT_SAFE_HEADERS = {
    "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
    "X-Observatory-Client": "internal-polling",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Cache-Control": "no-cache",
    "X-Polling-Reason": "websocket-fallback",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9"
}

# Additional headers for different scenarios
EXTENDED_HEADERS = {
    "X-Forwarded-For": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
    "Referer": "https://observatory.internal/",
    "Origin": "https://observatory.internal"
}

# Headers to avoid (commonly flagged by bot protection)
AVOID_HEADERS = {
    "X-Bot": "true",
    "X-Automated": "true", 
    "X-Scraping": "true",
    "X-Crawler": "true"
}


@dataclass
class RequestPattern:
    """Represents a bot-safe request pattern"""
    headers: Dict[str, str]
    method: str = "GET"
    timeout: float = 30.0
    follow_redirects: bool = True
    verify_ssl: bool = True


class BotSafeHeaders:
    """Manages bot-safe headers and request patterns"""
    
    def __init__(self):
        self.base_headers = BOT_SAFE_HEADERS.copy()
        self.extended_headers = EXTENDED_HEADERS.copy()
        self.avoid_headers = AVOID_HEADERS.copy()
        
    def get_headers(self, include_extended: bool = False) -> Dict[str, str]:
        """
        Get bot-safe headers for requests
        
        Args:
            include_extended: Whether to include extended headers
            
        Returns:
            Dictionary of bot-safe headers
        """
        headers = self.base_headers.copy()
        
        if include_extended:
            headers.update(self.extended_headers)
            
        # Add some randomization to avoid pattern detection
        headers = self._add_randomization(headers)
        
        return headers
    
    def _add_randomization(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Add subtle randomization to headers to avoid pattern detection"""
        randomized = headers.copy()
        
        # Randomize User-Agent slightly
        if "User-Agent" in randomized:
            base_ua = randomized["User-Agent"]
            # Add minor version variations
            version_variants = ["1.0", "1.1", "1.2"]
            variant = random.choice(version_variants)
            randomized["User-Agent"] = base_ua.replace("1.0", variant)
            
        # Add timestamp-based header for uniqueness
        randomized["X-Timestamp"] = str(int(time.time() * 1000))
        
        return randomized
    
    def get_request_pattern(self, endpoint: str, include_extended: bool = False) -> RequestPattern:
        """
        Get a complete bot-safe request pattern
        
        Args:
            endpoint: The endpoint being requested
            include_extended: Whether to include extended headers
            
        Returns:
            RequestPattern object with bot-safe configuration
        """
        headers = self.get_headers(include_extended)
        
        # Add endpoint-specific headers
        headers["X-Endpoint"] = endpoint
        headers["X-Request-ID"] = self._generate_request_id()
        
        return RequestPattern(
            headers=headers,
            method="GET",
            timeout=30.0,
            follow_redirects=True,
            verify_ssl=True
        )
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID"""
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        return f"req_{timestamp}_{random_suffix}"
    
    def validate_headers(self, headers: Dict[str, str]) -> bool:
        """
        Validate that headers are bot-safe
        
        Args:
            headers: Headers to validate
            
        Returns:
            True if headers are bot-safe, False otherwise
        """
        # Check for headers that should be avoided
        for avoid_header in self.avoid_headers:
            if avoid_header in headers:
                return False
                
        # Check for required bot-safe headers
        required_headers = ["User-Agent", "X-Observatory-Client", "Accept"]
        for required in required_headers:
            if required not in headers:
                return False
                
        return True
    
    def sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers to make them bot-safe
        
        Args:
            headers: Headers to sanitize
            
        Returns:
            Sanitized headers
        """
        sanitized = {}
        
        for key, value in headers.items():
            # Skip headers that should be avoided
            if key in self.avoid_headers:
                continue
                
            # Normalize header names
            normalized_key = key.title().replace("-", "-")
            sanitized[normalized_key] = value
            
        # Ensure required headers are present
        bot_safe_headers = self.get_headers()
        for key, value in bot_safe_headers.items():
            if key not in sanitized:
                sanitized[key] = value
                
        return sanitized