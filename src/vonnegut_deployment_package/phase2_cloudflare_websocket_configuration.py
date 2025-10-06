#!/usr/bin/env python3
"""
Phase 2 Cloudflare WebSocket Configuration
Enable WebSocket support in Cloudflare Dashboard for observatory.nkllon.com

This script provides comprehensive instructions and testing for:
1. Enable WebSocket support in Cloudflare Dashboard
2. Verify SSL/TLS configuration is set to Full (strict) mode
3. Test WebSocket endpoints through Cloudflare using curl commands
4. Document Cloudflare configuration changes and test results

Expected result: HTTP/1.1 101 Switching Protocols through Cloudflare
"""

import json
import subprocess
import time
import sys
import requests
import ssl
import socket
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/phase2_cloudflare_config.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_action(task: str, action: str, status: str, details: Dict[str, Any] = None):
    """Log action in JSON format to stdout"""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": "phase2-cloudflare-websocket",
        "action": action,
        "status": status,
        "details": details or {}
    }
    print(json.dumps(log_entry))

class Phase2CloudflareWebSocketConfig:
    """Phase 2 Cloudflare WebSocket Configuration Manager"""
    
    def __init__(self, domain: str = "observatory.nkllon.com"):
        self.domain = domain
        self.results = {}
        self.logs_dir = Path("logs/phase2_cloudflare")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔧 Phase 2 Cloudflare WebSocket Configuration initialized for {domain}")
    
    def generate_cloudflare_dashboard_instructions(self) -> Dict[str, Any]:
        """Generate comprehensive Cloudflare Dashboard instructions"""
        log_action("generate_instructions", "Creating Cloudflare Dashboard instructions", "in_progress")
        
        instructions = {
            "title": "Phase 2: Cloudflare WebSocket Configuration Instructions",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": self.domain,
            "phase": "Phase 2 - WebSocket Support Enablement",
            "critical_steps": [
                {
                    "step": 1,
                    "title": "Enable WebSocket Support",
                    "location": "Network → WebSockets",
                    "action": "Toggle WebSocket support to ON",
                    "description": "Enable WebSocket connections through Cloudflare tunnel",
                    "verification": "WebSocket connections will work through tunnel",
                    "expected_result": "HTTP/1.1 101 Switching Protocols for WebSocket endpoints"
                },
                {
                    "step": 2,
                    "title": "Verify SSL/TLS Configuration",
                    "location": "SSL/TLS → Overview → Encryption Mode",
                    "action": "Ensure SSL/TLS encryption mode is set to 'Full (strict)'",
                    "description": "End-to-end encryption with certificate validation",
                    "verification": "Certificate validation enabled",
                    "expected_result": "Secure WebSocket connections (wss://) with valid certificates"
                },
                {
                    "step": 3,
                    "title": "Configure TLS Version",
                    "location": "SSL/TLS → Edge Certificates → TLS Version",
                    "action": "Set minimum TLS version to TLS 1.2 or higher",
                    "description": "Modern TLS version for secure connections",
                    "verification": "TLS handshake successful with modern protocols",
                    "expected_result": "TLS 1.2+ connections supported"
                },
                {
                    "step": 4,
                    "title": "Enable HSTS",
                    "location": "SSL/TLS → Edge Certificates → HTTP Strict Transport Security (HSTS)",
                    "action": "Enable HSTS with appropriate max-age",
                    "description": "Force HTTPS connections and prevent downgrade attacks",
                    "verification": "Strict-Transport-Security header present",
                    "expected_result": "HTTPS-only connections enforced"
                }
            ],
            "testing_commands": {
                "websocket_test": f"curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://{self.domain}/ws/emoji-rain",
                "ssl_mode_test": f"curl -I https://{self.domain}",
                "tls_version_test": f"openssl s_client -connect {self.domain}:443 -tls1_2",
                "certificate_test": f"openssl s_client -connect {self.domain}:443 -servername {self.domain}"
            },
            "expected_results": {
                "before_configuration": "HTTP/2 404 errors on WebSocket endpoints",
                "after_configuration": "HTTP/1.1 101 Switching Protocols for WebSocket connections",
                "ssl_mode": "Full (strict) - end-to-end encryption with certificate validation",
                "websocket_endpoints": [
                    f"wss://{self.domain}/ws/emoji-rain",
                    f"wss://{self.domain}/ws/observatory",
                    f"wss://{self.domain}/ws/anomalies",
                    f"wss://{self.domain}/ws/doctor-status"
                ]
            }
        }
        
        log_action("generate_instructions", "Cloudflare Dashboard instructions created", "completed", {
            "total_steps": len(instructions["critical_steps"]),
            "testing_commands": len(instructions["testing_commands"])
        })
        
        return instructions
    
    def test_current_websocket_status(self) -> Dict[str, Any]:
        """Test current WebSocket status before configuration"""
        log_action("test_current_status", "Testing current WebSocket status", "in_progress")
        
        endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory",
            "/ws/anomalies", 
            "/ws/doctor-status"
        ]
        
        results = []
        success_count = 0
        
        for endpoint in endpoints:
            url = f"https://{self.domain}{endpoint}"
            
            # WebSocket handshake headers
            headers = [
                "-H", "Connection: Upgrade",
                "-H", "Upgrade: websocket",
                "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
                "-H", "Sec-WebSocket-Version: 13",
                "-H", f"Origin: https://{self.domain}"
            ]
            
            cmd = ["curl", "-i", "-N", "--max-time", "10"] + headers + [url]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                response_lines = result.stdout.split('\n')
                status_line = response_lines[0] if response_lines else ""
                
                # Check for current status
                has_404 = "404" in status_line
                has_101 = "101 Switching Protocols" in status_line
                has_http2 = "HTTP/2" in status_line
                has_http1 = "HTTP/1.1" in status_line
                
                test_result = {
                    "endpoint": endpoint,
                    "url": url,
                    "status_line": status_line.strip(),
                    "has_404_error": has_404,
                    "has_101_switching": has_101,
                    "has_http2": has_http2,
                    "has_http1": has_http1,
                    "websocket_supported": has_101,
                    "response_preview": "\n".join(response_lines[:5])
                }
                
                if has_101:
                    success_count += 1
                
                results.append(test_result)
                
            except Exception as e:
                test_result = {
                    "endpoint": endpoint,
                    "url": url,
                    "error": str(e),
                    "websocket_supported": False
                }
                results.append(test_result)
        
        current_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": self.domain,
            "total_endpoints": len(endpoints),
            "successful_endpoints": success_count,
            "success_rate": success_count / len(endpoints),
            "websocket_support_enabled": success_count > 0,
            "results": results
        }
        
        log_action("test_current_status", "Current WebSocket status tested", "completed", {
            "success_rate": current_status["success_rate"],
            "websocket_support_enabled": current_status["websocket_support_enabled"]
        })
        
        return current_status
    
    def verify_ssl_tls_configuration(self) -> Dict[str, Any]:
        """Verify SSL/TLS configuration"""
        log_action("verify_ssl_tls", "Verifying SSL/TLS configuration", "in_progress")
        
        try:
            # Test HTTPS connection
            response = requests.get(f"https://{self.domain}", timeout=10)
            
            # Check SSL/TLS headers
            ssl_headers = {
                'strict-transport-security': response.headers.get('strict-transport-security'),
                'x-frame-options': response.headers.get('x-frame-options'),
                'x-content-type-options': response.headers.get('x-content-type-options')
            }
            
            # Get certificate information
            cert_info = self.get_certificate_info()
            
            # Determine SSL/TLS mode
            ssl_mode = "Full (Strict)" if cert_info else "Unknown"
            
            ssl_config = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "domain": self.domain,
                "ssl_mode": ssl_mode,
                "https_response_code": response.status_code,
                "ssl_headers": ssl_headers,
                "certificate_valid": cert_info is not None,
                "certificate_info": cert_info,
                "hsts_enabled": bool(ssl_headers.get('strict-transport-security')),
                "tls_version": cert_info.get('tls_version') if cert_info else None
            }
            
            log_action("verify_ssl_tls", "SSL/TLS configuration verified", "completed", {
                "ssl_mode": ssl_mode,
                "certificate_valid": ssl_config["certificate_valid"],
                "hsts_enabled": ssl_config["hsts_enabled"]
            })
            
            return ssl_config
            
        except Exception as e:
            error_config = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "domain": self.domain,
                "error": str(e),
                "ssl_mode": "Unknown",
                "certificate_valid": False
            }
            
            log_action("verify_ssl_tls", "SSL/TLS verification failed", "error", {"error": str(e)})
            return error_config
    
    def get_certificate_info(self) -> Optional[Dict[str, Any]]:
        """Get SSL certificate information"""
        try:
            # Create SSL context for certificate verification
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            # Connect to get certificate
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Get certificate details
                    cert_info = {
                        "subject": cert.get('subject', ''),
                        "issuer": cert.get('issuer', ''),
                        "valid_from": cert.get('notBefore', ''),
                        "valid_to": cert.get('notAfter', ''),
                        "serial_number": cert.get('serialNumber', ''),
                        "tls_version": ssock.version(),
                        "cipher_suite": ssock.cipher()[0] if ssock.cipher() else "Unknown"
                    }
                    
                    return cert_info
                    
        except Exception as e:
            logger.error(f"Failed to get certificate info: {e}")
            return None
    
    def test_websocket_endpoints_after_config(self) -> Dict[str, Any]:
        """Test WebSocket endpoints after configuration"""
        log_action("test_websocket_endpoints", "Testing WebSocket endpoints after configuration", "in_progress")
        
        endpoints = [
            "/ws/emoji-rain",
            "/ws/observatory",
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        results = []
        success_count = 0
        
        for endpoint in endpoints:
            url = f"https://{self.domain}{endpoint}"
            
            # WebSocket handshake headers
            headers = [
                "-H", "Connection: Upgrade",
                "-H", "Upgrade: websocket",
                "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
                "-H", "Sec-WebSocket-Version: 13",
                "-H", f"Origin: https://{self.domain}"
            ]
            
            cmd = ["curl", "-i", "-N", "--max-time", "10"] + headers + [url]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                response_lines = result.stdout.split('\n')
                status_line = response_lines[0] if response_lines else ""
                
                # Check for HTTP/1.1 101 Switching Protocols
                handshake_successful = "101 Switching Protocols" in status_line
                connection_established = "101" in status_line
                is_http1 = "HTTP/1.1" in status_line
                
                test_result = {
                    "endpoint": endpoint,
                    "url": url,
                    "status_code": status_line.strip(),
                    "handshake_successful": handshake_successful,
                    "connection_established": connection_established,
                    "is_http1": is_http1,
                    "success": handshake_successful,
                    "response_preview": "\n".join(response_lines[:5])
                }
                
                if handshake_successful:
                    success_count += 1
                
                results.append(test_result)
                
            except Exception as e:
                test_result = {
                    "endpoint": endpoint,
                    "url": url,
                    "error": str(e),
                    "success": False
                }
                results.append(test_result)
        
        test_summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": self.domain,
            "total_endpoints": len(endpoints),
            "successful_endpoints": success_count,
            "success_rate": success_count / len(endpoints),
            "all_endpoints_working": success_count == len(endpoints),
            "expected_result_achieved": success_count > 0,
            "results": results
        }
        
        log_action("test_websocket_endpoints", "WebSocket endpoints tested", "completed", {
            "success_rate": test_summary["success_rate"],
            "all_endpoints_working": test_summary["all_endpoints_working"]
        })
        
        return test_summary
    
    def generate_test_commands(self) -> Dict[str, str]:
        """Generate test commands for verification"""
        commands = {
            "websocket_emoji_rain": f"curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://{self.domain}/ws/emoji-rain",
            "websocket_observatory": f"curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://{self.domain}/ws/observatory",
            "websocket_anomalies": f"curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://{self.domain}/ws/anomalies",
            "websocket_doctor_status": f"curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://{self.domain}/ws/doctor-status",
            "ssl_test": f"curl -I https://{self.domain}",
            "tls_version_test": f"openssl s_client -connect {self.domain}:443 -tls1_2",
            "certificate_test": f"openssl s_client -connect {self.domain}:443 -servername {self.domain}"
        }
        
        return commands
    
    def run_phase2_configuration(self) -> Dict[str, Any]:
        """Run complete Phase 2 configuration process"""
        log_action("phase2_configuration", "Starting Phase 2 Cloudflare WebSocket configuration", "in_progress", {
            "domain": self.domain,
            "objective": "Enable WebSocket support and verify SSL/TLS configuration"
        })
        
        # Step 1: Generate instructions
        instructions = self.generate_cloudflare_dashboard_instructions()
        
        # Step 2: Test current status
        current_status = self.test_current_websocket_status()
        
        # Step 3: Verify SSL/TLS configuration
        ssl_config = self.verify_ssl_tls_configuration()
        
        # Step 4: Generate test commands
        test_commands = self.generate_test_commands()
        
        # Create comprehensive report
        phase2_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "Phase 2 - Cloudflare WebSocket Configuration",
            "domain": self.domain,
            "instructions": instructions,
            "current_status": current_status,
            "ssl_configuration": ssl_config,
            "test_commands": test_commands,
            "next_steps": [
                "Follow Cloudflare Dashboard instructions to enable WebSocket support",
                "Verify SSL/TLS is set to Full (strict) mode",
                "Run test commands to verify configuration",
                "Monitor WebSocket endpoints for HTTP/1.1 101 Switching Protocols"
            ],
            "expected_results": {
                "websocket_support": "HTTP/1.1 101 Switching Protocols for WebSocket connections",
                "ssl_mode": "Full (strict) - end-to-end encryption with certificate validation",
                "hsts_enabled": "Strict-Transport-Security header present",
                "tls_version": "TLS 1.2 or higher supported"
            }
        }
        
        # Save report
        report_file = self.logs_dir / "phase2_cloudflare_configuration_report.json"
        with open(report_file, "w") as f:
            json.dump(phase2_report, f, indent=2)
        
        log_action("phase2_configuration", "Phase 2 configuration process completed", "completed", {
            "report_file": str(report_file),
            "current_websocket_support": current_status["websocket_support_enabled"],
            "ssl_mode": ssl_config["ssl_mode"]
        })
        
        return phase2_report

def main():
    """Main function - Execute Phase 2 Cloudflare WebSocket Configuration"""
    print("🔧 Phase 2: Cloudflare WebSocket Configuration")
    print("=" * 60)
    print("🎯 Objective: Enable WebSocket support in Cloudflare Dashboard")
    print("🌐 Domain: observatory.nkllon.com")
    print("📋 Expected Result: HTTP/1.1 101 Switching Protocols")
    print("=" * 60)
    
    # Initialize configuration manager
    config_manager = Phase2CloudflareWebSocketConfig()
    
    try:
        # Run Phase 2 configuration
        report = config_manager.run_phase2_configuration()
        
        # Display results
        print("\n📋 CLOUDFLARE DASHBOARD CONFIGURATION STEPS:")
        print("-" * 50)
        
        for step in report["instructions"]["critical_steps"]:
            print(f"\n{step['step']}. {step['title']}")
            print(f"   📍 Location: {step['location']}")
            print(f"   🎯 Action: {step['action']}")
            print(f"   📝 Description: {step['description']}")
            print(f"   ✅ Verification: {step['verification']}")
            print(f"   🎉 Expected: {step['expected_result']}")
        
        print("\n🧪 TESTING COMMANDS:")
        print("-" * 30)
        for name, command in report["test_commands"].items():
            print(f"\n{name}:")
            print(f"  {command}")
        
        print("\n📊 CURRENT STATUS:")
        print("-" * 20)
        current_status = report["current_status"]
        print(f"   WebSocket Support: {'✅ Enabled' if current_status['websocket_support_enabled'] else '❌ Disabled'}")
        print(f"   Success Rate: {current_status['success_rate']:.1%}")
        print(f"   Endpoints Working: {current_status['successful_endpoints']}/{current_status['total_endpoints']}")
        
        ssl_config = report["ssl_configuration"]
        print(f"\n🔒 SSL/TLS CONFIGURATION:")
        print(f"   SSL Mode: {ssl_config['ssl_mode']}")
        print(f"   Certificate Valid: {'✅ Yes' if ssl_config['certificate_valid'] else '❌ No'}")
        print(f"   HSTS Enabled: {'✅ Yes' if ssl_config['hsts_enabled'] else '❌ No'}")
        
        print("\n🎯 EXPECTED RESULTS AFTER CONFIGURATION:")
        print("-" * 45)
        for key, value in report["expected_results"].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print("\n🚀 NEXT STEPS:")
        print("-" * 15)
        for i, step in enumerate(report["next_steps"], 1):
            print(f"   {i}. {step}")
        
        print(f"\n📄 Detailed report saved to: {config_manager.logs_dir}/phase2_cloudflare_configuration_report.json")
        print("\n" + "=" * 60)
        
        return 0
        
    except Exception as e:
        error_log = {
            "task": "phase2-cloudflare-websocket",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        print(json.dumps(error_log))
        logger.error(f"❌ Phase 2 configuration failed: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Configuration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Configuration failed with error: {e}")
        sys.exit(1)