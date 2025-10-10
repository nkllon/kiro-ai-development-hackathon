```python
import re
from threading import Lock
import time

class RateLimiter:
    def __init__(self, limit=100, period=60):
        if not isinstance(limit, int) or limit < 0:
            raise ValueError('Invalid limit')
        if not isinstance(period, int) or period <= 0:
            raise ValueError('Invalid period')
        
        self._lock = Lock()
        self._endpoints = {}
        self.limit = limit
        self.period = period
    
    def can_proceed(self, endpoint):
        with self._lock:
            if not self._validate_endpoint(endpoint):
                return False
            
            elapsed = time.monotonic() - self._endpoints[endpoint]['last_check']
            if elapsed < self.period:
                return self._endpoints[endpoint]['count'] < self.limit
        
        return True
    
    def record_request(self, endpoint):
        with self._lock:
            if not self._validate_endpoint(endpoint):
                raise ValueError('Invalid endpoint')
            
            if self._endpoints[endpoint]['count'] >= self.limit:
                return False
            
            self._endpoints[endpoint]['count'] += 1
            self._endpoints[endpoint]['last_check'] = time.monotonic()
            return True
        
    def reset(self, endpoint):
        with self._lock:
            if not self._validate_endpoint(endpoint):
                raise ValueError('Invalid endpoint')
            
            self._endpoints[endpoint]['count'] = 0
            self._endpoints[endpoint]['last_check'] = time.monotonic()
            return True
    
    def _validate_endpoint(self, endpoint: str) -> bool:
        if not isinstance(endpoint, str) or len(endpoint) == 0:
            raise ValueError('Invalid endpoint')
        
        if endpoint not in self._endpoints:
            self._endpoints[endpoint] = {
                'count': 0,
                'last_check': time.monotonic()
            }
            
        elapsed = time.monotonic() - self._endpoints[endpoint]['last_check']
        if elapsed >= self.period:
            self._endpoints[endpoint]['count'] = 0
            self._endpoints[endpoint]['last_check'] = time.monotonic()
        
        return True
```
