#!/usr/bin/env python3
"""
Smart DevPost Navigator V2
==========================

Intelligent navigation system with proper event listeners and hooks
for detecting successful navigation and form interactions.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Automated DevPost form navigation with event-driven detection
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext
from typing import Dict, List, Any, Optional, Callable

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class SmartDevPostNavigatorV2:
    """Intelligent DevPost navigation system with event listeners."""
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.current_step = None
        self.submission_flow = []
        self.project_data = {}
        self.navigation_events = []
        self.form_events = []
        self.success_callbacks = []
        self.error_callbacks = []
        
    def start_navigation(self, base_url: str, project_data: Dict[str, Any] = None):
        """Start intelligent navigation through DevPost submission."""
        print("🧠 Smart DevPost Navigator V2 Starting")
        print("=" * 50)
        
        try:
            # Start browser
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch_persistent_context(
                user_data_dir="/tmp/devpost-smart-browser-v2",
                headless=False,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            self.page = self.browser.new_page()
            
            # Set up event listeners
            self.setup_event_listeners()
            
            # Set project data
            if project_data:
                self.project_data = project_data
                print(f"📊 Project data loaded: {len(project_data)} fields")
            
            # Navigate to base URL
            print(f"🌐 Navigating to: {base_url}")
            self.page.goto(base_url, wait_until="networkidle")
            
            # Wait for initial load and detect step
            self.wait_for_page_ready()
            self.detect_current_step()
            
            # Start automated flow
            self.run_automated_flow()
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.browser:
                self.browser.close()
    
    def setup_event_listeners(self):
        """Set up comprehensive event listeners for page events."""
        print("🎧 Setting up event listeners...")
        
        # Navigation events
        self.page.on("load", self.on_page_load)
        self.page.on("domcontentloaded", self.on_dom_loaded)
        self.page.on("networkidle", self.on_network_idle)
        
        # Form events
        self.page.on("console", self.on_console_message)
        
        # Error events
        self.page.on("pageerror", self.on_page_error)
        self.page.on("crash", self.on_page_crash)
        
        # Request/Response events for debugging
        self.page.on("request", self.on_request)
        self.page.on("response", self.on_response)
        
        print("✅ Event listeners configured")
    
    def on_page_load(self, page: Page):
        """Handle page load event."""
        print(f"📄 Page loaded: {page.url}")
        self.navigation_events.append({
            "type": "load",
            "url": page.url,
            "timestamp": time.time()
        })
    
    def on_dom_loaded(self, page: Page):
        """Handle DOM content loaded event."""
        print(f"🌐 DOM loaded: {page.url}")
        self.navigation_events.append({
            "type": "dom_loaded",
            "url": page.url,
            "timestamp": time.time()
        })
    
    def on_network_idle(self, page: Page):
        """Handle network idle event."""
        print(f"🔌 Network idle: {page.url}")
        self.navigation_events.append({
            "type": "network_idle",
            "url": page.url,
            "timestamp": time.time()
        })
    
    def on_console_message(self, msg):
        """Handle console messages."""
        if msg.type in ["error", "warning"]:
            print(f"⚠️ Console {msg.type}: {msg.text}")
        elif "form" in msg.text.lower() or "submit" in msg.text.lower():
            print(f"📝 Form message: {msg.text}")
    
    def on_page_error(self, error):
        """Handle page errors."""
        print(f"❌ Page error: {error}")
    
    def on_page_crash(self, error):
        """Handle page crashes."""
        print(f"💥 Page crash: {error}")
    
    def on_request(self, request):
        """Handle outgoing requests."""
        if "devpost.com" in request.url and request.method in ["POST", "PUT", "PATCH"]:
            print(f"📤 Form submission: {request.method} {request.url}")
    
    def on_response(self, response):
        """Handle responses."""
        if "devpost.com" in response.url and response.status in [200, 201, 302, 303]:
            print(f"📥 Response: {response.status} {response.url}")
    
    def wait_for_page_ready(self, timeout: int = 10000):
        """Wait for page to be fully ready with multiple checks."""
        print("⏳ Waiting for page to be ready...")
        
        try:
            # Wait for basic load
            self.page.wait_for_load_state("load", timeout=timeout)
            
            # Wait for DOM to be ready
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # Wait for network to be idle
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            
            # Additional check for DevPost-specific elements
            self.page.wait_for_selector("body", timeout=5000)
            
            # Check if we're on a DevPost page
            if "devpost.com" in self.page.url:
                print("✅ DevPost page loaded successfully")
                return True
            else:
                print("⚠️ Not on DevPost page")
                return False
                
        except Exception as e:
            print(f"⚠️ Page ready check failed: {e}")
            return False
    
    def detect_current_step(self):
        """Detect current step in submission flow with better detection."""
        try:
            current_url = self.page.url
            page_title = self.page.title()
            
            print(f"📄 Current page: {page_title}")
            print(f"🔗 Current URL: {current_url}")
            
            # Wait a moment for any dynamic content
            time.sleep(1)
            
            # Detect step based on URL patterns and page content
            if "project-overview" in current_url:
                self.current_step = "project_overview"
            elif "project_details" in current_url or "photo" in current_url:
                self.current_step = "project_details"
            elif "additional-info" in current_url:
                self.current_step = "additional_info"
            elif "submission" in current_url and "manage" in current_url:
                self.current_step = "submission_dashboard"
            else:
                # Try to detect by page content
                self.current_step = self.detect_step_by_content()
            
            print(f"🎯 Detected step: {self.current_step}")
            
            # Detect available navigation options
            self.detect_navigation_options()
            
        except Exception as e:
            print(f"❌ Step detection failed: {e}")
            import traceback
            traceback.print_exc()
    
    def detect_step_by_content(self) -> str:
        """Detect step by analyzing page content."""
        try:
            # Look for specific text patterns
            page_text = self.page.text_content("body").lower()
            
            if "project name" in page_text or "project title" in page_text:
                return "project_overview"
            elif "photo" in page_text or "image" in page_text or "screenshot" in page_text:
                return "project_details"
            elif "additional" in page_text or "more info" in page_text:
                return "additional_info"
            elif "submit" in page_text or "final" in page_text:
                return "submission"
            else:
                return "unknown"
                
        except Exception as e:
            print(f"❌ Content detection failed: {e}")
            return "unknown"
    
    def detect_navigation_options(self):
        """Detect available navigation options with better selectors."""
        try:
            # Look for step navigation with multiple selectors
            step_selectors = [
                ".step", ".wizard-step", ".form-step", 
                "a[class*='step']", "button[class*='step']",
                ".nav-step", ".progress-step", ".form-nav",
                "[data-step]", "[data-wizard-step]"
            ]
            
            all_steps = []
            for selector in step_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    all_steps.extend(elements)
                except:
                    continue
            
            print(f"📋 Found {len(all_steps)} potential navigation elements")
            
            for i, element in enumerate(all_steps, 1):
                try:
                    text = element.text_content().strip()
                    classes = element.get_attribute("class") or ""
                    href = element.get_attribute("href")
                    is_clickable = element.is_visible() and element.is_enabled()
                    
                    if text and len(text) < 100 and is_clickable:
                        print(f"   {i}. {text} (class: {classes})")
                        
                        # Determine step type
                        step_type = self.classify_step(text, classes, href)
                        self.submission_flow.append({
                            "text": text,
                            "classes": classes,
                            "href": href,
                            "type": step_type,
                            "element": element,
                            "clickable": is_clickable
                        })
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"❌ Navigation detection failed: {e}")
    
    def classify_step(self, text: str, classes: str, href: str) -> str:
        """Classify step type based on text and attributes."""
        text_lower = text.lower()
        classes_lower = classes.lower()
        
        if "overview" in text_lower or "project name" in text_lower:
            return "project_overview"
        elif "details" in text_lower or "photo" in text_lower or "image" in text_lower:
            return "project_details"
        elif "additional" in text_lower or "info" in text_lower:
            return "additional_info"
        elif "submit" in text_lower or "final" in text_lower:
            return "submission"
        elif "completed" in classes_lower:
            return "completed"
        elif "current" in classes_lower or "active" in classes_lower:
            return "current"
        else:
            return "unknown"
    
    def run_automated_flow(self):
        """Run automated submission flow with better error handling."""
        print("\n🤖 Starting Automated Flow")
        print("=" * 30)
        
        try:
            # Process current step
            success = self.process_current_step()
            if not success:
                print("⚠️ Current step processing failed, but continuing...")
            
            # Look for next step
            next_step = self.find_next_step()
            if next_step:
                print(f"🔄 Moving to next step: {next_step['text']}")
                success = self.navigate_to_step(next_step)
                if success:
                    print("✅ Navigation successful")
                    # Process the new step
                    self.process_current_step()
                else:
                    print("❌ Navigation failed")
            else:
                print("ℹ️ No next step found - may be at end of flow")
            
            print("\n✅ Automated flow complete!")
            print("🎮 Interactive mode available")
            
            # Start interactive mode
            self.interactive_mode()
            
        except Exception as e:
            print(f"❌ Automated flow failed: {e}")
            import traceback
            traceback.print_exc()
    
    def process_current_step(self) -> bool:
        """Process current step (fill forms, take screenshots, etc.)."""
        print(f"\n📝 Processing step: {self.current_step}")
        
        try:
            # Take screenshot
            self.take_step_screenshot()
            
            # Extract form data
            form_data = self.extract_current_form()
            if form_data:
                self.save_form_data(form_data)
            
            # Fill form if we have project data
            if self.project_data and form_data:
                filled_count = self.fill_current_form(form_data)
                return filled_count > 0
            
            return True
            
        except Exception as e:
            print(f"❌ Step processing failed: {e}")
            return False
    
    def find_next_step(self) -> Optional[Dict]:
        """Find next step in submission flow with better detection."""
        try:
            # Look for next/continue buttons with multiple selectors
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
            for step in self.submission_flow:
                if step["type"] in ["project_details", "additional_info", "submission"] and step.get("clickable", False):
                    return step
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to find next step: {e}")
            return None
    
    def navigate_to_step(self, step: Dict) -> bool:
        """Navigate to specific step with proper error handling."""
        try:
            if step["type"] == "next_button":
                print(f"🔄 Clicking: {step['text']}")
                step["element"].click()
            else:
                print(f"🔄 Clicking step: {step['text']}")
                step["element"].click()
            
            # Wait for navigation with multiple strategies
            success = self.wait_for_navigation()
            if success:
                # Update current step
                self.detect_current_step()
                return True
            else:
                print("⚠️ Navigation may not have completed")
                return False
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def wait_for_navigation(self, timeout: int = 10000) -> bool:
        """Wait for navigation to complete with multiple strategies."""
        try:
            # Strategy 1: Wait for URL change
            initial_url = self.page.url
            start_time = time.time()
            
            while time.time() - start_time < timeout / 1000:
                if self.page.url != initial_url:
                    print(f"✅ URL changed: {self.page.url}")
                    break
                time.sleep(0.1)
            else:
                print("⚠️ URL didn't change, checking for other indicators...")
            
            # Strategy 2: Wait for page load
            self.page.wait_for_load_state("load", timeout=timeout)
            
            # Strategy 3: Wait for network idle
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            
            # Strategy 4: Wait for specific elements
            self.page.wait_for_selector("body", timeout=5000)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Navigation wait failed: {e}")
            return False
    
    def extract_current_form(self) -> Optional[Dict]:
        """Extract current form data with better error handling."""
        try:
            # Find main form with multiple selectors
            form_selectors = ["form", "[role='form']", ".form", ".submission-form"]
            form = None
            
            for selector in form_selectors:
                try:
                    form = self.page.query_selector(selector)
                    if form:
                        break
                except:
                    continue
            
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
    
    def fill_current_form(self, form_data: Dict) -> int:
        """Fill current form with project data."""
        print("📝 Filling form with project data...")
        
        filled_count = 0
        for field in form_data["fields"]:
            if self.fill_field(field):
                filled_count += 1
        
        print(f"✅ Filled {filled_count}/{len(form_data['fields'])} fields")
        return filled_count
    
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
    
    def take_step_screenshot(self):
        """Take screenshot of current step."""
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
        print("Commands: next, prev, extract, screenshot, fill, quit")
        
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
                    form_data = self.extract_current_form()
                    if form_data:
                        self.save_form_data(form_data)
                elif command == "screenshot":
                    self.take_step_screenshot()
                elif command == "fill":
                    form_data = self.extract_current_form()
                    if form_data:
                        self.fill_current_form(form_data)
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🧠 Smart DevPost Navigator V2")
    print("=" * 40)
    
    # Load project data
    try:
        with open("sample_project_data.json", 'r') as f:
            project_data = json.load(f)
        print(f"📊 Loaded project data: {len(project_data)} fields")
    except Exception as e:
        print(f"⚠️ Could not load project data: {e}")
        project_data = {}
    
    # Start navigation
    base_url = "https://devpost.com/submit-to/25444-code-with-kiro-hackathon/manage/submissions/784734-untitled/project-overview"
    
    navigator = SmartDevPostNavigatorV2()
    navigator.start_navigation(base_url, project_data)

if __name__ == "__main__":
    main()







