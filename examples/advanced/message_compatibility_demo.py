"""
Beast Mode Message Compatibility Layer Demo

Demonstrates message type translation, version detection, and cross-version compatibility.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from src.beast_mode.messaging.compatibility import (
    MessageCompatibilityLayer,
    MessageTypeTranslator,
    MessageVersionDetector,
    MessageConverter,
    MessageVersion,
    CompatibilityMode,
    convert_message,
    detect_message_version,
    is_compatible_message,
)
from src.beast_mode.messaging.models import (
    BeastModeMessage,
    MessageType,
    AgentCapabilities,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def demo_message_type_translation():
    """Demonstrate message type translation between versions"""
    print_section("Message Type Translation Demo")

    translator = MessageTypeTranslator()

    # Test legacy to current translation
    print_subsection("Legacy to Current Translation")
    legacy_types = [
        "message",
        "request",
        "response",
        "discovery",
        "help",
        "spore",
        "msg",
        "text",
        "prompt",
        "query",
        "answer",
        "ping",
    ]

    for legacy_type in legacy_types:
        current_type = translator.translate_to_current(legacy_type)
        print(f"  {legacy_type:12} -> {current_type.value}")

    # Test current to legacy translation
    print_subsection("Current to Legacy Translation")
    current_types = [
        MessageType.SIMPLE_MESSAGE,
        MessageType.PROMPT_REQUEST,
        MessageType.PROMPT_RESPONSE,
        MessageType.AGENT_DISCOVERY,
        MessageType.HELP_WANTED,
        MessageType.SPORE_DELIVERY,
        MessageType.COLLABORATION_REQUEST,
        MessageType.SYSTEM_HEALTH,
    ]

    for current_type in current_types:
        legacy_type = translator.translate_to_legacy(current_type)
        print(f"  {current_type.value:25} -> {legacy_type}")


def demo_version_detection():
    """Demonstrate message version detection"""
    print_section("Message Version Detection Demo")

    detector = MessageVersionDetector()

    # Test messages from different versions
    test_messages = [
        # V1.0 format
        {
            "name": "V1.0 Message",
            "data": {
                "type": "message",
                "from": "agent1",
                "to": "agent2",
                "content": "Hello from V1.0",
            },
        },
        # V1.1 format
        {
            "name": "V1.1 Message",
            "data": {
                "type": "request",
                "source": "agent1",
                "target": "agent2",
                "payload": {"prompt": "What is AI?"},
                "correlation_id": "req_123",
                "priority": 3,
            },
        },
        # V1.2 format
        {
            "name": "V1.2 Message",
            "data": {
                "type": "collaboration_request",
                "source": "agent1",
                "target": "agent2",
                "payload": {"session_type": "code_review"},
                "correlation_id": "collab_456",
                "priority": 2,
            },
        },
        # V2.0 format
        {
            "name": "V2.0 Message",
            "data": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "type": "simple_message",
                "source": "agent1",
                "target": "agent2",
                "payload": {"content": "Hello from V2.0"},
                "timestamp": "2023-01-01T12:00:00",
                "priority": 5,
            },
        },
        # Unknown format
        {
            "name": "Unknown Message",
            "data": {"msg": "hello", "sender": "unknown_agent"},
        },
    ]

    for test_msg in test_messages:
        version = detector.detect_version(test_msg["data"])
        print(f"  {test_msg['name']:20} -> {version.value}")

        # Check compatibility
        is_compatible = detector.is_compatible_version(version, MessageVersion.V2_0)
        compat_status = "✓ Compatible" if is_compatible else "✗ Incompatible"
        print(f"  {' '*20}    {compat_status}")


def demo_message_conversion():
    """Demonstrate message conversion between versions"""
    print_section("Message Conversion Demo")

    converter = MessageConverter()

    # Test conversion scenarios
    conversion_scenarios = [
        {
            "name": "V1.0 Simple Message",
            "data": {
                "type": "message",
                "from": "legacy_agent",
                "to": "modern_agent",
                "content": "Hello from the past!",
            },
        },
        {
            "name": "V1.1 Help Request",
            "data": {
                "type": "help",
                "source": "helper_agent",
                "payload": {
                    "description": "Need help with Python",
                    "required_capabilities": ["python", "debugging"],
                },
                "request_id": "help_789",
                "priority": 2,
            },
        },
        {
            "name": "Malformed Message",
            "data": {
                "msg_type": "text",  # Wrong field name
                "sender": "broken_agent",  # Wrong field name
                "data": "This message has wrong field names",
            },
        },
    ]

    for scenario in conversion_scenarios:
        print_subsection(f"Converting: {scenario['name']}")

        result = converter.convert_to_current(scenario["data"])

        if result.success:
            print(f"  ✓ Conversion successful")
            print(f"    Original version: {result.original_version.value}")
            print(f"    Target version: {result.target_version.value}")
            print(f"    Message type: {result.message.type.value}")
            print(f"    Source: {result.message.source}")
            print(f"    Target: {result.message.target}")

            if result.warnings:
                print(f"    Warnings: {len(result.warnings)}")
                for warning in result.warnings:
                    print(f"      - {warning}")
        else:
            print(f"  ✗ Conversion failed")
            for error in result.errors:
                print(f"    Error: {error}")


def demo_compatibility_layer():
    """Demonstrate the main compatibility layer functionality"""
    print_section("Compatibility Layer Demo")

    # Test different compatibility modes
    modes = [
        (CompatibilityMode.STRICT, "Strict Mode"),
        (CompatibilityMode.CONVERT, "Convert Mode"),
        (CompatibilityMode.PASSTHROUGH, "Passthrough Mode"),
    ]

    test_message = {
        "type": "unknown_custom_type",
        "source": "custom_agent",
        "payload": {"custom_data": "test"},
    }

    for mode, mode_name in modes:
        print_subsection(mode_name)

        compatibility_layer = MessageCompatibilityLayer(mode)

        # Register custom handler for unknown type
        if mode != CompatibilityMode.STRICT:
            compatibility_layer.register_unknown_type_handler(
                "unknown_custom_type", MessageType.TECHNICAL_EXCHANGE
            )

        result = compatibility_layer.process_message(test_message)

        if result.success:
            print(f"  ✓ Processing successful")
            print(f"    Mapped type: {result.message.type.value}")
        else:
            print(f"  ✗ Processing failed")
            for error in result.errors:
                print(f"    Error: {error}")


def demo_real_world_scenarios():
    """Demonstrate real-world compatibility scenarios"""
    print_section("Real-World Compatibility Scenarios")

    compatibility_layer = MessageCompatibilityLayer(CompatibilityMode.CONVERT)

    # Scenario 1: Mixed agent network
    print_subsection("Mixed Agent Network Simulation")

    network_messages = [
        # Legacy agent announcing presence
        {
            "type": "discovery",
            "from": "legacy_file_processor",
            "agent_info": {
                "capabilities": ["file_processing", "data_analysis"],
                "version": "1.0",
            },
        },
        # Modern agent requesting help
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "type": "help_wanted",
            "source": "modern_ml_agent",
            "payload": {
                "description": "Need help processing large CSV files",
                "required_capabilities": ["file_processing", "data_analysis"],
                "urgency": "normal",
            },
            "priority": 3,
        },
        # Legacy agent responding
        {
            "type": "help",
            "from": "legacy_file_processor",
            "to": "modern_ml_agent",
            "response": "I can help with CSV processing",
            "capabilities_match": ["file_processing", "data_analysis"],
        },
    ]

    processed_count = 0
    for i, msg in enumerate(network_messages):
        result = compatibility_layer.process_message(msg)
        if result.success:
            processed_count += 1
            print(
                f"  Message {i+1}: ✓ {result.message.type.value} from {result.message.source}"
            )
        else:
            print(f"  Message {i+1}: ✗ Failed to process")

    print(
        f"  Successfully processed: {processed_count}/{len(network_messages)} messages"
    )

    # Scenario 2: Spore sharing across versions
    print_subsection("Cross-Version Spore Sharing")

    # Modern agent sharing spore
    modern_spore = BeastModeMessage(
        type=MessageType.SPORE_DELIVERY,
        source="optimization_expert",
        target="legacy_agent",
        payload={
            "spore_name": "performance_optimizer",
            "spore_content": "def optimize_performance(): return 'optimized'",
            "metadata": {
                "version": "2.1",
                "author": "optimization_expert",
                "description": "Performance optimization spore",
            },
        },
    )

    # Convert to legacy format for legacy agent
    legacy_format = compatibility_layer.converter.convert_to_legacy(
        modern_spore, MessageVersion.V1_0
    )

    print(f"  Modern spore converted to legacy format:")
    print(f"    Type: {legacy_format['type']}")
    print(f"    From: {legacy_format['from']}")
    print(f"    To: {legacy_format['to']}")
    print(f"    Has payload: {'payload' in legacy_format}")

    # Convert back to modern format
    result = compatibility_layer.process_message(legacy_format)
    if result.success:
        print(f"  ✓ Successfully converted back to modern format")
        print(f"    Final type: {result.message.type.value}")


def demo_performance_and_statistics():
    """Demonstrate performance monitoring and statistics"""
    print_section("Performance and Statistics Demo")

    compatibility_layer = MessageCompatibilityLayer(CompatibilityMode.CONVERT)

    # Process a variety of messages
    test_messages = []

    # Generate V1.0 messages
    for i in range(20):
        test_messages.append(
            {"type": "message", "from": f"agent_{i}", "content": f"Message {i}"}
        )

    # Generate V1.1 messages
    for i in range(15):
        test_messages.append(
            {
                "type": "request",
                "source": f"requester_{i}",
                "payload": {"prompt": f"Request {i}"},
                "priority": (i % 5) + 1,
            }
        )

    # Generate V2.0 messages
    for i in range(10):
        test_messages.append(
            BeastModeMessage(
                type=MessageType.SYSTEM_HEALTH,
                source=f"health_monitor_{i}",
                payload={"status": "healthy", "uptime": i * 100},
            )
        )

    # Process all messages
    print_subsection("Processing Messages")
    successful = 0
    failed = 0

    for msg in test_messages:
        result = compatibility_layer.process_message(msg)
        if result.success:
            successful += 1
        else:
            failed += 1

    print(f"  Total messages: {len(test_messages)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Success rate: {(successful/len(test_messages)*100):.1f}%")

    # Show statistics
    print_subsection("Compatibility Statistics")
    stats = compatibility_layer.get_compatibility_stats()

    print(f"  Mode: {stats['mode']}")
    print(f"  Messages processed: {stats['stats']['messages_processed']}")
    print(f"  Conversions successful: {stats['stats']['conversions_successful']}")
    print(f"  Conversions failed: {stats['stats']['conversions_failed']}")

    if stats["stats"]["version_distribution"]:
        print(f"  Version distribution:")
        for version, count in stats["stats"]["version_distribution"].items():
            print(f"    {version}: {count} messages")

    # Generate compatibility report
    print_subsection("Compatibility Report")
    report = compatibility_layer.create_compatibility_report()

    print(f"  Summary:")
    for key, value in report["summary"].items():
        print(f"    {key}: {value}")


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print_section("Convenience Functions Demo")

    # Test convert_message function
    print_subsection("convert_message() Function")

    legacy_message = {
        "type": "help",
        "from": "helper",
        "payload": {
            "description": "Need assistance",
            "required_capabilities": ["python"],
        },
    }

    converted = convert_message(legacy_message)
    if converted:
        print(f"  ✓ Conversion successful")
        print(f"    Type: {converted.type.value}")
        print(f"    Source: {converted.source}")
    else:
        print(f"  ✗ Conversion failed")

    # Test detect_message_version function
    print_subsection("detect_message_version() Function")

    test_messages = [
        {"type": "message", "from": "agent1"},
        {"type": "request", "source": "agent2", "correlation_id": "123"},
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "type": "simple_message",
            "source": "agent3",
        },
    ]

    for i, msg in enumerate(test_messages):
        version = detect_message_version(msg)
        print(f"  Message {i+1}: {version.value}")

    # Test is_compatible_message function
    print_subsection("is_compatible_message() Function")

    compatibility_tests = [
        {"type": "simple_message", "source": "agent1"},  # Compatible
        {"invalid": "structure"},  # Incompatible
        {"type": "message", "from": "legacy_agent"},  # Compatible (legacy)
    ]

    for i, msg in enumerate(compatibility_tests):
        is_compat = is_compatible_message(msg)
        status = "✓ Compatible" if is_compat else "✗ Incompatible"
        print(f"  Message {i+1}: {status}")


async def main():
    """Run all compatibility demos"""
    print("Beast Mode Message Compatibility Layer Demo")
    print("=" * 60)

    try:
        # Run all demo functions
        demo_message_type_translation()
        demo_version_detection()
        demo_message_conversion()
        demo_compatibility_layer()
        demo_real_world_scenarios()
        demo_performance_and_statistics()
        demo_convenience_functions()

        print_section("Demo Complete")
        print("All compatibility layer features demonstrated successfully!")

    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
