#!/usr/bin/env python3
"""
Cloudflare API Token Helper
==========================

This script helps you get the right Cloudflare API token for Custom Error Pages deployment.

The tunnel credentials are different from the API token needed for Custom Error Pages.
You need a token with Zone:Edit permissions.

Author: Kiro AI Assistant
Date: 2025-01-27
"""

import os
import sys
import requests
from datetime import datetime

def check_existing_token():
    """Check if CLOUDFLARE_API_TOKEN is already set."""
    token = os.getenv('CLOUDFLARE_API_TOKEN')
    if token:
        print(f"✅ Found CLOUDFLARE_API_TOKEN environment variable")
        return test_token(token)
    else:
        print("❌ CLOUDFLARE_API_TOKEN environment variable not set")
        return None

def test_token(token):
    """Test if the API token works and has the right permissions."""
    print(f"🔍 Testing API token...")
    
    try:
        # Test token validity
        response = requests.get(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Token is valid")
                
                # Check zone access
                zones_response = requests.get(
                    "https://api.cloudflare.com/client/v4/zones",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"name": "nkllon.com"},
                    timeout=10
                )
                
                if zones_response.status_code == 200:
                    zones_data = zones_response.json()
                    if zones_data.get("success") and zones_data.get("result"):
                        zone = zones_data["result"][0]
                        print(f"✅ Can access zone: {zone['name']} (ID: {zone['id']})")
                        
                        # Check if zone has Pro plan (required for Custom Error Pages)
                        if zone.get("plan", {}).get("name", "").lower() in ["pro", "business", "enterprise"]:
                            print(f"✅ Zone has {zone['plan']['name']} plan (Custom Error Pages supported)")
                            return token
                        else:
                            print(f"⚠️  Zone has {zone.get('plan', {}).get('name', 'Unknown')} plan")
                            print("   Custom Error Pages require Pro plan or higher")
                            return token  # Still return token, user can upgrade plan
                    else:
                        print("❌ Cannot access nkllon.com zone with this token")
                        return None
                else:
                    print(f"❌ Cannot list zones: {zones_response.status_code}")
                    return None
            else:
                print(f"❌ Token validation failed: {data.get('errors', 'Unknown error')}")
                return None
        else:
            print(f"❌ Token validation failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return None

def show_token_creation_instructions():
    """Show instructions for creating a new API token."""
    print("\n" + "="*60)
    print("🔑 HOW TO CREATE CLOUDFLARE API TOKEN")
    print("="*60)
    
    print("\n📋 Steps to create the right token:")
    print("1. Go to: https://dash.cloudflare.com/profile/api-tokens")
    print("2. Click 'Create Token'")
    print("3. Click 'Use template' next to 'Edit zone DNS'")
    print("4. Modify the template:")
    print("   • Permissions: Zone:Edit, Zone:Read")
    print("   • Zone Resources: Include - Specific zone - nkllon.com")
    print("5. Click 'Continue to summary'")
    print("6. Click 'Create Token'")
    print("7. Copy the token (you won't see it again!)")
    
    print("\n💡 Alternative - Use existing token:")
    print("If you already have a token with Zone:Edit permissions:")
    print("1. Find your existing token")
    print("2. Make sure it has Zone:Edit permissions for nkllon.com")
    print("3. Set it as environment variable")
    
    print("\n🔧 How to set the token:")
    print("export CLOUDFLARE_API_TOKEN='your-token-here'")
    print("# Add to ~/.zshrc or ~/.bashrc to make it permanent")

def prompt_for_token():
    """Prompt user to enter a token."""
    print("\n" + "="*60)
    print("🔑 ENTER CLOUDFLARE API TOKEN")
    print("="*60)
    
    token = input("\nPaste your Cloudflare API token here: ").strip()
    
    if token:
        print(f"\n🔍 Testing provided token...")
        return test_token(token)
    else:
        print("❌ No token provided")
        return None

def main():
    """Main function."""
    print("🔑 Cloudflare API Token Helper")
    print("=" * 35)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🎯 Purpose: Get API token for Custom Error Pages deployment")
    print("Note: Tunnel credentials are separate from API tokens")
    
    # Check existing token
    token = check_existing_token()
    
    if not token:
        print("\n" + "="*60)
        print("🤔 WHAT DO YOU WANT TO DO?")
        print("="*60)
        print("1. I have a token - let me enter it")
        print("2. I need to create a new token - show me how")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            token = prompt_for_token()
        elif choice == "2":
            show_token_creation_instructions()
            print("\nAfter creating the token, run this script again or set CLOUDFLARE_API_TOKEN")
            return
        else:
            print("👋 Goodbye!")
            return
    
    if token:
        print("\n" + "="*60)
        print("🎉 SUCCESS!")
        print("="*60)
        print("✅ Valid Cloudflare API token found")
        print("✅ Ready for Custom Error Pages deployment")
        
        print(f"\n🔧 To use this token permanently:")
        print(f"export CLOUDFLARE_API_TOKEN='{token[:8]}...{token[-8:]}'")
        print("# Add to ~/.zshrc or ~/.bashrc")
        
        print(f"\n🚀 Now you can run:")
        print(f"python3 cloudflare-error-pages-cli.py deploy --interactive")
        print(f"# or")
        print(f"CLOUDFLARE_API_TOKEN='{token[:8]}...{token[-8:]}' python3 cloudflare-error-pages-cli.py deploy --interactive")
        
    else:
        print("\n❌ No valid token available")
        print("Please create a token and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()