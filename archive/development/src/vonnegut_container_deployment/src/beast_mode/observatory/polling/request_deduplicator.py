"""
Request Deduplicator for Intelligent Polling

This module provides request deduplication and batching capabilities
to reduce redundant requests and improve efficiency.
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, Set, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import uuid


@dataclass
class CachedRequest:
    """Represents a cached request"""
    request_id: str
    endpoint: str
    params: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: float
    response_data: Optional[Any] = None
    response_headers: Optional[Dict[str, str]] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    clients_waiting: Set[str] = field(default_factory=set)


@dataclass
class BatchRequest:
    """Represents a batch of requests"""
    batch_id: str
    requests: List[CachedRequest]
    created_at: float
    max_wait_time: float = 5.0  # Maximum time to wait for batching


class RequestDeduplicator:
    """Handles request deduplication and batching"""
    
    def __init__(self, cache_ttl: float = 30.0, batch_window: float = 2.0):
        self.cache_ttl = cache_ttl
        self.batch_window = batch_window
        
        # Request cache
        self.request_cache: Dict[str, CachedRequest] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        # Pending requests for batching
        self.pending_requests: Dict[str, List[CachedRequest]] = defaultdict(list)
        self.batch_timers: Dict[str, asyncio.Task] = {}
        
        # Active requests (in progress)
        self.active_requests: Dict[str, CachedRequest] = {}
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "batched_requests": 0,
            "deduplicated_requests": 0
        }
        
        self._lock = asyncio.Lock()
        
    def _generate_request_key(self, endpoint: str, params: Dict[str, Any], headers: Dict[str, str]) -> str:
        """Generate a unique key for request deduplication"""
        # Create a normalized representation of the request
        normalized_data = {
            "endpoint": endpoint,
            "params": sorted(params.items()) if params else [],
            "headers": {k: v for k, v in headers.items() if k.lower() not in ["x-timestamp", "x-request-id"]}
        }
        
        # Create hash of normalized data
        data_str = json.dumps(normalized_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def get_or_create_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any], 
        headers: Dict[str, str],
        client_id: str
    ) -> Tuple[CachedRequest, bool]:
        """
        Get existing request or create new one
        
        Args:
            endpoint: The endpoint to request
            params: Request parameters
            headers: Request headers
            client_id: ID of the client making the request
            
        Returns:
            Tuple of (CachedRequest, is_new_request)
        """
        async with self._lock:
            request_key = self._generate_request_key(endpoint, params, headers)
            current_time = time.time()
            
            # Clean expired cache entries
            self._cleanup_expired_cache(current_time)
            
            # Check if request is already cached
            if request_key in self.request_cache:
                cached_request = self.request_cache[request_key]
                
                # Check if cache is still valid
                if current_time - cached_request.timestamp < self.cache_ttl:
                    self.stats["cache_hits"] += 1
                    self._log_deduplication(endpoint, request_key, "cache_hit", client_id)
                    return cached_request, False
            
            # Check if request is already in progress
            if request_key in self.active_requests:
                active_request = self.active_requests[request_key]
                active_request.clients_waiting.add(client_id)
                self.stats["deduplicated_requests"] += 1
                self._log_deduplication(endpoint, request_key, "deduplicated", client_id)
                return active_request, False
            
            # Create new request
            request_id = str(uuid.uuid4())
            new_request = CachedRequest(
                request_id=request_id,
                endpoint=endpoint,
                params=params,
                headers=headers,
                timestamp=current_time,
                clients_waiting={client_id}
            )
            
            # Add to active requests
            self.active_requests[request_key] = new_request
            
            # Check if we should batch this request
            if self._should_batch_request(endpoint):
                await self._add_to_batch(endpoint, new_request, request_key)
                self.stats["batched_requests"] += 1
                self._log_deduplication(endpoint, request_key, "batched", client_id)
            else:
                self.stats["cache_misses"] += 1
                self._log_deduplication(endpoint, request_key, "new_request", client_id)
            
            self.stats["total_requests"] += 1
            return new_request, True
    
    async def complete_request(
        self, 
        request_key: str, 
        response_data: Any = None,
        response_headers: Dict[str, str] = None,
        status_code: int = None,
        error: str = None
    ) -> None:
        """
        Mark a request as completed
        
        Args:
            request_key: The request key
            response_data: Response data
            response_headers: Response headers
            status_code: HTTP status code
            error: Error message if any
        """
        async with self._lock:
            if request_key not in self.active_requests:
                return
            
            request = self.active_requests[request_key]
            
            # Update request with response data
            request.response_data = response_data
            request.response_headers = response_headers
            request.status_code = status_code
            request.error = error
            
            # Move to cache
            self.request_cache[request_key] = request
            self.cache_timestamps[request_key] = time.time()
            
            # Remove from active requests
            del self.active_requests[request_key]
            
            # Log completion
            self._log_deduplication(
                request.endpoint, 
                request_key, 
                "completed", 
                f"{len(request.clients_waiting)} clients"
            )
    
    def _should_batch_request(self, endpoint: str) -> bool:
        """Determine if request should be batched"""
        # Don't batch if there are already pending requests for this endpoint
        return len(self.pending_requests[endpoint]) > 0
    
    async def _add_to_batch(self, endpoint: str, request: CachedRequest, request_key: str) -> None:
        """Add request to batch"""
        self.pending_requests[endpoint].append(request)
        
        # Start batch timer if not already running
        if endpoint not in self.batch_timers:
            self.batch_timers[endpoint] = asyncio.create_task(
                self._process_batch(endpoint)
            )
    
    async def _process_batch(self, endpoint: str) -> None:
        """Process batched requests"""
        await asyncio.sleep(self.batch_window)
        
        async with self._lock:
            if endpoint not in self.pending_requests:
                return
            
            requests = self.pending_requests[endpoint]
            if not requests:
                return
            
            # Create batch
            batch_id = str(uuid.uuid4())
            batch = BatchRequest(
                batch_id=batch_id,
                requests=requests.copy(),
                created_at=time.time()
            )
            
            # Clear pending requests
            self.pending_requests[endpoint] = []
            
            # Clean up timer
            if endpoint in self.batch_timers:
                del self.batch_timers[endpoint]
            
            # Log batch creation
            self._log_batch(endpoint, batch_id, len(requests))
            
            # Process batch (this would be handled by the poller)
            return batch
    
    def _cleanup_expired_cache(self, current_time: float) -> None:
        """Clean up expired cache entries"""
        expired_keys = []
        
        for request_key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > self.cache_ttl:
                expired_keys.append(request_key)
        
        for key in expired_keys:
            if key in self.request_cache:
                del self.request_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
    
    def _log_deduplication(self, endpoint: str, request_key: str, action: str, client_id: str) -> None:
        """Log deduplication activity"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "task": "2.2",
            "action": f"deduplication_{action}",
            "status": "in_progress",
            "details": {
                "endpoint": endpoint,
                "request_key": request_key[:8],  # Truncate for readability
                "client_id": client_id,
                "cache_size": len(self.request_cache),
                "active_requests": len(self.active_requests),
                "pending_batches": len(self.pending_requests)
            }
        }
        print(json.dumps(log_entry))
    
    def _log_batch(self, endpoint: str, batch_id: str, request_count: int) -> None:
        """Log batch creation"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "task": "2.2",
            "action": "batch_created",
            "status": "in_progress",
            "details": {
                "endpoint": endpoint,
                "batch_id": batch_id[:8],
                "request_count": request_count,
                "batch_window": self.batch_window
            }
        }
        print(json.dumps(log_entry))
    
    def get_stats(self) -> Dict:
        """Get deduplicator statistics"""
        return {
            "stats": self.stats.copy(),
            "cache_size": len(self.request_cache),
            "active_requests": len(self.active_requests),
            "pending_batches": len(self.pending_requests),
            "batch_timers": len(self.batch_timers)
        }
    
    async def clear_cache(self) -> None:
        """Clear all cached requests"""
        async with self._lock:
            self.request_cache.clear()
            self.cache_timestamps.clear()
            self.active_requests.clear()
            self.pending_requests.clear()
            
            # Cancel any running batch timers
            for timer in self.batch_timers.values():
                timer.cancel()
            self.batch_timers.clear()
            
            self._log_deduplication("", "", "cache_cleared", "system")