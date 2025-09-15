#!/usr/bin/env python3
"""
Simple DevPost Form Extractor
=============================

Quick and simple form extraction without complex debugging.
"""

import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def extract_devpost_form():
    """Extract DevPost form data."""
    url = "https://devpost.com/submit-to/25444-code-with-kiro-hackathon/manage/submissions/784734-untitled/project-overview"

    print("🎯 DevPost Form Extractor")
    print("=" * 40)
    print(f"🌐 URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        try:
            print("🌐 Navigating to page...")
            page.goto(url, wait_until="networkidle")

            print("👤 Please authenticate and navigate to your submission form...")
            input("Press Enter when ready to extract form data...")

            # Get page info
            title = page.title()
            current_url = page.url
            print(f"📄 Title: {title}")
            print(f"🔗 URL: {current_url}")

            # Find the main form
            main_form = page.query_selector("#project-overview-form")
            if not main_form:
                print("❌ Main form not found!")
                return

            print("✅ Found main form: project-overview-form")

            # Extract all form fields
            fields = main_form.query_selector_all("input, textarea, select")
            print(f"📝 Found {len(fields)} form fields")

            form_data = {
                "hackathon_id": "25444-code-with-kiro-hackathon",
                "submission_id": "784734-untitled",
                "form_id": "project-overview-form",
                "page_title": title,
                "page_url": current_url,
                "fields": [],
            }

            for i, field in enumerate(fields, 1):
                # Get field properties
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
                    label_elem = page.query_selector(f"label[for='{field_id}']")
                    if label_elem:
                        field_label = label_elem.text_content().strip()

                # Get help text
                help_text = ""
                parent = field.evaluate("el => el.parentElement")
                if parent:
                    help_elem = page.evaluate(
                        """
                        (parent) => {
                            const help = parent.querySelector('.help-text, .hint, .description');
                            return help ? help.textContent.trim() : '';
                        }
                    """,
                        parent,
                    )
                    help_text = help_elem or ""

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
                    "help_text": help_text,
                }

                form_data["fields"].append(field_info)

                print(f"   {i}. {field_label} ({field_type})")
                print(f"      Name: {field_name}")
                print(f"      ID: {field_id}")
                print(
                    f"      Value: {field_value[:50]}{'...' if len(field_value) > 50 else ''}"
                )
                print(f"      Required: {field_required}")
                if field_placeholder:
                    print(f"      Placeholder: {field_placeholder}")
                if help_text:
                    print(
                        f"      Help: {help_text[:50]}{'...' if len(help_text) > 50 else ''}"
                    )
                print()

            # Save form data
            output_file = "devpost_form_extracted.json"
            with open(output_file, "w") as f:
                json.dump(form_data, f, indent=2)

            print(f"💾 Form data saved to: {output_file}")

            # Take screenshot
            page.screenshot(path="devpost_form_screenshot.png")
            print("📸 Screenshot saved: devpost_form_screenshot.png")

            print("\n🎉 Form extraction complete!")
            print(
                f"📊 Extracted {len(form_data['fields'])} fields from the DevPost submission form"
            )

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    extract_devpost_form()
