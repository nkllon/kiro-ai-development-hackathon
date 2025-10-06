#!/usr/bin/env python3
"""
Start Jaeger tracing infrastructure for Beast Mode system visibility
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def start_jaeger():
    """Start Jaeger using docker-compose"""
    print("🚀 Starting Jaeger distributed tracing...")
    
    # Check if docker-compose file exists
    compose_file = Path("docker-compose.jaeger.yml")
    if not compose_file.exists():
        print(f"❌ Docker compose file not found: {compose_file}")
        return False
    
    try:
        # Start Jaeger
        result = subprocess.run([
            "docker-compose", "-f", "docker-compose.jaeger.yml", "up", "-d"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Jaeger container started")
            return True
        else:
            print(f"❌ Failed to start Jaeger: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ docker-compose not found. Install Docker Compose.")
        return False

def wait_for_jaeger():
    """Wait for Jaeger to be ready"""
    print("⏳ Waiting for Jaeger to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:16686/", timeout=5)
            if response.status_code == 200:
                print("✅ Jaeger UI is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ Jaeger failed to start within timeout")
    return False

def install_opentelemetry():
    """Install OpenTelemetry dependencies"""
    print("📦 Installing OpenTelemetry dependencies...")
    
    packages = [
        "opentelemetry-api",
        "opentelemetry-sdk", 
        "opentelemetry-exporter-jaeger",
        "opentelemetry-instrumentation-fastapi",
        "opentelemetry-instrumentation-requests",
        "opentelemetry-instrumentation-logging"
    ]
    
    try:
        for package in packages:
            print(f"   Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install {package}: {result.stderr}")
                return False
        
        print("✅ OpenTelemetry dependencies installed")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def show_jaeger_info():
    """Show Jaeger access information"""
    print("\n🎯 Jaeger Distributed Tracing Ready!")
    print("=" * 50)
    print("🌐 Jaeger UI: http://localhost:16686")
    print("📊 Collector HTTP: http://localhost:14268")
    print("🔍 Agent UDP: localhost:6831")
    print()
    print("💡 Usage:")
    print("   1. Start your Beast Mode services")
    print("   2. Generate some activity (status announcements, API calls)")
    print("   3. View traces in Jaeger UI")
    print("   4. Analyze service dependencies and performance")
    print()
    print("🔧 To stop Jaeger:")
    print("   docker-compose -f docker-compose.jaeger.yml down")

def main():
    """Main function"""
    print("🔍 Beast Mode Jaeger Tracing Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_docker():
        print("\n💡 Install Docker first: https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    # Install OpenTelemetry if needed
    try:
        import opentelemetry
        print("✅ OpenTelemetry is available")
    except ImportError:
        if not install_opentelemetry():
            sys.exit(1)
    
    # Start Jaeger
    if not start_jaeger():
        sys.exit(1)
    
    # Wait for Jaeger to be ready
    if not wait_for_jaeger():
        sys.exit(1)
    
    # Show access information
    show_jaeger_info()

if __name__ == "__main__":
    main()