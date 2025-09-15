#!/usr/bin/env python3
"""
Event Handler - Page event management
====================================

Extracted from smart_devpost_navigator_v2.py for RDI compliance.
Handles all page events, console messages, and navigation events.
"""

import time
from typing import Any, Dict, List


class EventHandler:
    """Handles all page events and navigation tracking."""

    def __init__(self, navigator):
        self.navigator = navigator

    def setup_event_listeners(self):
        """Set up comprehensive event listeners for page events."""
        print("🎧 Setting up event listeners...")

        # Navigation events
        self.navigator.page.on("load", self.on_page_load)
        self.navigator.page.on("domcontentloaded", self.on_dom_loaded)
        self.navigator.page.on("networkidle", self.on_network_idle)

        # Form events
        self.navigator.page.on("console", self.on_console_message)

        # Error events
        self.navigator.page.on("pageerror", self.on_page_error)
        self.navigator.page.on("crash", self.on_page_crash)

        # Request/Response events for debugging
        self.navigator.page.on("request", self.on_request)
        self.navigator.page.on("response", self.on_response)

        print("✅ Event listeners configured")

    def on_page_load(self, page):
        """Handle page load event."""
        print(f"📄 Page loaded: {page.url}")
        self.navigator.navigation_events.append(
            {"type": "load", "url": page.url, "timestamp": time.time()}
        )

    def on_dom_loaded(self, page):
        """Handle DOM content loaded event."""
        print(f"🌐 DOM loaded: {page.url}")
        self.navigator.navigation_events.append(
            {"type": "dom_loaded", "url": page.url, "timestamp": time.time()}
        )

    def on_network_idle(self, page):
        """Handle network idle event."""
        print(f"🔌 Network idle: {page.url}")
        self.navigator.navigation_events.append(
            {"type": "network_idle", "url": page.url, "timestamp": time.time()}
        )

    def on_console_message(self, msg):
        """Handle console messages."""
        if msg.type in ["error", "warning"]:
            print(f"⚠️ Console {msg.type}: {msg.text}")
        elif "form" in msg.text.lower() or "submit" in msg.text.lower():
            print(f"📝 Form message: {msg.text}")

    def on_page_error(self, error):
        """Handle page errors."""
        print(f"❌ Page error: {error}")

    def on_page_crash(self, error):
        """Handle page crashes."""
        print(f"💥 Page crash: {error}")

    def on_request(self, request):
        """Handle outgoing requests."""
        if "devpost.com" in request.url and request.method in ["POST", "PUT", "PATCH"]:
            print(f"📤 Form submission: {request.method} {request.url}")

    def on_response(self, response):
        """Handle responses."""
        if "devpost.com" in response.url and response.status in [200, 201, 302, 303]:
            print(f"📥 Response: {response.status} {response.url}")
