#!/usr/bin/env python3
"""
DevPost Hybrid Integration
==========================

Hybrid integration combining browser automation and web scraping.
Implements the fallback strategy: Playwright -> Web Scraping.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide hybrid DevPost data extraction with fallback strategies
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability
from .browser_automation import DevPostBrowserAutomation, DevPostHackathonData, DevPostProjectData
from .web_scraping import DevPostWebScraping

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of data extraction attempt."""
    success: bool
    data: Optional[Union[DevPostHackathonData, DevPostProjectData]]
    method_used: str
    error: Optional[str] = None
    extracted_at: datetime = None

    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now()


class DevPostHybridIntegration(ReflectiveModule):
    """Hybrid integration combining browser automation and web scraping."""

    def __init__(self, headless: bool = True, browser_type: str = "chromium", 
                 rate_limit_delay: float = 1.0, max_retries: int = 3):
        super().__init__()
        self.module_id = "devpost_hybrid_integration"
        self.capabilities = [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
        self.dependencies = []
        
        # Initialize components
        self.browser_automation = DevPostBrowserAutomation(
            headless=headless, 
            browser_type=browser_type
        )
        self.web_scraping = DevPostWebScraping(
            rate_limit_delay=rate_limit_delay,
            max_retries=max_retries
        )
        
        # Configuration
        self.headless = headless
        self.browser_type = browser_type
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': self.module_id,
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': self.dependencies,
            'capabilities': [cap.value for cap in self.capabilities],
            'browser_type': self.browser_type,
            'headless': self.headless,
            'rate_limit_delay': self.rate_limit_delay,
            'max_retries': self.max_retries
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return self.capabilities

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        browser_health = self.browser_automation.get_health_status()
        scraping_health = self.web_scraping.get_health_status()
        
        # Overall health is the minimum of component healths
        overall_health_score = min(browser_health.health_score, scraping_health.health_score)
        overall_status = ModuleStatus.HEALTHY if overall_health_score >= 90 else ModuleStatus.DEGRADED
        
        # Combine issues
        all_issues = browser_health.issues + scraping_health.issues
        
        return ModuleHealth(
            module_id=self.module_id,
            status=overall_status,
            health_score=overall_health_score,
            issues=all_issues,
            last_check=datetime.now()
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        return {
            'success': True,
            'degraded_capabilities': [],
            'remaining_capabilities': [cap.value for cap in self.capabilities]
        }

    async def extract_hackathon_data_async(self, hackathon_url: str) -> ExtractionResult:
        """Extract hackathon data using hybrid approach (async)."""
        logger.info(f"Starting hybrid hackathon data extraction from: {hackathon_url}")
        
        # Try browser automation first
        try:
            logger.info("Attempting browser automation extraction...")
            data = await self.browser_automation.extract_hackathon_data_async(hackathon_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="browser_automation_async"
            )
        except Exception as e:
            logger.warning(f"Browser automation failed: {e}")
        
        # Fallback to web scraping
        try:
            logger.info("Attempting web scraping extraction...")
            data = self.web_scraping.extract_hackathon_data(hackathon_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="web_scraping"
            )
        except Exception as e:
            logger.error(f"Web scraping also failed: {e}")
            return ExtractionResult(
                success=False,
                data=None,
                method_used="none",
                error=str(e)
            )

    def extract_hackathon_data_sync(self, hackathon_url: str) -> ExtractionResult:
        """Extract hackathon data using hybrid approach (sync)."""
        logger.info(f"Starting hybrid hackathon data extraction from: {hackathon_url}")
        
        # Try browser automation first
        try:
            logger.info("Attempting browser automation extraction...")
            data = self.browser_automation.extract_hackathon_data_sync(hackathon_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="browser_automation_sync"
            )
        except Exception as e:
            logger.warning(f"Browser automation failed: {e}")
        
        # Fallback to web scraping
        try:
            logger.info("Attempting web scraping extraction...")
            data = self.web_scraping.extract_hackathon_data(hackathon_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="web_scraping"
            )
        except Exception as e:
            logger.error(f"Web scraping also failed: {e}")
            return ExtractionResult(
                success=False,
                data=None,
                method_used="none",
                error=str(e)
            )

    async def extract_project_data_async(self, project_url: str) -> ExtractionResult:
        """Extract project data using hybrid approach (async)."""
        logger.info(f"Starting hybrid project data extraction from: {project_url}")
        
        # Try browser automation first
        try:
            logger.info("Attempting browser automation extraction...")
            data = await self.browser_automation.extract_project_data_async(project_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="browser_automation_async"
            )
        except Exception as e:
            logger.warning(f"Browser automation failed: {e}")
        
        # Fallback to web scraping
        try:
            logger.info("Attempting web scraping extraction...")
            data = self.web_scraping.extract_project_data(project_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="web_scraping"
            )
        except Exception as e:
            logger.error(f"Web scraping also failed: {e}")
            return ExtractionResult(
                success=False,
                data=None,
                method_used="none",
                error=str(e)
            )

    def extract_project_data_sync(self, project_url: str) -> ExtractionResult:
        """Extract project data using hybrid approach (sync)."""
        logger.info(f"Starting hybrid project data extraction from: {project_url}")
        
        # Try browser automation first
        try:
            logger.info("Attempting browser automation extraction...")
            data = self.browser_automation.extract_project_data_sync(project_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="browser_automation_sync"
            )
        except Exception as e:
            logger.warning(f"Browser automation failed: {e}")
        
        # Fallback to web scraping
        try:
            logger.info("Attempting web scraping extraction...")
            data = self.web_scraping.extract_project_data(project_url)
            return ExtractionResult(
                success=True,
                data=data,
                method_used="web_scraping"
            )
        except Exception as e:
            logger.error(f"Web scraping also failed: {e}")
            return ExtractionResult(
                success=False,
                data=None,
                method_used="none",
                error=str(e)
            )

    def search_hackathons(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Search for hackathons using web scraping (browser automation doesn't support search)."""
        try:
            logger.info(f"Searching for hackathons with query: {query}")
            return self.web_scraping.search_hackathons(query=query, limit=limit)
        except Exception as e:
            logger.error(f"Failed to search hackathons: {e}")
            raise

    async def close_async(self):
        """Close async components."""
        try:
            await self.browser_automation.close_async()
            self.web_scraping.close()
            logger.info("Hybrid integration closed (async)")
        except Exception as e:
            logger.error(f"Error closing hybrid integration: {e}")

    def close_sync(self):
        """Close sync components."""
        try:
            self.browser_automation.close_sync()
            self.web_scraping.close()
            logger.info("Hybrid integration closed (sync)")
        except Exception as e:
            logger.error(f"Error closing hybrid integration: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_sync()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_async()
