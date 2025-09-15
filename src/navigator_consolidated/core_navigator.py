#!/usr/bin/env python3
"""
Core Navigator - Main navigation logic
=====================================

Extracted from smart_devpost_navigator_v2.py for RDI compliance.
Contains the main SmartDevPostNavigatorV2 class and core functionality.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from playwright.sync_api import BrowserContext, Page, sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .event_handler import EventHandler
from .form_processor import FormProcessor
from .step_detector import StepDetector
from .interactive_mode import InteractiveMode


class SmartDevPostNavigatorV2:
    """Intelligent DevPost navigation system with event listeners."""

    def __init__(self):
        self.browser = None
        self.page = None
        self.current_step = None
        self.submission_flow = []
        self.project_data = {}
        self.navigation_events = []
        self.form_events = []
        self.success_callbacks = []
        self.error_callbacks = []
        
        # Initialize components
        self.event_handler = EventHandler(self)
        self.form_processor = FormProcessor(self)
        self.step_detector = StepDetector(self)
        self.interactive_mode = InteractiveMode(self)

    def start_navigation(self, base_url: str, project_data: Dict[str, Any] = None):
        """Start intelligent navigation through DevPost submission."""
        print("🧠 Smart DevPost Navigator V2 Starting")
        print("=" * 50)

        try:
            # Start browser
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch_persistent_context(
                user_data_dir="/tmp/devpost-smart-browser-v2",
                headless=False,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )

            self.page = self.browser.new_page()

            # Set up event listeners
            self.event_handler.setup_event_listeners()

            # Set project data
            if project_data:
                self.project_data = project_data
                print(f"📊 Project data loaded: {len(project_data)} fields")

            # Navigate to base URL
            print(f"🌐 Navigating to: {base_url}")
            self.page.goto(base_url, wait_until="networkidle")

            # Wait for initial load and detect step
            self.wait_for_page_ready()
            self.step_detector.detect_current_step()

            # Start automated flow
            self.run_automated_flow()

        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.browser:
                self.browser.close()

    def wait_for_page_ready(self, timeout: int = 10000):
        """Wait for page to be fully ready with multiple checks."""
        print("⏳ Waiting for page to be ready...")

        try:
            # Wait for basic load
            self.page.wait_for_load_state("load", timeout=timeout)

            # Wait for DOM to be ready
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

            # Wait for network to be idle
            self.page.wait_for_load_state("networkidle", timeout=timeout)

            # Additional check for DevPost-specific elements
            self.page.wait_for_selector("body", timeout=5000)

            # Check if we're on a DevPost page
            if "devpost.com" in self.page.url:
                print("✅ DevPost page loaded successfully")
                return True
            else:
                print("⚠️ Not on DevPost page")
                return False

        except Exception as e:
            print(f"⚠️ Page ready check failed: {e}")
            return False

    def run_automated_flow(self):
        """Run automated submission flow with better error handling."""
        print("\n🤖 Starting Automated Flow")
        print("=" * 30)

        try:
            # Process current step
            success = self.process_current_step()
            if not success:
                print("⚠️ Current step processing failed, but continuing...")

            # Look for next step
            next_step = self.find_next_step()
            if next_step:
                print(f"🔄 Moving to next step: {next_step['text']}")
                success = self.navigate_to_step(next_step)
                if success:
                    print("✅ Navigation successful")
                    # Process the new step
                    self.process_current_step()
                else:
                    print("❌ Navigation failed")
            else:
                print("ℹ️ No next step found - may be at end of flow")

            print("\n✅ Automated flow complete!")
            print("🎮 Interactive mode available")

            # Start interactive mode
            self.interactive_mode.start()

        except Exception as e:
            print(f"❌ Automated flow failed: {e}")
            import traceback
            traceback.print_exc()

    def process_current_step(self) -> bool:
        """Process current step (fill forms, take screenshots, etc.)."""
        print(f"\n📝 Processing step: {self.current_step}")

        try:
            # Take screenshot
            self.take_step_screenshot()

            # Extract form data
            form_data = self.form_processor.extract_current_form()
            if form_data:
                self.form_processor.save_form_data(form_data)

            # Fill form if we have project data
            if self.project_data and form_data:
                filled_count = self.form_processor.fill_current_form(form_data)
                return filled_count > 0

            return True

        except Exception as e:
            print(f"❌ Step processing failed: {e}")
            return False

    def find_next_step(self) -> Optional[Dict]:
        """Find next step in submission flow with better detection."""
        return self.step_detector.find_next_step()

    def navigate_to_step(self, step: Dict) -> bool:
        """Navigate to specific step with proper error handling."""
        return self.step_detector.navigate_to_step(step)

    def take_step_screenshot(self):
        """Take screenshot of current step."""
        try:
            timestamp = int(time.time())
            filename = f"devpost_{self.current_step}_{timestamp}.png"
            self.page.screenshot(path=filename)
            print(f"📸 Screenshot: {filename}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")


def main():
    """Main function."""
    print("🧠 Smart DevPost Navigator V2")
    print("=" * 40)

    # Load project data
    try:
        with open("sample_project_data.json", "r") as f:
            project_data = json.load(f)
        print(f"📊 Loaded project data: {len(project_data)} fields")
    except Exception as e:
        print(f"⚠️ Could not load project data: {e}")
        project_data = {}

    # Start navigation
    base_url = "https://devpost.com/submit-to/25444-code-with-kiro-hackathon/manage/submissions/784734-untitled/project-overview"

    navigator = SmartDevPostNavigatorV2()
    navigator.start_navigation(base_url, project_data)


if __name__ == "__main__":
    main()
