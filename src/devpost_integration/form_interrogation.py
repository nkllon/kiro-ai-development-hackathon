#!/usr/bin/env python3
"""
DevPost Form Interrogation System
=================================

Interrogates DevPost submission forms to build a comprehensive model
of required fields and current data. Designed for human-in-the-middle
authentication scenarios.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Extract form structure and data from authenticated DevPost pages
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright.sync_api import sync_playwright, Browser as SyncBrowser, BrowserContext as SyncBrowserContext, Page as SyncPage

from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability

logger = logging.getLogger(__name__)


@dataclass
class FormField:
    """Represents a form field in the DevPost submission."""
    name: str
    field_type: str  # text, textarea, select, checkbox, radio, file, etc.
    label: str
    placeholder: str = ""
    required: bool = False
    current_value: str = ""
    options: List[str] = field(default_factory=list)  # For select/radio fields
    validation_rules: List[str] = field(default_factory=list)
    help_text: str = ""
    section: str = ""  # Which section of the form this belongs to


@dataclass
class FormSection:
    """Represents a section of the DevPost submission form."""
    name: str
    title: str
    description: str = ""
    fields: List[FormField] = field(default_factory=list)
    order: int = 0
    required: bool = True


@dataclass
class DevPostSubmissionModel:
    """Complete model of the DevPost submission form."""
    hackathon_id: str
    hackathon_title: str
    submission_url: str
    sections: List[FormSection] = field(default_factory=list)
    all_fields: List[FormField] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)
    form_metadata: Dict[str, Any] = field(default_factory=dict)


class DevPostFormInterrogation(ReflectiveModule):
    """Form interrogation system for DevPost submission pages."""

    def __init__(self, headless: bool = False, browser_type: str = "chromium"):
        super().__init__()
        self.module_id = "devpost_form_interrogation"
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
            
            logger.info(f"Form interrogation browser initialized: {self.browser_type} (headless={self.headless})")
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
            
            logger.info(f"Sync form interrogation browser initialized: {self.browser_type} (headless={self.headless})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize sync browser automation: {e}")
            return False

    async def interrogate_submission_form_async(self, submission_url: str) -> DevPostSubmissionModel:
        """Interrogate the DevPost submission form to build a complete model."""
        if not self.page:
            await self.initialize_async()
        
        try:
            logger.info(f"Interrogating submission form at: {submission_url}")
            
            # Navigate to submission page
            await self.page.goto(submission_url, wait_until="networkidle")
            
            # Wait for page to load - try multiple selectors
            form_selectors = [
                "form",
                "[data-testid='submission-form']",
                ".submission-form",
                ".form",
                "form[action*='submit']",
                "form[action*='submission']",
                ".step",
                ".page",
                ".section"
            ]
            
            form_found = False
            for selector in form_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    form_found = True
                    logger.info(f"Found form using selector: {selector}")
                    break
                except:
                    continue
            
            if not form_found:
                logger.warning("No form element found, proceeding with page analysis")
                # Take a screenshot for debugging
                await self.page.screenshot(path="devpost_page_debug.png")
                logger.info("Screenshot saved as devpost_page_debug.png")
            
            # Extract hackathon information
            hackathon_title = await self.extract_hackathon_title()
            hackathon_id = await self.extract_hackathon_id()
            
            # Extract form sections and fields
            sections = await self.extract_form_sections()
            
            # Build complete model
            model = DevPostSubmissionModel(
                hackathon_id=hackathon_id,
                hackathon_title=hackathon_title,
                submission_url=submission_url,
                sections=sections,
                all_fields=[field for section in sections for field in section.fields],
                extracted_at=datetime.now()
            )
            
            # Extract form metadata
            model.form_metadata = await self.extract_form_metadata()
            
            logger.info(f"Form interrogation complete: {len(sections)} sections, {len(model.all_fields)} fields")
            return model
            
        except Exception as e:
            logger.error(f"Failed to interrogate submission form: {e}")
            raise

    def interrogate_submission_form_sync(self, submission_url: str) -> DevPostSubmissionModel:
        """Interrogate the DevPost submission form to build a complete model (sync)."""
        if not self.sync_page:
            self.initialize_sync()
        
        try:
            logger.info(f"Interrogating submission form at: {submission_url}")
            
            # Navigate to submission page
            self.sync_page.goto(submission_url, wait_until="networkidle")
            
            # Wait for page to load - try multiple selectors
            form_selectors = [
                "form",
                "[data-testid='submission-form']",
                ".submission-form",
                ".form",
                "form[action*='submit']",
                "form[action*='submission']",
                ".step",
                ".page",
                ".section"
            ]
            
            form_found = False
            for selector in form_selectors:
                try:
                    self.sync_page.wait_for_selector(selector, timeout=5000)
                    form_found = True
                    logger.info(f"Found form using selector: {selector}")
                    break
                except:
                    continue
            
            if not form_found:
                logger.warning("No form element found, proceeding with page analysis")
                # Take a screenshot for debugging
                self.sync_page.screenshot(path="devpost_page_debug.png")
                logger.info("Screenshot saved as devpost_page_debug.png")
            
            # Extract hackathon information
            hackathon_title = self.extract_hackathon_title_sync()
            hackathon_id = self.extract_hackathon_id_sync()
            
            # Extract form sections and fields
            sections = self.extract_form_sections_sync()
            
            # Build complete model
            model = DevPostSubmissionModel(
                hackathon_id=hackathon_id,
                hackathon_title=hackathon_title,
                submission_url=submission_url,
                sections=sections,
                all_fields=[field for section in sections for field in section.fields],
                extracted_at=datetime.now()
            )
            
            # Extract form metadata
            model.form_metadata = self.extract_form_metadata_sync()
            
            logger.info(f"Form interrogation complete: {len(sections)} sections, {len(model.all_fields)} fields")
            return model
            
        except Exception as e:
            logger.error(f"Failed to interrogate submission form: {e}")
            raise

    async def extract_hackathon_title(self) -> str:
        """Extract hackathon title from the page."""
        try:
            # Try multiple selectors for hackathon title
            selectors = [
                "h1",
                "[data-testid='hackathon-title']",
                ".hackathon-title",
                ".challenge-title",
                "title"
            ]
            
            for selector in selectors:
                element = await self.page.query_selector(selector)
                if element:
                    title = await element.text_content()
                    if title and title.strip():
                        return title.strip()
            
            return "Unknown Hackathon"
            
        except Exception as e:
            logger.warning(f"Failed to extract hackathon title: {e}")
            return "Unknown Hackathon"

    def extract_hackathon_title_sync(self) -> str:
        """Extract hackathon title from the page (sync)."""
        try:
            # Try multiple selectors for hackathon title
            selectors = [
                "h1",
                "[data-testid='hackathon-title']",
                ".hackathon-title",
                ".challenge-title",
                "title"
            ]
            
            for selector in selectors:
                element = self.sync_page.query_selector(selector)
                if element:
                    title = element.text_content()
                    if title and title.strip():
                        return title.strip()
            
            return "Unknown Hackathon"
            
        except Exception as e:
            logger.warning(f"Failed to extract hackathon title: {e}")
            return "Unknown Hackathon"

    async def extract_hackathon_id(self) -> str:
        """Extract hackathon ID from the page."""
        try:
            # Try to extract from URL or page data
            url = self.page.url
            if "/hackathons/" in url:
                parts = url.split("/hackathons/")
                if len(parts) > 1:
                    hackathon_id = parts[1].split("/")[0]
                    return hackathon_id
            
            # Try to find in page data
            hackathon_id_element = await self.page.query_selector("[data-hackathon-id]")
            if hackathon_id_element:
                return await hackathon_id_element.get_attribute("data-hackathon-id")
            
            return "unknown"
            
        except Exception as e:
            logger.warning(f"Failed to extract hackathon ID: {e}")
            return "unknown"

    def extract_hackathon_id_sync(self) -> str:
        """Extract hackathon ID from the page (sync)."""
        try:
            # Try to extract from URL or page data
            url = self.sync_page.url
            if "/hackathons/" in url:
                parts = url.split("/hackathons/")
                if len(parts) > 1:
                    hackathon_id = parts[1].split("/")[0]
                    return hackathon_id
            
            # Try to find in page data
            hackathon_id_element = self.sync_page.query_selector("[data-hackathon-id]")
            if hackathon_id_element:
                return hackathon_id_element.get_attribute("data-hackathon-id")
            
            return "unknown"
            
        except Exception as e:
            logger.warning(f"Failed to extract hackathon ID: {e}")
            return "unknown"

    async def extract_form_sections(self) -> List[FormSection]:
        """Extract form sections and their fields."""
        sections = []
        
        try:
            # Find form sections - look for common patterns
            section_selectors = [
                ".form-section",
                ".section",
                ".step",
                ".page",
                ".tab-content",
                "fieldset",
                "[data-section]",
                ".submission-step",
                ".form-step",
                ".wizard-step",
                ".panel",
                ".card",
                ".container"
            ]
            
            section_elements = []
            for selector in section_selectors:
                elements = await self.page.query_selector_all(selector)
                section_elements.extend(elements)
            
            # If no explicit sections found, look for any container with form elements
            if not section_elements:
                # Look for containers that might have form elements
                container_selectors = [
                    "main",
                    ".main-content",
                    ".content",
                    ".submission-content",
                    ".form-container",
                    "div[class*='form']",
                    "div[class*='step']",
                    "div[class*='section']"
                ]
                
                for selector in container_selectors:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        # Check if this container has form elements
                        has_form_elements = await element.query_selector("input, textarea, select, button[type='submit']")
                        if has_form_elements:
                            section_elements.append(element)
            
            # If still no sections found, treat the entire page as one section
            if not section_elements:
                section_elements = [self.page]
            
            for i, section_element in enumerate(section_elements):
                section_name = f"section_{i+1}"
                section_title = await self.extract_section_title(section_element)
                section_description = await self.extract_section_description(section_element)
                
                # Extract fields from this section
                fields = await self.extract_fields_from_section(section_element, section_name)
                
                section = FormSection(
                    name=section_name,
                    title=section_title,
                    description=section_description,
                    fields=fields,
                    order=i,
                    required=True
                )
                
                sections.append(section)
            
            return sections
            
        except Exception as e:
            logger.error(f"Failed to extract form sections: {e}")
            return []

    def extract_form_sections_sync(self) -> List[FormSection]:
        """Extract form sections and their fields (sync)."""
        sections = []
        
        try:
            # Find form sections - look for common patterns
            section_selectors = [
                ".form-section",
                ".section",
                ".step",
                ".page",
                ".tab-content",
                "fieldset",
                "[data-section]",
                ".submission-step",
                ".form-step",
                ".wizard-step",
                ".panel",
                ".card",
                ".container"
            ]
            
            section_elements = []
            for selector in section_selectors:
                elements = self.sync_page.query_selector_all(selector)
                section_elements.extend(elements)
            
            # If no explicit sections found, look for any container with form elements
            if not section_elements:
                # Look for containers that might have form elements
                container_selectors = [
                    "main",
                    ".main-content",
                    ".content",
                    ".submission-content",
                    ".form-container",
                    "div[class*='form']",
                    "div[class*='step']",
                    "div[class*='section']"
                ]
                
                for selector in container_selectors:
                    elements = self.sync_page.query_selector_all(selector)
                    for element in elements:
                        # Check if this container has form elements
                        has_form_elements = element.query_selector("input, textarea, select, button[type='submit']")
                        if has_form_elements:
                            section_elements.append(element)
            
            # If still no sections found, treat the entire page as one section
            if not section_elements:
                section_elements = [self.sync_page]
            
            for i, section_element in enumerate(section_elements):
                section_name = f"section_{i+1}"
                section_title = self.extract_section_title_sync(section_element)
                section_description = self.extract_section_description_sync(section_element)
                
                # Extract fields from this section
                fields = self.extract_fields_from_section_sync(section_element, section_name)
                
                section = FormSection(
                    name=section_name,
                    title=section_title,
                    description=section_description,
                    fields=fields,
                    order=i,
                    required=True
                )
                
                sections.append(section)
            
            return sections
            
        except Exception as e:
            logger.error(f"Failed to extract form sections: {e}")
            return []

    async def extract_section_title(self, section_element) -> str:
        """Extract title from a section element."""
        try:
            # Look for title elements within the section
            title_selectors = ["h1", "h2", "h3", ".title", ".section-title", "legend"]
            
            for selector in title_selectors:
                title_element = await section_element.query_selector(selector)
                if title_element:
                    title = await title_element.text_content()
                    if title and title.strip():
                        return title.strip()
            
            return "Untitled Section"
            
        except Exception as e:
            logger.warning(f"Failed to extract section title: {e}")
            return "Untitled Section"

    def extract_section_title_sync(self, section_element) -> str:
        """Extract title from a section element (sync)."""
        try:
            # Look for title elements within the section
            title_selectors = ["h1", "h2", "h3", ".title", ".section-title", "legend"]
            
            for selector in title_selectors:
                title_element = section_element.query_selector(selector)
                if title_element:
                    title = title_element.text_content()
                    if title and title.strip():
                        return title.strip()
            
            return "Untitled Section"
            
        except Exception as e:
            logger.warning(f"Failed to extract section title: {e}")
            return "Untitled Section"

    async def extract_section_description(self, section_element) -> str:
        """Extract description from a section element."""
        try:
            # Look for description elements
            desc_selectors = [".description", ".help-text", ".section-description", "p"]
            
            for selector in desc_selectors:
                desc_element = await section_element.query_selector(selector)
                if desc_element:
                    desc = await desc_element.text_content()
                    if desc and desc.strip():
                        return desc.strip()
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract section description: {e}")
            return ""

    def extract_section_description_sync(self, section_element) -> str:
        """Extract description from a section element (sync)."""
        try:
            # Look for description elements
            desc_selectors = [".description", ".help-text", ".section-description", "p"]
            
            for selector in desc_selectors:
                desc_element = section_element.query_selector(selector)
                if desc_element:
                    desc = desc_element.text_content()
                    if desc and desc.strip():
                        return desc.strip()
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract section description: {e}")
            return ""

    async def extract_fields_from_section(self, section_element, section_name: str) -> List[FormField]:
        """Extract form fields from a section element."""
        fields = []
        
        try:
            # Find all input elements in the section
            input_selectors = [
                "input[type='text']",
                "input[type='email']",
                "input[type='url']",
                "input[type='tel']",
                "input[type='number']",
                "input[type='date']",
                "input[type='time']",
                "input[type='datetime-local']",
                "input[type='password']",
                "input[type='hidden']",
                "input[type='checkbox']",
                "input[type='radio']",
                "input[type='file']",
                "textarea",
                "select"
            ]
            
            for selector in input_selectors:
                elements = await section_element.query_selector_all(selector)
                for element in elements:
                    field = await self.extract_field_info(element, section_name)
                    if field:
                        fields.append(field)
            
            return fields
            
        except Exception as e:
            logger.error(f"Failed to extract fields from section: {e}")
            return []

    def extract_fields_from_section_sync(self, section_element, section_name: str) -> List[FormField]:
        """Extract form fields from a section element (sync)."""
        fields = []
        
        try:
            # Find all input elements in the section
            input_selectors = [
                "input[type='text']",
                "input[type='email']",
                "input[type='url']",
                "input[type='tel']",
                "input[type='number']",
                "input[type='date']",
                "input[type='time']",
                "input[type='datetime-local']",
                "input[type='password']",
                "input[type='hidden']",
                "input[type='checkbox']",
                "input[type='radio']",
                "input[type='file']",
                "textarea",
                "select"
            ]
            
            for selector in input_selectors:
                elements = section_element.query_selector_all(selector)
                for element in elements:
                    field = self.extract_field_info_sync(element, section_name)
                    if field:
                        fields.append(field)
            
            return fields
            
        except Exception as e:
            logger.error(f"Failed to extract fields from section: {e}")
            return []

    async def extract_field_info(self, element, section_name: str) -> Optional[FormField]:
        """Extract information about a form field."""
        try:
            # Get basic field information
            field_name = await element.get_attribute("name") or await element.get_attribute("id") or "unnamed_field"
            field_type = await element.get_attribute("type") or element.tag_name.lower()
            placeholder = await element.get_attribute("placeholder") or ""
            required = await element.get_attribute("required") is not None
            current_value = await element.get_attribute("value") or ""
            
            # Get label
            label = await self.extract_field_label(element)
            
            # Get options for select/radio fields
            options = []
            if field_type in ["select", "radio"]:
                options = await self.extract_field_options(element)
            
            # Get validation rules
            validation_rules = await self.extract_validation_rules(element)
            
            # Get help text
            help_text = await self.extract_field_help_text(element)
            
            return FormField(
                name=field_name,
                field_type=field_type,
                label=label,
                placeholder=placeholder,
                required=required,
                current_value=current_value,
                options=options,
                validation_rules=validation_rules,
                help_text=help_text,
                section=section_name
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract field info: {e}")
            return None

    def extract_field_info_sync(self, element, section_name: str) -> Optional[FormField]:
        """Extract information about a form field (sync)."""
        try:
            # Get basic field information
            field_name = element.get_attribute("name") or element.get_attribute("id") or "unnamed_field"
            field_type = element.get_attribute("type") or element.tag_name.lower()
            placeholder = element.get_attribute("placeholder") or ""
            required = element.get_attribute("required") is not None
            current_value = element.get_attribute("value") or ""
            
            # Get label
            label = self.extract_field_label_sync(element)
            
            # Get options for select/radio fields
            options = []
            if field_type in ["select", "radio"]:
                options = self.extract_field_options_sync(element)
            
            # Get validation rules
            validation_rules = self.extract_validation_rules_sync(element)
            
            # Get help text
            help_text = self.extract_field_help_text_sync(element)
            
            return FormField(
                name=field_name,
                field_type=field_type,
                label=label,
                placeholder=placeholder,
                required=required,
                current_value=current_value,
                options=options,
                validation_rules=validation_rules,
                help_text=help_text,
                section=section_name
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract field info: {e}")
            return None

    async def extract_field_label(self, element) -> str:
        """Extract label for a form field."""
        try:
            # Try to find associated label
            field_id = await element.get_attribute("id")
            if field_id:
                label_element = await self.page.query_selector(f"label[for='{field_id}']")
                if label_element:
                    label_text = await label_element.text_content()
                    if label_text and label_text.strip():
                        return label_text.strip()
            
            # Look for nearby text that might be a label
            parent = await element.query_selector("xpath=..")
            if parent:
                # Look for text nodes or label elements in parent
                text_content = await parent.text_content()
                if text_content:
                    # Simple heuristic: take the first line of text
                    lines = text_content.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) < 100:  # Reasonable label length
                            return line
            
            return "Unlabeled Field"
            
        except Exception as e:
            logger.warning(f"Failed to extract field label: {e}")
            return "Unlabeled Field"

    def extract_field_label_sync(self, element) -> str:
        """Extract label for a form field (sync)."""
        try:
            # Try to find associated label
            field_id = element.get_attribute("id")
            if field_id:
                label_element = self.sync_page.query_selector(f"label[for='{field_id}']")
                if label_element:
                    label_text = label_element.text_content()
                    if label_text and label_text.strip():
                        return label_text.strip()
            
            # Look for nearby text that might be a label
            parent = element.query_selector("xpath=..")
            if parent:
                # Look for text nodes or label elements in parent
                text_content = parent.text_content()
                if text_content:
                    # Simple heuristic: take the first line of text
                    lines = text_content.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) < 100:  # Reasonable label length
                            return line
            
            return "Unlabeled Field"
            
        except Exception as e:
            logger.warning(f"Failed to extract field label: {e}")
            return "Unlabeled Field"

    async def extract_field_options(self, element) -> List[str]:
        """Extract options for select/radio fields."""
        try:
            options = []
            
            if element.tag_name.lower() == "select":
                option_elements = await element.query_selector_all("option")
                for option in option_elements:
                    option_text = await option.text_content()
                    if option_text and option_text.strip():
                        options.append(option_text.strip())
            elif element.get_attribute("type") == "radio":
                # Find all radio buttons with the same name
                name = await element.get_attribute("name")
                if name:
                    radio_elements = await self.page.query_selector_all(f"input[type='radio'][name='{name}']")
                    for radio in radio_elements:
                        # Look for associated label or value
                        radio_id = await radio.get_attribute("id")
                        if radio_id:
                            label_element = await self.page.query_selector(f"label[for='{radio_id}']")
                            if label_element:
                                label_text = await label_element.text_content()
                                if label_text and label_text.strip():
                                    options.append(label_text.strip())
            
            return options
            
        except Exception as e:
            logger.warning(f"Failed to extract field options: {e}")
            return []

    def extract_field_options_sync(self, element) -> List[str]:
        """Extract options for select/radio fields (sync)."""
        try:
            options = []
            
            if element.tag_name.lower() == "select":
                option_elements = element.query_selector_all("option")
                for option in option_elements:
                    option_text = option.text_content()
                    if option_text and option_text.strip():
                        options.append(option_text.strip())
            elif element.get_attribute("type") == "radio":
                # Find all radio buttons with the same name
                name = element.get_attribute("name")
                if name:
                    radio_elements = self.sync_page.query_selector_all(f"input[type='radio'][name='{name}']")
                    for radio in radio_elements:
                        # Look for associated label or value
                        radio_id = radio.get_attribute("id")
                        if radio_id:
                            label_element = self.sync_page.query_selector(f"label[for='{radio_id}']")
                            if label_element:
                                label_text = label_element.text_content()
                                if label_text and label_text.strip():
                                    options.append(label_text.strip())
            
            return options
            
        except Exception as e:
            logger.warning(f"Failed to extract field options: {e}")
            return []

    async def extract_validation_rules(self, element) -> List[str]:
        """Extract validation rules for a field."""
        try:
            rules = []
            
            # Check for HTML5 validation attributes
            if await element.get_attribute("required"):
                rules.append("required")
            if await element.get_attribute("minlength"):
                rules.append(f"minlength:{await element.get_attribute('minlength')}")
            if await element.get_attribute("maxlength"):
                rules.append(f"maxlength:{await element.get_attribute('maxlength')}")
            if await element.get_attribute("min"):
                rules.append(f"min:{await element.get_attribute('min')}")
            if await element.get_attribute("max"):
                rules.append(f"max:{await element.get_attribute('max')}")
            if await element.get_attribute("pattern"):
                rules.append(f"pattern:{await element.get_attribute('pattern')}")
            
            return rules
            
        except Exception as e:
            logger.warning(f"Failed to extract validation rules: {e}")
            return []

    def extract_validation_rules_sync(self, element) -> List[str]:
        """Extract validation rules for a field (sync)."""
        try:
            rules = []
            
            # Check for HTML5 validation attributes
            if element.get_attribute("required"):
                rules.append("required")
            if element.get_attribute("minlength"):
                rules.append(f"minlength:{element.get_attribute('minlength')}")
            if element.get_attribute("maxlength"):
                rules.append(f"maxlength:{element.get_attribute('maxlength')}")
            if element.get_attribute("min"):
                rules.append(f"min:{element.get_attribute('min')}")
            if element.get_attribute("max"):
                rules.append(f"max:{element.get_attribute('max')}")
            if element.get_attribute("pattern"):
                rules.append(f"pattern:{element.get_attribute('pattern')}")
            
            return rules
            
        except Exception as e:
            logger.warning(f"Failed to extract validation rules: {e}")
            return []

    async def extract_field_help_text(self, element) -> str:
        """Extract help text for a field."""
        try:
            # Look for help text elements
            help_selectors = [".help-text", ".field-help", ".description", ".hint"]
            
            for selector in help_selectors:
                help_element = await element.query_selector(selector)
                if help_element:
                    help_text = await help_element.text_content()
                    if help_text and help_text.strip():
                        return help_text.strip()
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract field help text: {e}")
            return ""

    def extract_field_help_text_sync(self, element) -> str:
        """Extract help text for a field (sync)."""
        try:
            # Look for help text elements
            help_selectors = [".help-text", ".field-help", ".description", ".hint"]
            
            for selector in help_selectors:
                help_element = element.query_selector(selector)
                if help_element:
                    help_text = help_element.text_content()
                    if help_text and help_text.strip():
                        return help_text.strip()
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract field help text: {e}")
            return ""

    async def extract_form_metadata(self) -> Dict[str, Any]:
        """Extract additional form metadata."""
        try:
            metadata = {
                "form_action": await self.page.get_attribute("form", "action"),
                "form_method": await self.page.get_attribute("form", "method"),
                "form_enctype": await self.page.get_attribute("form", "enctype"),
                "page_title": await self.page.title(),
                "page_url": self.page.url,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to extract form metadata: {e}")
            return {}

    def extract_form_metadata_sync(self) -> Dict[str, Any]:
        """Extract additional form metadata (sync)."""
        try:
            metadata = {
                "form_action": self.sync_page.get_attribute("form", "action"),
                "form_method": self.sync_page.get_attribute("form", "method"),
                "form_enctype": self.sync_page.get_attribute("form", "enctype"),
                "page_title": self.sync_page.title(),
                "page_url": self.sync_page.url,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to extract form metadata: {e}")
            return {}

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
            
            logger.info("Async form interrogation browser closed")
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
            
            logger.info("Sync form interrogation browser closed")
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
