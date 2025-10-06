#!/usr/bin/env python3
"""
Simple Cloudflare Error Pages Deployment Script
==============================================

A simplified deployment script that validates the error page and provides
manual deployment instructions without requiring API tokens.

Usage:
    python3 deploy-simple.py

Author: Kiro AI Assistant
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def validate_error_page():
    """Validate the error page file."""
    html_file = Path("cloudflare/error-pages/1033-enhanced.html")
    
    print("🔍 Validating error page...")
    
    # Check file exists
    if not html_file.exists():
        print(f"❌ Error: HTML file not found at {html_file}")
        return False
    
    # Check file size
    file_size = html_file.stat().st_size
    file_size_kb = file_size / 1024
    
    print(f"📊 File size: {file_size_kb:.1f} KB", end="")
    if file_size_kb > 50:
        print(" ❌ (exceeds 50KB Cloudflare limit)")
        return False
    else:
        print(" ✅ (within 50KB limit)")
    
    # Check required content
    content = html_file.read_text()
    required_elements = [
        "<!DOCTYPE html>",
        "Observatory",
        "Minor Lab Incident", 
        "🐭",  # Lab rat emoji
        "Retry Now",
        "countdown",
        "d1e53e43-033f-4994-8f46-c83962ae3785"  # Tunnel ID
    ]
    
    missing = [elem for elem in required_elements if elem not in content]
    if missing:
        print(f"❌ Missing required elements: {missing}")
        return False
    
    print("✅ Content validation passed")
    return True

def show_deployment_instructions():
    """Show manual deployment instructions."""
    print("\n" + "="*60)
    print("🚀 CLOUDFLARE DASHBOARD DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 Steps to deploy:")
    print("1. Open your browser and go to: https://dash.cloudflare.com/")
    print("2. Log in to your Cloudflare account")
    print("3. Select the 'nkllon.com' zone")
    print("4. In the left sidebar, click 'Rules'")
    print("5. Click 'Custom Error Responses'")
    print("6. Click 'Create custom error response'")
    print("7. Select Error code: '1033'")
    print("8. Select Response type: 'Custom HTML'")
    print("9. Copy and paste the content from: cloudflare/error-pages/1033-enhanced.html")
    print("10. Click 'Save'")
    print("11. Wait for deployment (usually < 5 minutes)")
    
    print("\n✅ After deployment, the custom error page will appear when:")
    print("   - The Cloudflare tunnel is down")
    print("   - Users visit observatory.nkllon.com, grafana.observatory.nkllon.com, or prometheus.observatory.nkllon.com")

def show_testing_instructions():
    """Show testing instructions."""
    print("\n" + "="*60)
    print("🧪 TESTING INSTRUCTIONS")
    print("="*60)
    
    print("\n⚠️  IMPORTANT: Only test when you can afford brief downtime!")
    
    print("\n🔍 To test the custom error page:")
    print("1. Stop the Cloudflare tunnel:")
    print("   make tunnel-stop")
    print("   (or: pkill -f cloudflared)")
    
    print("\n2. Visit these URLs in your browser:")
    print("   • https://observatory.nkllon.com")
    print("   • https://grafana.observatory.nkllon.com")
    print("   • https://prometheus.observatory.nkllon.com")
    
    print("\n3. You should see:")
    print("   ✅ Observatory branding with space gradient background")
    print("   ✅ Animated lab rat mascot 🐭 with smoke and sparks")
    print("   ✅ '30-second countdown timer'")
    print("   ✅ 'Retry Now' button with loading spinner")
    print("   ✅ Technical details in YAML format")
    print("   ✅ Responsive design on mobile devices")
    
    print("\n4. Test interactive features:")
    print("   • Click the 'Retry Now' button (should show spinner)")
    print("   • Press spacebar (should also trigger retry)")
    print("   • Try the Konami code: ↑↑↓↓←→←→BA (Easter egg!)")
    
    print("\n5. Restore service:")
    print("   make tunnel-start")
    print("   (or restart your tunnel manually)")

def show_current_status():
    """Show current tunnel and error page status."""
    print("\n" + "="*60)
    print("📊 CURRENT STATUS")
    print("="*60)
    
    # Check tunnel status
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'cloudflared'], 
                              capture_output=True, text=True)
        tunnel_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        if tunnel_count > 0:
            print(f"🟢 Cloudflare tunnel: RUNNING ({tunnel_count} processes)")
            print("   Users see normal Observatory interface")
        else:
            print("🔴 Cloudflare tunnel: DOWN (0 processes)")
            print("   Users see error page (perfect for testing!)")
    except:
        print("❓ Cloudflare tunnel: Status unknown")
    
    # Test current error response
    print("\n🌐 Testing current error response...")
    try:
        import requests
        response = requests.get("https://observatory.nkllon.com", timeout=5)
        print(f"   Response: {response.status_code}")
        if response.status_code == 530:
            print("   ✅ Getting Cloudflare error (tunnel down)")
        else:
            print("   ✅ Site is responding normally")
    except requests.exceptions.RequestException:
        print("   ✅ Connection failed (tunnel down - perfect for testing!)")

def main():
    """Main function."""
    print("🚀 Cloudflare Custom Error Pages - Simple Deployment")
    print("=" * 55)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate error page
    if not validate_error_page():
        print("\n❌ Validation failed. Please fix issues before deploying.")
        sys.exit(1)
    
    print("\n✅ Pre-deployment validation passed!")
    
    # Show current status
    show_current_status()
    
    # Show deployment instructions
    show_deployment_instructions()
    
    # Show testing instructions
    show_testing_instructions()
    
    print("\n" + "="*60)
    print("🎉 READY TO DEPLOY!")
    print("="*60)
    print("The error page is validated and ready for manual upload to Cloudflare Dashboard.")
    print("Follow the instructions above to complete the deployment.")
    print("\n💡 Tip: Since the tunnel appears to be down, this is perfect timing to test!")

if __name__ == "__main__":
    main()