#!/usr/bin/env python3
"""
Call Ghostbusters about encoding issues and code smell
"""

import asyncio
from pathlib import Path


async def call_ghostbusters_about_encoding() -> None:
    """Call Ghostbusters about the encoding issue"""
    print("🔍 Calling Ghostbusters about encoding issues...")

    try:
        from src.ghostbusters.ghostbusters_orchestrator import GhostbustersOrchestrator

        # Create orchestrator
        orchestrator = GhostbustersOrchestrator(".")

        # Run Ghostbusters
        print("🚀 Running Ghostbusters analysis...")
        state = await orchestrator.run_ghostbusters()

        print("📊 Ghostbusters Results:")
        print(f"   Confidence Score: {state.confidence_score}")
        print(f"   Current Phase: {state.current_phase}")
        print(f"   Errors: {len(state.errors)}")
        print(f"   Warnings: {len(state.warnings)}")

        if state.errors:
            print("\n❌ Errors:")
            for error in state.errors:
                print(f"   - {error}")

        if state.warnings:
            print("\n⚠️ Warnings:")
            for warning in state.warnings:
                print(f"   - {warning}")

        print("\n✅ Ghostbusters analysis complete!")

    except Exception as e:
        print(f"💥 Ghostbusters Error: {e}")
        print("   Ghostbusters might be fucked up too!")


def main() -> None:
    """Main function"""
    print("🎯 Ghostbusters Encoding Issue Analysis")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("src/ghostbusters").exists():
        print("❌ ERROR: Ghostbusters not found!")
        return

    # Run Ghostbusters
    asyncio.run(call_ghostbusters_about_encoding())


if __name__ == "__main__":
    main()
