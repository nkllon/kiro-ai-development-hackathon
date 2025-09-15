#!/usr/bin/env python3
"""
HTTP Analyze Page
================

Analyze the DevPost page using HTTP API instead of WebSocket.
This bypasses the WebSocket connection issues.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: HTTP-based page analysis
"""

import sys
import json
import time
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def get_devpost_page_info():
    """Get the DevPost page info from the debugging port."""
    try:
        response = requests.get("http://localhost:9222/json")
        pages = response.json()
        
        # Find the DevPost page
        for page in pages:
            if "devpost.com" in page["url"] and "submission" in page["url"]:
                return page
        
        # If no DevPost page found, return the first page
        if pages:
            return pages[0]
        
        return None
    except Exception as e:
        print(f"❌ Failed to get page info: {e}")
        return None

def analyze_page_via_http(page_info):
    """Analyze the page using HTTP API."""
    try:
        # Get page content
        print("📄 Getting page content...")
        response = requests.get(f"http://localhost:9222/json/page/{page_info['id']}")
        if response.status_code != 200:
            print(f"❌ Failed to get page content: {response.status_code}")
            return
        
        page_data = response.json()
        print(f"📄 Title: {page_data.get('title', 'Unknown')}")
        print(f"🔗 URL: {page_data.get('url', 'Unknown')}")
        
        # Get page source
        print("📄 Getting page source...")
        source_response = requests.get(f"http://localhost:9222/json/page/{page_info['id']}/source")
        if source_response.status_code == 200:
            source_data = source_response.json()
            html_content = source_data.get('source', '')
            print(f"📄 HTML length: {len(html_content)} characters")
            
            # Analyze HTML content
            analyze_html_content(html_content)
        else:
            print(f"❌ Failed to get page source: {source_response.status_code}")
        
    except Exception as e:
        print(f"❌ HTTP analysis failed: {e}")

def analyze_html_content(html_content):
    """Analyze HTML content for forms and elements."""
    print("\n🔍 Analyzing HTML content...")
    
    # Count elements using simple string matching
    form_count = html_content.count('<form')
    button_count = html_content.count('<button') + html_content.count('type="button"') + html_content.count('type="submit"')
    input_count = html_content.count('<input') + html_content.count('<textarea') + html_content.count('<select')
    link_count = html_content.count('<a ')
    image_count = html_content.count('<img')
    
    print(f"📊 Elements found:")
    print(f"   Forms: {form_count}")
    print(f"   Buttons: {button_count}")
    print(f"   Inputs: {input_count}")
    print(f"   Links: {link_count}")
    print(f"   Images: {image_count}")
    
    # Look for form patterns
    if form_count > 0:
        print(f"\n📝 Form Analysis:")
        analyze_forms_in_html(html_content)
    
    # Look for button patterns
    if button_count > 0:
        print(f"\n🔘 Button Analysis:")
        analyze_buttons_in_html(html_content)
    
    # Look for navigation patterns
    print(f"\n🧭 Navigation Analysis:")
    analyze_navigation_in_html(html_content)

def analyze_forms_in_html(html_content):
    """Analyze forms in HTML content."""
    import re
    
    # Find form tags
    form_pattern = r'<form[^>]*>(.*?)</form>'
    forms = re.findall(form_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for i, form_html in enumerate(forms[:5], 1):  # Analyze first 5 forms
        print(f"   Form {i}:")
        
        # Extract form attributes
        form_tag_match = re.search(r'<form[^>]*>', form_html, re.IGNORECASE)
        if form_tag_match:
            form_tag = form_tag_match.group(0)
            
            # Extract ID
            id_match = re.search(r'id=["\']([^"\']*)["\']', form_tag, re.IGNORECASE)
            form_id = id_match.group(1) if id_match else f"form_{i}"
            
            # Extract class
            class_match = re.search(r'class=["\']([^"\']*)["\']', form_tag, re.IGNORECASE)
            form_class = class_match.group(1) if class_match else ""
            
            # Extract action
            action_match = re.search(r'action=["\']([^"\']*)["\']', form_tag, re.IGNORECASE)
            form_action = action_match.group(1) if action_match else ""
            
            # Extract method
            method_match = re.search(r'method=["\']([^"\']*)["\']', form_tag, re.IGNORECASE)
            form_method = method_match.group(1) if method_match else "get"
            
            print(f"      ID: {form_id}")
            print(f"      Class: {form_class}")
            print(f"      Action: {form_action}")
            print(f"      Method: {form_method}")
            
            # Count fields in this form
            field_count = len(re.findall(r'<input|<textarea|<select', form_html, re.IGNORECASE))
            print(f"      Fields: {field_count}")
            
            # Analyze fields
            if field_count > 0:
                analyze_fields_in_form(form_html, i)

def analyze_fields_in_form(form_html, form_index):
    """Analyze fields in a specific form."""
    import re
    
    # Find input, textarea, and select tags
    field_pattern = r'<(input|textarea|select)[^>]*>'
    fields = re.findall(field_pattern, form_html, re.IGNORECASE)
    
    for i, field_tag in enumerate(fields[:10], 1):  # Analyze first 10 fields
        try:
            # Extract field attributes
            field_type_match = re.search(r'type=["\']([^"\']*)["\']', field_tag, re.IGNORECASE)
            field_type = field_type_match.group(1) if field_type_match else "text"
            
            name_match = re.search(r'name=["\']([^"\']*)["\']', field_tag, re.IGNORECASE)
            field_name = name_match.group(1) if name_match else ""
            
            field_id_match = re.search(r'id=["\']([^"\']*)["\']', field_tag, re.IGNORECASE)
            field_id = field_id_match.group(1) if field_id_match else ""
            
            placeholder_match = re.search(r'placeholder=["\']([^"\']*)["\']', field_tag, re.IGNORECASE)
            placeholder = placeholder_match.group(1) if placeholder_match else ""
            
            value_match = re.search(r'value=["\']([^"\']*)["\']', field_tag, re.IGNORECASE)
            value = value_match.group(1) if value_match else ""
            
            required = 'required' in field_tag.lower()
            
            print(f"      Field {i}: {field_type}")
            if field_name:
                print(f"         Name: {field_name}")
            if field_id:
                print(f"         ID: {field_id}")
            if placeholder:
                print(f"         Placeholder: {placeholder}")
            if value:
                print(f"         Value: {value[:50]}...")
            if required:
                print(f"         Required: Yes")
                
        except Exception as e:
            print(f"      Field {i}: Error analyzing - {e}")

def analyze_buttons_in_html(html_content):
    """Analyze buttons in HTML content."""
    import re
    
    # Find button tags and input buttons
    button_pattern = r'<(button|input[^>]*type=["\'](?:button|submit)["\'][^>]*)>'
    buttons = re.findall(button_pattern, html_content, re.IGNORECASE)
    
    for i, button_tag in enumerate(buttons[:15], 1):  # Analyze first 15 buttons
        try:
            # Extract button text
            text_match = re.search(r'>([^<]*)<', button_tag)
            button_text = text_match.group(1).strip() if text_match else ""
            
            # Extract type
            type_match = re.search(r'type=["\']([^"\']*)["\']', button_tag, re.IGNORECASE)
            button_type = type_match.group(1) if type_match else "button"
            
            # Extract class
            class_match = re.search(r'class=["\']([^"\']*)["\']', button_tag, re.IGNORECASE)
            button_class = class_match.group(1) if class_match else ""
            
            if button_text and len(button_text) < 100:
                print(f"   {i}. {button_text} (type: {button_type})")
                if button_class:
                    print(f"      Classes: {button_class}")
                    
        except Exception as e:
            print(f"   Button {i}: Error analyzing - {e}")

def analyze_navigation_in_html(html_content):
    """Analyze navigation elements in HTML content."""
    import re
    
    # Find navigation keywords
    nav_keywords = ["next", "continue", "back", "previous", "submit", "save", "finish", "complete", "go", "click", "start", "begin"]
    
    # Look for buttons with navigation keywords
    button_pattern = r'<(button|input[^>]*type=["\'](?:button|submit)["\'][^>]*)>'
    buttons = re.findall(button_pattern, html_content, re.IGNORECASE)
    
    nav_buttons = []
    for button_tag in buttons:
        try:
            # Extract button text
            text_match = re.search(r'>([^<]*)<', button_tag)
            button_text = text_match.group(1).strip() if text_match else ""
            
            # Check if text contains navigation keywords
            if button_text:
                text_lower = button_text.lower()
                if any(keyword in text_lower for keyword in nav_keywords):
                    nav_buttons.append(button_text)
                    
        except Exception as e:
            continue
    
    if nav_buttons:
        print(f"   Found {len(nav_buttons)} navigation buttons:")
        for i, nav_text in enumerate(nav_buttons, 1):
            print(f"      {i}. {nav_text}")
    else:
        print("   No obvious navigation buttons found")

def main():
    """Main function."""
    print("🔌 HTTP Analyze DevPost Page")
    print("=" * 40)
    
    # Get page info
    page_info = get_devpost_page_info()
    if not page_info:
        print("❌ No pages found!")
        return
    
    print(f"📄 Found page: {page_info['title']}")
    print(f"🔗 URL: {page_info['url']}")
    print(f"🆔 ID: {page_info['id']}")
    
    # Analyze the page
    analyze_page_via_http(page_info)
    
    print(f"\n🎮 Interactive Mode")
    print("Commands: analyze, quit")
    
    while True:
        try:
            command = input("🔧 Command: ").strip().lower()
            
            if command == "quit":
                break
            elif command == "analyze":
                print("🔄 Re-analyzing page...")
                analyze_page_via_http(page_info)
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

