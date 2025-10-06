#!/usr/bin/env python3
"""
Cloudflare Dashboard WebSocket Configuration Script
Phase 2 Implementation - WebSocket Remediation Plan

This script provides comprehensive instructions and automation for configuring
Cloudflare Dashboard WebSocket support for observatory.nkllon.com
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any

class CloudflareWebSocketConfigurator:
    """Configure Cloudflare Dashboard for WebSocket support."""
    
    def __init__(self, domain: str = "observatory.nkllon.com"):
        self.domain = domain
        self.configuration_log = []
        
    def log_configuration(self, step: str, status: str, details: str = ""):
        """Log configuration steps for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "status": status,
            "details": details
        }
        self.configuration_log.append(log_entry)
        print(f"[{status.upper()}] {step}: {details}")
    
    def generate_dashboard_instructions(self) -> Dict[str, Any]:
        """Generate step-by-step Cloudflare Dashboard configuration instructions."""
        
        instructions = {
            "domain": self.domain,
            "configuration_steps": [
                {
                    "step": 1,
                    "title": "Enable WebSocket Support",
                    "location": "Network → WebSockets",
                    "action": "Toggle WebSocket support to ON",
                    "expected_result": "WebSocket support enabled for the domain",
                    "verification": "WebSocket upgrade requests will be proxied correctly"
                },
                {
                    "step": 2,
                    "title": "Configure SSL/TLS Mode",
                    "location": "SSL/TLS → Overview → Encryption Mode",
                    "action": "Set encryption mode to 'Full (strict)'",
                    "expected_result": "End-to-end encryption with certificate validation",
                    "verification": "HTTPS connections use proper certificate chain"
                },
                {
                    "step": 3,
                    "title": "Set Minimum TLS Version",
                    "location": "SSL/TLS → Edge Certificates → TLS Version",
                    "action": "Set minimum TLS version to TLS 1.2 or higher",
                    "expected_result": "Modern TLS encryption support",
                    "verification": "Only secure TLS versions are accepted"
                },
                {
                    "step": 4,
                    "title": "Enable HTTP Strict Transport Security (HSTS)",
                    "location": "SSL/TLS → Edge Certificates → HTTP Strict Transport Security (HSTS)",
                    "action": "Enable HSTS with max-age 31536000 (1 year)",
                    "expected_result": "Forced HTTPS connections",
                    "verification": "Browser will enforce HTTPS for the domain"
                },
                {
                    "step": 5,
                    "title": "Configure Bot Protection",
                    "location": "Security → Bot Fight Mode",
                    "action": "Enable Bot Fight Mode with WebSocket-friendly settings",
                    "expected_result": "Bot protection without blocking WebSocket connections",
                    "verification": "WebSocket connections are not blocked by bot protection"
                }
            ],
            "post_configuration_tests": [
                {
                    "test": "WebSocket Upgrade Test",
                    "command": f"curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://{self.domain}/ws/emoji-rain",
                    "expected_response": "HTTP/1.1 101 Switching Protocols"
                },
                {
                    "test": "SSL/TLS Verification",
                    "command": f"curl -I https://{self.domain}",
                    "expected_response": "HTTP/2 200"
                },
                {
                    "test": "TLS Certificate Check",
                    "command": f"openssl s_client -connect {self.domain}:443 -tls1_2",
                    "expected_response": "Certificate chain validation successful"
                }
            ]
        }
        
        return instructions
    
    def test_current_websocket_status(self) -> Dict[str, Any]:
        """Test current WebSocket endpoint status."""
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "endpoints_tested": [],
            "overall_status": "unknown"
        }
        
        endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        successful_endpoints = 0
        
        for endpoint in endpoints:
            try:
                # Test WebSocket upgrade request
                cmd = [
                    "curl", "-I", "-N",
                    "-H", "Connection: Upgrade",
                    "-H", "Upgrade: websocket", 
                    "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
                    "-H", "Sec-WebSocket-Version: 13",
                    f"https://{self.domain}{endpoint}"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                endpoint_result = {
                    "endpoint": endpoint,
                    "status_code": "unknown",
                    "response_headers": result.stdout,
                    "error": result.stderr if result.stderr else None,
                    "success": False
                }
                
                # Parse HTTP status from response
                if result.stdout:
                    first_line = result.stdout.split('\n')[0]
                    if "HTTP/" in first_line:
                        status_code = first_line.split()[1]
                        endpoint_result["status_code"] = status_code
                        
                        if status_code == "101":
                            endpoint_result["success"] = True
                            successful_endpoints += 1
                            self.log_configuration(f"WebSocket Test {endpoint}", "SUCCESS", f"HTTP/1.1 101 Switching Protocols")
                        elif status_code == "404":
                            self.log_configuration(f"WebSocket Test {endpoint}", "FAILED", "HTTP/2 404 - WebSocket support not enabled")
                        else:
                            self.log_configuration(f"WebSocket Test {endpoint}", "FAILED", f"Unexpected status: {status_code}")
                
                test_results["endpoints_tested"].append(endpoint_result)
                
            except subprocess.TimeoutExpired:
                self.log_configuration(f"WebSocket Test {endpoint}", "TIMEOUT", "Request timed out")
                test_results["endpoints_tested"].append({
                    "endpoint": endpoint,
                    "status_code": "timeout",
                    "success": False,
                    "error": "Request timed out"
                })
            except Exception as e:
                self.log_configuration(f"WebSocket Test {endpoint}", "ERROR", str(e))
                test_results["endpoints_tested"].append({
                    "endpoint": endpoint,
                    "status_code": "error",
                    "success": False,
                    "error": str(e)
                })
        
        # Determine overall status
        if successful_endpoints == len(endpoints):
            test_results["overall_status"] = "fully_functional"
            self.log_configuration("Overall WebSocket Status", "SUCCESS", "All endpoints working correctly")
        elif successful_endpoints > 0:
            test_results["overall_status"] = "partially_functional"
            self.log_configuration("Overall WebSocket Status", "PARTIAL", f"{successful_endpoints}/{len(endpoints)} endpoints working")
        else:
            test_results["overall_status"] = "non_functional"
            self.log_configuration("Overall WebSocket Status", "FAILED", "No WebSocket endpoints working")
        
        return test_results
    
    def validate_ssl_tls_configuration(self) -> Dict[str, Any]:
        """Validate SSL/TLS configuration."""
        
        ssl_results = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "tests": []
        }
        
        # Test 1: Basic HTTPS connectivity
        try:
            cmd = ["curl", "-I", f"https://{self.domain}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            ssl_test = {
                "test": "HTTPS Connectivity",
                "command": " ".join(cmd),
                "success": result.returncode == 0,
                "response": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
            if "HTTP/2 200" in result.stdout or "HTTP/1.1 200" in result.stdout:
                ssl_test["success"] = True
                self.log_configuration("HTTPS Connectivity", "SUCCESS", "HTTPS connection successful")
            else:
                self.log_configuration("HTTPS Connectivity", "FAILED", "HTTPS connection failed")
            
            ssl_results["tests"].append(ssl_test)
            
        except Exception as e:
            self.log_configuration("HTTPS Connectivity", "ERROR", str(e))
            ssl_results["tests"].append({
                "test": "HTTPS Connectivity",
                "success": False,
                "error": str(e)
            })
        
        # Test 2: TLS certificate validation
        try:
            cmd = ["openssl", "s_client", "-connect", f"{self.domain}:443", "-tls1_2"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            ssl_test = {
                "test": "TLS Certificate Validation",
                "command": " ".join(cmd),
                "success": "Verify return code: 0" in result.stdout,
                "response": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
            if ssl_test["success"]:
                self.log_configuration("TLS Certificate", "SUCCESS", "Certificate validation successful")
            else:
                self.log_configuration("TLS Certificate", "FAILED", "Certificate validation failed")
            
            ssl_results["tests"].append(ssl_test)
            
        except Exception as e:
            self.log_configuration("TLS Certificate", "ERROR", str(e))
            ssl_results["tests"].append({
                "test": "TLS Certificate Validation",
                "success": False,
                "error": str(e)
            })
        
        return ssl_results
    
    def generate_configuration_report(self) -> Dict[str, Any]:
        """Generate comprehensive configuration report."""
        
        # Test current status
        websocket_status = self.test_current_websocket_status()
        ssl_status = self.validate_ssl_tls_configuration()
        instructions = self.generate_dashboard_instructions()
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "current_status": {
                "websocket_endpoints": websocket_status,
                "ssl_tls_configuration": ssl_status
            },
            "configuration_instructions": instructions,
            "configuration_log": self.configuration_log,
            "recommendations": []
        }
        
        # Generate recommendations based on current status
        if websocket_status["overall_status"] != "fully_functional":
            report["recommendations"].append({
                "priority": "CRITICAL",
                "action": "Enable WebSocket support in Cloudflare Dashboard",
                "reason": "WebSocket endpoints are not functioning correctly",
                "steps": ["Navigate to Network → WebSockets", "Toggle WebSocket support to ON"]
            })
        
        if not all(test["success"] for test in ssl_status["tests"]):
            report["recommendations"].append({
                "priority": "HIGH", 
                "action": "Configure SSL/TLS settings",
                "reason": "SSL/TLS configuration issues detected",
                "steps": ["Set SSL/TLS mode to Full (strict)", "Enable HSTS", "Set minimum TLS version to 1.2+"]
            })
        
        if not report["recommendations"]:
            report["recommendations"].append({
                "priority": "INFO",
                "action": "Configuration is optimal",
                "reason": "All tests passed successfully",
                "steps": ["Monitor WebSocket performance", "Regular SSL/TLS certificate renewal"]
            })
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save configuration report to file."""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cloudflare_websocket_configuration_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_configuration("Report Generation", "SUCCESS", f"Report saved to {filename}")
        return filename

def main():
    """Main execution function."""
    
    print("🌐 Cloudflare Dashboard WebSocket Configuration")
    print("=" * 50)
    
    configurator = CloudflareWebSocketConfigurator()
    
    # Generate comprehensive report
    report = configurator.generate_configuration_report()
    
    # Save report
    report_file = configurator.save_report(report)
    
    # Display summary
    print(f"\n📊 Configuration Status Summary:")
    print(f"Domain: {report['domain']}")
    print(f"WebSocket Status: {report['current_status']['websocket_endpoints']['overall_status']}")
    print(f"SSL/TLS Status: {'OK' if all(test['success'] for test in report['current_status']['ssl_tls_configuration']['tests']) else 'NEEDS_ATTENTION'}")
    print(f"Recommendations: {len(report['recommendations'])}")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Display critical recommendations
    critical_recs = [r for r in report['recommendations'] if r['priority'] == 'CRITICAL']
    if critical_recs:
        print(f"\n🚨 CRITICAL Actions Required:")
        for rec in critical_recs:
            print(f"  - {rec['action']}: {rec['reason']}")
    
    return report

if __name__ == "__main__":
    main()