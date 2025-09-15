#!/usr/bin/env python3
"""
DevPost Browser Daemon
======================

Persistent browser daemon that stays alive and allows multiple operations
without restarting. Production-ready for operations scenarios.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Persistent browser session for DevPost operations
"""

import sys
import json
import time
import signal
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import subprocess
import os
import atexit

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class DevPostBrowserDaemon:
    """Persistent browser daemon for DevPost operations."""
    
    def __init__(self, port=9222, headless=False):
        self.port = port
        self.headless = headless
        self.browser_process = None
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.running = False
        self.lock = threading.Lock()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)
    
    def start_daemon(self):
        """Start the browser daemon."""
        print("🚀 Starting DevPost Browser Daemon")
        print("=" * 50)
        
        try:
            # Start Playwright
            self.playwright = sync_playwright().start()
            
            # Launch browser with remote debugging
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    f'--remote-debugging-port={self.port}',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--user-data-dir=/tmp/devpost-browser-data'
                ]
            )
            
            # Create context
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            # Create initial page
            self.page = self.context.new_page()
            
            self.running = True
            
            print("✅ Browser daemon started successfully!")
            print(f"🌐 Remote debugging: http://localhost:{self.port}")
            print(f"🔗 Browser PID: {self.browser.process.pid if self.browser.process else 'Unknown'}")
            print("💡 Daemon is running in background...")
            print("🎮 Use the control commands to interact with the browser")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start daemon: {e}")
            self.cleanup()
            return False
    
    def connect_to_daemon(self):
        """Connect to existing daemon."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{self.port}")
            
            # Get existing context or create new one
            if self.browser.contexts:
                self.context = self.browser.contexts[0]
            else:
                self.context = self.browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080}
                )
            
            # Get existing page or create new one
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()
            
            self.running = True
            print("✅ Connected to existing daemon!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to daemon: {e}")
            return False
    
    def navigate_to(self, url):
        """Navigate to URL."""
        with self.lock:
            try:
                print(f"🌐 Navigating to: {url}")
                self.page.goto(url, wait_until="networkidle")
                print(f"📄 Title: {self.page.title()}")
                print(f"🔗 URL: {self.page.url}")
                return True
            except Exception as e:
                print(f"❌ Navigation failed: {e}")
                return False
    
    def extract_form_data(self, form_id=None):
        """Extract form data from current page."""
        with self.lock:
            try:
                print("📊 Extracting form data...")
                
                # Find form
                if form_id:
                    form = self.page.query_selector(f"#{form_id}")
                else:
                    # Look for main submission form
                    form = self.page.query_selector("#project-overview-form")
                    if not form:
                        forms = self.page.query_selector_all("form")
                        if forms:
                            form = forms[-1]  # Get last form (usually main one)
                
                if not form:
                    print("❌ No form found!")
                    return None
                
                print(f"✅ Found form: {form.get_attribute('id') or 'unnamed'}")
                
                # Extract fields
                fields = form.query_selector_all("input, textarea, select")
                print(f"📝 Found {len(fields)} fields")
                
                form_data = {
                    "form_id": form.get_attribute("id"),
                    "form_class": form.get_attribute("class"),
                    "form_action": form.get_attribute("action"),
                    "page_title": self.page.title(),
                    "page_url": self.page.url,
                    "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "fields": []
                }
                
                for i, field in enumerate(fields, 1):
                    field_type = field.get_attribute("type") or field.evaluate("el => el.tagName").lower()
                    field_name = field.get_attribute("name")
                    field_id = field.get_attribute("id")
                    field_value = field.get_attribute("value") or ""
                    field_placeholder = field.get_attribute("placeholder") or ""
                    field_required = field.get_attribute("required") is not None
                    field_class = field.get_attribute("class")
                    
                    # Get label
                    field_label = "Unlabeled"
                    if field_id:
                        label_elem = self.page.query_selector(f"label[for='{field_id}']")
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
                        "class": field_class
                    }
                    
                    form_data["fields"].append(field_info)
                
                return form_data
                
            except Exception as e:
                print(f"❌ Extraction failed: {e}")
                return None
    
    def take_screenshot(self, filename="devpost_screenshot.png"):
        """Take screenshot."""
        with self.lock:
            try:
                self.page.screenshot(path=filename)
                print(f"📸 Screenshot saved: {filename}")
                return True
            except Exception as e:
                print(f"❌ Screenshot failed: {e}")
                return False
    
    def save_page_html(self, filename="devpost_page.html"):
        """Save page HTML."""
        with self.lock:
            try:
                html = self.page.content()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"💾 HTML saved: {filename}")
                return True
            except Exception as e:
                print(f"❌ HTML save failed: {e}")
                return False
    
    def get_page_info(self):
        """Get current page information."""
        with self.lock:
            try:
                return {
                    "title": self.page.title(),
                    "url": self.page.url,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            except Exception as e:
                print(f"❌ Failed to get page info: {e}")
                return None
    
    def is_running(self):
        """Check if daemon is running."""
        return self.running and self.browser and not self.browser.is_connected() == False
    
    def cleanup(self):
        """Cleanup resources."""
        print("🧹 Cleaning up browser daemon...")
        self.running = False
        
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        
        print("✅ Cleanup complete")

class DevPostOperations:
    """Operations interface for DevPost daemon."""
    
    def __init__(self, daemon):
        self.daemon = daemon
    
    def extract_submission_form(self, url, output_file=None):
        """Extract submission form data."""
        print("🎯 DevPost Submission Form Extraction")
        print("=" * 50)
        
        # Navigate to URL
        if not self.daemon.navigate_to(url):
            return False
        
        # Extract form data
        form_data = self.daemon.extract_form_data()
        if not form_data:
            return False
        
        # Save data
        if not output_file:
            output_file = f"devpost_form_{int(time.time())}.json"
        
        with open(output_file, 'w') as f:
            json.dump(form_data, f, indent=2)
        
        print(f"💾 Form data saved: {output_file}")
        
        # Display summary
        print(f"\n📊 Extraction Summary:")
        print(f"   Form ID: {form_data.get('form_id', 'Unknown')}")
        print(f"   Fields: {len(form_data.get('fields', []))}")
        print(f"   Page: {form_data.get('page_title', 'Unknown')}")
        
        # Show fields
        print(f"\n📋 Form Fields:")
        for field in form_data.get('fields', []):
            print(f"   {field['index']:2d}. {field['label']} ({field['tag']})")
            print(f"       Name: {field['name']}")
            print(f"       Value: {field['value'][:50]}{'...' if len(field['value']) > 50 else ''}")
            print(f"       Required: {field['required']}")
            print()
        
        return True
    
    def monitor_page(self, url, interval=30):
        """Monitor page for changes."""
        print(f"👁️ Monitoring page: {url}")
        print(f"⏱️ Check interval: {interval} seconds")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                if not self.daemon.navigate_to(url):
                    print("❌ Navigation failed, retrying...")
                    time.sleep(5)
                    continue
                
                page_info = self.daemon.get_page_info()
                if page_info:
                    print(f"📄 {page_info['timestamp']} - {page_info['title']}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

def main():
    """Main function."""
    print("🎯 DevPost Browser Daemon")
    print("=" * 40)
    
    daemon = DevPostBrowserDaemon(port=9222, headless=False)
    
    # Try to connect to existing daemon first
    if daemon.connect_to_daemon():
        print("✅ Connected to existing daemon")
    else:
        print("🚀 Starting new daemon...")
        if not daemon.start_daemon():
            print("❌ Failed to start daemon")
            return
    
    # Create operations interface
    ops = DevPostOperations(daemon)
    
    # Interactive mode
    print("\n🎮 Interactive Mode - Available Commands:")
    print("=" * 50)
    print("extract <url> [output] - Extract form data")
    print("navigate <url>         - Navigate to URL")
    print("screenshot [file]      - Take screenshot")
    print("html [file]            - Save page HTML")
    print("info                   - Show page info")
    print("monitor <url> [sec]    - Monitor page")
    print("status                 - Show daemon status")
    print("quit                   - Exit (daemon stays running)")
    print()
    
    while True:
        try:
            command = input("🔧 Command: ").strip()
            
            if command == "quit":
                print("👋 Exiting (daemon continues running)")
                break
            elif command.startswith("extract "):
                parts = command.split(" ", 2)
                url = parts[1]
                output = parts[2] if len(parts) > 2 else None
                ops.extract_submission_form(url, output)
            elif command.startswith("navigate "):
                url = command.split(" ", 1)[1]
                daemon.navigate_to(url)
            elif command.startswith("screenshot"):
                parts = command.split(" ", 1)
                filename = parts[1] if len(parts) > 1 else None
                daemon.take_screenshot(filename)
            elif command.startswith("html"):
                parts = command.split(" ", 1)
                filename = parts[1] if len(parts) > 1 else None
                daemon.save_page_html(filename)
            elif command == "info":
                info = daemon.get_page_info()
                if info:
                    print(f"📄 Title: {info['title']}")
                    print(f"🔗 URL: {info['url']}")
                    print(f"⏰ Time: {info['timestamp']}")
            elif command.startswith("monitor "):
                parts = command.split(" ")
                url = parts[1]
                interval = int(parts[2]) if len(parts) > 2 else 30
                ops.monitor_page(url, interval)
            elif command == "status":
                status = "Running" if daemon.is_running() else "Stopped"
                print(f"🟢 Daemon Status: {status}")
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            print("\n👋 Exiting (daemon continues running)")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()







