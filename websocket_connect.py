#!/usr/bin/env python3
"""
WebSocket Connect
================

Connect directly to the DevPost page using WebSocket URL.
This bypasses the CDP connection issues.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Direct WebSocket connection to DevPost page
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def get_devpost_page_websocket():
    """Get the WebSocket URL for the DevPost page."""
    try:
        response = requests.get("http://localhost:9222/json")
        pages = response.json()

        # Find the DevPost page
        for page in pages:
            if "devpost.com" in page["url"] and "submission" in page["url"]:
                return page["webSocketDebuggerUrl"]

        # If no DevPost page found, return the first page
        if pages:
            return pages[0]["webSocketDebuggerUrl"]

        return None
    except Exception as e:
        print(f"❌ Failed to get WebSocket URL: {e}")
        return None


def main():
    """Connect to the DevPost page using WebSocket."""
    print("🔌 WebSocket Connect to DevPost Page")
    print("=" * 50)

    # Get WebSocket URL
    websocket_url = get_devpost_page_websocket()
    if not websocket_url:
        print("❌ No WebSocket URL found!")
        return

    print(f"🔗 WebSocket URL: {websocket_url}")

    try:
        # Start Playwright
        playwright = sync_playwright().start()

        # Connect to the browser first, then get the page
        print("🔍 Connecting to browser...")
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        print("✅ Connected to browser!")

        # Get the specific page
        print("🔍 Getting DevPost page...")
        pages = browser.pages
        if not pages:
            print("❌ No pages found!")
            return

        # Find the DevPost page
        page = None
        for p in pages:
            if "devpost.com" in p.url and "submission" in p.url:
                page = p
                break

        if not page:
            page = pages[0]  # Use first page if DevPost not found
            print(f"⚠️ DevPost page not found, using first page: {page.url}")
        else:
            print(f"✅ Found DevPost page: {page.url}")

        # Analyze the page
        print(f"\n🔍 Analyzing page...")
        print(f"📄 Title: {page.title()}")
        print(f"🔗 URL: {page.url}")

        # Count elements
        forms = page.query_selector_all("form")
        buttons = page.query_selector_all(
            "button, input[type='button'], input[type='submit']"
        )
        inputs = page.query_selector_all("input, textarea, select")
        links = page.query_selector_all("a")
        images = page.query_selector_all("img")

        print(f"\n📊 Elements found:")
        print(f"   Forms: {len(forms)}")
        print(f"   Buttons: {len(buttons)}")
        print(f"   Inputs: {len(inputs)}")
        print(f"   Links: {len(links)}")
        print(f"   Images: {len(images)}")

        # Analyze forms in detail
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

                # Analyze fields in this form
                fields = form.query_selector_all("input, textarea, select")
                for j, field in enumerate(fields[:10], 1):  # Show first 10 fields
                    try:
                        field_type = (
                            field.get_attribute("type")
                            or field.evaluate("el => el.tagName").lower()
                        )
                        name = field.get_attribute("name") or ""
                        element_id = field.get_attribute("id") or ""
                        placeholder = field.get_attribute("placeholder") or ""
                        value = field.get_attribute("value") or ""
                        required = field.get_attribute("required") is not None

                        # Get label
                        label = "Unlabeled"
                        if element_id:
                            label_elem = page.query_selector(
                                f"label[for='{element_id}']"
                            )
                            if label_elem:
                                label = label_elem.text_content().strip()

                        print(f"      Field {j}: {label} ({field_type})")
                        if name:
                            print(f"         Name: {name}")
                        if placeholder:
                            print(f"         Placeholder: {placeholder}")
                        if value:
                            print(f"         Value: {value[:50]}...")
                        if required:
                            print(f"         Required: Yes")
                    except Exception as e:
                        print(f"      Field {j}: Error analyzing - {e}")

        # Analyze buttons in detail
        if buttons:
            print(f"\n🔘 Button Analysis:")
            for i, button in enumerate(buttons[:15], 1):  # Show first 15
                try:
                    text = button.text_content().strip()
                    button_type = button.get_attribute("type") or "button"
                    classes = button.get_attribute("class") or ""
                    is_visible = button.is_visible()
                    is_enabled = button.is_enabled()

                    if text and len(text) < 100:
                        status = "✅" if is_visible and is_enabled else "❌"
                        print(f"   {status} {text} (type: {button_type})")
                        if classes:
                            print(f"      Classes: {classes}")
                except Exception as e:
                    print(f"   Button {i}: Error analyzing - {e}")

        # Look for navigation elements
        print(f"\n🧭 Navigation Analysis:")
        nav_keywords = [
            "next",
            "continue",
            "back",
            "previous",
            "submit",
            "save",
            "finish",
            "complete",
            "go",
            "click",
            "start",
            "begin",
        ]
        nav_buttons = []

        for button in buttons:
            try:
                text = button.text_content().strip().lower()
                if any(keyword in text for keyword in nav_keywords):
                    nav_buttons.append(
                        {
                            "text": button.text_content().strip(),
                            "element": button,
                            "type": button.get_attribute("type") or "button",
                        }
                    )
            except:
                continue

        if nav_buttons:
            print(f"   Found {len(nav_buttons)} navigation buttons:")
            for i, nav in enumerate(nav_buttons, 1):
                print(f"      {i}. {nav['text']} ({nav['type']})")
        else:
            print("   No obvious navigation buttons found")

        # Take screenshot
        try:
            timestamp = int(time.time())
            url_parts = page.url.split("/")
            hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
            submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
            page_title = page.title().replace(" ", "_").replace("/", "_")[:20]

            filename = f"websocket_analysis_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
            page.screenshot(path=filename)
            print(f"\n📸 Screenshot: {filename}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")

        # Interactive mode
        print(f"\n🎮 Interactive Mode")
        print("Commands: analyze, screenshot, navigate, quit")

        while True:
            try:
                command = input("🔧 Command: ").strip().lower()

                if command == "quit":
                    break
                elif command == "analyze":
                    # Re-analyze
                    forms = page.query_selector_all("form")
                    buttons = page.query_selector_all(
                        "button, input[type='button'], input[type='submit']"
                    )
                    print(
                        f"📊 Current state: {len(forms)} forms, {len(buttons)} buttons"
                    )
                elif command == "screenshot":
                    try:
                        timestamp = int(time.time())
                        filename = f"interactive_screenshot_{timestamp}.png"
                        page.screenshot(path=filename)
                        print(f"📸 Screenshot: {filename}")
                    except Exception as e:
                        print(f"❌ Screenshot failed: {e}")
                elif command == "navigate":
                    if nav_buttons:
                        print("🧭 Available navigation buttons:")
                        for i, nav in enumerate(nav_buttons, 1):
                            print(f"   {i}. {nav['text']}")

                        try:
                            choice = int(input("Choose button (number): ")) - 1
                            if 0 <= choice < len(nav_buttons):
                                print(f"🔄 Clicking: {nav_buttons[choice]['text']}")
                                nav_buttons[choice]["element"].click()

                                # Wait for navigation
                                page.wait_for_load_state("networkidle")

                                # Re-analyze
                                print("🔄 Page changed, re-analyzing...")
                                forms = page.query_selector_all("form")
                                buttons = page.query_selector_all(
                                    "button, input[type='button'], input[type='submit']"
                                )
                                print(
                                    f"📊 New state: {len(forms)} forms, {len(buttons)} buttons"
                                )
                                print(f"📄 New URL: {page.url}")
                                print(f"📄 New title: {page.title()}")
                            else:
                                print("❌ Invalid choice")
                        except ValueError:
                            print("❌ Invalid input")
                    else:
                        print("❌ No navigation buttons available")
                else:
                    print("❌ Unknown command")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
