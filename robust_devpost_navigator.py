#!/usr/bin/env python3
"""
Robust DevPost Navigator
========================

Implementation based on comprehensive model and observations.
Uses heuristics for reliable navigation detection.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Robust DevPost form navigation
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

def robust_navigate_devpost():
    """Robust DevPost navigation using model-based heuristics."""
    try:
        playwright = sync_playwright().start()
        
        # Connect to browser daemon
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
        target_page.wait_for_load_state("networkidle")
        
        # Navigation loop
        navigation_count = 0
        max_navigations = 10
        
        while navigation_count < max_navigations:
            print(f"\n{'='*60}")
            print(f"🔄 Navigation Step {navigation_count + 1}")
            print(f"📄 Current: {target_page.title()}")
            print(f"🔗 URL: {target_page.url}")
            
            # Get visible step navigation elements
            step_links = target_page.query_selector_all("#steps-navigation a.step")
            visible_steps = []
            
            for step in step_links:
                if step.is_visible() and step.is_enabled():
                    text = step.text_content().strip()
                    classes = step.get_attribute("class") or ""
                    href = step.get_attribute("href") or ""
                    
                    visible_steps.append({
                        "element": step,
                        "text": text,
                        "classes": classes,
                        "href": href
                    })
            
            print(f"🎯 Available steps: {len(visible_steps)}")
            for i, step in enumerate(visible_steps, 1):
                status = "📍 CURRENT" if "current" in step["classes"] else "✅ COMPLETED" if "completed" in step["classes"] else "⏳ AVAILABLE"
                print(f"   {i}. {step['text']} {status}")
            
            # Find next step
            next_step = None
            current_found = False
            
            for step in visible_steps:
                if "current" in step["classes"]:
                    current_found = True
                    continue
                
                if current_found and "current" not in step["classes"]:
                    next_step = step
                    break
            
            if not next_step:
                print("❌ No next step found")
                break
            
            # Record initial state
            initial_url = target_page.url
            initial_title = target_page.title()
            
            print(f"\n🎯 Navigating to: {next_step['text']}")
            print(f"   -> {next_step['href']}")
            
            try:
                # Click and monitor
                next_step["element"].click()
                
                # Wait for navigation with heuristics
                navigation_success = False
                for i in range(10):
                    time.sleep(0.5)
                    
                    current_url = target_page.url
                    if current_url != initial_url:
                        print(f"✅ URL changed: {initial_url} -> {current_url}")
                        navigation_success = True
                        break
                
                if navigation_success:
                    navigation_count += 1
                    print(f"✅ Navigation successful!")
                else:
                    print(f"⚠️ No URL change detected")
                    break
                
            except Exception as e:
                print(f"❌ Navigation failed: {e}")
                break
        
        print(f"\n🏁 Navigation complete after {navigation_count} steps")
        
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    robust_navigate_devpost()
