#!/usr/bin/env python3
"""
DevPost Form ORM System
=======================

Object-Relational Mapping system for DevPost submission forms.
Analyzes extracted form data and provides intelligent form filling.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: ORM-based form filling for DevPost submissions
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

@dataclass
class FormFieldMapping:
    """Mapping between form field and data source."""
    field_name: str
    field_id: str
    field_type: str
    label: str
    required: bool
    data_source: str  # Where to get the data from
    data_path: str    # Path to the data
    transformation: Optional[str] = None  # How to transform the data
    validation_rules: List[str] = field(default_factory=list)

@dataclass
class FormPage:
    """Represents a DevPost submission page."""
    page_name: str
    form_id: str
    url_pattern: str
    fields: List[FormFieldMapping]
    navigation_selectors: Dict[str, str] = field(default_factory=dict)
    submit_selectors: List[str] = field(default_factory=list)

class DevPostFormORM:
    """ORM system for DevPost forms."""
    
    def __init__(self):
        self.forms = {}
        self.project_data = {}
        self.browser = None
        self.page = None
        
    def load_form_data(self, json_file: str) -> Dict[str, Any]:
        """Load form data from JSON file."""
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {json_file}: {e}")
            return {}
    
    def analyze_forms(self, form_files: List[str]):
        """Analyze multiple form files and create ORM mappings."""
        print("🔍 Analyzing DevPost Forms for ORM Mapping")
        print("=" * 50)
        
        for form_file in form_files:
            form_data = self.load_form_data(form_file)
            if not form_data:
                continue
                
            form_id = form_data.get('form_id', 'unknown')
            page_url = form_data.get('page_url', '')
            fields = form_data.get('fields', [])
            
            print(f"\n📋 Analyzing Form: {form_id}")
            print(f"   URL: {page_url}")
            print(f"   Fields: {len(fields)}")
            
            # Determine page type based on URL and form ID
            page_type = self.determine_page_type(page_url, form_id)
            
            # Create field mappings
            field_mappings = []
            for field in fields:
                mapping = self.create_field_mapping(field, page_type)
                if mapping:
                    field_mappings.append(mapping)
            
            # Create form page
            form_page = FormPage(
                page_name=page_type,
                form_id=form_id,
                url_pattern=page_url,
                fields=field_mappings,
                navigation_selectors=self.get_navigation_selectors(page_type),
                submit_selectors=self.get_submit_selectors(page_type)
            )
            
            self.forms[page_type] = form_page
            
            print(f"   ✅ Mapped {len(field_mappings)} fields")
            self.print_field_summary(field_mappings)
    
    def determine_page_type(self, url: str, form_id: str) -> str:
        """Determine the type of page based on URL and form ID."""
        if "project-overview" in url or form_id == "project-overview-form":
            return "project_overview"
        elif "project_details" in url or form_id == "new_software_photo":
            return "project_details"
        elif "additional-info" in url or form_id == "additional-info-form":
            return "additional_info"
        else:
            return "unknown"
    
    def create_field_mapping(self, field: Dict[str, Any], page_type: str) -> Optional[FormFieldMapping]:
        """Create field mapping based on field data and page type."""
        field_name = field.get('name', '')
        field_id = field.get('id', '')
        field_type = field.get('tag', '')
        label = field.get('label', '')
        required = field.get('required', False)
        
        # Skip hidden fields unless they're important
        if field_type == 'hidden' and not any(x in field_name.lower() for x in ['token', 'method', 'version']):
            return None
        
        # Determine data source based on field name and label
        data_source, data_path, transformation = self.map_field_to_data_source(
            field_name, label, field_type, page_type
        )
        
        if not data_source:
            return None
        
        return FormFieldMapping(
            field_name=field_name,
            field_id=field_id,
            field_type=field_type,
            label=label,
            required=required,
            data_source=data_source,
            data_path=data_path,
            transformation=transformation,
            validation_rules=self.get_validation_rules(field)
        )
    
    def map_field_to_data_source(self, field_name: str, label: str, field_type: str, page_type: str) -> tuple:
        """Map field to data source."""
        field_lower = field_name.lower()
        label_lower = label.lower()
        
        # Project Overview mappings
        if page_type == "project_overview":
            if "title" in field_lower or "project name" in label_lower:
                return "project_data", "title", None
            elif "tagline" in field_lower or "elevator pitch" in label_lower:
                return "project_data", "description", "truncate_500"
            elif "version" in field_lower:
                return "static", "2", None
        
        # Project Details mappings
        elif page_type == "project_details":
            if "photo" in field_lower or "image" in field_lower:
                return "project_data", "image_path", None
            elif "video" in field_lower:
                return "project_data", "video_url", None
            elif "github" in field_lower:
                return "project_data", "github_url", None
            elif "website" in field_lower or "url" in field_lower:
                return "project_data", "website_url", None
        
        # Additional Info mappings
        elif page_type == "additional_info":
            if "built_with" in field_lower or "technologies" in field_lower:
                return "project_data", "technologies", "join_comma"
            elif "challenge" in field_lower:
                return "project_data", "challenges", None
            elif "accomplishment" in field_lower:
                return "project_data", "accomplishments", None
            elif "learned" in field_lower:
                return "project_data", "learnings", None
            elif "future" in field_lower:
                return "project_data", "future_plans", None
            elif "team" in field_lower:
                return "project_data", "team_members", "join_comma"
            elif "category" in field_lower:
                return "project_data", "category", None
            elif "prize" in field_lower:
                return "project_data", "prize_categories", "join_comma"
        
        # CSRF and method fields
        if "authenticity_token" in field_lower:
            return "form_data", "authenticity_token", None
        elif "utf8" in field_lower:
            return "static", "✓", None
        elif "_method" in field_lower:
            return "static", "patch", None
        
        return None, None, None
    
    def get_validation_rules(self, field: Dict[str, Any]) -> List[str]:
        """Get validation rules for a field."""
        rules = []
        
        if field.get('required', False):
            rules.append("required")
        
        # Add other validation rules based on field attributes
        if field.get('class', ''):
            if 'email' in field['class']:
                rules.append("email")
            if 'url' in field['class']:
                rules.append("url")
        
        return rules
    
    def get_navigation_selectors(self, page_type: str) -> Dict[str, str]:
        """Get navigation selectors for page type."""
        selectors = {
            "next": [
                "button[class*='next']", "a[class*='next']", ".next-step",
                "button:has-text('Next')", "a:has-text('Next')",
                "button:has-text('Continue')", "a:has-text('Continue')"
            ],
            "previous": [
                "button[class*='prev']", "a[class*='prev']", ".prev-step",
                "button:has-text('Previous')", "a:has-text('Previous')",
                "button:has-text('Back')", "a:has-text('Back')"
            ],
            "submit": [
                "button[type='submit']", "input[type='submit']",
                "button:has-text('Submit')", "button:has-text('Save')"
            ]
        }
        
        return selectors
    
    def get_submit_selectors(self, page_type: str) -> List[str]:
        """Get submit button selectors for page type."""
        return [
            "button[type='submit']", "input[type='submit']",
            "button:has-text('Submit')", "button:has-text('Save')",
            "button:has-text('Continue')", "button:has-text('Next')"
        ]
    
    def print_field_summary(self, field_mappings: List[FormFieldMapping]):
        """Print summary of field mappings."""
        for mapping in field_mappings:
            if mapping.data_source != "static":
                print(f"     • {mapping.label} → {mapping.data_source}.{mapping.data_path}")
    
    def set_project_data(self, project_data: Dict[str, Any]):
        """Set project data for form filling."""
        self.project_data = project_data
        print(f"📊 Project data loaded: {len(project_data)} fields")
    
    def connect_to_browser(self, port: int = 9222):
        """Connect to running browser daemon."""
        try:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
            
            if self.browser.contexts:
                context = self.browser.contexts[0]
            else:
                context = self.browser.new_context()
            
            if context.pages:
                self.page = context.pages[0]
            else:
                self.page = context.new_page()
            
            print("✅ Connected to browser daemon")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to browser: {e}")
            return False
    
    def fill_form(self, page_type: str, project_data: Dict[str, Any] = None):
        """Fill form for specific page type."""
        if page_type not in self.forms:
            print(f"❌ Unknown page type: {page_type}")
            return False
        
        if not self.page:
            print("❌ Not connected to browser")
            return False
        
        form_page = self.forms[page_type]
        print(f"📝 Filling form: {form_page.page_name}")
        print(f"   Form ID: {form_page.form_id}")
        print(f"   Fields: {len(form_page.fields)}")
        
        # Use provided data or stored data
        data = project_data or self.project_data
        
        filled_count = 0
        for mapping in form_page.fields:
            if self.fill_field(mapping, data):
                filled_count += 1
        
        print(f"✅ Filled {filled_count}/{len(form_page.fields)} fields")
        return True
    
    def fill_field(self, mapping: FormFieldMapping, data: Dict[str, Any]) -> bool:
        """Fill a single form field."""
        try:
            # Get field value
            value = self.get_field_value(mapping, data)
            if value is None:
                return False
            
            # Find field element
            field_element = None
            
            # Try by ID first
            if mapping.field_id:
                field_element = self.page.query_selector(f"#{mapping.field_id}")
            
            # Try by name
            if not field_element and mapping.field_name:
                field_element = self.page.query_selector(f"[name='{mapping.field_name}']")
            
            if not field_element:
                print(f"   ❌ Field not found: {mapping.label}")
                return False
            
            # Fill field based on type
            if mapping.field_type in ['text', 'email', 'url', 'tel', 'number']:
                field_element.fill(str(value))
            elif mapping.field_type == 'textarea':
                field_element.fill(str(value))
            elif mapping.field_type == 'select':
                field_element.select_option(str(value))
            elif mapping.field_type == 'file':
                # Handle file uploads
                if isinstance(value, str) and Path(value).exists():
                    field_element.set_input_files(value)
                else:
                    print(f"   ⚠️ File not found: {value}")
                    return False
            
            print(f"   ✅ {mapping.label}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to fill {mapping.label}: {e}")
            return False
    
    def get_field_value(self, mapping: FormFieldMapping, data: Dict[str, Any]) -> Any:
        """Get value for field from data source."""
        try:
            if mapping.data_source == "static":
                return mapping.data_path
            
            elif mapping.data_source == "project_data":
                value = data.get(mapping.data_path, "")
                
                # Apply transformations
                if mapping.transformation:
                    value = self.apply_transformation(value, mapping.transformation)
                
                return value
            
            elif mapping.data_source == "form_data":
                # This would be handled by the form itself
                return None
            
            return None
            
        except Exception as e:
            print(f"   ❌ Error getting value for {mapping.label}: {e}")
            return None
    
    def apply_transformation(self, value: Any, transformation: str) -> str:
        """Apply transformation to field value."""
        if not value:
            return ""
        
        if transformation == "truncate_500":
            return str(value)[:500]
        elif transformation == "join_comma":
            if isinstance(value, list):
                return ", ".join(str(x) for x in value)
            return str(value)
        elif transformation == "join_newline":
            if isinstance(value, list):
                return "\n".join(str(x) for x in value)
            return str(value)
        
        return str(value)
    
    def navigate_to_page(self, page_type: str) -> bool:
        """Navigate to specific page type."""
        if page_type not in self.forms:
            print(f"❌ Unknown page type: {page_type}")
            return False
        
        form_page = self.forms[page_type]
        print(f"🌐 Navigating to: {form_page.page_name}")
        
        try:
            self.page.goto(form_page.url_pattern, wait_until="networkidle")
            print(f"📄 Page loaded: {self.page.title()}")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def submit_form(self, page_type: str) -> bool:
        """Submit form for specific page type."""
        if page_type not in self.forms:
            print(f"❌ Unknown page type: {page_type}")
            return False
        
        form_page = self.forms[page_type]
        print(f"📤 Submitting form: {form_page.page_name}")
        
        try:
            # Look for submit button
            for selector in form_page.submit_selectors:
                submit_button = self.page.query_selector(selector)
                if submit_button and submit_button.is_visible():
                    print(f"🔄 Clicking submit: {submit_button.text_content().strip()}")
                    submit_button.click()
                    self.page.wait_for_load_state("networkidle")
                    print("✅ Form submitted successfully")
                    return True
            
            print("❌ No submit button found")
            return False
            
        except Exception as e:
            print(f"❌ Submit failed: {e}")
            return False
    
    def print_form_analysis(self):
        """Print analysis of all forms."""
        print("\n📊 DevPost Form ORM Analysis")
        print("=" * 50)
        
        for page_type, form_page in self.forms.items():
            print(f"\n📋 {form_page.page_name.upper()}")
            print(f"   Form ID: {form_page.form_id}")
            print(f"   URL: {form_page.url_pattern}")
            print(f"   Fields: {len(form_page.fields)}")
            
            # Show field mappings
            for mapping in form_page.fields:
                if mapping.data_source != "static":
                    print(f"     • {mapping.label} → {mapping.data_source}.{mapping.data_path}")

def main():
    """Main function for testing ORM."""
    print("🎯 DevPost Form ORM System")
    print("=" * 40)
    
    # Initialize ORM
    orm = DevPostFormORM()
    
    # Analyze forms (use the latest extracted forms)
    form_files = [
        "devpost_form_1757874108.json",  # Project Overview
        "devpost_form_1757874528.json",  # Project Details  
        "devpost_form_1757875233.json"   # Additional Info
    ]
    
    orm.analyze_forms(form_files)
    
    # Print analysis
    orm.print_form_analysis()
    
    # Connect to browser
    if orm.connect_to_browser():
        print("\n🎮 ORM Commands:")
        print("navigate <page>  - Navigate to page (project_overview, project_details, additional_info)")
        print("fill <page>      - Fill form for page")
        print("submit <page>    - Submit form for page")
        print("data <json>      - Load project data from JSON")
        print("quit             - Exit")
        print()
        
        # Interactive mode
        while True:
            try:
                command = input("🔧 ORM Command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command.startswith("navigate "):
                    page_type = command.split(" ", 1)[1]
                    orm.navigate_to_page(page_type)
                elif command.startswith("fill "):
                    page_type = command.split(" ", 1)[1]
                    orm.fill_form(page_type)
                elif command.startswith("submit "):
                    page_type = command.split(" ", 1)[1]
                    orm.submit_form(page_type)
                elif command.startswith("data "):
                    json_file = command.split(" ", 1)[1]
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    orm.set_project_data(data)
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

