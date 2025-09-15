#!/usr/bin/env python3
"""
Session Recovery Node
====================

Handles sophisticated session recovery logic for different page similarity scenarios.
This addresses the complex cases you described:

1. "I've been here before" - exact match with working navigation model
2. "This looks familiar" - visual similarity but URL differences  
3. "LinkedIn mystery land" - dynamic links that move around
4. "DevPost quirks" - site-specific navigation differences
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import difflib

from langchain_core.messages import AIMessage
from langgraph_devpost_state import DevPostState, add_error, update_performance_metrics
from multi_dimensional_context_analyzer import MultiDimensionalContextAnalyzer, MultiDimensionalAnalysis


class PageSimilarityResult:
    """Result of page similarity analysis"""
    
    def __init__(self):
        self.exact_match = False
        self.visual_similarity = 0.0
        self.url_similarity = 0.0
        self.navigation_similarity = 0.0
        self.confidence = 0.0
        self.matched_page_data = None
        self.similarity_type = "unknown"  # "exact", "visual", "url", "navigation", "dynamic"
        self.recommendations = []
        self.exclamation = None  # Dramatic exclamation for uncharted territory


class SessionRecoveryAnalyzer:
    """Analyzes current page against historical data for session recovery"""
    
    def __init__(self, telemetry_graph, state_model):
        self.telemetry_graph = telemetry_graph
        self.state_model = state_model
    
    def analyze_page_similarity(self, current_page_data: Dict[str, Any]) -> PageSimilarityResult:
        """
        Analyze similarity between current page and historical data.
        
        This implements the sophisticated logic you described:
        - Exact matches with working navigation models
        - Visual similarity with URL differences
        - Dynamic link scenarios (LinkedIn mystery land)
        - Site-specific quirks (DevPost save/continue differences)
        """
        
        result = PageSimilarityResult()
        
        # 1. Check for exact URL match (99% confidence)
        exact_match = self._check_exact_url_match(current_page_data["url"])
        if exact_match:
            result.exact_match = True
            result.confidence = 0.99
            result.similarity_type = "exact"
            result.matched_page_data = exact_match
            result.recommendations = ["Use existing navigation model", "Resume from last known state"]
            return result
        
        # 2. Check for visual similarity (screenshot comparison)
        visual_match = self._check_visual_similarity(current_page_data.get("visual_hash"))
        if visual_match:
            result.visual_similarity = visual_match["similarity"]
            result.confidence = visual_match["similarity"]
            result.similarity_type = "visual"
            result.matched_page_data = visual_match["page_data"]
            
            # 3. Check URL similarity for parameterized URLs
            url_similarity = self._check_url_similarity(current_page_data["url"], visual_match["page_data"]["url"])
            if url_similarity > 0.8:
                result.url_similarity = url_similarity
                result.confidence = min(0.95, result.confidence + 0.2)
                result.similarity_type = "url"
                result.recommendations = ["URL is parameterized version of known page", "Use existing navigation model"]
            else:
                result.recommendations = ["Visual match but URL differs significantly", "Check for dynamic content"]
            
            return result
        
        # 4. Check for navigation pattern similarity (LinkedIn mystery land scenario)
        navigation_match = self._check_navigation_similarity(current_page_data)
        if navigation_match:
            result.navigation_similarity = navigation_match["similarity"]
            result.confidence = navigation_match["similarity"] * 0.7  # Lower confidence for navigation-only matches
            result.similarity_type = "navigation"
            result.matched_page_data = navigation_match["page_data"]
            result.recommendations = [
                "Navigation patterns match known page",
                "Links may be dynamically positioned",
                "Use semantic navigation rather than positional"
            ]
            return result
        
        # 5. Check for site-specific quirks (DevPost save/continue differences)
        site_quirk_match = self._check_site_specific_quirks(current_page_data)
        if site_quirk_match:
            result.similarity_type = "dynamic"
            result.confidence = 0.6
            result.matched_page_data = site_quirk_match
            result.recommendations = [
                "Site-specific behavior detected",
                "Use adaptive navigation strategy",
                "Focus on semantic elements rather than DOM structure"
            ]
            return result
        
        # 6. No significant similarity found - "Toto, we aren't in Kansas anymore!"
        result.confidence = 0.0
        result.similarity_type = "unknown"
        result.recommendations = ["This appears to be a new page", "Build new navigation model"]
        
        # Add dramatic exclamation for uncharted territory
        import random
        
        # Different messaging for different confidence levels
        if result.confidence < 0.1:
            # Completely lost - dramatic exclamations
            low_confidence_exclamations = [
                "Toto, we aren't in Kansas anymore!",
                "Houston, we have a new page!",
                "This looks like uncharted territory!",
                "We've entered the Twilight Zone!",
                "This is completely new territory!",
                "We're in uncharted waters now!",
                "This page is from another dimension!",
                "Houston, we have a problem - new page detected!"
            ]
            result.exclamation = random.choice(low_confidence_exclamations)
            
        elif result.confidence < 0.2:
            # Very uncertain but not completely lost
            uncertain_exclamations = [
                "I'm not in Kansas, but I'm not sure. Am I close?",
                "This doesn't look right, but something's familiar...",
                "I think I'm lost, but maybe not completely?",
                "This feels wrong, but I can't put my finger on it...",
                "I'm gonna have to look around more carefully...",
                "Something's off here, but I'm not sure what...",
                "This doesn't match what I expected, but maybe I'm close?"
            ]
            result.exclamation = random.choice(uncertain_exclamations)
            
        elif result.confidence < 0.4:
            # Moderately uncertain - more investigative
            moderate_uncertainty = [
                "This looks vaguely familiar, but something's different!",
                "I think I've seen something like this before, but...",
                "This seems similar to what I know, but not quite...",
                "I'm getting mixed signals here - need to investigate further",
                "Something's familiar about this, but I can't be sure...",
                "I think I'm on the right track, but need to verify...",
                "This reminds me of something, but I need to look closer..."
            ]
            result.exclamation = random.choice(moderate_uncertainty)
            
        elif result.confidence < 0.6:
            # Somewhat confident but cautious
            cautious_confidence = [
                "I think I've seen this before, but I want to be sure...",
                "This looks familiar, but let me double-check...",
                "I'm pretty sure I know this page, but just to be safe...",
                "This matches what I remember, but I'll verify...",
                "I think I'm in the right place, but I'll confirm..."
            ]
            result.exclamation = random.choice(cautious_confidence)
            
        elif result.confidence < 0.8:
            # Fairly confident
            result.exclamation = "This looks familiar - I think I know where I am!"
            
        else:
            # High confidence
            result.exclamation = "I'm confident this is a known page!"
        
        return result
    
    def _check_exact_url_match(self, current_url: str) -> Optional[Dict[str, Any]]:
        """Check for exact URL match in telemetry data"""
        
        for node_id, data in self.telemetry_graph.graph.nodes(data=True):
            if data.get("url") == current_url:
                return data
        
        return None
    
    def _check_visual_similarity(self, current_visual_hash: str) -> Optional[Dict[str, Any]]:
        """Check for visual similarity using perceptual hashing"""
        
        if not current_visual_hash or current_visual_hash == "unknown":
            return None
        
        try:
            from PIL import Image
            import imagehash
            
            current_hash = imagehash.hex_to_hash(current_visual_hash)
            best_match = None
            best_similarity = 0.0
            
            for node_id, data in self.telemetry_graph.graph.nodes(data=True):
                stored_hash = data.get("visual_hash")
                if stored_hash and stored_hash != "unknown":
                    try:
                        stored_image_hash = imagehash.hex_to_hash(stored_hash)
                        distance = current_hash - stored_image_hash
                        similarity = max(0.0, 1.0 - (distance / 64.0))  # Normalize to 0-1
                        
                        if similarity > best_similarity and similarity > 0.8:  # 80% similarity threshold
                            best_similarity = similarity
                            best_match = {
                                "similarity": similarity,
                                "page_data": data,
                                "node_id": node_id
                            }
                    except:
                        continue
            
            return best_match
            
        except ImportError:
            # Fallback to simple hash comparison
            for node_id, data in self.telemetry_graph.graph.nodes(data=True):
                if data.get("visual_hash") == current_visual_hash:
                    return {
                        "similarity": 1.0,
                        "page_data": data,
                        "node_id": node_id
                    }
        
        return None
    
    def _check_url_similarity(self, current_url: str, stored_url: str) -> float:
        """Check URL similarity for parameterized URLs"""
        
        # Parse URLs and compare components
        from urllib.parse import urlparse, parse_qs
        
        current_parsed = urlparse(current_url)
        stored_parsed = urlparse(stored_url)
        
        # Compare domain and path
        domain_match = current_parsed.netloc == stored_parsed.netloc
        path_similarity = difflib.SequenceMatcher(None, current_parsed.path, stored_parsed.path).ratio()
        
        # Compare query parameters
        current_params = parse_qs(current_parsed.query)
        stored_params = parse_qs(stored_parsed.query)
        
        param_similarity = 0.0
        if current_params or stored_params:
            common_params = set(current_params.keys()) & set(stored_params.keys())
            total_params = set(current_params.keys()) | set(stored_params.keys())
            param_similarity = len(common_params) / len(total_params) if total_params else 0.0
        
        # Weighted similarity score
        similarity = 0.0
        if domain_match:
            similarity += 0.4  # Domain match is important
            similarity += path_similarity * 0.4  # Path similarity
            similarity += param_similarity * 0.2  # Parameter similarity
        
        return similarity
    
    def _check_navigation_similarity(self, current_page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for navigation pattern similarity (LinkedIn mystery land scenario)"""
        
        current_nav_elements = current_page_data.get("navigation", [])
        if not current_nav_elements:
            return None
        
        best_match = None
        best_similarity = 0.0
        
        for node_id, data in self.telemetry_graph.graph.nodes(data=True):
            stored_nav_elements = data.get("navigation_elements", [])
            if not stored_nav_elements:
                continue
            
            # Compare navigation element text and structure
            similarity = self._compare_navigation_elements(current_nav_elements, stored_nav_elements)
            
            if similarity > best_similarity and similarity > 0.7:  # 70% similarity threshold
                best_similarity = similarity
                best_match = {
                    "similarity": similarity,
                    "page_data": data,
                    "node_id": node_id
                }
        
        return best_match
    
    def _compare_navigation_elements(self, nav1: List[Dict], nav2: List[Dict]) -> float:
        """Compare navigation elements for semantic similarity"""
        
        # Extract text content from navigation elements
        text1 = [elem.get("text", "").strip() for elem in nav1 if elem.get("text")]
        text2 = [elem.get("text", "").strip() for elem in nav2 if elem.get("text")]
        
        # Remove empty strings
        text1 = [t for t in text1 if t]
        text2 = [t for t in text2 if t]
        
        if not text1 or not text2:
            return 0.0
        
        # Calculate similarity based on common navigation text
        common_texts = set(text1) & set(text2)
        total_texts = set(text1) | set(text2)
        
        if not total_texts:
            return 0.0
        
        text_similarity = len(common_texts) / len(total_texts)
        
        # Also check for structural similarity (button types, form elements)
        type1 = [elem.get("type", elem.get("tagName", "")).lower() for elem in nav1]
        type2 = [elem.get("type", elem.get("tagName", "")).lower() for elem in nav2]
        
        common_types = set(type1) & set(type2)
        total_types = set(type1) | set(type2)
        
        type_similarity = len(common_types) / len(total_types) if total_types else 0.0
        
        # Weighted combination
        return (text_similarity * 0.7) + (type_similarity * 0.3)
    
    def _check_site_specific_quirks(self, current_page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for site-specific quirks like DevPost save/continue differences"""
        
        # DevPost-specific quirk detection
        if "devpost.com" in current_page_data.get("url", ""):
            return self._check_devpost_quirks(current_page_data)
        
        # Add other site-specific checks here
        return None
    
    def _check_devpost_quirks(self, current_page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for DevPost-specific quirks"""
        
        # Look for the "Manage Team" page quirk
        page_text = current_page_data.get("pageText", "").lower()
        if "manage team" in page_text or "team members" in page_text:
            # Check for save/continue button variations
            buttons = current_page_data.get("buttons", [])
            save_buttons = [btn for btn in buttons if any(
                keyword in btn.get("text", "").lower() 
                for keyword in ["save", "continue", "next"]
            )]
            
            if save_buttons:
                return {
                    "quirk_type": "devpost_manage_team_save_button",
                    "description": "DevPost Manage Team page has different save button behavior",
                    "recommendations": [
                        "Use semantic button detection rather than positional",
                        "Try multiple save button strategies",
                        "Wait for page state changes after clicking"
                    ],
                    "button_data": save_buttons
                }
        
        return None


def session_recovery_node(state: DevPostState) -> DevPostState:
    """
    Node: Session Recovery and Navigation Model Matching
    
    This is the sophisticated session recovery logic you described:
    - "I've been here before" - exact match with working navigation model
    - "This looks familiar" - visual similarity but URL differences  
    - "LinkedIn mystery land" - dynamic links that move around
    - "DevPost quirks" - site-specific navigation differences
    """
    
    print("🔍 Session Recovery Node")
    start_time = time.time()
    
    try:
        browser_manager = state.get("browser_session_manager")
        if not browser_manager or not browser_manager.context:
            add_error(state, "Browser not available for session recovery")
            return state
        
        page = browser_manager.context.pages[0]
        
        # Collect current page data
        current_page_data = page.evaluate("""
            () => {
                return {
                    url: window.location.href,
                    title: document.title,
                    pageText: document.body.innerText,
                    navigation: Array.from(document.querySelectorAll('a, button')).map(el => ({
                        text: el.textContent?.trim(),
                        href: el.href || null,
                        type: el.type || el.tagName.toLowerCase(),
                        id: el.id,
                        className: el.className
                    })),
                    buttons: Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"]')).map(btn => ({
                        text: btn.textContent || btn.value,
                        type: btn.type,
                        id: btn.id,
                        className: btn.className
                    }))
                };
            }
        """)
        
        # Capture screenshot for visual comparison
        screenshot_path = f"session_recovery_{int(time.time())}.png"
        page.screenshot(path=screenshot_path)
        current_page_data["screenshot"] = screenshot_path
        
        # Calculate visual hash
        try:
            from PIL import Image
            import imagehash
            with Image.open(screenshot_path) as img:
                phash = imagehash.phash(img)
                current_page_data["visual_hash"] = str(phash)
        except ImportError:
            import hashlib
            with open(screenshot_path, 'rb') as f:
                current_page_data["visual_hash"] = hashlib.md5(f.read()).hexdigest()
        
        # Initialize analyzers if not exists
        if not hasattr(state, "_session_analyzer"):
            state["_session_analyzer"] = SessionRecoveryAnalyzer(
                state.get("telemetry_graph"),
                state.get("state_model")
            )
        
        if not hasattr(state, "_multi_dimensional_analyzer"):
            state["_multi_dimensional_analyzer"] = MultiDimensionalContextAnalyzer(
                state.get("telemetry_graph"),
                state.get("state_model")
            )
        
        session_analyzer = state["_session_analyzer"]
        multi_dimensional_analyzer = state["_multi_dimensional_analyzer"]
        
        # Perform multi-dimensional context analysis
        print("🔍 Performing multi-dimensional context analysis...")
        multi_dimensional_analysis = multi_dimensional_analyzer.analyze_multi_dimensional_context(current_page_data)
        
        # Perform traditional similarity analysis
        similarity_result = session_analyzer.analyze_page_similarity(current_page_data)
        
        # Enhance similarity result with multi-dimensional insights
        similarity_result.multi_dimensional_analysis = multi_dimensional_analysis
        
        # Update state based on similarity result and multi-dimensional analysis
        state["session_recovery"] = {
            "similarity_result": similarity_result.__dict__,
            "multi_dimensional_analysis": multi_dimensional_analysis.__dict__,
            "current_page_data": current_page_data,
            "recovery_strategy": similarity_result.similarity_type,
            "confidence": similarity_result.confidence,
            "recommendations": similarity_result.recommendations,
            "overall_confidence": multi_dimensional_analysis.overall_confidence,
            "primary_strategy": multi_dimensional_analysis.primary_strategy,
            "fallback_strategies": multi_dimensional_analysis.fallback_strategies,
            "test_plan": multi_dimensional_analysis.test_plan,
            "learning_opportunities": multi_dimensional_analysis.learning_opportunities
        }
        
        # Apply recovery strategy with multi-dimensional insights and dramatic exclamations
        overall_confidence = multi_dimensional_analysis.overall_confidence
        primary_strategy = multi_dimensional_analysis.primary_strategy
        
        # CONFIDENCE-BASED ROUTING: Route to appropriate mode based on confidence level
        AUTONOMOUS_NAVIGATION_THRESHOLD = 0.3  # Below this, we need human intervention
        EXPLORATORY_THRESHOLD = 0.2  # Below this, we're in "completely confused" territory
        PROMPT_MODE_THRESHOLD = 0.4  # Below this, we need conversational decision-making
        
        if overall_confidence < EXPLORATORY_THRESHOLD:
            # GHOSTBUSTERS TIME! Completely confused - stop and ask for help
            ghostbusters_exclamations = [
                "🚨 GHOSTBUSTERS TIME! 🚨 I'm completely confused and need to stop!",
                "🛑 STOP! I have no idea where I am or what I'm doing!",
                "🚨 EMERGENCY STOP! My confidence is critically low - I need help!",
                "🛑 HALT! This is beyond my ability to navigate autonomously!",
                "🚨 ABORT MISSION! I'm too confused to continue safely!",
                "🛑 STOP EVERYTHING! I'm in completely uncharted territory!",
                "🚨 RED ALERT! I need human intervention - I'm lost!"
            ]
            import random
            stop_message = random.choice(ghostbusters_exclamations)
            stop_message += f"\n📊 Confidence Level: {overall_confidence:.2f} (CRITICALLY LOW)"
            stop_message += f"\n🎯 Primary Strategy: {primary_strategy}"
            stop_message += f"\n🔍 Similarity Type: {similarity_result.similarity_type}"
            
            if multi_dimensional_analysis.test_plan:
                stop_message += f"\n📋 What I would test: {', '.join(multi_dimensional_analysis.test_plan[:3])}..."
            
            stop_message += "\n\n🤔 INTERACTIVE RECOVERY OPTIONS:"
            stop_message += "\n   1. Tell me where we are (user provides context)"
            stop_message += "\n   2. Guide me step by step (user provides direction)"
            stop_message += "\n   3. Start fresh from a known page (reset session)"
            stop_message += "\n   4. Analyze this page together (collaborative exploration)"
            stop_message += "\n   5. Save session and quit (preserve current state)"
            
            state["messages"].append(AIMessage(content=stop_message))
            
            # Set state to require user input
            state["user_input_required"] = True
            state["ghostbusters_mode"] = True
            state["session_stopped"] = True
            state["stop_reason"] = "confidence_below_exploratory_threshold"
            state["recovery_options"] = [
                "user_context_guidance",
                "step_by_step_guidance", 
                "fresh_start",
                "collaborative_analysis",
                "save_and_quit"
            ]
            
            # Preserve session state for recovery
            state["session_save_data"] = {
                "current_page_data": current_page_data,
                "similarity_result": similarity_result.__dict__,
                "multi_dimensional_analysis": multi_dimensional_analysis.__dict__,
                "confidence": overall_confidence,
                "timestamp": time.time(),
                "screenshot": screenshot_path
            }
            
            print(f"🚨 GHOSTBUSTERS MODE ACTIVATED!")
            print(f"   Confidence: {overall_confidence:.2f} (below {EXPLORATORY_THRESHOLD})")
            print(f"   Session stopped - awaiting user guidance")
            
            return state
        
        elif overall_confidence < EXPLORATORY_THRESHOLD + 0.1:  # Very low confidence
            # GHOSTBUSTERS AUTONOMOUS MODE: Too risky for human consultation
            autonomous_ghostbusters_exclamations = [
                "🚨 GHOSTBUSTERS AUTONOMOUS MODE - We're going in!",
                "🛑 Stand back! Ghostbusters are taking over!",
                "🚨 Emergency protocols activated - autonomous investigation initiated!",
                "🛑 This is too dangerous for human interaction - Ghostbusters deploying!",
                "🚨 Critical situation detected - executing autonomous recovery protocol!",
                "🛑 Ghostbusters emergency response - investigating without human guidance!"
            ]
            import random
            autonomous_message = random.choice(autonomous_ghostbusters_exclamations)
            autonomous_message += f"\n📊 Confidence Level: {overall_confidence:.2f} (critically low - autonomous investigation)"
            autonomous_message += f"\n🎯 Primary Strategy: {primary_strategy}"
            autonomous_message += "\n🚨 Running autonomous investigation - will return with findings!"
            state["messages"].append(AIMessage(content=autonomous_message))
            
            # Set autonomous Ghostbusters mode
            state["ghostbusters_autonomous_mode"] = True
            state["user_input_required"] = False
            state["navigation_model"] = f"autonomous_ghostbusters_{primary_strategy}"
            
        elif overall_confidence < PROMPT_MODE_THRESHOLD:
            # PROMPT MODE: Conversational decision-making
            prompt_mode_exclamations = [
                "This is it! The moment we should have trained for!",
                "Situation report: We're in uncharted territory, but I've got a plan!",
                "Stand by for briefing: Current situation requires tactical discussion!",
                "All units, this is what we trained for - time to execute the plan!",
                "Situation unclear, but we're not out of options yet!",
                "This is exactly the scenario we prepared for - let's discuss our approach!",
                "Mission briefing: We're in a complex situation that requires careful analysis!",
                "Stand down from autonomous mode - time for strategic consultation!"
            ]
            import random
            prompt_message = random.choice(prompt_mode_exclamations)
            prompt_message += f"\n📊 Confidence Level: {overall_confidence:.2f} (moderate uncertainty - tactical discussion needed)"
            prompt_message += f"\n🎯 Primary Strategy: {primary_strategy}"
            prompt_message += "\n🎖️ PROMPT MODE ACTIVATED - Let's discuss our approach!"
            state["messages"].append(AIMessage(content=prompt_message))
            
            # Set prompt mode
            state["prompt_mode"] = True
            state["user_input_required"] = True
            state["navigation_model"] = f"prompt_mode_{primary_strategy}"
            
        elif overall_confidence < AUTONOMOUS_NAVIGATION_THRESHOLD:
            # Cautious mode - proceed with caution but can continue
            cautious_exclamations = [
                "⚠️ I'm not very confident about this, but I'll proceed cautiously...",
                "🤔 I'm somewhat uncertain, but I'll try to navigate carefully...",
                "⚠️ My confidence is low, but I'll attempt to continue...",
                "🤔 I'm not sure about this, but I'll proceed with caution...",
                "⚠️ This is uncertain territory, but I'll try to handle it..."
            ]
            import random
            cautious_message = random.choice(cautious_exclamations)
            cautious_message += f"\n📊 Confidence Level: {overall_confidence:.2f} (below autonomous threshold of {AUTONOMOUS_NAVIGATION_THRESHOLD})"
            cautious_message += f"\n🎯 Using cautious navigation strategy: {primary_strategy}"
            state["messages"].append(AIMessage(content=cautious_message))
            
            # Set cautious mode
            state["cautious_mode"] = True
            state["navigation_model"] = f"cautious_{primary_strategy}"
            
        else:
            # High enough confidence for autonomous navigation
            state["cautonomous_mode"] = False
            state["ghostbusters_mode"] = False
            state["prompt_mode"] = False
        
        # Enhanced messaging with multi-dimensional context
        if similarity_result.similarity_type == "exact":
            message = f"✅ Exact page match found! Confidence: {similarity_result.confidence:.2f}"
            message += f"\n🔍 Multi-dimensional analysis: {overall_confidence:.2f} confidence using {primary_strategy}"
            state["messages"].append(AIMessage(content=message))
            # Use existing navigation model
            if similarity_result.matched_page_data:
                state["navigation_model"] = similarity_result.matched_page_data.get("navigation_model")
                
        elif similarity_result.similarity_type == "visual":
            message = f"👁️ Visual similarity detected! Confidence: {similarity_result.confidence:.2f}"
            message += f"\n🔍 Multi-dimensional analysis: {overall_confidence:.2f} confidence using {primary_strategy}"
            state["messages"].append(AIMessage(content=message))
            # Adapt existing model for visual match
            state["navigation_model"] = "visual_adapted"
            
        elif similarity_result.similarity_type == "navigation":
            message = f"🧭 Navigation pattern match! Confidence: {similarity_result.confidence:.2f}"
            message += f"\n🔍 Multi-dimensional analysis: {overall_confidence:.2f} confidence using {primary_strategy}"
            state["messages"].append(AIMessage(content=message))
            # Use semantic navigation (LinkedIn mystery land scenario)
            state["navigation_model"] = "semantic_navigation"
            
        elif similarity_result.similarity_type == "dynamic":
            message = f"🔄 Dynamic content detected! Confidence: {similarity_result.confidence:.2f}"
            message += f"\n🔍 Multi-dimensional analysis: {overall_confidence:.2f} confidence using {primary_strategy}"
            state["messages"].append(AIMessage(content=message))
            # Use adaptive navigation strategy
            state["navigation_model"] = "adaptive_navigation"
            
        else:
            # Uncharted territory - use dramatic exclamation with multi-dimensional context!
            if similarity_result.exclamation:
                message = f"🚨 {similarity_result.exclamation}"
                message += f"\n🔍 Multi-dimensional analysis: {overall_confidence:.2f} confidence using {primary_strategy}"
                if multi_dimensional_analysis.test_plan:
                    message += f"\n📋 Test plan: {', '.join(multi_dimensional_analysis.test_plan[:3])}..."
                state["messages"].append(AIMessage(content=message))
            else:
                message = "🆕 New page detected - building fresh navigation model"
                message += f"\n🔍 Multi-dimensional analysis: {overall_confidence:.2f} confidence using {primary_strategy}"
                state["messages"].append(AIMessage(content=message))
            # Build new navigation model
            state["navigation_model"] = "fresh_model"
        
        # Add learning opportunities to messages
        if multi_dimensional_analysis.learning_opportunities:
            learning_msg = f"🎓 Learning opportunities: {', '.join(multi_dimensional_analysis.learning_opportunities[:3])}..."
            state["messages"].append(AIMessage(content=learning_msg))
        
        # Add recommendations to state
        state["navigation_recommendations"] = similarity_result.recommendations
        
        # Update performance metrics
        recovery_time = time.time() - start_time
        update_performance_metrics(state, {
            "session_recovery_time": recovery_time,
            "similarity_type": similarity_result.similarity_type,
            "confidence": similarity_result.confidence,
            "navigation_model": state["navigation_model"]
        })
        
        # Log detailed analysis
        print(f"🔍 Session Recovery Analysis:")
        print(f"   Similarity Type: {similarity_result.similarity_type}")
        print(f"   Confidence: {similarity_result.confidence:.2f}")
        print(f"   Navigation Model: {state['navigation_model']}")
        print(f"   Recommendations: {', '.join(similarity_result.recommendations)}")
        
    except Exception as e:
        add_error(state, f"Session recovery failed: {str(e)}")
    
    return state
