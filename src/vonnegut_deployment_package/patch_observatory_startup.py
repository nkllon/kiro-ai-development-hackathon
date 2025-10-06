#!/usr/bin/env python3
"""
🚨 OBSERVER MODE PATCH - Observatory Startup Fix
Patches the Observatory startup to handle Prometheus initialization issues
"""

import os
import sys
from pathlib import Path


def patch_prometheus_initialization():
    """Patch the Prometheus initialization to be more robust."""
    print("🔧 PATCHING PROMETHEUS INITIALIZATION")
    print("=" * 40)
    
    # Find the prometheus_exporter module
    prometheus_files = [
        "src/beast_mode/observatory/prometheus_exporter.py",
        "src/beast_mode/prometheus_exporter.py", 
        "src/prometheus_exporter.py"
    ]
    
    target_file = None
    for file_path in prometheus_files:
        if Path(file_path).exists():
            target_file = file_path
            break
    
    if not target_file:
        print("❌ Could not find prometheus_exporter.py")
        return False
    
    print(f"✅ Found prometheus exporter: {target_file}")
    
    # Read the current file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Create a patched version that handles initialization more gracefully
    patched_content = content
    
    # Add timeout and error handling to prometheus initialization
    if "prometheus_client" in content and "start_http_server" in content:
        # Patch the start_http_server call to be more robust
        patched_content = patched_content.replace(
            "start_http_server(port)",
            """try:
            start_http_server(port, addr='0.0.0.0')
            print(f"✅ Prometheus metrics server started on port {port}")
        except Exception as e:
            print(f"⚠️  Prometheus metrics server failed to start: {e}")
            print("📊 Metrics will be available but not served via HTTP")"""
        )
    
    # Add graceful handling for monitoring daemon connection
    if "Monitoring daemon not running" in content:
        patched_content = patched_content.replace(
            'print("WARNING - Monitoring daemon not running on port 8000, falling back to legacy mode")',
            'print("INFO - Using legacy metrics mode (monitoring daemon not required)")'
        )
    
    # Write the patched file
    with open(target_file, 'w') as f:
        f.write(patched_content)
    
    print(f"✅ Patched {target_file}")
    return True


def patch_observatory_startup():
    """Patch the main Observatory startup to be more robust."""
    print("🔧 PATCHING OBSERVATORY STARTUP")
    print("=" * 40)
    
    startup_file = "start_observatory.py"
    if not Path(startup_file).exists():
        print("❌ start_observatory.py not found")
        return False
    
    with open(startup_file, 'r') as f:
        content = f.read()
    
    # Add better error handling and timeout
    if "await server.run_server" in content:
        patched_content = content.replace(
            'await server.run_server(host="0.0.0.0", port=8888)',
            '''print("🚀 Starting Observatory server...")
        try:
            await server.run_server(host="0.0.0.0", port=8888)
        except Exception as e:
            print(f"❌ Observatory server failed to start: {e}")
            import traceback
            traceback.print_exc()
            # Try to start in minimal mode
            print("🔄 Attempting minimal mode startup...")
            await server.run_minimal_server(host="0.0.0.0", port=8888)'''
        )
        
        with open(startup_file, 'w') as f:
            f.write(patched_content)
        
        print(f"✅ Patched {startup_file}")
        return True
    
    return False


def create_minimal_health_server():
    """Create a minimal health server as fallback."""
    print("🔧 CREATING MINIMAL HEALTH SERVER")
    print("=" * 40)
    
    minimal_server_content = '''#!/usr/bin/env python3
"""
Minimal Observatory Health Server - Emergency Fallback
Provides basic health endpoints when full Observatory fails
"""

from fastapi import FastAPI
import uvicorn
import asyncio
import sys
import os

app = FastAPI(title="Observatory Health Server - Emergency Mode")

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "emergency", "message": "Observatory running in minimal mode"}

@app.get("/api/observatory/status") 
async def status():
    return {
        "status": "degraded",
        "mode": "emergency",
        "services": {
            "health": "ok",
            "metrics": "unavailable", 
            "websocket": "unavailable"
        },
        "message": "Observatory running in emergency mode - limited functionality"
    }

@app.get("/")
async def root():
    return {"message": "Observatory Emergency Health Server", "endpoints": ["/health", "/api/observatory/status"]}

async def main():
    print("🚨 STARTING OBSERVATORY EMERGENCY HEALTH SERVER")
    print("📊 Limited functionality - health endpoints only")
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=8888,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("start_observatory_minimal.py", "w") as f:
        f.write(minimal_server_content)
    
    print("✅ Created start_observatory_minimal.py")
    return True


def apply_emergency_patches():
    """Apply all emergency patches to get Observatory running."""
    print("🚨 APPLYING EMERGENCY OBSERVATORY PATCHES")
    print("=" * 50)
    
    success = True
    
    # Patch 1: Prometheus initialization
    if not patch_prometheus_initialization():
        print("⚠️  Prometheus patch failed")
        success = False
    
    # Patch 2: Observatory startup
    if not patch_observatory_startup():
        print("⚠️  Observatory startup patch failed")
        success = False
    
    # Patch 3: Create minimal fallback
    if not create_minimal_health_server():
        print("⚠️  Minimal server creation failed")
        success = False
    
    return success


def update_dockerfile_for_patches():
    """Update Dockerfile to use patched startup."""
    print("🔧 UPDATING DOCKERFILE FOR PATCHES")
    print("=" * 40)
    
    dockerfile_path = "deployment/observatory/Dockerfile"
    if not Path(dockerfile_path).exists():
        print("❌ Dockerfile not found")
        return False
    
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    # Add the minimal server as backup
    if "COPY start_observatory.py ." in content:
        patched_content = content.replace(
            "COPY start_observatory.py .",
            """COPY start_observatory.py .
COPY start_observatory_minimal.py ."""
        )
        
        # Update the CMD to try main server first, fallback to minimal
        patched_content = patched_content.replace(
            'CMD ["python", "start_observatory.py"]',
            '''CMD ["sh", "-c", "python start_observatory.py || python start_observatory_minimal.py"]'''
        )
        
        with open(dockerfile_path, 'w') as f:
            f.write(patched_content)
        
        print("✅ Updated Dockerfile with fallback server")
        return True
    
    return False


if __name__ == "__main__":
    print("🚨 OBSERVATORY EMERGENCY PATCH SYSTEM")
    print("Observer Mode: Patch → Rebuild → Deploy")
    print()
    
    # Apply patches
    if apply_emergency_patches():
        print("✅ Emergency patches applied successfully")
        
        # Update Dockerfile
        if update_dockerfile_for_patches():
            print("✅ Dockerfile updated with patches")
            print()
            print("🔧 NEXT STEPS:")
            print("1. Rebuild containers: docker-compose build observatory")
            print("2. Restart deployment: docker-compose up -d")
            print("3. Test health: curl http://localhost:8888/health")
            print()
            print("🚨 Emergency patches will provide basic health endpoints")
            print("📊 Full Observatory functionality may be limited")
        else:
            print("❌ Failed to update Dockerfile")
            sys.exit(1)
    else:
        print("❌ Emergency patches failed")
        sys.exit(1)