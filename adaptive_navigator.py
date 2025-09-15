#!/usr/bin/env python3
"""
Adaptive Navigator
=================

A learning navigation system that incorporates lessons learned dynamically
during the session. Adapts to new patterns and improves decision making.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Dynamic learning navigation with real-time adaptation
"""

import sys
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright
from typing import Dict, List, Any, Optional
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class LearningPattern:
    """Represents a learned navigation pattern."""
    def __init__(self, pattern_type: str, selector: str, confidence: float, 
                 success_count: int = 0, failure_count: int = 0, 
                 context: Dict[str, Any] = None):
        self.pattern_type = pattern_type
        self.selector = selector
        self.confidence = confidence
        self.success_count = success_count
        self.failure_count = failure_count
        self.context = context or {}
        self.last_used = time.time()
    
    def update_success(self):
        """Update pattern after successful navigation."""
        self.success_count += 1
        self.confidence = min(1.0, self.confidence + 0.1)
        self.last_used = time.time()
    
    def update_failure(self):
        """Update pattern after failed navigation."""
        self.failure_count += 1
        self.confidence = max(0.0, self.confidence - 0.1)
        self.last_used = time.time()
    
    def to_dict(self):
        return {
            "pattern_type": self.pattern_type,
            "selector": self.selector,
            "confidence": self.confidence,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "context": self.context,
            "last_used": self.last_used
        }

class AdaptiveNavigator:
    """Adaptive navigation system that learns from experience."""
    
    def __init__(self, cdp_url: str = "http://localhost:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Learning system
        self.learned_patterns: List[LearningPattern] = []
        self.session_history: List[Dict[str, Any]] = []
        self.current_context = {}
        
        # Load existing patterns
        self._load_learned_patterns()
    
    def _load_learned_patterns(self):
        """Load previously learned patterns from file."""
        try:
            with open("learned_navigation_patterns.json", "r") as f:
                patterns_data = json.load(f)
                self.learned_patterns = [
                    LearningPattern(**pattern) for pattern in patterns_data
                ]
            print(f"📚 Loaded {len(self.learned_patterns)} learned patterns")
        except FileNotFoundError:
            print("📚 No existing patterns found, starting fresh")
            self.learned_patterns = []
    
    def _save_learned_patterns(self):
        """Save learned patterns to file."""
        try:
            patterns_data = [pattern.to_dict() for pattern in self.learned_patterns]
            with open("learned_navigation_patterns.json", "w") as f:
                json.dump(patterns_data, f, indent=2)
            print(f"💾 Saved {len(self.learned_patterns)} learned patterns")
        except Exception as e:
            print(f"❌ Failed to save patterns: {e}")
    
    def _discover_new_patterns(self, page) -> List[LearningPattern]:
        """Discover new navigation patterns from the current page."""
        new_patterns = []
        
        try:
            # Discover DevPost-specific patterns
            devpost_patterns = self._discover_devpost_patterns(page)
            new_patterns.extend(devpost_patterns)
            
            # Discover general navigation patterns
            general_patterns = self._discover_general_patterns(page)
            new_patterns.extend(general_patterns)
            
            # Discover context-specific patterns
            context_patterns = self._discover_context_patterns(page)
            new_patterns.extend(context_patterns)
            
        except Exception as e:
            print(f"⚠️ Error discovering patterns: {e}")
        
        return new_patterns
    
    def _discover_devpost_patterns(self, page) -> List[LearningPattern]:
        """Discover DevPost-specific navigation patterns."""
        patterns = []
        
        try:
            # Step navigation patterns
            step_links = page.query_selector_all("#steps-navigation a.step")
            if step_links:
                patterns.append(LearningPattern(
                    "devpost_steps",
                    "#steps-navigation a.step",
                    0.9,
                    context={"site": "devpost", "type": "step_navigation"}
                ))
            
            # Next/Previous patterns
            next_links = page.query_selector_all("a.step.next")
            if next_links:
                patterns.append(LearningPattern(
                    "devpost_next",
                    "a.step.next",
                    0.95,
                    context={"site": "devpost", "type": "forward_navigation"}
                ))
            
            prev_links = page.query_selector_all("a.step.previous")
            if prev_links:
                patterns.append(LearningPattern(
                    "devpost_prev",
                    "a.step.previous",
                    0.95,
                    context={"site": "devpost", "type": "backward_navigation"}
                ))
            
            # Current step pattern
            current_links = page.query_selector_all("a.step.current")
            if current_links:
                patterns.append(LearningPattern(
                    "devpost_current",
                    "a.step.current",
                    0.1,
                    context={"site": "devpost", "type": "current_step", "navigable": False}
                ))
            
        except Exception as e:
            print(f"⚠️ Error discovering DevPost patterns: {e}")
        
        return patterns
    
    def _discover_general_patterns(self, page) -> List[LearningPattern]:
        """Discover general navigation patterns."""
        patterns = []
        
        try:
            # Button patterns
            buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
            for button in buttons:
                text = button.text_content().strip().lower()
                if any(word in text for word in ["next", "continue", "proceed", "forward"]):
                    patterns.append(LearningPattern(
                        "button_forward",
                        f"button:has-text('{text}')",
                        0.8,
                        context={"type": "button", "action": "forward", "text": text}
                    ))
                elif any(word in text for word in ["back", "previous", "return"]):
                    patterns.append(LearningPattern(
                        "button_backward",
                        f"button:has-text('{text}')",
                        0.8,
                        context={"type": "button", "action": "backward", "text": text}
                    ))
            
            # Link patterns
            links = page.query_selector_all("a")
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.text_content().strip().lower()
                
                if any(word in href.lower() for word in ["next", "continue", "step", "forward"]):
                    patterns.append(LearningPattern(
                        "link_forward",
                        f"a[href*='{href.split('/')[-1]}']",
                        0.7,
                        context={"type": "link", "action": "forward", "href": href, "text": text}
                    ))
                elif any(word in href.lower() for word in ["back", "previous", "prev"]):
                    patterns.append(LearningPattern(
                        "link_backward",
                        f"a[href*='{href.split('/')[-1]}']",
                        0.7,
                        context={"type": "link", "action": "backward", "href": href, "text": text}
                    ))
            
        except Exception as e:
            print(f"⚠️ Error discovering general patterns: {e}")
        
        return patterns
    
    def _discover_context_patterns(self, page) -> List[LearningPattern]:
        """Discover context-specific patterns based on page content."""
        patterns = []
        
        try:
            # Analyze page title and URL for context
            title = page.title().lower()
            url = page.url.lower()
            
            # Form navigation patterns
            if "form" in title or "edit" in url:
                form_buttons = page.query_selector_all("form button, form input[type='submit']")
                if form_buttons:
                    patterns.append(LearningPattern(
                        "form_navigation",
                        "form button, form input[type='submit']",
                        0.6,
                        context={"type": "form", "page_context": "form_editing"}
                    ))
            
            # Step-based navigation patterns
            if "step" in url or "manage" in url:
                step_indicators = page.query_selector_all("[class*='step'], [id*='step']")
                if step_indicators:
                    patterns.append(LearningPattern(
                        "step_indicators",
                        "[class*='step'], [id*='step']",
                        0.7,
                        context={"type": "step_indicators", "page_context": "multi_step"}
                    ))
            
        except Exception as e:
            print(f"⚠️ Error discovering context patterns: {e}")
        
        return patterns
    
    def _merge_patterns(self, new_patterns: List[LearningPattern]):
        """Merge new patterns with existing ones, updating confidence."""
        for new_pattern in new_patterns:
            # Check if similar pattern already exists
            existing = None
            for existing_pattern in self.learned_patterns:
                if (existing_pattern.pattern_type == new_pattern.pattern_type and
                    existing_pattern.selector == new_pattern.selector):
                    existing = existing_pattern
                    break
            
            if existing:
                # Update existing pattern
                existing.confidence = (existing.confidence + new_pattern.confidence) / 2
                existing.context.update(new_pattern.context)
                print(f"🔄 Updated existing pattern: {existing.pattern_type}")
            else:
                # Add new pattern
                self.learned_patterns.append(new_pattern)
                print(f"✨ Discovered new pattern: {new_pattern.pattern_type}")
    
    def _analyze_element_with_learned_patterns(self, element, element_type: str, page) -> Dict[str, Any]:
        """Analyze element using both learned patterns and heuristics."""
        analysis = {
            "text": "",
            "confidence": 0.0,
            "action": "unknown",
            "reasoning": [],
            "learned_pattern": None
        }
        
        try:
            # Get basic element info
            if hasattr(element, 'text_content'):
                analysis["text"] = element.text_content().strip().lower()
            
            # Check against learned patterns
            for pattern in self.learned_patterns:
                try:
                    if self._element_matches_pattern(element, pattern):
                        analysis["confidence"] = max(analysis["confidence"], pattern.confidence)
                        analysis["learned_pattern"] = pattern.pattern_type
                        analysis["reasoning"].append(f"Matches learned pattern: {pattern.pattern_type}")
                        
                        # Determine action from pattern context
                        if pattern.context.get("action") == "forward":
                            analysis["action"] = "forward"
                        elif pattern.context.get("action") == "backward":
                            analysis["action"] = "backward"
                        elif pattern.context.get("navigable", True):
                            analysis["action"] = "navigate"
                        else:
                            analysis["action"] = "current"
                        
                        break
                except:
                    continue
            
            # If no learned pattern matches, use heuristics
            if analysis["confidence"] < 0.5:
                heuristic_analysis = self._heuristic_analysis(element, element_type, page)
                analysis.update(heuristic_analysis)
            
        except Exception as e:
            analysis["reasoning"].append(f"Analysis error: {e}")
        
        return analysis
    
    def _element_matches_pattern(self, element, pattern: LearningPattern) -> bool:
        """Check if element matches a learned pattern."""
        try:
            # Simple selector matching
            if pattern.selector.startswith("#"):
                element_id = element.get_attribute("id")
                return element_id and pattern.selector[1:] in element_id
            elif pattern.selector.startswith("."):
                element_class = element.get_attribute("class")
                return element_class and pattern.selector[1:] in element_class
            elif "has-text" in pattern.selector:
                text = element.text_content().strip().lower()
                return pattern.context.get("text", "").lower() in text
            else:
                # Try to evaluate selector
                return element.evaluate(f"el => el.matches('{pattern.selector}')")
        except:
            return False
    
    def _heuristic_analysis(self, element, element_type: str, page) -> Dict[str, Any]:
        """Fallback heuristic analysis when no learned patterns match."""
        analysis = {
            "confidence": 0.0,
            "action": "unknown",
            "reasoning": []
        }
        
        try:
            text = element.text_content().strip().lower() if hasattr(element, 'text_content') else ""
            classes = element.get_attribute("class") or "" if hasattr(element, 'get_attribute') else ""
            
            # Basic keyword matching
            if any(word in text for word in ["next", "continue", "proceed", "forward"]):
                analysis["confidence"] = 0.7
                analysis["action"] = "forward"
                analysis["reasoning"].append("Contains forward keywords")
            elif any(word in text for word in ["back", "previous", "return"]):
                analysis["confidence"] = 0.7
                analysis["action"] = "backward"
                analysis["reasoning"].append("Contains backward keywords")
            elif "current" in classes:
                analysis["confidence"] = 0.1
                analysis["action"] = "current"
                analysis["reasoning"].append("Current step indicator")
            else:
                analysis["confidence"] = 0.3
                analysis["reasoning"].append("No clear navigation indicators")
        
        except Exception as e:
            analysis["reasoning"].append(f"Heuristic analysis error: {e}")
        
        return analysis
    
    def connect_and_navigate(self):
        """Connect to browser and start adaptive navigation."""
        try:
            self.playwright = sync_playwright().start()
            
            # Get page info
            response = requests.get(f"{self.cdp_url}/json")
            pages_info = response.json()
            
            devpost_page_info = None
            for p_info in pages_info:
                if "devpost.com" in p_info.get("url", "") and "submission" in p_info.get("url", ""):
                    devpost_page_info = p_info
                    break
            
            if not devpost_page_info:
                print("❌ No DevPost submission page found")
                return
            
            print(f"📄 Target page: {devpost_page_info['title']}")
            print(f"🔗 URL: {devpost_page_info['url']}")
            
            # Connect to browser
            print("🔍 Connecting to existing browser...")
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0]
            pages = self.context.pages
            
            # Find DevPost page
            self.page = None
            for page in pages:
                if "devpost.com" in page.url and "submission" in page.url:
                    self.page = page
                    break
            
            if not self.page:
                self.page = pages[0]
            
            print(f"✅ Connected to: {self.page.url}")
            
            # Start adaptive navigation loop
            self._adaptive_navigation_loop()
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
        finally:
            if self.playwright:
                self.playwright.stop()
    
    def _adaptive_navigation_loop(self):
        """Main adaptive navigation loop."""
        navigation_count = 0
        max_navigations = 10
        
        while navigation_count < max_navigations:
            print(f"\n{'='*60}")
            print(f"🧠 Adaptive Navigation Step {navigation_count + 1}")
            print(f"{'='*60}")
            
            # Discover new patterns from current page
            print("🔍 Discovering new patterns...")
            new_patterns = self._discover_new_patterns(self.page)
            if new_patterns:
                self._merge_patterns(new_patterns)
                print(f"📚 Total learned patterns: {len(self.learned_patterns)}")
            
            # Analyze current page
            print(f"📄 Current page: {self.page.title()}")
            print(f"🔗 Current URL: {self.page.url}")
            
            # Get all navigation elements
            all_elements = self._get_navigation_elements()
            
            if not all_elements:
                print("❌ No navigation elements found")
                break
            
            # Analyze elements using learned patterns
            element_analyses = []
            for element, element_type in all_elements:
                try:
                    analysis = self._analyze_element_with_learned_patterns(element, element_type, self.page)
                    analysis["element"] = element
                    analysis["type"] = element_type
                    element_analyses.append(analysis)
                except Exception as e:
                    print(f"⚠️ Error analyzing element: {e}")
            
            # Make navigation decision
            decision = self._make_adaptive_decision(element_analyses)
            
            if decision is None:
                print("🛑 No suitable navigation decision found")
                break
            
            # Execute navigation
            success = self._execute_navigation(decision)
            
            if success:
                navigation_count += 1
                # Update pattern success
                if decision.get("learned_pattern"):
                    for pattern in self.learned_patterns:
                        if pattern.pattern_type == decision["learned_pattern"]:
                            pattern.update_success()
                            break
            else:
                # Update pattern failure
                if decision.get("learned_pattern"):
                    for pattern in self.learned_patterns:
                        if pattern.pattern_type == decision["learned_pattern"]:
                            pattern.update_failure()
                            break
            
            # Save learned patterns
            self._save_learned_patterns()
        
        print(f"\n🏁 Adaptive navigation complete after {navigation_count} steps")
        print(f"📚 Final learned patterns: {len(self.learned_patterns)}")
    
    def _get_navigation_elements(self):
        """Get all potential navigation elements."""
        all_elements = []
        
        try:
            # DevPost-specific elements
            steps_navigation = self.page.query_selector_all("#steps-navigation a.step")
            all_elements.extend([(link, "devpost_step") for link in steps_navigation])
            
            # Other elements
            buttons = self.page.query_selector_all("button, input[type='button'], input[type='submit']")
            all_elements.extend([(btn, "button") for btn in buttons])
            
            links = self.page.query_selector_all("a:not(.step)")
            all_elements.extend([(link, "link") for link in links])
            
        except Exception as e:
            print(f"⚠️ Error getting navigation elements: {e}")
        
        return all_elements
    
    def _make_adaptive_decision(self, element_analyses):
        """Make navigation decision using learned patterns and heuristics."""
        # Filter high confidence elements
        high_confidence = [e for e in element_analyses if e["confidence"] >= 0.7]
        
        if high_confidence:
            # Choose best high confidence element
            best = max(high_confidence, key=lambda x: x["confidence"])
            print(f"✅ High confidence decision: {best['text']} (confidence: {best['confidence']:.2f})")
            if best.get("learned_pattern"):
                print(f"📚 Using learned pattern: {best['learned_pattern']}")
            return best
        
        # Medium confidence - ask user
        medium_confidence = [e for e in element_analyses if 0.4 <= e["confidence"] < 0.7]
        if medium_confidence:
            print("⚠️ Medium confidence decision required:")
            for i, elem in enumerate(medium_confidence[:5], 1):
                print(f"   {i}. {elem['text']} (confidence: {elem['confidence']:.2f})")
            
            try:
                choice = int(input("Choose element (number) or 0 to skip: ")) - 1
                if 0 <= choice < len(medium_confidence):
                    return medium_confidence[choice]
            except ValueError:
                pass
        
        return None
    
    def _execute_navigation(self, decision):
        """Execute the navigation decision."""
        try:
            print(f"🔄 Clicking: {decision['text']}")
            decision["element"].click()
            
            # Wait for navigation
            self.page.wait_for_load_state("networkidle")
            
            # Check if navigation occurred
            new_url = self.page.url
            new_title = self.page.title()
            
            print(f"✅ Navigation successful!")
            print(f"📄 New page: {new_title}")
            print(f"🔗 New URL: {new_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False

def main():
    """Main function."""
    print("🧠 Adaptive DevPost Navigator")
    print("=" * 50)
    
    navigator = AdaptiveNavigator()
    navigator.connect_and_navigate()

if __name__ == "__main__":
    main()







