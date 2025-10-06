#!/usr/bin/env python3
"""
Start the Beast Mode Engagement Manager service.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from beast_mode.engagement.manager import EngagementManager
    from beast_mode.engagement.config import EngagementConfig
except ImportError as e:
    print(f"⚠️ Engagement Manager not available: {e}")
    print("🔧 Starting minimal engagement service...")
    
    # Fallback minimal service
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI(title="Engagement Manager", version="1.0.0")
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "engagement-manager",
            "mode": "minimal"
        }
    
    @app.get("/status")
    async def status():
        return {
            "engagement_active": False,
            "message": "Engagement Manager in minimal mode"
        }
    
    if __name__ == "__main__":
        uvicorn.run(
            app,
            host=os.getenv("ENGAGEMENT_HOST", "0.0.0.0"),
            port=int(os.getenv("ENGAGEMENT_PORT", "8891")),
            log_level="info"
        )
    sys.exit(0)


async def main():
    """Start the Engagement Manager service."""
    print("🎯 Starting Beast Mode Engagement Manager...")
    
    # Create configuration
    config = EngagementConfig()
    config.host = os.getenv("ENGAGEMENT_HOST", "0.0.0.0")
    config.port = int(os.getenv("ENGAGEMENT_PORT", "8891"))
    config.observatory_url = os.getenv("OBSERVATORY_URL", "http://localhost:8888")
    config.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
    config.redis_host = os.getenv("REDIS_HOST", "localhost")
    config.redis_port = int(os.getenv("REDIS_PORT", "6379"))
    
    # Start the engagement manager
    manager = EngagementManager(config)
    
    try:
        print("✅ Engagement Manager initialized!")
        print(f"🌐 Starting service on http://{config.host}:{config.port}")
        print("📊 Connecting to Observatory and Jaeger...")
        print("Press Ctrl+C to stop...")
        
        # Run the manager
        await manager.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Engagement Manager...")
        await manager.shutdown()
        print("✅ Engagement Manager stopped gracefully")
    except Exception as e:
        print(f"❌ Error running Engagement Manager: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())