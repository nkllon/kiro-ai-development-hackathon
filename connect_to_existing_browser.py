#!/usr/bin/env python3
"""
Connect to Existing Browser
==========================

Connect to the already running browser daemon and provide
intelligent navigation without starting a new browser session.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Connect to existing browser for DevPost navigation
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class ExistingBrowserConnector:
    """Connect to existing browser session for DevPost navigation."""
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.current_step = None
        self.project_data = {}
        
    def connect_to_browser(self, project_data: Dict[str, Any] = None):
        """Connect to existing browser session."""
        print("🔌 Connecting to Existing Browser")
        print("=" * 40)
        
        try:
            # Start Playwright
            playwright = sync_playwright().start()
            
            # Try to connect to existing browser via CDP
            try:
                print("🔍 Attempting to connect to existing browser...")
                self.browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
                print("✅ Connected to existing browser!")
                
                # Get existing pages
                pages = self.browser.pages
                if pages:
                    self.page = pages[0]  # Use first page
                    print(f"📄 Using existing page: {self.page.url}")
                else:
                    # Create new page if none exist
                    self.page = self.browser.new_page()
                    print("📄 Created new page")
                
            except Exception as e:
                print(f"❌ Failed to connect to existing browser: {e}")
                print("🔄 Starting new browser session...")
                
                # Fallback to new browser
                self.browser = playwright.chromium.launch_persistent_context(
                    user_data_dir="/tmp/devpost-browser",
                    headless=False,
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080}
                )
                self.page = self.browser.new_page()
                print("✅ New browser session started")
            
            # Set project data
            if project_data:
                self.project_data = project_data
                print(f"📊 Project data loaded: {len(project_data)} fields")
            
            # Detect current state
            self.detect_current_state()
            
            # Start intelligent navigation
            self.start_intelligent_navigation()
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            import traceback
            traceback.print_exc()
    
    def detect_current_state(self):
        """Detect current state of the browser."""
        try:
            current_url = self.page.url
            page_title = self.page.title()
            
            print(f"📄 Current page: {page_title}")
            print(f"🔗 Current URL: {current_url}")
            
            # Detect step based on URL patterns
            if "project-overview" in current_url:
                self.current_step = "project_overview"
            elif "project_details" in current_url or "photo" in current_url:
                self.current_step = "project_details"
            elif "additional-info" in current_url:
                self.current_step = "additional_info"
            elif "submission" in current_url and "manage" in current_url:
                self.current_step = "submission_dashboard"
            else:
                self.current_step = "unknown"
            
            print(f"🎯 Detected step: {self.current_step}")
            
        except Exception as e:
            print(f"❌ State detection failed: {e}")
    
    def start_intelligent_navigation(self):
        """Start intelligent navigation through the form."""
        print("\n🤖 Starting Intelligent Navigation")
        print("=" * 40)
        
        try:
            # Process current step
            self.process_current_step()
            
            # Look for next step
            next_step = self.find_next_step()
            if next_step:
                print(f"🔄 Moving to next step: {next_step['text']}")
                self.navigate_to_step(next_step)
                
                # Process the new step
                self.process_current_step()
            
            print("\n✅ Navigation complete!")
            print("🎮 Interactive mode available")
            
            # Start interactive mode
            self.interactive_mode()
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            import traceback
            traceback.print_exc()
    
    def process_current_step(self):
        """Process current step (extract forms, fill data, etc.)."""
        print(f"\n📝 Processing step: {self.current_step}")
        
        try:
            # Take screenshot
            self.take_screenshot()
            
            # Extract form data
            form_data = self.extract_form()
            if form_data:
                self.save_form_data(form_data)
                
                # Fill form if we have project data
                if self.project_data:
                    self.fill_form(form_data)
            
        except Exception as e:
            print(f"❌ Step processing failed: {e}")
    
    def find_next_step(self) -> Optional[Dict]:
        """Find next step in the submission flow."""
        try:
            # Look for next/continue buttons
            next_selectors = [
                "button:has-text('Next')", "a:has-text('Next')",
                "button:has-text('Continue')", "a:has-text('Continue')",
                "button:has-text('Save & Continue')", "a:has-text('Save & Continue')",
                "button:has-text('Save and Continue')", "a:has-text('Save and Continue')",
                ".next-step", ".step-next", "button[class*='next']", "a[class*='next']",
                "button[type='submit']", "input[type='submit']",
                ".btn-next", ".btn-continue", ".continue-btn"
            ]
            
            for selector in next_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible() and element.is_enabled():
                        return {
                            "text": element.text_content().strip(),
                            "element": element,
                            "type": "next_button"
                        }
                except:
                    continue
            
            # Look for step navigation
            step_elements = self.page.query_selector_all(".step, .wizard-step, .form-step, a[class*='step']")
            for element in step_elements:
                try:
                    text = element.text_content().strip()
                    if text and len(text) < 100 and element.is_visible():
                        # Check if this is a next step
                        if any(keyword in text.lower() for keyword in ["next", "continue", "details", "photo", "additional", "submit"]):
                            return {
                                "text": text,
                                "element": element,
                                "type": "step_navigation"
                            }
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to find next step: {e}")
            return None
    
    def navigate_to_step(self, step: Dict):
        """Navigate to specific step."""
        try:
            if step["type"] == "next_button":
                print(f"🔄 Clicking: {step['text']}")
                step["element"].click()
            else:
                print(f"🔄 Clicking step: {step['text']}")
                step["element"].click()
            
            # Wait for navigation
            self.page.wait_for_load_state("networkidle")
            
            # Update current step
            self.detect_current_state()
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
    
    def extract_form(self) -> Optional[Dict]:
        """Extract current form data."""
        try:
            # Find main form
            form = self.page.query_selector("form")
            if not form:
                print("❌ No form found")
                return None
            
            form_id = form.get_attribute("id") or "unnamed"
            print(f"📋 Extracting form: {form_id}")
            
            # Extract fields
            fields = form.query_selector_all("input, textarea, select")
            print(f"📝 Found {len(fields)} fields")
            
            form_data = {
                "form_id": form_id,
                "form_class": form.get_attribute("class"),
                "form_action": form.get_attribute("action"),
                "page_title": self.page.title(),
                "page_url": self.page.url,
                "step": self.current_step,
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "fields": []
            }
            
            for i, field in enumerate(fields, 1):
                try:
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
                    
                except Exception as e:
                    print(f"⚠️ Failed to extract field {i}: {e}")
                    continue
            
            return form_data
            
        except Exception as e:
            print(f"❌ Form extraction failed: {e}")
            return None
    
    def fill_form(self, form_data: Dict):
        """Fill form with project data."""
        print("📝 Filling form with project data...")
        
        filled_count = 0
        for field in form_data["fields"]:
            if self.fill_field(field):
                filled_count += 1
        
        print(f"✅ Filled {filled_count}/{len(form_data['fields'])} fields")
    
    def fill_field(self, field: Dict) -> bool:
        """Fill a single form field."""
        try:
            field_name = field.get("name", "")
            field_type = field.get("tag", "")
            field_id = field.get("id", "")
            label = field.get("label", "")
            
            # Skip hidden fields unless important
            if field_type == "hidden" and "token" not in field_name.lower():
                return False
            
            # Determine value based on field name/label
            value = self.get_field_value(field)
            if not value:
                return False
            
            # Find field element
            field_element = None
            if field_id:
                field_element = self.page.query_selector(f"#{field_id}")
            if not field_element and field_name:
                field_element = self.page.query_selector(f"[name='{field_name}']")
            
            if not field_element:
                return False
            
            # Fill field
            if field_type in ['text', 'email', 'url', 'tel', 'number']:
                field_element.fill(str(value))
            elif field_type == 'textarea':
                field_element.fill(str(value))
            elif field_type == 'select':
                field_element.select_option(str(value))
            
            print(f"   ✅ {label}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to fill {field.get('label', 'field')}: {e}")
            return False
    
    def get_field_value(self, field: Dict) -> Optional[str]:
        """Get value for field from project data."""
        field_name = field.get("name", "").lower()
        label = field.get("label", "").lower()
        
        # Project name/title
        if "title" in field_name or "project name" in label:
            return self.project_data.get("title", "")
        
        # Description/tagline
        elif "tagline" in field_name or "elevator pitch" in label or "description" in label:
            return self.project_data.get("description", "")
        
        # Technologies
        elif "built_with" in field_name or "technologies" in label:
            techs = self.project_data.get("technologies", [])
            return ", ".join(techs) if isinstance(techs, list) else str(techs)
        
        # Challenges
        elif "challenge" in field_name or "challenge" in label:
            return self.project_data.get("challenges", "")
        
        # Accomplishments
        elif "accomplishment" in field_name or "accomplishment" in label:
            return self.project_data.get("accomplishments", "")
        
        # Learnings
        elif "learned" in field_name or "learning" in label:
            return self.project_data.get("learnings", "")
        
        # Future plans
        elif "future" in field_name or "future" in label:
            return self.project_data.get("future_plans", "")
        
        # Team members
        elif "team" in field_name or "team" in label:
            team = self.project_data.get("team_members", [])
            return ", ".join(team) if isinstance(team, list) else str(team)
        
        # GitHub URL
        elif "github" in field_name or "github" in label:
            return self.project_data.get("github_url", "")
        
        # Website URL
        elif "website" in field_name or "url" in field_name or "website" in label:
            return self.project_data.get("website_url", "")
        
        return None
    
    def take_screenshot(self):
        """Take screenshot of current page."""
        try:
            timestamp = int(time.time())
            filename = f"devpost_{self.current_step}_{timestamp}.png"
            self.page.screenshot(path=filename)
            print(f"📸 Screenshot: {filename}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
    
    def save_form_data(self, form_data: Dict):
        """Save form data to JSON."""
        try:
            timestamp = int(time.time())
            filename = f"devpost_form_{self.current_step}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(form_data, f, indent=2)
            print(f"💾 Form data: {filename}")
        except Exception as e:
            print(f"❌ Save failed: {e}")
    
    def interactive_mode(self):
        """Start interactive mode for manual control."""
        print("\n🎮 Interactive Mode")
        print("=" * 20)
        print("Commands: next, extract, screenshot, fill, quit")
        
        while True:
            try:
                command = input("🔧 Command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "next":
                    next_step = self.find_next_step()
                    if next_step:
                        self.navigate_to_step(next_step)
                    else:
                        print("❌ No next step found")
                elif command == "extract":
                    form_data = self.extract_form()
                    if form_data:
                        self.save_form_data(form_data)
                elif command == "screenshot":
                    self.take_screenshot()
                elif command == "fill":
                    form_data = self.extract_form()
                    if form_data:
                        self.fill_form(form_data)
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🔌 Connect to Existing Browser")
    print("=" * 40)
    
    # Load project data
    try:
        with open("sample_project_data.json", 'r') as f:
            project_data = json.load(f)
        print(f"📊 Loaded project data: {len(project_data)} fields")
    except Exception as e:
        print(f"⚠️ Could not load project data: {e}")
        project_data = {}
    
    # Connect to existing browser
    connector = ExistingBrowserConnector()
    connector.connect_to_browser(project_data)

if __name__ == "__main__":
    main()

