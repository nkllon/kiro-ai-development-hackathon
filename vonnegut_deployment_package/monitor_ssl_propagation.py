#!/usr/bin/env python3
"""
Monitor SSL Certificate Propagation for Cloudflare Subdomains
============================================================
"""

import time
import requests
import subprocess
from datetime import datetime

def check_ssl_status(hostname):
    """Check SSL certificate status for a hostname."""
    try:
        # Try HTTPS connection
        response = requests.get(f"https://{hostname}", timeout=10, verify=True)
        return {
            'status': 'SUCCESS',
            'code': response.status_code,
            'ssl_valid': True
        }
    except requests.exceptions.SSLError as e:
        return {
            'status': 'SSL_ERROR',
            'error': str(e),
            'ssl_valid': False
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'status': 'CONNECTION_ERROR', 
            'error': str(e),
            'ssl_valid': False
        }
    except Exception as e:
        return {
            'status': 'OTHER_ERROR',
            'error': str(e),
            'ssl_valid': False
        }

def monitor_subdomains():
    """Monitor SSL status for all subdomains."""
    subdomains = [
        'test.observatory.nkllon.com',
        'grafana.observatory.nkllon.com', 
        'prometheus.observatory.nkllon.com',
        'observatory.nkllon.com'  # Control - should work
    ]
    
    print("🔐 Monitoring SSL Certificate Propagation")
    print("=" * 60)
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] Checking SSL status...")
        
        all_ready = True
        
        for subdomain in subdomains:
            status = check_ssl_status(subdomain)
            
            if status['ssl_valid']:
                print(f"✅ {subdomain} - HTTPS working (HTTP {status.get('code', 'N/A')})")
            else:
                print(f"❌ {subdomain} - {status['status']}")
                if subdomain != 'observatory.nkllon.com':  # Don't count control in readiness
                    all_ready = False
        
        if all_ready:
            print(f"\n🎉 ALL SUBDOMAINS READY!")
            print("🔗 Access URLs:")
            print(f"   Observatory: https://observatory.nkllon.com")
            print(f"   Grafana:     https://grafana.observatory.nkllon.com")
            print(f"   Prometheus:  https://prometheus.observatory.nkllon.com")
            break
        
        print(f"⏳ Waiting 30 seconds for SSL propagation...")
        time.sleep(30)

if __name__ == "__main__":
    monitor_subdomains()