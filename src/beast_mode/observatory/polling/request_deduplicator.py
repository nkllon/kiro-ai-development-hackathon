"""
Request Deduplicator for Intelligent Polling

Implements request caching and batching to reduce redundant requests
and share responses across multiple clients.
"""

import json
import hashlib
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CachedRequest:
    """Represents a cached request and its response."""
    endpoint: str
    params_hash: str
    timestamp: datetime
    response_data: Any
    response_status: int
    ttl_seconds: int = 30  # Default 30 second TTL


@dataclass
class PendingRequest:
    """Represents a pending request waiting for response."""
    endpoint: str
    params_hash: str
    future: asyncio.Future
    timestamp: datetime


class RequestDeduplicator:
    """Manages request deduplication and response caching."""
    
    def __init__(self, cache_ttl: int = 30, max_cache_size: int = 1000):
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        
        # Cache storage
        self.cache: Dict[str, CachedRequest] = {}
        
        # Pending requests (for batching)
        self.pending_requests: Dict[str, List[PendingRequest]] = {}
        
        # Request tracking
        self.request_counts: Dict[str, int] = {}
        
        self._log_action("init", "RequestDeduplicator initialized", {
            "cache_ttl": cache_ttl,
            "max_cache_size": max_cache_size
        })
    
    def _generate_params_hash(self, endpoint: str, params: Dict[str, Any] = None) -> str:
        """
        Generate a hash for request parameters.
        
        Args:
            endpoint: The endpoint URL
            params: Request parameters
            
        Returns:
            Hash string for the request
        """
        if params is None:
            params = {}
        
        # Sort parameters for consistent hashing
        sorted_params = sorted(params.items())
        param_string = f"{endpoint}:{sorted_params}"
        
        return hashlib.md5(param_string.encode()).hexdigest()
    
    async def get_or_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any] = None,
        request_func: callable = None
    ) -> Tuple[Any, int]:
        """
        Get cached response or make new request with deduplication.
        
        Args:
            endpoint: The endpoint to request
            params: Request parameters
            request_func: Function to make the actual request
            
        Returns:
            Tuple of (response_data, status_code)
        """
        params_hash = self._generate_params_hash(endpoint, params)
        cache_key = f"{endpoint}:{params_hash}"
        
        # Check cache first
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            self._log_action("cache_hit", "Cached response returned", {
                "endpoint": endpoint,
                "cache_key": cache_key
            })
            return cached_response.response_data, cached_response.response_status
        
        # Check if there's already a pending request for this
        if cache_key in self.pending_requests:
            self._log_action("request_batch", "Joining pending request", {
                "endpoint": endpoint,
                "cache_key": cache_key
            })
            
            # Create a future for this request
            future = asyncio.Future()
            pending_request = PendingRequest(
                endpoint=endpoint,
                params_hash=params_hash,
                future=future,
                timestamp=datetime.utcnow()
            )
            
            self.pending_requests[cache_key].append(pending_request)
            
            # Wait for the original request to complete
            response_data, status_code = await future
            return response_data, status_code
        
        # Make new request
        if request_func is None:
            raise ValueError("request_func is required for new requests")
        
        self._log_action("new_request", "Making new request", {
            "endpoint": endpoint,
            "cache_key": cache_key
        })
        
        # Initialize pending requests list
        self.pending_requests[cache_key] = []
        
        try:
            # Make the actual request
            response_data, status_code = await request_func(endpoint, params)
            
            # Cache the response
            self._cache_response(cache_key, endpoint, params_hash, response_data, status_code)
            
            # Resolve all pending requests
            for pending_request in self.pending_requests[cache_key]:
                if not pending_request.future.done():
                    pending_request.future.set_result((response_data, status_code))
            
            # Clean up pending requests
            del self.pending_requests[cache_key]
            
            self._log_action("request_complete", "Request completed and cached", {
                "endpoint": endpoint,
                "cache_key": cache_key,
                "status_code": status_code,
                "pending_resolved": len(self.pending_requests.get(cache_key, []))
            })
            
            return response_data, status_code
            
        except Exception as e:
            # Reject all pending requests
            for pending_request in self.pending_requests[cache_key]:
                if not pending_request.future.done():
                    pending_request.future.set_exception(e)
            
            # Clean up pending requests
            del self.pending_requests[cache_key]
            
            self._log_action("request_error", "Request failed", {
                "endpoint": endpoint,
                "cache_key": cache_key,
                "error": str(e)
            })
            
            raise
    
    def _get_cached_response(self, cache_key: str) -> Optional[CachedRequest]:
        """Get cached response if valid."""
        if cache_key not in self.cache:
            return None
        
        cached_request = self.cache[cache_key]
        now = datetime.utcnow()
        
        # Check if cache entry is expired
        if now - cached_request.timestamp > timedelta(seconds=cached_request.ttl_seconds):
            del self.cache[cache_key]
            self._log_action("cache_expired", "Cache entry expired", {
                "cache_key": cache_key
            })
            return None
        
        return cached_request
    
    def _cache_response(
        self, 
        cache_key: str, 
        endpoint: str, 
        params_hash: str, 
        response_data: Any, 
        status_code: int
    ) -> None:
        """Cache a response."""
        # Clean up old cache entries if we're at the limit
        if len(self.cache) >= self.max_cache_size:
            self._cleanup_cache()
        
        cached_request = CachedRequest(
            endpoint=endpoint,
            params_hash=params_hash,
            timestamp=datetime.utcnow(),
            response_data=response_data,
            response_status=status_code,
            ttl_seconds=self.cache_ttl
        )
        
        self.cache[cache_key] = cached_request
        
        # Update request count
        if endpoint not in self.request_counts:
            self.request_counts[endpoint] = 0
        self.request_counts[endpoint] += 1
    
    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        now = datetime.utcnow()
        expired_keys = []
        
        for cache_key, cached_request in self.cache.items():
            if now - cached_request.timestamp > timedelta(seconds=cached_request.ttl_seconds):
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cache[key]
        
        self._log_action("cache_cleanup", "Cache cleaned up", {
            "expired_entries": len(expired_keys),
            "remaining_entries": len(self.cache)
        })
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.utcnow()
        valid_entries = 0
        expired_entries = 0
        
        for cached_request in self.cache.values():
            if now - cached_request.timestamp <= timedelta(seconds=cached_request.ttl_seconds):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "pending_requests": sum(len(requests) for requests in self.pending_requests.values()),
            "request_counts": self.request_counts.copy()
        }
    
    def clear_cache(self) -> None:
        """Clear all cached responses."""
        cache_size = len(self.cache)
        self.cache.clear()
        
        self._log_action("cache_clear", "Cache cleared", {
            "cleared_entries": cache_size
        })
    
    def _log_action(self, action: str, description: str, details: Dict = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "2.2",
            "component": "RequestDeduplicator",
            "action": action,
            "status": "completed",
            "description": description
        }
        
        if details:
            log_entry["details"] = details
            
        print(json.dumps(log_entry))