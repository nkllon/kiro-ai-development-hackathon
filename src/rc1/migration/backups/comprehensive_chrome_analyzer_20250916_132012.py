#!/usr/bin/env python3
"""
Comprehensive Chrome Tab Analyzer
Uses AppleScript to interrogate every tab in Chrome and provide full analysis
"""

import subprocess
import json
import time
from datetime import datetime


def run_applescript(script):
    """Run AppleScript and return the result"""
    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "AppleScript timeout", 1
    except Exception as e:
        return "", str(e), 1


def get_chrome_window_info():
    """Get information about all Chrome windows and tabs"""
    script = """
    tell application "Google Chrome"
        set windowList to {}
        repeat with w in windows
            set tabList to {}
            repeat with t in tabs of w
                set tabInfo to {name:title of t, url:URL of t, index:active tab index of w}
                set end of tabList to tabInfo
            end repeat
            set windowInfo to {window_index:index of w, active:active of w, tab_count:count of tabs of w, tabs:tabList}
            set end of windowList to windowInfo
        end repeat
        return windowList as string
    end tell
    """

    stdout, stderr, code = run_applescript(script)
    if code != 0:
        print(f"AppleScript Error: {stderr}")
        return None

    try:
        # AppleScript returns a string representation, we need to parse it
        # For now, let's get basic info
        return stdout
    except Exception as e:
        print(f"Parse error: {e}")
        return stdout


def get_current_tab_info():
    """Get current active tab information"""
    script = """
    tell application "Google Chrome"
        if (count of windows) > 0 then
            set currentWindow to front window
            set currentTab to active tab of currentWindow
            return "Title: " & title of currentTab & " | URL: " & URL of currentTab
        else
            return "No Chrome windows open"
        end if
    end tell
    """

    stdout, stderr, code = run_applescript(script)
    return stdout, stderr, code


def get_all_tab_titles():
    """Get titles of all tabs in all windows"""
    script = """
    tell application "Google Chrome"
        set allTitles to {}
        repeat with w in windows
            repeat with t in tabs of w
                set tabTitle to title of t
                set tabUrl to URL of t
                set tabInfo to tabTitle & " | " & tabUrl
                set end of allTitles to tabInfo
            end repeat
        end repeat
        return allTitles as string
    end tell
    """

    stdout, stderr, code = run_applescript(script)
    return stdout, stderr, code


def count_tabs():
    """Count total number of tabs"""
    script = """
    tell application "Google Chrome"
        set totalTabs to 0
        repeat with w in windows
            set totalTabs to totalTabs + (count of tabs of w)
        end repeat
        return totalTabs as string
    end tell
    """

    stdout, stderr, code = run_applescript(script)
    return stdout, stderr, code


def analyze_chrome_tabs():
    """Comprehensive Chrome tab analysis"""
    print("🔍 COMPREHENSIVE CHROME TAB ANALYSIS")
    print("=" * 50)
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get current tab info
    print("📍 CURRENT ACTIVE TAB:")
    current_info, current_err, current_code = get_current_tab_info()
    if current_code == 0:
        print(f"   {current_info}")
    else:
        print(f"   Error: {current_err}")
    print()

    # Count total tabs
    print("📊 TAB COUNT:")
    count_info, count_err, count_code = count_tabs()
    if count_code == 0:
        print(f"   Total tabs open: {count_info}")
    else:
        print(f"   Error counting tabs: {count_err}")
    print()

    # Get all tab information
    print("📋 ALL TABS ANALYSIS:")
    all_tabs, all_err, all_code = get_all_tab_titles()
    if all_code == 0 and all_tabs:
        tabs_list = all_tabs.split(", ")
        for i, tab in enumerate(tabs_list, 1):
            print(f"   Tab {i}: {tab}")
    else:
        print(f"   Error getting tab info: {all_err}")
    print()

    # Get window structure
    print("🪟 WINDOW STRUCTURE:")
    window_info = get_chrome_window_info()
    if window_info:
        print(f"   {window_info}")
    else:
        print("   Could not get window structure")
    print()

    # Look for DevPost-related content
    print("🎯 DEVPOST ANALYSIS:")
    if all_code == 0 and all_tabs:
        devpost_tabs = []
        for tab in all_tabs.split(", "):
            if "devpost" in tab.lower():
                devpost_tabs.append(tab)

        if devpost_tabs:
            print("   Found DevPost-related tabs:")
            for tab in devpost_tabs:
                print(f"   - {tab}")
        else:
            print("   No DevPost tabs found in current session")
    else:
        print("   Cannot analyze DevPost content due to tab retrieval error")
    print()

    # Look for hackathon-related content
    print("🏆 HACKATHON ANALYSIS:")
    if all_code == 0 and all_tabs:
        hackathon_keywords = ["hackathon", "kiro", "devpost", "submission", "project"]
        hackathon_tabs = []

        for tab in all_tabs.split(", "):
            tab_lower = tab.lower()
            if any(keyword in tab_lower for keyword in hackathon_keywords):
                hackathon_tabs.append(tab)

        if hackathon_tabs:
            print("   Found hackathon-related tabs:")
            for tab in hackathon_tabs:
                print(f"   - {tab}")
        else:
            print("   No obvious hackathon-related tabs found")
    else:
        print("   Cannot analyze hackathon content due to tab retrieval error")


if __name__ == "__main__":
    analyze_chrome_tabs()
