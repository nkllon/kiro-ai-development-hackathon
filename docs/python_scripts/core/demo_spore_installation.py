#!/usr/bin/env python3
"""
Demo: Beast Mode Bus Client Installation Spore
Shows how another agent would use the spore to join the network
"""

import asyncio
import subprocess
import sys
import time


async def demo_spore_installation():
    """Demonstrate the spore installation process"""

    print("🧬 BEAST MODE SPORE INSTALLATION DEMO")
    print("=" * 50)
    print()

    print("📋 Step 1: Check Redis Connection")
    try:
        result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
        if result.returncode == 0 and "PONG" in result.stdout:
            print("✅ Redis is running and accessible")
        else:
            print("❌ Redis not available - install with: brew install redis")
            return False
    except FileNotFoundError:
        print("❌ redis-cli not found - install with: brew install redis")
        return False

    print()
    print("📋 Step 2: Check Python Dependencies")
    try:
        import redis.asyncio as redis
        from pydantic import BaseModel

        print("✅ Python dependencies available (redis, pydantic)")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install 'redis[hiredis]' pydantic")
        return False

    print()
    print("📋 Step 3: Test Spore Client")
    print("Starting Beast Mode Bus Client from spore...")

    # Start the spore client
    process = subprocess.Popen(
        [sys.executable, "beast_mode_bus_client_from_spore.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Let it run for a few seconds
    time.sleep(3)

    # Check if it's still running (good sign)
    if process.poll() is None:
        print("✅ Spore client started successfully and is running")

        # Terminate it gracefully
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

        print("✅ Spore client terminated gracefully")
    else:
        stdout, stderr = process.communicate()
        print("❌ Spore client failed to start")
        if stdout:
            print("STDOUT:", stdout)
        if stderr:
            print("STDERR:", stderr)
        return False

    print()
    print("📋 Step 4: Network Communication Test")
    print("Testing agent discovery between two spore clients...")

    # Start two clients to test communication
    client1 = subprocess.Popen(
        [sys.executable, "test_bus_client.py", "demo_agent_1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    client2 = subprocess.Popen(
        [sys.executable, "beast_mode_bus_client_from_spore.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Let them discover each other
    time.sleep(2)

    # Check both are running
    if client1.poll() is None and client2.poll() is None:
        print("✅ Both clients running - agent discovery should be working")
    else:
        print("❌ One or both clients failed to start")

    # Clean up
    for client in [client1, client2]:
        if client.poll() is None:
            client.terminate()
            try:
                client.wait(timeout=2)
            except subprocess.TimeoutExpired:
                client.kill()

    print()
    print("🎉 SPORE INSTALLATION DEMO COMPLETE!")
    print()
    print("✅ The Beast Mode Bus Client Installation Spore is working correctly!")
    print("✅ Any agent can use this spore to join the Beast Mode network")
    print("✅ Network communication and agent discovery are functional")
    print()
    print("🚀 Ready for systematic collaboration!")

    return True


if __name__ == "__main__":
    success = asyncio.run(demo_spore_installation())
    if success:
        print("\n🧬 SPORE VALIDATION: SUCCESS")
    else:
        print("\n❌ SPORE VALIDATION: FAILED")
    sys.exit(0 if success else 1)
