#!/usr/bin/env python3
"""
Ghostbusters Check Script - Uses Secure Shell Service
NO MORE DIRECT SHELL COMMANDS! 🛡️
"""

import asyncio
import sys
from pathlib import Path

from src.ghostbusters.ghostbusters_orchestrator import run_ghostbusters
from src.secure_shell_service.elegant_client import secure_execute

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def run_ghostbusters_check():
    """Run Ghostbusters check using secure shell service"""
    print("🔍 Running Ghostbusters check...")

    try:
        # Run Ghostbusters directly (no shell command needed!)
        result = await run_ghostbusters(".")

        print("🔍 Ghostbusters Status:")
        print(f"   Confidence: {result.confidence_score}")
        print(f"   Delusions: {len(result.delusions_detected)}")
        print(f"   Phase: {result.current_phase}")

        # If we need to run any shell commands, use secure shell service
        if result.delusions_detected:
            print(f"\n🔧 Found {len(result.delusions_detected)} delusions!")

            # Example: Use secure shell for any cleanup if needed
            cleanup_result = await secure_execute("echo 'Ghostbusters check completed'")
            print(f"✅ Secure cleanup: {cleanup_result['success']}")

        return result

    except Exception as e:
        print(f"❌ Ghostbusters check failed: {e}")
        return None


async def main():
    """Main function"""
    print("🛡️ Ghostbusters Check - Using Secure Shell Service")
    print("=" * 50)

    result = await run_ghostbusters_check()

    if result:
        print("\n🎉 Ghostbusters check completed successfully!")
        print(f"   Final confidence: {result.confidence_score}")
    else:
        print("\n❌ Ghostbusters check failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
