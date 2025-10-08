#!/usr/bin/env python3
"""
Cloudflare Dashboard Automation for Custom Error Pages
======================================================

Automates the manual deployment of custom error pages through the Cloudflare
Dashboard using Playwright browser automation. This solves the limitation that
Cloudflare doesn't provide API access for Custom Error Pages.

Usage:
    python cloudflare-dashboard-automation.py --email your@email.com --password your_password
    python cloudflare-dashboard-automation.py --email your@email.com --interactive  # Prompts for password
    python cloudflare-dashboard-automation.py --headless  # Run without browser UI

Author: Claude Code AI Assistant
Date: 2025-09-30
"""

import argparse
import asyncio
import getpass
import os
import sys
import time
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError


class CloudflareDashboardAutomator:
    """Automates Cloudflare dashboard operations using Playwright."""

    def __init__(self, headless: bool = False, slow_mo: int = 1000):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.page = await self.browser.new_page()

        # Set a reasonable viewport
        await self.page.set_viewport_size({"width": 1280, "height": 720})

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def login(self, email: str = None, password: str = None) -> bool:
        """Login to Cloudflare Dashboard (supports manual Google OAuth)."""
        try:
            print("🌐 Navigating to Cloudflare Dashboard...")
            await self.page.goto("https://dash.cloudflare.com/login")

            # If no credentials provided, assume manual login (Google OAuth)
            if not email or not password:
                print("\n" + "="*60)
                print("🔐 MANUAL LOGIN REQUIRED")
                print("="*60)
                print("\n👉 Please complete login in the browser window:")
                print("   1. Click 'Sign in with Google' (or your preferred method)")
                print("   2. Complete the authentication flow")
                print("   3. Wait for the Cloudflare dashboard to load")
                print("\n⏳ Waiting for you to complete login (timeout: 300 seconds / 5 minutes)...")
                print("="*60 + "\n")

                # Wait for dashboard to appear (indicating successful login)
                try:
                    await self.page.wait_for_selector('[data-testid="zone-card"], .zone-card, [href*="/zones/"], nav[class*="sidebar"]', timeout=300000)
                    print("✅ Login successful! Dashboard detected.")
                    return True
                except PlaywrightTimeoutError:
                    print("❌ Login timeout - dashboard not detected within 300 seconds")
                    print("💡 Current URL:", await self.page.url)
                    return False

            # Traditional email/password login
            else:
                print("📧 Entering email...")
                await self.page.wait_for_selector('input[type="email"]', timeout=10000)
                await self.page.fill('input[type="email"]', email)

                print("🔑 Entering password...")
                await self.page.fill('input[type="password"]', password)

                print("🚀 Clicking login...")
                await self.page.click('button[type="submit"]')

                # Wait for dashboard to load or 2FA prompt
                print("⏳ Waiting for login to complete...")

                # Check for 2FA prompt
                try:
                    # Wait briefly to see if 2FA appears
                    await self.page.wait_for_selector('input[placeholder*="code"], input[name*="totp"], [data-testid*="2fa"]', timeout=5000)
                    print("🔐 Two-factor authentication detected. Please complete 2FA in the browser...")

                    # Wait for 2FA completion (look for dashboard elements)
                    await self.page.wait_for_selector('[data-testid="zone-card"], .zone-card, [href*="/zones/"]', timeout=60000)
                    print("✅ 2FA completed successfully!")

                except PlaywrightTimeoutError:
                    # No 2FA, check if we're already at dashboard
                    try:
                        await self.page.wait_for_selector('[data-testid="zone-card"], .zone-card, [href*="/zones/"]', timeout=10000)
                        print("✅ Login successful!")
                    except PlaywrightTimeoutError:
                        print("❌ Login failed - unable to reach dashboard")
                        return False

                return True

        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    async def navigate_to_zone(self, zone_name: str) -> bool:
        """Navigate to specific zone."""
        try:
            print(f"🎯 Looking for zone: {zone_name}")

            # Look for zone card or link with the domain name
            zone_selectors = [
                f'[data-testid="zone-card"] a[href*="{zone_name}"]',
                f'.zone-card a[href*="{zone_name}"]',
                f'a[href*="/zones/"][href*="{zone_name}"]',
                f'text="{zone_name}"'
            ]

            for selector in zone_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    print(f"✅ Found zone using selector: {selector}")
                    await self.page.click(selector)
                    break
                except PlaywrightTimeoutError:
                    continue
            else:
                # If no selector worked, try searching
                print(f"🔍 Searching for zone: {zone_name}")
                search_selectors = [
                    'input[placeholder*="Search"], input[type="search"]',
                    '[data-testid="search-input"]'
                ]

                for search_selector in search_selectors:
                    try:
                        await self.page.wait_for_selector(search_selector, timeout=3000)
                        await self.page.fill(search_selector, zone_name)
                        await self.page.keyboard.press('Enter')
                        await asyncio.sleep(2)

                        # Try to click the zone after search
                        for selector in zone_selectors:
                            try:
                                await self.page.wait_for_selector(selector, timeout=3000)
                                await self.page.click(selector)
                                break
                            except PlaywrightTimeoutError:
                                continue
                        break
                    except PlaywrightTimeoutError:
                        continue
                else:
                    print(f"❌ Could not find zone: {zone_name}")
                    return False

            # Wait for zone dashboard to load
            await self.page.wait_for_selector('h1, [data-testid="zone-name"]', timeout=10000)
            print(f"✅ Successfully navigated to {zone_name} zone")
            return True

        except Exception as e:
            print(f"❌ Failed to navigate to zone: {e}")
            return False

    async def navigate_to_custom_error_pages(self) -> bool:
        """Navigate to Custom Error Pages settings."""
        try:
            print("🛠️ Looking for Custom Error Pages...")

            # Try multiple navigation paths
            navigation_attempts = [
                ("Rules", "sidebar"),
                ("Custom Error Responses", "sidebar"),
                ("Configuration", "sidebar"),
                ("Error Pages", "sidebar"),
                ("Custom Error", "search")
            ]

            for item_text, method in navigation_attempts:
                try:
                    if method == "sidebar":
                        await self._click_sidebar_item(item_text)
                    elif method == "search":
                        await self._search_and_navigate(item_text)
                    # Look for error page indicators
                    error_page_indicators = [
                        'text="Custom Error Responses"',
                        'text="Error Pages"',
                        '[data-testid*="error"], [class*="error-page"]'
                    ]

                    for indicator in error_page_indicators:
                        try:
                            await self.page.wait_for_selector(indicator, timeout=3000)
                            print("✅ Found Custom Error Pages section")
                            return True
                        except PlaywrightTimeoutError:
                            continue

                except Exception:
                    continue

            print("❌ Could not find Custom Error Pages section")
            print("💡 This feature requires Cloudflare Pro plan or higher")
            return False

        except Exception as e:
            print(f"❌ Failed to navigate to Custom Error Pages: {e}")
            return False

    async def _click_sidebar_item(self, item_text: str):
        """Helper to click sidebar navigation items."""
        selectors = [
            f'nav a:has-text("{item_text}")',
            f'[data-testid="sidebar"] a:has-text("{item_text}")',
            f'.sidebar a:has-text("{item_text}")',
            f'text="{item_text}"'
        ]

        for selector in selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=2000)
                await self.page.click(selector)
                await asyncio.sleep(1)
                return
            except PlaywrightTimeoutError:
                continue

        raise Exception(f"Could not find sidebar item: {item_text}")

    async def _search_and_navigate(self, search_term: str):
        """Helper to search for navigation items."""
        search_selectors = [
            'input[placeholder*="Search"], input[type="search"]',
            '[data-testid="search-input"]'
        ]

        for selector in search_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=2000)
                await self.page.fill(selector, search_term)
                await self.page.keyboard.press('Enter')
                await asyncio.sleep(2)
                return
            except PlaywrightTimeoutError:
                continue

        raise Exception(f"Could not search for: {search_term}")

    async def deploy_error_page(self, error_code: int, html_file_path: str) -> bool:
        """Deploy custom error page."""
        try:
            print(f"📄 Deploying error page for code {error_code}...")

            # Read HTML content
            html_path = Path(html_file_path)
            if not html_path.exists():
                print(f"❌ HTML file not found: {html_file_path}")
                return False

            html_content = html_path.read_text()
            print(f"📊 HTML file size: {len(html_content) / 1024:.1f} KB")

            # Look for "Create" or "Add" button
            create_buttons = [
                'button:has-text("Create")',
                'button:has-text("Add")',
                'a:has-text("Create")',
                '[data-testid*="create"], [class*="create"]'
            ]

            for button in create_buttons:
                try:
                    await self.page.wait_for_selector(button, timeout=3000)
                    await self.page.click(button)
                    print("✅ Clicked create button")
                    break
                except PlaywrightTimeoutError:
                    continue
            else:
                print("❌ Could not find create button")
                return False

            # Wait for form to appear
            await asyncio.sleep(2)

            # Select error code
            print(f"🔢 Selecting error code {error_code}...")
            error_code_selectors = [
                f'select option[value="{error_code}"]',
                f'option:has-text("{error_code}")',
                f'[data-testid*="error-code"] option[value="{error_code}"]'
            ]

            for selector in error_code_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    await self.page.click(selector)
                    print(f"✅ Selected error code {error_code}")
                    break
                except PlaywrightTimeoutError:
                    continue

            # Select Custom HTML option
            print("📝 Selecting Custom HTML option...")
            html_selectors = [
                'option:has-text("Custom HTML")',
                'input[value="custom"], input[value="html"]',
                '[data-testid*="html"], [class*="html"]'
            ]

            for selector in html_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    await self.page.click(selector)
                    print("✅ Selected Custom HTML")
                    break
                except PlaywrightTimeoutError:
                    continue

            # Find and fill HTML content area
            print("📋 Entering HTML content...")
            content_selectors = [
                'textarea[name*="html"], textarea[name*="content"]',
                'textarea[placeholder*="HTML"]',
                '.CodeMirror textarea',
                'textarea'
            ]

            for selector in content_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)

                    # Clear existing content and fill with new content
                    await self.page.click(selector)
                    await self.page.keyboard.press('Control+a')  # Select all
                    await self.page.fill(selector, html_content)
                    print("✅ HTML content entered")
                    break
                except PlaywrightTimeoutError:
                    continue
            else:
                print("❌ Could not find HTML content field")
                return False

            # Preview (optional)
            preview_buttons = [
                'button:has-text("Preview")',
                '[data-testid*="preview"]'
            ]

            for button in preview_buttons:
                try:
                    await self.page.wait_for_selector(button, timeout=2000)
                    await self.page.click(button)
                    print("👀 Opened preview")
                    await asyncio.sleep(3)  # Give time to review
                    break
                except PlaywrightTimeoutError:
                    continue

            # Save/Deploy
            print("💾 Saving deployment...")
            save_buttons = [
                'button:has-text("Save")',
                'button:has-text("Deploy")',
                'button:has-text("Create")',
                'button[type="submit"]'
            ]

            for button in save_buttons:
                try:
                    await self.page.wait_for_selector(button, timeout=3000)
                    await self.page.click(button)
                    print("✅ Clicked save/deploy")
                    break
                except PlaywrightTimeoutError:
                    continue
            else:
                print("❌ Could not find save button")
                return False

            # Wait for deployment confirmation
            print("⏳ Waiting for deployment confirmation...")
            success_indicators = [
                'text="Success"', 'text="Created"', 'text="Deployed"',
                '[data-testid*="success"], .success, .alert-success'
            ]

            for indicator in success_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=10000)
                    print("✅ Deployment successful!")
                    return True
                except PlaywrightTimeoutError:
                    continue

            # Check if we're back at the list view (also indicates success)
            try:
                await self.page.wait_for_selector('table, .list, [data-testid*="list"]', timeout=5000)
                print("✅ Deployment appears successful (returned to list view)")
                return True
            except PlaywrightTimeoutError:
                pass

            print("⚠️ Deployment status unclear - please verify manually")
            return True

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False

    async def verify_deployment(self, error_code: int) -> bool:
        """Verify the error page deployment."""
        try:
            print(f"🔍 Verifying deployment for error code {error_code}...")

            # Look for the deployed error page in the list
            verification_selectors = [
                f'text="{error_code}"',
                f'[data-testid*="{error_code}"]',
                'td:has-text("Active"), .status-active',
                'text="Active"'
            ]

            for selector in verification_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    print(f"✅ Found indicator: {selector}")
                    break
                except PlaywrightTimeoutError:
                    continue
            else:
                print("⚠️ Could not verify deployment status")
                return False

            print("✅ Deployment verification successful")
            return True

        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False


async def main():
    """Main automation function."""
    parser = argparse.ArgumentParser(
        description="Automate Cloudflare Dashboard for Custom Error Pages deployment"
    )
    parser.add_argument("--email", help="Cloudflare account email (optional for Google OAuth)")
    parser.add_argument("--password", help="Cloudflare account password")
    parser.add_argument("--interactive", action="store_true", help="Prompt for password")
    parser.add_argument("--manual-login", action="store_true", help="Use manual login (Google OAuth, SSO, etc.)")
    parser.add_argument("--zone", default="nkllon.com", help="Zone name (default: nkllon.com)")
    parser.add_argument("--error-code", type=int, default=1033, help="Error code (default: 1033)")
    parser.add_argument("--html-file", default="cloudflare/error-pages/1033-enhanced.html",
                       help="HTML file path")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--slow-mo", type=int, default=1000, help="Slow motion delay in ms")

    args = parser.parse_args()

    # Get password (or skip for manual login)
    if args.manual_login:
        # Manual login mode (Google OAuth, etc.)
        email = None
        password = None
        print("🔐 Manual login mode enabled (for Google OAuth, SSO, etc.)")
    elif args.interactive and args.email:
        email = args.email
        password = getpass.getpass("Cloudflare password: ")
    elif args.password and args.email:
        email = args.email
        password = args.password
    else:
        # Default to manual login if no credentials provided
        email = None
        password = None
        print("🔐 No credentials provided - using manual login mode")

    # Validate HTML file exists
    if not Path(args.html_file).exists():
        print(f"❌ HTML file not found: {args.html_file}")
        sys.exit(1)

    print("🚀 Starting Cloudflare Dashboard automation...")
    print(f"🌐 Zone: {args.zone}")
    print(f"🔢 Error code: {args.error_code}")
    print(f"📄 HTML file: {args.html_file}")
    print(f"👁️ Headless: {args.headless}")
    if email:
        print(f"📧 Email: {email}")

    async with CloudflareDashboardAutomator(headless=args.headless, slow_mo=args.slow_mo) as automator:
        # Step 1: Login
        if not await automator.login(email, password):
            print("❌ Login failed")
            sys.exit(1)

        # Step 2: Navigate to zone
        if not await automator.navigate_to_zone(args.zone):
            print(f"❌ Failed to navigate to zone: {args.zone}")
            sys.exit(1)

        # Step 3: Navigate to Custom Error Pages
        if not await automator.navigate_to_custom_error_pages():
            print("❌ Failed to navigate to Custom Error Pages")
            print("💡 Ensure your Cloudflare plan supports Custom Error Pages (Pro or higher)")
            sys.exit(1)

        # Step 4: Deploy error page
        if not await automator.deploy_error_page(args.error_code, args.html_file):
            print("❌ Failed to deploy error page")
            sys.exit(1)

        # Step 5: Verify deployment
        if not await automator.verify_deployment(args.error_code):
            print("⚠️ Could not verify deployment")

        print("🎉 Automation completed successfully!")
        print("💡 Test the error page by temporarily stopping your tunnel")


if __name__ == "__main__":
    asyncio.run(main())