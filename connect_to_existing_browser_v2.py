#!/usr/bin/env python3
"""
Connect to Existing Browser V2
==============================

Connect to the EXISTING browser session and navigate to DevPost.
No new browser sessions - just connect and work with what's there.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Connect to existing browser without starting new sessions
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class ExistingBrowserConnectorV2:
    """Connect to existing browser session safely."""
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.project_data = {}
        self.telemetry_events = []
    
    def connect_and_navigate(self, project_data: Dict[str, Any] = None, target_url: str = None):
        """Connect to existing browser and navigate to target."""
        print("🔌 Connecting to Existing Browser V2")
        print("=" * 50)
        
        try:
            # Start Playwright
            playwright = sync_playwright().start()
            
            # Connect to existing browser via CDP
            print("🔍 Connecting to existing browser on port 9222...")
            self.browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Connected to existing browser!")
            
            # Get existing pages
            try:
                pages = self.browser.pages
                if pages:
                    self.page = pages[0]  # Use first page
                    print(f"📄 Using existing page: {self.page.url}")
                else:
                    # Create new page if none exist
                    self.page = self.browser.new_page()
                    print("📄 Created new page")
            except AttributeError:
                # If pages attribute doesn't exist, create new page
                self.page = self.browser.new_page()
                print("📄 Created new page")
            
            # Set project data
            if project_data:
                self.project_data = project_data
                print(f"📊 Project data loaded: {len(project_data)} fields")
            
            # Navigate to target URL if provided
            if target_url:
                print(f"🌐 Navigating to: {target_url}")
                self.page.goto(target_url, wait_until="networkidle")
                print(f"✅ Navigated to: {self.page.url}")
                print(f"📄 Page title: {self.page.title()}")
            
            # Analyze current page
            self.analyze_current_page()
            
            # Start interactive mode
            self.interactive_mode()
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            import traceback
            traceback.print_exc()
    
    def analyze_current_page(self):
        """Analyze current page with curiosity."""
        try:
            print(f"\n🔍 Analyzing current page...")
            print(f"URL: {self.page.url}")
            print(f"Title: {self.page.title()}")
            
            # Count elements
            forms = self.page.query_selector_all("form")
            buttons = self.page.query_selector_all("button, input[type='button'], input[type='submit']")
            inputs = self.page.query_selector_all("input, textarea, select")
            links = self.page.query_selector_all("a")
            images = self.page.query_selector_all("img")
            
            print(f"📊 Elements found:")
            print(f"   Forms: {len(forms)}")
            print(f"   Buttons: {len(buttons)}")
            print(f"   Inputs: {len(inputs)}")
            print(f"   Links: {len(links)}")
            print(f"   Images: {len(images)}")
            
            # Analyze forms
            if forms:
                print(f"\n📝 Form Analysis:")
                for i, form in enumerate(forms, 1):
                    form_id = form.get_attribute("id") or f"form_{i}"
                    form_class = form.get_attribute("class") or ""
                    form_action = form.get_attribute("action") or ""
                    field_count = len(form.query_selector_all("input, textarea, select"))
                    
                    print(f"   Form {i}: {form_id}")
                    print(f"      Class: {form_class}")
                    print(f"      Action: {form_action}")
                    print(f"      Fields: {field_count}")
            
            # Analyze buttons
            if buttons:
                print(f"\n🔘 Button Analysis:")
                for i, button in enumerate(buttons[:10], 1):  # Show first 10
                    try:
                        text = button.text_content().strip()
                        button_type = button.get_attribute("type") or "button"
                        classes = button.get_attribute("class") or ""
                        is_visible = button.is_visible()
                        is_enabled = button.is_enabled()
                        
                        if text and len(text) < 100:
                            status = "✅" if is_visible and is_enabled else "❌"
                            print(f"   {status} {text} (type: {button_type})")
                    except:
                        continue
            
            # Analyze inputs
            if inputs:
                print(f"\n📝 Input Analysis:")
                for i, input_elem in enumerate(inputs[:10], 1):  # Show first 10
                    try:
                        input_type = input_elem.get_attribute("type") or input_elem.evaluate("el => el.tagName").lower()
                        name = input_elem.get_attribute("name") or ""
                        element_id = input_elem.get_attribute("id") or ""
                        placeholder = input_elem.get_attribute("placeholder") or ""
                        value = input_elem.get_attribute("value") or ""
                        required = input_elem.get_attribute("required") is not None
                        
                        # Get label
                        label = "Unlabeled"
                        if element_id:
                            label_elem = self.page.query_selector(f"label[for='{element_id}']")
                            if label_elem:
                                label = label_elem.text_content().strip()
                        
                        if label != "Unlabeled" or name:
                            print(f"   {i}. {label} ({input_type})")
                            if name:
                                print(f"      Name: {name}")
                            if placeholder:
                                print(f"      Placeholder: {placeholder}")
                            if value:
                                print(f"      Value: {value[:50]}...")
                            if required:
                                print(f"      Required: Yes")
                    except:
                        continue
            
            # Take screenshot
            self.take_screenshot("analysis")
            
            # Log telemetry
            self.log_telemetry("page_analysis", {
                "url": self.page.url,
                "title": self.page.title(),
                "forms": len(forms),
                "buttons": len(buttons),
                "inputs": len(inputs),
                "links": len(links),
                "images": len(images)
            })
            
        except Exception as e:
            print(f"❌ Page analysis failed: {e}")
            self.log_telemetry("page_analysis", {}, False, str(e))
    
    def find_navigation_options(self) -> List[Dict[str, Any]]:
        """Find navigation options on current page."""
        try:
            navigation_options = []
            
            # Look for various navigation patterns
            nav_selectors = [
                "button", "a", "input[type='button']", "input[type='submit']",
                ".btn", ".button", ".link", ".nav", ".step", ".wizard",
                "[role='button']", "[role='link']", "[role='tab']"
            ]
            
            for selector in nav_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    for i, element in enumerate(elements):
                        try:
                            text = element.text_content().strip()
                            href = element.get_attribute("href")
                            onclick = element.get_attribute("onclick")
                            classes = element.get_attribute("class")
                            is_visible = element.is_visible()
                            is_enabled = element.is_enabled()
                            
                            if text and len(text) < 200 and is_visible and is_enabled:
                                # Check if this looks like navigation
                                text_lower = text.lower()
                                nav_keywords = ["next", "continue", "back", "previous", "submit", "save", "finish", "complete", "go", "click", "start", "begin"]
                                
                                if any(keyword in text_lower for keyword in nav_keywords) or href or onclick:
                                    navigation_options.append({
                                        "selector": selector,
                                        "index": i,
                                        "text": text,
                                        "href": href,
                                        "onclick": onclick,
                                        "classes": classes,
                                        "is_visible": is_visible,
                                        "is_enabled": is_enabled,
                                        "element_type": element.evaluate("el => el.tagName").lower()
                                    })
                        except:
                            continue
                except:
                    continue
            
            return navigation_options
            
        except Exception as e:
            print(f"❌ Failed to find navigation options: {e}")
            return []
    
    def navigate_to_element(self, element_info: Dict[str, Any]) -> bool:
        """Navigate to a specific element."""
        try:
            # Find the element
            element = None
            if element_info["id"]:
                element = self.page.query_selector(f"#{element_info['id']}")
            elif element_info["text"]:
                # Try to find by text
                elements = self.page.query_selector_all(f"button:has-text('{element_info['text']}'), a:has-text('{element_info['text']}')")
                if elements:
                    element = elements[0]
            
            if not element:
                print(f"❌ Could not find element: {element_info['text']}")
                return False
            
            print(f"🔄 Clicking: {element_info['text']}")
            element.click()
            
            # Wait for navigation
            self.page.wait_for_load_state("networkidle")
            
            # Analyze new page
            self.analyze_current_page()
            
            self.log_telemetry("navigation", {
                "element_text": element_info["text"],
                "success": True
            })
            
            return True
            
        except Exception as e:
            self.log_telemetry("navigation", {
                "element_text": element_info.get("text", ""),
                "success": False
            }, False, str(e))
            print(f"❌ Navigation failed: {e}")
            return False
    
    def take_screenshot(self, prefix: str = "page"):
        """Take screenshot with descriptive naming."""
        try:
            timestamp = int(time.time())
            url_parts = self.page.url.split("/")
            hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
            submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
            page_title = self.page.title().replace(" ", "_").replace("/", "_")[:20]
            
            filename = f"connected_{hackathon_id}_{submission_id}_{page_title}_{prefix}_{timestamp}.png"
            self.page.screenshot(path=filename)
            print(f"📸 Screenshot: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def log_telemetry(self, event_type: str, data: Dict[str, Any], success: bool = True, error: str = None):
        """Log telemetry event."""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "page_url": self.page.url if self.page else "unknown",
            "page_title": self.page.title() if self.page else "unknown",
            "data": data,
            "success": success,
            "error": error
        }
        self.telemetry_events.append(event)
        
        status = "✅" if success else "❌"
        print(f"{status} {event_type}: {self.page.url if self.page else 'unknown'} | {data.get('summary', '')}")
        if error:
            print(f"   Error: {error}")
    
    def interactive_mode(self):
        """Start interactive mode."""
        print("\n🎮 Interactive Mode")
        print("=" * 20)
        print("Commands: analyze, navigate, screenshot, telemetry, quit")
        
        while True:
            try:
                command = input("🔧 Command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "analyze":
                    self.analyze_current_page()
                elif command == "navigate":
                    options = self.find_navigation_options()
                    if options:
                        print("🧭 Available navigation options:")
                        for i, option in enumerate(options[:10], 1):
                            print(f"   {i}. {option['text']} ({option['element_type']})")
                        
                        try:
                            choice = int(input("Choose option (number): ")) - 1
                            if 0 <= choice < len(options):
                                self.navigate_to_element(options[choice])
                            else:
                                print("❌ Invalid choice")
                        except ValueError:
                            print("❌ Invalid input")
                    else:
                        print("❌ No navigation options found")
                elif command == "screenshot":
                    self.take_screenshot("manual")
                elif command == "telemetry":
                    print(f"📊 Telemetry Summary:")
                    print(f"   Total events: {len(self.telemetry_events)}")
                    successful = len([e for e in self.telemetry_events if e["success"]])
                    print(f"   Successful: {successful}")
                    print(f"   Failed: {len(self.telemetry_events) - successful}")
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🔌 Connect to Existing Browser V2")
    print("=" * 40)
    
    # Load project data
    try:
        with open("sample_project_data.json", 'r') as f:
            project_data = json.load(f)
        print(f"📊 Loaded project data: {len(project_data)} fields")
    except Exception as e:
        print(f"⚠️ Could not load project data: {e}")
        project_data = {}
    
    # Target URL
    target_url = "https://devpost.com/submit-to/25444-code-with-kiro-hackathon/manage/submissions/784734-untitled/project-overview"
    
    # Connect to existing browser
    connector = ExistingBrowserConnectorV2()
    connector.connect_and_navigate(project_data, target_url)

if __name__ == "__main__":
    main()







