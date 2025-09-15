#!/usr/bin/env python3
"""
Browser Session Manager
=======================

Manages browser instances, connections, and low-level browser operations.
Separate from site navigation logic.
"""

import requests
import json
import time
import subprocess
import os
from typing import Dict, List, Any, Optional, Tuple
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class BrowserInstance:
    """Represents a browser instance with connection details"""

    def __init__(
        self, port: int, browser_type: str = "chrome", has_extensions: bool = False
    ):
        self.port = port
        self.browser_type = browser_type
        self.has_extensions = has_extensions
        self.tabs: List[Dict[str, Any]] = []
        self.connection_status = "unknown"
        self.last_checked = None


class BrowserSessionManager:
    """Manages browser instances and connections"""

    def __init__(self) -> None:
        self.active_browsers: Dict[int, BrowserInstance] = {}
        self.playwright = None
        self.current_connection: Optional[Tuple[Browser, BrowserContext]] = None
        self.debug_ports = [9222, 9223, 9224, 9225, 9226]

    def start_playwright(self):
        """Initialize Playwright"""
        if not self.playwright:
            self.playwright = sync_playwright().start()

    def discover_browsers(self) -> List[BrowserInstance]:
        """Discover all browser instances with debugging enabled"""
        browsers = []

        for port in self.debug_ports:
            try:
                response = requests.get(f"http://localhost:{port}/json", timeout=2)
                if response.status_code == 200:
                    tabs = response.json()
                    if tabs:
                        # Determine browser type and capabilities
                        browser_type = "chrome"  # Default assumption
                        has_extensions = len(tabs) > 0 and any(
                            tab.get("url", "").startswith("chrome-extension://")
                            for tab in tabs
                        )

                        browser = BrowserInstance(
                            port=port,
                            browser_type=browser_type,
                            has_extensions=has_extensions,
                        )
                        browser.tabs = tabs
                        browser.connection_status = "available"
                        browser.last_checked = time.time()

                        browsers.append(browser)
                        self.active_browsers[port] = browser
            except:
                continue

        return browsers

    def start_chrome_with_extensions(
        self, port: int = 9222
    ) -> Optional[BrowserInstance]:
        """Start Chrome with extensions enabled"""
        print(f"🔧 Starting Chrome with extensions on port {port}...")

        # Chrome paths
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]

        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break

        if not chrome_path:
            print("❌ Chrome not found")
            return None

        # Kill any existing instances
        subprocess.run(
            ["pkill", "-f", f"remote-debugging-port={port}"],
            capture_output=True,
            text=True,
        )

        # Start Chrome
        cmd = [
            chrome_path,
            f"--remote-debugging-port={port}",
            "--user-data-dir=$HOME/Library/Application Support/Google/Chrome",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        try:
            subprocess.Popen(cmd)
            time.sleep(3)  # Wait for startup

            # Verify it started
            response = requests.get(f"http://localhost:{port}/json", timeout=5)
            if response.status_code == 200:
                tabs = response.json()
                browser = BrowserInstance(
                    port=port,
                    browser_type="chrome",
                    has_extensions=True,  # Using user's Chrome profile
                )
                browser.tabs = tabs
                browser.connection_status = "available"
                browser.last_checked = time.time()

                self.active_browsers[port] = browser
                print(f"✅ Chrome started with extensions on port {port}")
                return browser
        except Exception as e:
            print(f"❌ Failed to start Chrome: {e}")

        return None

    def connect_to_browser(
        self, browser: BrowserInstance
    ) -> Optional[Tuple[Browser, BrowserContext]]:
        """Connect Playwright to a browser instance"""
        if not self.playwright:
            self.start_playwright()

        try:
            print(f"🔗 Connecting to {browser.browser_type} on port {browser.port}...")

            if browser.has_extensions:
                print("🔐 Extensions enabled - 1Password should be available")

            # Connect to existing browser
            playwright_browser = self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{browser.port}"
            )

            # Get or create context
            contexts = playwright_browser.contexts
            if contexts:
                context = contexts[0]
                print(f"📊 Using existing context with {len(context.pages)} pages")
            else:
                context = playwright_browser.new_context()
                print("🆕 Created new browser context")

            self.current_connection = (playwright_browser, context)
            browser.connection_status = "connected"

            return self.current_connection

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            browser.connection_status = "failed"
            return None

    def get_or_create_page(self, url: str = None) -> Optional[Page]:
        """Get existing page or create new one"""
        if not self.current_connection:
            return None

        browser, context = self.current_connection
        pages = context.pages

        if pages:
            page = pages[0]
            print(f"📄 Using existing page: {page.title()} - {page.url}")
        else:
            page = context.new_page()
            print("🆕 Created new page")

        if url:
            print(f"🌐 Navigating to: {url}")
            page.goto(url)

        return page

    def list_tabs(self, browser: BrowserInstance) -> List[Dict[str, Any]]:
        """List all tabs in a browser instance"""
        try:
            response = requests.get(f"http://localhost:{browser.port}/json")
            if response.status_code == 200:
                tabs = response.json()
                browser.tabs = tabs
                browser.last_checked = time.time()
                return tabs
        except Exception as e:
            print(f"❌ Failed to list tabs: {e}")

        return []

    def find_tabs_by_domain(
        self, browser: BrowserInstance, domain: str
    ) -> List[Dict[str, Any]]:
        """Find tabs matching a specific domain"""
        tabs = self.list_tabs(browser)
        return [tab for tab in tabs if domain in tab.get("url", "")]

    def get_browser_capabilities(self, browser: BrowserInstance) -> Dict[str, Any]:
        """Get detailed browser capabilities and status"""
        return {
            "port": browser.port,
            "browser_type": browser.browser_type,
            "has_extensions": browser.has_extensions,
            "connection_status": browser.connection_status,
            "tab_count": len(browser.tabs),
            "last_checked": browser.last_checked,
            "extensions_detected": any(
                tab.get("url", "").startswith("chrome-extension://")
                for tab in browser.tabs
            ),
        }

    def cleanup(self):
        """Clean up resources"""
        if self.current_connection:
            browser, context = self.current_connection
            try:
                browser.close()
            except:
                pass

        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass


def create_browser_manager() -> BrowserSessionManager:
    """Create a new browser session manager"""
    return BrowserSessionManager()


if __name__ == "__main__":
    # Test the browser manager
    manager = create_browser_manager()

    print("🔍 Discovering browsers...")
    browsers = manager.discover_browsers()

    if browsers:
        print(f"✅ Found {len(browsers)} browser instances:")
        for browser in browsers:
            caps = manager.get_browser_capabilities(browser)
            print(
                f"   Port {browser.port}: {caps['browser_type']} "
                f"({'with extensions' if caps['has_extensions'] else 'no extensions'}) "
                f"- {caps['tab_count']} tabs"
            )
    else:
        print("❌ No browsers found")
        print("🔧 Starting Chrome with extensions...")
        browser = manager.start_chrome_with_extensions()
        if browser:
            print("✅ Chrome started successfully")

    manager.cleanup()
