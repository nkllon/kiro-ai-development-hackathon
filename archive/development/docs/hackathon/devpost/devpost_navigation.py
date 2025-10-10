#!/usr/bin/env python3
"""
DevPost Navigation Script
=========================

Navigate to DevPost and analyze the submission page.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Navigate to DevPost and analyze the page."""
    print("🔍 DevPost Navigation and Analysis")
    print("=" * 50)
    
    # Your DevPost URL
    devpost_url = "https://kiro.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Submissions+open&_gl=1*1b0lbpj*_gcl_au*MTEzNDU0OTI1Mi4xNzU2NDA5NzU1*_ga*MTA2NTYyNjg3OS4xNzU2NDA5NzU1*_ga_0YHJK3Y10M*czE3NTc5NjE1MTAkbzMwJGcwJHQxNzU3OTYxNTEwJGo2MCRsMCRoMA.."
    
    try:
        # Start Playwright
        print("🚀 Starting Playwright...")
        playwright = sync_playwright().start()
        
        # Connect to existing Chrome instance
        print("🔌 Connecting to existing Chrome...")
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        
        # Create a new page
        print("📄 Creating new page...")
        page = browser.new_page()
        
        # Navigate to DevPost
        print(f"🌐 Navigating to DevPost...")
        page.goto(devpost_url)
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        page.wait_for_load_state("networkidle", timeout=30000)
        
        # Get page info
        title = page.title()
        url = page.url
        print(f"📄 Page title: {title}")
        print(f"🔗 Current URL: {url}")
        
        # Take screenshot
        timestamp = int(time.time())
        screenshot_path = f"devpost_page_{timestamp}.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Analyze page elements
        print("\n🔍 Analyzing page elements...")
        
        # Count elements
        forms = page.query_selector_all("form")
        buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
        inputs = page.query_selector_all("input, textarea, select")
        links = page.query_selector_all("a")
        
        print(f"📊 Elements found:")
        print(f"   Forms: {len(forms)}")
        print(f"   Buttons: {len(buttons)}")
        print(f"   Inputs: {len(inputs)}")
        print(f"   Links: {len(links)}")
        
        # Look for specific DevPost elements
        print("\n🎯 Looking for DevPost-specific elements...")
        
        # Check for common DevPost text
        devpost_keywords = [
            "My projects", "Edit project", "Submit project", "Project name",
            "Elevator pitch", "Built with", "Try it out", "Learn more"
        ]
        
        found_keywords = []
        for keyword in devpost_keywords:
            try:
                element = page.query_selector(f"text={keyword}")
                if element:
                    found_keywords.append(keyword)
                    print(f"   ✅ Found: {keyword}")
            except:
                continue
        
        # Analyze forms in detail
        if forms:
            print(f"\n📝 Form Analysis:")
            for i, form in enumerate(forms, 1):
                form_id = form.get_attribute("id") or f"form_{i}"
                form_action = form.get_attribute("action") or ""
                field_count = len(form.query_selector_all("input, textarea, select"))
                
                print(f"   Form {i}: {form_id}")
                print(f"      Action: {form_action}")
                print(f"      Fields: {field_count}")
                
                # Show first few fields
                fields = form.query_selector_all("input, textarea, select")
                for j, field in enumerate(fields[:5], 1):
                    try:
                        field_type = field.get_attribute("type") or field.evaluate("el => el.tagName").lower()
                        name = field.get_attribute("name") or ""
                        placeholder = field.get_attribute("placeholder") or ""
                        
                        print(f"         Field {j}: {name} ({field_type})")
                        if placeholder:
                            print(f"            Placeholder: {placeholder}")
                    except Exception as e:
                        print(f"         Field {j}: Error - {e}")
        
        # Look for navigation buttons
        print(f"\n🧭 Navigation Analysis:")
        nav_keywords = ["next", "continue", "back", "previous", "submit", "save", "finish"]
        
        for button in buttons:
            try:
                text = button.text_content().strip().lower()
                if any(keyword in text for keyword in nav_keywords):
                    print(f"   🎯 Navigation button: {button.text_content().strip()}")
            except:
                continue
        
        # Interactive mode
        print(f"\n🎮 Interactive Mode")
        print("Commands: analyze, screenshot, navigate, quit")
        
        while True:
            try:
                command = input("🔧 Command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "analyze":
                    # Re-analyze
                    forms = page.query_selector_all("form")
                    buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
                    print(f"📊 Current state: {len(forms)} forms, {len(buttons)} buttons")
                elif command == "screenshot":
                    timestamp = int(time.time())
                    filename = f"interactive_screenshot_{timestamp}.png"
                    page.screenshot(path=filename)
                    print(f"📸 Screenshot: {filename}")
                elif command == "navigate":
                    url = input("Enter URL to navigate to: ")
                    page.goto(url)
                    page.wait_for_load_state("networkidle")
                    print(f"🌐 Navigated to: {page.url}")
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
