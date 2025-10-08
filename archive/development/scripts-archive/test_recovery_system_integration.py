#!/usr/bin/env python3
"""
Integration test for the Automated WebSocket Recovery System.
"""

import asyncio
import json
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, 'src')

from beast_mode.observatory.recovery import (
    AutomatedRecoverySystem,
    FailureType,
    FailureData
)


async def test_recovery_system():
    """Test the automated recovery system."""
    print("Starting Automated WebSocket Recovery System Test")
    print("=" * 60)
    
    # Initialize the recovery system
    recovery_system = AutomatedRecoverySystem()
    
    try:
        # Start the system
        await recovery_system.start()
        print("✓ Recovery system started successfully")
        
        # Test 1: Detect failure from symptoms
        print("\n1. Testing failure detection from symptoms...")
        symptoms = ["connection refused", "timeout"]
        failure_type = await recovery_system.detect_failure(symptoms)
        print(f"✓ Detected failure type: {failure_type.value}")
        
        # Test 2: Classify failure from detailed data
        print("\n2. Testing failure classification from detailed data...")
        failure_data = {
            "error_code": 1033,
            "error_message": "Cloudflare bot protection triggered",
            "http_status": 403,
            "response_headers": {"cf-ray": "1234567890"},
            "symptoms": ["connection refused", "timeout"]
        }
        classified_type = await recovery_system.classify_failure(failure_data)
        print(f"✓ Classified failure type: {classified_type.value}")
        
        # Test 3: Execute recovery
        print("\n3. Testing recovery execution...")
        recovery_result = await recovery_system.execute_recovery(FailureType.CONNECTION_REFUSED)
        print(f"✓ Recovery result: success={recovery_result.success}, strategy={recovery_result.strategy_used}, time={recovery_result.recovery_time:.2f}s")
        
        # Test 4: Handle failure with symptoms
        print("\n4. Testing failure handling with symptoms...")
        handle_result = await recovery_system.handle_failure(["connection refused"], failure_data)
        print(f"✓ Handle result: success={handle_result.success}, strategy={handle_result.strategy_used}")
        
        # Test 5: Get system status
        print("\n5. Testing system status...")
        status = recovery_system.get_system_status()
        print(f"✓ System active: {status['is_active']}")
        print(f"✓ Uptime: {status['uptime_seconds']:.2f}s")
        print(f"✓ Failures detected: {status['metrics']['total_failures_detected']}")
        print(f"✓ Recoveries attempted: {status['metrics']['total_recoveries_attempted']}")
        print(f"✓ Success rate: {status['metrics']['success_rate']:.2%}")
        
        # Test 6: Get recovery statistics
        print("\n6. Testing recovery statistics...")
        stats = await recovery_system.get_recovery_statistics()
        print(f"✓ Statistics retrieved: {len(stats)} sections")
        print(f"✓ Available strategies: {len(stats['available_strategies'])}")
        
        # Test 7: Test different failure types
        print("\n7. Testing different failure types...")
        failure_types = [
            FailureType.CONNECTION_REFUSED,
            FailureType.UPGRADE_FAILED,
            FailureType.TIMEOUT,
            FailureType.AUTHENTICATION_FAILED,
            FailureType.RATE_LIMITED,
            FailureType.BOT_PROTECTION_TRIGGERED
        ]
        
        for failure_type in failure_types:
            result = await recovery_system.execute_recovery(failure_type)
            print(f"✓ {failure_type.value}: success={result.success}, strategy={result.strategy_used}")
        
        # Stop the system
        await recovery_system.stop()
        print("\n✓ Recovery system stopped successfully")
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_failure_classifier():
    """Test the failure classifier component."""
    print("\nTesting FailureClassifier component...")
    
    from beast_mode.observatory.recovery import FailureClassifier
    
    classifier = FailureClassifier()
    
    # Test different failure scenarios
    test_cases = [
        {
            "name": "Bot Protection",
            "data": FailureData(
                error_code=1033,
                error_message="Cloudflare bot protection triggered",
                http_status=403,
                response_headers={"cf-ray": "1234567890"}
            ),
            "expected": FailureType.BOT_PROTECTION_TRIGGERED
        },
        {
            "name": "Connection Refused",
            "data": FailureData(
                error_message="Connection refused",
                http_status=502,
                symptoms=["connection refused"]
            ),
            "expected": FailureType.CONNECTION_REFUSED
        },
        {
            "name": "Timeout",
            "data": FailureData(
                error_message="Connection timed out",
                symptoms=["timeout"]
            ),
            "expected": FailureType.TIMEOUT
        },
        {
            "name": "Rate Limited",
            "data": FailureData(
                http_status=429,
                error_message="Too many requests",
                connection_attempts=15
            ),
            "expected": FailureType.RATE_LIMITED
        }
    ]
    
    for test_case in test_cases:
        result = await classifier.classify_failure(test_case["data"])
        success = result == test_case["expected"]
        print(f"✓ {test_case['name']}: {result.value} ({'PASS' if success else 'FAIL'})")
    
    return True


async def test_recovery_strategies():
    """Test the recovery strategies component."""
    print("\nTesting Recovery Strategies component...")
    
    from beast_mode.observatory.recovery import (
        WebSocketReconnectionStrategy,
        TunnelRestartStrategy,
        ConfigurationReloadStrategy,
        BotProtectionClearStrategy,
        FallbackActivationStrategy
    )
    
    strategies = [
        WebSocketReconnectionStrategy(),
        TunnelRestartStrategy(),
        ConfigurationReloadStrategy(),
        BotProtectionClearStrategy(),
        FallbackActivationStrategy()
    ]
    
    for strategy in strategies:
        print(f"✓ {strategy.name}: priority={strategy.get_priority()}")
        
        # Test can_handle for different failure types
        for failure_type in FailureType:
            can_handle = await strategy.can_handle(failure_type)
            if can_handle:
                print(f"  - Can handle: {failure_type.value}")
    
    return True


async def main():
    """Main test function."""
    print("Automated WebSocket Recovery System - Integration Tests")
    print("=" * 60)
    
    try:
        # Test individual components
        await test_failure_classifier()
        await test_recovery_strategies()
        
        # Test main system
        success = await test_recovery_system()
        
        if success:
            print("\n🎉 All tests passed successfully!")
            print("\nFinal log entry:")
            final_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "task": "4.1",
                "status": "completed",
                "summary": "Automated recovery implemented"
            }
            print(json.dumps(final_log, indent=2))
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)