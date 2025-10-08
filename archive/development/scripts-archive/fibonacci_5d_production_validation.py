#!/usr/bin/env python3
"""
Fibonacci Iteration 5d - Production WebSocket Endpoint Validation
Mission: Validate all WebSocket endpoints in production for observatory.nkllon.com

This script performs comprehensive production validation of all 4 WebSocket endpoints
with detailed performance metrics, security validation, and reliability assessment.
"""

import subprocess
import json
import time
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any
from pathlib import Path

def log_action(task: str, action: str, status: str, details: Dict[str, Any] = None):
    """Log action in JSON format to stdout"""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "action": action,
        "status": status,
        "details": details or {}
    }
    print(json.dumps(log_entry))

def test_websocket_endpoint_production(endpoint: str, base_url: str) -> Dict[str, Any]:
    """Test WebSocket endpoint in production using curl with comprehensive validation"""
    url = f"{base_url}{endpoint}"
    
    # Production WebSocket handshake headers
    headers = [
        "-H", "Connection: Upgrade",
        "-H", "Upgrade: websocket", 
        "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
        "-H", "Sec-WebSocket-Version: 13",
        "-H", "Sec-WebSocket-Protocol: chat, superchat",
        "-H", "Origin: https://observatory.nkllon.com",
        "-H", "User-Agent: Fibonacci-5d-Production-Validator/1.0"
    ]
    
    cmd = ["curl", "-i", "-N", "--max-time", "20", "--connect-timeout", "10"] + headers + [url]
    
    try:
        log_action("5d", f"Testing production WebSocket endpoint {endpoint}", "in_progress", {
            "url": url,
            "command": " ".join(cmd)
        })
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        response_time = (time.time() - start_time) * 1000
        
        # Parse response
        response_lines = result.stdout.split('\n')
        status_line = response_lines[0] if response_lines else ""
        
        # Check for HTTP/1.1 101 Switching Protocols
        handshake_successful = "101 Switching Protocols" in status_line
        connection_established = "101" in status_line
        
        # Look for WebSocket headers in response
        websocket_headers = {}
        for line in response_lines:
            if ":" in line and any(header in line.lower() for header in ["upgrade", "connection", "sec-websocket"]):
                key, value = line.split(":", 1)
                websocket_headers[key.strip()] = value.strip()
        
        # Check for any error responses
        error_detected = any("error" in line.lower() or "404" in line or "500" in line for line in response_lines)
        
        test_result = {
            "endpoint": endpoint,
            "url": url,
            "status_code": status_line.strip(),
            "response_time_ms": response_time,
            "handshake_successful": handshake_successful,
            "connection_established": connection_established,
            "websocket_headers": websocket_headers,
            "response_preview": "\n".join(response_lines[:20]),  # First 20 lines
            "error": None,
            "success": handshake_successful and not error_detected,
            "production_ready": handshake_successful and response_time < 5000 and not error_detected,
            "fibonacci_5d_status": "VALIDATED" if handshake_successful and not error_detected else "FAILED"
        }
        
        if result.returncode != 0:
            test_result["error"] = result.stderr
            test_result["success"] = False
            test_result["production_ready"] = False
            test_result["fibonacci_5d_status"] = "FAILED"
        
        log_action("5d", f"Production WebSocket endpoint {endpoint} tested", "completed", {
            "handshake_successful": handshake_successful,
            "response_time_ms": response_time,
            "status_code": status_line.strip(),
            "production_ready": test_result["production_ready"],
            "fibonacci_5d_status": test_result["fibonacci_5d_status"]
        })
        
        return test_result
        
    except subprocess.TimeoutExpired:
        log_action("5d", f"Production WebSocket endpoint {endpoint} timeout", "error", {
            "url": url,
            "timeout": "25 seconds"
        })
        return {
            "endpoint": endpoint,
            "url": url,
            "status_code": "TIMEOUT",
            "response_time_ms": 25000,
            "handshake_successful": False,
            "connection_established": False,
            "websocket_headers": {},
            "response_preview": "",
            "error": "Connection timeout after 25 seconds",
            "success": False,
            "production_ready": False,
            "fibonacci_5d_status": "TIMEOUT"
        }
    except Exception as e:
        log_action("5d", f"Production WebSocket endpoint {endpoint} error", "error", {
            "url": url,
            "error": str(e)
        })
        return {
            "endpoint": endpoint,
            "url": url,
            "status_code": "ERROR",
            "response_time_ms": 0,
            "handshake_successful": False,
            "connection_established": False,
            "websocket_headers": {},
            "response_preview": "",
            "error": str(e),
            "success": False,
            "production_ready": False,
            "fibonacci_5d_status": "ERROR"
        }

def test_ssl_certificate_production(domain: str) -> Dict[str, Any]:
    """Test SSL certificate validity in production"""
    try:
        cmd = ["openssl", "s_client", "-connect", f"{domain}:443", "-servername", domain]
        result = subprocess.run(cmd, input="", capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # Extract certificate dates
            cert_info = result.stdout
            valid_from = None
            valid_to = None
            
            for line in cert_info.split('\n'):
                if "notBefore" in line:
                    valid_from = line.split("=", 1)[1].strip()
                elif "notAfter" in line:
                    valid_to = line.split("=", 1)[1].strip()
            
            return {
                "domain": domain,
                "ssl_valid": True,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "error": None,
                "production_ready": True,
                "fibonacci_5d_status": "VALIDATED"
            }
        else:
            return {
                "domain": domain,
                "ssl_valid": False,
                "valid_from": None,
                "valid_to": None,
                "error": result.stderr,
                "production_ready": False,
                "fibonacci_5d_status": "FAILED"
            }
    except Exception as e:
        return {
            "domain": domain,
            "ssl_valid": False,
            "valid_from": None,
            "valid_to": None,
            "error": str(e),
            "production_ready": False,
            "fibonacci_5d_status": "ERROR"
        }

def test_http_connectivity_production(domain: str) -> Dict[str, Any]:
    """Test HTTP connectivity in production"""
    try:
        cmd = ["curl", "-I", f"https://{domain}/", "--max-time", "10", "--connect-timeout", "5"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        response_text = result.stdout
        http_accessible = "HTTP/" in response_text and result.returncode == 0
        
        return {
            "domain": domain,
            "http_accessible": http_accessible,
            "response_preview": response_text[:200],
            "error": None,
            "production_ready": http_accessible,
            "fibonacci_5d_status": "VALIDATED" if http_accessible else "FAILED"
        }
    except Exception as e:
        return {
            "domain": domain,
            "http_accessible": False,
            "response_preview": "",
            "error": str(e),
            "production_ready": False,
            "fibonacci_5d_status": "ERROR"
        }

def main():
    """Main function - Execute Fibonacci iteration 5d production WebSocket validation"""
    log_action("5d", "Fibonacci iteration 5d production WebSocket validation started", "in_progress", {
        "target": "observatory.nkllon.com",
        "objective": "Validate all 4 WebSocket endpoints in production environment",
        "expected_result": "All WebSocket endpoints validated and confirmed operational in production"
    })
    
    # Mission configuration
    endpoints = [
        "/ws/emoji-rain",
        "/ws/observatory", 
        "/ws/anomalies",
        "/ws/doctor-status"
    ]
    
    production_base_url = "https://observatory.nkllon.com"
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mission": "Fibonacci Iteration 5d - Production WebSocket Validation",
        "target": "observatory.nkllon.com",
        "production_tests": [],
        "ssl_test": {},
        "http_test": {},
        "summary": {},
        "success_criteria": {
            "all_endpoints_production_ready": False,
            "websocket_handshake_success": False,
            "ssl_certificate_valid": False,
            "http_connectivity_confirmed": False,
            "production_performance_acceptable": False
        }
    }
    
    # Test 1: SSL Certificate Validation
    log_action("5d", "Testing SSL certificate in production", "in_progress", {
        "domain": "observatory.nkllon.com"
    })
    ssl_result = test_ssl_certificate_production("observatory.nkllon.com")
    results["ssl_test"] = ssl_result
    log_action("5d", "SSL certificate test completed", "completed", ssl_result)
    
    # Test 2: HTTP Connectivity Check
    log_action("5d", "Testing HTTP connectivity in production", "in_progress", {
        "domain": "observatory.nkllon.com"
    })
    http_result = test_http_connectivity_production("observatory.nkllon.com")
    results["http_test"] = http_result
    log_action("5d", "HTTP connectivity test completed", "completed", http_result)
    
    # Test 3: Production WebSocket Endpoints
    log_action("5d", "Testing production WebSocket endpoints", "in_progress", {
        "base_url": production_base_url,
        "endpoints": endpoints
    })
    
    production_success_count = 0
    production_ready_count = 0
    validated_count = 0
    total_response_time = 0
    
    for endpoint in endpoints:
        result = test_websocket_endpoint_production(endpoint, production_base_url)
        results["production_tests"].append(result)
        if result["success"]:
            production_success_count += 1
        if result["production_ready"]:
            production_ready_count += 1
        if result["fibonacci_5d_status"] == "VALIDATED":
            validated_count += 1
        total_response_time += result["response_time_ms"]
    
    avg_response_time = total_response_time / len(endpoints) if endpoints else 0
    
    log_action("5d", "Production WebSocket endpoints tested", "completed", {
        "successful": production_success_count,
        "production_ready": production_ready_count,
        "validated": validated_count,
        "total": len(endpoints),
        "avg_response_time_ms": avg_response_time
    })
    
    # Calculate success criteria
    all_endpoints_success = production_success_count == len(endpoints)
    all_endpoints_production_ready = production_ready_count == len(endpoints)
    all_endpoints_validated = validated_count == len(endpoints)
    ssl_valid = ssl_result.get("ssl_valid", False)
    http_accessible = http_result.get("http_accessible", False)
    performance_acceptable = avg_response_time < 3000  # < 3 seconds average
    
    results["success_criteria"] = {
        "all_endpoints_production_ready": all_endpoints_production_ready,
        "websocket_handshake_success": all_endpoints_success,
        "ssl_certificate_valid": ssl_valid,
        "http_connectivity_confirmed": http_accessible,
        "production_performance_acceptable": performance_acceptable
    }
    
    # Generate summary
    results["summary"] = {
        "total_endpoints": len(endpoints),
        "production_successful": production_success_count,
        "production_ready": production_ready_count,
        "fibonacci_5d_validated": validated_count,
        "production_success_rate": production_success_count / len(endpoints),
        "production_ready_rate": production_ready_count / len(endpoints),
        "validation_rate": validated_count / len(endpoints),
        "avg_response_time_ms": avg_response_time,
        "ssl_valid": ssl_valid,
        "http_accessible": http_accessible,
        "mission_status": "PASS" if all_endpoints_validated else "FAIL",
        "success_criteria_met": sum(results["success_criteria"].values()),
        "total_criteria": len(results["success_criteria"])
    }
    
    # Generate recommendations
    recommendations = []
    if not all_endpoints_validated:
        recommendations.append("Review production WebSocket endpoint configuration")
        recommendations.append("Check Cloudflare tunnel WebSocket settings")
        recommendations.append("Verify Observatory server WebSocket handlers in production")
        recommendations.append("Ensure bot protection settings allow WebSocket connections")
    
    if not ssl_valid:
        recommendations.append("Check SSL certificate configuration in production")
    
    if not http_accessible:
        recommendations.append("Check HTTP connectivity and DNS resolution")
    
    if not performance_acceptable:
        recommendations.append("Optimize WebSocket response times for production")
    
    recommendations.extend([
        "Implement continuous production WebSocket monitoring",
        "Set up automated alerts for production WebSocket failures",
        "Consider WebSocket-specific production optimizations",
        "Establish production performance baselines",
        "Conduct regular Fibonacci iteration validation cycles"
    ])
    
    results["recommendations"] = recommendations
    
    # Final mission completion log
    log_action("5d", "Fibonacci iteration 5d production WebSocket validation completed", "completed", {
        "mission_status": results["summary"]["mission_status"],
        "validation_rate": results["summary"]["validation_rate"],
        "success_criteria_met": f"{results['summary']['success_criteria_met']}/{results['summary']['total_criteria']}"
    })
    
    # Print mission report
    print("\n" + "="*80)
    print("🚀 FIBONACCI ITERATION 5D - PRODUCTION WEBSOCKET VALIDATION REPORT")
    print("="*80)
    print(f"🎯 Target: {results['target']}")
    print(f"📊 Mission Status: {results['summary']['mission_status']}")
    print(f"🌐 Validation Rate: {results['summary']['validation_rate']:.1%}")
    print(f"⚡ Average Response Time: {results['summary']['avg_response_time_ms']:.1f}ms")
    print(f"🔗 Endpoints Tested: {results['summary']['total_endpoints']}")
    print(f"✅ Success Criteria Met: {results['summary']['success_criteria_met']}/{results['summary']['total_criteria']}")
    
    print("\n📋 Production Endpoint Results:")
    for i, endpoint in enumerate(endpoints):
        result = results["production_tests"][i]
        success_emoji = "✅" if result["success"] else "❌"
        ready_emoji = "🚀" if result["production_ready"] else "⚠️"
        validated_emoji = "🎯" if result["fibonacci_5d_status"] == "VALIDATED" else "❌"
        print(f"  {endpoint}:")
        print(f"    Status:     {success_emoji} {result['status_code']}")
        print(f"    Production: {ready_emoji} {'Ready' if result['production_ready'] else 'Not Ready'}")
        print(f"    Fibonacci:  {validated_emoji} {result['fibonacci_5d_status']}")
        print(f"    Response:   {result['response_time_ms']:.1f}ms")
        if result.get("error"):
            print(f"    Error:      {result['error']}")
    
    print("\n🔒 Infrastructure Status:")
    print(f"  SSL Certificate: {'✅ Valid' if results['summary']['ssl_valid'] else '❌ Invalid'}")
    print(f"  HTTP Connectivity: {'✅ Accessible' if results['summary']['http_accessible'] else '❌ Not Accessible'}")
    
    print("\n🎯 Success Criteria:")
    for criterion, met in results["success_criteria"].items():
        emoji = "✅" if met else "❌"
        print(f"  {emoji} {criterion.replace('_', ' ').title()}")
    
    print("\n💡 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*80)
    
    # Save detailed report
    report_file = Path("logs/fibonacci_5d_production_validation_report.json")
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_file}")
    
    return 0 if results['summary']['mission_status'] == 'PASS' else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Mission interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Mission failed with error: {e}")
        sys.exit(1)