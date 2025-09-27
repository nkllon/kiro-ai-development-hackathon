#!/usr/bin/env python3
"""
Simple WebSocket Test for observatory.nkllon.com
"""

import requests
import json
from datetime import datetime, timezone

def test_endpoint(endpoint):
    """Test a single WebSocket endpoint"""
    url = f"https://observatory.nkllon.com{endpoint}"
    
    try:
        # Test HTTP accessibility first
        response = requests.get(url, timeout=10)
        return {
            "endpoint": endpoint,
            "url": url,
            "status_code": response.status_code,
            "accessible": True,
            "error": None
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "url": url,
            "status_code": None,
            "accessible": False,
            "error": str(e)
        }

def main():
    """Main function"""
    print("🧪 WebSocket Endpoint Testing for observatory.nkllon.com")
    print("=" * 60)
    
    endpoints = [
        "/ws/emoji-rain",
        "/ws/observatory", 
        "/ws/anomalies",
        "/ws/doctor-status"
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint}...")
        result = test_endpoint(endpoint)
        results.append(result)
        
        if result["accessible"]:
            print(f"  ✅ Status: {result['status_code']}")
        else:
            print(f"  ❌ Error: {result['error']}")
    
    # Summary
    successful = sum(1 for r in results if r["accessible"])
    total = len(results)
    
    print(f"\n📊 Summary:")
    print(f"  Total endpoints: {total}")
    print(f"  Accessible: {successful}")
    print(f"  Success rate: {successful/total:.1%}")
    
    # Save results
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": "observatory.nkllon.com",
        "endpoints": results,
        "summary": {
            "total": total,
            "successful": successful,
            "success_rate": successful/total
        }
    }
    
    with open("websocket_test_results.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Results saved to: websocket_test_results.json")
    
    return 0 if successful == total else 1

if __name__ == "__main__":
    exit(main())