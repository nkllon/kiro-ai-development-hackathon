#!/usr/bin/env python3
"""
Manage Team Page Handler
========================

Proper handler for the Manage Team page that understands
the actual DevPost workflow - no Save & Continue button exists!

Author: Beast Mode Framework
Date: 2025-01-14
Purpose: Handle Manage Team page navigation correctly
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright


def handle_manage_team_page():
    """Handle the Manage Team page correctly."""
    try:
        playwright = sync_playwright().start()

        # Get page info
        response = requests.get("http://localhost:9222/json")
        pages_info = response.json()

        devpost_page_info = None
        for p_info in pages_info:
            if "devpost.com" in p_info.get("url", "") and "manage-team" in p_info.get(
                "url", ""
            ):
                devpost_page_info = p_info
                break

        if not devpost_page_info:
            print("❌ No DevPost manage team page found")
            return

        print(f"📄 Target page: {devpost_page_info['title']}")
        print(f"🔗 URL: {devpost_page_info['url']}")

        # Connect to browser
        print("🔍 Connecting to existing browser...")
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        pages = context.pages

        # Find DevPost page
        target_page = None
        for page in pages:
            if "devpost.com" in page.url and "manage-team" in page.url:
                target_page = page
                break

        if not target_page:
            target_page = pages[0]

        print(f"✅ Connected to: {target_page.url}")

        # Wait for page to be ready
        print("⏳ Waiting for page to be ready...")
        target_page.wait_for_load_state("networkidle")

        print(f"\n{'='*60}")
        print(f"👥 MANAGE TEAM PAGE - CORRECT WORKFLOW")
        print(f"{'='*60}")

        # Check if we're on the right page
        if "manage-team" not in target_page.url:
            print("❌ Not on the Manage Team page!")
            return

        print("✅ On Manage Team page - this page has NO Save & Continue button!")
        print(
            "💡 The Manage Team page is for inviting team members, not for saving progress."
        )

        # Get available actions
        buttons = target_page.query_selector_all(
            "button, input[type='button'], input[type='submit']"
        )
        email_input = target_page.query_selector("input[type='email']")
        join_url_input = target_page.query_selector("input[name='join_url']")

        print(f"\n🔘 Available Actions:")

        # Show email invitation option
        if email_input:
            print(f"   1. Add team member via email")
            print(
                f"      • Email input: {email_input.get_attribute('placeholder') or 'Email address'}"
            )

        # Show join URL option
        if join_url_input:
            join_url = join_url_input.get_attribute("value") or ""
            print(f"   2. Share team join URL")
            print(f"      • URL: {join_url}")

        # Show available buttons
        for i, button in enumerate(buttons, 1):
            button_text = (
                button.text_content().strip()
                or button.get_attribute("value")
                or "no-text"
            )
            is_visible = button.is_visible()
            is_enabled = button.is_enabled()

            print(f"   {len(buttons) + i}. {button_text}")
            print(f"      Visible: {is_visible} | Enabled: {is_enabled}")

        print(f"\n🎯 Navigation Options:")
        print(f"   • Use step navigation to go to next step (Project Overview)")
        print(f"   • Add team members if needed")
        print(f"   • Share join URL with team members")
        print(f"   • Navigate away from this page when done")

        # Interactive menu
        while True:
            print(f"\n🎛️  What would you like to do?")
            print(f"   1. Add team member via email")
            print(f"   2. Copy team join URL")
            print(f"   3. Navigate to next step (Project Overview)")
            print(f"   4. Navigate to previous step")
            print(f"   5. Show current team members")
            print(f"   6. Take screenshot")
            print(f"   0. Exit")

            choice = input(f"\n🎯 Enter your choice (0-6): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                # Add team member via email
                if email_input:
                    email = input("📧 Enter team member email: ").strip()
                    if email:
                        email_input.fill(email)
                        send_button = target_page.query_selector(
                            "button:has-text('Send invite')"
                        )
                        if send_button and send_button.is_enabled():
                            print(f"📤 Sending invite to: {email}")
                            send_button.click()
                            target_page.wait_for_timeout(2000)  # Wait for response
                            print("✅ Invite sent!")
                        else:
                            print("❌ Send invite button not available")
                    else:
                        print("❌ No email provided")
                else:
                    print("❌ Email input not found")
            elif choice == "2":
                # Copy team join URL
                if join_url_input:
                    join_url = join_url_input.get_attribute("value") or ""
                    copy_button = target_page.query_selector("button:has-text('Copy')")
                    if copy_button and copy_button.is_enabled():
                        print(f"📋 Copying join URL: {join_url}")
                        copy_button.click()
                        print("✅ URL copied to clipboard!")
                    else:
                        print(f"📋 Join URL: {join_url}")
                        print("💡 You can manually copy this URL")
                else:
                    print("❌ Join URL not found")
            elif choice == "3":
                # Navigate to next step
                print("🔄 Navigating to Project Overview...")
                # Look for step navigation
                next_step = target_page.query_selector(
                    "#steps-navigation a.step:not(.current):not(.completed)"
                )
                if next_step and next_step.is_visible():
                    next_step.click()
                    target_page.wait_for_load_state("networkidle")
                    print(f"✅ Navigated to: {target_page.url}")
                    break
                else:
                    print("❌ Next step not available")
            elif choice == "4":
                # Navigate to previous step
                print("🔄 Navigating to previous step...")
                prev_step = target_page.query_selector(
                    "#steps-navigation a.step.completed"
                )
                if prev_step and prev_step.is_visible():
                    prev_step.click()
                    target_page.wait_for_load_state("networkidle")
                    print(f"✅ Navigated to: {target_page.url}")
                    break
                else:
                    print("❌ Previous step not available")
            elif choice == "5":
                # Show current team members
                team_members = target_page.query_selector_all(
                    "[class*='team-member'], [class*='member']"
                )
                print(f"\n👥 Current Team Members: {len(team_members)}")
                for i, member in enumerate(team_members, 1):
                    member_text = member.text_content().strip()
                    print(f"   {i}. {member_text}")
            elif choice == "6":
                # Take screenshot
                timestamp = int(time.time())
                screenshot_path = f"manage_team_{timestamp}.png"
                target_page.screenshot(path=screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
            else:
                print("❌ Invalid choice")

    except Exception as e:
        print(f"❌ Handler failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()


if __name__ == "__main__":
    handle_manage_team_page()
