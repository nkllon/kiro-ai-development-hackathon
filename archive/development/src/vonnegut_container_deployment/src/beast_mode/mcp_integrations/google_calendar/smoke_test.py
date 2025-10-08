#!/usr/bin/env python3
"""Smoke test for Google Calendar MCP Integration.

This script tests the basic functionality of the Google Calendar MCP integration
without requiring actual Google Calendar API credentials.
"""

import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from src.beast_mode.mcp_integrations.google_calendar import (
            GoogleCalendarMCPServer,
            GoogleAuthManager,
            CalendarOperationsHandler,
            get_profiler,
            profile
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_server_initialization():
    """Test server initialization."""
    print("\n🧪 Testing server initialization...")
    
    try:
        from src.beast_mode.mcp_integrations.google_calendar import GoogleCalendarMCPServer
        
        config = {
            "host": "localhost",
            "port": 3001,
            "log_level": "debug"
        }
        
        server = GoogleCalendarMCPServer(config)
        print("✅ Server initialized successfully")
        
        # Test health status
        health = server.get_health_status()
        print(f"✅ Health status: {health.status}")
        
        # Test module info
        info = server.get_module_info()
        print(f"✅ Module info: {info['module_id']}")
        
        return True
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        traceback.print_exc()
        return False

def test_auth_manager():
    """Test authentication manager."""
    print("\n🧪 Testing authentication manager...")
    
    try:
        from src.beast_mode.mcp_integrations.google_calendar import GoogleAuthManager
        
        config = {
            "credentials_file": "/tmp/test_credentials.json",
            "scopes": ["https://www.googleapis.com/auth/calendar"]
        }
        
        auth_manager = GoogleAuthManager(config)
        print("✅ Auth manager initialized")
        
        # Test health status
        health = auth_manager.get_health_status()
        print(f"✅ Auth manager health: {health.status}")
        
        # Test authentication status (should be False without real credentials)
        is_auth = auth_manager.is_authenticated()
        print(f"✅ Authentication status: {is_auth}")
        
        return True
    except Exception as e:
        print(f"❌ Auth manager test failed: {e}")
        traceback.print_exc()
        return False

def test_operations_handler():
    """Test calendar operations handler."""
    print("\n🧪 Testing operations handler...")
    
    try:
        from src.beast_mode.mcp_integrations.google_calendar import CalendarOperationsHandler
        
        config = {
            "default_calendar_id": "primary",
            "timezone": "UTC"
        }
        
        ops_handler = CalendarOperationsHandler(config)
        print("✅ Operations handler initialized")
        
        # Test health status
        health = ops_handler.get_health_status()
        print(f"✅ Operations handler health: {health.status}")
        
        return True
    except Exception as e:
        print(f"❌ Operations handler test failed: {e}")
        traceback.print_exc()
        return False

def test_profiling():
    """Test profiling functionality."""
    print("\n🧪 Testing profiling...")
    
    try:
        from src.beast_mode.mcp_integrations.google_calendar.profiling import get_profiler, profile
        
        profiler = get_profiler()
        print("✅ Profiler initialized")
        
        # Test profiling decorator
        @profile("test_operation")
        def test_function():
            return "test_result"
        
        result = test_function()
        print(f"✅ Profiled function result: {result}")
        
        # Check metrics
        metrics = profiler.get_all_metrics()
        print(f"✅ Profiler has {len(metrics)} operation types")
        
        return True
    except Exception as e:
        print(f"❌ Profiling test failed: {e}")
        traceback.print_exc()
        return False

def test_mcp_request_handling():
    """Test MCP request handling (stub mode)."""
    print("\n🧪 Testing MCP request handling...")
    
    try:
        from src.beast_mode.mcp_integrations.google_calendar import GoogleCalendarMCPServer
        from src.beast_mode.mcp_integrations.google_calendar.models import MCPRequest
        
        # Create server with dependencies
        server = GoogleCalendarMCPServer({"port": 3001})
        
        # Create mock dependencies
        from unittest.mock import Mock
        mock_auth = Mock()
        mock_auth.is_authenticated.return_value = False
        mock_auth.get_access_token.return_value = None
        
        mock_ops = Mock()
        mock_error = Mock()
        
        server.set_auth_manager(mock_auth)
        server.set_operations_handler(mock_ops)
        server.set_error_handler(mock_error)
        
        # Test health status request
        request_data = {
            "method": "health.status",
            "params": {},
            "id": "test_health"
        }
        
        response = server.handle_mcp_request(request_data)
        print(f"✅ Health request response: {response.get('result', {}).get('status', 'unknown')}")
        
        # Test auth status request
        auth_request = {
            "method": "auth.status",
            "params": {},
            "id": "test_auth"
        }
        
        auth_response = server.handle_mcp_request(auth_request)
        print(f"✅ Auth status response: {auth_response.get('result', {})}")
        
        return True
    except Exception as e:
        print(f"❌ MCP request handling test failed: {e}")
        traceback.print_exc()
        return False

def test_docker_readiness():
    """Test Docker deployment readiness."""
    print("\n🧪 Testing Docker readiness...")
    
    try:
        # Check if we have the necessary files for Docker deployment
        import os
        
        required_files = [
            "src/beast_mode/mcp_integrations/google_calendar/server.py",
            "src/beast_mode/mcp_integrations/google_calendar/auth_manager.py",
            "src/beast_mode/mcp_integrations/google_calendar/operations_handler.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing files for Docker deployment: {missing_files}")
            return False
        
        print("✅ All required files present for Docker deployment")
        
        # Test that we can create a basic server instance
        from src.beast_mode.mcp_integrations.google_calendar import GoogleCalendarMCPServer
        server = GoogleCalendarMCPServer({"port": 3000})
        print("✅ Server can be instantiated for Docker deployment")
        
        return True
    except Exception as e:
        print(f"❌ Docker readiness test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all smoke tests."""
    print("🚀 Google Calendar MCP Integration - Smoke Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_server_initialization,
        test_auth_manager,
        test_operations_handler,
        test_profiling,
        test_mcp_request_handling,
        test_docker_readiness
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All smoke tests passed! Ready for Docker deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Check implementation before Docker deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())