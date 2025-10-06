#!/usr/bin/env python3
"""Main entry point for Google Calendar MCP Server.

This module provides the command-line interface and server startup logic
for the Google Calendar MCP integration.
"""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from .server import GoogleCalendarMCPServer
from .auth_manager import GoogleAuthManager
from .operations_handler import CalendarOperationsHandler
from .profiling import get_profiler


class MCPServerRunner:
    """Runner for the Google Calendar MCP Server."""
    
    def __init__(self, config: dict):
        """Initialize the server runner.
        
        Args:
            config: Server configuration dictionary
        """
        self.config = config
        self.server: Optional[GoogleCalendarMCPServer] = None
        self.running = False
        
        # Set up logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Set up structured logging."""
        log_level = getattr(logging, self.config.get("log_level", "INFO").upper())
        
        logging.basicConfig(
            level=log_level,
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                   '"module": "%(name)s", "message": "%(message)s"}',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _create_server_components(self):
        """Create and configure server components."""
        self.logger.info("Creating server components...")
        
        # Create authentication manager
        auth_config = {
            "credentials_file": self.config.get("credentials_file"),
            "scopes": [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events"
            ]
        }
        auth_manager = GoogleAuthManager(auth_config)
        
        # Create operations handler
        ops_config = {
            "default_calendar_id": "primary",
            "timezone": "UTC"
        }
        operations_handler = CalendarOperationsHandler(ops_config)
        
        # Create main server
        server_config = {
            "host": self.config.get("host", "0.0.0.0"),
            "port": self.config.get("port", 3000),
            "log_level": self.config.get("log_level", "info")
        }
        server = GoogleCalendarMCPServer(server_config)
        
        # Wire dependencies
        server.set_auth_manager(auth_manager)
        server.set_operations_handler(operations_handler)
        operations_handler.set_auth_manager(auth_manager)
        
        # Error handler is optional for now
        
        return server, auth_manager, operations_handler
    
    async def start_server(self):
        """Start the MCP server."""
        self.logger.info("Starting Google Calendar MCP Server...")
        
        try:
            # Create components
            self.server, auth_manager, operations_handler = self._create_server_components()
            
            # Initialize components
            self.logger.info("Initializing server components...")
            
            if not auth_manager.initialize():
                self.logger.warning("Auth manager initialization failed, continuing in stub mode")
            
            if not operations_handler.initialize():
                self.logger.warning("Operations handler initialization failed, continuing in stub mode")
            
            if not self.server.initialize():
                self.logger.error("Server initialization failed")
                return False
            
            # Start the server
            if not self.server.start_server():
                self.logger.error("Failed to start MCP server")
                return False
            
            self.running = True
            self.logger.info(f"🚀 Google Calendar MCP Server started on port {self.config['port']}")
            
            # Start profiling
            profiler = get_profiler()
            self.logger.info("📊 Performance profiling enabled")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    async def run_server(self):
        """Run the server main loop."""
        self._setup_signal_handlers()
        
        if not await self.start_server():
            return 1
        
        try:
            # Main server loop
            while self.running:
                await asyncio.sleep(1)
                
                # Health check
                if self.server:
                    health = self.server.get_health_status()
                    if health.status.value != "healthy":
                        self.logger.warning(f"Server health degraded: {health.status}")
            
            self.logger.info("Server shutdown initiated...")
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            return 1
        
        finally:
            await self.shutdown_server()
        
        return 0
    
    async def shutdown_server(self):
        """Gracefully shutdown the server."""
        self.logger.info("Shutting down Google Calendar MCP Server...")
        
        if self.server:
            try:
                self.server.shutdown()
                self.logger.info("✅ Server shutdown complete")
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")
        
        # Generate final profiling report
        try:
            profiler = get_profiler()
            report = profiler.generate_performance_report()
            self.logger.info(f"📊 Final performance report: {report['summary']}")
        except Exception as e:
            self.logger.warning(f"Could not generate final performance report: {e}")


def create_health_check_server():
    """Create a simple health check server for Docker."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    import threading
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                health_data = {
                    "status": "healthy",
                    "service": "google-calendar-mcp",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                self.wfile.write(json.dumps(health_data).encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            # Suppress default logging
            pass
    
    def run_health_server():
        server = HTTPServer(('0.0.0.0', 3000), HealthHandler)
        server.serve_forever()
    
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    return health_thread


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Google Calendar MCP Server")
    parser.add_argument("--port", type=int, default=3000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--log-level", default="info", help="Log level")
    parser.add_argument("--credentials-file", help="Path to Google OAuth credentials file")
    parser.add_argument("--health-only", action="store_true", help="Run health check server only")
    
    args = parser.parse_args()
    
    # If running health-only mode (for Docker health checks)
    if args.health_only:
        print("Starting health check server...")
        health_thread = create_health_check_server()
        try:
            health_thread.join()
        except KeyboardInterrupt:
            print("Health check server stopped")
        return 0
    
    # Validate credentials file
    if args.credentials_file and not Path(args.credentials_file).exists():
        print(f"⚠️  Credentials file not found: {args.credentials_file}")
        print("   Server will start in stub mode for testing")
    
    # Create configuration
    config = {
        "port": args.port,
        "host": args.host,
        "log_level": args.log_level,
        "credentials_file": args.credentials_file
    }
    
    # Create and run server
    runner = MCPServerRunner(config)
    
    try:
        return asyncio.run(runner.run_server())
    except KeyboardInterrupt:
        print("\n🛑 Server interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Server failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())