#!/usr/bin/env python3
"""
Debug Navigation
===============

Debug version that gives real-time feedback about navigation attempts
and page changes.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Debug navigation with detailed feedback
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_navigation():
    """Debug navigation with detailed feedback."""
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
        
        # Set up page event listeners for debugging
        print("🎧 Setting up page event listeners...")
        
        def on_navigation(url):
            print(f"🔄 NAVIGATION EVENT: {url}")
        
        def on_load():
            print(f"📄 PAGE LOAD EVENT: {target_page.title()}")
        
        def on_dom_content_loaded():
            print(f"🏗️  DOM CONTENT LOADED: {target_page.url}")
        
        # Add event listeners
        target_page.on("framenavigated", on_navigation)
        target_page.on("load", on_load)
        target_page.on("domcontentloaded", on_dom_content_loaded)
        
        # Single navigation attempt with detailed feedback
        print(f"\n{'='*60}")
        print(f"🔍 DEBUG NAVIGATION ATTEMPT")
        print(f"{'='*60}")
        
        print(f"📄 Current page: {target_page.title()}")
        print(f"🔗 Current URL: {target_page.url}")
        
        # Get visible step navigation links
        step_links = target_page.query_selector_all("#steps-navigation a.step")
        visible_steps = []
        
        print(f"\n🎯 Step Navigation Analysis:")
        for i, step in enumerate(step_links, 1):
            text = step.text_content().strip()
            classes = step.get_attribute("class") or ""
            href = step.get_attribute("href") or ""
            is_visible = step.is_visible()
            is_enabled = step.is_enabled()
            bounding_box = step.bounding_box()
            
            if is_visible and is_enabled:
                visible_steps.append({
                    "element": step,
                    "text": text,
                    "classes": classes,
                    "href": href,
                    "position": bounding_box
                })
                status = "📍 CURRENT" if "current" in classes else "✅ COMPLETED" if "completed" in classes else "⏳ AVAILABLE"
                print(f"   {i}. {text} [{classes}] {status}")
                print(f"      -> {href}")
                print(f"      Position: {bounding_box}")
            else:
                print(f"   {i}. {text} [{classes}] ❌ HIDDEN/DISABLED")
        
        # Find next step
        next_step = None
        current_found = False
        
        for step in visible_steps:
            if "current" in step["classes"]:
                current_found = True
                print(f"📍 Found current step: {step['text']}")
                continue
            
            if current_found and "current" not in step["classes"]:
                next_step = step
                print(f"➡️ Found next step: {step['text']}")
                break
        
        if not next_step:
            print("❌ No next step found")
            return
        
        print(f"\n🎯 Attempting navigation to: {next_step['text']}")
        print(f"   -> {next_step['href']}")
        print(f"   Position: {next_step['position']}")
        
        # Record initial state
        initial_url = target_page.url
        initial_title = target_page.title()
        
        print(f"\n📊 Initial State:")
        print(f"   URL: {initial_url}")
        print(f"   Title: {initial_title}")
        
        # Attempt click with detailed feedback
        print(f"\n🔄 Clicking element...")
        try:
            # Use force click to bypass visibility checks
            next_step["element"].click(force=True)
            print(f"✅ Click executed successfully")
            
            # Wait a bit for navigation
            print(f"⏳ Waiting for navigation...")
            time.sleep(2)
            
            # Check for navigation
            new_url = target_page.url
            new_title = target_page.title()
            
            print(f"\n📊 After Click State:")
            print(f"   URL: {new_url}")
            print(f"   Title: {new_title}")
            
            if new_url != initial_url:
                print(f"✅ NAVIGATION SUCCESSFUL!")
                print(f"   URL changed: {initial_url} -> {new_url}")
                if new_title != initial_title:
                    print(f"   Title changed: {initial_title} -> {new_title}")
            else:
                print(f"⚠️ No URL change detected")
                
                # Check if we're still on the same page
                current_step_links = target_page.query_selector_all("#steps-navigation a.step")
                current_visible = []
                for step in current_step_links:
                    if step.is_visible() and step.is_enabled():
                        text = step.text_content().strip()
                        classes = step.get_attribute("class") or ""
                        if "current" in classes:
                            current_visible.append(text)
                
                print(f"   Current visible steps: {current_visible}")
            
        except Exception as e:
            print(f"❌ Click failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Take final screenshot
        timestamp = int(time.time())
        url_parts = target_page.url.split("/")
        hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
        submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
        page_title = target_page.title().replace(" ", "_").replace("/", "_")[:20]
        
        filename = f"debug_nav_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
        target_page.screenshot(path=filename)
        print(f"📸 Final screenshot: {filename}")
        
    except Exception as e:
        print(f"❌ Debug navigation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    debug_navigation()







