#!/usr/bin/env python3
"""
Heuristic Page Analyzer
======================

Heuristically analyze page data and events to detect when pages flip
and when navigation is complete.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Heuristic analysis of page state changes
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def analyze_page_heuristics():
    """Heuristically analyze page state and changes."""
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
        
        # Heuristic analysis function
        def analyze_page_state(page, label=""):
            """Analyze current page state heuristically."""
            print(f"\n🔍 {label} Page State Analysis:")
            
            # Basic page info
            url = page.url
            title = page.title()
            print(f"   URL: {url}")
            print(f"   Title: {title}")
            
            # Extract step information from URL
            url_parts = url.split("/")
            step_info = {}
            if "submission" in url:
                try:
                    submission_idx = url_parts.index("submission")
                    if submission_idx + 1 < len(url_parts):
                        submission_id = url_parts[submission_idx + 1]
                        step_info["submission_id"] = submission_id
                    if submission_idx + 2 < len(url_parts):
                        current_step = url_parts[submission_idx + 2]
                        step_info["current_step"] = current_step
                except:
                    pass
            
            print(f"   Step Info: {step_info}")
            
            # Analyze step navigation
            step_links = page.query_selector_all("#steps-navigation a.step")
            step_analysis = []
            
            for step in step_links:
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                href = step.get_attribute("href") or ""
                is_visible = step.is_visible()
                is_enabled = step.is_enabled()
                
                step_data = {
                    "text": text,
                    "classes": classes,
                    "href": href,
                    "visible": is_visible,
                    "enabled": is_enabled
                }
                
                # Extract step from href
                if "/submission/" in href:
                    try:
                        href_parts = href.split("/")
                        submission_idx = href_parts.index("submission")
                        if submission_idx + 2 < len(href_parts):
                            step_name = href_parts[submission_idx + 2]
                            step_data["step_name"] = step_name
                    except:
                        pass
                
                step_analysis.append(step_data)
            
            print(f"   Step Navigation: {len(step_analysis)} steps")
            for i, step in enumerate(step_analysis, 1):
                status = "📍 CURRENT" if "current" in step["classes"] else "✅ COMPLETED" if "completed" in step["classes"] else "⏳ AVAILABLE"
                print(f"      {i}. {step['text']} [{step['classes']}] {status}")
                if "step_name" in step:
                    print(f"         -> {step['step_name']}")
            
            # Analyze form content
            forms = page.query_selector_all("form")
            form_analysis = []
            
            for form in forms:
                form_data = {
                    "action": form.get_attribute("action") or "",
                    "method": form.get_attribute("method") or "get",
                    "id": form.get_attribute("id") or "",
                    "class": form.get_attribute("class") or ""
                }
                
                # Count inputs
                inputs = form.query_selector_all("input, textarea, select")
                form_data["input_count"] = len(inputs)
                
                # Check for specific form types
                if "project" in form_data["class"].lower():
                    form_data["type"] = "project_form"
                elif "team" in form_data["class"].lower():
                    form_data["type"] = "team_form"
                elif "additional" in form_data["class"].lower():
                    form_data["type"] = "additional_form"
                else:
                    form_data["type"] = "unknown"
                
                form_analysis.append(form_data)
            
            print(f"   Forms: {len(form_analysis)}")
            for i, form in enumerate(form_analysis, 1):
                print(f"      {i}. {form['type']} ({form['input_count']} inputs)")
            
            # Analyze page content for step indicators
            content_indicators = []
            
            # Look for step indicators in the page
            step_indicators = page.query_selector_all("[class*='step'], [id*='step'], [data-step]")
            for indicator in step_indicators:
                text = indicator.text_content().strip()
                classes = indicator.get_attribute("class") or ""
                step_id = indicator.get_attribute("id") or ""
                data_step = indicator.get_attribute("data-step") or ""
                
                if text or classes or step_id or data_step:
                    content_indicators.append({
                        "text": text,
                        "classes": classes,
                        "id": step_id,
                        "data_step": data_step
                    })
            
            print(f"   Step Indicators: {len(content_indicators)}")
            for indicator in content_indicators[:5]:  # Show first 5
                print(f"      - {indicator['text']} [{indicator['classes']}]")
            
            return {
                "url": url,
                "title": title,
                "step_info": step_info,
                "step_analysis": step_analysis,
                "form_analysis": form_analysis,
                "content_indicators": content_indicators
            }
        
        # Analyze initial state
        initial_state = analyze_page_state(target_page, "INITIAL")
        
        # Find next step to navigate to
        next_step = None
        current_found = False
        
        for step in initial_state["step_analysis"]:
            if "current" in step["classes"]:
                current_found = True
                print(f"\n📍 Current step: {step['text']}")
                continue
            
            if current_found and "current" not in step["classes"] and step["visible"] and step["enabled"]:
                next_step = step
                print(f"➡️ Next step: {step['text']}")
                break
        
        if not next_step:
            print("❌ No next step found")
            return
        
        # Attempt navigation with monitoring
        print(f"\n🔄 Attempting navigation to: {next_step['text']}")
        print(f"   -> {next_step['href']}")
        
        # Set up monitoring
        navigation_start = time.time()
        initial_url = target_page.url
        
        # Click and monitor
        try:
            # Find the actual element
            step_element = None
            for step in target_page.query_selector_all("#steps-navigation a.step"):
                if step.text_content().strip() == next_step["text"]:
                    step_element = step
                    break
            
            if not step_element:
                print("❌ Could not find step element")
                return
            
            print(f"✅ Found step element, clicking...")
            step_element.click()
            
            # Monitor for changes
            print(f"⏳ Monitoring for changes...")
            
            # Check multiple times for changes
            for i in range(10):
                time.sleep(0.5)
                
                current_url = target_page.url
                current_title = target_page.title()
                
                print(f"   Check {i+1}: URL={current_url}, Title={current_title}")
                
                # Check if URL changed
                if current_url != initial_url:
                    print(f"✅ URL CHANGED! {initial_url} -> {current_url}")
                    break
                
                # Check if title changed
                if current_title != initial_state["title"]:
                    print(f"✅ TITLE CHANGED! {initial_state['title']} -> {current_title}")
                    break
                
                # Check if step navigation changed
                current_steps = target_page.query_selector_all("#steps-navigation a.step")
                if len(current_steps) != len(initial_state["step_analysis"]):
                    print(f"✅ STEP COUNT CHANGED! {len(initial_state['step_analysis'])} -> {len(current_steps)}")
                    break
                
                # Check for current step change
                current_step_found = False
                for step in current_steps:
                    if "current" in step.get_attribute("class") or "":
                        current_step_found = True
                        current_step_text = step.text_content().strip()
                        if current_step_text != next_step["text"]:
                            print(f"✅ CURRENT STEP CHANGED! {next_step['text']} -> {current_step_text}")
                            break
                
                if current_step_found:
                    break
            
            # Final analysis
            final_state = analyze_page_state(target_page, "FINAL")
            
            # Compare states
            print(f"\n📊 State Comparison:")
            print(f"   URL changed: {initial_state['url']} -> {final_state['url']}")
            print(f"   Title changed: {initial_state['title']} -> {final_state['title']}")
            print(f"   Step count: {len(initial_state['step_analysis'])} -> {len(final_state['step_analysis'])}")
            
            # Check if we're on a different step
            if final_state["step_info"].get("current_step") != initial_state["step_info"].get("current_step"):
                print(f"✅ STEP NAVIGATION SUCCESSFUL!")
                print(f"   From: {initial_state['step_info'].get('current_step', 'unknown')}")
                print(f"   To: {final_state['step_info'].get('current_step', 'unknown')}")
            else:
                print(f"⚠️ No step change detected")
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Heuristic analysis failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    analyze_page_heuristics()







