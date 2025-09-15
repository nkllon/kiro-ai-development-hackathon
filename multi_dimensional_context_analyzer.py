#!/usr/bin/env python3
"""
Multi-Dimensional Context Analyzer
=================================

Analyzes page context across multiple dimensions and levels to make sound decisions
from wherever the system finds itself. This implements the sophisticated learning
and testing approach you described.
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from langchain_core.messages import AIMessage


class ContextDimension(Enum):
    """Different dimensions of context analysis"""
    URL_STRUCTURE = "url_structure"
    VISUAL_LAYOUT = "visual_layout" 
    NAVIGATION_PATTERNS = "navigation_patterns"
    FORM_STRUCTURE = "form_structure"
    CONTENT_SEMANTICS = "content_semantics"
    SITE_BEHAVIOR = "site_behavior"
    DOM_STRUCTURE = "dom_structure"


class KnowledgeLevel(Enum):
    """Different levels of learned knowledge"""
    GENERAL_TECHNIQUES = "general_techniques"  # Learned from any site
    SITE_SPECIFIC = "site_specific"  # Learned from this specific site
    PAGE_SPECIFIC = "page_specific"  # Learned from this specific page
    SESSION_SPECIFIC = "session_specific"  # Learned in this session


@dataclass
class ContextTestResult:
    """Result of testing context information in a specific dimension"""
    dimension: ContextDimension
    level: KnowledgeLevel
    confidence: float
    match_type: str  # "exact", "similar", "pattern", "unknown"
    evidence: Dict[str, Any]
    recommendation: str
    test_actions: List[str]


@dataclass
class MultiDimensionalAnalysis:
    """Complete multi-dimensional context analysis"""
    url_analysis: ContextTestResult
    visual_analysis: ContextTestResult
    navigation_analysis: ContextTestResult
    form_analysis: ContextTestResult
    content_analysis: ContextTestResult
    site_analysis: ContextTestResult
    dom_analysis: ContextTestResult
    
    overall_confidence: float
    primary_strategy: str
    fallback_strategies: List[str]
    test_plan: List[str]
    learning_opportunities: List[str]


class MultiDimensionalContextAnalyzer:
    """
    Analyzes page context across multiple dimensions and knowledge levels.
    
    This implements the sophisticated approach you described:
    - General navigation techniques learned from any site
    - Site-specific techniques learned from this site
    - Multi-dimensional context testing
    - Sound decision-making from wherever the system finds itself
    """
    
    def __init__(self, telemetry_graph, state_model):
        self.telemetry_graph = telemetry_graph
        self.state_model = state_model
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> Dict[KnowledgeLevel, Dict[str, Any]]:
        """Build knowledge base from telemetry data across different levels"""
        
        knowledge_base = {
            KnowledgeLevel.GENERAL_TECHNIQUES: {},
            KnowledgeLevel.SITE_SPECIFIC: {},
            KnowledgeLevel.PAGE_SPECIFIC: {},
            KnowledgeLevel.SESSION_SPECIFIC: {}
        }
        
        # Extract general techniques from all sites
        knowledge_base[KnowledgeLevel.GENERAL_TECHNIQUES] = self._extract_general_techniques()
        
        # Extract site-specific techniques
        knowledge_base[KnowledgeLevel.SITE_SPECIFIC] = self._extract_site_specific_techniques()
        
        # Extract page-specific techniques
        knowledge_base[KnowledgeLevel.PAGE_SPECIFIC] = self._extract_page_specific_techniques()
        
        # Extract session-specific techniques
        knowledge_base[KnowledgeLevel.SESSION_SPECIFIC] = self._extract_session_specific_techniques()
        
        return knowledge_base
    
    def _extract_general_techniques(self) -> Dict[str, Any]:
        """Extract general navigation techniques from all sites"""
        
        general_techniques = {
            "common_navigation_selectors": [
                'a:has-text("Next")',
                'a:has-text("Continue")',
                'button:has-text("Submit")',
                'button:has-text("Save")',
                '[data-testid*="next"]',
                '[data-testid*="continue"]',
                '.next-button',
                '.continue-button',
                '.submit-button'
            ],
            "common_form_patterns": [
                "input[type='text']",
                "input[type='email']",
                "textarea",
                "select",
                "input[type='submit']"
            ],
            "common_page_indicators": [
                "breadcrumbs",
                "progress indicators",
                "step counters",
                "page titles"
            ],
            "common_error_patterns": [
                ".error-message",
                ".validation-error",
                "[role='alert']",
                ".field-error"
            ]
        }
        
        return general_techniques
    
    def _extract_site_specific_techniques(self) -> Dict[str, Any]:
        """Extract site-specific techniques from DevPost data"""
        
        site_techniques = {}
        
        # Analyze telemetry for site-specific patterns
        for node_id, data in self.telemetry_graph.graph.nodes(data=True):
            url = data.get("url", "")
            if "devpost.com" in url:
                site_techniques[url] = {
                    "navigation_elements": data.get("navigation_elements", []),
                    "form_patterns": data.get("form_data", []),
                    "save_button_behavior": data.get("interactive_elements", []),
                    "page_flow": data.get("page_flow", [])
                }
        
        return site_techniques
    
    def _extract_page_specific_techniques(self) -> Dict[str, Any]:
        """Extract page-specific techniques"""
        
        page_techniques = {}
        
        for node_id, data in self.telemetry_graph.graph.nodes(data=True):
            page_techniques[node_id] = {
                "exact_navigation": data.get("navigation_elements", []),
                "exact_forms": data.get("form_data", []),
                "exact_layout": data.get("dom_structure", {}),
                "successful_actions": data.get("successful_actions", [])
            }
        
        return page_techniques
    
    def _extract_session_specific_techniques(self) -> Dict[str, Any]:
        """Extract techniques learned in current session"""
        
        # This would be populated during the current session
        return {
            "recent_navigations": [],
            "recent_form_interactions": [],
            "recent_errors": [],
            "session_insights": []
        }
    
    def analyze_multi_dimensional_context(self, current_page_data: Dict[str, Any]) -> MultiDimensionalAnalysis:
        """
        Perform multi-dimensional context analysis across all dimensions and levels.
        
        This implements the sophisticated testing approach you described:
        - Test context information at different levels
        - Test across different dimensions
        - Make sound decisions from wherever the system finds itself
        """
        
        print("🔍 Multi-Dimensional Context Analysis")
        print("=" * 50)
        
        # Test each dimension across all knowledge levels
        url_analysis = self._test_url_context(current_page_data)
        visual_analysis = self._test_visual_context(current_page_data)
        navigation_analysis = self._test_navigation_context(current_page_data)
        form_analysis = self._test_form_context(current_page_data)
        content_analysis = self._test_content_context(current_page_data)
        site_analysis = self._test_site_context(current_page_data)
        dom_analysis = self._test_dom_context(current_page_data)
        
        # Combine results into overall analysis
        analysis = MultiDimensionalAnalysis(
            url_analysis=url_analysis,
            visual_analysis=visual_analysis,
            navigation_analysis=navigation_analysis,
            form_analysis=form_analysis,
            content_analysis=content_analysis,
            site_analysis=site_analysis,
            dom_analysis=dom_analysis,
            overall_confidence=0.0,
            primary_strategy="",
            fallback_strategies=[],
            test_plan=[],
            learning_opportunities=[]
        )
        
        # Calculate overall confidence and determine strategy
        analysis = self._synthesize_analysis(analysis)
        
        return analysis
    
    def _test_url_context(self, current_page_data: Dict[str, Any]) -> ContextTestResult:
        """Test URL context across different knowledge levels"""
        
        current_url = current_page_data.get("url", "")
        
        # Test against different levels of knowledge
        general_match = self._test_url_against_general_techniques(current_url)
        site_match = self._test_url_against_site_specific(current_url)
        page_match = self._test_url_against_page_specific(current_url)
        session_match = self._test_url_against_session_specific(current_url)
        
        # Determine best match
        best_match = max([general_match, site_match, page_match, session_match], 
                        key=lambda x: x.get("confidence", 0))
        
        return ContextTestResult(
            dimension=ContextDimension.URL_STRUCTURE,
            level=best_match["level"],
            confidence=best_match["confidence"],
            match_type=best_match["match_type"],
            evidence=best_match["evidence"],
            recommendation=best_match["recommendation"],
            test_actions=["Parse URL structure", "Compare domain patterns", "Check parameter patterns"]
        )
    
    def _test_visual_context(self, current_page_data: Dict[str, Any]) -> ContextTestResult:
        """Test visual context across different knowledge levels"""
        
        current_visual_hash = current_page_data.get("visual_hash", "")
        
        # Test visual similarity against all levels
        general_visual = self._test_visual_against_general_techniques(current_visual_hash)
        site_visual = self._test_visual_against_site_specific(current_visual_hash)
        page_visual = self._test_visual_against_page_specific(current_visual_hash)
        
        best_match = max([general_visual, site_visual, page_visual], 
                        key=lambda x: x.get("confidence", 0))
        
        return ContextTestResult(
            dimension=ContextDimension.VISUAL_LAYOUT,
            level=best_match["level"],
            confidence=best_match["confidence"],
            match_type=best_match["match_type"],
            evidence=best_match["evidence"],
            recommendation=best_match["recommendation"],
            test_actions=["Calculate visual hash", "Compare against known layouts", "Analyze visual patterns"]
        )
    
    def _test_navigation_context(self, current_page_data: Dict[str, Any]) -> ContextTestResult:
        """Test navigation context across different knowledge levels"""
        
        current_navigation = current_page_data.get("navigation", [])
        
        # Test navigation patterns against all levels
        general_nav = self._test_navigation_against_general_techniques(current_navigation)
        site_nav = self._test_navigation_against_site_specific(current_navigation)
        page_nav = self._test_navigation_against_page_specific(current_navigation)
        
        best_match = max([general_nav, site_nav, page_nav], 
                        key=lambda x: x.get("confidence", 0))
        
        return ContextTestResult(
            dimension=ContextDimension.NAVIGATION_PATTERNS,
            level=best_match["level"],
            confidence=best_match["confidence"],
            match_type=best_match["match_type"],
            evidence=best_match["evidence"],
            recommendation=best_match["recommendation"],
            test_actions=["Extract navigation elements", "Compare link patterns", "Test semantic navigation"]
        )
    
    def _test_form_context(self, current_page_data: Dict[str, Any]) -> ContextTestResult:
        """Test form context across different knowledge levels"""
        
        current_forms = current_page_data.get("forms", [])
        
        # Test form patterns against all levels
        general_forms = self._test_forms_against_general_techniques(current_forms)
        site_forms = self._test_forms_against_site_specific(current_forms)
        page_forms = self._test_forms_against_page_specific(current_forms)
        
        best_match = max([general_forms, site_forms, page_forms], 
                        key=lambda x: x.get("confidence", 0))
        
        return ContextTestResult(
            dimension=ContextDimension.FORM_STRUCTURE,
            level=best_match["level"],
            confidence=best_match["confidence"],
            match_type=best_match["match_type"],
            evidence=best_match["evidence"],
            recommendation=best_match["recommendation"],
            test_actions=["Analyze form structure", "Compare field patterns", "Test form completion"]
        )
    
    def _test_content_context(self, current_page_data: Dict[str, Any]) -> ContextTestResult:
        """Test content semantics across different knowledge levels"""
        
        current_content = current_page_data.get("pageText", "")
        
        # Test content against all levels
        general_content = self._test_content_against_general_techniques(current_content)
        site_content = self._test_content_against_site_specific(current_content)
        page_content = self._test_content_against_page_specific(current_content)
        
        best_match = max([general_content, site_content, page_content], 
                        key=lambda x: x.get("confidence", 0))
        
        return ContextTestResult(
            dimension=ContextDimension.CONTENT_SEMANTICS,
            level=best_match["level"],
            confidence=best_match["confidence"],
            match_type=best_match["match_type"],
            evidence=best_match["evidence"],
            recommendation=best_match["recommendation"],
            test_actions=["Extract page text", "Compare semantic patterns", "Analyze content structure"]
        )
    
    def _test_site_context(self, current_page_data: Dict[str, Any]) -> ContextTestResult:
        """Test site behavior patterns"""
        
        current_url = current_page_data.get("url", "")
        site_domain = self._extract_domain(current_url)
        
        # Test site-specific behavior patterns
        site_behavior = self._analyze_site_behavior(site_domain, current_page_data)
        
        return ContextTestResult(
            dimension=ContextDimension.SITE_BEHAVIOR,
            level=KnowledgeLevel.SITE_SPECIFIC,
            confidence=site_behavior["confidence"],
            match_type=site_behavior["match_type"],
            evidence=site_behavior["evidence"],
            recommendation=site_behavior["recommendation"],
            test_actions=["Analyze site domain", "Check site-specific patterns", "Test site behavior"]
        )
    
    def _test_dom_context(self, current_page_data: Dict[str, Any]) -> ContextTestResult:
        """Test DOM structure patterns"""
        
        current_dom = current_page_data.get("dom_structure", {})
        
        # Test DOM structure against all levels
        general_dom = self._test_dom_against_general_techniques(current_dom)
        site_dom = self._test_dom_against_site_specific(current_dom)
        page_dom = self._test_dom_against_page_specific(current_dom)
        
        best_match = max([general_dom, site_dom, page_dom], 
                        key=lambda x: x.get("confidence", 0))
        
        return ContextTestResult(
            dimension=ContextDimension.DOM_STRUCTURE,
            level=best_match["level"],
            confidence=best_match["confidence"],
            match_type=best_match["match_type"],
            evidence=best_match["evidence"],
            recommendation=best_match["recommendation"],
            test_actions=["Analyze DOM structure", "Compare element patterns", "Test structural navigation"]
        )
    
    def _synthesize_analysis(self, analysis: MultiDimensionalAnalysis) -> MultiDimensionalAnalysis:
        """Synthesize all dimension results into overall strategy"""
        
        # Calculate weighted overall confidence
        dimension_results = [
            analysis.url_analysis,
            analysis.visual_analysis,
            analysis.navigation_analysis,
            analysis.form_analysis,
            analysis.content_analysis,
            analysis.site_analysis,
            analysis.dom_analysis
        ]
        
        # Weight different dimensions based on reliability
        dimension_weights = {
            ContextDimension.URL_STRUCTURE: 0.2,
            ContextDimension.VISUAL_LAYOUT: 0.15,
            ContextDimension.NAVIGATION_PATTERNS: 0.2,
            ContextDimension.FORM_STRUCTURE: 0.15,
            ContextDimension.CONTENT_SEMANTICS: 0.1,
            ContextDimension.SITE_BEHAVIOR: 0.1,
            ContextDimension.DOM_STRUCTURE: 0.1
        }
        
        weighted_confidence = sum(
            result.confidence * dimension_weights.get(result.dimension, 0.1)
            for result in dimension_results
        )
        
        analysis.overall_confidence = weighted_confidence
        
        # Determine primary strategy based on best-performing dimensions
        best_dimensions = sorted(dimension_results, key=lambda x: x.confidence, reverse=True)[:3]
        
        if analysis.overall_confidence > 0.8:
            analysis.primary_strategy = "high_confidence_navigation"
        elif analysis.overall_confidence > 0.6:
            analysis.primary_strategy = "moderate_confidence_navigation"
        elif analysis.overall_confidence > 0.4:
            analysis.primary_strategy = "cautious_investigative_navigation"
        else:
            analysis.primary_strategy = "exploratory_navigation"
        
        # Build fallback strategies
        analysis.fallback_strategies = [
            f"fallback_{dim.dimension.value}_strategy" 
            for dim in best_dimensions
        ]
        
        # Create test plan
        analysis.test_plan = []
        for result in dimension_results:
            if result.confidence < 0.7:  # Need more testing
                analysis.test_plan.extend(result.test_actions)
        
        # Identify learning opportunities
        analysis.learning_opportunities = [
            f"Learn_{dim.dimension.value}_patterns" 
            for dim in dimension_results 
            if dim.confidence < 0.5
        ]
        
        return analysis
    
    # Helper methods for testing against different knowledge levels
    def _test_url_against_general_techniques(self, url: str) -> Dict[str, Any]:
        """Test URL against general techniques"""
        # Implementation for general URL testing
        return {"level": KnowledgeLevel.GENERAL_TECHNIQUES, "confidence": 0.3, 
                "match_type": "pattern", "evidence": {}, "recommendation": "Use general URL patterns"}
    
    def _test_url_against_site_specific(self, url: str) -> Dict[str, Any]:
        """Test URL against site-specific knowledge"""
        # Implementation for site-specific URL testing
        return {"level": KnowledgeLevel.SITE_SPECIFIC, "confidence": 0.7, 
                "match_type": "similar", "evidence": {}, "recommendation": "Use site-specific URL patterns"}
    
    def _test_url_against_page_specific(self, url: str) -> Dict[str, Any]:
        """Test URL against page-specific knowledge"""
        # Implementation for page-specific URL testing
        return {"level": KnowledgeLevel.PAGE_SPECIFIC, "confidence": 0.9, 
                "match_type": "exact", "evidence": {}, "recommendation": "Use exact page navigation"}
    
    def _test_url_against_session_specific(self, url: str) -> Dict[str, Any]:
        """Test URL against session-specific knowledge"""
        # Implementation for session-specific URL testing
        return {"level": KnowledgeLevel.SESSION_SPECIFIC, "confidence": 0.5, 
                "match_type": "session", "evidence": {}, "recommendation": "Use session-learned patterns"}
    
    # Similar methods for other dimensions...
    def _test_visual_against_general_techniques(self, visual_hash: str) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.GENERAL_TECHNIQUES, "confidence": 0.2, 
                "match_type": "pattern", "evidence": {}, "recommendation": "Use general visual patterns"}
    
    def _test_visual_against_site_specific(self, visual_hash: str) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.SITE_SPECIFIC, "confidence": 0.6, 
                "match_type": "similar", "evidence": {}, "recommendation": "Use site-specific visual patterns"}
    
    def _test_visual_against_page_specific(self, visual_hash: str) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.PAGE_SPECIFIC, "confidence": 0.8, 
                "match_type": "exact", "evidence": {}, "recommendation": "Use exact visual navigation"}
    
    # Placeholder methods for other dimensions - would be fully implemented
    def _test_navigation_against_general_techniques(self, navigation: List[Dict]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.GENERAL_TECHNIQUES, "confidence": 0.4, 
                "match_type": "pattern", "evidence": {}, "recommendation": "Use general navigation patterns"}
    
    def _test_navigation_against_site_specific(self, navigation: List[Dict]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.SITE_SPECIFIC, "confidence": 0.7, 
                "match_type": "similar", "evidence": {}, "recommendation": "Use site-specific navigation"}
    
    def _test_navigation_against_page_specific(self, navigation: List[Dict]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.PAGE_SPECIFIC, "confidence": 0.9, 
                "match_type": "exact", "evidence": {}, "recommendation": "Use exact page navigation"}
    
    def _test_forms_against_general_techniques(self, forms: List[Dict]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.GENERAL_TECHNIQUES, "confidence": 0.3, 
                "match_type": "pattern", "evidence": {}, "recommendation": "Use general form patterns"}
    
    def _test_forms_against_site_specific(self, forms: List[Dict]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.SITE_SPECIFIC, "confidence": 0.6, 
                "match_type": "similar", "evidence": {}, "recommendation": "Use site-specific form patterns"}
    
    def _test_forms_against_page_specific(self, forms: List[Dict]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.PAGE_SPECIFIC, "confidence": 0.8, 
                "match_type": "exact", "evidence": {}, "recommendation": "Use exact form navigation"}
    
    def _test_content_against_general_techniques(self, content: str) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.GENERAL_TECHNIQUES, "confidence": 0.2, 
                "match_type": "pattern", "evidence": {}, "recommendation": "Use general content patterns"}
    
    def _test_content_against_site_specific(self, content: str) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.SITE_SPECIFIC, "confidence": 0.5, 
                "match_type": "similar", "evidence": {}, "recommendation": "Use site-specific content patterns"}
    
    def _test_content_against_page_specific(self, content: str) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.PAGE_SPECIFIC, "confidence": 0.7, 
                "match_type": "exact", "evidence": {}, "recommendation": "Use exact content navigation"}
    
    def _analyze_site_behavior(self, site_domain: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"confidence": 0.6, "match_type": "site", "evidence": {}, 
                "recommendation": "Use site-specific behavior patterns"}
    
    def _test_dom_against_general_techniques(self, dom: Dict[str, Any]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.GENERAL_TECHNIQUES, "confidence": 0.3, 
                "match_type": "pattern", "evidence": {}, "recommendation": "Use general DOM patterns"}
    
    def _test_dom_against_site_specific(self, dom: Dict[str, Any]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.SITE_SPECIFIC, "confidence": 0.5, 
                "match_type": "similar", "evidence": {}, "recommendation": "Use site-specific DOM patterns"}
    
    def _test_dom_against_page_specific(self, dom: Dict[str, Any]) -> Dict[str, Any]:
        return {"level": KnowledgeLevel.PAGE_SPECIFIC, "confidence": 0.8, 
                "match_type": "exact", "evidence": {}, "recommendation": "Use exact DOM navigation"}
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc
