#!/usr/bin/env python3
"""
🎯 LEARNING MVC SYSTEM MODULE
============================
Main Learning MVC System class.
Extracted from learning_mvc_system.py for better organization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

import time
from typing import Any, Dict, Optional

from playwright.sync_api import Page

from .analyzer import CuriousPageAnalyzer
from .collector import TelemetryCollector
from .telemetry import PageAnalysis


class LearningMVCSystem:
    """Main learning MVC system."""

    def __init__(self, page: Page):
        self.page = page
        self.telemetry = TelemetryCollector()
        self.analyzer = CuriousPageAnalyzer(page, self.telemetry)
        self.current_analysis: Optional[PageAnalysis] = None
        self.project_data = {}

    def initialize(self, project_data: Dict[str, Any] = None):
        """Initialize the learning system."""
        print("🧠 Learning MVC System Starting")
        print("=" * 50)
        if project_data:
            self.project_data = project_data
            print(f"📊 Project data loaded: {len(project_data)} fields")
        # Set up comprehensive event listeners
        self._setup_event_listeners()
        # Perform initial analysis
        self.analyze_current_page()
        # Take initial screenshot
        self._take_curious_screenshot("initial_analysis")

    def _setup_event_listeners(self):
        """Set up comprehensive event listeners."""
        print("🎧 Setting up comprehensive event listeners...")
        # Page events
        self.page.on("load", self._on_page_load)
        self.page.on("domcontentloaded", self._on_dom_loaded)
        self.page.on("networkidle", self._on_network_idle)
        # Console events
        self.page.on("console", self._on_console_message)
        # Error events
        self.page.on("pageerror", self._on_page_error)
        self.page.on("crash", self._on_page_crash)
        # Request/Response events
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)
        # Dialog events
        self.page.on("dialog", self._on_dialog)
        print("✅ Event listeners configured")

    def _on_page_load(self, page: Page):
        """Handle page load event."""
        self.telemetry.log_event("page_load", page, {"url": page.url})
        print(f"📄 Page loaded: {page.url}")
        self.analyze_current_page()

    def _on_dom_loaded(self, page: Page):
        """Handle DOM loaded event."""
        self.telemetry.log_event("dom_loaded", page, {"url": page.url})
        print("🌐 DOM content loaded")

    def _on_network_idle(self, page: Page):
        """Handle network idle event."""
        self.telemetry.log_event("network_idle", page, {"url": page.url})
        print("🔌 Network idle - page fully loaded")

    def _on_console_message(self, message):
        """Handle console message event."""
        self.telemetry.log_event(
            "console_message",
            self.page,
            {
                "type": message.type,
                "text": message.text,
                "location": str(message.location),
            },
        )

    def _on_page_error(self, error):
        """Handle page error event."""
        self.telemetry.log_event(
            "page_error",
            self.page,
            {"error": str(error)},
            success=False,
            error=str(error),
        )
        print(f"❌ Page error: {error}")

    def _on_page_crash(self, page: Page):
        """Handle page crash event."""
        self.telemetry.log_event(
            "page_crash",
            page,
            {"url": page.url},
            success=False,
            error="Page crashed",
        )
        print(f"💥 Page crashed: {page.url}")

    def _on_request(self, request):
        """Handle request event."""
        self.telemetry.log_event(
            "request",
            self.page,
            {
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
            },
        )

    def _on_response(self, response):
        """Handle response event."""
        self.telemetry.log_event(
            "response",
            self.page,
            {
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text,
            },
        )

    def _on_dialog(self, dialog):
        """Handle dialog event."""
        self.telemetry.log_event(
            "dialog",
            self.page,
            {
                "type": dialog.type,
                "message": dialog.message,
                "default_value": dialog.default_value,
            },
        )
        # Auto-dismiss dialogs
        dialog.dismiss()

    def analyze_current_page(self) -> PageAnalysis:
        """Analyze the current page."""
        print("\n🔍 Analyzing current page...")
        try:
            self.current_analysis = self.analyzer.analyze_page()
            return self.current_analysis
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            self.telemetry.log_event(
                "analysis_failed",
                self.page,
                {"error": str(e)},
                success=False,
                error=str(e),
            )
            raise

    def _take_curious_screenshot(self, name: str):
        """Take a screenshot with curiosity."""
        try:
            timestamp = int(time.time())
            filename = f"screenshot_{name}_{timestamp}.png"
            self.page.screenshot(path=filename)
            print(f"📸 Curious screenshot saved: {filename}")
            self.telemetry.log_event(
                "screenshot_taken",
                self.page,
                {"filename": filename, "name": name},
            )
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get learning summary."""
        return {
            "total_pages_analyzed": self.analyzer.learning_state.total_pages_analyzed,
            "successful_navigations": self.analyzer.learning_state.successful_navigations,
            "failed_navigations": self.analyzer.learning_state.failed_navigations,
            "discovered_patterns": len(self.analyzer.learning_state.discovered_patterns),
            "learned_selectors": len(self.analyzer.learning_state.learned_selectors),
            "page_type_patterns": len(self.analyzer.learning_state.page_type_patterns),
            "button_patterns": len(self.analyzer.learning_state.button_patterns),
            "form_patterns": len(self.analyzer.learning_state.form_patterns),
            "telemetry_summary": self.telemetry.get_summary(),
        }

    def save_learning_data(self, filename: str = None):
        """Save learning data to file."""
        if not filename:
            timestamp = int(time.time())
            filename = f"learning_data_{timestamp}.json"
        
        learning_data = {
            "learning_summary": self.get_learning_summary(),
            "learning_state": {
                "total_pages_analyzed": self.analyzer.learning_state.total_pages_analyzed,
                "successful_navigations": self.analyzer.learning_state.successful_navigations,
                "failed_navigations": self.analyzer.learning_state.failed_navigations,
                "discovered_patterns": self.analyzer.learning_state.discovered_patterns,
                "learned_selectors": self.analyzer.learning_state.learned_selectors,
                "page_type_patterns": self.analyzer.learning_state.page_type_patterns,
                "button_patterns": self.analyzer.learning_state.button_patterns,
                "form_patterns": self.analyzer.learning_state.form_patterns,
            },
            "current_analysis": self.current_analysis.__dict__ if self.current_analysis else None,
        }
        
        import json
        with open(filename, "w") as f:
            json.dump(learning_data, f, indent=2, default=str)
        print(f"💾 Learning data saved: {filename}")
        return filename


