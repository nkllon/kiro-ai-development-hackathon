#!/usr/bin/env python3
"""
Paranoid DevPost Automation - Check preconditions after EVERY operation
Like debugging Oracle stored procedures - verify state after every single step
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
        print(f"❌ AppleScript error: {e.stderr}")
        return None


def take_screenshot(step_name):
    """Take screenshot after every operation"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{step_name}_{timestamp}.png"
    subprocess.run(["screencapture", "-x", filename], check=True)
    print(f"📸 Screenshot saved: {filename}")
    return filename


def check_chrome_focus():
    """Check if Chrome is focused - PRECONDITION CHECK"""
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = execute_applescript(script)
    is_focused = result == "Google Chrome"
    print(f"🔍 Precondition check - Chrome focused: {is_focused} (current: {result})")
    return is_focused


def get_current_url():
    """Get current URL - STATE VERIFICATION"""
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.location.href"'
    result = execute_applescript(script)
    print(f"🔍 State check - Current URL: {result}")
    return result


def get_page_title():
    """Get current page title - STATE VERIFICATION"""
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.title"'
    result = execute_applescript(script)
    print(f"🔍 State check - Page title: {result}")
    return result


def paranoid_step_1():
    """Step 1: Ensure Chrome is focused"""
    print("=== PARANOID STEP 1: Ensure Chrome Focus ===")

    # PRECONDITION CHECK
    if not check_chrome_focus():
        print("⚠️  Chrome not focused, attempting to focus...")
        script = 'tell application "Google Chrome" to activate'
        execute_applescript(script)
        time.sleep(1)  # Wait for focus change

        # POST-CONDITION CHECK
        if not check_chrome_focus():
            print("❌ FAILED: Could not focus Chrome")
            return False

    # STATE VERIFICATION
    url = get_current_url()
    title = get_page_title()
    take_screenshot("step1_chrome_focused")

    print("✅ Step 1 completed - Chrome is focused")
    return True


def paranoid_step_2():
    """Step 2: Navigate to DevPost homepage"""
    print("=== PARANOID STEP 2: Navigate to DevPost ===")

    # PRECONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Chrome not focused before navigation")
        return False

    # ACTION
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.location.href = \\"https://devpost.com\\"; \\"Navigated\\";"'
    result = execute_applescript(script)
    time.sleep(3)  # Wait for page load

    # POST-CONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Lost Chrome focus after navigation")
        return False

    # STATE VERIFICATION
    url = get_current_url()
    title = get_page_title()
    take_screenshot("step2_devpost_homepage")

    if "devpost.com" in url:
        print("✅ Step 2 completed - On DevPost homepage")
        return True
    else:
        print(f"❌ FAILED: Not on DevPost homepage. URL: {url}")
        return False


def paranoid_step_3():
    """Step 3: Search for Kiro hackathon"""
    print("=== PARANOID STEP 3: Search for Kiro ===")

    # PRECONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Chrome not focused before search")
        return False

    # ACTION
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.find(\\"Kiro\\", false, false, true, false, true, false);"'
    result = execute_applescript(script)

    # POST-CONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Lost Chrome focus after search")
        return False

    # STATE VERIFICATION
    take_screenshot("step3_kiro_found")

    if result == "true":
        print("✅ Step 3 completed - Found Kiro text")
        return True
    else:
        print(f"❌ FAILED: Kiro text not found. Result: {result}")
        return False


def paranoid_step_4():
    """Step 4: Click on Kiro"""
    print("=== PARANOID STEP 4: Click on Kiro ===")

    # PRECONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Chrome not focused before click")
        return False

    # ACTION
    script = '''tell application "Google Chrome" to tell active tab of front window to execute javascript "
        var selection = window.getSelection();
        if(selection.rangeCount > 0) {
            var range = selection.getRangeAt(0);
            var element = range.commonAncestorContainer;
            if(element.nodeType === 3) { element = element.parentNode; }
            element.click();
            console.log('Clicked on Kiro');
        }
    "'''
    result = execute_applescript(script)
    time.sleep(2)  # Wait for navigation

    # POST-CONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Lost Chrome focus after click")
        return False

    # STATE VERIFICATION
    url = get_current_url()
    title = get_page_title()
    take_screenshot("step4_kiro_clicked")

    print(f"🔍 After click - URL: {url}, Title: {title}")
    print("✅ Step 4 completed - Clicked on Kiro")
    return True


def paranoid_step_5():
    """Step 5: Look for My Projects"""
    print("=== PARANOID STEP 5: Look for My Projects ===")

    # PRECONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Chrome not focused before search")
        return False

    # ACTION
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.find(\\"My projects\\", false, false, true, false, true, false);"'
    result = execute_applescript(script)

    # POST-CONDITION CHECK
    if not check_chrome_focus():
        print("❌ FAILED: Lost Chrome focus after search")
        return False

    # STATE VERIFICATION
    take_screenshot("step5_my_projects_search")

    if result == "true":
        print("✅ Step 5 completed - Found My Projects")
        return True
    else:
        print(f"❌ FAILED: My Projects not found. Result: {result}")
        # Let's see what's actually on the page
        script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.body.innerText.substring(0, 300)"'
        page_content = execute_applescript(script)
        print(f"🔍 Page content: {page_content}")
        return False


def main():
    """Run paranoid automation with preconditions checked at every step"""
    print("🔧 PARANOID DevPost Automation")
    print("Checking preconditions after EVERY operation")
    print("=" * 60)

    steps = [
        paranoid_step_1,
        paranoid_step_2,
        paranoid_step_3,
        paranoid_step_4,
        paranoid_step_5,
    ]

    for i, step in enumerate(steps, 1):
        print(f"\n{'='*20} RUNNING STEP {i} {'='*20}")
        if not step():
            print(f"❌ STEP {i} FAILED. STOPPING AUTOMATION.")
            break
        print(f"✅ STEP {i} COMPLETED SUCCESSFULLY")
        time.sleep(1)  # Brief pause between steps

    print("\n🎯 PARANOID AUTOMATION COMPLETE!")


if __name__ == "__main__":
    main()
