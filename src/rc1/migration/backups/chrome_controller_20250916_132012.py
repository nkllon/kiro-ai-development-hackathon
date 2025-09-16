#!/usr/bin/env python3
"""
Control Chrome using AppleScript without needing debugging port
"""

import subprocess
import json
import time
from datetime import datetime


class ChromeController:
    def __init__(self):
        self.applescript_commands = {
            "get_url": """
                tell application "Google Chrome"
                    return URL of active tab of front window
                end tell
            """,
            "get_title": """
                tell application "Google Chrome"
                    return title of active tab of front window
                end tell
            """,
            "navigate": """
                tell application "Google Chrome"
                    set URL of active tab of front window to "{}"
                end tell
            """,
            "click_element": """
                tell application "Google Chrome"
                    tell active tab of front window
                        execute javascript "document.querySelector('{}').click();"
                    end tell
                end tell
            """,
            "get_page_source": """
                tell application "Google Chrome"
                    tell active tab of front window
                        return execute javascript "document.documentElement.outerHTML"
                    end tell
                end tell
            """,
            "take_screenshot": """
                tell application "Google Chrome"
                    tell active tab of front window
                        execute javascript "html2canvas(document.body).then(canvas => canvas.toDataURL());"
                    end tell
                end tell
            """,
        }

    def execute_applescript(self, script):
        """Execute AppleScript command"""
        try:
            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"❌ AppleScript error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("❌ AppleScript timeout")
            return None
        except Exception as e:
            print(f"❌ AppleScript failed: {e}")
            return None

    def get_current_page_info(self):
        """Get current page URL and title"""
        print("🔍 GETTING CURRENT PAGE INFO...")

        url = self.execute_applescript(self.applescript_commands["get_url"])
        title = self.execute_applescript(self.applescript_commands["get_title"])

        if url and title:
            print(f"✅ Current page:")
            print(f"   URL: {url}")
            print(f"   Title: {title}")

            return {"url": url, "title": title, "timestamp": datetime.now().isoformat()}
        else:
            print("❌ Could not get page info")
            return None

    def navigate_to_url(self, url):
        """Navigate to a specific URL"""
        print(f"🌐 NAVIGATING TO: {url}")

        script = self.applescript_commands["navigate"].format(url)
        result = self.execute_applescript(script)

        if result is not None:
            print("✅ Navigation command sent")
            time.sleep(2)  # Wait for page to load
            return True
        else:
            print("❌ Navigation failed")
            return False

    def get_page_source(self):
        """Get the HTML source of the current page"""
        print("📄 GETTING PAGE SOURCE...")

        source = self.execute_applescript(self.applescript_commands["get_page_source"])

        if source:
            print(f"✅ Got page source ({len(source)} characters)")
            return source
        else:
            print("❌ Could not get page source")
            return None

    def click_element(self, selector):
        """Click an element using CSS selector"""
        print(f"🖱️ CLICKING ELEMENT: {selector}")

        script = self.applescript_commands["click_element"].format(selector)
        result = self.execute_applescript(script)

        if result is not None:
            print("✅ Click command sent")
            time.sleep(1)
            return True
        else:
            print("❌ Click failed")
            return False

    def analyze_current_page(self):
        """Perform comprehensive analysis of current page"""
        print("🔍 ANALYZING CURRENT PAGE...")

        page_info = self.get_current_page_info()
        if not page_info:
            return None

        # Get page source for analysis
        source = self.get_page_source()

        analysis = {
            "page_info": page_info,
            "source_length": len(source) if source else 0,
            "has_forms": "form" in source.lower() if source else False,
            "has_inputs": "input" in source.lower() if source else False,
            "has_buttons": "button" in source.lower() if source else False,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        # Save analysis
        analysis_file = (
            f"chrome_page_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)

        print(f"📊 ANALYSIS COMPLETE:")
        print(f"   Page type: {self._classify_page_type(page_info['url'])}")
        print(f"   Has forms: {analysis['has_forms']}")
        print(f"   Has inputs: {analysis['has_inputs']}")
        print(f"   Has buttons: {analysis['has_buttons']}")
        print(f"   Analysis saved: {analysis_file}")

        return analysis

    def _classify_page_type(self, url):
        """Classify the type of page based on URL"""
        if "chrome://" in url:
            return "Chrome Internal"
        elif "devpost.com" in url:
            return "DevPost"
        elif "github.com" in url:
            return "GitHub"
        elif url == "chrome://newtab/":
            return "New Tab"
        elif url.startswith("http"):
            return "Web Page"
        else:
            return "Unknown"


def main():
    controller = ChromeController()

    print("🚀 CHROME CONTROLLER (No Debugging Port Required)")
    print("=" * 60)

    # Analyze current page
    analysis = controller.analyze_current_page()

    if analysis:
        print("\n✅ SUCCESS! I can control your Chrome without the debugging port!")
        print("   Ready for further instructions:")
        print("   - Navigate to specific URLs")
        print("   - Click elements")
        print("   - Analyze page content")
        print("   - Take screenshots")

        # Offer to navigate somewhere
        current_url = analysis["page_info"]["url"]
        if current_url == "chrome://newtab/":
            print("\n🎯 You're on the new tab page. Want me to navigate somewhere?")
            print("   Try: controller.navigate_to_url('https://devpost.com')")
    else:
        print("\n❌ Could not analyze current page")


if __name__ == "__main__":
    main()
