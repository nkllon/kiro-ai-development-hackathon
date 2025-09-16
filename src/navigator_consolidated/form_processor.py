#!/usr/bin/env python3
"""
Form Processor - Form extraction and filling
===========================================

Extracted from smart_devpost_navigator_v2.py for RDI compliance.
Handles form data extraction, filling, and processing.
"""

import json
import time
from typing import Any, Dict, List, Optional


class FormProcessor:
    """Handles form data extraction and filling."""

    def __init__(self, navigator):
        self.navigator = navigator

    def extract_current_form(self) -> Optional[Dict]:
        """Extract current form data with better error handling."""
        try:
            # Find main form with multiple selectors
            form_selectors = ["form", "[role='form']", ".form", ".submission-form"]
            form = None

            for selector in form_selectors:
                try:
                    form = self.navigator.page.query_selector(selector)
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
                "page_title": self.navigator.page.title(),
                "page_url": self.navigator.page.url,
                "step": self.navigator.current_step,
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "fields": [],
            }

            for i, field in enumerate(fields, 1):
                try:
                    field_type = (
                        field.get_attribute("type")
                        or field.evaluate("el => el.tagName").lower()
                    )
                    field_name = field.get_attribute("name")
                    field_id = field.get_attribute("id")
                    field_value = field.get_attribute("value") or ""
                    field_placeholder = field.get_attribute("placeholder") or ""
                    field_required = field.get_attribute("required") is not None
                    field_class = field.get_attribute("class")

                    # Get label
                    field_label = "Unlabeled"
                    if field_id:
                        label_elem = self.navigator.page.query_selector(
                            f"label[for='{field_id}']"
                        )
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
                        "class": field_class,
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
                field_element = self.navigator.page.query_selector(f"#{field_id}")
            if not field_element and field_name:
                field_element = self.navigator.page.query_selector(f"[name='{field_name}']")

            if not field_element:
                return False

            # Fill field
            if field_type in ["text", "email", "url", "tel", "number"]:
                field_element.fill(str(value))
            elif field_type == "textarea":
                field_element.fill(str(value))
            elif field_type == "select":
                field_element.select_option(str(value))

            print(
                f"   ✅ {label}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}"
            )
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
            return self.navigator.project_data.get("title", "")

        # Description/tagline
        elif (
            "tagline" in field_name
            or "elevator pitch" in label
            or "description" in label
        ):
            return self.navigator.project_data.get("description", "")

        # Technologies
        elif "built_with" in field_name or "technologies" in label:
            techs = self.navigator.project_data.get("technologies", [])
            return ", ".join(techs) if isinstance(techs, list) else str(techs)

        # Challenges
        elif "challenge" in field_name or "challenge" in label:
            return self.navigator.project_data.get("challenges", "")

        # Accomplishments
        elif "accomplishment" in field_name or "accomplishment" in label:
            return self.navigator.project_data.get("accomplishments", "")

        # Learnings
        elif "learned" in field_name or "learning" in label:
            return self.navigator.project_data.get("learnings", "")

        # Future plans
        elif "future" in field_name or "future" in label:
            return self.navigator.project_data.get("future_plans", "")

        # Team members
        elif "team" in field_name or "team" in label:
            team = self.navigator.project_data.get("team_members", [])
            return ", ".join(team) if isinstance(team, list) else str(team)

        # GitHub URL
        elif "github" in field_name or "github" in label:
            return self.navigator.project_data.get("github_url", "")

        # Website URL
        elif "website" in field_name or "url" in field_name or "website" in label:
            return self.navigator.project_data.get("website_url", "")

        return None

    def save_form_data(self, form_data: Dict):
        """Save form data to JSON."""
        try:
            timestamp = int(time.time())
            filename = f"devpost_form_{self.navigator.current_step}_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(form_data, f, indent=2)
            print(f"💾 Form data: {filename}")
        except Exception as e:
            print(f"❌ Save failed: {e}")

