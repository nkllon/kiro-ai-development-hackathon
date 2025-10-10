#!/usr/bin/env python3
"""
DevPost Form Helper
==================

Provides form data and tries to focus on form fields for easy copy-paste.
"""

import subprocess
import time


def run_applescript(script):
    """Run AppleScript and return the result."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e}")
        return None


def focus_form_fields():
    """Try to focus on form fields to make them easier to fill."""
    print("🎯 Focusing on form fields...")

    # Try to focus on the first text input
    result = run_applescript(
        """
    tell application "Google Chrome"
        tell active tab of front window
            execute javascript "
                var inputs = document.querySelectorAll('input[type=\"text\"], textarea');
                if(inputs.length > 0) {
                    inputs[0].focus();
                    inputs[0].scrollIntoView();
                    console.log('Focused on first input');
                }
            "
        end tell
    end tell
    """
    )

    if result is None:
        print("❌ Failed to focus on form fields")
    else:
        print("✅ Focused on form fields")


def print_form_data():
    """Print the form data in a copy-paste friendly format."""
    print("🎯 DevPost Hackathon Submission Data")
    print("=" * 40)
    print()

    print("📝 TITLE (copy this):")
    print("-" * 25)
    print("The Requirements ARE the Solution - Beast Mode Framework")
    print()

    print("📄 DESCRIPTION (copy this):")
    print("-" * 30)
    print(
        """A revolutionary AI-powered development framework that transforms requirements into executable solutions, demonstrating 20.4% systematic superiority over ad-hoc development approaches.

## 🚀 The Future of Development
Beast Mode proves that systematic approaches consistently outperform ad-hoc development. Requirements become executable solutions, not just documentation.
**The Requirements ARE the Solution - and we have the evidence to prove it!**"""
    )
    print()

    print("🔗 PROJECT URL (copy this):")
    print("-" * 30)
    print("https://github.com/nkllon/kiro-ai-development-hackathon")
    print()

    print("🎥 DEMO VIDEO URL (copy this):")
    print("-" * 35)
    print("https://youtube.com/watch?v=demo-video")
    print()

    print("💡 INSTRUCTIONS:")
    print("-" * 15)
    print("1. Click on each form field")
    print("2. Copy and paste the data above")
    print("3. Make sure to fill all required fields")
    print("4. Submit the form when complete")
    print()


def main():
    print("🎯 DevPost Form Helper")
    print("=" * 25)

    # Get current page info
    url = run_applescript(
        'tell application "Google Chrome" to get URL of active tab of front window'
    )
    title = run_applescript(
        'tell application "Google Chrome" to get title of active tab of front window'
    )

    print(f"📍 Current URL: {url}")
    print(f"📄 Current Title: {title}")

    if "edit" not in url or "submission" not in url:
        print("❌ Not on the submission edit page!")
        return

    print("✅ On submission edit page - ready to help!")

    # Try to focus on form fields
    focus_form_fields()

    # Print the data
    print_form_data()

    print("🎉 Ready to fill out your DevPost submission!")


if __name__ == "__main__":
    main()
