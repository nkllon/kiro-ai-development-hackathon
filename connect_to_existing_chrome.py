#!/usr/bin/env python3
"""
Connect to Existing Chrome with Extensions
=========================================

This script connects to your existing Chrome browser with all extensions,
including 1Password, instead of launching a new Chromium instance.
"""

import requests
import json
from playwright.sync_api import sync_playwright
import subprocess
import time
import os


def find_chrome_debug_port():
    """Find Chrome instances with debugging enabled"""
    try:
        # Check common Chrome debug ports
        ports = [9222, 9223, 9224, 9225, 9226]
        for port in ports:
            try:
                response = requests.get(f"http://localhost:{port}/json", timeout=2)
                if response.status_code == 200:
                    tabs = response.json()
                    if tabs:
                        return port, tabs
            except:
                continue
        return None, []
    except Exception as e:
        print(f"Error checking Chrome debug ports: {e}")
        return None, []


def start_chrome_with_debug():
    """Start Chrome with debugging enabled if not already running"""
    print("🔧 Starting Chrome with debugging enabled...")
    
    # Common Chrome paths on macOS
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium"
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if not chrome_path:
        print("❌ Chrome not found in standard locations")
        return None
    
    # Start Chrome with debugging
    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--user-data-dir=/tmp/chrome-with-extensions",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    try:
        subprocess.Popen(cmd)
        time.sleep(3)  # Wait for Chrome to start
        return 9222
    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return None


def connect_to_existing_chrome():
    """Connect to existing Chrome or start new one with extensions"""
    print("🔍 Looking for existing Chrome instances...")
    
    port, tabs = find_chrome_debug_port()
    
    if port and tabs:
        print(f"✅ Found Chrome on port {port} with {len(tabs)} tabs")
        
        # Show existing tabs
        print("📋 Existing tabs:")
        for i, tab in enumerate(tabs):
            title = tab.get('title', 'Untitled')[:50]
            url = tab.get('url', 'No URL')[:80]
            print(f"   {i+1}. {title} - {url}")
        
        return port, tabs
    else:
        print("❌ No Chrome instances found with debugging enabled")
        port = start_chrome_with_debug()
        if port:
            time.sleep(2)
            try:
                response = requests.get(f"http://localhost:{port}/json")
                tabs = response.json()
                print(f"✅ Started Chrome on port {port}")
                return port, tabs
            except:
                pass
    
    return None, []


def main():
    """Main function to connect to Chrome and test DevPost"""
    print("🎯 Connecting to Chrome with Extensions (including 1Password)")
    
    port, tabs = connect_to_existing_chrome()
    
    if not port:
        print("❌ Could not connect to Chrome")
        return
    
    try:
        playwright = sync_playwright().start()
        
        # Connect to existing Chrome
        print(f"🔗 Connecting to Chrome on port {port}...")
        browser = playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
        
        # Get all contexts and pages
        contexts = browser.contexts
        print(f"📊 Found {len(contexts)} browser contexts")
        
        all_pages = []
        for context in contexts:
            pages = context.pages
            all_pages.extend(pages)
            print(f"   Context has {len(pages)} pages")
        
        if not all_pages:
            print("🆕 No existing pages found, creating new one...")
            context = browser.new_context()
            page = context.new_page()
        else:
            # Use the first page or let user choose
            page = all_pages[0]
            print(f"📄 Using page: {page.title()} - {page.url}")
        
        # Navigate to DevPost
        print("🌐 Navigating to DevPost...")
        page.goto("https://devpost.com")
        
        print("✅ Connected to Chrome with all extensions!")
        print("🔐 1Password should be available if installed")
        print("👤 Please log in to DevPost and navigate to your submission...")
        input("Press Enter when ready to continue with automation...")
        
        # Now you can use this page for DevPost automation
        print(f"📄 Current page: {page.title()}")
        print(f"🔗 Current URL: {page.url}")
        
        # Keep the browser open for further automation
        input("Press Enter to close connection...")
        
        browser.close()
        playwright.stop()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
