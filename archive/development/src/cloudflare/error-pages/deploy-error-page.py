#!/usr/bin/env python3
"""
Deploy custom error page to Cloudflare

This script uploads the enhanced 1033 error page to Cloudflare
and configures it for the Observatory domain.

Usage:
    python deploy-error-page.py

Requirements:
    - Cloudflare API token with Zone.Custom Pages permissions
    - Zone ID for nkllon.com
    - Pro plan or higher on the zone
"""

import os
import sys
import requests
from pathlib import Path

# Configuration
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
ERROR_PAGE_FILE = "cloudflare/error-pages/1033-enhanced.html"


def validate_environment():
    """Validate required environment variables"""
    if not CLOUDFLARE_API_TOKEN:
        print("❌ Error: CLOUDFLARE_API_TOKEN environment variable not set")
        print("\nTo set it:")
        print("  export CLOUDFLARE_API_TOKEN='your-token-here'")
        return False

    if not CLOUDFLARE_ZONE_ID:
        print("❌ Error: CLOUDFLARE_ZONE_ID environment variable not set")
        print("\nTo find your Zone ID:")
        print("  1. Log in to Cloudflare Dashboard")
        print("  2. Select your domain (nkllon.com)")
        print("  3. Look for 'Zone ID' on the Overview page (right sidebar)")
        print("\nTo set it:")
        print("  export CLOUDFLARE_ZONE_ID='your-zone-id-here'")
        return False

    return True


def read_error_page():
    """Read the error page HTML file"""
    error_page_path = Path(__file__).parent.parent / ERROR_PAGE_FILE

    if not error_page_path.exists():
        print(f"❌ Error: File not found: {error_page_path}")
        return None

    with open(error_page_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"✅ Loaded error page: {error_page_path}")
    print(f"   File size: {len(content)} bytes")
    return content


def get_custom_error_rules(zone_id, token):
    """Get existing custom error rules"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"⚠️  Warning: Could not fetch existing rules: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

    return response.json()


def deploy_via_custom_pages(zone_id, token, html_content):
    """
    Deploy error page via Custom Pages API (simpler method)

    Note: This method may not work for all error codes.
    For 1033 errors, you may need to use Custom Error Rules instead.
    """
    # For Cloudflare 1xxx errors, we need to use a different approach
    # This is a placeholder - the actual API endpoint for 1033 may vary

    print("\n📋 Deployment Instructions (Manual):")
    print("\nSince error 1033 is a Cloudflare-specific tunnel error,")
    print("the best way to deploy is through the Cloudflare Dashboard:\n")

    print("1. Log in to Cloudflare Dashboard:")
    print("   https://dash.cloudflare.com/\n")

    print("2. Select your zone: nkllon.com\n")

    print("3. Navigate to:")
    print("   Rules → Custom Error Responses (or Custom Pages)\n")

    print("4. Create a new custom error response:")
    print("   - Error Code: 1033")
    print("   - Response Type: Custom HTML")
    print("   - Paste the content from:")
    print(f"     {Path(__file__).parent.parent / ERROR_PAGE_FILE}\n")

    print("5. Save and Deploy\n")

    print("6. Test by stopping your tunnel:")
    print("   cloudflared tunnel stop observatory-tunnel")
    print("   Then visit: https://observatory.nkllon.com\n")

    return True


def create_error_page_asset(zone_id, token, html_content):
    """Create custom error page asset"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/custom_error_assets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Create asset
    payload = {
        "content": html_content,
        "type": "html",
        "status_code": 1033,
    }

    print("\n🚀 Attempting API deployment...")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print("✅ Successfully deployed error page via API!")
        print(f"   Response: {response.json()}")
        return True
    else:
        print(f"⚠️  API deployment not available: {response.status_code}")
        print(f"   Response: {response.text}")
        print("\n   This is expected - falling back to manual instructions.")
        return False


def main():
    """Main deployment flow"""
    print("=" * 60)
    print("  Cloudflare 1033 Error Page Deployment")
    print("=" * 60)
    print()

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    # Read error page
    html_content = read_error_page()
    if not html_content:
        sys.exit(1)

    zone_id = CLOUDFLARE_ZONE_ID
    token = CLOUDFLARE_API_TOKEN

    # Try API deployment first
    api_success = create_error_page_asset(zone_id, token, html_content)

    if not api_success:
        # Fall back to manual instructions
        deploy_via_custom_pages(zone_id, token, html_content)

    print("\n" + "=" * 60)
    print("  Additional Testing Steps")
    print("=" * 60)
    print()
    print("1. Stop the Observatory tunnel:")
    print("   make tunnel-stop")
    print()
    print("2. Visit the Observatory URL:")
    print("   https://observatory.nkllon.com")
    print()
    print("3. Verify the custom error page appears")
    print()
    print("4. Test on mobile device as well")
    print()
    print("5. Restart the tunnel when done:")
    print("   make tunnel-start")
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()