#!/usr/bin/env python3
"""
Cloudflare Custom Error Pages Deployment Script
==============================================

This script helps deploy the custom error pages to Cloudflare Dashboard.
Since Cloudflare doesn't provide a direct API for Custom Error Pages,
this script provides guidance and validation for manual deployment.

Author: Kiro AI Assistant
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def validate_error_page_file():
    """Validate the error page file exists and meets requirements."""
    error_page_path = Path("cloudflare/error-pages/1033-enhanced.html")
    
    if not error_page_path.exists():
        print("❌ Error: 1033-enhanced.html not found!")
        print(f"   Expected location: {error_page_path.absolute()}")
        return False
    
    # Check file size (should be under 50KB)
    file_size = error_page_path.stat().st_size
    file_size_kb = file_size / 1024
    
    print(f"✅ Error page file found: {error_page_path}")
    print(f"📊 File size: {file_size_kb:.1f} KB", end="")
    
    if file_size_kb > 50:
        print(" ❌ (exceeds 50KB limit)")
        return False
    else:
        print(" ✅ (within 50KB limit)")
    
    # Basic content validation
    content = error_page_path.read_text()
    
    required_elements = [
        "<!DOCTYPE html>",
        "Observatory",
        "Minor Lab Incident",
        "🐭",  # Lab rat emoji
        "Retry Now",
        "countdown",
        "d1e53e43-033f-4994-8f46-c83962ae3785"  # Tunnel ID
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing required elements: {missing_elements}")
        return False
    
    print("✅ Content validation passed")
    return True

def print_deployment_instructions():
    """Print step-by-step deployment instructions."""
    print("\n" + "="*60)
    print("🚀 CLOUDFLARE DASHBOARD DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 Prerequisites:")
    print("   • Cloudflare account with nkllon.com zone")
    print("   • Pro plan or higher (required for Custom Error Pages)")
    print("   • Dashboard access permissions")
    
    print("\n🔧 Deployment Steps:")
    print("\n1. 📂 Prepare the file:")
    print("   • Open: cloudflare/error-pages/1033-enhanced.html")
    print("   • Copy the entire file content (Ctrl+A, Ctrl+C)")
    
    print("\n2. 🌐 Access Cloudflare Dashboard:")
    print("   • Go to: https://dash.cloudflare.com/")
    print("   • Log in to your account")
    print("   • Select the 'nkllon.com' zone")
    
    print("\n3. ⚙️ Navigate to Custom Error Pages:")
    print("   • In the left sidebar, click 'Rules'")
    print("   • Click 'Custom Error Responses'")
    print("   • (If not available, upgrade to Pro plan)")
    
    print("\n4. 📝 Create Custom Error Response:")
    print("   • Click 'Create custom error response'")
    print("   • Error code: Select '1033' from dropdown")
    print("   • Response type: Select 'Custom HTML'")
    print("   • Paste the copied HTML content")
    
    print("\n5. 👀 Preview and Deploy:")
    print("   • Click 'Preview' to see how it looks")
    print("   • If satisfied, click 'Save'")
    print("   • Wait for deployment (usually < 5 minutes)")
    
    print("\n6. ✅ Verify Deployment:")
    print("   • Status should show 'Active'")
    print("   • Note: Changes propagate globally within 5 minutes")

def print_testing_instructions():
    """Print testing instructions."""
    print("\n" + "="*60)
    print("🧪 TESTING INSTRUCTIONS")
    print("="*60)
    
    print("\n⚠️  IMPORTANT: Only test when you can afford brief downtime!")
    
    print("\n🔍 Testing Steps:")
    print("\n1. 🛑 Stop the Cloudflare tunnel:")
    print("   • Run: make tunnel-stop")
    print("   • Or: pkill -f cloudflared")
    
    print("\n2. 🌐 Test each domain:")
    print("   • Visit: https://observatory.nkllon.com")
    print("   • Visit: https://grafana.observatory.nkllon.com") 
    print("   • Visit: https://prometheus.observatory.nkllon.com")
    
    print("\n3. ✅ Verify custom error page appears:")
    print("   • Should see Observatory branding")
    print("   • Should see animated lab rat 🐭")
    print("   • Should see 30-second countdown")
    print("   • Should see 'Retry Now' button")
    print("   • Should see technical details in YAML format")
    
    print("\n4. 🎮 Test interactive features:")
    print("   • Click 'Retry Now' button (should show spinner)")
    print("   • Press spacebar (should trigger retry)")
    print("   • Try Konami code: ↑↑↓↓←→←→BA (Easter egg)")
    
    print("\n5. 📱 Test on mobile:")
    print("   • Check responsive layout")
    print("   • Verify touch interactions work")
    
    print("\n6. 🔄 Restore service:")
    print("   • Run: make tunnel-start")
    print("   • Verify normal service resumes")
    
    print("\n7. 🌍 Geographic testing (optional):")
    print("   • Test from different locations if possible")
    print("   • Verify consistent rendering")

def print_monitoring_setup():
    """Print monitoring setup instructions."""
    print("\n" + "="*60)
    print("📊 MONITORING SETUP")
    print("="*60)
    
    print("\n📈 Cloudflare Analytics:")
    print("   • Go to Analytics & Logs > Web Analytics")
    print("   • Monitor error page views")
    print("   • Track geographic distribution")
    print("   • Monitor load times")
    
    print("\n🔔 Set up alerts:")
    print("   • Go to Notifications")
    print("   • Create alert for high error rates")
    print("   • Monitor tunnel health")
    
    print("\n📝 Success metrics to track:")
    print("   • Error page engagement rate (target: >60%)")
    print("   • Average time on error page (target: 15-45s)")
    print("   • Retry button click rate (target: >50%)")
    print("   • Support ticket reduction (target: >50%)")

def main():
    """Main deployment function."""
    print("🚀 Cloudflare Custom Error Pages Deployment")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate the error page file
    if not validate_error_page_file():
        print("\n❌ Validation failed. Please fix issues before deploying.")
        sys.exit(1)
    
    print("\n✅ Pre-deployment validation passed!")
    
    # Print deployment instructions
    print_deployment_instructions()
    
    # Print testing instructions
    print_testing_instructions()
    
    # Print monitoring setup
    print_monitoring_setup()
    
    print("\n" + "="*60)
    print("🎯 DEPLOYMENT CHECKLIST")
    print("="*60)
    print("□ File validation passed")
    print("□ Cloudflare Dashboard access confirmed")
    print("□ Pro plan verified")
    print("□ Custom Error Response created (Error 1033)")
    print("□ HTML content pasted and saved")
    print("□ Deployment status shows 'Active'")
    print("□ Testing completed successfully")
    print("□ Service restored")
    print("□ Monitoring configured")
    
    print("\n🎉 Ready to deploy! Follow the instructions above.")
    print("💡 Tip: Keep this terminal open for reference during deployment.")

if __name__ == "__main__":
    main()