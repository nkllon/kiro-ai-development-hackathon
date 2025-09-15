#!/usr/bin/env python3
"""
Safe Navigation Helper
=====================

Interactive helper for DevPost navigation without automatic clicking.
Shows available options and lets you choose what to do next.

Author: Beast Mode Framework
Date: 2025-01-14
Purpose: Safe DevPost navigation assistance
"""

import sys
import json
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

def get_page_info():
    """Get current page information without making changes."""
    try:
        response = requests.get("http://localhost:9222/json")
        pages_info = response.json()
        
        devpost_page_info = None
        for p_info in pages_info:
            if "devpost.com" in p_info.get("url", "") or "github.com" in p_info.get("url", ""):
                devpost_page_info = p_info
                break
        
        if devpost_page_info:
            print(f"📄 Current page: {devpost_page_info['title']}")
            print(f"🔗 Current URL: {devpost_page_info['url']}")
            return devpost_page_info
        else:
            print("❌ No DevPost or GitHub page found")
            return None
            
    except Exception as e:
        print(f"❌ Error getting page info: {e}")
        return None

def show_navigation_options():
    """Show available navigation options without clicking."""
    print("\n" + "="*60)
    print("🎯 AVAILABLE NAVIGATION OPTIONS")
    print("="*60)
    
    print("\n🔘 Other Navigation Options:")
    print("   • Continue with Google (button)")
    print("   • Sign in with a passkey (button)")
    print("   • Manage cookies (button)")
    print("   • Do not share my personal information (button)")
    
    print("\n📋 What would you like to do?")
    print("   1. Continue with Google")
    print("   2. Sign in with a passkey")
    print("   3. Manage cookies")
    print("   4. Do not share my personal information")
    print("   5. Just show me the page content")
    print("   6. Take a screenshot")
    print("   7. Go back to DevPost")
    print("   0. Exit")
    
    return input("\n🎯 Enter your choice (0-7): ").strip()

def show_page_content():
    """Show page content without making changes."""
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages
        
        # Find the current page
        target_page = None
        for page in pages:
            if "devpost.com" in page.url or "github.com" in page.url:
                target_page = page
                break
        
        if target_page:
            print(f"\n📄 Page Title: {target_page.title()}")
            print(f"🔗 Page URL: {target_page.url}")
            
            # Get visible text content
            content = target_page.locator("body").text_content()
            if content:
                print(f"\n📝 Page Content Preview (first 500 chars):")
                print("-" * 50)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 50)
            
            # Get available buttons/links
            buttons = target_page.locator("button, input[type='button'], input[type='submit'], a").all()
            print(f"\n🔘 Available Interactive Elements ({len(buttons)} found):")
            for i, button in enumerate(buttons[:10], 1):  # Show first 10
                try:
                    text = button.text_content() or button.get_attribute("value") or button.get_attribute("title") or "No text"
                    element_type = button.tag_name.lower()
                    print(f"   {i}. {element_type}: {text[:50]}")
                except:
                    print(f"   {i}. [Could not read element]")
            
            if len(buttons) > 10:
                print(f"   ... and {len(buttons) - 10} more elements")
        
        browser.close()
        playwright.stop()
        
    except Exception as e:
        print(f"❌ Error showing page content: {e}")

def take_screenshot():
    """Take a screenshot of the current page."""
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages
        
        # Find the current page
        target_page = None
        for page in pages:
            if "devpost.com" in page.url or "github.com" in page.url:
                target_page = page
                break
        
        if target_page:
            timestamp = Path(__file__).stem + "_" + str(int(time.time()))
            screenshot_path = f"devpost_navigation_{timestamp}.png"
            target_page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
        else:
            print("❌ No suitable page found for screenshot")
        
        browser.close()
        playwright.stop()
        
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")

def main():
    """Main interactive loop."""
    print("🛡️  Safe DevPost Navigation Helper")
    print("="*50)
    print("This helper shows you options without automatically clicking anything.")
    
    while True:
        # Get current page info
        page_info = get_page_info()
        if not page_info:
            print("❌ No browser session found. Please start Chrome with --remote-debugging-port=9222")
            break
        
        # Show options
        choice = show_navigation_options()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            print("✅ You chose: Continue with Google")
            print("💡 You can manually click this button in the browser")
        elif choice == "2":
            print("✅ You chose: Sign in with a passkey")
            print("💡 You can manually click this button in the browser")
        elif choice == "3":
            print("✅ You chose: Manage cookies")
            print("💡 You can manually click this button in the browser")
        elif choice == "4":
            print("✅ You chose: Do not share my personal information")
            print("💡 You can manually click this button in the browser")
        elif choice == "5":
            show_page_content()
        elif choice == "6":
            take_screenshot()
        elif choice == "7":
            print("✅ You chose: Go back to DevPost")
            print("💡 You can manually navigate back in the browser")
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    import time
    main()
