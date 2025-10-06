#!/usr/bin/env python3
"""
Simple Browser Connection
========================

Connect to existing Chrome browser and take initial assessment.
"""

import json
import requests
import time
from datetime import datetime
import base64
from urllib.parse import urlparse


def connect_to_chrome():
    """Connect to existing Chrome browser via CDP"""
    print("🌐 CONNECTING TO EXISTING CHROME BROWSER...")

    # Chrome DevTools Protocol endpoint
    cdp_url = "http://127.0.0.1:9222/json"

    try:
        # Get list of available targets
        response = requests.get(cdp_url, timeout=5)
        targets = response.json()

        print(f"✅ Found {len(targets)} Chrome targets")

        # Find the active page target (any page type)
        page_target = None
        for target in targets:
            if target.get("type") == "page":
                page_target = target
                break

        if not page_target:
            print("❌ No active page found")
            return None

        print(f"🎯 Active page: {page_target.get('url', 'Unknown')}")
        print(f"   Title: {page_target.get('title', 'Unknown')}")

        # Connect to the page
        ws_url = page_target.get("webSocketDebuggerUrl")
        if not ws_url:
            print("❌ No WebSocket URL available")
            return None

        print(f"🔗 WebSocket URL: {ws_url}")

        # Get page info
        page_info = {
            "url": page_target.get("url"),
            "title": page_target.get("title"),
            "target_id": page_target.get("id"),
            "timestamp": datetime.now().isoformat(),
        }

        return page_info

    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to Chrome. Is Chrome running with --remote-debugging-port=9222?"
        )
        return None
    except Exception as e:
        print(f"❌ Error connecting to Chrome: {e}")
        return None


def take_screenshot():
    """Take a screenshot of the current page"""
    print("📸 TAKING SCREENSHOT...")

    try:
        # Get screenshot via CDP
        screenshot_url = "http://localhost:9222/json/runtime/evaluate"

        # Use a different approach - get page source first
        cdp_url = "http://localhost:9222/json"
        response = requests.get(cdp_url, timeout=5)
        targets = response.json()

        # Find active page
        page_target = None
        for target in targets:
            if target.get("type") == "page" and target.get("url", "").startswith(
                "http"
            ):
                page_target = target
                break

        if page_target:
            print(f"✅ Screenshot context: {page_target.get('url')}")

            # Generate screenshot filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_file = f"browser_session_{timestamp}.png"

            # For now, just document what we found
            print(f"📸 Screenshot would be saved as: {screenshot_file}")
            print(f"   URL: {page_target.get('url')}")
            print(f"   Title: {page_target.get('title')}")

            return {
                "screenshot_file": screenshot_file,
                "url": page_target.get("url"),
                "title": page_target.get("title"),
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        return None


def initial_assessment():
    """Perform initial assessment of the current page"""
    print("🔍 INITIAL ASSESSMENT...")

    page_info = connect_to_chrome()
    if not page_info:
        return None

    screenshot_info = take_screenshot()

    # Basic analysis
    url = page_info.get("url", "")
    title = page_info.get("title", "")

    assessment = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "title": title,
        "domain": urlparse(url).netloc if url else "Unknown",
        "page_type": "Unknown",
        "assessment_notes": [],
        "screenshot_info": screenshot_info,
    }

    # Basic page type detection
    if "devpost" in url.lower():
        assessment["page_type"] = "DevPost"
        assessment["assessment_notes"].append("DevPost platform detected")
    elif "login" in url.lower():
        assessment["page_type"] = "Login Page"
        assessment["assessment_notes"].append("Login page detected")
    elif "dashboard" in url.lower():
        assessment["page_type"] = "Dashboard"
        assessment["assessment_notes"].append("Dashboard page detected")
    elif "form" in url.lower():
        assessment["page_type"] = "Form Page"
        assessment["assessment_notes"].append("Form page detected")

    # Additional context
    if title:
        assessment["assessment_notes"].append(f"Page title: {title}")

    if url:
        assessment["assessment_notes"].append(f"Full URL: {url}")

    print(f"📊 ASSESSMENT COMPLETE:")
    print(f"   Domain: {assessment['domain']}")
    print(f"   Page Type: {assessment['page_type']}")
    print(f"   Notes: {len(assessment['assessment_notes'])} observations")

    return assessment


def main():
    """Main function"""
    print("🚀 SIMPLE BROWSER CONNECTION")
    print("=" * 50)

    assessment = initial_assessment()

    if assessment:
        print(f"\n✅ CONNECTION SUCCESSFUL!")
        print(f"   Ready for further instructions")
        print(f"   Current page: {assessment['url']}")
        print(f"   Page type: {assessment['page_type']}")

        # Save assessment
        with open("browser_session_assessment.json", "w") as f:
            json.dump(assessment, f, indent=2)
        print(f"   Assessment saved: browser_session_assessment.json")

        print(f"\n🎯 AWAITING FURTHER INSTRUCTIONS...")
        print(f"   Ready to interrogate and analyze the current page")

    else:
        print(f"\n❌ CONNECTION FAILED")
        print(f"   Please ensure Chrome is running with debugging enabled")


if __name__ == "__main__":
    main()
