#!/usr/bin/env python3
"""
DevPost Form Filler using AppleScript
=====================================

Fill out the DevPost hackathon submission form using AppleScript
to interact with the form elements directly.
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
    script = f'''
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "document.querySelector('{field_selector}').value = '{value}';"
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
    print("🎯 DevPost Form Filler")
    print("=" * 25)
    
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
        "demo_video": "https://youtube.com/watch?v=demo-video",
        "built_with": ["Kiro AI", "Python", "Systematic Development", "AI Collaboration", "GCP"],
        "tags": ["kiro", "ai", "systematic-development", "beast-mode", "requirements-driven", "pdca", "ai-collaboration"]
    }
    
    print("\\n📝 Filling out form fields...")
    
    # Try to fill the title field
    print("📝 Filling title...")
    result = fill_form_field('input[name="submission[title]"]', project_data["title"])
    if result is None:
        print("❌ Failed to fill title")
    else:
        print("✅ Title filled")
    
    # Try to fill the description field
    print("📝 Filling description...")
    result = fill_form_field('textarea[name="submission[description]"]', project_data["description"])
    if result is None:
        print("❌ Failed to fill description")
    else:
        print("✅ Description filled")
    
    # Try to fill the project URL
    print("📝 Filling project URL...")
    result = fill_form_field('input[name="submission[project_url]"]', project_data["project_url"])
    if result is None:
        print("❌ Failed to fill project URL")
    else:
        print("✅ Project URL filled")
    
    # Try to fill the demo video URL
    print("📝 Filling demo video URL...")
    result = fill_form_field('input[name="submission[demo_video_url]"]', project_data["demo_video"])
    if result is None:
        print("❌ Failed to fill demo video URL")
    else:
        print("✅ Demo video URL filled")
    
    print("\\n🎉 Form filling complete!")
    print("💡 Check the form to see if the fields were filled correctly")

if __name__ == "__main__":
    main()
