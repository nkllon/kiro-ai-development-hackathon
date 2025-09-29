#!/usr/bin/env python3
"""
AI Memory Palace API Server.

Starts the REST API server for AI Memory Palace with all integrated components.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.ai_memory_palace.api import ContextAPI
from beast_mode.ai_memory_palace.context_manager import ContextManager
from beast_mode.ai_memory_palace.context_registry import ContextRegistry
from beast_mode.ai_memory_palace.storage import ContextStorage
from beast_mode.ai_memory_palace.multi_project_manager import MultiProjectContextManager
from beast_mode.ai_memory_palace.backup_recovery import ContextBackupManager
from beast_mode.ai_memory_palace.analytics import ContextAnalyzer, ContextOptimizer
from beast_mode.ai_memory_palace.spec_integration import SpecWorkflowIntegrator
from beast_mode.ai_memory_palace.developer_tools import ContextInspector
from beast_mode.ai_memory_palace.security import ContextSecurityManager
from beast_mode.ai_memory_palace.context_validator import ContextValidator


def create_api_server() -> ContextAPI:
    """Create API server with all dependencies"""
    # Initialize storage and core components
    storage_dir = Path.home() / ".kiro" / "context_storage"
    storage = ContextStorage(storage_dir)
    registry = ContextRegistry(storage)
    
    # Initialize managers
    context_manager = ContextManager(registry)
    security = ContextSecurityManager()
    multi_project_manager = MultiProjectContextManager(registry, security)
    
    # Initialize backup system
    validator = ContextValidator()
    backup_manager = ContextBackupManager(storage, validator)
    
    # Initialize analytics
    analyzer = ContextAnalyzer(registry)
    optimizer = ContextOptimizer(registry, analyzer)
    
    # Initialize integrations
    spec_integrator = SpecWorkflowIntegrator(context_manager, multi_project_manager)
    inspector = ContextInspector(context_manager, registry, validator)
    
    # Create API server
    return ContextAPI(
        context_manager, multi_project_manager, backup_manager,
        analyzer, optimizer, spec_integrator, inspector
    )


def main():
    """Main server entry point"""
    parser = argparse.ArgumentParser(
        description="AI Memory Palace API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server on default port (8000)
  python ai_memory_palace_server.py
  
  # Start on custom port
  python ai_memory_palace_server.py --port 8080
  
  # Start with auto-reload for development
  python ai_memory_palace_server.py --reload --log-level debug
  
  # Start on all interfaces
  python ai_memory_palace_server.py --host 0.0.0.0 --port 8000
        """
    )
    
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true',
                       help='Enable auto-reload for development')
    parser.add_argument('--log-level', type=str, default='info',
                       choices=['debug', 'info', 'warning', 'error'],
                       help='Log level (default: info)')
    
    args = parser.parse_args()
    
    try:
        print("🚀 Starting AI Memory Palace API Server...")
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print(f"Reload: {args.reload}")
        print(f"Log Level: {args.log_level}")
        print()
        
        # Create API server
        api_server = create_api_server()
        
        print("✅ API server initialized")
        print(f"📖 API Documentation: http://{args.host}:{args.port}/docs")
        print(f"🔄 ReDoc Documentation: http://{args.host}:{args.port}/redoc")
        print(f"🏥 Health Check: http://{args.host}:{args.port}/health")
        print()
        
        # Start server
        api_server.run_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level
        )
        
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
        return 0
    
    except ImportError as e:
        if "fastapi" in str(e).lower():
            print("❌ FastAPI is required to run the API server")
            print("Install with: pip install fastapi uvicorn")
        else:
            print(f"❌ Import error: {e}")
        return 1
    
    except Exception as e:
        print(f"💥 Server error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())