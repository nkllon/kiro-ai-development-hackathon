#!/usr/bin/env python3
"""
Learning MVC System
==================
A truly learning MVC system that collects comprehensive telemetry,
heuristically analyzes HTML and visual elements, and shows curiosity
about what's actually on the page.
Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Learning-based page analysis and navigation
"""
import json
import re
import sys
import time
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from playwright.sync_api import Page
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class PageType(Enum):
    """Enumeration of detected page types."""

    UNKNOWN = "unknown"
    LOGIN = "login"
    AUTHENTICATION = "authentication"
    PROJECT_OVERVIEW = "project_overview"
    PROJECT_DETAILS = "project_details"
    ADDITIONAL_INFO = "additional_info"
    SUBMISSION = "submission"
    DASHBOARD = "dashboard"
    ERROR = "error"
    LOADING = "loading"


@dataclass
class TelemetryEvent:
    """Telemetry event for comprehensive logging."""

    timestamp: float
    event_type: str
    page_url: str
    page_title: str
    data: Dict[str, Any]
    success: bool
    error: Optional[str] = None


@dataclass
class PageAnalysis:
    """Comprehensive page analysis."""

    url: str
    title: str
    page_type: PageType
    html_length: int
    form_count: int
    button_count: int
    input_count: int
    link_count: int
    image_count: int
    status_indicators: List[str]
    navigation_elements: List[Dict[str, Any]]
    interactive_elements: List[Dict[str, Any]]
    text_content: str
    meta_info: Dict[str, Any]
    analysis_timestamp: float


@dataclass
class LearningState:
    """Learning state for the system."""

    total_pages_analyzed: int
    successful_navigations: int
    failed_navigations: int
    discovered_patterns: Dict[str, Any]
    learned_selectors: Dict[str, List[str]]
    page_type_patterns: Dict[str, List[str]]
    button_patterns: Dict[str, List[str]]
    form_patterns: Dict[str, List[str]]


class TelemetryCollector:
    """Comprehensive telemetry collection."""

    def __init__(self):
        self.events: List[TelemetryEvent] = []
        self.start_time = time.time()

    def log_event(
        self,
        event_type: str,
        page: Page,
        data: Dict[str, Any],
        success: bool = True,
        error: str = None,
    ):
        """Log a telemetry event."""
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type=event_type,
            page_url=page.url,
            page_title=page.title(),
            data=data,
            success=success,
            error=error,
        )
        self.events.append(event)
        # Real-time logging
        "✅" if success else "❌"
        print("{status} {event_type}: {page.url} | {data.get('summary', '')}")
        if error:
            print("   Error: {error}")

    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary."""
        total_events = len(self.events)
        successful_events = len([e for e in self.events if e.success])
        failed_events = total_events - successful_events
        event_types = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": successful_events / total_events if total_events > 0 else 0,
            "event_types": event_types,
            "session_duration": time.time() - self.start_time,
        }

    def save_telemetry(self, filename: str = None):
        """Save telemetry to file."""
        if not filename:
            int(time.time())
            filename = "telemetry_{timestamp}.json"
        # Convert to serializable format
        telemetry_data = {
            "summary": self.get_summary(),
            "events": [asdict(event) for event in self.events],
        }
        with open(filename, "w") as f:
            json.dump(telemetry_data, f, indent=2)
        print("📊 Telemetry saved: {filename}")
        return filename


class CuriousPageAnalyzer:
    """Curious page analyzer that learns from HTML and visual elements."""

    def __init__(self, page: Page, telemetry: TelemetryCollector):
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
        print("URL: {self.page.url}")
        print("Title: {self.page.title()}")
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
        url_lower = url.lower()
        title_lower = title.lower()
        html_lower = html_content.lower()
        # Look for multiple signals
        signals = {
            "login": 0,
            "authentication": 0,
            "project_overview": 0,
            "project_details": 0,
            "additional_info": 0,
            "submission": 0,
            "dashboard": 0,
            "error": 0,
            "loading": 0,
        }
        # URL patterns
        if "login" in url_lower or "signin" in url_lower:
            signals["login"] += 3
        if "auth" in url_lower or "oauth" in url_lower:
            signals["authentication"] += 3
        if "project-overview" in url_lower or "overview" in url_lower:
            signals["project_overview"] += 3
        if "project_details" in url_lower or "photo" in url_lower:
            signals["project_details"] += 3
        if "additional-info" in url_lower:
            signals["additional_info"] += 3
        if "submit" in url_lower:
            signals["submission"] += 3
        if "manage" in url_lower or "dashboard" in url_lower:
            signals["dashboard"] += 3
        if "error" in url_lower:
            signals["error"] += 3
        # Title patterns
        if "sign in" in title_lower or "login" in title_lower:
            signals["login"] += 2
        if "auth" in title_lower or "oauth" in title_lower:
            signals["authentication"] += 2
        if "project" in title_lower and "overview" in title_lower:
            signals["project_overview"] += 2
        if "project" in title_lower and (
            "details" in title_lower or "photo" in title_lower
        ):
            signals["project_details"] += 2
        if "additional" in title_lower or "info" in title_lower:
            signals["additional_info"] += 2
        if "submit" in title_lower:
            signals["submission"] += 2
        if "manage" in title_lower or "dashboard" in title_lower:
            signals["dashboard"] += 2
        if "error" in title_lower:
            signals["error"] += 2
        # HTML content patterns
        if "password" in html_lower and "email" in html_lower:
            signals["login"] += 1
        if "oauth" in html_lower or "authorize" in html_lower:
            signals["authentication"] += 1
        if "project name" in html_lower or "project title" in html_lower:
            signals["project_overview"] += 1
        if "photo" in html_lower or "image" in html_lower or "screenshot" in html_lower:
            signals["project_details"] += 1
        if "additional" in html_lower or "more info" in html_lower:
            signals["additional_info"] += 1
        if "submit" in html_lower and "form" in html_lower:
            signals["submission"] += 1
        if "manage" in html_lower or "dashboard" in html_lower:
            signals["dashboard"] += 1
        if "error" in html_lower or "not found" in html_lower:
            signals["error"] += 1
        if "loading" in html_lower or "spinner" in html_lower:
            signals["loading"] += 1
        # Find the highest scoring type
        max_score = max(signals.values())
        if max_score == 0:
            return PageType.UNKNOWN
        for page_type, score in signals.items():
            if score == max_score:
                return PageType(page_type)
        return PageType.UNKNOWN

    def _find_status_indicators(self) -> List[str]:
        """Find status indicators on the page."""
        indicators = []
        # Look for various status indicator patterns
        status_selectors = [
            ".status",
            ".state",
            ".progress",
            ".loading",
            ".error",
            ".success",
            ".alert",
            ".notification",
            ".message",
            ".warning",
            ".info",
            "[role='status']",
            "[role='alert']",
            "[aria-live]",
            ".step",
            ".wizard-step",
            ".form-step",
            ".nav-step",
            ".completed",
            ".current",
            ".active",
            ".pending",
            ".disabled",
        ]
        for selector in status_selectors:
            try:
                elements = self.page.query_selector_all(selector)
                for element in elements:
                    text = element.text_content().strip()
                    if text and len(text) < 100:
                        indicators.append("{selector}: {text}")
            except Exception:
                continue
        return indicators

    def _find_navigation_elements(self) -> List[Dict[str, Any]]:
        """Find navigation elements with detailed analysis."""
        nav_elements = []
        # Look for various navigation patterns
        nav_selectors = [
            "button",
            "a",
            "input[type='button']",
            "input[type='submit']",
            ".btn",
            ".button",
            ".link",
            ".nav",
            ".step",
            ".wizard",
            "[role='button']",
            "[role='link']",
            "[role='tab']",
        ]
        for selector in nav_selectors:
            try:
                elements = self.page.query_selector_all(selector)
                for i, element in enumerate(elements):
                    try:
                        text = element.text_content().strip()
                        href = element.get_attribute("href")
                        onclick = element.get_attribute("onclick")
                        classes = element.get_attribute("class")
                        is_visible = element.is_visible()
                        is_enabled = element.is_enabled()
                        if text and len(text) < 200:  # Reasonable text length
                            nav_elements.append(
                                {
                                    "selector": selector,
                                    "index": i,
                                    "text": text,
                                    "href": href,
                                    "onclick": onclick,
                                    "classes": classes,
                                    "is_visible": is_visible,
                                    "is_enabled": is_enabled,
                                    "element_type": element.evaluate(
                                        "el => el.tagName"
                                    ).lower(),
                                }
                            )
                    except Exception:
                        continue
            except Exception:
                continue
        return nav_elements

    def _find_interactive_elements(self) -> List[Dict[str, Any]]:
        """Find interactive elements for form filling."""
        interactive_elements = []
        # Look for form elements
        form_selectors = ["input", "textarea", "select", "button", "form"]
        for selector in form_selectors:
            try:
                elements = self.page.query_selector_all(selector)
                for i, element in enumerate(elements):
                    try:
                        element_type = (
                            element.get_attribute("type")
                            or element.evaluate("el => el.tagName").lower()
                        )
                        name = element.get_attribute("name")
                        element_id = element.get_attribute("id")
                        placeholder = element.get_attribute("placeholder")
                        value = element.get_attribute("value")
                        required = element.get_attribute("required") is not None
                        classes = element.get_attribute("class")
                        # Get label
                        label = "Unlabeled"
                        if element_id:
                            label_elem = self.page.query_selector(
                                "label[for='{element_id}']"
                            )
                            if label_elem:
                                label = label_elem.text_content().strip()
                        interactive_elements.append(
                            {
                                "selector": selector,
                                "index": i,
                                "element_type": element_type,
                                "name": name,
                                "id": element_id,
                                "label": label,
                                "placeholder": placeholder,
                                "value": value,
                                "required": required,
                                "classes": classes,
                                "is_visible": element.is_visible(),
                                "is_enabled": element.is_enabled(),
                            }
                        )
                    except Exception:
                        continue
            except Exception:
                continue
        return interactive_elements

    def _extract_meta_info(self) -> Dict[str, Any]:
        """Extract meta information from the page."""
        meta_info = {}
        try:
            # Get meta tags
            meta_tags = self.page.query_selector_all("meta")
            for meta in meta_tags:
                name = meta.get_attribute("name") or meta.get_attribute("property")
                content = meta.get_attribute("content")
                if name and content:
                    meta_info["meta_{name}"] = content
            # Get page language
            html_lang = self.page.get_attribute("html", "lang")
            if html_lang:
                meta_info["language"] = html_lang
            # Get viewport
            viewport = self.page.viewport_size
            if viewport:
                meta_info["viewport"] = "{viewport['width']}x{viewport['height']}"
            # Get page load time
            load_time = self.page.evaluate(
                "() => performance.timing.loadEventEnd - performance.timing.navigationStart"
            )
            if load_time:
                meta_info["load_time_ms"] = load_time
        except Exception as e:
            meta_info["error"] = str(e)
        return meta_info

    def _learn_from_analysis(self, analysis: PageAnalysis):
        """Learn from page analysis to improve future detection."""
        page_type = analysis.page_type.value
        # Learn page type patterns
        if page_type not in self.learning_state.page_type_patterns:
            self.learning_state.page_type_patterns[page_type] = []
        # Learn from URL patterns
        url_patterns = re.findall(r"[a-zA-Z0-9-]+", analysis.url)
        self.learning_state.page_type_patterns[page_type].extend(url_patterns)
        # Learn from title patterns
        title_words = re.findall(r"[a-zA-Z0-9-]+", analysis.title)
        self.learning_state.page_type_patterns[page_type].extend(title_words)
        # Learn button patterns
        for nav_element in analysis.navigation_elements:
            if nav_element["text"]:
                button_text = nav_element["text"].lower()
                if button_text not in self.learning_state.button_patterns:
                    self.learning_state.button_patterns[button_text] = []
                self.learning_state.button_patterns[button_text].append(
                    nav_element["classes"]
                )
        # Learn form patterns
        for interactive_element in analysis.interactive_elements:
            if interactive_element["name"]:
                field_name = interactive_element["name"].lower()
                if field_name not in self.learning_state.form_patterns:
                    self.learning_state.form_patterns[field_name] = []
                self.learning_state.form_patterns[field_name].append(
                    {
                        "type": interactive_element["element_type"],
                        "classes": interactive_element["classes"],
                    }
                )

    def _display_curious_findings(self, analysis: PageAnalysis):
        """Display findings with curiosity and insight."""
        print("\n🤔 Curious Findings:")
        print("   📄 Page Type: {analysis.page_type.value}")
        print(
            "   📊 Elements: {analysis.form_count} forms, {analysis.button_count} buttons, {analysis.input_count} inputs"
        )
        print("   🔗 Links: {analysis.link_count}, Images: {analysis.image_count}")
        if analysis.status_indicators:
            print("   🚦 Status Indicators ({len(analysis.status_indicators)}):")
            for indicator in analysis.status_indicators[:5]:  # Show first 5
                print("      • {indicator}")
        if analysis.navigation_elements:
            print("   🧭 Navigation Elements ({len(analysis.navigation_elements)}):")
            for nav in analysis.navigation_elements[:5]:  # Show first 5
                "✅" if nav["is_visible"] and nav["is_enabled"] else "❌"
                print(
                    "      {status} {nav['text'][:50]}... (type: {nav['element_type']})"
                )
        if analysis.interactive_elements:
            print("   🎮 Interactive Elements ({len(analysis.interactive_elements)}):")
            for elem in analysis.interactive_elements[:5]:  # Show first 5
                if elem["label"] != "Unlabeled":
                    print("      • {elem['label']} ({elem['element_type']})")
        # Show learning insights
        print("\n🧠 Learning Insights:")
        print("   📚 Total pages analyzed: {self.learning_state.total_pages_analyzed}")
        print(
            "   🎯 Successful navigations: {self.learning_state.successful_navigations}"
        )
        print("   ❌ Failed navigations: {self.learning_state.failed_navigations}")
        if self.learning_state.button_patterns:
            print(
                "   🔘 Learned button patterns: {len(self.learning_state.button_patterns)}"
            )
        if self.learning_state.form_patterns:
            print(
                "   📝 Learned form patterns: {len(self.learning_state.form_patterns)}"
            )


class LearningMVCSystem:
    """Main learning MVC system."""

    def __init__(self, page: Page):
        self.page = page
        self.telemetry = TelemetryCollector()
        self.analyzer = CuriousPageAnalyzer(page, self.telemetry)
        self.current_analysis: Optional[PageAnalysis] = None
        self.project_data = {}

    def initialize(self, project_data: Dict[str, Any] = None):
        """Initialize the learning system."""
        print("🧠 Learning MVC System Starting")
        print("=" * 50)
        if project_data:
            self.project_data = project_data
            print("📊 Project data loaded: {len(project_data)} fields")
        # Set up comprehensive event listeners
        self._setup_event_listeners()
        # Perform initial analysis
        self.analyze_current_page()
        # Take initial screenshot
        self._take_curious_screenshot("initial_analysis")

    def _setup_event_listeners(self):
        """Set up comprehensive event listeners."""
        print("🎧 Setting up comprehensive event listeners...")
        # Page events
        self.page.on("load", self._on_page_load)
        self.page.on("domcontentloaded", self._on_dom_loaded)
        self.page.on("networkidle", self._on_network_idle)
        # Console events
        self.page.on("console", self._on_console_message)
        # Error events
        self.page.on("pageerror", self._on_page_error)
        self.page.on("crash", self._on_page_crash)
        # Request/Response events
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)
        # Dialog events
        self.page.on("dialog", self._on_dialog)
        print("✅ Event listeners configured")

    def _on_page_load(self, page: Page):
        """Handle page load event."""
        self.telemetry.log_event("page_load", page, {"url": page.url})
        print("📄 Page loaded: {page.url}")
        self.analyze_current_page()

    def _on_dom_loaded(self, page: Page):
        """Handle DOM loaded event."""
        self.telemetry.log_event("dom_loaded", page, {"url": page.url})
        print("🌐 DOM loaded: {page.url}")

    def _on_network_idle(self, page: Page):
        """Handle network idle event."""
        self.telemetry.log_event("network_idle", page, {"url": page.url})
        print("🔌 Network idle: {page.url}")

    def _on_console_message(self, msg):
        """Handle console messages."""
        if msg.type in ["error", "warning"]:
            self.telemetry.log_event(
                "console_message", self.page, {"type": msg.type, "text": msg.text}
            )
            print("⚠️ Console {msg.type}: {msg.text}")

    def _on_page_error(self, error):
        """Handle page errors."""
        self.telemetry.log_event("page_error", self.page, {}, False, str(error))
        print("❌ Page error: {error}")

    def _on_page_crash(self, error):
        """Handle page crashes."""
        self.telemetry.log_event("page_crash", self.page, {}, False, str(error))
        print("💥 Page crash: {error}")

    def _on_request(self, request):
        """Handle outgoing requests."""
        if (
            "devpost.com" in request.url
            or "github.com" in request.url
            or "google.com" in request.url
        ):
            self.telemetry.log_event(
                "request",
                self.page,
                {
                    "method": request.method,
                    "url": request.url,
                    "resource_type": request.resource_type,
                },
            )

    def _on_response(self, response):
        """Handle responses."""
        if (
            "devpost.com" in response.url
            or "github.com" in response.url
            or "google.com" in response.url
        ):
            self.telemetry.log_event(
                "response",
                self.page,
                {
                    "status": response.status,
                    "url": response.url,
                    "status_text": response.status_text,
                },
            )

    def _on_dialog(self, dialog):
        """Handle dialogs."""
        self.telemetry.log_event(
            "dialog", self.page, {"type": dialog.type, "message": dialog.message}
        )
        print("💬 Dialog: {dialog.type} - {dialog.message}")

    def analyze_current_page(self):
        """Analyze current page with curiosity."""
        try:
            self.current_analysis = self.analyzer.analyze_page()
            return self.current_analysis
        except Exception as e:
            self.telemetry.log_event("page_analysis", self.page, {}, False, str(e))
            print("❌ Page analysis failed: {e}")
            return None

    def find_navigation_options(self) -> List[Dict[str, Any]]:
        """Find navigation options with learning."""
        if not self.current_analysis:
            return []
        # Use learned patterns to find navigation
        navigation_options = []
        for nav_element in self.current_analysis.navigation_elements:
            if nav_element["is_visible"] and nav_element["is_enabled"]:
                # Analyze if this looks like a navigation element
                text = nav_element["text"].lower()
                is_navigation = False
                # Check against learned patterns
                for pattern in self.analyzer.learning_state.button_patterns:
                    if pattern in text:
                        is_navigation = True
                        break
                # Check for common navigation keywords
                nav_keywords = [
                    "next",
                    "continue",
                    "back",
                    "previous",
                    "submit",
                    "save",
                    "finish",
                    "complete",
                ]
                if any(keyword in text for keyword in nav_keywords):
                    is_navigation = True
                if is_navigation:
                    navigation_options.append(nav_element)
        return navigation_options

    def navigate_to_element(self, element_info: Dict[str, Any]) -> bool:
        """Navigate to a specific element."""
        try:
            # Find the element
            element = None
            if element_info["id"]:
                element = self.page.query_selector("#{element_info['id']}")
            elif element_info["text"]:
                # Try to find by text
                elements = self.page.query_selector_all(
                    "button:has-text('{element_info['text']}'), a:has-text('{element_info['text']}')"
                )
                if elements:
                    element = elements[0]
            if not element:
                print("❌ Could not find element: {element_info['text']}")
                return False
            print("🔄 Clicking: {element_info['text']}")
            element.click()
            # Wait for navigation
            self.page.wait_for_load_state("networkidle")
            # Update analysis
            self.analyze_current_page()
            # Update learning state
            self.analyzer.learning_state.successful_navigations += 1
            self.telemetry.log_event(
                "navigation",
                self.page,
                {"element_text": element_info["text"], "success": True},
            )
            return True
        except Exception as e:
            self.analyzer.learning_state.failed_navigations += 1
            self.telemetry.log_event(
                "navigation",
                self.page,
                {"element_text": element_info.get("text", ""), "success": False},
                False,
                str(e),
            )
            print("❌ Navigation failed: {e}")
            return False

    def _take_curious_screenshot(self, prefix: str = "curious"):
        """Take screenshot with curious naming."""
        try:
            int(time.time())
            url_parts = self.page.url.split("/")
            url_parts[-3] if len(url_parts) > 3 else "unknown"
            url_parts[-2] if len(url_parts) > 2 else "unknown"
            page_title = self.page.title().replace(" ", "_").replace("/", "_")[:20]
            page_type = (
                self.current_analysis.page_type.value
                if self.current_analysis
                else "unknown"
            )
            filename = "curious_{hackathon_id}_{submission_id}_{page_type}_{page_title}_{prefix}_{timestamp}.png"
            self.page.screenshot(path=filename)
            print("📸 Curious screenshot: {filename}")
            return filename
        except Exception:
            print("❌ Screenshot failed: {e}")
            return None

    def interactive_mode(self):
        """Start interactive mode with learning."""
        print("\n🎮 Interactive Learning Mode")
        print("=" * 30)
        print("Commands: analyze, navigate, screenshot, telemetry, learn, quit")
        while True:
            try:
                command = input("🔧 Command: ").strip().lower()
                if command == "quit":
                    break
                elif command == "analyze":
                    self.analyze_current_page()
                elif command == "navigate":
                    options = self.find_navigation_options()
                    if options:
                        print("🧭 Available navigation options:")
                        for i, option in enumerate(options[:10], 1):
                            print("   {i}. {option['text']} ({option['element_type']})")
                        try:
                            choice = int(input("Choose option (number): ")) - 1
                            if 0 <= choice < len(options):
                                self.navigate_to_element(options[choice])
                            else:
                                print("❌ Invalid choice")
                        except ValueError:
                            print("❌ Invalid input")
                    else:
                        print("❌ No navigation options found")
                elif command == "screenshot":
                    self._take_curious_screenshot("manual")
                elif command == "telemetry":
                    self.telemetry.get_summary()
                    print("📊 Telemetry Summary:")
                    print("   Total events: {summary['total_events']}")
                    print("   Success rate: {summary['success_rate']:.2%}")
                    print("   Session duration: {summary['session_duration']:.1f}s")
                    print("   Event types: {summary['event_types']}")
                elif command == "learn":
                    print("🧠 Learning State:")
                    print(
                        "   Pages analyzed: {self.analyzer.learning_state.total_pages_analyzed}"
                    )
                    print(
                        "   Successful navigations: {self.analyzer.learning_state.successful_navigations}"
                    )
                    print(
                        "   Failed navigations: {self.analyzer.learning_state.failed_navigations}"
                    )
                    print(
                        "   Button patterns learned: {len(self.analyzer.learning_state.button_patterns)}"
                    )
                    print(
                        "   Form patterns learned: {len(self.analyzer.learning_state.form_patterns)}"
                    )
                else:
                    print("❌ Unknown command")
            except KeyboardInterrupt:
                break
            except Exception:
                print("❌ Error: {e}")
        # Save telemetry before exit
        self.telemetry.save_telemetry()


def main():
    """Main function."""
    print("🧠 Learning MVC System")
    print("=" * 40)
    # Load project data
    try:
        with open("sample_project_data.json", "r") as f:
            project_data = json.load(f)
        print("📊 Loaded project data: {len(project_data)} fields")
    except Exception:
        print("⚠️ Could not load project data: {e}")
        project_data = {}
    # Connect to existing browser
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        # Get existing pages or create new one
        try:
            pages = browser.pages
            page = pages[0] if pages else browser.new_page()
        except AttributeError:
            # If pages attribute doesn't exist, create new page
            page = browser.new_page()
        # Initialize learning system
        learning_system = LearningMVCSystem(page)
        learning_system.initialize(project_data)
        # Start interactive mode
        learning_system.interactive_mode()
    except Exception:
        print("❌ Connection failed: {e}")
        print("Make sure the browser daemon is running!")


if __name__ == "__main__":
    main()
