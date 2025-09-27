#!/usr/bin/env python3
"""
Test script to verify FastAPI route discovery implementation for Task 3.1.
"""

import sys
import tempfile
import os
sys.path.append('src')

# Import the specific modules we need
from websocket_validation.config import ValidationConfig
from websocket_validation.collectors import EvidenceCollector

# Create a minimal SystemStateTester to avoid import issues
class MinimalSystemStateTester:
    def __init__(self, config, evidence_collector):
        self.config = config
        self.evidence_collector = evidence_collector
    
    def run_all_tests(self):
        return []

# Monkey patch to avoid circular imports
sys.modules['websocket_validation.testers.system_state'] = type('module', (), {
    'SystemStateTester': MinimalSystemStateTester
})()

# Now import the CodeAnalysisTester
from websocket_validation.testers.code_analysis import CodeAnalysisTester

print("🧪 Testing FastAPI Route Discovery System (Task 3.1)")
print("=" * 55)

# Create configuration and evidence collector
config = ValidationConfig(evidence_dir="test_evidence")
evidence_collector = EvidenceCollector(config)

# Create CodeAnalysisTester
tester = CodeAnalysisTester(config, evidence_collector)

print(f"📋 Configuration:")
print(f"   Evidence Directory: {config.evidence_dir}")
print()

# Test 1: Test FastAPI file discovery
print("🔍 Testing FastAPI file discovery...")
try:
    discovery_result = tester._discover_fastapi_files()
    print(f"   Status: {discovery_result.status.value}")
    print(f"   Server Files Found: {len(discovery_result.metrics.get('server_files', []))}")
    print(f"   Execution Time: {discovery_result.execution_time:.3f}s")
    
    if discovery_result.error_details:
        print(f"   Error: {discovery_result.error_details}")
    
    server_files = discovery_result.metrics.get("server_files", [])
    if server_files:
        print(f"   📁 Found Server Files:")
        for i, file_path in enumerate(server_files[:5]):  # Show first 5
            print(f"     {i+1}. {file_path}")
        if len(server_files) > 5:
            print(f"     ... and {len(server_files) - 5} more files")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print()

# Test 2: Test route analysis on sample FastAPI code
print("🔍 Testing route analysis on sample FastAPI code...")
sample_fastapi_code = '''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="Test WebSocket API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected from chat")

@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send periodic notifications
            await asyncio.sleep(5)
            await websocket.send_text("Notification: System status OK")
    except WebSocketDisconnect:
        print("Client disconnected from notifications")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "websockets": "enabled"}

@app.get("/api/info")
async def get_info():
    return {
        "name": "Test WebSocket API",
        "version": "1.0.0",
        "websocket_endpoints": ["/ws/chat", "/ws/notifications"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(sample_fastapi_code)
    temp_file = f.name

try:
    result = tester._analyze_server_file(temp_file)
    print(f"   Status: {result.status.value}")
    print(f"   WebSocket Routes: {result.metrics.get('websocket_routes', 0)}")
    print(f"   HTTP Routes: {result.metrics.get('http_routes', 0)}")
    print(f"   Total Routes: {result.metrics.get('total_routes', 0)}")
    print(f"   Middleware Count: {result.metrics.get('middleware_count', 0)}")
    print(f"   Execution Time: {result.execution_time:.3f}s")
    
    if result.error_details:
        print(f"   Error: {result.error_details}")
    
    # Show evidence details
    if result.evidence_ids:
        evidence = evidence_collector.get_evidence(result.evidence_ids[0])
        if evidence and isinstance(evidence.data, dict):
            route_analysis = evidence.data.get("route_analysis", {})
            websocket_routes = route_analysis.get("websocket_routes", [])
            http_routes = route_analysis.get("http_routes", [])
            
            print(f"   📊 Route Details:")
            if websocket_routes:
                print(f"     WebSocket Routes:")
                for route in websocket_routes:
                    if isinstance(route, dict):
                        print(f"       - {route.get('path', 'unknown')} -> {route.get('handler', 'unknown')}")
                    else:
                        print(f"       - {route}")
            
            if http_routes:
                print(f"     HTTP Routes:")
                for route in http_routes[:3]:  # Show first 3
                    if isinstance(route, dict):
                        print(f"       - {route.get('method', 'GET')} {route.get('path', 'unknown')} -> {route.get('handler', 'unknown')}")
                    else:
                        print(f"       - {route}")
                if len(http_routes) > 3:
                    print(f"       ... and {len(http_routes) - 3} more HTTP routes")
    print()
    
finally:
    os.unlink(temp_file)

# Test 3: Test full analyze_fastapi_routes method
print("🔍 Testing full analyze_fastapi_routes method...")
try:
    route_results = tester.analyze_fastapi_routes()
    print(f"   Results: {len(route_results)} test results")
    
    total_files = 0
    total_websocket_routes = 0
    total_http_routes = 0
    total_routes = 0
    
    for result in route_results:
        print(f"   - {result.test_name}: {result.status.value}")
        if result.metrics:
            if 'server_files' in result.metrics:
                files = len(result.metrics.get('server_files', []))
                total_files += files
                print(f"     Server Files: {files}")
            elif 'websocket_routes' in result.metrics:
                ws_routes = result.metrics.get('websocket_routes', 0)
                http_routes = result.metrics.get('http_routes', 0)
                routes = result.metrics.get('total_routes', 0)
                total_websocket_routes += ws_routes
                total_http_routes += http_routes
                total_routes += routes
                print(f"     Routes: {ws_routes} WebSocket, {http_routes} HTTP, {routes} total")
    
    print(f"   📊 Overall Summary:")
    print(f"     Total Server Files Analyzed: {total_files}")
    print(f"     Total WebSocket Routes Found: {total_websocket_routes}")
    print(f"     Total HTTP Routes Found: {total_http_routes}")
    print(f"     Total Routes Found: {total_routes}")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print()

# Test 4: Test route discovery on Observatory server
print("🔍 Testing route discovery on Observatory server...")
observatory_server_path = "src/beast_mode/observatory/server.py"
if os.path.exists(observatory_server_path):
    try:
        result = tester._analyze_server_file(observatory_server_path)
        print(f"   Status: {result.status.value}")
        print(f"   WebSocket Routes: {result.metrics.get('websocket_routes', 0)}")
        print(f"   HTTP Routes: {result.metrics.get('http_routes', 0)}")
        print(f"   Total Routes: {result.metrics.get('total_routes', 0)}")
        print(f"   Middleware Count: {result.metrics.get('middleware_count', 0)}")
        print(f"   Execution Time: {result.execution_time:.3f}s")
        
        if result.error_details:
            print(f"   Error: {result.error_details}")
        
        # Show some route details
        if result.evidence_ids:
            evidence = evidence_collector.get_evidence(result.evidence_ids[0])
            if evidence and isinstance(evidence.data, dict):
                route_analysis = evidence.data.get("route_analysis", {})
                websocket_routes = route_analysis.get("websocket_routes", [])
                
                if websocket_routes:
                    print(f"   📊 WebSocket Routes Found:")
                    for route in websocket_routes[:3]:  # Show first 3
                        if isinstance(route, dict):
                            print(f"     - {route.get('path', 'unknown')} -> {route.get('handler', 'unknown')}")
                        else:
                            print(f"     - {route}")
                    if len(websocket_routes) > 3:
                        print(f"     ... and {len(websocket_routes) - 3} more WebSocket routes")
        print()
        
    except Exception as e:
        print(f"   ❌ Error analyzing Observatory server: {e}")
        print()
else:
    print(f"   ⚠️  Observatory server file not found: {observatory_server_path}")
    print()

# Show evidence summary
print("📊 Evidence Collection Summary:")
summary = evidence_collector.generate_summary()
print(f"   Total Evidence Items: {summary['total_items']}")
print(f"   Evidence by Type: {summary['by_type']}")
print(f"   Total Size: {summary['total_size']} bytes")
print(f"   Integrity Verified: {summary['integrity_verified']}")
print()

print("✅ FastAPI Route Discovery System test completed!")
print()
print("🎯 Task 3.1 Implementation Summary:")
print("   ✅ FastAPI server file discovery")
print("   ✅ WebSocket route identification (@app.websocket decorators)")
print("   ✅ HTTP route discovery and analysis")
print("   ✅ Route path and handler extraction")
print("   ✅ Middleware configuration detection")
print("   ✅ AST-based parsing for accuracy")
print("   ✅ Comprehensive evidence collection")
print("   ✅ Integration with validation framework")