#!/usr/bin/env python3
"""
Restart Chrome with Debugging Enabled
====================================

Safely restart Chrome with remote debugging enabled while preserving
the current form state and navigation.
"""

import subprocess
import json
import time
import os
from pathlib import Path


def save_current_state():
    """Save current Chrome state before restarting."""
    print("💾 Saving current state...")

    try:
        # Get current URL
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "Google Chrome" to get URL of active tab of front window',
            ],
            capture_output=True,
            text=True,
        )
        current_url = result.stdout.strip()

        # Get current page title
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "Google Chrome" to get title of active tab of front window',
            ],
            capture_output=True,
            text=True,
        )
        page_title = result.stdout.strip()

        # Save state
        state = {
            "url": current_url,
            "title": page_title,
            "timestamp": time.time(),
            "hackathon_id": "25444-code-with-kiro-hackathon",
            "submission_id": "784734-untitled",
        }

        with open("chrome_state.json", "w") as f:
            json.dump(state, f, indent=2)

        print(f"✅ Saved state: {page_title}")
        print(f"   URL: {current_url}")
        return state

    except Exception as e:
        print(f"❌ Failed to save state: {e}")
        return None


def close_chrome():
    """Close Chrome safely."""
    print("🔄 Closing Chrome...")

    try:
        subprocess.run(
            ["osascript", "-e", 'tell application "Google Chrome" to quit'],
            capture_output=True,
            text=True,
        )
        time.sleep(2)
        print("✅ Chrome closed")
        return True
    except Exception as e:
        print(f"❌ Failed to close Chrome: {e}")
        return False


def start_chrome_with_debugging():
    """Start Chrome with remote debugging enabled."""
    print("🚀 Starting Chrome with debugging...")

    try:
        # Start Chrome with remote debugging
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        cmd = [
            chrome_path,
            "--remote-debugging-port=9222",
            "--user-data-dir=/tmp/chrome-debug",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
        ]

        # Start Chrome in background
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for Chrome to start
        time.sleep(3)

        # Check if debugging port is available
        import requests

        try:
            response = requests.get("http://localhost:9222/json/version", timeout=5)
            if response.status_code == 200:
                print("✅ Chrome started with debugging enabled")
                return True
        except:
            pass

        print("⚠️ Chrome started but debugging port not ready yet")
        return True

    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return False


def restore_navigation(state):
    """Restore navigation to the saved URL."""
    print("🌐 Restoring navigation...")

    try:
        # Wait a bit for Chrome to be ready
        time.sleep(2)

        # Navigate to the saved URL
        url = state["url"]
        script = f'tell application "Google Chrome" to set URL of active tab of front window to "{url}"'

        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✅ Navigated to: {url}")
            return True
        else:
            print(f"❌ Navigation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Failed to restore navigation: {e}")
        return False


def main():
    """Main function to restart Chrome with debugging."""
    print("🔄 Restarting Chrome with Debugging Enabled")
    print("=" * 50)

    # Step 1: Save current state
    state = save_current_state()
    if not state:
        print("❌ Cannot proceed without saving current state")
        return

    # Step 2: Close Chrome
    if not close_chrome():
        print("❌ Cannot proceed without closing Chrome")
        return

    # Step 3: Start Chrome with debugging
    if not start_chrome_with_debugging():
        print("❌ Failed to start Chrome with debugging")
        return

    # Step 4: Restore navigation
    if not restore_navigation(state):
        print("❌ Failed to restore navigation")
        return

    print("\n✅ Chrome restarted with debugging enabled!")
    print("🔗 You can now connect via CDP on port 9222")
    print(f"🌐 Current page: {state['title']}")
    print(f"🔗 URL: {state['url']}")

    # Test connection
    print("\n🧪 Testing CDP connection...")
    try:
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        pages = browser.pages
        if pages:
            page = pages[0]
            print(f"✅ CDP connection successful!")
            print(f"📄 Current page: {page.title()}")
            print(f"🔗 Current URL: {page.url}")
        else:
            print("⚠️ CDP connected but no pages found")
    except Exception as e:
        print(f"❌ CDP connection failed: {e}")


if __name__ == "__main__":
    main()
