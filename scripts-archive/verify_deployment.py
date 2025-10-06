#!/usr/bin/env python3
"""
Cloudflare Error Page Deployment Verification Script
===================================================

This script helps verify that the custom error page is working correctly
after deployment to Cloudflare Dashboard.

Author: Kiro AI Assistant
Date: 2025-01-27
"""

import subprocess
import sys
import time
from datetime import datetime

def check_tunnel_status():
    """Check if Cloudflare tunnel is running."""
    try:
        result = subprocess.run(['pgrep', '-f', 'cloudflared'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def stop_tunnel():
    """Stop the Cloudflare tunnel."""
    print("🛑 Stopping Cloudflare tunnel...")
    try:
        subprocess.run(['pkill', '-f', 'cloudflared'], check=True)
        time.sleep(3)  # Wait for tunnel to stop
        print("✅ Tunnel stopped")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to stop tunnel")
        return False

def start_tunnel():
    """Start the Cloudflare tunnel."""
    print("🔄 Starting Cloudflare tunnel...")
    try:
        # Try make command first
        result = subprocess.run(['make', 'tunnel-start'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Tunnel started via make")
            return True
    except:
        pass
    
    # Fallback to direct cloudflared command
    try:
        subprocess.Popen(['cloudflared', 'tunnel', 'run', 'observatory-tunnel'])
        time.sleep(5)  # Wait for tunnel to start
        print("✅ Tunnel started via cloudflared")
        return True
    except:
        print("❌ Failed to start tunnel")
        return False

def test_error_page(domain):
    """Test if custom error page appears for a domain."""
    print(f"🌐 Testing {domain}...")
    try:
        result = subprocess.run(['curl', '-s', '-I', f'https://{domain}'], 
                              capture_output=True, text=True, timeout=10)
        
        if '1033' in result.stdout or 'Tunnel connection error' in result.stdout:
            print(f"✅ {domain}: Error page should be displayed")
            return True
        else:
            print(f"⚠️  {domain}: Unexpected response")
            return False
    except subprocess.TimeoutExpired:
        print(f"✅ {domain}: Timeout (expected when tunnel is down)")
        return True
    except:
        print(f"❌ {domain}: Failed to test")
        return False

def main():
    """Main verification function."""
    print("🔍 Cloudflare Error Page Deployment Verification")
    print("=" * 55)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    domains = [
        'observatory.nkllon.com',
        'grafana.observatory.nkllon.com', 
        'prometheus.observatory.nkllon.com'
    ]
    
    # Check initial tunnel status
    tunnel_running = check_tunnel_status()
    print(f"🔍 Initial tunnel status: {'Running' if tunnel_running else 'Stopped'}")
    
    if tunnel_running:
        print("\n⚠️  WARNING: This test will temporarily stop your tunnel!")
        response = input("Continue? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Test cancelled by user")
            sys.exit(0)
    
    try:
        # Stop tunnel if running
        if tunnel_running:
            if not stop_tunnel():
                sys.exit(1)
        
        print(f"\n🧪 Testing custom error page on {len(domains)} domains...")
        print("=" * 55)
        
        # Test each domain
        success_count = 0
        for domain in domains:
            if test_error_page(domain):
                success_count += 1
        
        print(f"\n📊 Test Results: {success_count}/{len(domains)} domains tested successfully")
        
        if success_count == len(domains):
            print("✅ All domains should display custom error page!")
        else:
            print("⚠️  Some domains may not show custom error page")
        
        print("\n💡 Manual verification steps:")
        print("   1. Open browser and visit the domains above")
        print("   2. Look for Observatory branding and lab rat 🐭")
        print("   3. Verify 30-second countdown timer")
        print("   4. Test 'Retry Now' button")
        print("   5. Try Konami code: ↑↑↓↓←→←→BA")
        
    finally:
        # Always try to restart tunnel
        if tunnel_running:
            print(f"\n🔄 Restoring tunnel...")
            start_tunnel()
            
            # Wait and verify tunnel is back
            time.sleep(5)
            if check_tunnel_status():
                print("✅ Tunnel restored successfully")
            else:
                print("❌ Failed to restore tunnel - manual intervention needed")
                print("   Run: make tunnel-start")
    
    print(f"\n🎯 Verification complete!")
    print("📝 Next steps:")
    print("   • Monitor Cloudflare Analytics for error page views")
    print("   • Set up alerts for tunnel health")
    print("   • Track user engagement metrics")

if __name__ == "__main__":
    main()