#!/usr/bin/env python3
"""One-time API discovery script - run this once to cache all APIs"""

import json
import subprocess
from datetime import datetime
from typing import Optional


def discover_all_apis() -> list:
    """Discover all API keys from 1Password once"""
    print("🔍 One-time API discovery (this may take a while)...")

    try:
        # Get list of all items from 1Password
        result = subprocess.run(
            ["op", "item", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
        )

        items = json.loads(result.stdout)
        discovered_keys = []

        # Generic API patterns to search for
        api_patterns = [
            "api",
            "key",
            "token",
            "secret",
            "credential",
            "auth",
            "openai",
            "anthropic",
            "google",
            "azure",
            "aws",
            "github",
            "stripe",
            "twilio",
            "sendgrid",
            "mailgun",
            "slack",
            "discord",
            "jira",
            "confluence",
            "notion",
            "airtable",
            "zapier",
            "webhook",
            "database",
            "redis",
            "postgres",
            "mysql",
            "mongodb",
            "elasticsearch",
            "cloudflare",
            "vercel",
            "netlify",
            "heroku",
            "digitalocean",
            "linode",
        ]

        for i, item in enumerate(items):
            item_title = item.get("title", "").lower()
            item_id = item.get("id")

            # Skip system items
            if any(skip in item_title for skip in ["login", "password", "secure note", "software license"]):
                continue

            # Check if this item looks like an API key
            if any(pattern in item_title for pattern in api_patterns):
                try:
                    print(f"  🔍 [{i + 1}/{len(items)}] Checking {item_title}...")

                    # Get detailed item information
                    item_result = subprocess.run(
                        ["op", "item", "get", item_id, "--format=json"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                    item_details = json.loads(item_result.stdout)
                    key_info = extract_generic_key_info(item_details)

                    if key_info:
                        discovered_keys.append(key_info)
                        print(f"    ✅ Found {key_info['provider']} API key")

                except subprocess.CalledProcessError as e:
                    print(f"    ⚠️ Could not get details: {e}")
                    continue

        return discovered_keys

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to access 1Password: {e}")
        print("Make sure you're signed into 1Password: eval $(op signin)")
        return []
    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        return []


def extract_generic_key_info(item_details: dict) -> Optional[dict]:
    """Extract generic API key information from 1Password item"""
    try:
        title = item_details.get("title", "")
        fields = item_details.get("fields", [])

        # Find the API key field
        api_key = None
        endpoint = None
        username = None
        organization = None

        for field in fields:
            field_label = field.get("label", "").lower()
            field_value = field.get("value", "")

            # Look for API key in various field types
            if any(keyword in field_label for keyword in ["api key", "key", "token", "secret", "credential"]):
                if field_value and len(field_value) > 20:  # Likely an API key
                    api_key = field_value

            # Look for endpoint/URL
            elif any(keyword in field_label for keyword in ["url", "endpoint", "base url", "host", "server"]):
                if field_value and field_value.startswith(("http://", "https://")):
                    endpoint = field_value

            # Look for username
            elif any(keyword in field_label for keyword in ["username", "user", "login", "email"]):
                if field_value:
                    username = field_value

            # Look for organization
            elif any(keyword in field_label for keyword in ["org", "organization", "company", "team", "account"]):
                if field_value:
                    organization = field_value

        if not api_key:
            return None

        # Determine provider from title
        provider = identify_provider(title)

        # Generate standardized key names
        key_name = f"{provider.upper()}_API_KEY"
        endpoint_name = f"{provider.upper()}_ENDPOINT" if endpoint else None
        username_name = f"{provider.upper()}_USERNAME" if username else None
        org_name = f"{provider.upper()}_ORG" if organization else None

        return {
            "provider": provider,
            "key_name": key_name,
            "value": api_key,
            "endpoint_name": endpoint_name,
            "endpoint": endpoint,
            "username_name": username_name,
            "username": username,
            "org_name": org_name,
            "organization": organization,
            "status": "available" if api_key else "missing",
            "title": title,
        }

    except Exception as e:
        print(f"⚠️ Error extracting key info for {title}: {e}")
        return None


def identify_provider(title: str) -> str:
    """Identify the API provider from the title"""
    title_lower = title.lower()

    # Common provider mappings
    provider_mappings = {
        "openai": ["openai", "gpt", "azure openai", "microsoft openai"],
        "anthropic": ["anthropic", "claude"],
        "google": ["google", "gemini", "palm", "vertex"],
        "aws": ["aws", "amazon", "lambda", "dynamodb", "s3"],
        "github": ["github", "gh"],
        "stripe": ["stripe"],
        "twilio": ["twilio"],
        "sendgrid": ["sendgrid"],
        "mailgun": ["mailgun"],
        "slack": ["slack"],
        "discord": ["discord"],
        "jira": ["jira", "atlassian"],
        "notion": ["notion"],
        "airtable": ["airtable"],
        "zapier": ["zapier"],
        "database": ["database", "db", "postgres", "mysql", "mongodb"],
        "redis": ["redis"],
        "cloudflare": ["cloudflare"],
        "vercel": ["vercel"],
        "netlify": ["netlify"],
        "heroku": ["heroku"],
        "digitalocean": ["digitalocean", "do"],
        "linode": ["linode", "akamai"],
    }

    for provider, patterns in provider_mappings.items():
        if any(pattern in title_lower for pattern in patterns):
            return provider

    # If no specific provider found, extract from title
    words = title_lower.split()
    for word in words:
        if word not in ["api", "key", "token", "secret", "credential", "auth"]:
            return word

    return "unknown"


def main():
    """Main function to discover and cache all APIs"""
    print("🚀 One-Time API Discovery Script")
    print("=" * 40)
    print("This will discover ALL APIs and cache them for future use.")
    print("Run this once, then use the cached results.")
    print()

    # Discover all APIs
    discovered_keys = discover_all_apis()

    if not discovered_keys:
        print("❌ No APIs discovered")
        return

    # Cache the results
    cache_data = {
        "timestamp": datetime.now().isoformat(),
        "discovered_keys": discovered_keys,
        "total_count": len(discovered_keys),
    }

    cache_file = "api_discovery_cache.json"
    with open(cache_file, "w") as f:
        json.dump(cache_data, f, indent=2)

    print(f"\n💾 Discovery results cached to {cache_file}")
    print(f"✅ Total APIs discovered: {len(discovered_keys)}")
    print("\n🎯 Now you can use the main script with cached results!")
    print("   python scripts/op_api_key_manager.py --discovery-only")


if __name__ == "__main__":
    main()
