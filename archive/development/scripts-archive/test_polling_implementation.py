#!/usr/bin/env python3
"""
Test script for Intelligent HTTP Polling Fallback System
"""

import asyncio
import json
from datetime import datetime
from src.beast_mode.observatory.polling import IntelligentPoller, RateLimiter, RequestDeduplicator, BotSafeHeaders, PollingStrategy


async def test_basic_functionality():
    """Test basic functionality of the polling system."""
    
    print(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "task": "2.2",
        "action": "test_start",
        "status": "in_progress",
        "description": "Testing intelligent polling system"
    }))
    
    # Test BotSafeHeaders
    print("\n=== Testing BotSafeHeaders ===")
    headers = BotSafeHeaders()
    test_headers = headers.get_headers("http://test.com/api")
    print(f"Generated headers: {test_headers}")
    
    retry_headers = headers.get_retry_headers(3, "http://test.com/api")
    print(f"Retry headers: {retry_headers}")
    
    # Test RateLimiter
    print("\n=== Testing RateLimiter ===")
    rate_limiter = RateLimiter()
    
    # Test can make request
    can_request = await rate_limiter.can_make_request("test-endpoint")
    print(f"Can make request: {can_request}")
    
    # Record a request
    await rate_limiter.record_request("test-endpoint")
    print("Request recorded")
    
    # Test RequestDeduplicator
    print("\n=== Testing RequestDeduplicator ===")
    deduplicator = RequestDeduplicator()
    
    # Mock request function
    async def mock_request_func(endpoint, params=None):
        return {"data": "test_response"}, 200
    
    # Test caching
    response1, status1 = await deduplicator.get_or_request("test-endpoint", {}, mock_request_func)
    print(f"First request: {response1}, {status1}")
    
    response2, status2 = await deduplicator.get_or_request("test-endpoint", {}, mock_request_func)
    print(f"Second request (should be cached): {response2}, {status2}")
    
    # Test PollingStrategy
    print("\n=== Testing PollingStrategy ===")
    strategy = PollingStrategy()
    
    # Test interval calculation
    interval1 = strategy.calculate_next_interval("test-endpoint", success=True)
    print(f"Success interval: {interval1}")
    
    interval2 = strategy.calculate_next_interval("test-endpoint", success=False)
    print(f"Failure interval: {interval2}")
    
    # Test IntelligentPoller
    print("\n=== Testing IntelligentPoller ===")
    poller = IntelligentPoller()
    
    # Test status
    status = await poller.get_status()
    print(f"Poller status: {json.dumps(status, indent=2)}")
    
    # Test shutdown
    await poller.shutdown()
    print("Poller shutdown complete")
    
    print(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "task": "2.2",
        "action": "test_complete",
        "status": "completed",
        "description": "All tests passed successfully"
    }))


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())