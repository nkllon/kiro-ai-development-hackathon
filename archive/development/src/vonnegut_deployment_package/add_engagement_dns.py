#!/usr/bin/env python3
"""
Add engagement.observatory.nkllon.com DNS record via Cloudflare API
"""

import os
import requests
import json
from typing import Dict, Any

def get_cloudflare_credentials() -> Dict[str, str]:
    """Get Cloudflare API credentials from environment variables."""
    api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
    
    if not api_token:
        print("❌ CLOUDFLARE_API_TOKEN environment variable not set")
        print("   Get your API token from: https://dash.cloudflare.com/profile/api-tokens")
        return {}
    
    if not zone_id:
        print("❌ CLOUDFLARE_ZONE_ID environment variable not set")
        print("   Find your Zone ID in the Cloudflare dashboard for nkllon.com")
        return {}
    
    return {
        'api_token': api_token,
        'zone_id': zone_id
    }

def get_existing_dns_records(api_token: str, zone_id: str) -> Dict[str, Any]:
    """Get existing DNS records for the zone."""
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    params = {
        'name': 'observatory.nkllon.com',
        'type': 'CNAME'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['result']:
            return data['result'][0]  # Return the first matching record
    
    return {}

def create_engagement_dns_record(api_token: str, zone_id: str) -> bool:
    """Create DNS record for engagement.observatory.nkllon.com."""
    
    # First, get the existing observatory record to copy its target
    existing_record = get_existing_dns_records(api_token, zone_id)
    
    if not existing_record:
        print("❌ Could not find existing observatory.nkllon.com record to copy")
        return False
    
    target = existing_record.get('content', 'observatory.nkllon.com')
    print(f"📋 Using target from existing record: {target}")
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Create the new DNS record
    dns_record = {
        'type': 'CNAME',
        'name': 'engagement.observatory.nkllon.com',
        'content': target,
        'ttl': 1,  # Auto TTL
        'proxied': True  # Enable Cloudflare proxy (orange cloud)
    }
    
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    
    print(f"🌐 Creating DNS record: engagement.observatory.nkllon.com -> {target}")
    
    response = requests.post(url, headers=headers, json=dns_record)
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            record_id = data['result']['id']
            print(f"✅ DNS record created successfully!")
            print(f"   Record ID: {record_id}")
            print(f"   Name: {data['result']['name']}")
            print(f"   Content: {data['result']['content']}")
            print(f"   Proxied: {data['result']['proxied']}")
            return True
        else:
            print(f"❌ API request failed: {data['errors']}")
    else:
        print(f"❌ HTTP error {response.status_code}: {response.text}")
    
    return False

def check_dns_propagation() -> bool:
    """Check if the DNS record has propagated."""
    import time
    import subprocess
    
    print("🔍 Checking DNS propagation...")
    
    for attempt in range(5):
        try:
            result = subprocess.run(
                ['dig', '+short', 'engagement.observatory.nkllon.com'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                ips = result.stdout.strip().split('\n')
                print(f"✅ DNS propagated! IPs: {', '.join(ips)}")
                return True
            else:
                print(f"⏳ Attempt {attempt + 1}/5: DNS not yet propagated")
                time.sleep(2)
        
        except subprocess.TimeoutExpired:
            print(f"⏳ Attempt {attempt + 1}/5: DNS lookup timeout")
            time.sleep(2)
    
    print("⚠️  DNS may still be propagating (can take up to 5 minutes)")
    return False

def test_engagement_endpoint() -> bool:
    """Test if the engagement endpoint is accessible through the tunnel."""
    import time
    
    print("🧪 Testing engagement endpoint...")
    
    for attempt in range(3):
        try:
            response = requests.get(
                'https://engagement.observatory.nkllon.com/health',
                timeout=10,
                verify=False  # Skip SSL verification for testing
            )
            
            if response.status_code == 200:
                print(f"✅ Engagement endpoint working! Response: {response.text}")
                return True
            else:
                print(f"⚠️  Attempt {attempt + 1}/3: HTTP {response.status_code}")
                time.sleep(5)
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Attempt {attempt + 1}/3: {str(e)}")
            time.sleep(5)
    
    print("❌ Engagement endpoint not yet accessible (may need more time)")
    return False

def main():
    """Main function to add engagement DNS record."""
    print("🌐 Cloudflare DNS Management: Adding engagement.observatory.nkllon.com")
    print("=" * 70)
    
    # Get credentials
    creds = get_cloudflare_credentials()
    if not creds:
        print("\n💡 To set up Cloudflare API access:")
        print("   1. Go to https://dash.cloudflare.com/profile/api-tokens")
        print("   2. Create a token with Zone:Edit permissions for nkllon.com")
        print("   3. Set CLOUDFLARE_API_TOKEN environment variable")
        print("   4. Set CLOUDFLARE_ZONE_ID from your Cloudflare dashboard")
        return False
    
    # Create DNS record
    success = create_engagement_dns_record(creds['api_token'], creds['zone_id'])
    
    if success:
        print("\n🎉 DNS record created successfully!")
        
        # Check propagation
        print("\n" + "=" * 50)
        check_dns_propagation()
        
        # Test endpoint
        print("\n" + "=" * 50)
        test_engagement_endpoint()
        
        print("\n✅ Setup complete! The engagement server should be accessible at:")
        print("   https://engagement.observatory.nkllon.com/health")
        
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)