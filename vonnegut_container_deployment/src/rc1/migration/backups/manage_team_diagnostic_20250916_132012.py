The edit button is highlighted. The edit and edit project is highlighted.
#!/usr/bin/env python3
"""
Manage Team Page Diagnostic
===========================

Diagnostic tool to analyze the Manage Team page and understand
why Save and Continue isn't working.

Author: Beast Mode Framework
Date: 2025-01-14
Purpose: Debug Manage Team page issues
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

def diagnose_manage_team_page():
    """Diagnose issues with the Manage Team page."""
    try:
        playwright = sync_playwright().start()
        
        # Get page info
        response = requests.get("http://localhost:9222/json")
        pages_info = response.json()
        
        devpost_page_info = None
        for p_info in pages_info:
            if "devpost.com" in p_info.get("url", "") and ("manage-team" in p_info.get("url", "") or "manage" in p_info.get("url", "")):
                devpost_page_info = p_info
                break
        
        if not devpost_page_info:
            print("❌ No DevPost manage team page found")
            print("📋 Available pages:")
            for p_info in pages_info:
                if "devpost.com" in p_info.get("url", ""):
                    print(f"   • {p_info['title']}: {p_info['url']}")
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
            if "devpost.com" in page.url and ("manage-team" in page.url or "manage" in page.url):
                target_page = page
                break
        
        if not target_page:
            target_page = pages[0]
        
        print(f"✅ Connected to: {target_page.url}")
        
        # Wait for page to be ready
        print("⏳ Waiting for page to be ready...")
        target_page.wait_for_load_state("networkidle")
        
        print(f"\n{'='*60}")
        print(f"🔍 MANAGE TEAM PAGE DIAGNOSTIC")
        print(f"{'='*60}")
        
        # 1. Check page title and URL
        print(f"📄 Page Title: {target_page.title()}")
        print(f"🔗 Page URL: {target_page.url}")
        
        # 2. Look for forms
        forms = target_page.query_selector_all("form")
        print(f"\n📋 Forms Found: {len(forms)}")
        for i, form in enumerate(forms, 1):
            form_id = form.get_attribute("id") or "no-id"
            form_class = form.get_attribute("class") or "no-class"
            print(f"   {i}. Form ID: {form_id}, Class: {form_class}")
        
        # 3. Check all input fields
        inputs = target_page.query_selector_all("input, textarea, select")
        print(f"\n📝 Input Fields Found: {len(inputs)}")
        for i, input_elem in enumerate(inputs, 1):
            input_type = input_elem.get_attribute("type") or input_elem.tag_name
            input_name = input_elem.get_attribute("name") or "no-name"
            input_value = input_elem.get_attribute("value") or ""
            input_placeholder = input_elem.get_attribute("placeholder") or ""
            is_required = input_elem.get_attribute("required") is not None
            is_disabled = input_elem.get_attribute("disabled") is not None
            
            print(f"   {i}. {input_type}: {input_name}")
            print(f"      Value: '{input_value}' | Placeholder: '{input_placeholder}'")
            print(f"      Required: {is_required} | Disabled: {is_disabled}")
        
        # 4. Check all buttons
        buttons = target_page.query_selector_all("button, input[type='button'], input[type='submit']")
        print(f"\n🔘 Buttons Found: {len(buttons)}")
        for i, button in enumerate(buttons, 1):
            button_text = button.text_content().strip() or button.get_attribute("value") or "no-text"
            button_type = button.get_attribute("type") or "button"
            button_id = button.get_attribute("id") or "no-id"
            button_class = button.get_attribute("class") or "no-class"
            is_disabled = button.get_attribute("disabled") is not None
            is_visible = button.is_visible()
            is_enabled = button.is_enabled()
            
            print(f"   {i}. {button_text} ({button_type})")
            print(f"      ID: {button_id} | Class: {button_class}")
            print(f"      Disabled: {is_disabled} | Visible: {is_visible} | Enabled: {is_enabled}")
        
        # 5. Look for Save & Continue specifically
        save_continue_buttons = []
        for button in buttons:
            text = button.text_content().strip().lower()
            if any(word in text for word in ["save", "continue", "submit", "next"]):
                save_continue_buttons.append(button)
        
        print(f"\n💾 Save & Continue Buttons: {len(save_continue_buttons)}")
        for i, button in enumerate(save_continue_buttons, 1):
            button_text = button.text_content().strip()
            is_disabled = button.get_attribute("disabled") is not None
            is_visible = button.is_visible()
            is_enabled = button.is_enabled()
            
            print(f"   {i}. '{button_text}'")
            print(f"      Disabled: {is_disabled} | Visible: {is_visible} | Enabled: {is_enabled}")
            
            # Check if button has click handlers
            has_onclick = button.get_attribute("onclick") is not None
            print(f"      Has onclick: {has_onclick}")
        
        # 6. Check for validation messages or errors
        error_elements = target_page.query_selector_all(".error, .alert, .warning, [class*='error'], [class*='alert'], [class*='warning']")
        print(f"\n⚠️  Error/Warning Elements: {len(error_elements)}")
        for i, error_elem in enumerate(error_elements, 1):
            if error_elem.is_visible():
                error_text = error_elem.text_content().strip()
                print(f"   {i}. {error_text}")
        
        # 7. Check for required field indicators
        required_fields = target_page.query_selector_all("[required], .required, [aria-required='true']")
        print(f"\n🔴 Required Fields: {len(required_fields)}")
        for i, field in enumerate(required_fields, 1):
            field_name = field.get_attribute("name") or field.get_attribute("id") or "unnamed"
            field_type = field.get_attribute("type") or field.tag_name
            field_value = field.get_attribute("value") or ""
            is_empty = not field_value.strip()
            
            print(f"   {i}. {field_type}: {field_name}")
            print(f"      Value: '{field_value}' | Empty: {is_empty}")
        
        # 8. Check for team member related elements
        team_elements = target_page.query_selector_all("[class*='team'], [id*='team'], [name*='team']")
        print(f"\n👥 Team-Related Elements: {len(team_elements)}")
        for i, elem in enumerate(team_elements, 1):
            elem_tag = elem.evaluate("el => el.tagName").lower()
            elem_class = elem.get_attribute("class") or "no-class"
            elem_id = elem.get_attribute("id") or "no-id"
            elem_text = elem.text_content().strip()[:50] or "no-text"
            
            print(f"   {i}. {elem_tag}: {elem_id} | {elem_class}")
            print(f"      Text: {elem_text}")
        
        # 9. Take screenshot for visual analysis
        timestamp = int(time.time())
        screenshot_path = f"manage_team_diagnostic_{timestamp}.png"
        target_page.screenshot(path=screenshot_path)
        print(f"\n📸 Screenshot saved: {screenshot_path}")
        
        # 10. Interactive analysis
        print(f"\n🎯 INTERACTIVE ANALYSIS")
        print(f"{'='*60}")
        print("Based on the analysis above:")
        
        if not save_continue_buttons:
            print("❌ No Save & Continue buttons found!")
        elif any(btn.get_attribute("disabled") for btn in save_continue_buttons):
            print("❌ Save & Continue button is DISABLED")
            print("💡 This usually means required fields are not filled")
        elif any(not btn.is_visible() for btn in save_continue_buttons):
            print("❌ Save & Continue button is not visible")
            print("💡 This might mean the form is not ready")
        else:
            print("✅ Save & Continue button appears to be clickable")
            print("💡 If clicking doesn't work, there might be JavaScript validation")
        
        if required_fields:
            empty_required = [f for f in required_fields if not f.get_attribute("value", "").strip()]
            if empty_required:
                print(f"❌ {len(empty_required)} required fields are empty")
                print("💡 Fill these fields first before Save & Continue")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        print(f"   1. Check if all required fields are filled")
        print(f"   2. Look for validation messages")
        print(f"   3. Try filling team member information")
        print(f"   4. Check browser console for JavaScript errors")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    diagnose_manage_team_page()
