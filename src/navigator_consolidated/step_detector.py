#!/usr/bin/env python3
"""
Step Detector - Navigation step detection and management
======================================================

Extracted from smart_devpost_navigator_v2.py for RDI compliance.
Handles step detection, navigation, and flow management.
"""

import time
from typing import Any, Dict, List, Optional


class StepDetector:
    """Handles step detection and navigation logic."""

    def __init__(self, navigator):
        self.navigator = navigator

    def detect_current_step(self):
        """Detect current step in submission flow with better detection."""
        try:
            current_url = self.navigator.page.url
            page_title = self.navigator.page.title()

            print(f"📄 Current page: {page_title}")
            print(f"🔗 Current URL: {current_url}")

            # Wait a moment for any dynamic content
            time.sleep(1)

            # Detect step based on URL patterns and page content
            if "project-overview" in current_url:
                self.navigator.current_step = "project_overview"
            elif "project_details" in current_url or "photo" in current_url:
                self.navigator.current_step = "project_details"
            elif "additional-info" in current_url:
                self.navigator.current_step = "additional_info"
            elif "submission" in current_url and "manage" in current_url:
                self.navigator.current_step = "submission_dashboard"
            else:
                # Try to detect by page content
                self.navigator.current_step = self.detect_step_by_content()

            print(f"🎯 Detected step: {self.navigator.current_step}")

            # Detect available navigation options
            self.detect_navigation_options()

        except Exception as e:
            print(f"❌ Step detection failed: {e}")
            import traceback
            traceback.print_exc()

    def detect_step_by_content(self) -> str:
        """Detect step by analyzing page content."""
        try:
            # Look for specific text patterns
            page_text = self.navigator.page.text_content("body").lower()

            if "project name" in page_text or "project title" in page_text:
                return "project_overview"
            elif (
                "photo" in page_text
                or "image" in page_text
                or "screenshot" in page_text
            ):
                return "project_details"
            elif "additional" in page_text or "more info" in page_text:
                return "additional_info"
            elif "submit" in page_text or "final" in page_text:
                return "submission"
            else:
                return "unknown"

        except Exception as e:
            print(f"❌ Content detection failed: {e}")
            return "unknown"

    def detect_navigation_options(self):
        """Detect available navigation options with better selectors."""
        try:
            # Look for step navigation with multiple selectors
            step_selectors = [
                ".step",
                ".wizard-step",
                ".form-step",
                "a[class*='step']",
                "button[class*='step']",
                ".nav-step",
                ".progress-step",
                ".form-nav",
                "[data-step]",
                "[data-wizard-step]",
            ]

            all_steps = []
            for selector in step_selectors:
                try:
                    elements = self.navigator.page.query_selector_all(selector)
                    all_steps.extend(elements)
                except:
                    continue

            print(f"📋 Found {len(all_steps)} potential navigation elements")

            for i, element in enumerate(all_steps, 1):
                try:
                    text = element.text_content().strip()
                    classes = element.get_attribute("class") or ""
                    href = element.get_attribute("href")
                    is_clickable = element.is_visible() and element.is_enabled()

                    if text and len(text) < 100 and is_clickable:
                        print(f"   {i}. {text} (class: {classes})")

                        # Determine step type
                        step_type = self.classify_step(text, classes, href)
                        self.navigator.submission_flow.append(
                            {
                                "text": text,
                                "classes": classes,
                                "href": href,
                                "type": step_type,
                                "element": element,
                                "clickable": is_clickable,
                            }
                        )
                except Exception as e:
                    continue

        except Exception as e:
            print(f"❌ Navigation detection failed: {e}")

    def classify_step(self, text: str, classes: str, href: str) -> str:
        """Classify step type based on text and attributes."""
        text_lower = text.lower()
        classes_lower = classes.lower()

        if "overview" in text_lower or "project name" in text_lower:
            return "project_overview"
        elif "details" in text_lower or "photo" in text_lower or "image" in text_lower:
            return "project_details"
        elif "additional" in text_lower or "info" in text_lower:
            return "additional_info"
        elif "submit" in text_lower or "final" in text_lower:
            return "submission"
        elif "completed" in classes_lower:
            return "completed"
        elif "current" in classes_lower or "active" in classes_lower:
            return "current"
        else:
            return "unknown"

    def find_next_step(self) -> Optional[Dict]:
        """Find next step in submission flow with better detection."""
        try:
            # Look for next/continue buttons with multiple selectors
            next_selectors = [
                "button:has-text('Next')",
                "a:has-text('Next')",
                "button:has-text('Continue')",
                "a:has-text('Continue')",
                "button:has-text('Save & Continue')",
                "a:has-text('Save & Continue')",
                "button:has-text('Save and Continue')",
                "a:has-text('Save and Continue')",
                ".next-step",
                ".step-next",
                "button[class*='next']",
                "a[class*='next']",
                "button[type='submit']",
                "input[type='submit']",
                ".btn-next",
                ".btn-continue",
                ".continue-btn",
            ]

            for selector in next_selectors:
                try:
                    element = self.navigator.page.query_selector(selector)
                    if element and element.is_visible() and element.is_enabled():
                        return {
                            "text": element.text_content().strip(),
                            "element": element,
                            "type": "next_button",
                        }
                except:
                    continue

            # Look for step navigation
            for step in self.navigator.submission_flow:
                if step["type"] in [
                    "project_details",
                    "additional_info",
                    "submission",
                ] and step.get("clickable", False):
                    return step

            return None

        except Exception as e:
            print(f"❌ Failed to find next step: {e}")
            return None

    def navigate_to_step(self, step: Dict) -> bool:
        """Navigate to specific step with proper error handling."""
        try:
            if step["type"] == "next_button":
                print(f"🔄 Clicking: {step['text']}")
                step["element"].click()
            else:
                print(f"🔄 Clicking step: {step['text']}")
                step["element"].click()

            # Wait for navigation with multiple strategies
            success = self.wait_for_navigation()
            if success:
                # Update current step
                self.detect_current_step()
                return True
            else:
                print("⚠️ Navigation may not have completed")
                return False

        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False

    def wait_for_navigation(self, timeout: int = 10000) -> bool:
        """Wait for navigation to complete with multiple strategies."""
        try:
            # Strategy 1: Wait for URL change
            initial_url = self.navigator.page.url
            start_time = time.time()

            while time.time() - start_time < timeout / 1000:
                if self.navigator.page.url != initial_url:
                    print(f"✅ URL changed: {self.navigator.page.url}")
                    break
                time.sleep(0.1)
            else:
                print("⚠️ URL didn't change, checking for other indicators...")

            # Strategy 2: Wait for page load
            self.navigator.page.wait_for_load_state("load", timeout=timeout)

            # Strategy 3: Wait for network idle
            self.navigator.page.wait_for_load_state("networkidle", timeout=timeout)

            # Strategy 4: Wait for specific elements
            self.navigator.page.wait_for_selector("body", timeout=5000)

            return True

        except Exception as e:
            print(f"⚠️ Navigation wait failed: {e}")
            return False


