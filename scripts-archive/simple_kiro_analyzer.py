#!/usr/bin/env python3
"""
Simple Kiro Page Analyzer - Analyze the current Kiro DevPost page for edit buttons
"""

import subprocess
import requests
import re
import time


def get_current_page_url():
    """Get the current page URL from Chrome"""
    script = """
    tell application "Google Chrome"
        if (count of windows) > 0 then
            set currentWindow to front window
            set currentTab to active tab of currentWindow
            return URL of currentTab
        else
            return "No Chrome windows open"
        end if
    end tell
    """

    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def get_page_content(url):
    """Get page content using curl"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        return response.text
    except Exception as e:
        return f"Error fetching page: {e}"


def analyze_kiro_page():
    """Analyze the Kiro DevPost page for edit buttons and project information"""
    print("🔍 KIRO DEVPOST PAGE ANALYSIS")
    print("=" * 50)

    # Get current URL
    current_url = get_current_page_url()
    print(f"Current URL: {current_url}")
    print()

    if "kiro.devpost.com" not in current_url:
        print("❌ Not on Kiro DevPost page!")
        return

    # Get page content
    print("📄 Fetching page content...")
    content = get_page_content(current_url)

    if content.startswith("Error"):
        print(f"❌ {content}")
        return

    print("✅ Page content fetched successfully")
    print()

    # Look for edit buttons using regex
    print("🔍 SEARCHING FOR EDIT BUTTONS:")

    # Look for edit buttons/links in HTML
    edit_patterns = [
        r"<[^>]*edit[^>]*>",
        r"<button[^>]*edit[^>]*>",
        r"<a[^>]*edit[^>]*>",
        r"<input[^>]*edit[^>]*>",
        r"Edit\s+[Pp]roject",
        r"edit\s+project",
        r"Edit\s+[Ss]ubmission",
        r"edit\s+submission",
    ]

    edit_matches = []
    for pattern in edit_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        edit_matches.extend(matches)

    if edit_matches:
        print(f"✅ Found {len(edit_matches)} potential edit elements:")
        for i, match in enumerate(edit_matches[:10], 1):  # Show first 10
            # Clean up the match for display
            clean_match = re.sub(r"\s+", " ", match.strip())
            if len(clean_match) > 100:
                clean_match = clean_match[:100] + "..."
            print(f"   {i}. {clean_match}")
    else:
        print("❌ No edit buttons found with regex patterns")

    print()

    # Look for form elements
    print("📝 FORM ELEMENTS:")
    form_matches = re.findall(r"<form[^>]*>", content, re.IGNORECASE)
    if form_matches:
        print(f"Found {len(form_matches)} forms:")
        for i, form in enumerate(form_matches[:5], 1):
            # Extract action and method
            action_match = re.search(r'action=["\']([^"\']*)["\']', form, re.IGNORECASE)
            method_match = re.search(r'method=["\']([^"\']*)["\']', form, re.IGNORECASE)
            action = action_match.group(1) if action_match else "not specified"
            method = method_match.group(1) if method_match else "GET"
            print(f"   Form {i}: Action={action}, Method={method}")

    print()

    # Look for JavaScript that might handle edit functionality
    print("⚡ JAVASCRIPT ANALYSIS:")
    js_edit_patterns = [
        r"edit[A-Za-z]*\s*[:=]",
        r"onClick.*edit",
        r"function.*edit",
        r"edit.*function",
    ]

    js_matches = []
    for pattern in js_edit_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        js_matches.extend(matches)

    if js_matches:
        print(f"Found {len(js_matches)} JavaScript edit-related patterns:")
        for i, match in enumerate(js_matches[:5], 1):
            clean_match = re.sub(r"\s+", " ", match.strip())
            if len(clean_match) > 80:
                clean_match = clean_match[:80] + "..."
            print(f"   {i}. {clean_match}")
    else:
        print("No JavaScript edit patterns found")

    print()

    # Look for submission-related content
    print("📋 SUBMISSION STATUS:")
    submission_keywords = [
        "submission",
        "submitted",
        "draft",
        "complete",
        "incomplete",
        "project",
    ]
    for keyword in submission_keywords:
        pattern = rf"{keyword}[^<]*"
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"'{keyword}' mentions:")
            for match in matches[:3]:  # Show first 3
                clean_match = re.sub(r"\s+", " ", match.strip())
                if len(clean_match) > 60:
                    clean_match = clean_match[:60] + "..."
                print(f"   - {clean_match}")

    print()

    # Save page content for further analysis
    with open("kiro_page_content.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("💾 Page content saved to 'kiro_page_content.html' for further analysis")

    # Look for specific DevPost patterns
    print("🎯 DEVPOST SPECIFIC PATTERNS:")

    # Look for DevPost-specific edit URLs
    devpost_edit_patterns = [
        r"/edit",
        r"/projects/[^/]+/edit",
        r"submissions/[^/]+/edit",
        r"edit.*project",
        r"edit.*submission",
    ]

    for pattern in devpost_edit_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"Found DevPost edit patterns ({pattern}):")
            for match in matches[:3]:
                print(f"   - {match}")


if __name__ == "__main__":
    analyze_kiro_page()
