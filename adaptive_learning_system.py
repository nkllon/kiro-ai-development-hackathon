#!/usr/bin/env python3
"""
Adaptive Learning System
========================

A comprehensive learning system that can adapt and patch itself
during the session, learning from both successes and failures.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Self-adapting navigation with real-time learning
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright
from typing import Dict, List, Any, Optional
import re
from collections import defaultdict
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class AdaptiveLearningSystem:
    """Comprehensive adaptive learning system for navigation."""
    
    def __init__(self, cdp_url: str = "http://localhost:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Learning components
        self.knowledge_base = {
            "patterns": {},
            "success_indicators": [],
            "failure_patterns": [],
            "adaptations": [],
            "heuristics": {},
            "session_memory": []
        }
        
        # Performance tracking
        self.performance = {
            "navigations_attempted": 0,
            "navigations_successful": 0,
            "patterns_discovered": 0,
            "adaptations_created": 0,
            "heuristics_updated": 0
        }
        
        # Learning parameters
        self.learning_config = {
            "confidence_threshold": 0.7,
            "adaptation_threshold": 3,
            "pattern_decay": 0.95,
            "learning_rate": 0.1
        }
        
        # Load existing knowledge
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load existing knowledge base."""
        try:
            with open("adaptive_knowledge_base.json", "r") as f:
                self.knowledge_base = json.load(f)
            print(f"🧠 Loaded knowledge base with {len(self.knowledge_base['patterns'])} patterns")
        except FileNotFoundError:
            print("🧠 Starting with empty knowledge base")
    
    def _save_knowledge_base(self):
        """Save knowledge base."""
        try:
            with open("adaptive_knowledge_base.json", "w") as f:
                json.dump(self.knowledge_base, f, indent=2)
            print(f"💾 Saved knowledge base")
        except Exception as e:
            print(f"❌ Failed to save knowledge base: {e}")
    
    def _observe_environment(self) -> Dict[str, Any]:
        """Comprehensive environment observation."""
        observation = {
            "timestamp": time.time(),
            "url": self.page.url,
            "title": self.page.title(),
            "step_info": self._extract_step_information(),
            "navigation_elements": self._catalog_navigation_elements(),
            "form_structures": self._analyze_form_structures(),
            "page_indicators": self._detect_page_indicators(),
            "interaction_possibilities": self._identify_interaction_possibilities()
        }
        
        self.knowledge_base["session_memory"].append(observation)
        return observation
    
    def _extract_step_information(self) -> Dict[str, Any]:
        """Extract comprehensive step information."""
        step_info = {
            "current_step": None,
            "available_steps": [],
            "step_sequence": [],
            "navigation_state": "unknown"
        }
        
        # Extract from URL
        url_match = re.search(r'/submission/([^/]+)/([^/]+)/', self.page.url)
        if url_match:
            step_info["submission_id"] = url_match.group(1)
            step_info["current_step"] = url_match.group(2)
        
        # Extract from step navigation
        step_links = self.page.query_selector_all("#steps-navigation a.step")
        for step in step_links:
            if step.is_visible() and step.is_enabled():
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                href = step.get_attribute("href") or ""
                
                step_data = {
                    "text": text,
                    "classes": classes,
                    "href": href,
                    "is_current": "current" in classes,
                    "is_completed": "completed" in classes,
                    "is_available": True
                }
                
                step_info["available_steps"].append(step_data)
                
                if step_data["is_current"]:
                    step_info["navigation_state"] = "current"
                elif step_data["is_completed"]:
                    step_info["navigation_state"] = "completed"
        
        return step_info
    
    def _catalog_navigation_elements(self) -> List[Dict[str, Any]]:
        """Catalog all navigation elements."""
        elements = []
        
        # Step navigation links
        step_links = self.page.query_selector_all("#steps-navigation a.step")
        for step in step_links:
            elements.append({
                "type": "step_link",
                "text": step.text_content().strip(),
                "classes": step.get_attribute("class") or "",
                "href": step.get_attribute("href") or "",
                "visible": step.is_visible(),
                "enabled": step.is_enabled(),
                "confidence": self._calculate_element_confidence(step, "step_link")
            })
        
        # Buttons
        buttons = self.page.query_selector_all("button, input[type='button'], input[type='submit']")
        for button in buttons:
            if button.is_visible() and button.is_enabled():
                elements.append({
                    "type": "button",
                    "text": button.text_content().strip(),
                    "classes": button.get_attribute("class") or "",
                    "visible": True,
                    "enabled": True,
                    "confidence": self._calculate_element_confidence(button, "button")
                })
        
        # Links
        links = self.page.query_selector_all("a:not(.step)")
        for link in links:
            if link.is_visible() and link.is_enabled():
                text = link.text_content().strip()
                if text and any(word in text.lower() for word in ["next", "continue", "back", "previous", "submit"]):
                    elements.append({
                        "type": "navigation_link",
                        "text": text,
                        "href": link.get_attribute("href") or "",
                        "classes": link.get_attribute("class") or "",
                        "visible": True,
                        "enabled": True,
                        "confidence": self._calculate_element_confidence(link, "navigation_link")
                    })
        
        return elements
    
    def _calculate_element_confidence(self, element, element_type: str) -> float:
        """Calculate confidence score for element."""
        confidence = 0.0
        
        try:
            text = element.text_content().strip().lower()
            classes = element.get_attribute("class") or ""
            
            # Base confidence by type
            if element_type == "step_link":
                confidence = 0.8
            elif element_type == "button":
                confidence = 0.6
            elif element_type == "navigation_link":
                confidence = 0.7
            
            # Boost confidence for navigation keywords
            if any(word in text for word in ["next", "continue", "forward", "proceed"]):
                confidence += 0.2
            elif any(word in text for word in ["back", "previous", "return"]):
                confidence += 0.2
            elif any(word in text for word in ["submit", "save", "finish"]):
                confidence += 0.1
            
            # Boost confidence for current step
            if "current" in classes:
                confidence += 0.1
            
            # Apply learned patterns
            pattern_key = f"{element_type}_{text}"
            if pattern_key in self.knowledge_base["patterns"]:
                pattern = self.knowledge_base["patterns"][pattern_key]
                success_rate = pattern.get("success_count", 0) / max(1, pattern.get("attempt_count", 1))
                confidence = (confidence + success_rate) / 2
            
        except Exception as e:
            confidence = 0.0
        
        return min(1.0, confidence)
    
    def _analyze_form_structures(self) -> List[Dict[str, Any]]:
        """Analyze form structures on the page."""
        forms = self.page.query_selector_all("form")
        form_analysis = []
        
        for form in forms:
            form_data = {
                "action": form.get_attribute("action") or "",
                "method": form.get_attribute("method") or "get",
                "id": form.get_attribute("id") or "",
                "class": form.get_attribute("class") or "",
                "inputs": [],
                "input_count": 0
            }
            
            inputs = form.query_selector_all("input, textarea, select")
            for inp in inputs:
                input_data = {
                    "type": inp.get_attribute("type") or inp.tag_name,
                    "name": inp.get_attribute("name") or "",
                    "id": inp.get_attribute("id") or "",
                    "class": inp.get_attribute("class") or "",
                    "placeholder": inp.get_attribute("placeholder") or "",
                    "value": inp.get_attribute("value") or "",
                    "required": inp.get_attribute("required") is not None
                }
                form_data["inputs"].append(input_data)
            
            form_data["input_count"] = len(form_data["inputs"])
            form_analysis.append(form_data)
        
        return form_analysis
    
    def _detect_page_indicators(self) -> Dict[str, Any]:
        """Detect page state indicators."""
        indicators = {}
        
        # Progress indicators
        progress_elements = self.page.query_selector_all("[class*='step'], [class*='progress'], [class*='deadline']")
        for elem in progress_elements:
            text = elem.text_content().strip()
            if text and any(word in text.lower() for word in ["step", "done", "deadline", "hours"]):
                indicators["progress"] = text
        
        # Form indicators
        form_elements = self.page.query_selector_all("form, input, textarea, select")
        indicators["form_count"] = len(form_elements)
        
        # Navigation indicators
        nav_elements = self.page.query_selector_all("#steps-navigation, .navigation, .nav")
        indicators["navigation_present"] = len(nav_elements) > 0
        
        return indicators
    
    def _identify_interaction_possibilities(self) -> List[Dict[str, Any]]:
        """Identify possible interactions."""
        possibilities = []
        
        # Navigation possibilities
        nav_elements = self.page.query_selector_all("#steps-navigation a.step")
        for element in nav_elements:
            if element.is_visible() and element.is_enabled():
                possibilities.append({
                    "type": "navigate",
                    "element": element,
                    "action": "click",
                    "target": element.text_content().strip(),
                    "confidence": self._calculate_element_confidence(element, "step_link")
                })
        
        # Form interactions
        buttons = self.page.query_selector_all("button, input[type='button'], input[type='submit']")
        for button in buttons:
            if button.is_visible() and button.is_enabled():
                possibilities.append({
                    "type": "form_action",
                    "element": button,
                    "action": "click",
                    "target": button.text_content().strip(),
                    "confidence": self._calculate_element_confidence(button, "button")
                })
        
        return possibilities
    
    def _learn_from_interaction(self, interaction: Dict[str, Any], success: bool):
        """Learn from an interaction attempt."""
        self.performance["navigations_attempted"] += 1
        
        if success:
            self.performance["navigations_successful"] += 1
            self._learn_success_pattern(interaction)
        else:
            self._learn_failure_pattern(interaction)
    
    def _learn_success_pattern(self, interaction: Dict[str, Any]):
        """Learn from successful interaction."""
        element_type = interaction.get("type")
        target = interaction.get("target")
        
        if element_type and target:
            pattern_key = f"{element_type}_{target}"
            
            if pattern_key in self.knowledge_base["patterns"]:
                pattern = self.knowledge_base["patterns"][pattern_key]
                pattern["success_count"] = pattern.get("success_count", 0) + 1
                pattern["attempt_count"] = pattern.get("attempt_count", 0) + 1
            else:
                self.knowledge_base["patterns"][pattern_key] = {
                    "type": element_type,
                    "target": target,
                    "success_count": 1,
                    "attempt_count": 1,
                    "confidence": 1.0
                }
                self.performance["patterns_discovered"] += 1
                print(f"🧠 Discovered new pattern: {pattern_key}")
    
    def _learn_failure_pattern(self, interaction: Dict[str, Any]):
        """Learn from failed interaction."""
        failure = {
            "timestamp": time.time(),
            "interaction": interaction,
            "error": interaction.get("error", "unknown")
        }
        
        self.knowledge_base["failure_patterns"].append(failure)
        
        # Create adaptation if we see repeated failures
        if len(self.knowledge_base["failure_patterns"]) >= self.learning_config["adaptation_threshold"]:
            self._create_adaptation()
    
    def _create_adaptation(self):
        """Create an adaptation based on failure patterns."""
        recent_failures = self.knowledge_base["failure_patterns"][-self.learning_config["adaptation_threshold"]:]
        
        # Analyze common failure patterns
        error_counts = defaultdict(int)
        for failure in recent_failures:
            error_counts[failure["error"]] += 1
        
        if error_counts:
            most_common_error = max(error_counts, key=error_counts.get)
            
            adaptation = {
                "timestamp": time.time(),
                "trigger": most_common_error,
                "solution": self._generate_adaptation_solution(most_common_error),
                "applied": False,
                "success_count": 0
            }
            
            self.knowledge_base["adaptations"].append(adaptation)
            self.performance["adaptations_created"] += 1
            print(f"🔧 Created adaptation for: {most_common_error}")
    
    def _generate_adaptation_solution(self, error: str) -> str:
        """Generate solution for error."""
        solutions = {
            "Element is not attached to the DOM": "reconnect_and_retry",
            "Timeout exceeded": "force_click_and_wait",
            "Element not visible": "scroll_and_retry",
            "Element not enabled": "wait_and_retry"
        }
        return solutions.get(error, "retry_with_different_strategy")
    
    def _apply_adaptations(self, element, action: str) -> bool:
        """Apply learned adaptations."""
        for adaptation in self.knowledge_base["adaptations"]:
            if not adaptation.get("applied") and adaptation["trigger"] in str(action):
                solution = adaptation["solution"]
                print(f"🔧 Applying adaptation: {solution}")
                
                try:
                    if solution == "reconnect_and_retry":
                        self._reconnect_browser()
                    elif solution == "force_click_and_wait":
                        element.click(force=True)
                        time.sleep(2)
                    elif solution == "scroll_and_retry":
                        element.scroll_into_view_if_needed()
                        element.click()
                    elif solution == "wait_and_retry":
                        time.sleep(1)
                        element.click()
                    
                    adaptation["applied"] = True
                    adaptation["success_count"] += 1
                    return True
                except Exception as e:
                    print(f"❌ Adaptation failed: {e}")
        
        return False
    
    def _reconnect_browser(self):
        """Reconnect to browser."""
        try:
            if self.playwright:
                self.playwright.stop()
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0]
            self.page = self.context.pages[0]
            
            print("🔄 Reconnected to browser")
        except Exception as e:
            print(f"❌ Reconnection failed: {e}")
    
    def adaptive_navigate(self):
        """Main adaptive navigation function."""
        try:
            self.playwright = sync_playwright().start()
            
            # Connect to browser
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0]
            self.page = self.context.pages[0]
            
            print(f"✅ Connected to: {self.page.url}")
            
            # Wait for page to be ready
            self.page.wait_for_load_state("networkidle")
            
            # Adaptive navigation loop
            navigation_count = 0
            max_navigations = 10
            
            while navigation_count < max_navigations:
                print(f"\n{'='*60}")
                print(f"🧠 Adaptive Navigation Step {navigation_count + 1}")
                print(f"📊 Performance: {self.performance['navigations_successful']}/{self.performance['navigations_attempted']} success rate")
                
                # Observe environment
                environment = self._observe_environment()
                
                # Find best interaction
                best_interaction = self._find_best_interaction(environment)
                
                if not best_interaction:
                    print("❌ No suitable interaction found")
                    break
                
                # Execute interaction with learning
                success = self._execute_interaction_with_learning(best_interaction, environment)
                
                if success:
                    navigation_count += 1
                    print(f"✅ Interaction successful!")
                else:
                    print(f"❌ Interaction failed, learning from failure...")
                
                # Save knowledge
                self._save_knowledge_base()
            
            print(f"\n🏁 Adaptive navigation complete after {navigation_count} steps")
            print(f"📊 Final performance: {self.performance}")
            
        except Exception as e:
            print(f"❌ Adaptive navigation failed: {e}")
        finally:
            if self.playwright:
                self.playwright.stop()
    
    def _find_best_interaction(self, environment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the best interaction based on current environment."""
        possibilities = environment["interaction_possibilities"]
        
        if not possibilities:
            return None
        
        # Sort by confidence
        possibilities.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Filter by confidence threshold
        high_confidence = [p for p in possibilities if p["confidence"] >= self.learning_config["confidence_threshold"]]
        
        if high_confidence:
            return high_confidence[0]
        
        # If no high confidence, return best available
        return possibilities[0] if possibilities else None
    
    def _execute_interaction_with_learning(self, interaction: Dict[str, Any], environment: Dict[str, Any]) -> bool:
        """Execute interaction with learning."""
        element = interaction["element"]
        action = interaction["action"]
        target = interaction["target"]
        
        print(f"🎯 Executing: {action} on {target}")
        
        # Record initial state
        initial_url = self.page.url
        initial_title = self.page.title()
        
        try:
            # Apply adaptations if needed
            adaptation_applied = self._apply_adaptations(element, action)
            
            # Execute action
            if not adaptation_applied:
                if action == "click":
                    element.click()
                else:
                    print(f"❌ Unknown action: {action}")
                    return False
            
            # Monitor for success
            success = self._monitor_success(initial_url, initial_title)
            
            # Learn from attempt
            interaction["success"] = success
            interaction["error"] = None if success else "monitoring_failed"
            self._learn_from_interaction(interaction, success)
            
            return success
            
        except Exception as e:
            print(f"❌ Interaction failed: {e}")
            
            # Learn from failure
            interaction["success"] = False
            interaction["error"] = str(e)
            self._learn_from_interaction(interaction, False)
            
            return False
    
    def _monitor_success(self, initial_url: str, initial_title: str) -> bool:
        """Monitor for interaction success."""
        for i in range(10):
            time.sleep(0.5)
            
            current_url = self.page.url
            current_title = self.page.title()
            
            # Check for changes
            if current_url != initial_url or current_title != initial_title:
                return True
        
        return False

def main():
    """Main function."""
    print("🧠 Adaptive Learning System")
    print("=" * 50)
    
    system = AdaptiveLearningSystem()
    system.adaptive_navigate()

if __name__ == "__main__":
    main()





