#!/usr/bin/env python3
"""
Explore Steps
============

Explore all DevPost form steps and build a comprehensive model
of the navigation patterns and form structures.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Build comprehensive model from observations
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def explore_all_steps():
    """Explore all DevPost form steps and build a model."""
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
        
        # Model to store observations
        devpost_model = {
            "steps": {},
            "navigation_patterns": {},
            "form_structures": {},
            "common_elements": {},
            "heuristics": {}
        }
        
        # Get all available steps
        step_links = target_page.query_selector_all("#steps-navigation a.step")
        available_steps = []
        
        print(f"\n🎯 Available Steps:")
        for i, step in enumerate(step_links, 1):
            text = step.text_content().strip()
            classes = step.get_attribute("class") or ""
            href = step.get_attribute("href") or ""
            is_visible = step.is_visible()
            is_enabled = step.is_enabled()
            
            if is_visible and is_enabled:
                available_steps.append({
                    "element": step,
                    "text": text,
                    "classes": classes,
                    "href": href,
                    "index": i
                })
                status = "📍 CURRENT" if "current" in classes else "✅ COMPLETED" if "completed" in classes else "⏳ AVAILABLE"
                print(f"   {i}. {text} [{classes}] {status}")
        
        # Explore each step
        for step_info in available_steps:
            print(f"\n{'='*60}")
            print(f"🔍 Exploring Step: {step_info['text']}")
            print(f"{'='*60}")
            
            # Navigate to step
            try:
                step_info["element"].click()
                target_page.wait_for_load_state("networkidle")
                time.sleep(2)  # Wait for page to stabilize
                
                # Analyze current step
                current_url = target_page.url
                current_title = target_page.title()
                
                print(f"📄 Current URL: {current_url}")
                print(f"📄 Current Title: {current_title}")
                
                # Extract step name from URL
                step_name = "unknown"
                if "/submission/" in current_url:
                    url_parts = current_url.split("/")
                    try:
                        submission_idx = url_parts.index("submission")
                        if submission_idx + 2 < len(url_parts):
                            step_name = url_parts[submission_idx + 2]
                    except:
                        pass
                
                print(f"📄 Step Name: {step_name}")
                
                # Analyze forms
                forms = target_page.query_selector_all("form")
                form_analysis = []
                
                for form_idx, form in enumerate(forms):
                    form_data = {
                        "index": form_idx,
                        "action": form.get_attribute("action") or "",
                        "method": form.get_attribute("method") or "get",
                        "id": form.get_attribute("id") or "",
                        "class": form.get_attribute("class") or "",
                        "inputs": []
                    }
                    
                    # Analyze inputs
                    inputs = form.query_selector_all("input, textarea, select")
                    for input_elem in inputs:
                        input_data = {
                            "type": input_elem.get_attribute("type") or input_elem.tag_name,
                            "name": input_elem.get_attribute("name") or "",
                            "id": input_elem.get_attribute("id") or "",
                            "class": input_elem.get_attribute("class") or "",
                            "placeholder": input_elem.get_attribute("placeholder") or "",
                            "value": input_elem.get_attribute("value") or "",
                            "required": input_elem.get_attribute("required") is not None
                        }
                        form_data["inputs"].append(input_data)
                    
                    form_analysis.append(form_data)
                
                print(f"📝 Forms: {len(form_analysis)}")
                for form in form_analysis:
                    print(f"   Form {form['index']}: {form['class']} ({len(form['inputs'])} inputs)")
                    for inp in form["inputs"][:5]:  # Show first 5 inputs
                        print(f"      - {inp['type']} {inp['name']} {inp['placeholder']}")
                
                # Analyze step navigation
                current_step_links = target_page.query_selector_all("#steps-navigation a.step")
                step_nav_analysis = []
                
                for step in current_step_links:
                    step_data = {
                        "text": step.text_content().strip(),
                        "classes": step.get_attribute("class") or "",
                        "href": step.get_attribute("href") or "",
                        "visible": step.is_visible(),
                        "enabled": step.is_enabled()
                    }
                    step_nav_analysis.append(step_data)
                
                print(f"🧭 Step Navigation: {len(step_nav_analysis)} steps")
                for step in step_nav_analysis:
                    status = "📍 CURRENT" if "current" in step["classes"] else "✅ COMPLETED" if "completed" in step["classes"] else "⏳ AVAILABLE"
                    print(f"   - {step['text']} [{step['classes']}] {status}")
                
                # Analyze page content
                page_content = {
                    "url": current_url,
                    "title": current_title,
                    "step_name": step_name,
                    "forms": form_analysis,
                    "step_navigation": step_nav_analysis,
                    "timestamp": time.time()
                }
                
                # Store in model
                devpost_model["steps"][step_name] = page_content
                
                # Take screenshot
                timestamp = int(time.time())
                filename = f"step_{step_name}_{timestamp}.png"
                target_page.screenshot(path=filename)
                print(f"📸 Screenshot: {filename}")
                
                # Save HTML
                html_filename = f"step_{step_name}_{timestamp}.html"
                with open(html_filename, "w", encoding="utf-8") as f:
                    f.write(target_page.content())
                print(f"📄 HTML: {html_filename}")
                
            except Exception as e:
                print(f"❌ Error exploring step {step_info['text']}: {e}")
                continue
        
        # Build navigation patterns
        print(f"\n{'='*60}")
        print(f"🧠 Building Navigation Patterns")
        print(f"{'='*60}")
        
        # Analyze step progression
        step_sequence = []
        for step_name, step_data in devpost_model["steps"].items():
            step_sequence.append({
                "name": step_name,
                "url": step_data["url"],
                "forms_count": len(step_data["forms"]),
                "total_inputs": sum(len(form["inputs"]) for form in step_data["forms"])
            })
        
        print(f"📊 Step Sequence:")
        for i, step in enumerate(step_sequence, 1):
            print(f"   {i}. {step['name']} - {step['forms_count']} forms, {step['total_inputs']} inputs")
        
        # Build heuristics
        heuristics = {
            "navigation_indicators": {
                "url_change": "Primary indicator of navigation success",
                "step_navigation_update": "Current step class moves between steps",
                "form_content_change": "Different forms appear for different steps"
            },
            "step_detection": {
                "url_pattern": "/submission/{submission_id}/{step_name}/",
                "step_names": [step["name"] for step in step_sequence],
                "navigation_selector": "#steps-navigation a.step"
            },
            "form_patterns": {
                "common_inputs": ["name", "description", "url", "github", "technologies"],
                "step_specific_inputs": {}
            }
        }
        
        # Analyze common inputs across steps
        all_inputs = []
        for step_data in devpost_model["steps"].values():
            for form in step_data["forms"]:
                for inp in form["inputs"]:
                    all_inputs.append(inp["name"])
        
        from collections import Counter
        input_counts = Counter(all_inputs)
        common_inputs = [inp for inp, count in input_counts.most_common(10) if inp]
        
        heuristics["form_patterns"]["common_inputs"] = common_inputs
        
        print(f"🔍 Common Inputs: {common_inputs}")
        
        # Store heuristics
        devpost_model["heuristics"] = heuristics
        
        # Save complete model
        model_filename = f"devpost_model_{int(time.time())}.json"
        with open(model_filename, "w", encoding="utf-8") as f:
            json.dump(devpost_model, f, indent=2, default=str)
        
        print(f"\n💾 Complete model saved: {model_filename}")
        
        # Summary
        print(f"\n📊 Model Summary:")
        print(f"   Steps explored: {len(devpost_model['steps'])}")
        print(f"   Total forms: {sum(len(step['forms']) for step in devpost_model['steps'].values())}")
        print(f"   Total inputs: {sum(len(form['inputs']) for step in devpost_model['steps'].values() for form in step['forms'])}")
        print(f"   Common inputs: {len(common_inputs)}")
        
        return devpost_model
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    model = explore_all_steps()
    if model:
        print(f"\n✅ Model building complete!")
        print(f"📊 Explored {len(model['steps'])} steps")
        print(f"🔍 Found {len(model['heuristics']['step_detection']['step_names'])} step names")
        print(f"📝 Identified {len(model['heuristics']['form_patterns']['common_inputs'])} common inputs")






