#!/usr/bin/env python3
"""
Whiskey Mode Demo

Test the beautiful terminal dashboard with mock data.
Run this to see the satisfying animations in action!

Usage:
    python scripts/whiskey_mode_demo.py
"""

import asyncio
import random
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.monitoring import WhiskeyModeDisplay


async def simulate_test_data(display: WhiskeyModeDisplay):
    """Simulate incoming test data and system events"""
    
    # Initial test results
    await asyncio.sleep(2)
    display.update_test_results({
        'total': 88,
        'passed': 84,
        'failed': 2,
        'skipped': 2,
        'duration': 12.3
    })
    
    # System health updates
    for i in range(20):
        await asyncio.sleep(3)
        
        # Simulate varying system health
        cpu = random.uniform(30, 80)
        memory = random.uniform(50, 85)
        test_velocity = random.uniform(10, 25)
        
        display.update_system_health({
            'cpu': cpu,
            'memory': memory,
            'test_velocity': test_velocity
        })
        
        # Occasionally simulate test updates
        if i % 4 == 0:
            # Simulate new test run
            total = random.randint(80, 100)
            passed = random.randint(int(total * 0.8), total)
            failed = total - passed
            
            display.update_test_results({
                'total': total,
                'passed': passed,
                'failed': failed,
                'skipped': random.randint(0, 3),
                'duration': random.uniform(8.0, 20.0)
            })
        
        # Occasionally simulate hubris alerts
        if i % 7 == 0:
            hubris_messages = [
                "Emergency bypass attempt detected",
                "Accountability chain verification failed",
                "Systematic governance override rejected",
                "Reality check intervention required"
            ]
            display.show_hubris_alert(random.choice(hubris_messages))
        
        # Occasionally simulate mama discoveries
        if i % 10 == 0:
            mama_messages = [
                "Board oversight discovered for Actor-7742",
                "Regulatory compliance chain activated",
                "Physics reality check initiated"
            ]
            display.display_mama_discovery(random.choice(mama_messages))


async def main():
    """Run the Whiskey Mode demo"""
    print("🥃 Starting Whiskey Mode Demo...")
    print("Press Ctrl+C to exit")
    print()
    
    display = WhiskeyModeDisplay()
    
    # Start the display and simulation concurrently
    try:
        await asyncio.gather(
            display.start_display(),
            simulate_test_data(display)
        )
    except KeyboardInterrupt:
        print("\n🥃 Whiskey Mode demo ended. Cheers!")


if __name__ == "__main__":
    asyncio.run(main())