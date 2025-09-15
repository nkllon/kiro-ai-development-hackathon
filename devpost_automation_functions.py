#!/usr/bin/env python3
"""
DevPost Automation Functions - Broken down into tiny, testable steps
Like debugging Oracle stored procedures - one word at a time
"""

import subprocess
import time


def execute_applescript(script):
    """Execute AppleScript and return result"""
    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e.stderr}")
        return None


def check_chrome_focus():
    """Check if Chrome is the focused application"""
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = execute_applescript(script)
    print(f"Current focus: {result}")
    return result == "Google Chrome"


def focus_chrome():
    """Focus Chrome application"""
    script = 'tell application "Google Chrome" to activate'
    result = execute_applescript(script)
    time.sleep(1)  # Give it time to focus
    return check_chrome_focus()


def get_current_url():
    """Get current URL from Chrome"""
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.location.href"'
    result = execute_applescript(script)
    print(f"Current URL: {result}")
    return result


def get_page_title():
    """Get current page title"""
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.title"'
    result = execute_applescript(script)
    print(f"Page title: {result}")
    return result


def navigate_to_url(url):
    """Navigate to specific URL"""
    script = f'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.location.href = \\"{url}\\"; \\"Navigated\\";"'
    result = execute_applescript(script)
    time.sleep(2)  # Wait for page to load
    return result


def find_text_on_page(text):
    """Search for text on current page"""
    script = f'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.find(\\"{text}\\", false, false, true, false, true, false);"'
    result = execute_applescript(script)
    print(f"Found '{text}': {result}")
    return result == "true"


def click_selected_text():
    """Click on currently selected text"""
    script = '''tell application "Google Chrome" to tell active tab of front window to execute javascript "
        var selection = window.getSelection();
        if(selection.rangeCount > 0) {
            var range = selection.getRangeAt(0);
            var element = range.commonAncestorContainer;
            if(element.nodeType === 3) { element = element.parentNode; }
            element.click();
            console.log('Clicked on selected text');
        }
    "'''
    result = execute_applescript(script)
    return result


def get_focused_element_info():
    """Get information about currently focused element"""
    script = '''tell application "Google Chrome" to tell active tab of front window to execute javascript "
        var focusedElement = document.activeElement;
        var info = 'Tag: ' + focusedElement.tagName + ', Type: ' + focusedElement.type + ', Name: ' + focusedElement.name;
        console.log(info);
        info;
    "'''
    result = execute_applescript(script)
    print(f"Focused element: {result}")
    return result


def hit_tab():
    """Hit Tab key"""
    script = 'tell application "System Events" to key code 48'
    result = execute_applescript(script)
    time.sleep(0.5)  # Small delay
    return result


def type_text(text):
    """Type text into focused field"""
    script = f'tell application "System Events" to keystroke "{text}"'
    result = execute_applescript(script)
    return result


def test_step_1():
    """Test: Check Chrome focus"""
    print("=== Test Step 1: Check Chrome Focus ===")
    if not check_chrome_focus():
        print("Chrome not focused, focusing...")
        if not focus_chrome():
            print("❌ Failed to focus Chrome")
            return False
    print("✅ Chrome is focused")
    return True


def test_step_2():
    """Test: Get current page info"""
    print("=== Test Step 2: Get Page Info ===")
    url = get_current_url()
    title = get_page_title()
    if url and title:
        print("✅ Got page info")
        return True
    else:
        print("❌ Failed to get page info")
        return False


def test_step_3():
    """Test: Navigate to hackathon page"""
    print("=== Test Step 3: Navigate to Hackathon ===")
    result = navigate_to_url("https://devpost.com/kiro-ai-development-hackathon")
    if result:
        print("✅ Navigated to hackathon page")
        return True
    else:
        print("❌ Failed to navigate")
        return False


def test_step_4():
    """Test: Find 'My projects' text"""
    print("=== Test Step 4: Find My Projects ===")
    if find_text_on_page("My projects"):
        print("✅ Found 'My projects' text")
        return True
    else:
        print("❌ 'My projects' not found")
        return False


def test_step_5():
    """Test: Click on My projects"""
    print("=== Test Step 5: Click My Projects ===")
    if click_selected_text():
        print("✅ Clicked My projects")
        time.sleep(2)  # Wait for navigation
        return True
    else:
        print("❌ Failed to click My projects")
        return False


def test_step_6():
    """Test: Find 'Edit project' text"""
    print("=== Test Step 6: Find Edit Project ===")
    if find_text_on_page("Edit project"):
        print("✅ Found 'Edit project' text")
        return True
    else:
        print("❌ 'Edit project' not found")
        return False


def test_step_7():
    """Test: Click Edit project"""
    print("=== Test Step 7: Click Edit Project ===")
    if click_selected_text():
        print("✅ Clicked Edit project")
        time.sleep(2)  # Wait for form to load
        return True
    else:
        print("❌ Failed to click Edit project")
        return False


def test_step_8():
    """Test: Check if on submission form"""
    print("=== Test Step 8: Check Form ===")
    if find_text_on_page("Project name") and find_text_on_page("Elevator pitch"):
        print("✅ On submission form")
        return True
    else:
        print("❌ Not on submission form")
        return False


def main():
    """Run all test steps systematically"""
    print("🔧 DevPost Automation - Step by Step Testing")
    print("=" * 50)

    steps = [
        test_step_1,
        test_step_2,
        test_step_3,
        test_step_4,
        test_step_5,
        test_step_6,
        test_step_7,
        test_step_8,
    ]

    for i, step in enumerate(steps, 1):
        print(f"\n--- Running Step {i} ---")
        if not step():
            print(f"❌ Step {i} failed. Stopping.")
            break
        print(f"✅ Step {i} completed")

    print("\n🎯 Testing complete!")


if __name__ == "__main__":
    main()
