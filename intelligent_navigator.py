#!/usr/bin/env python3
"""
Intelligent Navigator
====================

Navigate through DevPost forms with intelligent decision making.
Stop on low probability decisions and analyze button context.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Intelligent form navigation with heuristic analysis
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def get_devpost_page_info():
    """Get the DevPost page info from the debugging port."""
    try:
        response = requests.get("http://localhost:9222/json")
        pages = response.json()

        # Find the DevPost page
        for page in pages:
            if "devpost.com" in page["url"] and "submission" in page["url"]:
                return page

        # If no DevPost page found, return the first page
        if pages:
            return pages[0]

        return None
    except Exception as e:
        print(f"❌ Failed to get page info: {e}")
        return None


def analyze_navigation_element(element, element_type, page):
    """Analyze any navigation element (button, link, image, etc.) for navigation probability."""
    try:
        # Get element text
        text = ""
        if hasattr(element, "text_content"):
            text = element.text_content().strip().lower()
        elif hasattr(element, "get_attribute"):
            text = element.get_attribute("alt") or element.get_attribute("title") or ""
            text = text.strip().lower()

        # Get element attributes
        classes = (
            element.get_attribute("class") or ""
            if hasattr(element, "get_attribute")
            else ""
        )
        href = (
            element.get_attribute("href") or ""
            if hasattr(element, "get_attribute")
            else ""
        )
        src = (
            element.get_attribute("src") or ""
            if hasattr(element, "get_attribute")
            else ""
        )
        onclick = (
            element.get_attribute("onclick") or ""
            if hasattr(element, "get_attribute")
            else ""
        )

        # Get element position and styling
        bounding_box = (
            element.bounding_box() if hasattr(element, "bounding_box") else None
        )

        # Get surrounding context
        try:
            parent = (
                element.evaluate("el => el.parentElement")
                if hasattr(element, "evaluate")
                else None
            )
            parent_text = parent.text_content().strip()[:200] if parent else ""
        except:
            parent_text = ""

        # Analyze element characteristics
        analysis = {
            "text": text,
            "classes": classes,
            "href": href,
            "src": src,
            "onclick": onclick,
            "position": bounding_box,
            "parent_text": parent_text,
            "is_visible": (
                element.is_visible() if hasattr(element, "is_visible") else True
            ),
            "is_enabled": (
                element.is_enabled() if hasattr(element, "is_enabled") else True
            ),
            "confidence": 0.0,
            "action": "unknown",
            "reasoning": [],
        }

        # DevPost-specific navigation patterns (highest confidence)
        if element_type == "devpost_next":
            analysis["confidence"] = 0.95
            analysis["action"] = "forward"
            analysis["reasoning"].append("DevPost next step link")

        elif element_type == "devpost_prev":
            analysis["confidence"] = 0.95
            analysis["action"] = "backward"
            analysis["reasoning"].append("DevPost previous step link")

        elif element_type == "devpost_step":
            # Check if it's a forward or backward step
            if "next" in classes or "next" in text:
                analysis["confidence"] = 0.9
                analysis["action"] = "forward"
                analysis["reasoning"].append("DevPost step link with next indicator")
            elif "previous" in classes or "prev" in text:
                analysis["confidence"] = 0.9
                analysis["action"] = "backward"
                analysis["reasoning"].append(
                    "DevPost step link with previous indicator"
                )
            elif "current" in classes:
                analysis["confidence"] = 0.1
                analysis["action"] = "current"
                analysis["reasoning"].append("DevPost current step (no navigation)")
            elif "completed" in classes:
                analysis["confidence"] = 0.3
                analysis["action"] = "completed"
                analysis["reasoning"].append(
                    "DevPost completed step (low navigation priority)"
                )
            else:
                analysis["confidence"] = 0.7
                analysis["action"] = "navigate"
                analysis["reasoning"].append("DevPost step link (general navigation)")

        # General high confidence navigation patterns
        elif any(
            word in text
            for word in [
                "next",
                "continue",
                "save and continue",
                "proceed",
                "forward",
                "→",
                ">",
            ]
        ):
            analysis["confidence"] = 0.8
            analysis["action"] = "forward"
            analysis["reasoning"].append("Contains forward navigation keywords")

        elif any(
            word in text for word in ["back", "previous", "return", "go back", "←", "<"]
        ):
            analysis["confidence"] = 0.8
            analysis["action"] = "backward"
            analysis["reasoning"].append("Contains backward navigation keywords")

        elif any(
            word in text for word in ["submit", "finish", "complete", "done", "save"]
        ):
            analysis["confidence"] = 0.7
            analysis["action"] = "submit"
            analysis["reasoning"].append("Contains submission keywords")

        # Image-based navigation analysis
        if element_type == "image":
            # Check for navigation-related alt text or src
            if any(
                word in text
                for word in [
                    "next",
                    "continue",
                    "forward",
                    "back",
                    "previous",
                    "arrow",
                    "nav",
                ]
            ):
                analysis["confidence"] = 0.8
                analysis["action"] = "navigate"
                analysis["reasoning"].append("Image with navigation-related alt text")

            # Check if image is in header/banner area
            if bounding_box and bounding_box["y"] < 200:  # Top 200px
                analysis["confidence"] += 0.3
                analysis["reasoning"].append("Image in header/banner area")

            # Check for arrow-like images
            if any(
                word in src.lower()
                for word in ["arrow", "next", "forward", "back", "nav"]
            ):
                analysis["confidence"] += 0.4
                analysis["reasoning"].append("Image source suggests navigation")

        # Link analysis
        elif element_type == "link":
            # Check href for navigation patterns
            if any(
                word in href.lower()
                for word in ["next", "continue", "forward", "step", "page"]
            ):
                analysis["confidence"] = 0.7
                analysis["action"] = "navigate"
                analysis["reasoning"].append("Link href suggests navigation")

            # Check for step indicators in URL
            if "step" in href.lower() or "page" in href.lower():
                analysis["confidence"] += 0.2
                analysis["reasoning"].append("Link contains step/page indicators")

        # Header element analysis
        elif element_type == "header":
            # Header elements are more likely to be navigation
            analysis["confidence"] += 0.2
            analysis["reasoning"].append("Element in header area")

            # Check for navigation classes
            if any(
                word in classes.lower()
                for word in ["nav", "navigation", "menu", "breadcrumb"]
            ):
                analysis["confidence"] += 0.3
                analysis["reasoning"].append("Has navigation-related classes")

        # Clickable div analysis
        elif element_type == "clickable_div":
            # Check for navigation-related onclick
            if any(
                word in onclick.lower()
                for word in ["next", "continue", "forward", "back", "submit"]
            ):
                analysis["confidence"] = 0.6
                analysis["action"] = "navigate"
                analysis["reasoning"].append("Clickable div with navigation onclick")

        # Analyze positioning
        if bounding_box:
            # Top area elements are more likely to be navigation
            if bounding_box["y"] < 300:  # Top 300px
                analysis["confidence"] += 0.2
                analysis["reasoning"].append("Positioned in top area")

            # Right side elements are often forward navigation
            if bounding_box["x"] > 500:  # Rough right side detection
                analysis["confidence"] += 0.1
                analysis["reasoning"].append("Positioned on right side")

        # Analyze CSS classes
        if "primary" in classes or "btn-primary" in classes:
            analysis["confidence"] += 0.1
            analysis["reasoning"].append("Primary styling")

        if "nav" in classes or "navigation" in classes or "breadcrumb" in classes:
            analysis["confidence"] += 0.3
            analysis["reasoning"].append("Navigation-related classes")

        # Analyze parent context
        if "form" in parent_text.lower():
            analysis["confidence"] += 0.1
            analysis["reasoning"].append("Inside form context")

        if "navigation" in parent_text.lower() or "nav" in parent_text.lower():
            analysis["confidence"] += 0.2
            analysis["reasoning"].append("Inside navigation context")

        return analysis

    except Exception as e:
        return {
            "text": "unknown",
            "confidence": 0.0,
            "action": "unknown",
            "reasoning": [f"Error analyzing: {e}"],
        }


def analyze_button_context(button, page):
    """Analyze button context to determine navigation probability."""
    try:
        # Get button text
        text = button.text_content().strip().lower()

        # Get button position and styling
        bounding_box = button.bounding_box()
        classes = button.get_attribute("class") or ""

        # Get surrounding context
        try:
            parent = button.evaluate("el => el.parentElement")
            parent_text = parent.text_content().strip()[:200] if parent else ""
        except:
            parent_text = ""

        # Analyze button characteristics
        analysis = {
            "text": text,
            "classes": classes,
            "position": bounding_box,
            "parent_text": parent_text,
            "is_visible": button.is_visible(),
            "is_enabled": button.is_enabled(),
            "confidence": 0.0,
            "action": "unknown",
            "reasoning": [],
        }

        # High confidence navigation patterns
        if any(
            word in text
            for word in ["next", "continue", "save and continue", "proceed"]
        ):
            analysis["confidence"] = 0.9
            analysis["action"] = "forward"
            analysis["reasoning"].append("Contains forward navigation keywords")

        elif any(word in text for word in ["back", "previous", "return", "go back"]):
            analysis["confidence"] = 0.9
            analysis["action"] = "backward"
            analysis["reasoning"].append("Contains backward navigation keywords")

        elif any(word in text for word in ["submit", "finish", "complete", "done"]):
            analysis["confidence"] = 0.8
            analysis["action"] = "submit"
            analysis["reasoning"].append("Contains submission keywords")

        # Medium confidence patterns
        elif "save" in text and "continue" not in text:
            analysis["confidence"] = 0.6
            analysis["action"] = "save"
            analysis["reasoning"].append("Save button - may not navigate")

        elif "copy" in text or "invite" in text:
            analysis["confidence"] = 0.3
            analysis["action"] = "utility"
            analysis["reasoning"].append("Utility button - unlikely to navigate")

        # Analyze positioning
        if bounding_box:
            # Right side buttons are often forward navigation
            if bounding_box["x"] > 500:  # Rough right side detection
                if analysis["confidence"] < 0.5:
                    analysis["confidence"] += 0.2
                    analysis["reasoning"].append("Positioned on right side")

        # Analyze CSS classes
        if "primary" in classes or "btn-primary" in classes:
            analysis["confidence"] += 0.1
            analysis["reasoning"].append("Primary button styling")

        if "secondary" in classes or "btn-secondary" in classes:
            analysis["confidence"] -= 0.1
            analysis["reasoning"].append("Secondary button styling")

        # Analyze parent context
        if "form" in parent_text.lower():
            analysis["confidence"] += 0.1
            analysis["reasoning"].append("Inside form context")

        if "navigation" in parent_text.lower() or "nav" in parent_text.lower():
            analysis["confidence"] += 0.2
            analysis["reasoning"].append("Inside navigation context")

        return analysis

    except Exception as e:
        return {
            "text": "unknown",
            "confidence": 0.0,
            "action": "unknown",
            "reasoning": [f"Error analyzing: {e}"],
        }


def make_navigation_decision(button_analyses, page_url, page_title):
    """Make intelligent navigation decision based on button analysis."""
    print(f"\n🧠 Making navigation decision...")
    print(f"📄 Page: {page_title}")
    print(f"🔗 URL: {page_url}")

    # Filter out low confidence buttons
    high_confidence_buttons = [b for b in button_analyses if b["confidence"] >= 0.7]
    medium_confidence_buttons = [
        b for b in button_analyses if 0.4 <= b["confidence"] < 0.7
    ]
    low_confidence_buttons = [b for b in button_analyses if b["confidence"] < 0.4]

    print(f"📊 Button Analysis:")
    print(f"   High confidence (≥0.7): {len(high_confidence_buttons)}")
    print(f"   Medium confidence (0.4-0.7): {len(medium_confidence_buttons)}")
    print(f"   Low confidence (<0.4): {len(low_confidence_buttons)}")

    # Display button analysis
    for i, analysis in enumerate(button_analyses, 1):
        confidence_bar = "█" * int(analysis["confidence"] * 10) + "░" * (
            10 - int(analysis["confidence"] * 10)
        )
        print(
            f"   {i}. {analysis['text']} [{confidence_bar}] {analysis['confidence']:.1f} - {analysis['action']}"
        )
        for reason in analysis["reasoning"]:
            print(f"      • {reason}")

    # Decision logic
    if high_confidence_buttons:
        # If we have high confidence buttons, choose the best one
        best_button = max(high_confidence_buttons, key=lambda x: x["confidence"])
        print(f"\n✅ High confidence decision: {best_button['text']}")
        return best_button, "high_confidence"

    elif medium_confidence_buttons:
        # Medium confidence - ask for confirmation
        print(f"\n⚠️ Medium confidence decision required")
        print("Available options:")
        for i, analysis in enumerate(medium_confidence_buttons, 1):
            print(
                f"   {i}. {analysis['text']} (confidence: {analysis['confidence']:.1f})"
            )

        try:
            choice = int(input("Choose button (number) or 0 to skip: ")) - 1
            if 0 <= choice < len(medium_confidence_buttons):
                return medium_confidence_buttons[choice], "medium_confidence"
            else:
                return None, "skipped"
        except ValueError:
            return None, "skipped"

    else:
        # Low confidence - stop and ask
        print(f"\n❌ Low confidence - stopping for manual decision")
        print("All buttons have low confidence. Manual intervention required.")
        return None, "low_confidence"


def main():
    """Main intelligent navigation function."""
    print("🧠 Intelligent DevPost Navigator")
    print("=" * 50)

    # Get page info first
    page_info = get_devpost_page_info()
    if not page_info:
        print("❌ No pages found!")
        return

    print(f"📄 Target page: {page_info['title']}")
    print(f"🔗 URL: {page_info['url']}")

    try:
        # Start Playwright
        playwright = sync_playwright().start()

        # Connect to existing browser
        print("🔍 Connecting to existing browser...")
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages

        # Find the DevPost page
        target_page = None
        for page in pages:
            if "devpost.com" in page.url and "submission" in page.url:
                target_page = page
                break

        if not target_page:
            target_page = pages[0]

        print(f"✅ Connected to: {target_page.url}")

        # Navigation loop
        navigation_count = 0
        max_navigations = 10

        while navigation_count < max_navigations:
            print(f"\n{'='*60}")
            print(f"🔄 Navigation Step {navigation_count + 1}")
            print(f"{'='*60}")

            # Analyze current page
            print(f"📄 Current page: {target_page.title()}")
            print(f"🔗 Current URL: {target_page.url}")

            # Get DevPost-specific navigation elements first
            steps_navigation = target_page.query_selector_all(
                "#steps-navigation a.step"
            )
            prev_links = target_page.query_selector_all("a.step.previous")
            next_links = target_page.query_selector_all("a.step.next")
            current_links = target_page.query_selector_all("a.step.current")
            completed_links = target_page.query_selector_all("a.step.completed")

            print(f"🎯 Found {len(steps_navigation)} step navigation links")
            print(f"⬅️ Found {len(prev_links)} previous links")
            print(f"➡️ Found {len(next_links)} next links")
            print(f"📍 Found {len(current_links)} current links")
            print(f"✅ Found {len(completed_links)} completed links")

            # Get other potential navigation elements
            buttons = target_page.query_selector_all(
                "button, input[type='button'], input[type='submit']"
            )
            other_links = target_page.query_selector_all("a:not(.step)")
            images = target_page.query_selector_all("img")
            clickable_divs = target_page.query_selector_all(
                "div[onclick], div[role='button'], div[tabindex]"
            )

            print(f"🔘 Found {len(buttons)} other buttons")
            print(f"🔗 Found {len(other_links)} other links")
            print(f"🖼️ Found {len(images)} images")
            print(f"📦 Found {len(clickable_divs)} clickable divs")

            # Combine all potential navigation elements, prioritizing DevPost steps
            all_elements = []
            # DevPost step navigation (highest priority)
            all_elements.extend([(link, "devpost_step") for link in steps_navigation])
            all_elements.extend([(link, "devpost_prev") for link in prev_links])
            all_elements.extend([(link, "devpost_next") for link in next_links])
            all_elements.extend([(link, "devpost_current") for link in current_links])
            all_elements.extend(
                [(link, "devpost_completed") for link in completed_links]
            )
            # Other elements (lower priority)
            all_elements.extend([(btn, "button") for btn in buttons])
            all_elements.extend([(link, "link") for link in other_links])
            all_elements.extend([(img, "image") for img in images])
            all_elements.extend([(div, "clickable_div") for div in clickable_divs])

            if not all_elements:
                print("❌ No navigation elements found - stopping navigation")
                break

            # Analyze each element
            element_analyses = []
            for i, (element, element_type) in enumerate(all_elements):
                try:
                    analysis = analyze_navigation_element(
                        element, element_type, target_page
                    )
                    analysis["element"] = element
                    analysis["type"] = element_type
                    element_analyses.append(analysis)
                except Exception as e:
                    print(f"⚠️ Error analyzing {element_type} {i+1}: {e}")
                    # Create a basic analysis for failed elements
                    try:
                        text = (
                            element.text_content().strip()
                            if hasattr(element, "text_content")
                            else "unknown"
                        )
                        element_analyses.append(
                            {
                                "text": text,
                                "confidence": 0.0,
                                "action": "unknown",
                                "reasoning": [f"Analysis failed: {e}"],
                                "element": element,
                                "type": element_type,
                            }
                        )
                    except:
                        element_analyses.append(
                            {
                                "text": "unknown",
                                "confidence": 0.0,
                                "action": "unknown",
                                "reasoning": [f"Complete analysis failure: {e}"],
                                "element": element,
                                "type": element_type,
                            }
                        )

            # Make navigation decision
            decision, confidence = make_navigation_decision(
                element_analyses, target_page.url, target_page.title()
            )

            if decision is None:
                if confidence == "low_confidence":
                    print("\n🛑 Stopping due to low confidence decision")
                    print("Please manually navigate and restart the script")
                    break
                elif confidence == "skipped":
                    print("\n⏭️ Skipping navigation")
                    break
                else:
                    print("\n❌ No valid decision made")
                    break

            # Execute navigation
            try:
                print(f"\n🔄 Clicking: {decision['text']}")
                decision["element"].click()

                # Wait for navigation
                target_page.wait_for_load_state("networkidle")

                # Check if we actually navigated
                new_url = target_page.url
                new_title = target_page.title()

                if new_url != page_info["url"] or new_title != page_info["title"]:
                    print(f"✅ Navigation successful!")
                    print(f"📄 New page: {new_title}")
                    print(f"🔗 New URL: {new_url}")
                    navigation_count += 1

                    # Update page info for next iteration
                    page_info["url"] = new_url
                    page_info["title"] = new_title
                else:
                    print(f"⚠️ No navigation detected - may be on same page")
                    break

            except Exception as e:
                print(f"❌ Navigation failed: {e}")
                break

        print(f"\n🏁 Navigation complete after {navigation_count} steps")

        # Final analysis
        print(f"\n📊 Final Page Analysis:")
        print(f"📄 Title: {target_page.title()}")
        print(f"🔗 URL: {target_page.url}")

        forms = target_page.query_selector_all("form")
        buttons = target_page.query_selector_all(
            "button, input[type='button'], input[type='submit']"
        )
        inputs = target_page.query_selector_all("input, textarea, select")

        print(
            f"📊 Elements: {len(forms)} forms, {len(buttons)} buttons, {len(inputs)} inputs"
        )

        # Take final screenshot
        try:
            timestamp = int(time.time())
            url_parts = target_page.url.split("/")
            hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
            submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
            page_title = target_page.title().replace(" ", "_").replace("/", "_")[:20]

            filename = f"intelligent_nav_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
            target_page.screenshot(path=filename)
            print(f"📸 Final screenshot: {filename}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")

    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
