#!/usr/bin/env python3
"""
🎯 CURIOUS PAGE ANALYZER MODULE
==============================
Page analysis and learning for Learning MVC System.
Extracted from learning_mvc_system.py for better organization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

import re
import time
from typing import Any, Dict, List

from playwright.sync_api import Page

from .learning_state import LearningState
from .page_types import PageType
from .telemetry import PageAnalysis, TelemetryEvent


class CuriousPageAnalyzer:
    """Curious page analyzer that learns from HTML and visual elements."""

    def __init__(self, page: Page, telemetry):
        self.page = page
        self.telemetry = telemetry
        self.learning_state = LearningState(
            total_pages_analyzed=0,
            successful_navigations=0,
            failed_navigations=0,
            discovered_patterns={},
            learned_selectors={},
            page_type_patterns={},
            button_patterns={},
            form_patterns={},
        )

    def analyze_page(self) -> PageAnalysis:
        """Perform comprehensive page analysis with curiosity."""
        print("\n🔍 Curiously analyzing page...")
        print(f"URL: {self.page.url}")
        print(f"Title: {self.page.title()}")
        try:
            # Basic page info
            url = self.page.url
            title = self.page.title()
            # Get HTML content for analysis
            html_content = self.page.content()
            html_length = len(html_content)
            # Count elements
            form_count = len(self.page.query_selector_all("form"))
            button_count = len(
                self.page.query_selector_all(
                    "button, input[type='button'], input[type='submit']"
                )
            )
            input_count = len(self.page.query_selector_all("input, textarea, select"))
            link_count = len(self.page.query_selector_all("a"))
            image_count = len(self.page.query_selector_all("img"))
            # Analyze page type heuristically
            page_type = self._heuristically_detect_page_type(url, title, html_content)
            # Find status indicators
            status_indicators = self._find_status_indicators()
            # Find navigation elements
            navigation_elements = self._find_navigation_elements()
            # Find interactive elements
            interactive_elements = self._find_interactive_elements()
            # Extract text content
            text_content = self.page.text_content("body")[:1000]  # First 1000 chars
            # Extract meta information
            meta_info = self._extract_meta_info()
            analysis = PageAnalysis(
                url=url,
                title=title,
                page_type=page_type,
                html_length=html_length,
                form_count=form_count,
                button_count=button_count,
                input_count=input_count,
                link_count=link_count,
                image_count=image_count,
                status_indicators=status_indicators,
                navigation_elements=navigation_elements,
                interactive_elements=interactive_elements,
                text_content=text_content,
                meta_info=meta_info,
                analysis_timestamp=time.time(),
            )
            # Log telemetry
            self.telemetry.log_event(
                "page_analysis",
                self.page,
                {
                    "page_type": page_type.value,
                    "element_counts": {
                        "forms": form_count,
                        "buttons": button_count,
                        "inputs": input_count,
                        "links": link_count,
                        "images": image_count,
                    },
                    "status_indicators": len(status_indicators),
                    "navigation_elements": len(navigation_elements),
                    "interactive_elements": len(interactive_elements),
                },
            )
            # Update learning state
            self.learning_state.total_pages_analyzed += 1
            self._learn_from_analysis(analysis)
            # Display findings with curiosity
            self._display_curious_findings(analysis)
            return analysis
        except Exception as e:
            self.telemetry.log_event("page_analysis", self.page, {}, False, str(e))
            raise

    def _heuristically_detect_page_type(
        self, url: str, title: str, html_content: str
    ) -> PageType:
        """Heuristically detect page type from multiple signals."""
        # URL patterns
        if "login" in url.lower() or "signin" in url.lower():
            return PageType.LOGIN
        if "auth" in url.lower() or "authenticate" in url.lower():
            return PageType.AUTHENTICATION
        if "project" in url.lower() and "overview" in url.lower():
            return PageType.PROJECT_OVERVIEW
        if "project" in url.lower() and "detail" in url.lower():
            return PageType.PROJECT_DETAILS
        if "submit" in url.lower() or "submission" in url.lower():
            return PageType.SUBMISSION
        if "dashboard" in url.lower():
            return PageType.DASHBOARD
        if "error" in url.lower() or "404" in url.lower():
            return PageType.ERROR
        if "loading" in url.lower() or "spinner" in html_content.lower():
            return PageType.LOADING
        # Title patterns
        if "login" in title.lower() or "sign in" in title.lower():
            return PageType.LOGIN
        if "error" in title.lower():
            return PageType.ERROR
        # HTML content patterns
        if "form" in html_content.lower() and "password" in html_content.lower():
            return PageType.LOGIN
        if "error" in html_content.lower() and "404" in html_content.lower():
            return PageType.ERROR
        return PageType.UNKNOWN

    def _find_status_indicators(self) -> List[str]:
        """Find status indicators on the page."""
        indicators = []
        # Look for common status indicators
        status_selectors = [
            ".status",
            ".alert",
            ".message",
            ".notification",
            ".error",
            ".success",
            ".warning",
            ".info",
        ]
        for selector in status_selectors:
            elements = self.page.query_selector_all(selector)
            for element in elements:
                text = element.text_content()
                if text and text.strip():
                    indicators.append(text.strip())
        return indicators

    def _find_navigation_elements(self) -> List[Dict[str, Any]]:
        """Find navigation elements on the page."""
        nav_elements = []
        # Look for navigation elements
        nav_selectors = [
            "nav",
            ".nav",
            ".navigation",
            ".menu",
            ".breadcrumb",
            ".pagination",
        ]
        for selector in nav_selectors:
            elements = self.page.query_selector_all(selector)
            for element in elements:
                nav_elements.append({
                    "type": selector,
                    "text": element.text_content()[:100],
                    "href": element.get_attribute("href"),
                })
        return nav_elements

    def _find_interactive_elements(self) -> List[Dict[str, Any]]:
        """Find interactive elements on the page."""
        interactive_elements = []
        # Look for interactive elements
        interactive_selectors = [
            "button",
            "input",
            "select",
            "textarea",
            "a[href]",
            "[onclick]",
            "[role='button']",
        ]
        for selector in interactive_selectors:
            elements = self.page.query_selector_all(selector)
            for element in elements:
                interactive_elements.append({
                    "type": selector,
                    "text": element.text_content()[:50],
                    "attributes": {
                        "id": element.get_attribute("id"),
                        "class": element.get_attribute("class"),
                        "type": element.get_attribute("type"),
                    },
                })
        return interactive_elements

    def _extract_meta_info(self) -> Dict[str, Any]:
        """Extract meta information from the page."""
        meta_info = {}
        # Extract meta tags
        meta_tags = self.page.query_selector_all("meta")
        for tag in meta_tags:
            name = tag.get_attribute("name") or tag.get_attribute("property")
            content = tag.get_attribute("content")
            if name and content:
                meta_info[name] = content
        return meta_info

    def _learn_from_analysis(self, analysis: PageAnalysis):
        """Learn from page analysis to improve future navigation."""
        # Learn page type patterns
        page_type = analysis.page_type.value
        if page_type not in self.learning_state.page_type_patterns:
            self.learning_state.page_type_patterns[page_type] = []
        self.learning_state.page_type_patterns[page_type].append(analysis.url)
        # Learn button patterns
        for element in analysis.interactive_elements:
            if element["type"] == "button":
                button_text = element["text"]
                if button_text not in self.learning_state.button_patterns:
                    self.learning_state.button_patterns[button_text] = []
                self.learning_state.button_patterns[button_text].append(analysis.url)
        # Learn form patterns
        if analysis.form_count > 0:
            form_key = f"forms_{analysis.form_count}"
            if form_key not in self.learning_state.form_patterns:
                self.learning_state.form_patterns[form_key] = []
            self.learning_state.form_patterns[form_key].append(analysis.url)

    def _display_curious_findings(self, analysis: PageAnalysis):
        """Display findings with curiosity and enthusiasm."""
        print(f"\n🎯 Page Analysis Results:")
        print(f"   Type: {analysis.page_type.value}")
        print(f"   Elements: {analysis.form_count} forms, {analysis.button_count} buttons, {analysis.input_count} inputs")
        print(f"   Content: {analysis.link_count} links, {analysis.image_count} images")
        print(f"   Status indicators: {len(analysis.status_indicators)}")
        print(f"   Navigation elements: {len(analysis.navigation_elements)}")
        print(f"   Interactive elements: {len(analysis.interactive_elements)}")
        if analysis.status_indicators:
            print(f"   Status: {', '.join(analysis.status_indicators[:3])}")
        print(f"   Learning state: {self.learning_state.total_pages_analyzed} pages analyzed")


