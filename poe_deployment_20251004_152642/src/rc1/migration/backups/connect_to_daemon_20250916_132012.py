#!/usr/bin/env python3
"""
Connect to Running DevPost Daemon
=================================

Connect to the already running browser daemon.
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def connect_to_daemon():
    """Connect to running daemon."""
    print("🔗 Connecting to running DevPost daemon...")

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")

        # Get existing context or create new one
        if browser.contexts:
            context = browser.contexts[0]
        else:
            context = browser.new_context()

        # Get existing page or create new one
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        print("✅ Connected to running daemon!")
        print(f"📄 Current page: {page.title()}")
        print(f"🔗 Current URL: {page.url}")

        # Interactive commands
        print("\n🎮 Available Commands:")
        print("navigate <url>     - Navigate to URL")
        print("next               - Click next step")
        print("prev               - Click previous step")
        print("steps              - Show navigation steps")
        print("goto <step>        - Go to specific step")
        print("extract            - Extract form data")
        print("screenshot         - Take screenshot")
        print("html               - Save HTML")
        print("quit               - Exit")
        print()

        while True:
            try:
                command = input("🔧 Command: ").strip().lower()

                if command == "quit":
                    break
                elif command.startswith("navigate "):
                    url = command.split(" ", 1)[1]
                    print(f"🌐 Navigating to: {url}")
                    page.goto(url, wait_until="networkidle")
                    print(f"📄 Title: {page.title()}")
                    print(f"🔗 URL: {page.url}")
                elif command == "next":
                    # Look for next step buttons
                    next_selectors = [
                        "button[class*='next']",
                        "a[class*='next']",
                        ".next-step",
                        "button:has-text('Next')",
                        "a:has-text('Next')",
                        "button:has-text('Continue')",
                        "a:has-text('Continue')",
                    ]

                    clicked = False
                    for selector in next_selectors:
                        try:
                            element = page.query_selector(selector)
                            if element and element.is_visible():
                                print(f"🔄 Clicking: {element.text_content().strip()}")
                                element.click()
                                page.wait_for_load_state("networkidle")
                                print(f"📄 New page: {page.title()}")
                                print(f"🔗 New URL: {page.url}")
                                clicked = True
                                break
                        except:
                            continue

                    if not clicked:
                        print("❌ No next step button found")
                elif command == "prev":
                    # Look for previous step buttons
                    prev_selectors = [
                        "button[class*='prev']",
                        "a[class*='prev']",
                        ".prev-step",
                        "button:has-text('Previous')",
                        "a:has-text('Previous')",
                        "button:has-text('Back')",
                        "a:has-text('Back')",
                    ]

                    clicked = False
                    for selector in prev_selectors:
                        try:
                            element = page.query_selector(selector)
                            if element and element.is_visible():
                                print(f"🔄 Clicking: {element.text_content().strip()}")
                                element.click()
                                page.wait_for_load_state("networkidle")
                                print(f"📄 New page: {page.title()}")
                                print(f"🔗 New URL: {page.url}")
                                clicked = True
                                break
                        except:
                            continue

                    if not clicked:
                        print("❌ No previous step button found")
                elif command == "steps":
                    # Find step navigation elements
                    step_selectors = [
                        ".step",
                        ".wizard-step",
                        ".form-step",
                        "a[class*='step']",
                    ]
                    steps = []

                    for selector in step_selectors:
                        elements = page.query_selector_all(selector)
                        for elem in elements:
                            text = elem.text_content().strip()
                            if text and len(text) < 100:
                                steps.append(
                                    {
                                        "text": text,
                                        "class": elem.get_attribute("class") or "",
                                        "href": elem.get_attribute("href"),
                                    }
                                )

                    if steps:
                        print("📋 Available navigation steps:")
                        for i, step in enumerate(steps, 1):
                            print(f"   {i}. {step['text']} (class: {step['class']})")
                    else:
                        print("❌ No navigation steps found")
                elif command.startswith("goto "):
                    step_text = command.split(" ", 1)[1]
                    # Find and click step
                    step_selectors = [
                        ".step",
                        ".wizard-step",
                        ".form-step",
                        "a[class*='step']",
                    ]

                    clicked = False
                    for selector in step_selectors:
                        elements = page.query_selector_all(selector)
                        for elem in elements:
                            text = elem.text_content().strip()
                            if step_text.lower() in text.lower():
                                print(f"🔄 Clicking step: {text}")
                                elem.click()
                                page.wait_for_load_state("networkidle")
                                print(f"📄 New page: {page.title()}")
                                print(f"🔗 New URL: {page.url}")
                                clicked = True
                                break
                        if clicked:
                            break

                    if not clicked:
                        print(f"❌ Step '{step_text}' not found")
                elif command == "extract":
                    # Extract form data
                    print("📊 Extracting form data...")

                    # Find main form
                    form = page.query_selector("#project-overview-form")
                    if not form:
                        forms = page.query_selector_all("form")
                        if forms:
                            form = forms[-1]

                    if not form:
                        print("❌ No form found!")
                        continue

                    print(f"✅ Found form: {form.get_attribute('id') or 'unnamed'}")

                    # Extract fields
                    fields = form.query_selector_all("input, textarea, select")
                    print(f"📝 Found {len(fields)} fields")

                    form_data = {
                        "form_id": form.get_attribute("id"),
                        "form_class": form.get_attribute("class"),
                        "form_action": form.get_attribute("action"),
                        "page_title": page.title(),
                        "page_url": page.url,
                        "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "fields": [],
                    }

                    for i, field in enumerate(fields, 1):
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

                    # Save data
                    output_file = f"devpost_form_{int(time.time())}.json"
                    with open(output_file, "w") as f:
                        json.dump(form_data, f, indent=2)

                    print(f"💾 Form data saved: {output_file}")

                    # Show summary
                    print(f"\n📊 Form Summary:")
                    print(f"   Fields: {len(form_data['fields'])}")
                    print(f"   Form ID: {form_data.get('form_id', 'Unknown')}")

                    # Show fields
                    print(f"\n📋 Fields:")
                    for field in form_data["fields"]:
                        print(
                            f"   {field['index']:2d}. {field['label']} ({field['tag']})"
                        )
                        print(f"       Name: {field['name']}")
                        print(
                            f"       Value: {field['value'][:50]}{'...' if len(field['value']) > 50 else ''}"
                        )
                        print(f"       Required: {field['required']}")
                        print()
                elif command == "screenshot":
                    # Take screenshot with descriptive name
                    page_title = page.title().replace(" ", "_").replace("/", "_")[:30]
                    url_parts = page.url.split("/")
                    hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
                    submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
                    timestamp = int(time.time())
                    filename = f"devpost_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"

                    page.screenshot(path=filename)
                    print(f"📸 Screenshot: {filename}")
                elif command == "html":
                    # Save HTML with descriptive name
                    page_title = page.title().replace(" ", "_").replace("/", "_")[:30]
                    url_parts = page.url.split("/")
                    hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
                    submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
                    timestamp = int(time.time())
                    filename = f"devpost_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.html"

                    html = page.content()
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"💾 HTML saved: {filename}")
                else:
                    print("❌ Unknown command")

            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        # Don't close browser, just disconnect
        playwright.stop()

    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("Make sure the browser daemon is running on port 9222")


if __name__ == "__main__":
    connect_to_daemon()


