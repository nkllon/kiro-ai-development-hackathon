#!/usr/bin/env python3
"""
Proper Ghostbusters Caller
Calls Ghostbusters using Python instead of bash commands
"""

import asyncio
from pathlib import Path


async def call_ghostbusters() -> None:
    """Call Ghostbusters properly with Python"""
    print("🔍 Calling Ghostbusters...")

    try:
        # Import Ghostbusters components
        from src.ghostbusters.ghostbusters_orchestrator import GhostbustersOrchestrator

        print("✅ Ghostbusters components imported successfully")

        # Create orchestrator
        orchestrator = GhostbustersOrchestrator(".")

        # Run Ghostbusters
        print("🚀 Running Ghostbusters analysis...")
        state = await orchestrator.run_ghostbusters()

        print("📊 Ghostbusters Results:")
        print(f"   Confidence Score: {state.confidence_score}")
        print(f"   State Type: {type(state)}")

        # Print state attributes
        print(f"   State Attributes: {dir(state)}")

        print("\n✅ Ghostbusters analysis complete!")

        print("\n✅ Ghostbusters analysis complete!")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Ghostbusters components not available")
        return

    except Exception as e:
        print(f"💥 Ghostbusters Error: {e}")
        print("   Ghostbusters is fucked up too!")
        return


def main() -> None:
    """Main function"""
    print("🎯 Proper Ghostbusters Caller")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("src/ghostbusters").exists():
        print("❌ ERROR: Ghostbusters not found!")
        print("   Expected: src/ghostbusters/")
        return

    # Run Ghostbusters
    asyncio.run(call_ghostbusters())


if __name__ == "__main__":
    main()
