#!/usr/bin/env python3
"""
Debug DevPost Page
==================

Simple script to debug what's on a DevPost page and understand its structure.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Debug DevPost page structure for form interrogation
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def debug_devpost_page(url: str):
    """Debug a DevPost page to understand its structure."""
    print(f"🔍 Debugging DevPost page: {url}")
    print("=" * 60)

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        try:
            # Navigate to page
            print("🌐 Navigating to page...")
            page.goto(url, wait_until="networkidle")

            # Wait for user to authenticate
            print("👤 Please log in to DevPost in the browser window...")
            print("📝 Navigate to your submission page and press Enter when ready...")
            input("Press Enter when you're ready to analyze the page...")

            # Take screenshot
            print("📸 Taking screenshot...")
            page.screenshot(path="devpost_debug_screenshot.png")

            # Get page title
            title = page.title()
            print(f"📄 Page Title: {title}")

            # Get page URL
            current_url = page.url
            print(f"🔗 Current URL: {current_url}")

            # Look for form elements
            print("\n🔍 Looking for form elements...")
            form_selectors = [
                "form",
                "input",
                "textarea",
                "select",
                "button",
                "[data-testid*='form']",
                "[data-testid*='input']",
                "[data-testid*='field']",
                ".form",
                ".input",
                ".field",
                ".step",
                ".section",
            ]

            for selector in form_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    print(
                        f"   ✅ Found {len(elements)} elements with selector: {selector}"
                    )

                    # Show first few elements
                    for i, element in enumerate(elements[:3]):
                        tag_name = element.evaluate("el => el.tagName")
                        element_id = element.get_attribute("id")
                        element_class = element.get_attribute("class")
                        element_type = element.get_attribute("type")
                        element_name = element.get_attribute("name")

                        print(
                            f"      {i+1}. <{tag_name.lower()}> id='{element_id}' class='{element_class}' type='{element_type}' name='{element_name}'"
                        )
                else:
                    print(f"   ❌ No elements found with selector: {selector}")

            # Look for specific DevPost patterns
            print("\n🔍 Looking for DevPost-specific patterns...")
            devpost_selectors = [
                "[data-testid*='submission']",
                "[data-testid*='hackathon']",
                "[data-testid*='project']",
                ".submission",
                ".hackathon",
                ".project",
                ".challenge",
                ".wizard",
                ".step",
                ".page",
            ]

            for selector in devpost_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    print(
                        f"   ✅ Found {len(elements)} DevPost elements with selector: {selector}"
                    )

                    # Show first few elements
                    for i, element in enumerate(elements[:2]):
                        tag_name = element.evaluate("el => el.tagName")
                        element_id = element.get_attribute("id")
                        element_class = element.get_attribute("class")
                        text_content = element.text_content()

                        print(
                            f"      {i+1}. <{tag_name.lower()}> id='{element_id}' class='{element_class}'"
                        )
                        if text_content:
                            print(
                                f"         Text: {text_content[:100]}{'...' if len(text_content) > 100 else ''}"
                            )
                else:
                    print(f"   ❌ No DevPost elements found with selector: {selector}")

            # Get page HTML structure
            print("\n🔍 Analyzing page structure...")
            html = page.content()

            # Look for common form patterns in HTML
            form_patterns = [
                "form",
                "input",
                "textarea",
                "select",
                "button",
                "fieldset",
                "label",
            ]

            for pattern in form_patterns:
                count = html.count(f"<{pattern}")
                print(f"   📊 Found {count} <{pattern}> tags in HTML")

            # Look for JavaScript frameworks
            js_frameworks = [
                "React",
                "Vue",
                "Angular",
                "jQuery",
                "Bootstrap",
                "Material-UI",
            ]

            print("\n🔍 Looking for JavaScript frameworks...")
            for framework in js_frameworks:
                if framework.lower() in html.lower():
                    print(f"   ✅ Found {framework} in page")
                else:
                    print(f"   ❌ {framework} not found")

            # Save HTML for analysis
            with open("devpost_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n💾 Page HTML saved to: devpost_debug.html")

            print(f"\n✅ Debug complete! Check the files:")
            print(f"   📸 Screenshot: devpost_debug_screenshot.png")
            print(f"   📄 HTML: devpost_debug.html")

        except Exception as e:
            print(f"❌ Error debugging page: {e}")
        finally:
            browser.close()


def main():
    """Main function."""
    print("🔍 DevPost Page Debug Tool")
    print("=" * 40)

    url = input("Enter DevPost URL: ").strip()
    if not url:
        print("❌ No URL provided. Exiting.")
        return

    if not url.startswith("http"):
        url = "https://" + url

    debug_devpost_page(url)


if __name__ == "__main__":
    main()
