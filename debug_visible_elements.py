#!/usr/bin/env python3
"""
Debug Visible Elements
=====================

Debug script to see what elements are actually visible and clickable
on the current DevPost page.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Debug element visibility issues
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_visible_elements():
    """Debug what elements are actually visible on the page."""
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
        
        # Check what's actually visible
        print("\n🔍 Checking visible elements...")
        
        # Check step navigation
        print("\n📊 Step Navigation Analysis:")
        steps_container = target_page.query_selector("#steps-navigation")
        if steps_container:
            print("✅ Steps container found")
            is_visible = steps_container.is_visible()
            print(f"   Visible: {is_visible}")
            
            if is_visible:
                bounding_box = steps_container.bounding_box()
                print(f"   Position: {bounding_box}")
            
            # Check individual step links
            step_links = target_page.query_selector_all("#steps-navigation a.step")
            print(f"   Step links found: {len(step_links)}")
            
            for i, step in enumerate(step_links[:5], 1):
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                is_visible = step.is_visible()
                is_enabled = step.is_enabled()
                bounding_box = step.bounding_box()
                
                print(f"   {i}. '{text}' [{classes}]")
                print(f"      Visible: {is_visible}, Enabled: {is_enabled}")
                if bounding_box:
                    print(f"      Position: {bounding_box}")
                else:
                    print(f"      Position: None (not in viewport)")
        else:
            print("❌ Steps container not found")
        
        # Check buttons
        print("\n🔘 Button Analysis:")
        buttons = target_page.query_selector_all("button, input[type='button'], input[type='submit']")
        print(f"   Total buttons found: {len(buttons)}")
        
        visible_buttons = []
        for i, button in enumerate(buttons[:10], 1):
            text = button.text_content().strip()
            is_visible = button.is_visible()
            is_enabled = button.is_enabled()
            bounding_box = button.bounding_box()
            
            if is_visible:
                visible_buttons.append(button)
                print(f"   {i}. '{text}' - Visible: {is_visible}, Enabled: {is_enabled}")
                if bounding_box:
                    print(f"      Position: {bounding_box}")
        
        print(f"   Visible buttons: {len(visible_buttons)}")
        
        # Check links
        print("\n🔗 Link Analysis:")
        links = target_page.query_selector_all("a")
        print(f"   Total links found: {len(links)}")
        
        visible_links = []
        for i, link in enumerate(links[:10], 1):
            text = link.text_content().strip()
            href = link.get_attribute("href") or ""
            is_visible = link.is_visible()
            bounding_box = link.bounding_box()
            
            if is_visible and text:
                visible_links.append(link)
                print(f"   {i}. '{text}' -> {href[:50]}...")
                if bounding_box:
                    print(f"      Position: {bounding_box}")
        
        print(f"   Visible links: {len(visible_links)}")
        
        # Try to find navigation elements that are actually clickable
        print("\n🎯 Looking for clickable navigation elements...")
        
        # Look for any clickable elements with navigation-like text
        all_clickable = target_page.query_selector_all("a, button, input[type='button'], input[type='submit'], [onclick], [role='button']")
        
        navigation_candidates = []
        for element in all_clickable:
            try:
                text = element.text_content().strip().lower()
                if any(word in text for word in ["next", "continue", "forward", "back", "previous", "prev", "submit", "save"]):
                    is_visible = element.is_visible()
                    is_enabled = element.is_enabled()
                    bounding_box = element.bounding_box()
                    
                    if is_visible and is_enabled:
                        navigation_candidates.append({
                            "element": element,
                            "text": text,
                            "position": bounding_box
                        })
            except:
                continue
        
        print(f"   Navigation candidates: {len(navigation_candidates)}")
        for i, candidate in enumerate(navigation_candidates[:5], 1):
            print(f"   {i}. '{candidate['text']}' at {candidate['position']}")
        
        # Take a screenshot
        timestamp = int(time.time())
        url_parts = target_page.url.split("/")
        hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
        submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
        page_title = target_page.title().replace(" ", "_").replace("/", "_")[:20]
        
        filename = f"debug_visible_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
        target_page.screenshot(path=filename)
        print(f"📸 Screenshot saved: {filename}")
        
        # Try to click a visible element if we found any
        if navigation_candidates:
            print(f"\n🔄 Attempting to click first navigation candidate...")
            try:
                candidate = navigation_candidates[0]
                print(f"   Clicking: '{candidate['text']}'")
                candidate["element"].click()
                target_page.wait_for_load_state("networkidle", timeout=5000)
                print(f"   ✅ Click successful! New URL: {target_page.url}")
            except Exception as e:
                print(f"   ❌ Click failed: {e}")
        else:
            print("❌ No clickable navigation elements found")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    debug_visible_elements()







