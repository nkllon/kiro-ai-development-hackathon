#!/usr/bin/env python3
"""
Verify Hybrid Service Discovery Deployment
==========================================

Quick verification script to check that the hybrid service discovery
system is working correctly.
"""

import sys
import requests
import subprocess
from typing import Dict, List

# Add project root to path
sys.path.insert(0, '.')

from scripts.hybrid_service_manager import HybridServiceManager
from scripts.port_conflict_detector import PortConflictDetector

def verify_admin_dashboard(port: int = 8889) -> bool:
    """Verify admin dashboard is accessible."""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def verify_api_endpoints(port: int = 8889) -> Dict[str, bool]:
    """Verify API endpoints are working."""
    endpoints = {
        '/api/services': False,
        '/api/make-targets': False
    }
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:{port}{endpoint}", timeout=5)
            endpoints[endpoint] = response.status_code == 200
        except Exception:
            pass
    
    return endpoints

def verify_service_discovery() -> Dict[str, any]:
    """Verify service discovery is working."""
    try:
        manager = HybridServiceManager()
        services = manager.discover_all_services()
        
        return {
            'working': True,
            'total_services': len(services),
            'services': services
        }
    except Exception as e:
        return {
            'working': False,
            'error': str(e)
        }

def verify_port_management() -> bool:
    """Verify port conflict detection is working."""
    try:
        detector = PortConflictDetector()
        report = detector.generate_port_report()
        return len(report) > 0
    except Exception:
        return False

def verify_bonjour_processes() -> List[Dict]:
    """Check for running dns-sd processes (our Bonjour registrations)."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        dns_sd_processes = []
        for line in lines:
            if 'dns-sd' in line and '-R' in line:
                # Extract service name from dns-sd command
                parts = line.split()
                if len(parts) > 10:
                    service_name = parts[10] if len(parts) > 10 else 'unknown'
                    dns_sd_processes.append({
                        'service': service_name,
                        'pid': parts[1],
                        'command': ' '.join(parts[10:15]) if len(parts) > 15 else ' '.join(parts[10:])
                    })
        
        return dns_sd_processes
    except Exception:
        return []

def main():
    """Run complete verification."""
    print("🔍 Verifying Hybrid Service Discovery Deployment")
    print("=" * 50)
    
    all_good = True
    
    # Verify admin dashboard
    print("🌐 Admin Dashboard...")
    dashboard_ok = verify_admin_dashboard()
    if dashboard_ok:
        print("   ✅ Dashboard accessible at http://localhost:8889")
    else:
        print("   ❌ Dashboard not accessible")
        all_good = False
    
    # Verify API endpoints
    print("🔌 API Endpoints...")
    api_status = verify_api_endpoints()
    for endpoint, status in api_status.items():
        if status:
            print(f"   ✅ {endpoint}")
        else:
            print(f"   ❌ {endpoint}")
            all_good = False
    
    # Verify service discovery
    print("🔍 Service Discovery...")
    discovery_status = verify_service_discovery()
    if discovery_status['working']:
        print(f"   ✅ {discovery_status['total_services']} services discovered")
        
        # Show service details
        for name, info in discovery_status['services'].items():
            method = info.get('discovery_method', 'unknown')
            domain = info.get('domain', 'unknown')
            port = info.get('port', 'unknown')
            print(f"      🌐 {name}: {domain}:{port} ({method})")
    else:
        print(f"   ❌ Service discovery failed: {discovery_status.get('error', 'unknown')}")
        all_good = False
    
    # Verify port management
    print("🔧 Port Management...")
    port_ok = verify_port_management()
    if port_ok:
        print("   ✅ Port conflict detection working")
    else:
        print("   ❌ Port conflict detection failed")
        all_good = False
    
    # Verify Bonjour processes
    print("📡 Bonjour Registration...")
    bonjour_processes = verify_bonjour_processes()
    if bonjour_processes:
        print(f"   ✅ {len(bonjour_processes)} Bonjour services registered:")
        for process in bonjour_processes:
            print(f"      🌐 {process['service']} (PID: {process['pid']})")
    else:
        print("   ⚠️  No active Bonjour registrations found")
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All systems operational!")
        print("🌐 Access dashboard: http://localhost:8889")
        print("🔧 Manage services: python scripts/hybrid_service_manager.py")
    else:
        print("⚠️  Some issues detected - check logs above")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)