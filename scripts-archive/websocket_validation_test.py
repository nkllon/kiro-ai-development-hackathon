#!/usr/bin/env python3
"""
WebSocket Validation Test
Phase 3 WebSocket Validation and Testing
"""

import asyncio
import json
import time
import websockets
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_websocket_endpoint(url: str, endpoint_name: str) -> Dict[str, Any]:
    """Test a single WebSocket endpoint."""
    logger.info(f"Testing {endpoint_name} at {url}")
    
    start_time = time.time()
    result = {
        "endpoint": endpoint_name,
        "url": url,
        "status": "unknown",
        "connection_time": 0,
        "message_received": False,
        "error": None,
        "duration": 0
    }
    
    try:
        # Test connection establishment
        connection_start = time.time()
        websocket = await websockets.connect(url, ping_interval=20, ping_timeout=10)
        connection_time = time.time() - connection_start
        result["connection_time"] = connection_time
        
        # Test message exchange
        test_message = {
            "type": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "test_id": f"validation_{int(time.time())}"
        }
        
        await websocket.send(json.dumps(test_message))
        
        # Try to receive a message
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            result["message_received"] = True
            result["response_type"] = response_data.get("type")
        except asyncio.TimeoutError:
            result["message_received"] = False
        
        await websocket.close()
        result["status"] = "passed"
        
        logger.info(f"✅ {endpoint_name}: {connection_time:.3f}s connection, message: {result['message_received']}")
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        logger.error(f"❌ {endpoint_name}: {e}")
    
    result["duration"] = time.time() - start_time
    return result

async def main():
    """Main validation function."""
    print("🔌 WebSocket Validation Test - Phase 3")
    print("=" * 50)
    
    # WebSocket endpoints to test
    endpoints = [
        ("/ws/emoji-rain", "Emoji Rain"),
        ("/ws/observatory", "Observatory Status"),
        ("/ws/anomalies", "Anomaly Detection"),
        ("/ws/doctor-status", "Doctor Status")
    ]
    
    base_urls = [
        ("wss://observatory.nkllon.com", "Production"),
        ("ws://localhost:8888", "Local")
    ]
    
    results = []
    
    for base_url, url_type in base_urls:
        print(f"\n🌐 Testing {url_type} endpoints at {base_url}")
        print("-" * 40)
        
        for endpoint_path, endpoint_name in endpoints:
            full_url = f"{base_url}{endpoint_path}"
            result = await test_websocket_endpoint(full_url, f"{endpoint_name} ({url_type})")
            results.append(result)
    
    # Generate summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = len([r for r in results if r["status"] == "passed"])
    failed_tests = len([r for r in results if r["status"] == "failed"])
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Connection time analysis
    connection_times = [r["connection_time"] for r in results if r["connection_time"] > 0]
    if connection_times:
        max_connection_time = max(connection_times)
        avg_connection_time = sum(connection_times) / len(connection_times)
        print(f"Max Connection Time: {max_connection_time:.3f}s")
        print(f"Avg Connection Time: {avg_connection_time:.3f}s")
        
        # Check requirements
        print("\n🎯 REQUIREMENTS STATUS")
        print("=" * 50)
        
        connection_time_ok = max_connection_time < 2.0
        print(f"{'✅' if connection_time_ok else '❌'} Connection Time < 2s: {max_connection_time:.3f}s")
        
        message_exchange_ok = len([r for r in results if r["message_received"]]) > 0
        print(f"{'✅' if message_exchange_ok else '❌'} Message Exchange: {'Working' if message_exchange_ok else 'Failed'}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"websocket_validation_results_{timestamp}.json"
    
    report = {
        "validation_summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "max_connection_time": max(connection_times) if connection_times else 0,
            "avg_connection_time": sum(connection_times) / len(connection_times) if connection_times else 0,
            "timestamp": datetime.utcnow().isoformat()
        },
        "test_results": results
    }
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {filename}")
    
    # Final status
    if failed_tests == 0:
        print("\n🎉 All WebSocket endpoints validated successfully!")
        return 0
    else:
        print(f"\n⚠️ {failed_tests} tests failed. Check the detailed results.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)