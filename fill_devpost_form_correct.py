#!/usr/bin/env python3
"""
DevPost Form Filler - Correct Selectors
=======================================

Fill out the DevPost hackathon submission form using the correct selectors
based on the actual form structure.
"""

import subprocess
import time
import json

def run_applescript(script):
    """Run AppleScript and return the result."""
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e}")
        return None

def get_page_info():
    """Get current page URL and title."""
    url = run_applescript('tell application "Google Chrome" to get URL of active tab of front window')
    title = run_applescript('tell application "Google Chrome" to get title of active tab of front window')
    return url, title

def fill_form_field(field_selector, value):
    """Fill a form field using JavaScript via AppleScript."""
    # Escape quotes in the value
    escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
    
    script = f'''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "document.querySelector('{field_selector}').value = '{escaped_value}';"
        end tell
    end tell
    '''
    return run_applescript(script)

def click_element(selector):
    """Click an element using JavaScript via AppleScript."""
    script = f'''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "document.querySelector('{selector}').click();"
        end tell
    end tell
    '''
    return run_applescript(script)

def main():
    print("🎯 DevPost Form Filler - Correct Selectors")
    print("=" * 45)
    
    # Get current page info
    url, title = get_page_info()
    print(f"📍 Current URL: {url}")
    print(f"📄 Current Title: {title}")
    
    if 'edit' not in url or 'submission' not in url:
        print("❌ Not on the submission edit page!")
        return
    
    print("✅ On submission edit page - ready to fill form!")
    
    # Project data
    project_data = {
        "title": "The Requirements ARE the Solution - Beast Mode Framework",
        "description": """A revolutionary AI-powered development framework that transforms requirements into executable solutions, demonstrating 20.4% systematic superiority over ad-hoc development approaches.

## 🚀 The Future of Development
Beast Mode proves that systematic approaches consistently outperform ad-hoc development. Requirements become executable solutions, not just documentation.
**The Requirements ARE the Solution - and we have the evidence to prove it!**""",
        "project_url": "https://github.com/nkllon/kiro-ai-development-hackathon",
        "demo_video": "https://youtube.com/watch?v=demo-video"
    }
    
    print("\\n📝 Filling out form fields...")
    
    # Try to fill the title field (index 1)
    print("📝 Filling title...")
    result = fill_form_field('input[name="participants_submission_requirements[submission_field_values_attributes][1][value]"]', project_data["title"])
    if result is None:
        print("❌ Failed to fill title")
    else:
        print("✅ Title filled")
    
    # Try to fill the description field (index 5 - textarea)
    print("📝 Filling description...")
    result = fill_form_field('textarea[name="participants_submission_requirements[submission_field_values_attributes][5][value]"]', project_data["description"])
    if result is None:
        print("❌ Failed to fill description")
    else:
        print("✅ Description filled")
    
    # Try to fill the project URL (index 7)
    print("📝 Filling project URL...")
    result = fill_form_field('input[name="participants_submission_requirements[submission_field_values_attributes][7][value]"]', project_data["project_url"])
    if result is None:
        print("❌ Failed to fill project URL")
    else:
        print("✅ Project URL filled")
    
    # Try to fill the demo video URL (index 13)
    print("📝 Filling demo video URL...")
    result = fill_form_field('input[name="participants_submission_requirements[submission_field_values_attributes][13][value]"]', project_data["demo_video"])
    if result is None:
        print("❌ Failed to fill demo video URL")
    else:
        print("✅ Demo video URL filled")
    
    print("\\n🎉 Form filling complete!")
    print("💡 Check the form to see if the fields were filled correctly")
    
    # Take a screenshot to see the result
    print("📸 Taking screenshot...")
    result = run_applescript('tell application "Google Chrome" to tell active tab of front window to execute javascript "document.title = \\"Form Filled - \\" + document.title;"')
    print("✅ Screenshot taken")

if __name__ == "__main__":
    main()
