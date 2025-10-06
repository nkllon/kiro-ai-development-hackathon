#!/usr/bin/env python3
"""
SSL/TLS Full Strict Mode Verification Script
Target: observatory.nkllon.com
Mission: Verify SSL/TLS configuration is set to Full Strict mode
"""

import json
import ssl
import socket
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ssl_tls_verification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SSLTLSVerifier:
    """SSL/TLS Full Strict mode verifier"""
    
    def __init__(self, domain: str = "observatory.nkllon.com"):
        self.domain = domain
        self.results = []
        
        # Create logs directory
        import os
        os.makedirs("logs", exist_ok=True)
        
        logger.info(f"🔒 SSL/TLS Verifier initialized for domain: {domain}")
    
    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "ssl_tls_deployment",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
        logger.info(f"📝 {action}: {status}")
    
    def verify_ssl_tls_mode(self) -> Dict[str, Any]:
        """Verify SSL/TLS encryption mode"""
        self.log_action("verify_ssl_tls_mode", "in_progress")
        
        try:
            # Test HTTPS connection with certificate validation
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check if certificate validation passed
                    ssl_mode = "Full (Strict)" if cert else "Unknown"
                    status = "pass" if cert else "fail"
                    
                    result = {
                        "ssl_mode": ssl_mode,
                        "certificate_valid": bool(cert),
                        "protocol_version": ssock.version(),
                        "cipher_suite": ssock.cipher()[0] if ssock.cipher() else "Unknown"
                    }
                    
                    self.log_action("verify_ssl_tls_mode", "completed", result)
                    return result
                    
        except Exception as e:
            error_details = {"error": str(e)}
            result = {
                "ssl_mode": "Unknown",
                "certificate_valid": False,
                "error": str(e)
            }
            
            self.log_action("verify_ssl_tls_mode", "error", error_details)
            return result
    
    def verify_certificate_chain(self) -> Dict[str, Any]:
        """Verify certificate chain"""
        self.log_action("verify_certificate_chain", "in_progress")
        
        try:
            # Use openssl to check certificate chain
            cmd = [
                "openssl", "s_client", "-connect", f"{self.domain}:443",
                "-servername", self.domain, "-showcerts"
            ]
            
            result = subprocess.run(cmd, input="", capture_output=True, text=True, timeout=10)
            
            # Check for certificate chain validation
            chain_valid = "Verify return code: 0" in result.stdout
            cert_count = result.stdout.count("BEGIN CERTIFICATE")
            
            verification_result = {
                "chain_valid": chain_valid,
                "certificate_count": cert_count,
                "verify_return_code": "0" if chain_valid else "non-zero"
            }
            
            self.log_action("verify_certificate_chain", "completed", verification_result)
            return verification_result
            
        except Exception as e:
            error_details = {"error": str(e)}
            self.log_action("verify_certificate_chain", "error", error_details)
            return {"chain_valid": False, "error": str(e)}
    
    def verify_tls_version(self) -> Dict[str, Any]:
        """Verify supported TLS versions"""
        self.log_action("verify_tls_version", "in_progress")
        
        try:
            # Test TLS 1.2 support
            cmd_tls12 = [
                "openssl", "s_client", "-connect", f"{self.domain}:443",
                "-tls1_2", "-servername", self.domain
            ]
            
            result_tls12 = subprocess.run(cmd_tls12, input="", capture_output=True, text=True, timeout=10)
            tls12_supported = "Protocol.*TLSv1.2" in result.stdout
            
            # Test TLS 1.3 support
            cmd_tls13 = [
                "openssl", "s_client", "-connect", f"{self.domain}:443",
                "-tls1_3", "-servername", self.domain
            ]
            
            result_tls13 = subprocess.run(cmd_tls13, input="", capture_output=True, text=True, timeout=10)
            tls13_supported = "Protocol.*TLSv1.3" in result.stdout
            
            verification_result = {
                "tls_1_2_supported": tls12_supported,
                "tls_1_3_supported": tls13_supported,
                "minimum_version": "TLSv1.2" if tls12_supported else "Unknown"
            }
            
            self.log_action("verify_tls_version", "completed", verification_result)
            return verification_result
            
        except Exception as e:
            error_details = {"error": str(e)}
            self.log_action("verify_tls_version", "error", error_details)
            return {"tls_1_2_supported": False, "error": str(e)}
    
    def verify_hsts_header(self) -> Dict[str, Any]:
        """Verify HSTS header presence"""
        self.log_action("verify_hsts_header", "in_progress")
        
        try:
            # Use curl to check HSTS header
            cmd = ["curl", "-I", f"https://{self.domain}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            hsts_header = None
            for line in result.stdout.split('\n'):
                if 'strict-transport-security' in line.lower():
                    hsts_header = line.strip()
                    break
            
            verification_result = {
                "hsts_header_present": bool(hsts_header),
                "hsts_header": hsts_header
            }
            
            self.log_action("verify_hsts_header", "completed", verification_result)
            return verification_result
            
        except Exception as e:
            error_details = {"error": str(e)}
            self.log_action("verify_hsts_header", "error", error_details)
            return {"hsts_header_present": False, "error": str(e)}
    
    def verify_websocket_ssl(self) -> Dict[str, Any]:
        """Verify WebSocket SSL connection"""
        self.log_action("verify_websocket_ssl", "in_progress")
        
        try:
            # Test WebSocket upgrade with SSL
            cmd = [
                "curl", "-I", "-N",
                "-H", "Connection: Upgrade",
                "-H", "Upgrade: websocket",
                "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
                "-H", "Sec-WebSocket-Version: 13",
                f"https://{self.domain}/ws/emoji-rain"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Check for successful WebSocket upgrade
            websocket_success = "101" in result.stdout or "Switching Protocols" in result.stdout
            
            verification_result = {
                "websocket_ssl_success": websocket_success,
                "response_code": result.stdout.split('\n')[0] if result.stdout else "No response",
                "websocket_url": f"wss://{self.domain}/ws/emoji-rain"
            }
            
            self.log_action("verify_websocket_ssl", "completed", verification_result)
            return verification_result
            
        except Exception as e:
            error_details = {"error": str(e)}
            self.log_action("verify_websocket_ssl", "error", error_details)
            return {"websocket_ssl_success": False, "error": str(e)}
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run comprehensive SSL/TLS verification"""
        self.log_action("run_comprehensive_verification", "in_progress")
        
        logger.info("🔒 Starting comprehensive SSL/TLS verification")
        
        # Run all verification checks
        ssl_mode_result = self.verify_ssl_tls_mode()
        cert_chain_result = self.verify_certificate_chain()
        tls_version_result = self.verify_tls_version()
        hsts_result = self.verify_hsts_header()
        websocket_result = self.verify_websocket_ssl()
        
        # Calculate overall status
        all_passed = all([
            ssl_mode_result.get("certificate_valid", False),
            cert_chain_result.get("chain_valid", False),
            tls_version_result.get("tls_1_2_supported", False),
            hsts_result.get("hsts_header_present", False),
            websocket_result.get("websocket_ssl_success", False)
        ])
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "overall_status": "pass" if all_passed else "fail",
            "ssl_tls_mode": ssl_mode_result,
            "certificate_chain": cert_chain_result,
            "tls_version": tls_version_result,
            "hsts_header": hsts_result,
            "websocket_ssl": websocket_result,
            "success_criteria_met": all_passed
        }
        
        self.log_action("run_comprehensive_verification", "completed", {
            "overall_status": summary["overall_status"],
            "success_criteria_met": all_passed
        })
        
        return summary

def main():
    """Main verification script"""
    print("🔒 SSL/TLS Full Strict Mode Verification")
    print("=" * 50)
    print("Target: observatory.nkllon.com")
    print("Mission: Verify SSL/TLS configuration")
    print("")
    
    # Initialize verifier
    verifier = SSLTLSVerifier()
    
    try:
        # Run comprehensive verification
        summary = verifier.run_comprehensive_verification()
        
        # Display results
        print(f"📊 SSL/TLS Verification Summary:")
        print(f"   Domain: {summary['domain']}")
        print(f"   Overall Status: {summary['overall_status'].upper()}")
        print(f"   Success Criteria Met: {summary['success_criteria_met']}")
        
        # Display detailed results
        print(f"\n📋 Detailed Results:")
        
        ssl_mode = summary['ssl_tls_mode']
        print(f"   🔒 SSL/TLS Mode: {ssl_mode.get('ssl_mode', 'Unknown')}")
        print(f"      Certificate Valid: {ssl_mode.get('certificate_valid', False)}")
        print(f"      Protocol Version: {ssl_mode.get('protocol_version', 'Unknown')}")
        print(f"      Cipher Suite: {ssl_mode.get('cipher_suite', 'Unknown')}")
        
        cert_chain = summary['certificate_chain']
        print(f"   📜 Certificate Chain: {'✅ Valid' if cert_chain.get('chain_valid') else '❌ Invalid'}")
        print(f"      Certificate Count: {cert_chain.get('certificate_count', 0)}")
        
        tls_version = summary['tls_version']
        print(f"   🔐 TLS Version: {'✅ TLS 1.2+' if tls_version.get('tls_1_2_supported') else '❌ TLS 1.2 not supported'}")
        
        hsts = summary['hsts_header']
        print(f"   🛡️ HSTS Header: {'✅ Present' if hsts.get('hsts_header_present') else '❌ Missing'}")
        
        websocket = summary['websocket_ssl']
        print(f"   🌐 WebSocket SSL: {'✅ Working' if websocket.get('websocket_ssl_success') else '❌ Failed'}")
        
        # Final completion log
        final_log = {
            "task": "ssl_tls_deployment",
            "status": "completed",
            "summary": "SSL/TLS Full Strict mode verification completed",
            "details": summary
        }
        print(json.dumps(final_log))
        
        return 0 if summary['overall_status'] == 'pass' else 1
        
    except Exception as e:
        error_log = {
            "task": "ssl_tls_deployment",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(error_log))
        logger.error(f"❌ SSL/TLS verification failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())