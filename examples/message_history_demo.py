#!/usr/bin/env python3
"""
Beast Mode Message History Demo

Demonstrates the comprehensive message history and retrieval capabilities
of the Beast Mode agent collaboration network.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from src.beast_mode.messaging.message_history import (
    MessageHistoryManager,
    MessageFilter,
    MessageStatus,
    SortOrder,
)
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_messages():
    """Create sample messages for demonstration"""
    now = datetime.now()

    messages = [
        BeastModeMessage(
            id="demo-msg-001",
            type=MessageType.SIMPLE_MESSAGE,
            source="alice-agent",
            target="bob-agent",
            payload={"text": "Hey Bob, how's the optimization project going?"},
            timestamp=now - timedelta(hours=3),
            priority=5,
        ),
        BeastModeMessage(
            id="demo-msg-002",
            type=MessageType.HELP_WANTED,
            source="bob-agent",
            target="alice-agent",
            payload={
                "help_type": "performance_optimization",
                "description": "Need help optimizing database queries for the user service",
                "urgency": "medium",
                "estimated_effort": "2-3 hours",
            },
            timestamp=now - timedelta(hours=2, minutes=30),
            priority=3,
            correlation_id="optimization-conv-001",
        ),
        BeastModeMessage(
            id="demo-msg-003",
            type=MessageType.HELP_RESPONSE,
            source="alice-agent",
            target="bob-agent",
            payload={
                "response": "I can definitely help with database optimization!",
                "availability": "Available now for the next 4 hours",
                "expertise_areas": ["PostgreSQL", "query optimization", "indexing"],
            },
            timestamp=now - timedelta(hours=2, minutes=15),
            priority=3,
            correlation_id="optimization-conv-001",
        ),
        BeastModeMessage(
            id="demo-msg-004",
            type=MessageType.SPORE_DELIVERY,
            source="alice-agent",
            target="bob-agent",
            payload={
                "spore_name": "database_query_optimizer",
                "spore_description": "Systematic approach to database query optimization",
                "spore_content": {
                    "methodology": "EXPLAIN ANALYZE -> Index Analysis -> Query Rewrite",
                    "tools": ["pg_stat_statements", "EXPLAIN", "pgbench"],
                    "success_metrics": [
                        "query_time_reduction",
                        "cpu_usage",
                        "memory_usage",
                    ],
                },
            },
            timestamp=now - timedelta(hours=2),
            priority=4,
            correlation_id="optimization-conv-001",
        ),
        BeastModeMessage(
            id="demo-msg-005",
            type=MessageType.SYSTEM_HEALTH,
            source="monitoring-agent",
            target=None,  # Broadcast
            payload={
                "status": "healthy",
                "cpu_usage": 23.5,
                "memory_usage": 67.2,
                "active_agents": 12,
                "message_throughput": 145.7,
            },
            timestamp=now - timedelta(hours=1, minutes=30),
            priority=7,
        ),
        BeastModeMessage(
            id="demo-msg-006",
            type=MessageType.TECHNICAL_EXCHANGE,
            source="bob-agent",
            target="alice-agent",
            payload={
                "topic": "query_optimization_results",
                "details": {
                    "before_optimization": {
                        "avg_query_time": "2.3s",
                        "cpu_usage": "85%",
                    },
                    "after_optimization": {
                        "avg_query_time": "0.4s",
                        "cpu_usage": "32%",
                    },
                    "improvement": "82% faster, 62% less CPU usage",
                },
                "next_steps": [
                    "Monitor for 24h",
                    "Apply to other services",
                    "Document learnings",
                ],
            },
            timestamp=now - timedelta(hours=1),
            priority=4,
            correlation_id="optimization-conv-001",
        ),
        BeastModeMessage(
            id="demo-msg-007",
            type=MessageType.SIMPLE_MESSAGE,
            source="charlie-agent",
            target="alice-agent",
            payload={
                "text": "Alice, could you share that database optimization spore with me too?"
            },
            timestamp=now - timedelta(minutes=45),
            priority=5,
        ),
        BeastModeMessage(
            id="demo-msg-008",
            type=MessageType.SPORE_REQUEST,
            source="charlie-agent",
            target="alice-agent",
            payload={
                "requested_spore": "database_query_optimizer",
                "use_case": "Optimizing analytics queries in the reporting service",
                "context": "Similar performance issues with complex JOIN queries",
            },
            timestamp=now - timedelta(minutes=30),
            priority=4,
        ),
        BeastModeMessage(
            id="demo-msg-009",
            type=MessageType.SPORE_DELIVERY,
            source="alice-agent",
            target="charlie-agent",
            payload={
                "spore_name": "database_query_optimizer",
                "spore_description": "Systematic approach to database query optimization",
                "spore_content": {
                    "methodology": "EXPLAIN ANALYZE -> Index Analysis -> Query Rewrite",
                    "tools": ["pg_stat_statements", "EXPLAIN", "pgbench"],
                    "success_metrics": [
                        "query_time_reduction",
                        "cpu_usage",
                        "memory_usage",
                    ],
                    "adaptation_notes": "For analytics queries, also consider partitioning and materialized views",
                },
            },
            timestamp=now - timedelta(minutes=15),
            priority=4,
        ),
        BeastModeMessage(
            id="demo-msg-010",
            type=MessageType.SYSTEM_HEALTH,
            source="monitoring-agent",
            target=None,  # Broadcast
            payload={
                "status": "healthy",
                "cpu_usage": 19.2,
                "memory_usage": 71.8,
                "active_agents": 13,
                "message_throughput": 167.3,
                "optimization_impact": "Overall system performance improved by 15%",
            },
            timestamp=now - timedelta(minutes=5),
            priority=7,
        ),
    ]

    return messages


def create_log_files(log_directory: Path, messages: list):
    """Create sample log files with the messages"""
    # Split messages across multiple log files to simulate real usage
    log_file_1 = log_directory / "mailbox_20240101_120000.log"
    log_file_2 = log_directory / "mailbox_20240101_140000.log"
    log_file_3 = log_directory / "mailbox_20240101_160000.log"

    # First log file (older messages)
    with open(log_file_1, "w", encoding="utf-8") as f:
        for message in messages[:3]:
            log_entry = {
                "timestamp": message.timestamp.isoformat(),
                "channel": "beast_mode_network",
                "raw_data": message.model_dump_json(),
                "parsed_message": message.model_dump(),
                "parsing_error": None,
            }
            f.write(json.dumps(log_entry, default=str) + "\n")

    # Second log file (middle messages)
    with open(log_file_2, "w", encoding="utf-8") as f:
        for message in messages[3:7]:
            log_entry = {
                "timestamp": message.timestamp.isoformat(),
                "channel": "beast_mode_network",
                "raw_data": message.model_dump_json(),
                "parsed_message": message.model_dump(),
                "parsing_error": None,
            }
            f.write(json.dumps(log_entry, default=str) + "\n")

    # Third log file (recent messages)
    with open(log_file_3, "w", encoding="utf-8") as f:
        for message in messages[7:]:
            log_entry = {
                "timestamp": message.timestamp.isoformat(),
                "channel": "beast_mode_network",
                "raw_data": message.model_dump_json(),
                "parsed_message": message.model_dump(),
                "parsing_error": None,
            }
            f.write(json.dumps(log_entry, default=str) + "\n")

    logger.info(f"Created 3 log files with {len(messages)} total messages")


async def demonstrate_basic_scanning(history_manager: MessageHistoryManager):
    """Demonstrate basic message scanning functionality"""
    print("\n" + "=" * 60)
    print("BASIC MESSAGE SCANNING")
    print("=" * 60)

    # Scan all messages
    all_messages = await history_manager.scan_messages()
    print(f"\n📨 Total messages found: {len(all_messages)}")

    # Show first few messages
    print("\n🔍 Recent messages (newest first):")
    for i, msg_entry in enumerate(all_messages[:3]):
        msg = msg_entry.message
        print(
            f"  {i+1}. [{msg.type.value}] {msg.source} -> {msg.target or 'BROADCAST'}"
        )
        print(f"     Time: {msg_entry.log_timestamp.strftime('%H:%M:%S')}")
        print(f"     Content: {str(msg.payload)[:80]}...")
        print()


async def demonstrate_filtering(history_manager: MessageHistoryManager):
    """Demonstrate message filtering capabilities"""
    print("\n" + "=" * 60)
    print("MESSAGE FILTERING")
    print("=" * 60)

    # Filter by message type
    help_messages = await history_manager.scan_messages(
        MessageFilter(
            message_types=[MessageType.HELP_WANTED, MessageType.HELP_RESPONSE]
        )
    )
    print(f"\n🆘 Help-related messages: {len(help_messages)}")
    for msg_entry in help_messages:
        msg = msg_entry.message
        print(f"  • [{msg.type.value}] {msg.source} -> {msg.target}")

    # Filter by agent
    alice_messages = await history_manager.scan_messages(
        MessageFilter(target_agents=["alice-agent"])
    )
    print(f"\n👩‍💻 Messages for Alice: {len(alice_messages)}")
    for msg_entry in alice_messages:
        msg = msg_entry.message
        print(f"  • [{msg.type.value}] {msg.source}: {str(msg.payload)[:50]}...")

    # Filter by priority
    high_priority = await history_manager.scan_messages(
        MessageFilter(priority_min=1, priority_max=4)
    )
    print(f"\n🔥 High priority messages (1-4): {len(high_priority)}")
    for msg_entry in high_priority:
        msg = msg_entry.message
        print(
            f"  • Priority {msg.priority}: [{msg.type.value}] {msg.source} -> {msg.target}"
        )

    # Filter by time range
    recent_messages = await history_manager.scan_messages(
        MessageFilter(since=datetime.now() - timedelta(hours=2))
    )
    print(f"\n⏰ Messages from last 2 hours: {len(recent_messages)}")


async def demonstrate_search(history_manager: MessageHistoryManager):
    """Demonstrate message search functionality"""
    print("\n" + "=" * 60)
    print("MESSAGE SEARCH")
    print("=" * 60)

    # Search for optimization-related messages
    optimization_results = await history_manager.search_messages("optimization")
    print(f"\n🔍 Search 'optimization': {len(optimization_results)} results")
    for msg_entry in optimization_results:
        msg = msg_entry.message
        print(f"  • [{msg.type.value}] {msg.source}: {str(msg.payload)[:60]}...")

    # Search for database-related messages
    database_results = await history_manager.search_messages("database")
    print(f"\n🔍 Search 'database': {len(database_results)} results")
    for msg_entry in database_results:
        msg = msg_entry.message
        print(f"  • [{msg.type.value}] {msg.source} -> {msg.target}")

    # Search with agent filter
    alice_help_results = await history_manager.search_messages(
        "help", agent_id="alice-agent"
    )
    print(f"\n🔍 Search 'help' for Alice: {len(alice_help_results)} results")


async def demonstrate_check_mail(history_manager: MessageHistoryManager):
    """Demonstrate check mail functionality"""
    print("\n" + "=" * 60)
    print("CHECK MAIL FUNCTIONALITY")
    print("=" * 60)

    # Check mail for Bob (without marking as read)
    bob_mail = await history_manager.check_mail("bob-agent", mark_as_read=False)
    print(f"\n📬 Bob's mailbox: {len(bob_mail)} messages")

    unread_count = sum(1 for msg in bob_mail if msg.status == MessageStatus.UNREAD)
    print(f"   📩 Unread: {unread_count}")

    # Show Bob's messages
    print("\n📨 Bob's messages:")
    for i, msg_entry in enumerate(bob_mail):
        msg = msg_entry.message
        status_icon = "📩" if msg_entry.status == MessageStatus.UNREAD else "📖"
        print(f"  {i+1}. {status_icon} [{msg.type.value}] from {msg.source}")
        print(f"     {str(msg.payload)[:70]}...")
        print()

    # Check mail for Alice and mark as read
    print("📖 Checking Alice's mail and marking as read...")
    alice_mail = await history_manager.check_mail("alice-agent", mark_as_read=True)
    print(f"   Alice has {len(alice_mail)} messages (now marked as read)")


async def demonstrate_conversation_threading(history_manager: MessageHistoryManager):
    """Demonstrate conversation threading"""
    print("\n" + "=" * 60)
    print("CONVERSATION THREADING")
    print("=" * 60)

    # Get the optimization conversation thread
    thread = await history_manager.get_conversation_thread("optimization-conv-001")
    print(f"\n💬 Optimization conversation thread: {len(thread)} messages")

    print("\n📝 Conversation flow (chronological order):")
    for i, msg_entry in enumerate(thread):
        msg = msg_entry.message
        time_str = msg_entry.log_timestamp.strftime("%H:%M")
        print(f"  {i+1}. [{time_str}] {msg.source} -> {msg.target}")
        print(f"     Type: {msg.type.value}")

        # Show relevant payload content
        if msg.type == MessageType.HELP_WANTED:
            print(f"     Help: {msg.payload.get('description', '')}")
        elif msg.type == MessageType.HELP_RESPONSE:
            print(f"     Response: {msg.payload.get('response', '')}")
        elif msg.type == MessageType.SPORE_DELIVERY:
            print(f"     Spore: {msg.payload.get('spore_name', '')}")
        elif msg.type == MessageType.TECHNICAL_EXCHANGE:
            print(f"     Topic: {msg.payload.get('topic', '')}")

        print()


async def demonstrate_status_management(history_manager: MessageHistoryManager):
    """Demonstrate message status management"""
    print("\n" + "=" * 60)
    print("MESSAGE STATUS MANAGEMENT")
    print("=" * 60)

    # Mark some messages with different statuses
    await history_manager.mark_message_read("demo-msg-001")
    await history_manager.archive_message("demo-msg-005")  # System health message
    await history_manager.flag_message("demo-msg-002")  # Important help request

    # Add tags to messages
    await history_manager.add_message_tag("demo-msg-002", "urgent")
    await history_manager.add_message_tag("demo-msg-002", "database")
    await history_manager.add_message_tag("demo-msg-004", "spore")
    await history_manager.add_message_tag("demo-msg-004", "optimization")

    # Add notes to messages
    await history_manager.add_message_note(
        "demo-msg-002",
        "High-impact optimization request - resulted in 82% performance improvement",
    )
    await history_manager.add_message_note(
        "demo-msg-004",
        "Valuable spore for database optimization - should be shared with other teams",
    )

    print("✅ Applied various statuses, tags, and notes to messages")

    # Get message counts by status
    counts = await history_manager.get_message_counts()
    print(f"\n📊 Message status summary:")
    print(f"   Total: {counts['total']}")
    print(f"   Unread: {counts[MessageStatus.UNREAD.value]}")
    print(f"   Read: {counts[MessageStatus.READ.value]}")
    print(f"   Archived: {counts[MessageStatus.ARCHIVED.value]}")
    print(f"   Flagged: {counts[MessageStatus.FLAGGED.value]}")

    # Show flagged messages
    flagged_messages = await history_manager.scan_messages(
        MessageFilter(status=[MessageStatus.FLAGGED])
    )
    print(f"\n🚩 Flagged messages: {len(flagged_messages)}")
    for msg_entry in flagged_messages:
        msg = msg_entry.message
        print(f"  • [{msg.type.value}] {msg.source} -> {msg.target}")
        print(f"    Tags: {', '.join(msg_entry.tags)}")
        if msg_entry.notes:
            print(f"    Note: {msg_entry.notes}")
        print()


async def demonstrate_advanced_filtering(history_manager: MessageHistoryManager):
    """Demonstrate advanced filtering capabilities"""
    print("\n" + "=" * 60)
    print("ADVANCED FILTERING")
    print("=" * 60)

    # Complex filter combining multiple criteria
    complex_filter = MessageFilter(
        message_types=[MessageType.SPORE_DELIVERY, MessageType.SPORE_REQUEST],
        priority_min=1,
        priority_max=5,
        search_text="optimization",
        limit=5,
    )

    spore_messages = await history_manager.scan_messages(complex_filter)
    print(f"\n🧬 High-priority optimization spores: {len(spore_messages)}")
    for msg_entry in spore_messages:
        msg = msg_entry.message
        print(
            f"  • [{msg.type.value}] Priority {msg.priority}: {msg.source} -> {msg.target}"
        )
        if msg.type == MessageType.SPORE_DELIVERY:
            spore_name = msg.payload.get("spore_name", "Unknown")
            print(f"    Spore: {spore_name}")
        print()

    # Filter by correlation ID (conversation)
    conversation_filter = MessageFilter(
        correlation_ids=["optimization-conv-001"],
        status=[MessageStatus.UNREAD, MessageStatus.READ, MessageStatus.FLAGGED],
    )

    conversation_messages = await history_manager.scan_messages(conversation_filter)
    print(f"\n💬 Optimization conversation messages: {len(conversation_messages)}")

    # Filter by time range and agent
    recent_alice_filter = MessageFilter(
        since=datetime.now() - timedelta(hours=2),
        source_agents=["alice-agent"],
        limit=3,
    )

    recent_alice = await history_manager.scan_messages(recent_alice_filter)
    print(f"\n👩‍💻 Alice's recent activity (last 2 hours): {len(recent_alice)}")


async def demonstrate_statistics(history_manager: MessageHistoryManager):
    """Demonstrate statistics and health monitoring"""
    print("\n" + "=" * 60)
    print("STATISTICS & HEALTH")
    print("=" * 60)

    # Get manager statistics
    stats = history_manager.get_stats()
    print(f"\n📈 Message History Manager Statistics:")
    print(f"   Messages scanned: {stats['messages_scanned']}")
    print(f"   Searches performed: {stats['searches_performed']}")
    print(f"   Status updates: {stats['status_updates']}")
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   Cache misses: {stats['cache_misses']}")
    print(f"   Message status count: {stats['message_status_count']}")
    print(f"   Is running: {stats['is_running']}")

    if stats["last_scan_time"]:
        print(f"   Last scan: {stats['last_scan_time'].strftime('%H:%M:%S')}")

    # Get health status
    health = history_manager.get_health_status()
    print(f"\n🏥 Health Status: {health['status']}")
    print(f"   Log directory: {health['log_directory']}")
    print(f"   Status file: {health['status_file']}")


async def main():
    """Main demonstration function"""
    print("🚀 Beast Mode Message History Demo")
    print("=" * 60)

    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        log_directory = Path(temp_dir)

        # Create sample messages and log files
        messages = create_sample_messages()
        create_log_files(log_directory, messages)

        # Create and start message history manager
        history_manager = MessageHistoryManager(
            log_directory=str(log_directory),
            auto_save_interval=5,  # Fast auto-save for demo
        )

        await history_manager.start()

        try:
            # Run all demonstrations
            await demonstrate_basic_scanning(history_manager)
            await demonstrate_filtering(history_manager)
            await demonstrate_search(history_manager)
            await demonstrate_check_mail(history_manager)
            await demonstrate_conversation_threading(history_manager)
            await demonstrate_status_management(history_manager)
            await demonstrate_advanced_filtering(history_manager)
            await demonstrate_statistics(history_manager)

            print("\n" + "=" * 60)
            print("✅ DEMO COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print("\nThe Beast Mode Message History system provides:")
            print("• 📨 Comprehensive message scanning and retrieval")
            print("• 🔍 Powerful search and filtering capabilities")
            print("• 📬 Agent-specific mailbox functionality")
            print("• 💬 Conversation threading by correlation ID")
            print("• 🏷️  Message status tracking (read/unread/archived/flagged)")
            print("• 🏷️  Tagging and note-taking for messages")
            print("• 📊 Statistics and health monitoring")
            print("• 💾 Persistent status across restarts")
            print("• ⚡ High-performance scanning of large message volumes")
            print("\nThis enables systematic collaboration and knowledge")
            print("management across the Beast Mode agent network!")

        finally:
            await history_manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
