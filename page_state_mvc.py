#!/usr/bin/env python3
"""
Page State MVC System
====================

Model-View-Controller architecture for DevPost page state detection
and intelligent navigation.

Model: PageState, FormData, NavigationState
View: BrowserView, ScreenshotView, UIView
Controller: PageController, NavigationController, FormController

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: MVC-based page state detection and navigation
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class PageStep(Enum):
    """Enumeration of possible page steps."""
    UNKNOWN = "unknown"
    LOGIN = "login"
    PROJECT_OVERVIEW = "project_overview"
    PROJECT_DETAILS = "project_details"
    ADDITIONAL_INFO = "additional_info"
    SUBMISSION = "submission"
    DASHBOARD = "dashboard"

@dataclass
class PageState:
    """Model: Current page state."""
    url: str
    title: str
    step: PageStep
    is_authenticated: bool
    has_form: bool
    form_count: int
    navigation_available: bool
    timestamp: float

@dataclass
class FormField:
    """Model: Individual form field."""
    name: str
    field_type: str
    value: str
    label: str
    required: bool
    placeholder: str
    element_id: str

@dataclass
class FormData:
    """Model: Complete form data."""
    form_id: str
    fields: List[FormField]
    action: str
    method: str
    step: PageStep
    extracted_at: float

@dataclass
class NavigationState:
    """Model: Navigation state."""
    current_step: PageStep
    available_steps: List[PageStep]
    next_step: Optional[PageStep]
    can_go_back: bool
    can_go_forward: bool

class BrowserView:
    """View: Browser interface and UI detection."""
    
    def __init__(self, page: Page):
        self.page = page
        self.screenshot_count = 0
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        try:
            return {
                "url": self.page.url,
                "title": self.page.title(),
                "viewport": self.page.viewport_size,
                "is_loading": self.page.evaluate("() => document.readyState") != "complete"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def detect_authentication_state(self) -> bool:
        """Detect if user is authenticated."""
        try:
            # Look for login indicators
            login_indicators = [
                "input[name='user[email]']",
                "input[name='user[password]']",
                ".login-form",
                "#user_email",
                "#user_password"
            ]
            
            for selector in login_indicators:
                if self.page.query_selector(selector):
                    return False  # Found login form, not authenticated
            
            # Look for authenticated indicators
            auth_indicators = [
                ".user-menu",
                ".profile-dropdown",
                "[data-testid='user-menu']",
                ".logout",
                "a[href*='logout']"
            ]
            
            for selector in auth_indicators:
                if self.page.query_selector(selector):
                    return True  # Found auth indicators
            
            return False
        except:
            return False
    
    def detect_forms(self) -> List[Dict[str, Any]]:
        """Detect all forms on the page."""
        try:
            forms = self.page.query_selector_all("form")
            form_data = []
            
            for i, form in enumerate(forms):
                form_info = {
                    "index": i,
                    "id": form.get_attribute("id") or f"form_{i}",
                    "class": form.get_attribute("class"),
                    "action": form.get_attribute("action"),
                    "method": form.get_attribute("method") or "get",
                    "field_count": len(form.query_selector_all("input, textarea, select"))
                }
                form_data.append(form_info)
            
            return form_data
        except Exception as e:
            return []
    
    def take_screenshot(self, prefix: str = "page") -> str:
        """Take screenshot with descriptive naming."""
        try:
            self.screenshot_count += 1
            timestamp = int(time.time())
            url_parts = self.page.url.split("/")
            hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
            submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
            page_title = self.page.title().replace(" ", "_").replace("/", "_")[:20]
            
            filename = f"devpost_{hackathon_id}_{submission_id}_{page_title}_{prefix}_{self.screenshot_count}_{timestamp}.png"
            self.page.screenshot(path=filename)
            return filename
        except Exception as e:
            return f"Error: {e}"

class PageStateModel:
    """Model: Page state management."""
    
    def __init__(self):
        self.current_state: Optional[PageState] = None
        self.state_history: List[PageState] = []
        self.form_data: Optional[FormData] = None
        self.navigation_state: Optional[NavigationState] = None
    
    def update_state(self, view: BrowserView) -> PageState:
        """Update current page state."""
        page_info = view.get_page_info()
        
        # Detect step from URL and content
        step = self._detect_step(page_info["url"], page_info["title"])
        
        # Detect authentication
        is_authenticated = view.detect_authentication_state()
        
        # Detect forms
        forms = view.detect_forms()
        has_form = len(forms) > 0
        form_count = len(forms)
        
        # Create new state
        new_state = PageState(
            url=page_info["url"],
            title=page_info["title"],
            step=step,
            is_authenticated=is_authenticated,
            has_form=has_form,
            form_count=form_count,
            navigation_available=True,  # Will be updated by controller
            timestamp=time.time()
        )
        
        # Update state
        if self.current_state:
            self.state_history.append(self.current_state)
        self.current_state = new_state
        
        return new_state
    
    def _detect_step(self, url: str, title: str) -> PageStep:
        """Detect current step from URL and title."""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if "login" in url_lower or "signin" in url_lower:
            return PageStep.LOGIN
        elif "project-overview" in url_lower or "overview" in url_lower:
            return PageStep.PROJECT_OVERVIEW
        elif "project_details" in url_lower or "photo" in url_lower or "image" in url_lower:
            return PageStep.PROJECT_DETAILS
        elif "additional-info" in url_lower or "additional" in url_lower:
            return PageStep.ADDITIONAL_INFO
        elif "submission" in url_lower and "manage" in url_lower:
            return PageStep.DASHBOARD
        elif "submit" in url_lower or "submit" in title_lower:
            return PageStep.SUBMISSION
        else:
            return PageStep.UNKNOWN

class FormController:
    """Controller: Form extraction and filling."""
    
    def __init__(self, view: BrowserView, model: PageStateModel):
        self.view = view
        self.model = model
        self.project_data = {}
    
    def extract_form_data(self) -> Optional[FormData]:
        """Extract form data from current page."""
        try:
            forms = self.view.detect_forms()
            if not forms:
                return None
            
            # Use first form
            form = self.view.page.query_selector("form")
            if not form:
                return None
            
            form_id = form.get_attribute("id") or "unnamed"
            action = form.get_attribute("action") or ""
            method = form.get_attribute("method") or "get"
            
            # Extract fields
            fields = form.query_selector_all("input, textarea, select")
            form_fields = []
            
            for i, field in enumerate(fields):
                try:
                    field_type = field.get_attribute("type") or field.evaluate("el => el.tagName").lower()
                    field_name = field.get_attribute("name") or f"field_{i}"
                    field_value = field.get_attribute("value") or ""
                    field_id = field.get_attribute("id") or ""
                    field_required = field.get_attribute("required") is not None
                    field_placeholder = field.get_attribute("placeholder") or ""
                    
                    # Get label
                    field_label = "Unlabeled"
                    if field_id:
                        label_elem = self.view.page.query_selector(f"label[for='{field_id}']")
                        if label_elem:
                            field_label = label_elem.text_content().strip()
                    
                    form_field = FormField(
                        name=field_name,
                        field_type=field_type,
                        value=field_value,
                        label=field_label,
                        required=field_required,
                        placeholder=field_placeholder,
                        element_id=field_id
                    )
                    
                    form_fields.append(form_field)
                    
                except Exception as e:
                    continue
            
            form_data = FormData(
                form_id=form_id,
                fields=form_fields,
                action=action,
                method=method,
                step=self.model.current_state.step if self.model.current_state else PageStep.UNKNOWN,
                extracted_at=time.time()
            )
            
            self.model.form_data = form_data
            return form_data
            
        except Exception as e:
            print(f"❌ Form extraction failed: {e}")
            return None
    
    def fill_form(self, project_data: Dict[str, Any]):
        """Fill form with project data."""
        if not self.model.form_data:
            print("❌ No form data to fill")
            return
        
        print(f"📝 Filling form: {self.model.form_data.form_id}")
        filled_count = 0
        
        for field in self.model.form_data.fields:
            if self._fill_field(field, project_data):
                filled_count += 1
        
        print(f"✅ Filled {filled_count}/{len(self.model.form_data.fields)} fields")
    
    def _fill_field(self, field: FormField, project_data: Dict[str, Any]) -> bool:
        """Fill a single form field."""
        try:
            # Skip hidden fields unless important
            if field.field_type == "hidden" and "token" not in field.name.lower():
                return False
            
            # Get value from project data
            value = self._get_field_value(field, project_data)
            if not value:
                return False
            
            # Find field element
            field_element = None
            if field.element_id:
                field_element = self.view.page.query_selector(f"#{field.element_id}")
            if not field_element and field.name:
                field_element = self.view.page.query_selector(f"[name='{field.name}']")
            
            if not field_element:
                return False
            
            # Fill field
            if field.field_type in ['text', 'email', 'url', 'tel', 'number']:
                field_element.fill(str(value))
            elif field.field_type == 'textarea':
                field_element.fill(str(value))
            elif field.field_type == 'select':
                field_element.select_option(str(value))
            
            print(f"   ✅ {field.label}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to fill {field.label}: {e}")
            return False
    
    def _get_field_value(self, field: FormField, project_data: Dict[str, Any]) -> Optional[str]:
        """Get value for field from project data."""
        field_name = field.name.lower()
        label = field.label.lower()
        
        # Project name/title
        if "title" in field_name or "project name" in label:
            return project_data.get("title", "")
        
        # Description/tagline
        elif "tagline" in field_name or "elevator pitch" in label or "description" in label:
            return project_data.get("description", "")
        
        # Technologies
        elif "built_with" in field_name or "technologies" in label:
            techs = project_data.get("technologies", [])
            return ", ".join(techs) if isinstance(techs, list) else str(techs)
        
        # Other fields...
        elif "challenge" in field_name or "challenge" in label:
            return project_data.get("challenges", "")
        elif "accomplishment" in field_name or "accomplishment" in label:
            return project_data.get("accomplishments", "")
        elif "learned" in field_name or "learning" in label:
            return project_data.get("learnings", "")
        elif "future" in field_name or "future" in label:
            return project_data.get("future_plans", "")
        elif "team" in field_name or "team" in label:
            team = project_data.get("team_members", [])
            return ", ".join(team) if isinstance(team, list) else str(team)
        elif "github" in field_name or "github" in label:
            return project_data.get("github_url", "")
        elif "website" in field_name or "url" in field_name or "website" in label:
            return project_data.get("website_url", "")
        
        return None

class NavigationController:
    """Controller: Navigation and page state management."""
    
    def __init__(self, view: BrowserView, model: PageStateModel):
        self.view = view
        self.model = model
        self.setup_page_events()
    
    def setup_page_events(self):
        """Set up page event listeners."""
        try:
            # Navigation events
            self.view.page.on("load", self._on_page_load)
            self.view.page.on("domcontentloaded", self._on_dom_loaded)
            self.view.page.on("networkidle", self._on_network_idle)
            
            # Form events
            self.view.page.on("console", self._on_console_message)
            
            print("✅ Page event listeners configured")
        except Exception as e:
            print(f"❌ Failed to setup page events: {e}")
    
    def _on_page_load(self, page: Page):
        """Handle page load event."""
        print(f"📄 Page loaded: {page.url}")
        self._update_state()
    
    def _on_dom_loaded(self, page: Page):
        """Handle DOM loaded event."""
        print(f"🌐 DOM loaded: {page.url}")
        self._update_state()
    
    def _on_network_idle(self, page: Page):
        """Handle network idle event."""
        print(f"🔌 Network idle: {page.url}")
        self._update_state()
    
    def _on_console_message(self, msg):
        """Handle console messages."""
        if msg.type in ["error", "warning"]:
            print(f"⚠️ Console {msg.type}: {msg.text}")
    
    def _update_state(self):
        """Update page state after events."""
        try:
            new_state = self.model.update_state(self.view)
            self._log_state_change(new_state)
        except Exception as e:
            print(f"❌ State update failed: {e}")
    
    def _log_state_change(self, state: PageState):
        """Log state changes."""
        print(f"🔄 State: {state.step.value} | Auth: {state.is_authenticated} | Forms: {state.form_count}")
    
    def find_next_step(self) -> Optional[Dict]:
        """Find next step in navigation."""
        try:
            # Look for next/continue buttons
            next_selectors = [
                "button:has-text('Next')", "a:has-text('Next')",
                "button:has-text('Continue')", "a:has-text('Continue')",
                "button:has-text('Save & Continue')", "a:has-text('Save & Continue')",
                "button[type='submit']", "input[type='submit']",
                ".next-step", ".step-next", "button[class*='next']"
            ]
            
            for selector in next_selectors:
                try:
                    element = self.view.page.query_selector(selector)
                    if element and element.is_visible() and element.is_enabled():
                        return {
                            "text": element.text_content().strip(),
                            "element": element,
                            "type": "next_button"
                        }
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"❌ Failed to find next step: {e}")
            return None
    
    def navigate_to_next(self) -> bool:
        """Navigate to next step."""
        try:
            next_step = self.find_next_step()
            if not next_step:
                print("❌ No next step found")
                return False
            
            print(f"🔄 Navigating: {next_step['text']}")
            next_step["element"].click()
            
            # Wait for navigation
            self.view.page.wait_for_load_state("networkidle")
            
            # Update state
            self._update_state()
            return True
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False

class PageStateMVC:
    """Main MVC controller."""
    
    def __init__(self, page: Page):
        self.view = BrowserView(page)
        self.model = PageStateModel()
        self.form_controller = FormController(self.view, self.model)
        self.nav_controller = NavigationController(self.view, self.model)
        self.project_data = {}
    
    def initialize(self, project_data: Dict[str, Any] = None):
        """Initialize the MVC system."""
        print("🎯 Initializing Page State MVC System")
        print("=" * 50)
        
        if project_data:
            self.project_data = project_data
            self.form_controller.project_data = project_data
            print(f"📊 Project data loaded: {len(project_data)} fields")
        
        # Initial state detection
        self.nav_controller._update_state()
        
        # Take initial screenshot
        screenshot = self.view.take_screenshot("initial")
        print(f"📸 Initial screenshot: {screenshot}")
        
        # Extract initial form if available
        if self.model.current_state and self.model.current_state.has_form:
            form_data = self.form_controller.extract_form_data()
            if form_data:
                self._save_form_data(form_data)
                
                # Fill form if we have project data
                if self.project_data:
                    self.form_controller.fill_form(self.project_data)
    
    def process_current_page(self):
        """Process current page."""
        print(f"\n📝 Processing current page")
        print(f"Step: {self.model.current_state.step.value if self.model.current_state else 'Unknown'}")
        print(f"URL: {self.model.current_state.url if self.model.current_state else 'Unknown'}")
        
        # Take screenshot
        screenshot = self.view.take_screenshot("process")
        print(f"📸 Screenshot: {screenshot}")
        
        # Extract form data
        if self.model.current_state and self.model.current_state.has_form:
            form_data = self.form_controller.extract_form_data()
            if form_data:
                self._save_form_data(form_data)
                
                # Fill form if we have project data
                if self.project_data:
                    self.form_controller.fill_form(self.project_data)
    
    def navigate_next(self):
        """Navigate to next step."""
        return self.nav_controller.navigate_to_next()
    
    def _save_form_data(self, form_data: FormData):
        """Save form data to JSON."""
        try:
            timestamp = int(time.time())
            filename = f"devpost_form_{form_data.step.value}_{timestamp}.json"
            
            # Convert to dict for JSON serialization
            form_dict = {
                "form_id": form_data.form_id,
                "action": form_data.action,
                "method": form_data.method,
                "step": form_data.step.value,
                "extracted_at": form_data.extracted_at,
                "fields": [
                    {
                        "name": field.name,
                        "field_type": field.field_type,
                        "value": field.value,
                        "label": field.label,
                        "required": field.required,
                        "placeholder": field.placeholder,
                        "element_id": field.element_id
                    }
                    for field in form_data.fields
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(form_dict, f, indent=2)
            print(f"💾 Form data saved: {filename}")
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
    
    def interactive_mode(self):
        """Start interactive mode."""
        print("\n🎮 Interactive Mode")
        print("=" * 20)
        print("Commands: next, extract, screenshot, fill, state, quit")
        
        while True:
            try:
                command = input("🔧 Command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "next":
                    self.navigate_next()
                elif command == "extract":
                    form_data = self.form_controller.extract_form_data()
                    if form_data:
                        self._save_form_data(form_data)
                elif command == "screenshot":
                    screenshot = self.view.take_screenshot("manual")
                    print(f"📸 Screenshot: {screenshot}")
                elif command == "fill":
                    if self.project_data:
                        self.form_controller.fill_form(self.project_data)
                    else:
                        print("❌ No project data loaded")
                elif command == "state":
                    if self.model.current_state:
                        print(f"Current state: {self.model.current_state}")
                    else:
                        print("❌ No current state")
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🎯 Page State MVC System")
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
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Initialize MVC system
        mvc = PageStateMVC(page)
        mvc.initialize(project_data)
        
        # Process current page
        mvc.process_current_page()
        
        # Start interactive mode
        mvc.interactive_mode()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure the browser daemon is running!")

if __name__ == "__main__":
    main()





