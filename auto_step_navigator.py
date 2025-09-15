#!/usr/bin/env python3
"""
Auto Step Navigator
==================

Automatically navigate through DevPost form steps by clicking
the next available step link.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Automatic step-by-step navigation
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def auto_navigate_steps():
    """Automatically navigate through DevPost form steps."""
    try:
        playwright = sync_playwright().start()
        
        # Get page info
        response = requests.get("http://localhost:9222/json")
        pages_info = response.json()
        
        devpost_page_info = None
        for p_info in pages_info:
            if "devpost.com" in p_info.get("url", "") and "submission" in p_info.get("url", ""):
                devpost_page_info = p_info
                break
        
        if not devpost_page_info:
            print("❌ No DevPost submission page found")
            return
        
        print(f"📄 Target page: {devpost_page_info['title']}")
        print(f"🔗 URL: {devpost_page_info['url']}")
        
        # Connect to browser
        print("🔍 Connecting to existing browser...")
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages
        
        # Find DevPost page
        target_page = None
        for page in pages:
            if "devpost.com" in page.url and "submission" in page.url:
                target_page = page
                break
        
        if not target_page:
            target_page = pages[0]
        
        print(f"✅ Connected to: {target_page.url}")
        
        # Wait for page to be ready
        print("⏳ Waiting for page to be ready...")
        target_page.wait_for_load_state("networkidle")
        
        # Auto-navigation loop
        navigation_count = 0
        max_navigations = 10
        
        while navigation_count < max_navigations:
            print(f"\n{'='*60}")
            print(f"🔄 Auto Navigation Step {navigation_count + 1}")
            print(f"📄 Current page: {target_page.title()}")
            print(f"🔗 Current URL: {target_page.url}")
            
            # Get visible step navigation links
            step_links = target_page.query_selector_all("#steps-navigation a.step")
            visible_steps = []
            
            print(f"\n🎯 Available Step Navigation:")
            for i, step in enumerate(step_links, 1):
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                href = step.get_attribute("href") or ""
                is_visible = step.is_visible()
                is_enabled = step.is_enabled()
                
                if is_visible and is_enabled:
                    visible_steps.append({
                        "element": step,
                        "text": text,
                        "classes": classes,
                        "href": href
                    })
                    status = "📍 CURRENT" if "current" in classes else "✅ COMPLETED" if "completed" in classes else "⏳ AVAILABLE"
                    print(f"   {i}. {text} [{classes}] {status}")
                else:
                    print(f"   {i}. {text} [{classes}] ❌ HIDDEN/DISABLED")
            
            # Find the next step to navigate to
            next_step = None
            current_found = False
            
            for step in visible_steps:
                if "current" in step["classes"]:
                    current_found = True
                    continue
                
                if current_found and "current" not in step["classes"]:
                    next_step = step
                    break
            
            # If no next step found, try to find any available step
            if not next_step:
                for step in visible_steps:
                    if "current" not in step["classes"] and "completed" not in step["classes"]:
                        next_step = step
                        break
            
            if next_step:
                print(f"\n🎯 Navigating to: {next_step['text']}")
                print(f"   -> {next_step['href']}")
                
                try:
                    next_step["element"].click()
                    target_page.wait_for_load_state("networkidle")
                    
                    # Check if navigation actually occurred
                    new_url = target_page.url
                    if new_url != target_page.url:
                        print(f"✅ Navigation successful!")
                        print(f"📄 New page: {target_page.title()}")
                        print(f"🔗 New URL: {new_url}")
                        navigation_count += 1
                    else:
                        print(f"⚠️ No navigation detected")
                        break
                        
                except Exception as e:
                    print(f"❌ Navigation failed: {e}")
                    break
            else:
                print("❌ No next step found to navigate to")
                break
            
            # Take screenshot
            timestamp = int(time.time())
            url_parts = target_page.url.split("/")
            hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
            submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
            page_title = target_page.title().replace(" ", "_").replace("/", "_")[:20]
            
            filename = f"auto_nav_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
            target_page.screenshot(path=filename)
            print(f"📸 Screenshot: {filename}")
        
        print(f"\n🏁 Auto navigation complete after {navigation_count} steps")
        
        # Final analysis
        print(f"\n📊 Final Page Analysis:")
        print(f"📄 Title: {target_page.title()}")
        print(f"🔗 URL: {target_page.url}")
        
        forms = target_page.query_selector_all("form")
        inputs = target_page.query_selector_all("input, textarea, select")
        buttons = target_page.query_selector_all("button, input[type='button'], input[type='submit']")
        
        print(f"📊 Elements: {len(forms)} forms, {len(buttons)} buttons, {len(inputs)} inputs")
        
    except Exception as e:
        print(f"❌ Auto navigation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    auto_navigate_steps()





