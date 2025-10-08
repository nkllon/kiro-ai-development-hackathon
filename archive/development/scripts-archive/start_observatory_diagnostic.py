#!/usr/bin/env python3
"""
Diagnostic Observatory startup script.
Shows exactly where the startup process fails with detailed logging.
"""

import asyncio
import sys
import os
import time
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def log_step(step, details=""):
    """Log each step with timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🔍 DIAGNOSTIC: {step}")
    if details:
        print(f"    └─ {details}")
    sys.stdout.flush()

def log_error(step, error):
    """Log errors with full traceback."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ❌ ERROR in {step}: {error}")
    print(f"    └─ Traceback:")
    traceback.print_exc()
    sys.stdout.flush()

async def main():
    """Diagnostic Observatory startup with detailed logging."""
    log_step("STARTUP", "Beginning diagnostic Observatory startup")
    
    # Step 1: Environment check
    log_step("ENVIRONMENT", "Checking environment variables")
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    log_step("REDIS_CONFIG", f"Redis: {redis_host}:{redis_port}")
    
    # Step 2: Import checks
    log_step("IMPORTS", "Testing critical imports")
    
    try:
        log_step("IMPORT_MODELS", "Importing Observatory models")
        from beast_mode.observatory.models import ObservatoryConfig, WebSocketConfig
        log_step("IMPORT_MODELS", "✅ Models imported successfully")
    except Exception as e:
        log_error("IMPORT_MODELS", e)
        return False
    
    try:
        log_step("IMPORT_SERVER", "Importing Observatory server")
        from beast_mode.observatory.server import ObservatoryServer
        log_step("IMPORT_SERVER", "✅ Server imported successfully")
    except Exception as e:
        log_error("IMPORT_SERVER", e)
        return False
    
    # Step 3: Configuration creation
    try:
        log_step("CONFIG_CREATE", "Creating Observatory configuration")
        config = ObservatoryConfig()
        log_step("CONFIG_CREATE", "✅ Configuration created")
        
        log_step("WEBSOCKET_CONFIG", "Setting up WebSocket configuration")
        config.websocket_config = WebSocketConfig(
            host="0.0.0.0",
            port=8888,
            max_connections=100,
            heartbeat_interval=30
        )
        log_step("WEBSOCKET_CONFIG", "✅ WebSocket config set")
        
    except Exception as e:
        log_error("CONFIG_CREATE", e)
        return False
    
    # Step 4: Server creation
    try:
        log_step("SERVER_CREATE", "Creating Observatory server instance")
        server = ObservatoryServer(config)
        log_step("SERVER_CREATE", "✅ Server instance created")
        
    except Exception as e:
        log_error("SERVER_CREATE", e)
        return False
    
    # Step 5: Redis connectivity test
    try:
        log_step("REDIS_TEST", "Testing Redis connectivity")
        import redis
        r = redis.Redis(host=redis_host, port=int(redis_port), db=0, socket_timeout=5)
        r.ping()
        log_step("REDIS_TEST", "✅ Redis connection successful")
        
    except Exception as e:
        log_error("REDIS_TEST", e)
        log_step("REDIS_FALLBACK", "Continuing without Redis...")
    
    # Step 6: Jaeger tracing check
    try:
        log_step("JAEGER_CHECK", "Checking Jaeger tracing availability")
        jaeger_endpoint = os.getenv('JAEGER_ENDPOINT', 'http://observatory-jaeger:14268/api/traces')
        log_step("JAEGER_CONFIG", f"Jaeger endpoint: {jaeger_endpoint}")
        
        # Try to import tracing
        try:
            from src.beast_mode.tracing.tracer import get_tracer
            tracer = get_tracer("observatory-diagnostic")
            log_step("JAEGER_CHECK", "✅ Jaeger tracing available")
        except ImportError:
            log_step("JAEGER_CHECK", "⚠️ Jaeger tracing not available (optional)")
            
    except Exception as e:
        log_error("JAEGER_CHECK", e)
    
    # Step 7: Server startup attempt
    try:
        log_step("SERVER_START", "Attempting to start Observatory server")
        log_step("SERVER_START", "This is where the hang usually occurs...")
        
        # Add timeout to detect hangs
        try:
            # Try to start with a timeout
            await asyncio.wait_for(
                server.run_server(host="0.0.0.0", port=8888),
                timeout=30.0  # 30 second timeout
            )
            
        except asyncio.TimeoutError:
            log_error("SERVER_START", "Server startup timed out after 30 seconds")
            log_step("TIMEOUT_ANALYSIS", "Server startup is hanging - this is the root issue")
            
            # Try to identify what's hanging
            log_step("HANG_ANALYSIS", "Analyzing potential hang causes:")
            log_step("HANG_ANALYSIS", "1. FastAPI app initialization")
            log_step("HANG_ANALYSIS", "2. WebSocket server setup")
            log_step("HANG_ANALYSIS", "3. Engagement integration")
            log_step("HANG_ANALYSIS", "4. External service connections")
            
            return False
            
    except Exception as e:
        log_error("SERVER_START", e)
        return False
    
    log_step("SUCCESS", "Observatory started successfully!")
    return True

def fallback_to_minimal():
    """Start minimal server as fallback."""
    log_step("FALLBACK", "Starting minimal Observatory server")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "start_observatory_minimal.py"])
        return result.returncode == 0
    except Exception as e:
        log_error("FALLBACK", e)
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            log_step("FALLBACK_DECISION", "Main Observatory failed, attempting fallback")
            fallback_to_minimal()
    except KeyboardInterrupt:
        log_step("SHUTDOWN", "Observatory diagnostic interrupted by user")
    except Exception as e:
        log_error("MAIN", e)
        log_step("FALLBACK_DECISION", "Unexpected error, attempting fallback")
        fallback_to_minimal()