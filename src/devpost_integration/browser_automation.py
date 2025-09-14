#!/usr/bin/env python3
"""
DevPost Browser Automation
==========================

Browser automation implementation for DevPost integration using Playwright.
This replaces the mock API approach with actual web automation.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide browser automation for DevPost data extraction
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright.sync_api import sync_playwright, Browser as SyncBrowser, BrowserContext as SyncBrowserContext, Page as SyncPage

from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability

logger = logging.getLogger(__name__)


@dataclass
class DevPostHackathonData:
    """Data structure for extracted hackathon information."""
    title: str
    description: str
    deadline: str
    url: str
    requirements: List[str]
    prizes: List[str]
    sponsors: List[str]
    submission_guidelines: str
    extracted_at: datetime


@dataclass
class DevPostProjectData:
    """Data structure for extracted project information."""
    title: str
    description: str
    tags: List[str]
    team_members: List[str]
    github_url: str
    demo_url: str
    submission_url: str
    extracted_at: datetime


class DevPostBrowserAutomation(ReflectiveModule):
    """Browser automation for DevPost data extraction using Playwright."""

    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        super().__init__()
        self.module_id = "devpost_browser_automation"
        self.capabilities = [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
        self.dependencies = []
        
        # Browser configuration
        self.headless = headless
        self.browser_type = browser_type
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Sync browser for synchronous operations
        self.sync_browser: Optional[SyncBrowser] = None
        self.sync_context: Optional[SyncBrowserContext] = None
        self.sync_page: Optional[SyncPage] = None
        
        # Playwright instance
        self.playwright = None
        self.sync_playwright = None

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': self.module_id,
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': self.dependencies,
            'capabilities': [cap.value for cap in self.capabilities],
            'browser_type': self.browser_type,
            'headless': self.headless
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return self.capabilities

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        issues = []
        
        if not self.browser:
            issues.append("Browser not initialized")
        if not self.context:
            issues.append("Browser context not initialized")
        if not self.page:
            issues.append("Browser page not initialized")
            
        status = ModuleStatus.HEALTHY if not issues else ModuleStatus.DEGRADED
        health_score = 100.0 if not issues else 70.0
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now()
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        return {
            'success': True,
            'degraded_capabilities': [],
            'remaining_capabilities': [cap.value for cap in self.capabilities]
        }

    async def initialize_async(self) -> bool:
        """Initialize async browser automation."""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser based on type
            if self.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Create context with realistic user agent
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            # Create new page
            self.page = await self.context.new_page()
            
            logger.info(f"Browser automation initialized: {self.browser_type} (headless={self.headless})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize async browser automation: {e}")
            return False

    def initialize_sync(self) -> bool:
        """Initialize sync browser automation."""
        try:
            self.sync_playwright = sync_playwright().start()
            
            # Launch browser based on type
            if self.browser_type == "chromium":
                self.sync_browser = self.sync_playwright.chromium.launch(headless=self.headless)
            elif self.browser_type == "firefox":
                self.sync_browser = self.sync_playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.sync_browser = self.sync_playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Create context with realistic user agent
            self.sync_context = self.sync_browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            # Create new page
            self.sync_page = self.sync_context.new_page()
            
            logger.info(f"Sync browser automation initialized: {self.browser_type} (headless={self.headless})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize sync browser automation: {e}")
            return False

    async def extract_hackathon_data_async(self, hackathon_url: str) -> DevPostHackathonData:
        """Extract hackathon data using async browser automation."""
        if not self.page:
            await self.initialize_async()
        
        try:
            logger.info(f"Extracting hackathon data from: {hackathon_url}")
            
            # Navigate to hackathon page
            await self.page.goto(hackathon_url, wait_until="networkidle")
            
            # Wait for content to load
            await self.page.wait_for_selector("h1", timeout=10000)
            
            # Extract hackathon title
            title_element = await self.page.query_selector("h1")
            title = await title_element.text_content() if title_element else "Unknown Title"
            
            # Extract description
            description_element = await self.page.query_selector("[data-testid='hackathon-description'], .hackathon-description, .description")
            description = await description_element.text_content() if description_element else "No description available"
            
            # Extract deadline
            deadline_element = await self.page.query_selector("[data-testid='deadline'], .deadline, .submission-deadline")
            deadline = await deadline_element.text_content() if deadline_element else "No deadline found"
            
            # Extract requirements
            requirements = []
            req_elements = await self.page.query_selector_all("[data-testid='requirement'], .requirement, .submission-requirement")
            for element in req_elements:
                req_text = await element.text_content()
                if req_text:
                    requirements.append(req_text.strip())
            
            # Extract prizes
            prizes = []
            prize_elements = await self.page.query_selector_all("[data-testid='prize'], .prize, .award")
            for element in prize_elements:
                prize_text = await element.text_content()
                if prize_text:
                    prizes.append(prize_text.strip())
            
            # Extract sponsors
            sponsors = []
            sponsor_elements = await self.page.query_selector_all("[data-testid='sponsor'], .sponsor, .partner")
            for element in sponsor_elements:
                sponsor_text = await element.text_content()
                if sponsor_text:
                    sponsors.append(sponsor_text.strip())
            
            # Extract submission guidelines
            guidelines_element = await self.page.query_selector("[data-testid='guidelines'], .guidelines, .submission-guidelines")
            submission_guidelines = await guidelines_element.text_content() if guidelines_element else "No guidelines found"
            
            return DevPostHackathonData(
                title=title.strip(),
                description=description.strip(),
                deadline=deadline.strip(),
                url=hackathon_url,
                requirements=requirements,
                prizes=prizes,
                sponsors=sponsors,
                submission_guidelines=submission_guidelines.strip(),
                extracted_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to extract hackathon data: {e}")
            raise

    def extract_hackathon_data_sync(self, hackathon_url: str) -> DevPostHackathonData:
        """Extract hackathon data using sync browser automation."""
        if not self.sync_page:
            self.initialize_sync()
        
        try:
            logger.info(f"Extracting hackathon data from: {hackathon_url}")
            
            # Navigate to hackathon page
            self.sync_page.goto(hackathon_url, wait_until="networkidle")
            
            # Wait for content to load
            self.sync_page.wait_for_selector("h1", timeout=10000)
            
            # Extract hackathon title
            title_element = self.sync_page.query_selector("h1")
            title = title_element.text_content() if title_element else "Unknown Title"
            
            # Extract description
            description_element = self.sync_page.query_selector("[data-testid='hackathon-description'], .hackathon-description, .description")
            description = description_element.text_content() if description_element else "No description available"
            
            # Extract deadline
            deadline_element = self.sync_page.query_selector("[data-testid='deadline'], .deadline, .submission-deadline")
            deadline = deadline_element.text_content() if deadline_element else "No deadline found"
            
            # Extract requirements
            requirements = []
            req_elements = self.sync_page.query_selector_all("[data-testid='requirement'], .requirement, .submission-requirement")
            for element in req_elements:
                req_text = element.text_content()
                if req_text:
                    requirements.append(req_text.strip())
            
            # Extract prizes
            prizes = []
            prize_elements = self.sync_page.query_selector_all("[data-testid='prize'], .prize, .award")
            for element in prize_elements:
                prize_text = element.text_content()
                if prize_text:
                    prizes.append(prize_text.strip())
            
            # Extract sponsors
            sponsors = []
            sponsor_elements = self.sync_page.query_selector_all("[data-testid='sponsor'], .sponsor, .partner")
            for element in sponsor_elements:
                sponsor_text = element.text_content()
                if sponsor_text:
                    sponsors.append(sponsor_text.strip())
            
            # Extract submission guidelines
            guidelines_element = self.sync_page.query_selector("[data-testid='guidelines'], .guidelines, .submission-guidelines")
            submission_guidelines = guidelines_element.text_content() if guidelines_element else "No guidelines found"
            
            return DevPostHackathonData(
                title=title.strip(),
                description=description.strip(),
                deadline=deadline.strip(),
                url=hackathon_url,
                requirements=requirements,
                prizes=prizes,
                sponsors=sponsors,
                submission_guidelines=submission_guidelines.strip(),
                extracted_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to extract hackathon data: {e}")
            raise

    async def extract_project_data_async(self, project_url: str) -> DevPostProjectData:
        """Extract project data using async browser automation."""
        if not self.page:
            await self.initialize_async()
        
        try:
            logger.info(f"Extracting project data from: {project_url}")
            
            # Navigate to project page
            await self.page.goto(project_url, wait_until="networkidle")
            
            # Wait for content to load
            await self.page.wait_for_selector("h1", timeout=10000)
            
            # Extract project title
            title_element = await self.page.query_selector("h1")
            title = await title_element.text_content() if title_element else "Unknown Title"
            
            # Extract description
            description_element = await self.page.query_selector("[data-testid='project-description'], .project-description, .description")
            description = await description_element.text_content() if description_element else "No description available"
            
            # Extract tags
            tags = []
            tag_elements = await self.page.query_selector_all("[data-testid='tag'], .tag, .tech-stack")
            for element in tag_elements:
                tag_text = await element.text_content()
                if tag_text:
                    tags.append(tag_text.strip())
            
            # Extract team members
            team_members = []
            member_elements = await self.page.query_selector_all("[data-testid='team-member'], .team-member, .member")
            for element in member_elements:
                member_text = await element.text_content()
                if member_text:
                    team_members.append(member_text.strip())
            
            # Extract GitHub URL
            github_element = await self.page.query_selector("a[href*='github.com']")
            github_url = await github_element.get_attribute("href") if github_element else ""
            
            # Extract demo URL
            demo_element = await self.page.query_selector("a[href*='demo'], a[href*='video'], a[href*='youtube.com'], a[href*='vimeo.com']")
            demo_url = await demo_element.get_attribute("href") if demo_element else ""
            
            return DevPostProjectData(
                title=title.strip(),
                description=description.strip(),
                tags=tags,
                team_members=team_members,
                github_url=github_url,
                demo_url=demo_url,
                submission_url=project_url,
                extracted_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to extract project data: {e}")
            raise

    def extract_project_data_sync(self, project_url: str) -> DevPostProjectData:
        """Extract project data using sync browser automation."""
        if not self.sync_page:
            self.initialize_sync()
        
        try:
            logger.info(f"Extracting project data from: {project_url}")
            
            # Navigate to project page
            self.sync_page.goto(project_url, wait_until="networkidle")
            
            # Wait for content to load
            self.sync_page.wait_for_selector("h1", timeout=10000)
            
            # Extract project title
            title_element = self.sync_page.query_selector("h1")
            title = title_element.text_content() if title_element else "Unknown Title"
            
            # Extract description
            description_element = self.sync_page.query_selector("[data-testid='project-description'], .project-description, .description")
            description = description_element.text_content() if description_element else "No description available"
            
            # Extract tags
            tags = []
            tag_elements = self.sync_page.query_selector_all("[data-testid='tag'], .tag, .tech-stack")
            for element in tag_elements:
                tag_text = element.text_content()
                if tag_text:
                    tags.append(tag_text.strip())
            
            # Extract team members
            team_members = []
            member_elements = self.sync_page.query_selector_all("[data-testid='team-member'], .team-member, .member")
            for element in member_elements:
                member_text = element.text_content()
                if member_text:
                    team_members.append(member_text.strip())
            
            # Extract GitHub URL
            github_element = self.sync_page.query_selector("a[href*='github.com']")
            github_url = github_element.get_attribute("href") if github_element else ""
            
            # Extract demo URL
            demo_element = self.sync_page.query_selector("a[href*='demo'], a[href*='video'], a[href*='youtube.com'], a[href*='vimeo.com']")
            demo_url = demo_element.get_attribute("href") if demo_element else ""
            
            return DevPostProjectData(
                title=title.strip(),
                description=description.strip(),
                tags=tags,
                team_members=team_members,
                github_url=github_url,
                demo_url=demo_url,
                submission_url=project_url,
                extracted_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to extract project data: {e}")
            raise

    async def close_async(self):
        """Close async browser automation."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("Async browser automation closed")
        except Exception as e:
            logger.error(f"Error closing async browser automation: {e}")

    def close_sync(self):
        """Close sync browser automation."""
        try:
            if self.sync_page:
                self.sync_page.close()
            if self.sync_context:
                self.sync_context.close()
            if self.sync_browser:
                self.sync_browser.close()
            if self.sync_playwright:
                self.sync_playwright.stop()
            
            logger.info("Sync browser automation closed")
        except Exception as e:
            logger.error(f"Error closing sync browser automation: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.initialize_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_sync()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_async()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_async()
