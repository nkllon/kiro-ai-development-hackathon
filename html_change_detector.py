#!/usr/bin/env python3
"""
HTML Change Detector
===================

Detect HTML changes when navigating between DevPost form steps.
Captures before/after HTML to see what actually changes.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Detect HTML changes during navigation
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def detect_html_changes():
    """Detect HTML changes during navigation."""
    try:
        playwright = sync_playwright().start()

        # Get page info
        response = requests.get("http://localhost:9222/json")
        pages_info = response.json()

        devpost_page_info = None
        for p_info in pages_info:
            if "devpost.com" in p_info.get("url", "") and "submission" in p_info.get(
                "url", ""
            ):
                devpost_page_info = p_info
                break

        if not devpost_page_info:
            print("❌ No DevPost submission page found")
            return

        print(f"📄 Target page: {devpost_page_info['title']}")
        print(f"🔗 URL: {devpost_page_info['url']}")

        # Connect to browser
        print("🔍 Connecting to existing browser...")
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages

        # Find DevPost page
        target_page = None
        for page in pages:
            if "devpost.com" in page.url and "submission" in page.url:
                target_page = page
                break

        if not target_page:
            target_page = pages[0]

        print(f"✅ Connected to: {target_page.url}")

        # Wait for page to be ready
        print("⏳ Waiting for page to be ready...")
        target_page.wait_for_load_state("networkidle")

        # Capture initial HTML
        print(f"\n📄 Initial State:")
        print(f"   URL: {target_page.url}")
        print(f"   Title: {target_page.title()}")

        # Get initial HTML
        initial_html = target_page.content()
        print(f"   HTML length: {len(initial_html)} characters")

        # Save initial HTML
        timestamp = int(time.time())
        initial_filename = f"html_before_{timestamp}.html"
        with open(initial_filename, "w", encoding="utf-8") as f:
            f.write(initial_html)
        print(f"   📄 Saved initial HTML: {initial_filename}")

        # Get visible step navigation links
        step_links = target_page.query_selector_all("#steps-navigation a.step")
        visible_steps = []

        print(f"\n🎯 Available Step Navigation:")
        for i, step in enumerate(step_links, 1):
            text = step.text_content().strip()
            classes = step.get_attribute("class") or ""
            href = step.get_attribute("href") or ""
            is_visible = step.is_visible()
            is_enabled = step.is_enabled()

            if is_visible and is_enabled:
                visible_steps.append(
                    {"element": step, "text": text, "classes": classes, "href": href}
                )
                status = (
                    "📍 CURRENT"
                    if "current" in classes
                    else "✅ COMPLETED" if "completed" in classes else "⏳ AVAILABLE"
                )
                print(f"   {i}. {text} [{classes}] {status}")

        # Find next step
        next_step = None
        current_found = False

        for step in visible_steps:
            if "current" in step["classes"]:
                current_found = True
                print(f"📍 Current step: {step['text']}")
                continue

            if current_found and "current" not in step["classes"]:
                next_step = step
                print(f"➡️ Next step: {step['text']}")
                break

        if not next_step:
            print("❌ No next step found")
            return

        # Attempt navigation
        print(f"\n🔄 Attempting navigation to: {next_step['text']}")
        print(f"   -> {next_step['href']}")

        try:
            # Click the next step
            next_step["element"].click()
            print(f"✅ Click executed")

            # Wait for changes
            print(f"⏳ Waiting for changes...")
            time.sleep(3)

            # Check for navigation
            new_url = target_page.url
            new_title = target_page.title()

            print(f"\n📄 After Navigation:")
            print(f"   URL: {new_url}")
            print(f"   Title: {new_title}")

            # Get new HTML
            new_html = target_page.content()
            print(f"   HTML length: {len(new_html)} characters")

            # Save new HTML
            new_filename = f"html_after_{timestamp}.html"
            with open(new_filename, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"   📄 Saved new HTML: {new_filename}")

            # Compare HTML
            if new_html != initial_html:
                print(f"✅ HTML CHANGED!")
                print(
                    f"   Length change: {len(initial_html)} -> {len(new_html)} ({len(new_html) - len(initial_html):+d})"
                )

                # Look for specific changes in step navigation
                if (
                    "#steps-navigation" in new_html
                    and "#steps-navigation" in initial_html
                ):
                    print(f"   Step navigation section exists in both")

                    # Extract step navigation from both HTMLs
                    import re

                    initial_steps = re.findall(
                        r'<a[^>]*class="[^"]*step[^"]*"[^>]*>.*?</a>',
                        initial_html,
                        re.DOTALL,
                    )
                    new_steps = re.findall(
                        r'<a[^>]*class="[^"]*step[^"]*"[^>]*>.*?</a>',
                        new_html,
                        re.DOTALL,
                    )

                    print(f"   Initial steps: {len(initial_steps)}")
                    print(f"   New steps: {len(new_steps)}")

                    # Check for current step changes
                    initial_current = re.findall(
                        r'class="[^"]*current[^"]*"', initial_html
                    )
                    new_current = re.findall(r'class="[^"]*current[^"]*"', new_html)

                    print(f"   Initial current classes: {len(initial_current)}")
                    print(f"   New current classes: {len(new_current)}")

                    if len(new_current) != len(initial_current):
                        print(f"   ✅ Current step changed!")
                    else:
                        print(f"   ⚠️ Current step unchanged")

            else:
                print(f"❌ HTML UNCHANGED - No navigation occurred")

            # Take screenshot
            screenshot_filename = f"html_change_{timestamp}.png"
            target_page.screenshot(path=screenshot_filename)
            print(f"📸 Screenshot: {screenshot_filename}")

        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ HTML change detection failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()


if __name__ == "__main__":
    detect_html_changes()

