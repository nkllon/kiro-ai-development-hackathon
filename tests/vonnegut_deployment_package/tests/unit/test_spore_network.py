#!/usr/bin/env python3
"""
Test Beast Mode Spore Network
Demonstrates spore distribution and reception
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode_spore_distributor import SporeDistributor
from beast_mode_spore_receiver import SporeReceiver


async def test_spore_network():
    """Test the complete spore distribution network"""
    print("🧬 Testing Beast Mode Spore Network")
    print("=" * 50)

    # Create distributor and receiver
    distributor = SporeDistributor()
    receiver = SporeReceiver()

    try:
        # Connect both
        await distributor.connect()
        await receiver.connect()

        # Load spores
        await distributor.load_spore_catalog()

        print(f"\n📡 Broadcasting spore catalog...")
        await distributor.broadcast_spore_catalog()

        # Give receiver time to process catalog
        await asyncio.sleep(2)

        print(f"\n📤 Broadcasting a sample spore...")
        if "gke-hackathon-spore" in distributor.spore_catalog:
            await distributor.broadcast_spore("gke-hackathon-spore")

        # Give receiver time to process spore
        await asyncio.sleep(2)

        print(f"\n📊 Test Results:")
        print(f"   Distributor loaded: {len(distributor.spore_catalog)} spores")
        print(f"   Receiver catalog: {len(receiver.available_catalog)} spores")
        print(f"   Receiver received: {len(receiver.received_spores)} spores")

        if receiver.received_spores:
            print(f"\n✅ Spore network test successful!")
            for spore_name, info in receiver.received_spores.items():
                print(f"   🧬 Received: {spore_name} ({info['size']:,} bytes)")
        else:
            print(f"\n⚠️  No spores received - check network timing")

    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await distributor.disconnect()
        await receiver.disconnect()


if __name__ == "__main__":
    asyncio.run(test_spore_network())
