#!/usr/bin/env python3
"""
Check Node B Environment Setup
=============================

Validates that all required credentials and dependencies are available
before launching Node B.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_environment():
    """Check if environment is properly configured for Node B."""
    print("🔍 Checking Node B Environment Setup...")
    
    issues = []
    
    # Check Redis credentials
    try:
        from src.security.secure_credentials import get_redis_password
        redis_password = get_redis_password()
        if redis_password:
            print("✅ Redis password: Available")
        else:
            issues.append("❌ Redis password: Not found")
    except Exception as e:
        issues.append(f"❌ Redis password: Error - {e}")
    
    # Check Redis connectivity
    try:
        import redis
        from src.security.secure_credentials import get_redis_password
        
        redis_password = get_redis_password()
        client = redis.Redis(
            host="192.168.1.119",
            port=6379,
            password=redis_password,
            socket_timeout=5
        )
        
        # Test connection
        client.ping()
        print("✅ Redis connectivity: Connected to 192.168.1.119:6379")
        
        # Test pub/sub
        pubsub = client.pubsub()
        pubsub.subscribe("test_channel")
        print("✅ Redis pub/sub: Available")
        pubsub.close()
        
    except Exception as e:
        issues.append(f"❌ Redis connectivity: {e}")
    
    # Check Beast Mode infrastructure
    try:
        from beast_mode.messaging import BeastModeBusClient, BeastModeMessage, MessageType
        print("✅ Beast Mode messaging: Available")
    except ImportError as e:
        issues.append(f"❌ Beast Mode messaging: {e}")
    
    # Check required Python packages
    required_packages = ['redis', 'asyncio']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Package {package}: Available")
        except ImportError:
            issues.append(f"❌ Package {package}: Not installed")
    
    # Summary
    print("\n" + "="*50)
    if issues:
        print("❌ ENVIRONMENT CHECK FAILED")
        print("\nIssues found:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🔧 To fix:")
        print("1. Add to ~/.env file:")
        print("   REDIS_PASSWORD=beastmode2025")
        print("2. Ensure Redis is running on 192.168.1.119:6379")
        print("3. Install missing packages: pip install redis")
        
        return False
    else:
        print("✅ ENVIRONMENT CHECK PASSED")
        print("Node B is ready to launch!")
        return True

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)