#!/usr/bin/env python3
"""
Simple Constellation Launcher
Bypasses complex validation and focuses on core execution
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
    print("🚀 SIMPLE CONSTELLATION LAUNCHER")
    print("🌟" * 40)
    print(f"🕐 Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def check_basic_requirements() -> bool:
    """Check basic requirements"""
    print("🔍 Checking basic requirements...")
    
    issues = []
    
    # Check staging prompts
    staging_dir = Path("prompts/staging")
    if not staging_dir.exists():
        issues.append("Staging prompts directory not found")
    else:
        prompt_count = len(list(staging_dir.glob("*.md")))
        print(f"  ✅ Found {prompt_count} staging prompts")
    
    # Check Claude CLI
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✅ Claude CLI available: {result.stdout.strip()}")
        else:
            issues.append("Claude CLI not working properly")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        issues.append("Claude CLI not found or not responding")
    
    # Check directories
    required_dirs = [".kiro", "logs", "reports"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Directory ready: {dir_name}")
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ Basic requirements satisfied")
        return True


async def run_dag_validation() -> bool:
    """Run DAG validation"""
    print("🔍 Running DAG validation...")
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "scripts/constellation_dag_validator.py", "--comprehensive",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print("  ✅ DAG validation passed")
            return True
        else:
            print("  ❌ DAG validation failed")
            print(f"     Error: {stderr.decode()[:200]}...")
            return False
    
    except Exception as e:
        print(f"  ❌ DAG validation error: {e}")
        return False


async def launch_constellation(max_agents: int, test_mode: bool = False):
    """Launch constellation execution"""
    print(f"🚀 Launching constellation execution...")
    print(f"   Agents: {max_agents}")
    print(f"   Test mode: {test_mode}")
    print()
    
    # Prepare orchestrator command
    orchestrator_args = [sys.executable, "scripts/constellation_orchestrator.py", str(max_agents)]
    if test_mode:
        print("🧪 Running in test mode (limited execution)")
    
    print("📊 You can monitor execution with:")
    print("   python scripts/constellation_monitor.py")
    print()
    print("🛑 Stop execution with Ctrl+C")
    print("=" * 60)
    
    try:
        # Launch orchestrator
        process = await asyncio.create_subprocess_exec(
            *orchestrator_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        # Stream output
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            print(line.decode().rstrip())
        
        await process.wait()
        
        if process.returncode == 0:
            print("\n🎉 Constellation execution completed successfully!")
            
            # Offer to generate report
            try:
                generate_report = input("\n📊 Generate execution report? (y/N): ").strip().lower()
                if generate_report in ['y', 'yes']:
                    print("📊 Generating execution report...")
                    report_process = await asyncio.create_subprocess_exec(
                        sys.executable, "scripts/constellation_execution_report.py",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT
                    )
                    
                    report_stdout, _ = await report_process.communicate()
                    print(report_stdout.decode())
            except (KeyboardInterrupt, EOFError):
                pass
        else:
            print(f"\n❌ Constellation execution failed (exit code: {process.returncode})")
    
    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user")
        if process.returncode is None:
            process.terminate()
            await process.wait()


async def main():
    parser = argparse.ArgumentParser(description="Simple Constellation Launcher")
    parser.add_argument("agents", type=int, nargs='?', default=10,
                       help="Number of agents to use (default: 10)")
    parser.add_argument("--test", action="store_true",
                       help="Run in test mode")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip validation checks")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Basic requirements check
    if not args.skip_validation:
        if not check_basic_requirements():
            print("\n❌ Basic requirements not met. Use --skip-validation to bypass.")
            return
        
        # DAG validation
        if not await run_dag_validation():
            print("\n❌ DAG validation failed. Use --skip-validation to bypass.")
            return
        
        print("\n✅ All validations passed!")
    else:
        print("⚠️  Skipping validation checks")
    
    print(f"\n🚀 Ready to launch with {args.agents} agents")
    
    # Confirm launch
    try:
        if not args.test:
            confirm = input("Continue with launch? (Y/n): ").strip().lower()
            if confirm in ['n', 'no']:
                print("👋 Launch cancelled")
                return
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Launch cancelled")
        return
    
    # Launch
    await launch_constellation(args.agents, test_mode=args.test)


if __name__ == "__main__":
    asyncio.run(main())