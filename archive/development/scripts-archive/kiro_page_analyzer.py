#!/usr/bin/env python3
"""
Kiro Page Analyzer - Analyze the current Kiro DevPost page for edit buttons and project status
"""

import subprocess
import requests
import re
from bs4 import BeautifulSoup
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

    # Parse with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Look for edit buttons
    print("🔍 SEARCHING FOR EDIT BUTTONS:")
    edit_keywords = ["edit", "Edit", "EDIT", "modify", "update", "change"]
    edit_buttons = []

    for keyword in edit_keywords:
        # Look for buttons, links, and form elements
        elements = soup.find_all(
            ["button", "a", "input"], string=re.compile(keyword, re.I)
        )
        edit_buttons.extend(elements)

        # Also look for elements with edit-related classes or IDs
        elements = soup.find_all(
            ["button", "a", "input"], class_=re.compile(keyword, re.I)
        )
        edit_buttons.extend(elements)

        elements = soup.find_all(["button", "a", "input"], id=re.compile(keyword, re.I))
        edit_buttons.extend(elements)

    # Remove duplicates
    edit_buttons = list(set(edit_buttons))

    if edit_buttons:
        print(f"✅ Found {len(edit_buttons)} potential edit elements:")
        for i, btn in enumerate(edit_buttons, 1):
            btn_text = (
                btn.get_text(strip=True) or btn.get("value", "") or btn.get("title", "")
            )
            btn_class = btn.get("class", [])
            btn_id = btn.get("id", "")
            btn_href = btn.get("href", "")
            print(
                f"   {i}. Text: '{btn_text}' | Class: {btn_class} | ID: {btn_id} | Href: {btn_href}"
            )
    else:
        print("❌ No edit buttons found")

    print()

    # Look for project information
    print("📋 PROJECT INFORMATION:")

    # Look for project title
    title_elements = soup.find_all(
        ["h1", "h2", "h3"], string=re.compile("project", re.I)
    )
    if title_elements:
        print("Project titles found:")
        for elem in title_elements[:3]:  # Show first 3
            print(f"   - {elem.get_text(strip=True)}")

    # Look for submission status
    status_keywords = ["submission", "submitted", "draft", "complete", "incomplete"]
    for keyword in status_keywords:
        elements = soup.find_all(string=re.compile(keyword, re.I))
        if elements:
            print(f"Status indicators for '{keyword}':")
            for elem in elements[:2]:  # Show first 2
                print(f"   - {elem.strip()}")

    print()

    # Look for form elements
    print("📝 FORM ELEMENTS:")
    forms = soup.find_all("form")
    if forms:
        print(f"Found {len(forms)} forms:")
        for i, form in enumerate(forms, 1):
            form_action = form.get("action", "")
            form_method = form.get("method", "GET")
            print(f"   Form {i}: Action={form_action}, Method={form_method}")

    print()

    # Look for navigation elements
    print("🧭 NAVIGATION ELEMENTS:")
    nav_elements = soup.find_all(["nav", "ul"], class_=re.compile("nav|menu", re.I))
    if nav_elements:
        print("Navigation elements found:")
        for nav in nav_elements:
            links = nav.find_all("a")
            for link in links[:5]:  # Show first 5 links
                link_text = link.get_text(strip=True)
                link_href = link.get("href", "")
                if link_text:
                    print(f"   - {link_text}: {link_href}")

    print()

    # Save page content for further analysis
    with open("kiro_page_content.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("💾 Page content saved to 'kiro_page_content.html' for further analysis")


if __name__ == "__main__":
    analyze_kiro_page()
