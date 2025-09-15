#!/usr/bin/env python3
"""
Backward Compatibility Validation Script

Runs comprehensive tests to validate that all existing functionality
works identically after the pluggable transport refactoring.
"""

import sys
import subprocess
import time
from pathlib import Path


def run_test_suite(test_file, description):
    """Run a specific test suite and report results"""
    print(f"\n🧪 Running {description}...")
    print("=" * 60)

    try:
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ {description} PASSED ({duration:.1f}s)")
            return True
        else:
            print(f"❌ {description} FAILED ({duration:.1f}s)")
            print("\nSTDOUT:")
            print(result.stdout)
            print("\nSTDERR:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ {description} ERROR: {e}")
        return False


def validate_imports():
    """Validate that all expected imports work"""
    print("\n📦 Validating Imports...")
    print("=" * 30)

    imports_to_test = [
        "from src.beast_mode.messaging.models import BeastModeMessage, MessageType",
        "from src.beast_mode.messaging.transport import BeastModeTransport, TransportFactory",
        "from src.beast_mode.messaging.daemon_client import BeastModeDaemon, BeastModeClient",
        "from src.beast_mode.messaging.unified_client import BeastModeClient as UnifiedClient",
        "from src.beast_mode.messaging.shared_state import BeastModeSharedState",
        "from src.beast_mode.messaging.redis_transport import RedisTransport",
    ]

    all_passed = True

    for import_statement in imports_to_test:
        try:
            exec(import_statement)
            print(f"✅ {import_statement}")
        except Exception as e:
            print(f"❌ {import_statement} - ERROR: {e}")
            all_passed = False

    return all_passed


def validate_transport_factory():
    """Validate transport factory functionality"""
    print("\n🏭 Validating Transport Factory...")
    print("=" * 35)

    try:
        from src.beast_mode.messaging.transport import TransportFactory

        # Test available transports
        available = TransportFactory.get_available_transports()
        print(f"✅ Available transports: {available}")

        if "redis" not in available:
            print("❌ Redis transport not registered")
            return False

        # Test transport creation
        transport = TransportFactory.create_transport("redis", agent_id="test")
        print("✅ Redis transport creation successful")

        # Test transport interface
        required_methods = [
            "initialize",
            "send_message",
            "subscribe",
            "start_daemon",
            "stop_daemon",
            "get_status",
            "get_capabilities",
        ]

        for method in required_methods:
            if not hasattr(transport, method):
                print(f"❌ Transport missing method: {method}")
                return False

        print("✅ Transport interface complete")
        return True

    except Exception as e:
        print(f"❌ Transport factory validation failed: {e}")
        return False


def validate_message_compatibility():
    """Validate message format compatibility"""
    print("\n📨 Validating Message Compatibility...")
    print("=" * 40)

    try:
        from src.beast_mode.messaging.models import BeastModeMessage, MessageType

        # Test message creation
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test_agent",
            payload={"text": "compatibility test"},
        )

        print("✅ Message creation successful")

        # Test serialization
        message_dict = message.model_dump()
        print("✅ Message serialization successful")

        # Test deserialization
        reconstructed = BeastModeMessage(**message_dict)
        print("✅ Message deserialization successful")

        # Test field compatibility
        required_fields = [
            "id",
            "type",
            "source",
            "target",
            "payload",
            "timestamp",
            "priority",
        ]
        for field in required_fields:
            if not hasattr(message, field):
                print(f"❌ Message missing field: {field}")
                return False

        print("✅ Message fields complete")

        # Test message types
        expected_types = [
            "SIMPLE_MESSAGE",
            "AGENT_DISCOVERY",
            "HELP_WANTED",
            "SPORE_DELIVERY",
            "TECHNICAL_EXCHANGE",
        ]

        for msg_type in expected_types:
            if not hasattr(MessageType, msg_type):
                print(f"❌ Missing message type: {msg_type}")
                return False

        print("✅ Message types complete")
        return True

    except Exception as e:
        print(f"❌ Message compatibility validation failed: {e}")
        return False


def main():
    """Run complete backward compatibility validation"""
    print("🔍 Beast Mode Backward Compatibility Validation")
    print("=" * 50)
    print("Testing that all existing functionality works identically")
    print("after pluggable transport refactoring.\n")

    start_time = time.time()
    results = []

    # 1. Validate imports
    results.append(("Import Validation", validate_imports()))

    # 2. Validate transport factory
    results.append(("Transport Factory", validate_transport_factory()))

    # 3. Validate message compatibility
    results.append(("Message Compatibility", validate_message_compatibility()))

    # 4. Run backward compatibility tests
    results.append(
        (
            "Backward Compatibility Tests",
            run_test_suite(
                "tests/integration/test_backward_compatibility.py",
                "Backward Compatibility Tests",
            ),
        )
    )

    # 5. Run performance benchmarks
    results.append(
        (
            "Performance Benchmarks",
            run_test_suite(
                "tests/integration/test_performance_benchmarks.py",
                "Performance Benchmarks",
            ),
        )
    )

    # 6. Run unit tests for new components
    unit_tests = [
        ("Transport Tests", "tests/unit/test_redis_transport.py"),
        ("Shared State Tests", "tests/unit/test_shared_state.py"),
        ("Unified Client Tests", "tests/unit/test_unified_client.py"),
    ]

    for test_name, test_file in unit_tests:
        results.append((test_name, run_test_suite(test_file, test_name)))

    # Summary
    total_time = time.time() - start_time
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 30)
    print(f"Total time: {total_time:.1f}s")
    print(f"Tests passed: {passed}/{total}")

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

    if passed == total:
        print(f"\n🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ Backward compatibility is maintained")
        print("✅ Performance is acceptable")
        print("✅ All interfaces work correctly")
        return 0
    else:
        print(f"\n❌ VALIDATION FAILED!")
        print(f"   {total - passed} test(s) failed")
        print("   Please review the failures above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
