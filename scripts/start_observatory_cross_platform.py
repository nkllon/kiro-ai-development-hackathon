#!/usr/bin/env python3
"""
Cross-platform Observatory startup script.
Handles Docker Desktop (macOS/Windows) and native Linux deployments.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def detect_environment():
    """Detect the runtime environment and return configuration."""
    
    # Check if running in Docker
    in_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_DESKTOP') == 'true'
    
    # Check platform
    system = platform.system().lower()
    
    # Determine Redis host based on environment
    if in_docker:
        if os.getenv('DOCKER_DESKTOP') == 'true':
            # Docker Desktop on macOS/Windows
            redis_host = 'host.docker.internal'
            print("🐳 Docker Desktop environment detected")
        else:
            # Native Docker on Linux
            redis_host = 'redis'  # Assume Redis container name
            print("🐧 Native Docker environment detected")
    else:
        # Native host execution
        redis_host = 'localhost'
        print(f"💻 Native {system} environment detected")
    
    return {
        'in_docker': in_docker,
        'system': system,
        'redis_host': redis_host,
        'docker_desktop': os.getenv('DOCKER_DESKTOP') == 'true'
    }

def set_environment_variables(config):
    """Set environment variables based on detected configuration."""
    
    # Set Redis configuration
    os.environ['REDIS_HOST'] = config['redis_host']
    os.environ['REDIS_PORT'] = '6379'
    os.environ['REDIS_DB'] = '0'
    
    # Set Observatory configuration
    os.environ['OBSERVATORY_HOST'] = '0.0.0.0'
    os.environ['OBSERVATORY_PORT'] = '8888'
    
    # Set logging
    os.environ['LOG_LEVEL'] = 'INFO'
    
    print(f"✅ Environment configured for {config['system']} ({'Docker' if config['in_docker'] else 'Native'})")
    print(f"📡 Redis host: {config['redis_host']}")

def main():
    """Main startup function."""
    print("🚀 Starting Cross-Platform Observatory...")
    
    # Detect environment and configure
    config = detect_environment()
    set_environment_variables(config)
    
    # Add src to Python path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Try to start the full Observatory
    try:
        print("🌐 Attempting to start full Observatory server...")
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent.parent / "start_observatory.py")
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Full Observatory failed to start: {e}")
        print("🔄 Falling back to minimal server...")
        
        try:
            subprocess.run([
                sys.executable,
                str(Path(__file__).parent.parent / "start_observatory_minimal.py")
            ], check=True)
        except subprocess.CalledProcessError as e2:
            print(f"❌ Minimal server also failed: {e2}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Observatory shutdown requested")
        sys.exit(0)

if __name__ == "__main__":
    main()