#!/usr/bin/env python3
"""
Minimal Observatory Startup
===========================

Start Observatory in minimal mode without external dependencies.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def start_minimal_observatory():
    """Start Observatory with minimal configuration."""
    print("🚀 Starting Minimal Observatory...")
    
    # Set minimal environment variables
    os.environ.update({
        'OBSERVATORY_HOST': '0.0.0.0',
        'OBSERVATORY_PORT': '8888',
        'LOG_LEVEL': 'INFO',
        'MINIMAL_MODE': 'true',
        'SKIP_REDIS': 'true',
        'SKIP_PROMETHEUS': 'true',
        'SKIP_GRAFANA': 'true',
        'SKIP_JAEGER': 'true',
        'SKIP_ENGAGEMENT': 'true'
    })
    
    try:
        # Try to import and start Observatory in minimal mode
        from beast_mode.observatory.server import create_server
        
        print("✅ Observatory modules imported")
        
        # Create server with minimal config
        server = create_server()
        print("✅ Observatory server created")
        
        # Start the server
        print("🌐 Starting Observatory on http://0.0.0.0:8888")
        await server.run_server(host="0.0.0.0", port=8888)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Trying alternative startup method...")
        
        # Alternative: try direct FastAPI startup
        try:
            from fastapi import FastAPI
            from fastapi.responses import JSONResponse
            import uvicorn
            
            app = FastAPI(title="Observatory Minimal")
            
            @app.get("/health")
            async def health():
                return JSONResponse({"status": "ok", "mode": "minimal"})
            
            @app.get("/ready")
            async def ready():
                return JSONResponse({"status": "ready", "mode": "minimal"})
            
            @app.get("/metrics")
            async def metrics():
                return "# Observatory minimal metrics\nobservatory_status 1\n"
            
            @app.get("/")
            async def dashboard():
                return JSONResponse({"message": "Observatory Minimal Dashboard", "status": "running"})
            
            print("✅ Minimal FastAPI server created")
            print("🌐 Starting minimal server on http://0.0.0.0:8888")
            
            # Run the server
            config = uvicorn.Config(app, host="0.0.0.0", port=8888, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            print(f"❌ Alternative startup failed: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Observatory startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        asyncio.run(start_minimal_observatory())
    except KeyboardInterrupt:
        print("\n🛑 Observatory stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)