#!/usr/bin/env python3
"""
Bootstrap Beast Mode Network - Single Machine Deployment
Proper deployment design for multiple Kiro instances on same macOS box
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

def check_redis():
    """Check if Redis is running"""
    try:
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() == 'PONG'
    except:
        return False

def start_redis():
    """Start Redis if not running"""
    if check_redis():
        print("✅ Redis already running")
        return True
        
    print("🔧 Starting Redis...")
    try:
        # Start Redis via Homebrew
        subprocess.run(['brew', 'services', 'start', 'redis'], check=True)
        
        # Wait for Redis to start
        for i in range(10):
            time.sleep(1)
            if check_redis():
                print("✅ Redis started successfully")
                return True
                
        print("❌ Redis failed to start")
        return False
        
    except subprocess.CalledProcessError:
        print("❌ Failed to start Redis via Homebrew")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'redis[hiredis]', 'pydantic'], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

async def test_network():
    """Test the Beast Mode network"""
    print("\n🧪 Testing Beast Mode Network...")
    
    # Import after dependencies are installed
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    try:
        import redis.asyncio as redis
        from pydantic import BaseModel
    except ImportError:
        print("❌ Dependencies not available")
        return False
    
    # Test Redis connection
    try:
        client = redis.from_url("redis://localhost:6379")
        await client.ping()
        await client.aclose()
        print("✅ Redis connection test passed")
        return True
    except Exception as e:
        print(f"❌ Redis connection test failed: {e}")
        return False

def print_deployment_status():
    """Print current deployment status"""
    print("\n🧬 Beast Mode Bootstrap Deployment Status")
    print("=" * 50)
    
    # Check Redis
    redis_status = "✅ Running" if check_redis() else "❌ Not Running"
    print(f"Redis Server: {redis_status}")
    
    # Check Python packages
    try:
        import redis
        import pydantic
        deps_status = "✅ Installed"
    except ImportError:
        deps_status = "❌ Missing"
    print(f"Python Dependencies: {deps_status}")
    
    # Check scripts
    scripts = [
        "beast_mode_spore_distributor.py",
        "beast_mode_spore_receiver.py", 
        "simple_pubsub_test.py"
    ]
    
    print(f"\nAvailable Scripts:")
    for script in scripts:
        if Path(script).exists():
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script}")
    
    print(f"\n🎯 Bootstrap Configuration:")
    print(f"  Redis URL: redis://localhost:6379")
    print(f"  Network Channel: beast_mode_network")
    print(f"  Deployment Type: Single Machine (macOS)")
    print(f"  Max Concurrent Agents: 100+")

def print_usage_instructions():
    """Print usage instructions for bootstrap deployment"""
    print(f"\n🚀 Bootstrap Usage Instructions")
    print("=" * 40)
    
    print(f"\n1. Test the network:")
    print(f"   python3 simple_pubsub_test.py")
    
    print(f"\n2. Start spore distributor (Terminal 1):")
    print(f"   python3 beast_mode_spore_distributor.py")
    print(f"   # Choose option 4 to listen for requests")
    
    print(f"\n3. Start spore receiver (Terminal 2):")
    print(f"   python3 beast_mode_spore_receiver.py")
    print(f"   # Choose option 3 for interactive mode")
    
    print(f"\n4. Start additional Kiro instances:")
    print(f"   # Each Kiro instance connects to redis://localhost:6379")
    print(f"   # Each gets unique agent ID automatically")
    print(f"   # All participate in same beast_mode_network channel")
    
    print(f"\n5. Monitor network activity:")
    print(f"   redis-cli monitor")
    print(f"   # Watch all pub/sub messages in real-time")

async def main():
    """Main bootstrap function"""
    print("🧬 Beast Mode Network Bootstrap")
    print("Single Machine Deployment (macOS)")
    print("=" * 50)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        return
    
    # Step 2: Start Redis
    if not start_redis():
        return
        
    # Step 3: Test network
    if not await test_network():
        return
        
    # Step 4: Show status
    print_deployment_status()
    
    # Step 5: Show usage
    print_usage_instructions()
    
    print(f"\n🎉 Beast Mode Bootstrap Complete!")
    print(f"Ready for systematic collaboration on single macOS box! 🧬")

if __name__ == "__main__":
    asyncio.run(main())