#!/usr/bin/env python3
"""
Ghostbusters Consultation Node
==============================

Implements "Ghostbusters Consultation Mode" - autonomous investigation and analysis
that runs independently and returns with findings and recommendations.

This is for very low confidence situations where the system doesn't even want to
ask the user - it just goes off to investigate and comes back with results.
"""

import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import AIMessage
from langgraph_devpost_state import DevPostState, add_error, update_performance_metrics


class GhostbustersConsultation:
    """Handles autonomous Ghostbusters investigation and consultation"""
    
    def __init__(self):
        self.investigation_history = []
        self.test_results = {}
        self.recommendations = []
        self.consultation_id = f"gb_consult_{int(time.time())}"
    
    def run_autonomous_investigation(self, state: DevPostState) -> Dict[str, Any]:
        """Run autonomous investigation and return findings"""
        
        print(f"🚨 Ghostbusters Consultation {self.consultation_id} - Starting Investigation")
        
        start_time = time.time()
        current_page_data = state.get("session_save_data", {}).get("current_page_data", {})
        confidence = state.get("session_recovery", {}).get("confidence", 0.0)
        
        # Ghostbusters autonomous exclamations
        autonomous_exclamations = [
            "🚨 GHOSTBUSTERS AUTONOMOUS MODE - We're going in!",
            "🛑 Stand back! Ghostbusters are taking over!",
            "🚨 Emergency protocols activated - autonomous investigation initiated!",
            "🛑 This is too dangerous for human interaction - Ghostbusters deploying!",
            "🚨 Critical situation detected - executing autonomous recovery protocol!",
            "🛑 Ghostbusters emergency response - investigating without human guidance!",
            "🚨 Autonomous mode: We're going to figure this out ourselves!",
            "🛑 Too risky for human consultation - Ghostbusters taking control!"
        ]
        
        investigation_start = random.choice(autonomous_exclamations)
        
        # Store investigation start
        self.investigation_history.append({
            "timestamp": time.time(),
            "phase": "investigation_start",
            "message": investigation_start,
            "confidence": confidence
        })
        
        # Run comprehensive investigation
        investigation_results = self._run_comprehensive_investigation(current_page_data, state)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(investigation_results, confidence)
        
        # Create consultation report
        consultation_report = {
            "consultation_id": self.consultation_id,
            "start_time": start_time,
            "end_time": time.time(),
            "duration": time.time() - start_time,
            "confidence": confidence,
            "investigation_results": investigation_results,
            "test_results": self.test_results,
            "recommendations": recommendations,
            "primary_strategy": recommendations.get("primary_strategy", "unknown"),
            "similarity_type": investigation_results.get("similarity_type", "unknown"),
            "recommendation": recommendations.get("summary", "No clear recommendation"),
            "detailed_recommendation": recommendations.get("detailed", "Investigation completed"),
            "risk_assessment": self._assess_risk(investigation_results),
            "next_steps": recommendations.get("next_steps", [])
        }
        
        # Store investigation completion
        self.investigation_history.append({
            "timestamp": time.time(),
            "phase": "investigation_complete",
            "consultation_report": consultation_report,
            "success": True
        })
        
        print(f"   Ghostbusters investigation completed in {consultation_report['duration']:.2f}s")
        
        return consultation_report
    
    def _run_comprehensive_investigation(self, page_data: Dict[str, Any], state: DevPostState) -> Dict[str, Any]:
        """Run comprehensive investigation of the current situation"""
        
        print("   🔍 Running comprehensive investigation...")
        
        investigation = {
            "page_analysis": self._analyze_page_structure(page_data),
            "navigation_analysis": self._analyze_navigation_elements(page_data),
            "form_analysis": self._analyze_form_elements(page_data),
            "content_analysis": self._analyze_page_content(page_data),
            "similarity_analysis": self._analyze_similarity_patterns(page_data, state),
            "risk_factors": self._identify_risk_factors(page_data),
            "opportunities": self._identify_opportunities(page_data)
        }
        
        # Run specific tests
        self.test_results = self._run_diagnostic_tests(page_data, state)
        
        # Determine similarity type
        investigation["similarity_type"] = self._determine_similarity_type(investigation, self.test_results)
        
        print(f"   Investigation complete: {investigation['similarity_type']} similarity detected")
        
        return investigation
    
    def _analyze_page_structure(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the overall page structure"""
        
        analysis = {
            "url_pattern": self._analyze_url_pattern(page_data.get("url", "")),
            "title_analysis": self._analyze_title(page_data.get("title", "")),
            "navigation_count": len(page_data.get("navigation", [])),
            "button_count": len(page_data.get("buttons", [])),
            "form_elements": self._count_form_elements(page_data),
            "content_length": len(page_data.get("pageText", "")),
            "structure_type": self._classify_page_structure(page_data)
        }
        
        return analysis
    
    def _analyze_url_pattern(self, url: str) -> Dict[str, Any]:
        """Analyze URL patterns for clues"""
        
        if not url:
            return {"pattern": "unknown", "domain": "unknown", "path_type": "unknown"}
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        return {
            "pattern": "devpost" if "devpost" in parsed.netloc.lower() else "other",
            "domain": parsed.netloc,
            "path_type": "form" if any(word in parsed.path.lower() for word in ["form", "submit", "create"]) else "navigation",
            "has_params": bool(parsed.query),
            "is_secure": parsed.scheme == "https"
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
            "length": len(title)
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
            "submit_buttons": 0
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
    
    def _analyze_navigation_elements(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze navigation elements for patterns"""
        
        navigation = page_data.get("navigation", [])
        
        analysis = {
            "total_elements": len(navigation),
            "button_types": {},
            "common_texts": {},
            "href_patterns": {},
            "interaction_patterns": []
        }
        
        for element in navigation:
            # Analyze button types
            element_type = element.get("type", "unknown")
            analysis["button_types"][element_type] = analysis["button_types"].get(element_type, 0) + 1
            
            # Analyze text content
            text = element.get("text", "").strip()
            if text:
                analysis["common_texts"][text] = analysis["common_texts"].get(text, 0) + 1
            
            # Analyze href patterns
            href = element.get("href", "")
            if href:
                from urllib.parse import urlparse
                parsed = urlparse(href)
                domain = parsed.netloc
                analysis["href_patterns"][domain] = analysis["href_patterns"].get(domain, 0) + 1
        
        return analysis
    
    def _analyze_form_elements(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze form elements specifically"""
        
        buttons = page_data.get("buttons", [])
        
        analysis = {
            "total_buttons": len(buttons),
            "button_texts": [btn.get("text", "").strip() for btn in buttons],
            "button_types": [btn.get("type", "unknown") for btn in buttons],
            "form_indicators": self._identify_form_indicators(page_data),
            "completion_indicators": self._identify_completion_indicators(buttons)
        }
        
        return analysis
    
    def _identify_form_indicators(self, page_data: Dict[str, Any]) -> List[str]:
        """Identify indicators that this is a form page"""
        
        indicators = []
        page_text = page_data.get("pageText", "").lower()
        
        form_keywords = ["submit", "save", "continue", "next", "form", "required", "field"]
        for keyword in form_keywords:
            if keyword in page_text:
                indicators.append(f"contains_{keyword}")
        
        return indicators
    
    def _identify_completion_indicators(self, buttons: List[Dict]) -> List[str]:
        """Identify indicators of form completion actions"""
        
        indicators = []
        
        for button in buttons:
            text = button.get("text", "").lower()
            if any(word in text for word in ["submit", "save", "continue", "next", "finish"]):
                indicators.append(f"completion_button_{text}")
        
        return indicators
    
    def _analyze_page_content(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze page content for context"""
        
        page_text = page_data.get("pageText", "")
        
        analysis = {
            "content_length": len(page_text),
            "word_count": len(page_text.split()),
            "key_phrases": self._extract_key_phrases(page_text),
            "content_type": self._classify_content_type(page_text),
            "language_indicators": self._identify_language_patterns(page_text)
        }
        
        return analysis
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from page text"""
        
        # Simple key phrase extraction
        phrases = []
        text_lower = text.lower()
        
        important_phrases = [
            "project overview", "project details", "team members", "manage team",
            "additional information", "submission", "hackathon", "devpost",
            "save and continue", "submit", "required field", "validation"
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
    
    def _analyze_similarity_patterns(self, page_data: Dict[str, Any], state: DevPostState) -> Dict[str, Any]:
        """Analyze patterns that might indicate similarity to known pages"""
        
        # This would integrate with the existing similarity analysis
        similarity_data = state.get("session_recovery", {})
        
        analysis = {
            "confidence": similarity_data.get("confidence", 0.0),
            "similarity_type": similarity_data.get("similarity_type", "unknown"),
            "url_similarity": self._calculate_url_similarity(page_data.get("url", "")),
            "content_similarity": self._calculate_content_similarity(page_data),
            "structure_similarity": self._calculate_structure_similarity(page_data)
        }
        
        return analysis
    
    def _calculate_url_similarity(self, url: str) -> float:
        """Calculate URL similarity to known patterns"""
        
        if not url:
            return 0.0
        
        # Simple URL similarity calculation
        if "devpost.com" in url:
            return 0.8
        elif any(word in url.lower() for word in ["form", "submit", "create"]):
            return 0.6
        else:
            return 0.2
    
    def _calculate_content_similarity(self, page_data: Dict[str, Any]) -> float:
        """Calculate content similarity to known patterns"""
        
        page_text = page_data.get("pageText", "").lower()
        
        # Look for DevPost-specific content
        devpost_indicators = ["hackathon", "project", "submission", "team", "devpost"]
        matches = sum(1 for indicator in devpost_indicators if indicator in page_text)
        
        return matches / len(devpost_indicators) if devpost_indicators else 0.0
    
    def _calculate_structure_similarity(self, page_data: Dict[str, Any]) -> float:
        """Calculate structural similarity to known patterns"""
        
        form_elements = self._count_form_elements(page_data)
        total_elements = sum(form_elements.values())
        
        # Simple structural similarity based on form elements
        if total_elements > 3:
            return 0.8  # Likely a form page
        elif total_elements > 0:
            return 0.5  # Some form elements
        else:
            return 0.2  # No form elements
    
    def _identify_risk_factors(self, page_data: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        
        risks = []
        
        # Check for error indicators
        page_text = page_data.get("pageText", "").lower()
        if any(word in page_text for word in ["error", "invalid", "failed", "timeout"]):
            risks.append("error_indicators")
        
        # Check for authentication issues
        if any(word in page_text for word in ["login", "sign in", "authentication"]):
            risks.append("authentication_required")
        
        # Check for dynamic content issues
        if len(page_data.get("navigation", [])) == 0:
            risks.append("no_navigation_elements")
        
        return risks
    
    def _identify_opportunities(self, page_data: Dict[str, Any]) -> List[str]:
        """Identify opportunities for successful navigation"""
        
        opportunities = []
        
        # Check for clear navigation paths
        buttons = page_data.get("buttons", [])
        if any(btn.get("text", "").lower() in ["continue", "next", "submit"] for btn in buttons):
            opportunities.append("clear_navigation_path")
        
        # Check for form completion opportunities
        if self._count_form_elements(page_data)["input_fields"] > 0:
            opportunities.append("form_completion_possible")
        
        # Check for familiar patterns
        if "devpost.com" in page_data.get("url", ""):
            opportunities.append("familiar_domain")
        
        return opportunities
    
    def _run_diagnostic_tests(self, page_data: Dict[str, Any], state: DevPostState) -> Dict[str, Any]:
        """Run specific diagnostic tests"""
        
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
        
        return tests
    
    def _determine_similarity_type(self, investigation: Dict[str, Any], test_results: Dict[str, Any]) -> str:
        """Determine the overall similarity type based on investigation"""
        
        # Use investigation results to determine similarity
        if test_results.get("url_recognized") and investigation["page_analysis"]["url_pattern"]["pattern"] == "devpost":
            return "devpost_known"
        elif investigation["form_analysis"]["total_buttons"] > 0:
            return "form_based"
        elif investigation["navigation_analysis"]["total_elements"] > 5:
            return "navigation_heavy"
        elif investigation["content_analysis"]["content_type"] == "project_content":
            return "content_based"
        else:
            return "unknown_pattern"
    
    def _generate_recommendations(self, investigation: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Generate recommendations based on investigation results"""
        
        recommendations = {
            "primary_strategy": "unknown",
            "summary": "Investigation completed",
            "detailed": "No specific recommendation available",
            "next_steps": [],
            "confidence_boost": 0.0
        }
        
        # Determine primary strategy
        similarity_type = investigation.get("similarity_type", "unknown")
        
        if similarity_type == "devpost_known":
            recommendations["primary_strategy"] = "devpost_adapted"
            recommendations["summary"] = "Known DevPost page - use adapted navigation"
            recommendations["detailed"] = "This appears to be a DevPost page with familiar patterns. Use DevPost-specific navigation strategies."
            recommendations["next_steps"] = ["Apply DevPost navigation model", "Focus on form completion", "Use semantic navigation"]
            recommendations["confidence_boost"] = 0.3
            
        elif similarity_type == "form_based":
            recommendations["primary_strategy"] = "form_focused"
            recommendations["summary"] = "Form page detected - focus on form completion"
            recommendations["detailed"] = "This appears to be a form page. Focus on identifying and completing form fields."
            recommendations["next_steps"] = ["Analyze form fields", "Complete required fields", "Submit form"]
            recommendations["confidence_boost"] = 0.2
            
        elif similarity_type == "navigation_heavy":
            recommendations["primary_strategy"] = "navigation_focused"
            recommendations["summary"] = "Navigation page detected - focus on navigation elements"
            recommendations["detailed"] = "This page has many navigation elements. Focus on identifying the correct navigation path."
            recommendations["next_steps"] = ["Analyze navigation options", "Identify target navigation", "Execute navigation"]
            recommendations["confidence_boost"] = 0.1
            
        else:
            recommendations["primary_strategy"] = "exploratory"
            recommendations["summary"] = "Unknown page type - use exploratory approach"
            recommendations["detailed"] = "This page type is not clearly identifiable. Use exploratory navigation with caution."
            recommendations["next_steps"] = ["Explore page structure", "Identify interactive elements", "Proceed with caution"]
            recommendations["confidence_boost"] = 0.0
        
        return recommendations
    
    def _assess_risk(self, investigation: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the risk level of proceeding with navigation"""
        
        risk_factors = investigation.get("risk_factors", [])
        opportunities = investigation.get("opportunities", [])
        
        risk_score = len(risk_factors) * 0.3
        opportunity_score = len(opportunities) * 0.2
        
        overall_risk = max(0.0, min(1.0, risk_score - opportunity_score))
        
        if overall_risk < 0.3:
            risk_level = "low"
        elif overall_risk < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "level": risk_level,
            "score": overall_risk,
            "factors": risk_factors,
            "opportunities": opportunities
        }


def ghostbusters_consultation_node(state: DevPostState) -> DevPostState:
    """
    Node: Ghostbusters Consultation
    
    Runs autonomous investigation when confidence is critically low.
    This mode operates independently and returns with findings and recommendations.
    """
    
    print("🚨 Ghostbusters Consultation Node")
    start_time = time.time()
    
    try:
        # Initialize Ghostbusters consultation if not exists
        if "ghostbusters_consultation" not in state:
            state["ghostbusters_consultation"] = GhostbustersConsultation()
        
        consultation = state["ghostbusters_consultation"]
        
        # Run autonomous investigation
        consultation_report = consultation.run_autonomous_investigation(state)
        
        # Store the report in state
        state["ghostbusters_report"] = consultation_report
        
        # Create summary message
        summary_message = f"📡 GHOSTBUSTERS CONSULTATION COMPLETE 📡\n\n"
        summary_message += f"Consultation ID: {consultation_report['consultation_id']}\n"
        summary_message += f"Investigation Duration: {consultation_report['duration']:.2f}s\n"
        summary_message += f"Primary Strategy: {consultation_report['primary_strategy']}\n"
        summary_message += f"Risk Assessment: {consultation_report['risk_assessment']['level']}\n"
        summary_message += f"Recommendation: {consultation_report['recommendation']}\n\n"
        summary_message += "🎯 Returning to Prompt Mode for final decision..."
        
        state["messages"].append(AIMessage(content=summary_message))
        
        # Set up return to Prompt Mode
        state["ghostbusters_mode"] = False
        state["prompt_mode_active"] = True
        state["awaiting_ghostbusters_report"] = True
        state["user_input_required"] = True
        state["next_mode"] = "prompt_mode_consensus"
        
        # Update performance metrics
        consultation_time = time.time() - start_time
        update_performance_metrics(state, {
            "ghostbusters_consultation_time": consultation_time,
            "investigation_duration": consultation_report['duration'],
            "primary_strategy": consultation_report['primary_strategy'],
            "risk_level": consultation_report['risk_assessment']['level']
        })
        
        print(f"   Ghostbusters consultation completed in {consultation_time:.2f}s")
        print(f"   Primary strategy: {consultation_report['primary_strategy']}")
        
    except Exception as e:
        add_error(state, f"Ghostbusters consultation failed: {str(e)}")
    
    return state
