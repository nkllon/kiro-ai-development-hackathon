#!/usr/bin/env python3
"""
Ultra Paranoid Automation - Handle focus loss and verify we're doing the right thing
Welcome to being human - constantly checking we're not making mistakes
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


def force_chrome_focus():
    """Force Chrome to focus and verify it worked"""
    print("🔧 Forcing Chrome focus...")
    script = 'tell application "Google Chrome" to activate'
    execute_applescript(script)
    time.sleep(1)  # Wait for focus change

    # Verify focus
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    focus = execute_applescript(script)
    is_focused = focus == "Google Chrome"
    print(f"🔍 Focus verification: {is_focused} (current: {focus})")
    return is_focused


def verify_we_are_where_we_think_we_are(expected_content):
    """Verify we're on the page we think we are"""
    print("🔍 Verifying we're where we think we are...")

    # Get page content
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.body.innerText.substring(0, 500)"'
    page_content = execute_applescript(script)

    print(f"📄 Current page content preview: {page_content[:200]}...")

    # Check for expected content
    for expected in expected_content:
        found = expected.lower() in page_content.lower()
        print(f"  - '{expected}': {'✅' if found else '❌'}")
        if not found:
            print(f"❌ DANGER: We're not where we think we are! Missing: {expected}")
            return False

    print("✅ Verification passed - we are where we think we are")
    return True


def safe_click_with_verification(click_text, expected_after_click):
    """Safely click something and verify the result"""
    print(f"🖱️  Attempting to click: {click_text}")

    # PRECONDITION: Ensure Chrome is focused
    if not force_chrome_focus():
        print("❌ CRITICAL: Cannot focus Chrome - aborting click")
        return False

    # Find the text
    script = f'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.find(\\"{click_text}\\", false, false, true, false, true, false);"'
    found = execute_applescript(script)

    if found != "true":
        print(f"❌ CRITICAL: Cannot find '{click_text}' - aborting click")
        return False

    # Click it
    script = '''tell application "Google Chrome" to tell active tab of front window to execute javascript "
        var selection = window.getSelection();
        if(selection.rangeCount > 0) {
            var range = selection.getRangeAt(0);
            var element = range.commonAncestorContainer;
            if(element.nodeType === 3) { element = element.parentNode; }
            element.click();
            console.log('Clicked successfully');
        }
    "'''
    execute_applescript(script)
    time.sleep(2)  # Wait for change

    # POST-CONDITION: Verify we're still focused and where we expected
    if not force_chrome_focus():
        print("❌ CRITICAL: Lost focus after click - this is dangerous!")
        return False

    # Verify we're where we expected to be
    if not verify_we_are_where_we_think_we_are(expected_after_click):
        print(f"❌ CRITICAL: Click didn't take us where we expected!")
        return False

    print(f"✅ Successfully clicked '{click_text}' and verified result")
    return True


def ultra_paranoid_step_1():
    """Step 1: Get to My Projects page safely"""
    print("=== ULTRA PARANOID STEP 1: Get to My Projects ===")

    # Verify we're on the hackathon page first
    if not verify_we_are_where_we_think_we_are(["Code with Kiro", "My projects"]):
        print("❌ CRITICAL: Not on hackathon page - aborting")
        return False

    # Click My Projects
    if not safe_click_with_verification(
        "My projects", ["Edit project", "Create project"]
    ):
        print("❌ CRITICAL: Failed to click My Projects safely")
        return False

    print("✅ Step 1 completed - Safely on My Projects page")
    return True


def ultra_paranoid_step_2():
    """Step 2: Get to submission form safely"""
    print("=== ULTRA PARANOID STEP 2: Get to Submission Form ===")

    # Click Edit project
    if not safe_click_with_verification(
        "Edit project", ["Project name", "Elevator pitch", "About the project"]
    ):
        print("❌ CRITICAL: Failed to click Edit project safely")
        return False

    print("✅ Step 2 completed - Safely on submission form")
    return True


def ultra_paranoid_step_3():
    """Step 3: Fill form fields safely"""
    print("=== ULTRA PARANOID STEP 3: Fill Form Fields ===")

    # Verify we're on the form
    if not verify_we_are_where_we_think_we_are(["Project name", "Elevator pitch"]):
        print("❌ CRITICAL: Not on submission form - aborting")
        return False

    # Focus Chrome
    if not force_chrome_focus():
        print("❌ CRITICAL: Cannot focus Chrome for form filling")
        return False

    # Find Project name field
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.find(\\"Project name\\", false, false, true, false, true, false);"'
    found = execute_applescript(script)

    if found != "true":
        print("❌ CRITICAL: Cannot find Project name field")
        return False

    # Click and type
    script = '''tell application "Google Chrome" to tell active tab of front window to execute javascript "
        var selection = window.getSelection();
        if(selection.rangeCount > 0) {
            var range = selection.getRangeAt(0);
            var element = range.commonAncestorContainer;
            if(element.nodeType === 3) { element = element.parentNode; }
            element.click();
        }
    "'''
    execute_applescript(script)

    # Type project name
    script = 'tell application "System Events" to keystroke "The Requirements ARE the Solution - Beast Mode Framework"'
    execute_applescript(script)

    print("✅ Step 3 completed - Safely filled project name")
    return True


def main():
    """Ultra paranoid automation - handle all the things that can go wrong"""
    print("🔧 ULTRA PARANOID AUTOMATION")
    print("Welcome to being human - constantly checking we're not making mistakes")
    print("=" * 70)

    steps = [ultra_paranoid_step_1, ultra_paranoid_step_2, ultra_paranoid_step_3]

    for i, step in enumerate(steps, 1):
        print(f"\n{'='*25} RUNNING STEP {i} {'='*25}")
        if not step():
            print(f"❌ STEP {i} FAILED. STOPPING - TOO DANGEROUS TO CONTINUE.")
            break
        print(f"✅ STEP {i} COMPLETED SAFELY")
        time.sleep(1)

    print("\n🎯 ULTRA PARANOID AUTOMATION COMPLETE!")


if __name__ == "__main__":
    main()
