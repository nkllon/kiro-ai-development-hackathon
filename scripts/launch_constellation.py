#!/usr/bin/env python3
"""
Constellation Execution Launcher
Simple launcher for constellation elaboration with built-in readiness checks
"""

import os
import sys
import asyncio
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def print_banner():
    """Print launch banner"""
    print("🌟" * 40)
    print("🚀 CONSTELLATION ELABORATION LAUNCHER")
    print("🌟" * 40)
    print(f"🕐 Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def print_launch_options():
    """Print available launch options"""
    print("🎯 LAUNCH OPTIONS:")
    print("  1. Quick Test (2 agents)     - Fast validation run")
    print("  2. Conservative (5 agents)   - Safe, steady execution")
    print("  3. Balanced (10 agents)      - Recommended for most cases")
    print("  4. Aggressive (20 agents)    - Maximum speed (requires resources)")
    print("  5. Custom (specify agents)   - Custom agent count")
    print("  6. Resume Previous           - Resume interrupted execution")
    print("  7. Monitor Only              - Just monitor existing execution")
    print("  8. Full Readiness Check      - Comprehensive pre-flight validation")
    print()


async def run_readiness_check(max_agents: int = 10) -> bool:
    """Run readiness check"""
    print("🔍 Running readiness check...")
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "scripts/constellation_execution_readiness.py",
            "--max-agents", str(max_agents),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print("✅ Readiness check passed!")
            return True
        else:
            print("❌ Readiness check failed!")
            print("Error output:")
            print(stderr.decode())
            return False
    
    except Exception as e:
        print(f"❌ Readiness check error: {e}")
        return False


async def launch_execution(max_agents: int, resume: bool = False):
    """Launch constellation execution"""
    print(f"🚀 Launching constellation execution with {max_agents} agents...")
    
    # Start monitoring in background
    print("📊 Starting monitoring system...")
    monitor_process = await asyncio.create_subprocess_exec(
        sys.executable, "scripts/constellation_monitor.py",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    
    # Give monitor time to start
    await asyncio.sleep(2)
    
    # Launch orchestrator
    orchestrator_args = [sys.executable, "scripts/constellation_orchestrator.py", str(max_agents)]
    if resume:
        orchestrator_args.append("--resume")
    
    print("🎭 Starting constellation orchestrator...")
    print(f"   Command: {' '.join(orchestrator_args)}")
    print()
    print("📊 Monitor the execution with:")
    print("   python scripts/constellation_monitor.py")
    print()
    print("🛑 Stop execution with Ctrl+C")
    print("=" * 60)
    
    try:
        orchestrator_process = await asyncio.create_subprocess_exec(
            *orchestrator_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        # Stream output in real-time
        while True:
            line = await orchestrator_process.stdout.readline()
            if not line:
                break
            print(line.decode().rstrip())
        
        await orchestrator_process.wait()
        
        if orchestrator_process.returncode == 0:
            print("\n🎉 Constellation execution completed successfully!")
        else:
            print(f"\n❌ Constellation execution failed (exit code: {orchestrator_process.returncode})")
    
    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user")
        orchestrator_process.terminate()
        await orchestrator_process.wait()
    
    finally:
        # Clean up monitor process
        if monitor_process.returncode is None:
            monitor_process.terminate()
            await monitor_process.wait()


async def monitor_execution():
    """Monitor existing execution"""
    print("📊 Starting execution monitor...")
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "scripts/constellation_monitor.py"
        )
        
        await process.wait()
    
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")


async def interactive_launcher():
    """Interactive launcher with menu"""
    print_banner()
    print_launch_options()
    
    while True:
        try:
            choice = input("🎯 Select option (1-8): ").strip()
            
            if choice == "1":
                # Quick test
                if await run_readiness_check(2):
                    await launch_execution(2)
                break
            
            elif choice == "2":
                # Conservative
                if await run_readiness_check(5):
                    await launch_execution(5)
                break
            
            elif choice == "3":
                # Balanced
                if await run_readiness_check(10):
                    await launch_execution(10)
                break
            
            elif choice == "4":
                # Aggressive
                if await run_readiness_check(20):
                    await launch_execution(20)
                break
            
            elif choice == "5":
                # Custom
                try:
                    agents = int(input("🤖 Enter number of agents (1-50): "))
                    if 1 <= agents <= 50:
                        if await run_readiness_check(agents):
                            await launch_execution(agents)
                        break
                    else:
                        print("❌ Invalid agent count. Please enter 1-50.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
            
            elif choice == "6":
                # Resume
                agents = int(input("🤖 Enter number of agents for resume (default 10): ") or "10")
                await launch_execution(agents, resume=True)
                break
            
            elif choice == "7":
                # Monitor only
                await monitor_execution()
                break
            
            elif choice == "8":
                # Full readiness check
                agents = int(input("🤖 Enter target agent count (default 10): ") or "10")
                await run_readiness_check(agents)
                break
            
            else:
                print("❌ Invalid choice. Please select 1-8.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


async def main():
    parser = argparse.ArgumentParser(description="Constellation Execution Launcher")
    parser.add_argument("--agents", type=int, help="Number of agents to use")
    parser.add_argument("--resume", action="store_true", help="Resume previous execution")
    parser.add_argument("--monitor", action="store_true", help="Monitor existing execution")
    parser.add_argument("--check", action="store_true", help="Run readiness check only")
    parser.add_argument("--quick", action="store_true", help="Quick test with 2 agents")
    
    args = parser.parse_args()
    
    # Handle command line arguments
    if args.check:
        agents = args.agents or 10
        await run_readiness_check(agents)
    elif args.monitor:
        await monitor_execution()
    elif args.quick:
        if await run_readiness_check(2):
            await launch_execution(2)
    elif args.agents:
        if await run_readiness_check(args.agents):
            await launch_execution(args.agents, resume=args.resume)
    else:
        # Interactive mode
        await interactive_launcher()


if __name__ == "__main__":
    asyncio.run(main())