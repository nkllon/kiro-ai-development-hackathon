#!/usr/bin/env python3
"""
Live DevPost Debug Session
==========================

Interactive debugging tool that connects to an existing browser session
or creates a persistent one for live form interrogation.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Live debugging without repeated authentication
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class LiveDevPostDebugger:
    """Live debugging session for DevPost forms."""
    
    def __init__(self, headless=False, browser_type="chromium"):
        self.headless = headless
        self.browser_type = browser_type
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
    def start_session(self):
        """Start a persistent browser session."""
        print("🚀 Starting Live DevPost Debug Session")
        print("=" * 50)
        
        self.playwright = sync_playwright().start()
        
        if self.browser_type == "chromium":
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--remote-debugging-port=9222']  # Enable remote debugging
            )
        elif self.browser_type == "firefox":
            self.browser = self.playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            self.browser = self.playwright.webkit.launch(headless=self.headless)
        
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        self.page = self.context.new_page()
        print("✅ Browser session started!")
        print("🌐 Navigate to your DevPost page and authenticate manually")
        print("💡 Use the commands below to interact with the page")
        
    def connect_to_existing(self, port=9222):
        """Connect to an existing Chrome instance with remote debugging."""
        print("🔗 Connecting to existing browser session...")
        
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
            self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            
            print("✅ Connected to existing browser session!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def navigate_to(self, url):
        """Navigate to a specific URL."""
        print(f"🌐 Navigating to: {url}")
        self.page.goto(url, wait_until="networkidle")
        print(f"📄 Page title: {self.page.title()}")
        print(f"🔗 Current URL: {self.page.url}")
        
    def analyze_current_page(self):
        """Analyze the current page for form elements."""
        print("\n🔍 Analyzing current page...")
        print("=" * 40)
        
        # Get page info
        title = self.page.title()
        url = self.page.url
        print(f"📄 Title: {title}")
        print(f"🔗 URL: {url}")
        
        # Look for forms
        forms = self.page.query_selector_all("form")
        print(f"\n📋 Found {len(forms)} forms:")
        
        for i, form in enumerate(forms, 1):
            form_id = form.get_attribute("id")
            form_class = form.get_attribute("class")
            form_action = form.get_attribute("action")
            print(f"   {i}. Form ID: {form_id}, Class: {form_class}, Action: {form_action}")
            
            # Get form fields
            inputs = form.query_selector_all("input, textarea, select")
            print(f"      Fields: {len(inputs)}")
            
            for j, field in enumerate(inputs[:5], 1):  # Show first 5 fields
                field_type = field.get_attribute("type") or field.tag_name.lower()
                field_name = field.get_attribute("name")
                field_id = field.get_attribute("id")
                field_value = field.get_attribute("value") or ""
                field_placeholder = field.get_attribute("placeholder") or ""
                
                print(f"         {j}. <{field_type}> name='{field_name}' id='{field_id}' value='{field_value[:30]}...' placeholder='{field_placeholder[:30]}...'")
        
        # Look for specific DevPost elements
        print(f"\n🎯 DevPost-specific elements:")
        devpost_selectors = [
            ".step", ".section", ".wizard", ".form-step",
            "[data-testid*='submission']", "[data-testid*='project']",
            ".submission", ".project", ".hackathon"
        ]
        
        for selector in devpost_selectors:
            elements = self.page.query_selector_all(selector)
            if elements:
                print(f"   ✅ {selector}: {len(elements)} elements")
                for i, elem in enumerate(elements[:3], 1):
                    text = elem.text_content()[:50] if elem.text_content() else ""
                    print(f"      {i}. {text}...")
            else:
                print(f"   ❌ {selector}: No elements")
    
    def extract_form_data(self):
        """Extract form data from current page."""
        print("\n📊 Extracting form data...")
        print("=" * 40)
        
        forms = self.page.query_selector_all("form")
        form_data = []
        
        for i, form in enumerate(forms, 1):
            form_info = {
                "form_index": i,
                "form_id": form.get_attribute("id"),
                "form_class": form.get_attribute("class"),
                "form_action": form.get_attribute("action"),
                "form_method": form.get_attribute("method"),
                "fields": []
            }
            
            # Extract all form fields
            fields = form.query_selector_all("input, textarea, select")
            
            for field in fields:
                field_info = {
                    "tag": field.tag_name.lower(),
                    "type": field.get_attribute("type") or field.tag_name.lower(),
                    "name": field.get_attribute("name"),
                    "id": field.get_attribute("id"),
                    "value": field.get_attribute("value") or "",
                    "placeholder": field.get_attribute("placeholder") or "",
                    "required": field.get_attribute("required") is not None,
                    "class": field.get_attribute("class"),
                    "label": self.get_field_label(field)
                }
                
                # Get options for select fields
                if field.tag_name.lower() == "select":
                    options = field.query_selector_all("option")
                    field_info["options"] = [opt.text_content() for opt in options if opt.text_content()]
                
                form_info["fields"].append(field_info)
            
            form_data.append(form_info)
        
        return form_data
    
    def get_field_label(self, field):
        """Get label for a form field."""
        try:
            field_id = field.get_attribute("id")
            if field_id:
                label = self.page.query_selector(f"label[for='{field_id}']")
                if label:
                    return label.text_content().strip()
            
            # Look for nearby text
            parent = field.query_selector("xpath=..")
            if parent:
                text = parent.text_content()
                if text:
                    lines = text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) < 100:
                            return line
            
            return "Unlabeled"
        except:
            return "Unlabeled"
    
    def take_screenshot(self, filename="devpost_live_debug.png"):
        """Take a screenshot of current page."""
        self.page.screenshot(path=filename)
        print(f"📸 Screenshot saved: {filename}")
    
    def save_page_html(self, filename="devpost_live_debug.html"):
        """Save current page HTML."""
        html = self.page.content()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 HTML saved: {filename}")
    
    def save_form_data(self, filename="devpost_form_data.json"):
        """Save extracted form data as JSON."""
        form_data = self.extract_form_data()
        with open(filename, 'w') as f:
            json.dump(form_data, f, indent=2)
        print(f"💾 Form data saved: {filename}")
        return form_data
    
    def interactive_mode(self):
        """Start interactive debugging mode."""
        print("\n🎮 Interactive Mode - Available Commands:")
        print("=" * 50)
        print("navigate <url>     - Navigate to URL")
        print("analyze            - Analyze current page")
        print("extract            - Extract form data")
        print("screenshot         - Take screenshot")
        print("html               - Save page HTML")
        print("save               - Save form data as JSON")
        print("url                - Show current URL")
        print("title              - Show page title")
        print("quit               - Exit")
        print()
        
        while True:
            try:
                command = input("🔧 Command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command.startswith("navigate "):
                    url = command.split(" ", 1)[1]
                    self.navigate_to(url)
                elif command == "analyze":
                    self.analyze_current_page()
                elif command == "extract":
                    form_data = self.extract_form_data()
                    print(f"📊 Extracted data from {len(form_data)} forms")
                elif command == "screenshot":
                    self.take_screenshot()
                elif command == "html":
                    self.save_page_html()
                elif command == "save":
                    self.save_form_data()
                elif command == "url":
                    print(f"🔗 Current URL: {self.page.url}")
                elif command == "title":
                    print(f"📄 Page Title: {self.page.title()}")
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def close(self):
        """Close the browser session."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("🔒 Browser session closed")

def main():
    """Main function."""
    print("🎯 Live DevPost Debug Session")
    print("=" * 40)
    
    # Try to connect to existing browser first
    debugger = LiveDevPostDebugger(headless=False)
    
    print("1. Try connecting to existing browser session")
    print("2. Start new browser session")
    
    choice = input("Choose option (1/2): ").strip()
    
    if choice == "1":
        if not debugger.connect_to_existing():
            print("Starting new session instead...")
            debugger.start_session()
    else:
        debugger.start_session()
    
    try:
        # Navigate to DevPost URL
        url = "https://devpost.com/submit-to/25444-code-with-kiro-hackathon/manage/submissions/784734-untitled/project-overview"
        debugger.navigate_to(url)
        
        print(f"\n✅ Ready! You can now:")
        print(f"   - Authenticate manually in the browser")
        print(f"   - Navigate to different pages")
        print(f"   - Use interactive commands")
        
        # Start interactive mode
        debugger.interactive_mode()
        
    finally:
        debugger.close()

if __name__ == "__main__":
    main()

