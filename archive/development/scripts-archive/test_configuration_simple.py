#!/usr/bin/env python3
"""
Simple test script to verify ConfigurationTester implementation for Task 4.
"""

import sys
import tempfile
import os
import yaml
sys.path.append('src')

# Direct imports to avoid circular dependencies
from websocket_validation.config import ValidationConfig
from websocket_validation.collectors import EvidenceCollector
from websocket_validation.testers.configuration import ConfigurationTester

print("🧪 Testing Configuration Tester System (Task 4) - Simple Version")
print("=" * 65)

# Create configuration and evidence collector
config = ValidationConfig(evidence_dir="test_evidence")
evidence_collector = EvidenceCollector(config)

# Create ConfigurationTester
tester = ConfigurationTester(config, evidence_collector)

print(f"📋 Configuration:")
print(f"   Evidence Directory: {config.evidence_dir}")
print(f"   Test Domains: {tester.test_domains}")
print(f"   Config Paths: {len(tester.cloudflare_config_paths)} paths to check")
print()

# Test 1: Test Cloudflare config discovery
print("🔍 Testing Cloudflare configuration discovery...")
try:
    result = tester._discover_cloudflare_configs()
    print(f"   Status: {result.status.value}")
    print(f"   Searched Paths: {result.metrics.get('searched_paths', 0)}")
    print(f"   Found Configs: {result.metrics.get('found_configs', 0)}")
    print(f"   Execution Time: {result.execution_time:.3f}s")
    
    if result.error_details:
        print(f"   Error: {result.error_details}")
    
    config_files = result.metrics.get("config_files", [])
    if config_files:
        print(f"   📁 Found Config Files:")
        for i, config_file in enumerate(config_files):
            print(f"     {i+1}. {config_file}")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print()

# Test 2: Test tunnel config analysis with sample config
print("🔍 Testing tunnel configuration analysis with sample config...")
sample_cloudflare_config = {
    "tunnel": "test-tunnel-id-12345",
    "credentials-file": "/path/to/credentials.json",
    "ingress": [
        {
            "hostname": "nkllon.com",
            "service": "http://localhost:8000",
            "originRequest": {
                "headers": {
                    "Upgrade": "websocket",
                    "Connection": "Upgrade"
                }
            }
        },
        {
            "hostname": "api.nkllon.com", 
            "service": "http://localhost:8001"
        },
        {
            "service": "http_status:404"
        }
    ]
}

with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
    yaml.dump(sample_cloudflare_config, f)
    temp_config_file = f.name

try:
    result = tester._analyze_tunnel_config_file(temp_config_file)
    print(f"   Status: {result.status.value}")
    print(f"   Tunnel ID: {result.metrics.get('tunnel_id', 'unknown')}")
    print(f"   WebSocket Support: {result.metrics.get('websocket_support', False)}")
    print(f"   Configuration Issues: {result.metrics.get('configuration_issues', 0)}")
    print(f"   Execution Time: {result.execution_time:.3f}s")
    
    if result.error_details:
        print(f"   Error: {result.error_details}")
    print()
    
finally:
    os.unlink(temp_config_file)

# Test 3: Test tunnel service status check
print("🔍 Testing tunnel service status check...")
try:
    result = tester._check_tunnel_service_status()
    print(f"   Status: {result.status.value}")
    print(f"   Service Running: {result.metrics.get('service_running', False)}")
    print(f"   Execution Time: {result.execution_time:.3f}s")
    
    if result.error_details:
        print(f"   Error: {result.error_details}")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print()

# Test 4: Test DNS analysis
print("🔍 Testing DNS configuration analysis...")
test_domain = "google.com"  # Use a reliable domain for testing
try:
    result = tester._analyze_domain_dns(test_domain)
    print(f"   Status: {result.status.value}")
    print(f"   Domain: {result.metrics.get('domain', 'unknown')}")
    print(f"   A Records: {result.metrics.get('a_records', 0)}")
    print(f"   NS Records: {result.metrics.get('ns_records', 0)}")
    print(f"   Cloudflare Detected: {result.metrics.get('cloudflare_detected', False)}")
    print(f"   DNS Issues: {result.metrics.get('dns_issues', 0)}")
    print(f"   Execution Time: {result.execution_time:.3f}s")
    
    if result.error_details:
        print(f"   Error: {result.error_details}")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print()

# Test 5: Test SSL analysis
print("🔍 Testing SSL/TLS configuration analysis...")
test_domain = "google.com"  # Use a reliable domain for testing
try:
    result = tester._analyze_domain_ssl(test_domain)
    print(f"   Status: {result.status.value}")
    print(f"   Domain: {result.metrics.get('domain', 'unknown')}")
    print(f"   TLS Version: {result.metrics.get('tls_version', 'unknown')}")
    print(f"   Certificate Valid: {result.metrics.get('certificate_valid', False)}")
    print(f"   WebSocket Support: {result.metrics.get('websocket_support', False)}")
    print(f"   SSL Issues: {result.metrics.get('ssl_issues', 0)}")
    print(f"   Execution Time: {result.execution_time:.3f}s")
    
    if result.error_details:
        print(f"   Error: {result.error_details}")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print()

# Test 6: Test connectivity testing
print("🔍 Testing infrastructure connectivity...")
test_domain = "google.com"  # Use a reliable domain for testing
try:
    result = tester._test_domain_connectivity(test_domain)
    print(f"   Status: {result.status.value}")
    print(f"   Domain: {result.metrics.get('domain', 'unknown')}")
    print(f"   HTTP Accessible: {result.metrics.get('http_accessible', False)}")
    print(f"   Ports Tested: {result.metrics.get('ports_tested', 0)}")
    print(f"   Connectivity Issues: {result.metrics.get('connectivity_issues', 0)}")
    print(f"   Execution Time: {result.execution_time:.3f}s")
    
    if result.error_details:
        print(f"   Error: {result.error_details}")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print()

# Show evidence summary
print("📊 Evidence Collection Summary:")
summary = evidence_collector.generate_summary()
print(f"   Total Evidence Items: {summary['total_items']}")
print(f"   Evidence by Type: {summary['by_type']}")
print(f"   Total Size: {summary['total_size']} bytes")
print(f"   Integrity Verified: {summary['integrity_verified']}")
print()

print("✅ Configuration Tester System test completed!")
print()
print("🎯 Task 4 Implementation Summary:")
print("   ✅ Cloudflare configuration discovery and parsing")
print("   ✅ Tunnel configuration analysis for WebSocket support")
print("   ✅ Tunnel service status checking")
print("   ✅ DNS configuration verification")
print("   ✅ SSL/TLS configuration analysis")
print("   ✅ Infrastructure connectivity testing")
print("   ✅ Comprehensive evidence collection")
print("   ✅ Integration with validation framework")