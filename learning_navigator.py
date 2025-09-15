#!/usr/bin/env python3
"""
Learning Navigator
=================

A navigator that learns and patches itself during the session.
Can adapt to new patterns and improve behavior in real-time.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Self-learning navigation with real-time adaptation
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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class LearningNavigator:
    """Self-learning navigator that adapts during the session."""
    
    def __init__(self, cdp_url: str = "http://localhost:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Learning system
        self.learned_patterns = {}
        self.session_observations = []
        self.success_indicators = []
        self.failure_patterns = []
        self.adaptations = []
        
        # Performance tracking
        self.navigation_stats = {
            "total_attempts": 0,
            "successful_navigations": 0,
            "failed_navigations": 0,
            "adaptations_applied": 0,
            "patterns_learned": 0
        }
        
        # Load existing knowledge
        self._load_learned_knowledge()
    
    def _load_learned_knowledge(self):
        """Load previously learned patterns and adaptations."""
        try:
            with open("learned_navigation_knowledge.json", "r") as f:
                knowledge = json.load(f)
                self.learned_patterns = knowledge.get("patterns", {})
                self.success_indicators = knowledge.get("success_indicators", [])
                self.failure_patterns = knowledge.get("failure_patterns", [])
                self.adaptations = knowledge.get("adaptations", [])
            print(f"🧠 Loaded {len(self.learned_patterns)} learned patterns")
        except FileNotFoundError:
            print("🧠 Starting with fresh knowledge")
            self.learned_patterns = {}
            self.success_indicators = []
            self.failure_patterns = []
            self.adaptations = []
    
    def _save_learned_knowledge(self):
        """Save learned patterns and adaptations."""
        try:
            knowledge = {
                "patterns": self.learned_patterns,
                "success_indicators": self.success_indicators,
                "failure_patterns": self.failure_patterns,
                "adaptations": self.adaptations,
                "last_updated": time.time()
            }
            with open("learned_navigation_knowledge.json", "w") as f:
                json.dump(knowledge, f, indent=2)
            print(f"💾 Saved learned knowledge")
        except Exception as e:
            print(f"❌ Failed to save knowledge: {e}")
    
    def _observe_page_state(self, label: str = "") -> Dict[str, Any]:
        """Observe and record current page state."""
        observation = {
            "timestamp": time.time(),
            "label": label,
            "url": self.page.url,
            "title": self.page.title(),
            "step_info": self._extract_step_info(),
            "navigation_elements": self._analyze_navigation_elements(),
            "form_elements": self._analyze_form_elements(),
            "page_indicators": self._analyze_page_indicators()
        }
        
        self.session_observations.append(observation)
        return observation
    
    def _extract_step_info(self) -> Dict[str, Any]:
        """Extract step information from URL and page."""
        step_info = {}
        
        # Extract from URL
        url_match = re.search(r'/submission/([^/]+)/([^/]+)/', self.page.url)
        if url_match:
            step_info["submission_id"] = url_match.group(1)
            step_info["current_step"] = url_match.group(2)
        
        # Extract from step navigation
        step_links = self.page.query_selector_all("#steps-navigation a.step")
        step_info["available_steps"] = []
        
        for step in step_links:
            if step.is_visible() and step.is_enabled():
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                href = step.get_attribute("href") or ""
                
                step_info["available_steps"].append({
                    "text": text,
                    "classes": classes,
                    "href": href,
                    "is_current": "current" in classes,
                    "is_completed": "completed" in classes
                })
        
        return step_info
    
    def _analyze_navigation_elements(self) -> List[Dict[str, Any]]:
        """Analyze navigation elements on the page."""
        elements = []
        
        # Step navigation
        step_links = self.page.query_selector_all("#steps-navigation a.step")
        for step in step_links:
            elements.append({
                "type": "step_link",
                "text": step.text_content().strip(),
                "classes": step.get_attribute("class") or "",
                "href": step.get_attribute("href") or "",
                "visible": step.is_visible(),
                "enabled": step.is_enabled()
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
                    "enabled": True
                })
        
        return elements
    
    def _analyze_form_elements(self) -> List[Dict[str, Any]]:
        """Analyze form elements on the page."""
        forms = self.page.query_selector_all("form")
        form_analysis = []
        
        for form in forms:
            form_data = {
                "action": form.get_attribute("action") or "",
                "method": form.get_attribute("method") or "get",
                "id": form.get_attribute("id") or "",
                "class": form.get_attribute("class") or "",
                "inputs": []
            }
            
            inputs = form.query_selector_all("input, textarea, select")
            for inp in inputs:
                form_data["inputs"].append({
                    "type": inp.get_attribute("type") or inp.tag_name,
                    "name": inp.get_attribute("name") or "",
                    "id": inp.get_attribute("id") or "",
                    "class": inp.get_attribute("class") or "",
                    "placeholder": inp.get_attribute("placeholder") or "",
                    "value": inp.get_attribute("value") or ""
                })
            
            form_analysis.append(form_data)
        
        return form_analysis
    
    def _analyze_page_indicators(self) -> Dict[str, Any]:
        """Analyze page state indicators."""
        indicators = {}
        
        # Look for step progress indicators
        progress_elements = self.page.query_selector_all("[class*='step'], [class*='progress'], [class*='deadline']")
        for elem in progress_elements:
            text = elem.text_content().strip()
            if text and any(word in text.lower() for word in ["step", "done", "deadline", "hours"]):
                indicators["progress"] = text
        
        # Look for form state indicators
        form_indicators = self.page.query_selector_all("[class*='form'], [class*='field'], [class*='input']")
        indicators["form_count"] = len(form_indicators)
        
        return indicators
    
    def _learn_from_navigation_attempt(self, attempt: Dict[str, Any], success: bool):
        """Learn from a navigation attempt."""
        self.navigation_stats["total_attempts"] += 1
        
        if success:
            self.navigation_stats["successful_navigations"] += 1
            self._learn_success_pattern(attempt)
        else:
            self.navigation_stats["failed_navigations"] += 1
            self._learn_failure_pattern(attempt)
    
    def _learn_success_pattern(self, attempt: Dict[str, Any]):
        """Learn from successful navigation."""
        # Extract success indicators
        success_indicators = []
        
        if attempt.get("url_changed"):
            success_indicators.append("url_change")
        if attempt.get("step_navigation_updated"):
            success_indicators.append("step_navigation_update")
        if attempt.get("form_content_changed"):
            success_indicators.append("form_content_change")
        if attempt.get("page_indicators_updated"):
            success_indicators.append("page_indicators_update")
        
        # Update success indicators
        for indicator in success_indicators:
            if indicator not in self.success_indicators:
                self.success_indicators.append(indicator)
                print(f"🧠 Learned new success indicator: {indicator}")
        
        # Learn element patterns
        element = attempt.get("element")
        if element:
            element_pattern = {
                "type": element.get("type"),
                "text": element.get("text"),
                "classes": element.get("classes"),
                "success_count": 1
            }
            
            pattern_key = f"{element_pattern['type']}_{element_pattern['text']}"
            if pattern_key in self.learned_patterns:
                self.learned_patterns[pattern_key]["success_count"] += 1
            else:
                self.learned_patterns[pattern_key] = element_pattern
                self.navigation_stats["patterns_learned"] += 1
                print(f"🧠 Learned new pattern: {pattern_key}")
    
    def _learn_failure_pattern(self, attempt: Dict[str, Any]):
        """Learn from failed navigation."""
        failure_pattern = {
            "timestamp": time.time(),
            "element": attempt.get("element"),
            "error": attempt.get("error"),
            "page_state": attempt.get("page_state")
        }
        
        self.failure_patterns.append(failure_pattern)
        
        # Create adaptation if we see repeated failures
        if len(self.failure_patterns) >= 3:
            self._create_adaptation()
    
    def _create_adaptation(self):
        """Create an adaptation based on failure patterns."""
        recent_failures = self.failure_patterns[-3:]
        
        # Analyze common failure patterns
        common_errors = defaultdict(int)
        for failure in recent_failures:
            if failure.get("error"):
                common_errors[failure["error"]] += 1
        
        if common_errors:
            most_common_error = max(common_errors, key=common_errors.get)
            
            # Create adaptation
            adaptation = {
                "timestamp": time.time(),
                "trigger": most_common_error,
                "solution": self._generate_adaptation_solution(most_common_error),
                "applied": False
            }
            
            self.adaptations.append(adaptation)
            self.navigation_stats["adaptations_applied"] += 1
            print(f"🔧 Created adaptation for: {most_common_error}")
    
    def _generate_adaptation_solution(self, error: str) -> str:
        """Generate a solution for a common error."""
        solutions = {
            "Element is not attached to the DOM": "reconnect_and_retry",
            "Timeout exceeded": "force_click_and_wait",
            "Element not visible": "scroll_to_element_and_retry",
            "Element not enabled": "wait_for_enable_and_retry"
        }
        
        return solutions.get(error, "retry_with_different_strategy")
    
    def _apply_adaptations(self, element, action: str):
        """Apply learned adaptations."""
        for adaptation in self.adaptations:
            if not adaptation.get("applied") and adaptation["trigger"] in str(action):
                solution = adaptation["solution"]
                print(f"🔧 Applying adaptation: {solution}")
                
                if solution == "reconnect_and_retry":
                    self._reconnect_browser()
                elif solution == "force_click_and_wait":
                    element.click(force=True)
                    time.sleep(2)
                elif solution == "scroll_to_element_and_retry":
                    element.scroll_into_view_if_needed()
                    element.click()
                
                adaptation["applied"] = True
                return True
        
        return False
    
    def _reconnect_browser(self):
        """Reconnect to browser if needed."""
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
    
    def navigate_with_learning(self):
        """Navigate with learning capabilities."""
        try:
            self.playwright = sync_playwright().start()
            
            # Connect to browser
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0]
            self.page = self.context.pages[0]
            
            print(f"✅ Connected to: {self.page.url}")
            
            # Wait for page to be ready
            self.page.wait_for_load_state("networkidle")
            
            # Learning navigation loop
            navigation_count = 0
            max_navigations = 10
            
            while navigation_count < max_navigations:
                print(f"\n{'='*60}")
                print(f"🧠 Learning Navigation Step {navigation_count + 1}")
                print(f"📊 Stats: {self.navigation_stats['successful_navigations']}/{self.navigation_stats['total_attempts']} success rate")
                
                # Observe current state
                current_state = self._observe_page_state(f"step_{navigation_count + 1}")
                
                # Find next step using learned patterns
                next_step = self._find_next_step_with_learning(current_state)
                
                if not next_step:
                    print("❌ No next step found")
                    break
                
                # Attempt navigation with learning
                success = self._attempt_navigation_with_learning(next_step, current_state)
                
                if success:
                    navigation_count += 1
                    print(f"✅ Navigation successful!")
                else:
                    print(f"❌ Navigation failed, learning from failure...")
                
                # Save learned knowledge
                self._save_learned_knowledge()
            
            print(f"\n🏁 Learning navigation complete after {navigation_count} steps")
            print(f"📊 Final stats: {self.navigation_stats}")
            
        except Exception as e:
            print(f"❌ Learning navigation failed: {e}")
        finally:
            if self.playwright:
                self.playwright.stop()
    
    def _find_next_step_with_learning(self, current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find next step using learned patterns."""
        available_steps = current_state["step_info"]["available_steps"]
        
        # Find current step
        current_step = None
        for step in available_steps:
            if step["is_current"]:
                current_step = step
                break
        
        if not current_step:
            return None
        
        # Find next step
        next_step = None
        current_found = False
        
        for step in available_steps:
            if step["is_current"]:
                current_found = True
                continue
            
            if current_found and not step["is_current"]:
                next_step = step
                break
        
        return next_step
    
    def _attempt_navigation_with_learning(self, next_step: Dict[str, Any], current_state: Dict[str, Any]) -> bool:
        """Attempt navigation with learning."""
        # Record initial state
        initial_url = self.page.url
        initial_title = self.page.title()
        
        print(f"🎯 Attempting navigation to: {next_step['text']}")
        
        try:
            # Find the actual element
            step_element = None
            for step in self.page.query_selector_all("#steps-navigation a.step"):
                if step.text_content().strip() == next_step["text"]:
                    step_element = step
                    break
            
            if not step_element:
                print("❌ Could not find step element")
                return False
            
            # Apply adaptations if needed
            adaptation_applied = self._apply_adaptations(step_element, "click")
            
            # Attempt click
            if not adaptation_applied:
                step_element.click()
            
            # Monitor for success using learned indicators
            success = self._monitor_navigation_success(initial_url, initial_title)
            
            # Learn from attempt
            attempt_data = {
                "element": next_step,
                "url_changed": success,
                "step_navigation_updated": success,
                "form_content_changed": success,
                "page_indicators_updated": success
            }
            
            self._learn_from_navigation_attempt(attempt_data, success)
            
            return success
            
        except Exception as e:
            print(f"❌ Navigation attempt failed: {e}")
            
            # Learn from failure
            attempt_data = {
                "element": next_step,
                "error": str(e),
                "page_state": current_state
            }
            
            self._learn_from_navigation_attempt(attempt_data, False)
            
            return False
    
    def _monitor_navigation_success(self, initial_url: str, initial_title: str) -> bool:
        """Monitor for navigation success using learned indicators."""
        # Check learned success indicators
        for i in range(10):
            time.sleep(0.5)
            
            current_url = self.page.url
            current_title = self.page.title()
            
            # Check URL change (primary indicator)
            if "url_change" in self.success_indicators and current_url != initial_url:
                return True
            
            # Check title change
            if current_title != initial_title:
                return True
            
            # Check step navigation update
            if "step_navigation_update" in self.success_indicators:
                current_steps = self.page.query_selector_all("#steps-navigation a.step")
                for step in current_steps:
                    if "current" in (step.get_attribute("class") or ""):
                        return True
        
        return False

def main():
    """Main function."""
    print("🧠 Learning DevPost Navigator")
    print("=" * 50)
    
    navigator = LearningNavigator()
    navigator.navigate_with_learning()

if __name__ == "__main__":
    main()







