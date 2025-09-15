#!/usr/bin/env python3
"""
Connect to Existing Page
========================

Connect to the EXISTING page in the browser, don't create new ones.
Just analyze what's already there.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Connect to existing page without creating new sessions
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Connect to existing page and analyze it."""
    print("🔌 Connecting to Existing Page")
    print("=" * 40)
    
    try:
        # Start Playwright
        playwright = sync_playwright().start()
        
        # Connect to existing browser via CDP
        print("🔍 Connecting to existing browser on port 9222...")
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        print("✅ Connected to existing browser!")
        
        # Get existing pages - don't create new ones!
        try:
            pages = browser.pages
            if not pages:
                print("❌ No existing pages found!")
                return
            
            print(f"📄 Found {len(pages)} existing pages")
            
            # Use the first page
            page = pages[0]
            print(f"📄 Using page: {page.url}")
            print(f"📄 Page title: {page.title()}")
            
            # Analyze the page
            print(f"\n🔍 Analyzing current page...")
            
            # Count elements
            forms = page.query_selector_all("form")
            buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
            inputs = page.query_selector_all("input, textarea, select")
            links = page.query_selector_all("a")
            images = page.query_selector_all("img")
            
            print(f"📊 Elements found:")
            print(f"   Forms: {len(forms)}")
            print(f"   Buttons: {len(buttons)}")
            print(f"   Inputs: {len(inputs)}")
            print(f"   Links: {len(links)}")
            print(f"   Images: {len(images)}")
            
            # Analyze forms
            if forms:
                print(f"\n📝 Form Analysis:")
                for i, form in enumerate(forms, 1):
                    form_id = form.get_attribute("id") or f"form_{i}"
                    form_class = form.get_attribute("class") or ""
                    form_action = form.get_attribute("action") or ""
                    field_count = len(form.query_selector_all("input, textarea, select"))
                    
                    print(f"   Form {i}: {form_id}")
                    print(f"      Class: {form_class}")
                    print(f"      Action: {form_action}")
                    print(f"      Fields: {field_count}")
                    
                    # Analyze fields in this form
                    fields = form.query_selector_all("input, textarea, select")
                    for j, field in enumerate(fields[:5], 1):  # Show first 5 fields
                        try:
                            field_type = field.get_attribute("type") or field.evaluate("el => el.tagName").lower()
                            name = field.get_attribute("name") or ""
                            element_id = field.get_attribute("id") or ""
                            placeholder = field.get_attribute("placeholder") or ""
                            value = field.get_attribute("value") or ""
                            required = field.get_attribute("required") is not None
                            
                            # Get label
                            label = "Unlabeled"
                            if element_id:
                                label_elem = page.query_selector(f"label[for='{element_id}']")
                                if label_elem:
                                    label = label_elem.text_content().strip()
                            
                            print(f"      Field {j}: {label} ({field_type})")
                            if name:
                                print(f"         Name: {name}")
                            if placeholder:
                                print(f"         Placeholder: {placeholder}")
                            if value:
                                print(f"         Value: {value[:50]}...")
                            if required:
                                print(f"         Required: Yes")
                        except Exception as e:
                            print(f"      Field {j}: Error analyzing - {e}")
            
            # Analyze buttons
            if buttons:
                print(f"\n🔘 Button Analysis:")
                for i, button in enumerate(buttons[:10], 1):  # Show first 10
                    try:
                        text = button.text_content().strip()
                        button_type = button.get_attribute("type") or "button"
                        classes = button.get_attribute("class") or ""
                        is_visible = button.is_visible()
                        is_enabled = button.is_enabled()
                        
                        if text and len(text) < 100:
                            status = "✅" if is_visible and is_enabled else "❌"
                            print(f"   {status} {text} (type: {button_type})")
                    except Exception as e:
                        print(f"   Button {i}: Error analyzing - {e}")
            
            # Take screenshot
            try:
                timestamp = int(time.time())
                url_parts = page.url.split("/")
                hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
                submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
                page_title = page.title().replace(" ", "_").replace("/", "_")[:20]
                
                filename = f"existing_page_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
                page.screenshot(path=filename)
                print(f"📸 Screenshot: {filename}")
            except Exception as e:
                print(f"❌ Screenshot failed: {e}")
            
            # Interactive mode
            print(f"\n🎮 Interactive Mode")
            print("Commands: analyze, screenshot, quit")
            
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
                        try:
                            timestamp = int(time.time())
                            filename = f"interactive_screenshot_{timestamp}.png"
                            page.screenshot(path=filename)
                            print(f"📸 Screenshot: {filename}")
                        except Exception as e:
                            print(f"❌ Screenshot failed: {e}")
                    else:
                        print("❌ Unknown command")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
            
        except AttributeError:
            print("❌ Browser doesn't have pages attribute - this is a connection issue")
            return
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()





