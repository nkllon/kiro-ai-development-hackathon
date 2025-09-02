#!/usr/bin/env python3
"""
Detailed Ghostbusters Analysis Script
Called from Makefile for multi-agent delusion detection
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from ghostbusters import run_ghostbusters
except ImportError:
    # Fallback for when running from different directory
    sys.path.insert(0, "src")
    from ghostbusters import run_ghostbusters


async def main():
    """Run detailed Ghostbusters analysis"""
    print("🔒 SECURITY EXPERT FINDINGS:")
    result = await run_ghostbusters(".")

    security_delusions = [d for d in result.get("delusions_detected", []) if d.get("agent") == "SecurityExpert"]
    for d in security_delusions:
        print(f"  - {d.get('type', 'Unknown')}: {d.get('description', 'No description')}")

    print("\n🏗️ ARCHITECTURE EXPERT FINDINGS:")
    arch_delusions = [d for d in result.get("delusions_detected", []) if d.get("agent") == "ArchitectureExpert"]
    for d in arch_delusions:
        print(f"  - {d.get('type', 'Unknown')}: {d.get('description', 'No description')}")

    print("\n🔧 CODE QUALITY EXPERT FINDINGS:")
    quality_delusions = [d for d in result.get("delusions_detected", []) if d.get("agent") == "CodeQualityExpert"]
    for d in quality_delusions:
        print(f"  - {d.get('type', 'Unknown')}: {d.get('description', 'No description')}")

    print("\n🧪 TEST EXPERT FINDINGS:")
    test_delusions = [d for d in result.get("delusions_detected", []) if d.get("agent") == "TestExpert"]
    for d in test_delusions:
        print(f"  - {d.get('type', 'Unknown')}: {d.get('description', 'No description')}")

    print("\n📊 OVERALL ASSESSMENT:")
    print(f"  Confidence Score: {result.get('confidence_score', 'Unknown')}")
    print(f"  Delusions Detected: {len(result.get('delusions_detected', []))}")
    print(f"  Errors: {len(result.get('errors', []))}")


if __name__ == "__main__":
    asyncio.run(main())
