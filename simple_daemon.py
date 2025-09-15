#!/usr/bin/env python3
"""
Simple DevPost Browser Daemon
=============================

Simple persistent browser daemon without asyncio conflicts.
"""

import sys
import json
import time
import signal
import subprocess
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class SimpleDevPostDaemon:
    """Simple persistent browser daemon."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.running = False
        
        # Register cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
    
    def start(self):
        """Start the daemon."""
        print("🚀 Starting Simple DevPost Daemon")
        print("=" * 40)
        
        try:
            # Start Playwright
            self.playwright = sync_playwright().start()
            
            # Launch browser with persistent context
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir="/tmp/devpost-browser",
                headless=False,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                args=[
                    '--remote-debugging-port=9222',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-background-timer-throttling'
                ]
            )
            
            # Create page
            self.page = self.context.new_page()
            
            self.running = True
            
            print("✅ Daemon started successfully!")
            print("🌐 Remote debugging: http://localhost:9222")
            print("💡 Browser will stay open for operations")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start: {e}")
            return False
    
    def navigate(self, url):
        """Navigate to URL."""
        try:
            print(f"🌐 Navigating to: {url}")
            self.page.goto(url, wait_until="networkidle")
            print(f"📄 Title: {self.page.title()}")
            print(f"🔗 URL: {self.page.url}")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def get_navigation_steps(self):
        """Get available navigation steps."""
        try:
            # Look for step navigation elements
            step_selectors = [
                ".step",
                ".wizard-step", 
                ".form-step",
                ".submission-step",
                "a[class*='step']",
                ".nav-step",
                ".progress-step"
            ]
            
            steps = []
            for selector in step_selectors:
                elements = self.page.query_selector_all(selector)
                for elem in elements:
                    step_text = elem.text_content().strip()
                    step_class = elem.get_attribute("class") or ""
                    step_href = elem.get_attribute("href")
                    step_id = elem.get_attribute("id")
                    
                    if step_text and len(step_text) < 100:  # Reasonable step text length
                        steps.append({
                            "text": step_text,
                            "class": step_class,
                            "href": step_href,
                            "id": step_id,
                            "element": elem
                        })
            
            return steps
        except Exception as e:
            print(f"❌ Failed to get navigation steps: {e}")
            return []
    
    def click_next_step(self):
        """Click the next step button."""
        try:
            # Look for next step buttons
            next_selectors = [
                "button[class*='next']",
                "a[class*='next']",
                ".next-step",
                ".step-next",
                "button:has-text('Next')",
                "a:has-text('Next')",
                "button:has-text('Continue')",
                "a:has-text('Continue')",
                ".btn-next",
                ".button-next"
            ]
            
            for selector in next_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        print(f"🔄 Clicking next step: {element.text_content().strip()}")
                        element.click()
                        self.page.wait_for_load_state("networkidle")
                        print(f"📄 New page: {self.page.title()}")
                        print(f"🔗 New URL: {self.page.url}")
                        return True
                except:
                    continue
            
            print("❌ No next step button found")
            return False
            
        except Exception as e:
            print(f"❌ Failed to click next step: {e}")
            return False
    
    def click_previous_step(self):
        """Click the previous step button."""
        try:
            # Look for previous step buttons
            prev_selectors = [
                "button[class*='prev']",
                "a[class*='prev']",
                ".prev-step",
                ".step-prev",
                "button:has-text('Previous')",
                "a:has-text('Previous')",
                "button:has-text('Back')",
                "a:has-text('Back')",
                ".btn-prev",
                ".button-prev"
            ]
            
            for selector in prev_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        print(f"🔄 Clicking previous step: {element.text_content().strip()}")
                        element.click()
                        self.page.wait_for_load_state("networkidle")
                        print(f"📄 New page: {self.page.title()}")
                        print(f"🔗 New URL: {self.page.url}")
                        return True
                except:
                    continue
            
            print("❌ No previous step button found")
            return False
            
        except Exception as e:
            print(f"❌ Failed to click previous step: {e}")
            return False
    
    def navigate_to_step(self, step_text):
        """Navigate to a specific step by text."""
        try:
            steps = self.get_navigation_steps()
            
            for step in steps:
                if step_text.lower() in step["text"].lower():
                    print(f"🔄 Clicking step: {step['text']}")
                    step["element"].click()
                    self.page.wait_for_load_state("networkidle")
                    print(f"📄 New page: {self.page.title()}")
                    print(f"🔗 New URL: {self.page.url}")
                    return True
            
            print(f"❌ Step '{step_text}' not found")
            print("Available steps:")
            for step in steps:
                print(f"   - {step['text']}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to navigate to step: {e}")
            return False
    
    def extract_form(self):
        """Extract form data."""
        try:
            print("📊 Extracting form data...")
            
            # Find main form
            form = self.page.query_selector("#project-overview-form")
            if not form:
                forms = self.page.query_selector_all("form")
                if forms:
                    form = forms[-1]
            
            if not form:
                print("❌ No form found!")
                return None
            
            print(f"✅ Found form: {form.get_attribute('id') or 'unnamed'}")
            
            # Extract fields
            fields = form.query_selector_all("input, textarea, select")
            print(f"📝 Found {len(fields)} fields")
            
            form_data = {
                "form_id": form.get_attribute("id"),
                "form_class": form.get_attribute("class"),
                "form_action": form.get_attribute("action"),
                "page_title": self.page.title(),
                "page_url": self.page.url,
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "fields": []
            }
            
            for i, field in enumerate(fields, 1):
                field_type = field.get_attribute("type") or field.evaluate("el => el.tagName").lower()
                field_name = field.get_attribute("name")
                field_id = field.get_attribute("id")
                field_value = field.get_attribute("value") or ""
                field_placeholder = field.get_attribute("placeholder") or ""
                field_required = field.get_attribute("required") is not None
                field_class = field.get_attribute("class")
                
                # Get label
                field_label = "Unlabeled"
                if field_id:
                    label_elem = self.page.query_selector(f"label[for='{field_id}']")
                    if label_elem:
                        field_label = label_elem.text_content().strip()
                
                field_info = {
                    "index": i,
                    "tag": field_type,
                    "name": field_name,
                    "id": field_id,
                    "label": field_label,
                    "value": field_value,
                    "placeholder": field_placeholder,
                    "required": field_required,
                    "class": field_class
                }
                
                form_data["fields"].append(field_info)
            
            return form_data
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return None
    
    def screenshot(self, filename=None):
        """Take screenshot."""
        try:
            if not filename:
                # Generate descriptive filename with form and URL data
                page_title = self.page.title().replace(" ", "_").replace("/", "_")[:30]
                url_parts = self.page.url.split("/")
                hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
                submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
                timestamp = int(time.time())
                filename = f"devpost_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
            
            self.page.screenshot(path=filename)
            print(f"📸 Screenshot: {filename}")
            return True
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return False
    
    def save_html(self, filename=None):
        """Save HTML."""
        try:
            if not filename:
                # Generate descriptive filename with form and URL data
                page_title = self.page.title().replace(" ", "_").replace("/", "_")[:30]
                url_parts = self.page.url.split("/")
                hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
                submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
                timestamp = int(time.time())
                filename = f"devpost_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.html"
            
            html = self.page.content()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"💾 HTML saved: {filename}")
            return True
        except Exception as e:
            print(f"❌ HTML save failed: {e}")
            return False
    
    def cleanup(self, signum=None, frame=None):
        """Cleanup on exit."""
        print("\n🧹 Cleaning up daemon...")
        self.running = False
        
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        
        print("✅ Cleanup complete")
        sys.exit(0)

def main():
    """Main function."""
    daemon = SimpleDevPostDaemon()
    
    if not daemon.start():
        return
    
    print("\n🎮 Daemon Commands:")
    print("navigate <url>     - Navigate to URL")
    print("next               - Click next step button")
    print("prev               - Click previous step button")
    print("steps              - Show available navigation steps")
    print("goto <step>        - Navigate to specific step")
    print("extract            - Extract form data")
    print("screenshot         - Take screenshot")
    print("html               - Save HTML")
    print("quit               - Exit")
    print()
    
    # Navigate to DevPost
    url = "https://devpost.com/submit-to/25444-code-with-kiro-hackathon/manage/submissions/784734-untitled/project-overview"
    daemon.navigate(url)
    
    print("👤 Please authenticate in the browser...")
    input("Press Enter when ready to extract form...")
    
    # Extract form
    form_data = daemon.extract_form()
    if form_data:
        # Save data
        output_file = f"devpost_form_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(form_data, f, indent=2)
        
        print(f"💾 Form data saved: {output_file}")
        
        # Show summary
        print(f"\n📊 Form Summary:")
        print(f"   Fields: {len(form_data['fields'])}")
        print(f"   Form ID: {form_data.get('form_id', 'Unknown')}")
        
        # Show fields
        print(f"\n📋 Fields:")
        for field in form_data['fields']:
            print(f"   {field['index']:2d}. {field['label']} ({field['tag']})")
            print(f"       Name: {field['name']}")
            print(f"       Value: {field['value'][:50]}{'...' if len(field['value']) > 50 else ''}")
            print(f"       Required: {field['required']}")
            print()
    
    # Interactive mode
    while True:
        try:
            command = input("🔧 Command: ").strip().lower()
            
            if command == "quit":
                break
            elif command.startswith("navigate "):
                url = command.split(" ", 1)[1]
                daemon.navigate(url)
            elif command == "next":
                daemon.click_next_step()
            elif command == "prev":
                daemon.click_previous_step()
            elif command == "steps":
                steps = daemon.get_navigation_steps()
                if steps:
                    print("📋 Available navigation steps:")
                    for i, step in enumerate(steps, 1):
                        print(f"   {i}. {step['text']} (class: {step['class']})")
                else:
                    print("❌ No navigation steps found")
            elif command.startswith("goto "):
                step_text = command.split(" ", 1)[1]
                daemon.navigate_to_step(step_text)
            elif command == "extract":
                form_data = daemon.extract_form()
                if form_data:
                    output_file = f"devpost_form_{int(time.time())}.json"
                    with open(output_file, 'w') as f:
                        json.dump(form_data, f, indent=2)
                    print(f"💾 Saved: {output_file}")
            elif command == "screenshot":
                daemon.screenshot()
            elif command == "html":
                daemon.save_html()
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    daemon.cleanup()

if __name__ == "__main__":
    main()
