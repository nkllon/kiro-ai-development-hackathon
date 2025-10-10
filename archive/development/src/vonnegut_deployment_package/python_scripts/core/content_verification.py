#!/usr/bin/env python3
"""
Content Verification - Don't rely on URL alone
SPAs can change content without changing URL
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


def verify_page_content(expected_texts):
    """Verify page contains expected content, not just URL"""
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.body.innerText"'
    page_content = execute_applescript(script)

    print(f"🔍 Page content verification:")
    for expected_text in expected_texts:
        found = expected_text.lower() in page_content.lower()
        print(f"  - '{expected_text}': {'✅' if found else '❌'}")
        if not found:
            return False

    return True


def paranoid_step_6():
    """Step 6: Click My Projects and verify content change"""
    print("=== PARANOID STEP 6: Click My Projects ===")

    # PRECONDITION CHECK
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    focus = execute_applescript(script)
    if focus != "Google Chrome":
        print(f"❌ FAILED: Chrome not focused (current: {focus})")
        return False

    # ACTION
    script = '''tell application "Google Chrome" to tell active tab of front window to execute javascript "
        var selection = window.getSelection();
        if(selection.rangeCount > 0) {
            var range = selection.getRangeAt(0);
            var element = range.commonAncestorContainer;
            if(element.nodeType === 3) { element = element.parentNode; }
            element.click();
            console.log('Clicked My Projects');
        }
    "'''
    result = execute_applescript(script)
    time.sleep(2)  # Wait for content change

    # POST-CONDITION CHECK
    focus = execute_applescript(script)
    if focus != "Google Chrome":
        print(f"❌ FAILED: Lost Chrome focus after click (current: {focus})")
        return False

    # CONTENT VERIFICATION (not just URL!)
    expected_content = ["Edit project", "Create project", "Import from portfolio"]
    if verify_page_content(expected_content):
        print("✅ Step 6 completed - Content verified: My Projects page loaded")
        return True
    else:
        print("❌ FAILED: Content verification failed - not on My Projects page")
        return False


def paranoid_step_7():
    """Step 7: Click Edit project and verify form content"""
    print("=== PARANOID STEP 7: Click Edit Project ===")

    # PRECONDITION CHECK
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    focus = execute_applescript(script)
    if focus != "Google Chrome":
        print(f"❌ FAILED: Chrome not focused (current: {focus})")
        return False

    # ACTION
    script = 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.find(\\"Edit project\\", false, false, true, false, true, false);"'
    execute_applescript(script)

    script = '''tell application "Google Chrome" to tell active tab of front window to execute javascript "
        var selection = window.getSelection();
        if(selection.rangeCount > 0) {
            var range = selection.getRangeAt(0);
            var element = range.commonAncestorContainer;
            if(element.nodeType === 3) { element = element.parentNode; }
            element.click();
            console.log('Clicked Edit project');
        }
    "'''
    result = execute_applescript(script)
    time.sleep(3)  # Wait for form to load

    # POST-CONDITION CHECK
    focus = execute_applescript(script)
    if focus != "Google Chrome":
        print(f"❌ FAILED: Lost Chrome focus after click (current: {focus})")
        return False

    # CONTENT VERIFICATION - Look for form fields, not just URL
    expected_form_content = [
        "Project name",
        "Elevator pitch",
        "About the project",
        "Built with",
    ]
    if verify_page_content(expected_form_content):
        print("✅ Step 7 completed - Content verified: Submission form loaded")
        return True
    else:
        print("❌ FAILED: Content verification failed - not on submission form")
        return False


def main():
    """Continue paranoid automation with content verification"""
    print("🔧 PARANOID AUTOMATION - Content Verification")
    print("Don't trust URLs - verify actual page content!")
    print("=" * 60)

    steps = [paranoid_step_6, paranoid_step_7]

    for i, step in enumerate(steps, 6):
        print(f"\n{'='*20} RUNNING STEP {i} {'='*20}")
        if not step():
            print(f"❌ STEP {i} FAILED. STOPPING AUTOMATION.")
            break
        print(f"✅ STEP {i} COMPLETED SUCCESSFULLY")
        time.sleep(1)

    print("\n🎯 CONTENT VERIFICATION COMPLETE!")


if __name__ == "__main__":
    main()
