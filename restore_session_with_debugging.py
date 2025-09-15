#!/usr/bin/env python3
"""
White Hat Session Restoration
============================

Restore Chrome session with full state including cookies, headers, and navigation.
This is OUR data, OUR session - we're just moving it to a debuggable environment.
"""

import subprocess
import json
import time
import os
import sqlite3
from pathlib import Path

def extract_session_state():
    """Extract complete session state from Chrome."""
    print("🕵️ Extracting Complete Session State")
    print("=" * 40)
    
    try:
        # Get current URL and title
        result = subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to get URL of active tab of front window'], 
                              capture_output=True, text=True)
        current_url = result.stdout.strip()
        
        result = subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to get title of active tab of front window'], 
                              capture_output=True, text=True)
        page_title = result.stdout.strip()
        
        # Extract cookies
        chrome_data_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome')
        cookies_db = os.path.join(chrome_data_dir, 'Default', 'Cookies')
        
        if os.path.exists(cookies_db):
            # Copy cookies database
            import shutil
            shutil.copy2(cookies_db, 'chrome_cookies.db')
            
            # Extract DevPost cookies
            conn = sqlite3.connect('chrome_cookies.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, 
                       creation_utc, last_access_utc, has_expires, is_persistent
                FROM cookies 
                WHERE host_key LIKE '%devpost%' OR host_key LIKE '%kiro%'
                ORDER BY creation_utc DESC
            ''')
            
            cookies = cursor.fetchall()
            conn.close()
            
            # Convert cookies to usable format
            cookie_list = []
            for cookie in cookies:
                name, value, host, path, expires, secure, httponly, created, accessed, has_expires, persistent = cookie
                cookie_list.append({
                    'name': name,
                    'value': value,
                    'domain': host,
                    'path': path,
                    'secure': bool(secure),
                    'httponly': bool(httponly)
                })
        else:
            cookie_list = []
        
        # Extract session info from URL
        url_parts = current_url.split('/')
        hackathon_id = None
        submission_id = None
        
        for i, part in enumerate(url_parts):
            if 'code-with-kiro-hackathon' in part:
                hackathon_id = part
            elif part.isdigit() and len(part) > 5:
                submission_id = part
        
        session_state = {
            'url': current_url,
            'title': page_title,
            'hackathon_id': hackathon_id,
            'submission_id': submission_id,
            'cookies': cookie_list,
            'timestamp': time.time(),
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Save complete session state
        with open('complete_session_state.json', 'w') as f:
            json.dump(session_state, f, indent=2)
        
        print(f"✅ Session state extracted:")
        print(f"   URL: {current_url}")
        print(f"   Title: {page_title}")
        print(f"   Cookies: {len(cookie_list)} DevPost/Kiro cookies")
        print(f"   Hackathon ID: {hackathon_id}")
        print(f"   Submission ID: {submission_id}")
        
        return session_state
        
    except Exception as e:
        print(f"❌ Failed to extract session state: {e}")
        return None

def close_chrome_safely():
    """Close Chrome safely."""
    print("🔄 Closing Chrome safely...")
    
    try:
        subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to quit'], 
                      capture_output=True, text=True)
        time.sleep(3)
        print("✅ Chrome closed")
        return True
    except Exception as e:
        print(f"❌ Failed to close Chrome: {e}")
        return False

def start_chrome_with_debugging():
    """Start Chrome with remote debugging enabled."""
    print("🚀 Starting Chrome with debugging...")
    
    try:
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        cmd = [
            chrome_path,
            "--remote-debugging-port=9222",
            "--user-data-dir=/tmp/chrome-debug-session",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-blink-features=AutomationControlled"
        ]
        
        # Start Chrome in background
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for Chrome to start
        time.sleep(5)
        
        # Test debugging connection
        import requests
        try:
            response = requests.get("http://localhost:9222/json/version", timeout=10)
            if response.status_code == 200:
                print("✅ Chrome started with debugging enabled")
                return True
        except:
            pass
        
        print("⚠️ Chrome started but debugging port not ready yet")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return False

def restore_session_with_playwright(session_state):
    """Restore session using Playwright with full state."""
    print("🔄 Restoring session with Playwright...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        
        # Get or create page
        pages = browser.pages
        if pages:
            page = pages[0]
        else:
            page = browser.new_page()
        
        # Set user agent
        page.set_extra_http_headers({
            'User-Agent': session_state['user_agent']
        })
        
        # Add cookies
        if session_state['cookies']:
            print(f"🍪 Adding {len(session_state['cookies'])} cookies...")
            for cookie in session_state['cookies']:
                try:
                    page.context.add_cookies([cookie])
                except Exception as e:
                    print(f"⚠️ Failed to add cookie {cookie['name']}: {e}")
        
        # Navigate to the saved URL
        print(f"🌐 Navigating to: {session_state['url']}")
        page.goto(session_state['url'], wait_until="networkidle")
        
        # Verify we're on the right page
        current_url = page.url
        current_title = page.title()
        
        print(f"✅ Session restored:")
        print(f"   Current URL: {current_url}")
        print(f"   Current Title: {current_title}")
        
        # Take screenshot to verify
        page.screenshot(path="restored_session.png")
        print("📸 Screenshot saved: restored_session.png")
        
        return page
        
    except Exception as e:
        print(f"❌ Failed to restore session: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to restore session with debugging."""
    print("🕵️ White Hat Session Restoration")
    print("=" * 40)
    print("This is OUR data, OUR session - we're just moving it to a debuggable environment")
    print()
    
    # Step 1: Extract complete session state
    session_state = extract_session_state()
    if not session_state:
        print("❌ Cannot proceed without session state")
        return
    
    # Step 2: Close Chrome safely
    if not close_chrome_safely():
        print("❌ Cannot proceed without closing Chrome")
        return
    
    # Step 3: Start Chrome with debugging
    if not start_chrome_with_debugging():
        print("❌ Failed to start Chrome with debugging")
        return
    
    # Step 4: Restore session with Playwright
    page = restore_session_with_playwright(session_state)
    if not page:
        print("❌ Failed to restore session")
        return
    
    print("\n🎉 Session successfully restored with debugging enabled!")
    print("🔗 You can now connect via CDP on port 9222")
    print("🕵️ All cookies, headers, and navigation state preserved")
    
    # Start interactive mode
    print("\n🎮 Interactive Mode Available")
    print("Commands: analyze, screenshot, quit")
    
    while True:
        try:
            command = input("🔧 Command: ").strip().lower()
            
            if command == "quit":
                break
            elif command == "analyze":
                # Analyze current page
                forms = page.query_selector_all("form")
                buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
                inputs = page.query_selector_all("input, textarea, select")
                
                print(f"📊 Current page analysis:")
                print(f"   Forms: {len(forms)}")
                print(f"   Buttons: {len(buttons)}")
                print(f"   Inputs: {len(inputs)}")
                print(f"   URL: {page.url}")
                print(f"   Title: {page.title()}")
                
            elif command == "screenshot":
                timestamp = int(time.time())
                filename = f"interactive_screenshot_{timestamp}.png"
                page.screenshot(path=filename)
                print(f"📸 Screenshot: {filename}")
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
