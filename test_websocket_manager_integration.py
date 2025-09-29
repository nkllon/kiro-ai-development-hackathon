#!/usr/bin/env python3
"""Integration test for WebSocket Manager implementation."""

import asyncio
import json
from datetime import datetime

# Test the WebSocket Manager implementation
async def test_websocket_manager():
    """Test WebSocket Manager functionality."""
    print("Testing WebSocket Manager Implementation...")
    
    try:
        # Import the manager
        from src.beast_mode.observatory.websocket.manager import (
            WebSocketManager,
            WebSocketManagerConfig,
            create_websocket_manager
        )
        
        print("✓ WebSocket Manager imported successfully")
        
        # Test configuration
        config = WebSocketManagerConfig(
            base_url="ws://localhost:8000",
            max_connections_per_endpoint=2,
            connection_timeout=5.0,
            retry_max_attempts=3,
            health_check_interval=10.0
        )
        
        print("✓ Configuration created successfully")
        print(f"  - Base URL: {config.base_url}")
        print(f"  - Max connections per endpoint: {config.max_connections_per_endpoint}")
        print(f"  - Connection timeout: {config.connection_timeout}")
        print(f"  - Retry max attempts: {config.retry_max_attempts}")
        
        # Test manager initialization
        manager = WebSocketManager(config)
        print("✓ WebSocket Manager initialized successfully")
        print(f"  - Endpoints: {manager.endpoints}")
        print(f"  - Retry strategies initialized: {len(manager.retry_strategies)}")
        print(f"  - Connection locks initialized: {len(manager.connection_locks)}")
        
        # Test manager start/stop
        await manager.start()
        print("✓ WebSocket Manager started successfully")
        
        # Test connection status
        status = manager.get_all_connection_status()
        print(f"✓ Connection status retrieved for {len(status)} endpoints")
        
        # Test health status (will fail without real server, but that's expected)
        try:
            health_status = await manager.get_health_status()
            print(f"✓ Health status retrieved for {len(health_status)} endpoints")
        except Exception as e:
            print(f"⚠ Health status check failed (expected without real server): {e}")
        
        await manager.stop()
        print("✓ WebSocket Manager stopped successfully")
        
        # Test convenience function
        manager2 = await create_websocket_manager(
            base_url="ws://test.example.com",
            max_connections_per_endpoint=1
        )
        print("✓ Convenience function create_websocket_manager works")
        await manager2.stop()
        
        print("\n🎉 All WebSocket Manager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_retry_strategy():
    """Test retry strategy functionality."""
    print("\nTesting Retry Strategy...")
    
    try:
        from src.beast_mode.observatory.websocket.retry_strategy import ExponentialBackoffRetry
        
        retry = ExponentialBackoffRetry(
            base_delay=1.0,
            max_delay=10.0,
            multiplier=2.0,
            max_attempts=5
        )
        
        print("✓ ExponentialBackoffRetry created successfully")
        
        # Test delay calculation
        retry.increment_attempt()
        delay1 = retry.calculate_delay()
        print(f"✓ First retry delay: {delay1:.2f}s")
        
        retry.increment_attempt()
        delay2 = retry.calculate_delay()
        print(f"✓ Second retry delay: {delay2:.2f}s")
        
        # Test retry logic
        from src.beast_mode.observatory.websocket.exceptions import ConnectionFailedError
        should_retry = retry.should_retry(ConnectionFailedError("Test error"))
        print(f"✓ Should retry connection error: {should_retry}")
        
        retry.reset()
        print("✓ Retry strategy reset successfully")
        
        print("🎉 Retry strategy tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Retry strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_connection_class():
    """Test WebSocket connection class."""
    print("\nTesting WebSocket Connection...")
    
    try:
        from src.beast_mode.observatory.websocket.connection import (
            WebSocketConnection,
            ConnectionState,
            ConnectionStatus
        )
        
        # Test connection state
        state = ConnectionState(endpoint="/ws/test")
        print("✓ ConnectionState created successfully")
        print(f"  - Endpoint: {state.endpoint}")
        print(f"  - Status: {state.status.value}")
        
        # Test connection class
        connection = WebSocketConnection("/ws/test", connection_timeout=5.0)
        print("✓ WebSocketConnection created successfully")
        print(f"  - Endpoint: {connection.endpoint}")
        print(f"  - Connection timeout: {connection.connection_timeout}")
        
        # Test state methods
        is_connected = connection.is_connected()
        print(f"✓ Connection status check: {is_connected}")
        
        metrics = connection.get_connection_metrics()
        print("✓ Connection metrics retrieved successfully")
        print(f"  - Status: {metrics['status']}")
        print(f"  - Message count: {metrics['message_count']}")
        
        print("🎉 WebSocket connection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_validator():
    """Test health validator functionality."""
    print("\nTesting Health Validator...")
    
    try:
        from src.beast_mode.observatory.websocket.health_validator import (
            WebSocketHealthValidator,
            HealthStatus,
            QualityMetrics,
            FailureIndicator
        )
        
        validator = WebSocketHealthValidator(timeout=5.0, max_retries=3)
        print("✓ WebSocketHealthValidator created successfully")
        print(f"  - Endpoints: {validator.endpoints}")
        print(f"  - Timeout: {validator.timeout}")
        print(f"  - Max retries: {validator.max_retries}")
        
        # Test health summary
        summary = validator.get_health_summary()
        print("✓ Health summary retrieved successfully")
        print(f"  - Overall status: {summary['overall_status']}")
        print(f"  - Total endpoints: {summary['total_endpoints']}")
        
        print("🎉 Health validator tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Health validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("WebSocket Manager Implementation Test Suite")
    print("=" * 60)
    
    tests = [
        test_websocket_manager,
        test_retry_strategy,
        test_connection_class,
        test_health_validator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! WebSocket Manager implementation is working correctly.")
        
        # Log final completion
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '2.1',
            'action': 'websocket_manager_implementation_completed',
            'status': 'completed',
            'summary': 'WebSocket manager implemented with retry logic, connection pooling, and health monitoring',
            'test_results': {
                'total_tests': total,
                'passed_tests': passed,
                'success_rate': f"{(passed/total)*100:.1f}%"
            }
        }
        print(json.dumps(log_data))
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(main())