#!/usr/bin/env python3
"""
Enhanced Hackathon Demo Script

Demonstrates Beast Mode + Simone integration for maximum competitive impact.
Showcases systematic superiority combined with AI-assisted development.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from beast_mode.integration.enhanced_demo import run_enhanced_demo


def main():
    """Run the enhanced hackathon demo."""
    print("🚀 BEAST MODE + SIMONE INTEGRATION DEMO")
    print("=" * 60)
    print("Demonstrating systematic superiority with AI-assisted development")
    print("=" * 60)

    try:
        # Run the enhanced demo
        results = run_enhanced_demo()

        if results["status"] == "success":
            print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
            print("✅ All phases completed successfully")
            print("✅ Systematic superiority demonstrated")
            print("✅ AI-assisted development showcased")
            print("✅ Velocity advantage proven")
            print("✅ Competitive advantage established")

            return 0
        else:
            print(f"\n❌ DEMO FAILED: {results.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"\n❌ DEMO ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
