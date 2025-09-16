#!/usr/bin/env python3
"""
Investigation Modules
====================

RMDDD-compliant modules for Ghostbusters consultation investigation.
Each module handles a specific aspect of the investigation process.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class InvestigationResult:
    """Result of an investigation module"""

    module_name: str
    success: bool
    data: Dict[str, Any]
    confidence: float
    errors: List[str] = None


class InvestigationModule(ABC):
    """Base class for investigation modules following RMDDD principles"""

    def __init__(self, name: str):
        self.name = name
        self.errors = []

    @abstractmethod
    def investigate(
        self, page_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> InvestigationResult:
        """Perform investigation and return results"""
        pass

    def _add_error(self, error: str):
        """Add error to module error list"""
        self.errors.append(f"{self.name}: {error}")

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information for debugging"""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "errors": self.errors,
        }


class PageStructureAnalyzer(InvestigationModule):
    """Analyzes overall page structure"""

    def __init__(self):
        super().__init__("PageStructureAnalyzer")

    def investigate(
        self, page_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> InvestigationResult:
        """Analyze page structure"""
        try:
            analysis = {
                "url_pattern": self._analyze_url_pattern(page_data.get("url", "")),
                "title_analysis": self._analyze_title(page_data.get("title", "")),
                "navigation_count": len(page_data.get("navigation", [])),
                "button_count": len(page_data.get("buttons", [])),
                "form_elements": self._count_form_elements(page_data),
                "content_length": len(page_data.get("pageText", "")),
                "structure_type": self._classify_page_structure(page_data),
            }

            return InvestigationResult(
                module_name=self.name,
                success=True,
                data=analysis,
                confidence=0.8 if analysis["content_length"] > 0 else 0.2,
            )

        except Exception as e:
            self._add_error(str(e))
            return InvestigationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )

    def _analyze_url_pattern(self, url: str) -> Dict[str, Any]:
        """Analyze URL patterns for clues"""
        if not url:
            return {"pattern": "unknown", "domain": "unknown", "path_type": "unknown"}

        from urllib.parse import urlparse

        parsed = urlparse(url)

        return {
            "pattern": "devpost" if "devpost" in parsed.netloc.lower() else "other",
            "domain": parsed.netloc,
            "path_type": (
                "form"
                if any(
                    word in parsed.path.lower() for word in ["form", "submit", "create"]
                )
                else "navigation"
            ),
            "has_params": bool(parsed.query),
            "is_secure": parsed.scheme == "https",
        }

    def _analyze_title(self, title: str) -> Dict[str, Any]:
        """Analyze page title for context clues"""
        if not title:
            return {"type": "unknown", "keywords": [], "confidence": 0.0}

        title_lower = title.lower()

        # Identify page types based on title
        if any(word in title_lower for word in ["form", "submit", "create", "edit"]):
            page_type = "form"
            confidence = 0.8
        elif any(word in title_lower for word in ["team", "manage", "members"]):
            page_type = "team_management"
            confidence = 0.8
        elif any(word in title_lower for word in ["project", "overview", "details"]):
            page_type = "project_info"
            confidence = 0.8
        elif any(word in title_lower for word in ["login", "sign", "auth"]):
            page_type = "authentication"
            confidence = 0.9
        else:
            page_type = "unknown"
            confidence = 0.3

        # Extract keywords
        keywords = [word for word in title_lower.split() if len(word) > 3]

        return {
            "type": page_type,
            "keywords": keywords,
            "confidence": confidence,
            "length": len(title),
        }

    def _count_form_elements(self, page_data: Dict[str, Any]) -> Dict[str, int]:
        """Count different types of form elements"""
        navigation = page_data.get("navigation", [])

        form_elements = {
            "input_fields": 0,
            "select_dropdowns": 0,
            "checkboxes": 0,
            "radio_buttons": 0,
            "text_areas": 0,
            "submit_buttons": 0,
        }

        for element in navigation:
            element_type = element.get("type", "").lower()
            if "input" in element_type:
                form_elements["input_fields"] += 1
            elif "select" in element_type:
                form_elements["select_dropdowns"] += 1
            elif "checkbox" in element_type:
                form_elements["checkboxes"] += 1
            elif "radio" in element_type:
                form_elements["radio_buttons"] += 1
            elif "textarea" in element_type:
                form_elements["text_areas"] += 1
            elif "submit" in element_type or "button" in element_type:
                form_elements["submit_buttons"] += 1

        return form_elements

    def _classify_page_structure(self, page_data: Dict[str, Any]) -> str:
        """Classify the overall page structure"""
        form_elements = self._count_form_elements(page_data)
        total_form_elements = sum(form_elements.values())

        if total_form_elements > 5:
            return "form_heavy"
        elif total_form_elements > 0:
            return "form_light"
        elif len(page_data.get("navigation", [])) > 10:
            return "navigation_heavy"
        else:
            return "content_focused"


class NavigationAnalyzer(InvestigationModule):
    """Analyzes navigation elements for patterns"""

    def __init__(self):
        super().__init__("NavigationAnalyzer")

    def investigate(
        self, page_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> InvestigationResult:
        """Analyze navigation elements"""
        try:
            navigation = page_data.get("navigation", [])

            analysis = {
                "total_elements": len(navigation),
                "button_types": {},
                "common_texts": {},
                "href_patterns": {},
                "interaction_patterns": self._identify_interaction_patterns(navigation),
            }

            for element in navigation:
                # Analyze button types
                element_type = element.get("type", "unknown")
                analysis["button_types"][element_type] = (
                    analysis["button_types"].get(element_type, 0) + 1
                )

                # Analyze text content
                text = element.get("text", "").strip()
                if text:
                    analysis["common_texts"][text] = (
                        analysis["common_texts"].get(text, 0) + 1
                    )

                # Analyze href patterns
                href = element.get("href", "")
                if href:
                    from urllib.parse import urlparse

                    parsed = urlparse(href)
                    domain = parsed.netloc
                    analysis["href_patterns"][domain] = (
                        analysis["href_patterns"].get(domain, 0) + 1
                    )

            confidence = 0.7 if analysis["total_elements"] > 0 else 0.3

            return InvestigationResult(
                module_name=self.name,
                success=True,
                data=analysis,
                confidence=confidence,
            )

        except Exception as e:
            self._add_error(str(e))
            return InvestigationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )

    def _identify_interaction_patterns(self, navigation: List[Dict]) -> List[str]:
        """Identify common interaction patterns"""
        patterns = []

        # Check for form-related patterns
        form_indicators = ["submit", "save", "continue", "next", "form"]
        for element in navigation:
            text = element.get("text", "").lower()
            if any(indicator in text for indicator in form_indicators):
                patterns.append("form_interaction")
                break

        # Check for navigation patterns
        nav_indicators = ["back", "forward", "home", "menu", "nav"]
        for element in navigation:
            text = element.get("text", "").lower()
            if any(indicator in text for indicator in nav_indicators):
                patterns.append("navigation_interaction")
                break

        return patterns


class ContentAnalyzer(InvestigationModule):
    """Analyzes page content for context"""

    def __init__(self):
        super().__init__("ContentAnalyzer")

    def investigate(
        self, page_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> InvestigationResult:
        """Analyze page content"""
        try:
            page_text = page_data.get("pageText", "")

            analysis = {
                "content_length": len(page_text),
                "word_count": len(page_text.split()),
                "key_phrases": self._extract_key_phrases(page_text),
                "content_type": self._classify_content_type(page_text),
                "language_indicators": self._identify_language_patterns(page_text),
                "semantic_analysis": self._perform_semantic_analysis(page_text),
            }

            confidence = 0.8 if analysis["content_length"] > 10 else 0.2

            return InvestigationResult(
                module_name=self.name,
                success=True,
                data=analysis,
                confidence=confidence,
            )

        except Exception as e:
            self._add_error(str(e))
            return InvestigationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from page text"""
        phrases = []
        text_lower = text.lower()

        important_phrases = [
            "project overview",
            "project details",
            "team members",
            "manage team",
            "additional information",
            "submission",
            "hackathon",
            "devpost",
            "save and continue",
            "submit",
            "required field",
            "validation",
        ]

        for phrase in important_phrases:
            if phrase in text_lower:
                phrases.append(phrase)

        return phrases

    def _classify_content_type(self, text: str) -> str:
        """Classify the type of content on the page"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["form", "field", "input", "required"]):
            return "form_content"
        elif any(word in text_lower for word in ["team", "member", "collaborator"]):
            return "team_content"
        elif any(word in text_lower for word in ["project", "description", "overview"]):
            return "project_content"
        elif any(word in text_lower for word in ["submit", "submission", "final"]):
            return "submission_content"
        else:
            return "general_content"

    def _identify_language_patterns(self, text: str) -> List[str]:
        """Identify language patterns that might indicate page type"""
        patterns = []
        text_lower = text.lower()

        if "please" in text_lower:
            patterns.append("polite_language")
        if "required" in text_lower:
            patterns.append("requirement_language")
        if "optional" in text_lower:
            patterns.append("optional_language")
        if "error" in text_lower or "invalid" in text_lower:
            patterns.append("error_language")
        if "success" in text_lower or "complete" in text_lower:
            patterns.append("success_language")

        return patterns

    def _perform_semantic_analysis(self, text: str) -> Dict[str, Any]:
        """Perform basic semantic analysis"""
        text_lower = text.lower()

        return {
            "has_questions": "?" in text,
            "has_instructions": any(
                word in text_lower for word in ["click", "enter", "select", "choose"]
            ),
            "has_warnings": any(
                word in text_lower for word in ["warning", "caution", "attention"]
            ),
            "has_errors": any(
                word in text_lower for word in ["error", "invalid", "failed"]
            ),
            "complexity_score": len(text.split()) / 100.0,  # Simple complexity measure
        }


class DiagnosticTester(InvestigationModule):
    """Runs diagnostic tests on the page"""

    def __init__(self):
        super().__init__("DiagnosticTester")

    def investigate(
        self, page_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> InvestigationResult:
        """Run diagnostic tests"""
        try:
            tests = {}

            # Test 1: Page accessibility
            tests["page_accessible"] = len(page_data.get("pageText", "")) > 0

            # Test 2: Navigation elements present
            tests["navigation_present"] = len(page_data.get("navigation", [])) > 0

            # Test 3: Form elements detected
            form_elements = self._count_form_elements(page_data)
            tests["forms_detected"] = sum(form_elements.values()) > 0

            # Test 4: Interactive elements available
            buttons = page_data.get("buttons", [])
            tests["interactive_elements"] = len(buttons) > 0

            # Test 5: URL pattern recognition
            url = page_data.get("url", "")
            tests["url_recognized"] = "devpost.com" in url or len(url) > 0

            # Test 6: Content analysis success
            tests["content_analyzed"] = len(page_data.get("pageText", "")) > 10

            # Calculate overall test confidence
            passed_tests = sum(1 for test_result in tests.values() if test_result)
            total_tests = len(tests)
            confidence = passed_tests / total_tests if total_tests > 0 else 0.0

            return InvestigationResult(
                module_name=self.name,
                success=True,
                data={
                    "tests": tests,
                    "summary": f"{passed_tests}/{total_tests} tests passed",
                },
                confidence=confidence,
            )

        except Exception as e:
            self._add_error(str(e))
            return InvestigationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )

    def _count_form_elements(self, page_data: Dict[str, Any]) -> Dict[str, int]:
        """Count form elements for testing"""
        navigation = page_data.get("navigation", [])

        form_elements = {
            "input_fields": 0,
            "select_dropdowns": 0,
            "checkboxes": 0,
            "radio_buttons": 0,
            "text_areas": 0,
            "submit_buttons": 0,
        }

        for element in navigation:
            element_type = element.get("type", "").lower()
            if "input" in element_type:
                form_elements["input_fields"] += 1
            elif "select" in element_type:
                form_elements["select_dropdowns"] += 1
            elif "checkbox" in element_type:
                form_elements["checkboxes"] += 1
            elif "radio" in element_type:
                form_elements["radio_buttons"] += 1
            elif "textarea" in element_type:
                form_elements["text_areas"] += 1
            elif "submit" in element_type or "button" in element_type:
                form_elements["submit_buttons"] += 1

        return form_elements


class InvestigationOrchestrator:
    """Orchestrates multiple investigation modules"""

    def __init__(self):
        self.modules = [
            PageStructureAnalyzer(),
            NavigationAnalyzer(),
            ContentAnalyzer(),
            DiagnosticTester(),
        ]

    def run_investigation(
        self, page_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run all investigation modules and aggregate results"""

        results = {}
        overall_confidence = 0.0
        successful_modules = 0

        for module in self.modules:
            print(f"   🔍 Running {module.name}...")
            result = module.investigate(page_data, context)
            results[module.name] = result

            if result.success:
                successful_modules += 1
                overall_confidence += result.confidence

        # Calculate overall confidence
        if successful_modules > 0:
            overall_confidence /= successful_modules

        # Aggregate results
        aggregated = {
            "overall_confidence": overall_confidence,
            "successful_modules": successful_modules,
            "total_modules": len(self.modules),
            "results": results,
            "summary": self._generate_summary(results),
        }

        return aggregated

    def _generate_summary(
        self, results: Dict[str, InvestigationResult]
    ) -> Dict[str, Any]:
        """Generate summary of investigation results"""
        successful = [r for r in results.values() if r.success]
        failed = [r for r in results.values() if not r.success]

        return {
            "successful_investigations": len(successful),
            "failed_investigations": len(failed),
            "primary_findings": [r.data for r in successful if r.data],
            "errors": [error for r in failed for error in (r.errors or [])],
        }

    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all modules for debugging"""
        return {
            "modules": [module.get_module_info() for module in self.modules],
            "total_modules": len(self.modules),
        }
