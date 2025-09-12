"""
Rate Limiter Core Core Core

This module was extracted from rate_limiter_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

class RateLimiter:
    """
    Token bucket rate limiter implementation.
    
    Provides rate limiting per operation and per client
    to ensure fair resource usage and prevent abuse.
    """

    def __init__(self, default_requests_per_minute: int=60, default_burst_size: int=10, cleanup_interval: int=300):
        self.default_requests_per_minute = default_requests_per_minute
        self.default_burst_size = default_burst_size
        self.cleanup_interval = cleanup_interval
        self._operation_limits: Dict[str, Dict[str, int]] = {}
        self._client_buckets: Dict[str, Dict[str, Dict]] = defaultdict(dict)
        self._request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._last_cleanup = datetime.utcnow()
        logger.info('Rate limiter initialized')

    def set_operation_limit(self, operation: str, requests_per_minute: int, burst_size: Optional[int]=None) -> None:
        """
        Set rate limit for specific operation.
        
        Args:
            operation: Name of operation
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute / 6)
        """
        if burst_size is None:
            burst_size = max(1, requests_per_minute // 6)
        self._operation_limits[operation] = {'requests_per_minute': requests_per_minute, 'burst_size': burst_size}
        logger.info(f'Set rate limit for {operation}: {requests_per_minute}/min, burst {burst_size}')

    async def check_limit(self, operation: str, client_id: str='default') -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            operation: Name of operation
            client_id: Client identifier (defaults to "default")
            
        Returns:
            True if request is allowed, False if rate limited
        """
        await self._cleanup_if_needed()
        bucket = self._get_bucket(client_id, operation)
        self._refill_bucket(bucket)
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            bucket['last_request'] = datetime.utcnow()
            self._record_request(operation, client_id, allowed=True)
            return True
        else:
            self._record_request(operation, client_id, allowed=False)
            logger.warning(f'Rate limit exceeded for {client_id}/{operation}')
            return False

    async def get_remaining_tokens(self, operation: str, client_id: str='default') -> int:
        """
        Get remaining tokens for client/operation.
        
        Args:
            operation: Name of operation
            client_id: Client identifier
            
        Returns:
            Number of remaining tokens
        """
        bucket = self._get_bucket(client_id, operation)
        self._refill_bucket(bucket)
        return int(bucket['tokens'])

    async def get_reset_time(self, operation: str, client_id: str='default') -> datetime:
        """
        Get time when rate limit will reset for client/operation.
        
        Args:
            operation: Name of operation
            client_id: Client identifier
            
        Returns:
            DateTime when rate limit resets
        """
        bucket = self._get_bucket(client_id, operation)
        limits = self._get_operation_limits(operation)
        tokens_needed = limits['burst_size'] - bucket['tokens']
        if tokens_needed <= 0:
            return datetime.utcnow()
        refill_rate = limits['requests_per_minute'] / 60.0
        seconds_to_refill = tokens_needed / refill_rate
        return datetime.utcnow() + timedelta(seconds=seconds_to_refill)

    def get_status(self) -> Dict[str, Any]:
        """
        Get rate limiter status.
        
        Returns:
            Dictionary with rate limiter status
        """
        active_clients = len(self._client_buckets)
        total_buckets = sum((len(ops) for ops in self._client_buckets.values()))
        return {'timestamp': datetime.utcnow().isoformat(), 'active_clients': active_clients, 'total_buckets': total_buckets, 'default_requests_per_minute': self.default_requests_per_minute, 'default_burst_size': self.default_burst_size, 'operation_limits': dict(self._operation_limits)}

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get rate limiter metrics.
        
        Returns:
            Dictionary with metrics information
        """
        total_requests = sum((len(history) for history in self._request_history.values()))
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        recent_allowed = 0
        recent_rejected = 0
        for operation, history in self._request_history.items():
            for request in history:
                if request['timestamp'] >= cutoff_time:
                    if request['allowed']:
                        recent_allowed += 1
                    else:
                        recent_rejected += 1
        return {'total_requests_recorded': total_requests, 'recent_allowed_requests': recent_allowed, 'recent_rejected_requests': recent_rejected, 'rejection_rate': recent_rejected / max(1, recent_allowed + recent_rejected), 'active_operations': len(self._request_history), 'cleanup_interval': self.cleanup_interval}

    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """
        Get statistics for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dictionary with client statistics
        """
        if client_id not in self._client_buckets:
            return {'error': 'Client not found'}
        client_buckets = self._client_buckets[client_id]
        stats = {'client_id': client_id, 'operations': {}, 'total_operations': len(client_buckets)}
        for operation, bucket in client_buckets.items():
            self._refill_bucket(bucket)
            limits = self._get_operation_limits(operation)
            stats['operations'][operation] = {'remaining_tokens': int(bucket['tokens']), 'max_tokens': limits['burst_size'], 'requests_per_minute': limits['requests_per_minute'], 'last_request': bucket['last_request'].isoformat() if bucket['last_request'] else None}
        return stats

    def reset_client_limits(self, client_id: str) -> bool:
        """
        Reset rate limits for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if client was reset, False if not found
        """
        if client_id in self._client_buckets:
            del self._client_buckets[client_id]
            logger.info(f'Reset rate limits for client {client_id}')
            return True
        return False

    def _get_bucket(self, client_id: str, operation: str) -> Dict:
        """Get or create token bucket for client/operation"""
        if operation not in self._client_buckets[client_id]:
            limits = self._get_operation_limits(operation)
            self._client_buckets[client_id][operation] = {'tokens': float(limits['burst_size']), 'last_refill': datetime.utcnow(), 'last_request': None}
        return self._client_buckets[client_id][operation]

    def _get_operation_limits(self, operation: str) -> Dict[str, int]:
        """Get rate limits for operation"""
        return self._operation_limits.get(operation, {'requests_per_minute': self.default_requests_per_minute, 'burst_size': self.default_burst_size})

    def _refill_bucket(self, bucket: Dict) -> None:
        """Refill token bucket based on elapsed time"""
        now = datetime.utcnow()
        time_elapsed = (now - bucket['last_refill']).total_seconds()
        if time_elapsed > 0:
            operation_limits = self._get_operation_limits('default')
            refill_rate = operation_limits['requests_per_minute'] / 60.0
            tokens_to_add = time_elapsed * refill_rate
            bucket['tokens'] = min(operation_limits['burst_size'], bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = now

    def _record_request(self, operation: str, client_id: str, allowed: bool) -> None:
        """Record request for statistics"""
        self._request_history[operation].append({'timestamp': datetime.utcnow(), 'client_id': client_id, 'allowed': allowed})

    async def _cleanup_if_needed(self) -> None:
        """Cleanup old data if needed"""
        now = datetime.utcnow()
        if (now - self._last_cleanup).total_seconds() >= self.cleanup_interval:
            await self._cleanup_old_data()
            self._last_cleanup = now

    async def _cleanup_old_data(self) -> None:
        """Clean up old buckets and request history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        clients_to_remove = []
        for client_id, operations in self._client_buckets.items():
            operations_to_remove = []
            for operation, bucket in operations.items():
                if bucket['last_request'] and bucket['last_request'] < cutoff_time:
                    operations_to_remove.append(operation)
            for operation in operations_to_remove:
                del operations[operation]
            if not operations:
                clients_to_remove.append(client_id)
        for client_id in clients_to_remove:
            del self._client_buckets[client_id]
        for operation, history in self._request_history.items():
            while history and history[0]['timestamp'] < cutoff_time:
                history.popleft()
        logger.debug(f'Cleaned up {len(clients_to_remove)} inactive clients')

def __init__(self, default_requests_per_minute: int=60, default_burst_size: int=10, cleanup_interval: int=300):
    self.default_requests_per_minute = default_requests_per_minute
    self.default_burst_size = default_burst_size
    self.cleanup_interval = cleanup_interval
    self._operation_limits: Dict[str, Dict[str, int]] = {}
    self._client_buckets: Dict[str, Dict[str, Dict]] = defaultdict(dict)
    self._request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
    self._last_cleanup = datetime.utcnow()
    logger.info('Rate limiter initialized')

def set_operation_limit(self, operation: str, requests_per_minute: int, burst_size: Optional[int]=None) -> None:
    """
        Set rate limit for specific operation.
        
        Args:
            operation: Name of operation
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute / 6)
        """
    if burst_size is None:
        burst_size = max(1, requests_per_minute // 6)
    self._operation_limits[operation] = {'requests_per_minute': requests_per_minute, 'burst_size': burst_size}
    logger.info(f'Set rate limit for {operation}: {requests_per_minute}/min, burst {burst_size}')

def get_status(self) -> Dict[str, Any]:
    """
        Get rate limiter status.
        
        Returns:
            Dictionary with rate limiter status
        """
    active_clients = len(self._client_buckets)
    total_buckets = sum((len(ops) for ops in self._client_buckets.values()))
    return {'timestamp': datetime.utcnow().isoformat(), 'active_clients': active_clients, 'total_buckets': total_buckets, 'default_requests_per_minute': self.default_requests_per_minute, 'default_burst_size': self.default_burst_size, 'operation_limits': dict(self._operation_limits)}

def get_metrics(self) -> Dict[str, Any]:
    """
        Get rate limiter metrics.
        
        Returns:
            Dictionary with metrics information
        """
    total_requests = sum((len(history) for history in self._request_history.values()))
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    recent_allowed = 0
    recent_rejected = 0
    for operation, history in self._request_history.items():
        for request in history:
            if request['timestamp'] >= cutoff_time:
                if request['allowed']:
                    recent_allowed += 1
                else:
                    recent_rejected += 1
    return {'total_requests_recorded': total_requests, 'recent_allowed_requests': recent_allowed, 'recent_rejected_requests': recent_rejected, 'rejection_rate': recent_rejected / max(1, recent_allowed + recent_rejected), 'active_operations': len(self._request_history), 'cleanup_interval': self.cleanup_interval}

def get_client_stats(self, client_id: str) -> Dict[str, Any]:
    """
        Get statistics for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dictionary with client statistics
        """
    if client_id not in self._client_buckets:
        return {'error': 'Client not found'}
    client_buckets = self._client_buckets[client_id]
    stats = {'client_id': client_id, 'operations': {}, 'total_operations': len(client_buckets)}
    for operation, bucket in client_buckets.items():
        self._refill_bucket(bucket)
        limits = self._get_operation_limits(operation)
        stats['operations'][operation] = {'remaining_tokens': int(bucket['tokens']), 'max_tokens': limits['burst_size'], 'requests_per_minute': limits['requests_per_minute'], 'last_request': bucket['last_request'].isoformat() if bucket['last_request'] else None}
    return stats

def reset_client_limits(self, client_id: str) -> bool:
    """
        Reset rate limits for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if client was reset, False if not found
        """
    if client_id in self._client_buckets:
        del self._client_buckets[client_id]
        logger.info(f'Reset rate limits for client {client_id}')
        return True
    return False

def _get_bucket(self, client_id: str, operation: str) -> Dict:
    """Get or create token bucket for client/operation"""
    if operation not in self._client_buckets[client_id]:
        limits = self._get_operation_limits(operation)
        self._client_buckets[client_id][operation] = {'tokens': float(limits['burst_size']), 'last_refill': datetime.utcnow(), 'last_request': None}
    return self._client_buckets[client_id][operation]

def _get_operation_limits(self, operation: str) -> Dict[str, int]:
    """Get rate limits for operation"""
    return self._operation_limits.get(operation, {'requests_per_minute': self.default_requests_per_minute, 'burst_size': self.default_burst_size})

def _refill_bucket(self, bucket: Dict) -> None:
    """Refill token bucket based on elapsed time"""
    now = datetime.utcnow()
    time_elapsed = (now - bucket['last_refill']).total_seconds()
    if time_elapsed > 0:
        operation_limits = self._get_operation_limits('default')
        refill_rate = operation_limits['requests_per_minute'] / 60.0
        tokens_to_add = time_elapsed * refill_rate
        bucket['tokens'] = min(operation_limits['burst_size'], bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now

def _record_request(self, operation: str, client_id: str, allowed: bool) -> None:
    """Record request for statistics"""
    self._request_history[operation].append({'timestamp': datetime.utcnow(), 'client_id': client_id, 'allowed': allowed})

def __init__(self, default_requests_per_minute: int=60, default_burst_size: int=10, cleanup_interval: int=300):
    self.default_requests_per_minute = default_requests_per_minute
    self.default_burst_size = default_burst_size
    self.cleanup_interval = cleanup_interval
    self._operation_limits: Dict[str, Dict[str, int]] = {}
    self._client_buckets: Dict[str, Dict[str, Dict]] = defaultdict(dict)
    self._request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
    self._last_cleanup = datetime.utcnow()
    logger.info('Rate limiter initialized')

def set_operation_limit(self, operation: str, requests_per_minute: int, burst_size: Optional[int]=None) -> None:
    """
        Set rate limit for specific operation.
        
        Args:
            operation: Name of operation
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute / 6)
        """
    if burst_size is None:
        burst_size = max(1, requests_per_minute // 6)
    self._operation_limits[operation] = {'requests_per_minute': requests_per_minute, 'burst_size': burst_size}
    logger.info(f'Set rate limit for {operation}: {requests_per_minute}/min, burst {burst_size}')

def get_status(self) -> Dict[str, Any]:
    """
        Get rate limiter status.
        
        Returns:
            Dictionary with rate limiter status
        """
    active_clients = len(self._client_buckets)
    total_buckets = sum((len(ops) for ops in self._client_buckets.values()))
    return {'timestamp': datetime.utcnow().isoformat(), 'active_clients': active_clients, 'total_buckets': total_buckets, 'default_requests_per_minute': self.default_requests_per_minute, 'default_burst_size': self.default_burst_size, 'operation_limits': dict(self._operation_limits)}

def get_metrics(self) -> Dict[str, Any]:
    """
        Get rate limiter metrics.
        
        Returns:
            Dictionary with metrics information
        """
    total_requests = sum((len(history) for history in self._request_history.values()))
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    recent_allowed = 0
    recent_rejected = 0
    for operation, history in self._request_history.items():
        for request in history:
            if request['timestamp'] >= cutoff_time:
                if request['allowed']:
                    recent_allowed += 1
                else:
                    recent_rejected += 1
    return {'total_requests_recorded': total_requests, 'recent_allowed_requests': recent_allowed, 'recent_rejected_requests': recent_rejected, 'rejection_rate': recent_rejected / max(1, recent_allowed + recent_rejected), 'active_operations': len(self._request_history), 'cleanup_interval': self.cleanup_interval}

def get_client_stats(self, client_id: str) -> Dict[str, Any]:
    """
        Get statistics for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dictionary with client statistics
        """
    if client_id not in self._client_buckets:
        return {'error': 'Client not found'}
    client_buckets = self._client_buckets[client_id]
    stats = {'client_id': client_id, 'operations': {}, 'total_operations': len(client_buckets)}
    for operation, bucket in client_buckets.items():
        self._refill_bucket(bucket)
        limits = self._get_operation_limits(operation)
        stats['operations'][operation] = {'remaining_tokens': int(bucket['tokens']), 'max_tokens': limits['burst_size'], 'requests_per_minute': limits['requests_per_minute'], 'last_request': bucket['last_request'].isoformat() if bucket['last_request'] else None}
    return stats

def reset_client_limits(self, client_id: str) -> bool:
    """
        Reset rate limits for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if client was reset, False if not found
        """
    if client_id in self._client_buckets:
        del self._client_buckets[client_id]
        logger.info(f'Reset rate limits for client {client_id}')
        return True
    return False

def _get_bucket(self, client_id: str, operation: str) -> Dict:
    """Get or create token bucket for client/operation"""
    if operation not in self._client_buckets[client_id]:
        limits = self._get_operation_limits(operation)
        self._client_buckets[client_id][operation] = {'tokens': float(limits['burst_size']), 'last_refill': datetime.utcnow(), 'last_request': None}
    return self._client_buckets[client_id][operation]

def _get_operation_limits(self, operation: str) -> Dict[str, int]:
    """Get rate limits for operation"""
    return self._operation_limits.get(operation, {'requests_per_minute': self.default_requests_per_minute, 'burst_size': self.default_burst_size})

def _refill_bucket(self, bucket: Dict) -> None:
    """Refill token bucket based on elapsed time"""
    now = datetime.utcnow()
    time_elapsed = (now - bucket['last_refill']).total_seconds()
    if time_elapsed > 0:
        operation_limits = self._get_operation_limits('default')
        refill_rate = operation_limits['requests_per_minute'] / 60.0
        tokens_to_add = time_elapsed * refill_rate
        bucket['tokens'] = min(operation_limits['burst_size'], bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now

def _record_request(self, operation: str, client_id: str, allowed: bool) -> None:
    """Record request for statistics"""
    self._request_history[operation].append({'timestamp': datetime.utcnow(), 'client_id': client_id, 'allowed': allowed})

def __init__(self, default_requests_per_minute: int=60, default_burst_size: int=10, cleanup_interval: int=300):
    self.default_requests_per_minute = default_requests_per_minute
    self.default_burst_size = default_burst_size
    self.cleanup_interval = cleanup_interval
    self._operation_limits: Dict[str, Dict[str, int]] = {}
    self._client_buckets: Dict[str, Dict[str, Dict]] = defaultdict(dict)
    self._request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
    self._last_cleanup = datetime.utcnow()
    logger.info('Rate limiter initialized')

def set_operation_limit(self, operation: str, requests_per_minute: int, burst_size: Optional[int]=None) -> None:
    """
        Set rate limit for specific operation.
        
        Args:
            operation: Name of operation
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute / 6)
        """
    if burst_size is None:
        burst_size = max(1, requests_per_minute // 6)
    self._operation_limits[operation] = {'requests_per_minute': requests_per_minute, 'burst_size': burst_size}
    logger.info(f'Set rate limit for {operation}: {requests_per_minute}/min, burst {burst_size}')

def get_status(self) -> Dict[str, Any]:
    """
        Get rate limiter status.
        
        Returns:
            Dictionary with rate limiter status
        """
    active_clients = len(self._client_buckets)
    total_buckets = sum((len(ops) for ops in self._client_buckets.values()))
    return {'timestamp': datetime.utcnow().isoformat(), 'active_clients': active_clients, 'total_buckets': total_buckets, 'default_requests_per_minute': self.default_requests_per_minute, 'default_burst_size': self.default_burst_size, 'operation_limits': dict(self._operation_limits)}

def get_metrics(self) -> Dict[str, Any]:
    """
        Get rate limiter metrics.
        
        Returns:
            Dictionary with metrics information
        """
    total_requests = sum((len(history) for history in self._request_history.values()))
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    recent_allowed = 0
    recent_rejected = 0
    for operation, history in self._request_history.items():
        for request in history:
            if request['timestamp'] >= cutoff_time:
                if request['allowed']:
                    recent_allowed += 1
                else:
                    recent_rejected += 1
    return {'total_requests_recorded': total_requests, 'recent_allowed_requests': recent_allowed, 'recent_rejected_requests': recent_rejected, 'rejection_rate': recent_rejected / max(1, recent_allowed + recent_rejected), 'active_operations': len(self._request_history), 'cleanup_interval': self.cleanup_interval}

def get_client_stats(self, client_id: str) -> Dict[str, Any]:
    """
        Get statistics for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dictionary with client statistics
        """
    if client_id not in self._client_buckets:
        return {'error': 'Client not found'}
    client_buckets = self._client_buckets[client_id]
    stats = {'client_id': client_id, 'operations': {}, 'total_operations': len(client_buckets)}
    for operation, bucket in client_buckets.items():
        self._refill_bucket(bucket)
        limits = self._get_operation_limits(operation)
        stats['operations'][operation] = {'remaining_tokens': int(bucket['tokens']), 'max_tokens': limits['burst_size'], 'requests_per_minute': limits['requests_per_minute'], 'last_request': bucket['last_request'].isoformat() if bucket['last_request'] else None}
    return stats

def reset_client_limits(self, client_id: str) -> bool:
    """
        Reset rate limits for specific client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if client was reset, False if not found
        """
    if client_id in self._client_buckets:
        del self._client_buckets[client_id]
        logger.info(f'Reset rate limits for client {client_id}')
        return True
    return False

def _get_bucket(self, client_id: str, operation: str) -> Dict:
    """Get or create token bucket for client/operation"""
    if operation not in self._client_buckets[client_id]:
        limits = self._get_operation_limits(operation)
        self._client_buckets[client_id][operation] = {'tokens': float(limits['burst_size']), 'last_refill': datetime.utcnow(), 'last_request': None}
    return self._client_buckets[client_id][operation]

def _get_operation_limits(self, operation: str) -> Dict[str, int]:
    """Get rate limits for operation"""
    return self._operation_limits.get(operation, {'requests_per_minute': self.default_requests_per_minute, 'burst_size': self.default_burst_size})

def _refill_bucket(self, bucket: Dict) -> None:
    """Refill token bucket based on elapsed time"""
    now = datetime.utcnow()
    time_elapsed = (now - bucket['last_refill']).total_seconds()
    if time_elapsed > 0:
        operation_limits = self._get_operation_limits('default')
        refill_rate = operation_limits['requests_per_minute'] / 60.0
        tokens_to_add = time_elapsed * refill_rate
        bucket['tokens'] = min(operation_limits['burst_size'], bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now

def _record_request(self, operation: str, client_id: str, allowed: bool) -> None:
    """Record request for statistics"""
    self._request_history[operation].append({'timestamp': datetime.utcnow(), 'client_id': client_id, 'allowed': allowed})
