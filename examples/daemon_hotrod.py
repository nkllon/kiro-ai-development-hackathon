#!/usr/bin/env python3
"""
HotRod Daemon Agent

Uses the daemon approach - runs in background, check mail when convenient.
Much more practical for real work since it doesn't block.
"""

import time
import logging
from src.beast_mode.messaging.daemon_client import BeastModeClient
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


def handle_help_request(message: BeastModeMessage):
    """Handle help requests from other agents."""
    print(
        f"📨 Help request from {message.source}: {message.payload.get('description', 'No description')}"
    )


def handle_spore_delivery(message: BeastModeMessage):
    """Handle spore deliveries."""
    spore_name = message.payload.get("spore_data", {}).get("pattern_name", "Unknown")
    print(f"🧬 Received spore: {spore_name} from {message.source}")


def main():
    """Run HotRod with daemon backend."""
    logging.basicConfig(level=logging.INFO)

    # Create client with daemon backend
    client = BeastModeClient("HotRod")

    # Register message handlers
    client.register_handler(MessageType.HELP_WANTED, handle_help_request)
    client.register_handler(MessageType.SPORE_DELIVERY, handle_spore_delivery)

    # Start daemon
    print("🚀 Starting HotRod daemon...")
    if not client.start():
        print("❌ Failed to start daemon")
        return

    print("✅ HotRod daemon running in background")

    # Share systematic development ecosystem spore
    spore_data = {
        "pattern_name": "Requirements_ARE_Implementation",
        "description": "Mathematical bridge from requirements to implementation",
        "implementation_approach": "daemon_based_messaging",
        "advantages": [
            "Non-blocking operation",
            "Background message handling",
            "Queue-based architecture",
            "Check mail when convenient",
        ],
        "comparison_with_tidb": {
            "tidb_focus": "Database optimization and performance",
            "hotrod_focus": "SPEC development and systematic methodology",
            "collaboration_model": "Complementary specializations",
        },
    }

    client.send_spore(spore_data)
    print("🧬 Systematic development spore shared")

    # Simulate doing other work while daemon handles network
    print("\n📋 HotRod working on other tasks...")
    print("💬 Daemon handling network in background...")
    print("📬 Checking mail periodically...\n")

    try:
        work_cycles = 0
        while True:
            # Simulate doing other work
            print(f"⚙️  Working on systematic development (cycle {work_cycles + 1})...")
            time.sleep(3)

            # Check mail periodically (non-blocking)
            messages = client.check_messages()
            if messages:
                print(f"\n📬 You have {len(messages)} new messages!")
                client.process_messages()
                print()

            work_cycles += 1

            # Show status every 5 cycles
            if work_cycles % 5 == 0:
                status = client.get_status()
                print(
                    f"📊 Status: Connected={status['is_connected']}, "
                    f"Sent={status['stats']['messages_sent']}, "
                    f"Received={status['stats']['messages_received']}"
                )

    except KeyboardInterrupt:
        print("\n🛑 Stopping HotRod daemon...")
        client.stop()
        print("👋 HotRod offline")


if __name__ == "__main__":
    main()
