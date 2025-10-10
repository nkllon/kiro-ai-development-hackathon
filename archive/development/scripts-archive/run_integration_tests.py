#!/usr/bin/env python3
"""
Run comprehensive engagement integration tests.

This script starts the Observatory server and runs integration tests.
"""

import asyncio
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def run_integration_tests():
    """Run the complete integration test suite."""
    print("🧪 Starting Observatory Engagement Integration Test Suite")
    print("=" * 60)
    
    server_process = None
    
    try:
        # Start the Observatory server in background
        print("🚀 Starting Observatory server for testing...")
        
        server_process = subprocess.Popen([
            sys.executable, "-c", """
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

async def start_server():
    from src.beast_mode.observatory.server import create_server
    server = create_server()
    await server.run_server(host="localhost", port=8888)

asyncio.run(start_server())
"""], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        await asyncio.sleep(5)
        
        # Check if server is running
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
        
        print("✅ Server started successfully")
        
        # Run the integration tests
        print("🧪 Running integration tests...")
        
        # Import and run the test suite
        from test_engagement_integration import EngagementIntegrationTester
        
        tester = EngagementIntegrationTester("http://localhost:8888")
        report = await tester.run_all_tests()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Partial: {summary['partial']} ⚠️")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Overall Status: {summary['overall_status']}")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)
        
        for result in report["test_results"]:
            status_emoji = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}
            print(f"{status_emoji.get(result['status'], '❓')} {result['test']}: {result['status']}")
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        # Save report
        import json
        report_file = "engagement_integration_test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Determine success
        success = summary["overall_status"] in ["PASS", "PARTIAL"]
        
        if success:
            print("\n✅ INTEGRATION TESTS COMPLETED SUCCESSFULLY")
        else:
            print("\n❌ INTEGRATION TESTS FAILED")
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up server process
        if server_process and server_process.poll() is None:
            print("🛑 Stopping test server...")
            try:
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
                else:
                    server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(server_process.pid), signal.SIGKILL)
                    else:
                        server_process.kill()
                    server_process.wait()
                    
                print("✅ Test server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping server: {e}")

if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)