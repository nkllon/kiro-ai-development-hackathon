#!/usr/bin/env python3
"""
LangGraph DevPost Nodes
=======================

Individual nodes for the DevPost automation workflow.
Each node handles a specific aspect of the automation process.
"""

import time
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from playwright.sync_api import Page

from langgraph_devpost_state import (
    DevPostState, 
    WorkflowPhase, 
    BrowserConnectionStatus, 
    PageDetectionResult,
    FormCompletionStatus,
    update_phase,
    add_error,
    increment_recovery_attempts,
    reset_recovery_attempts,
    update_form_status,
    set_user_input_required,
    update_performance_metrics
)
from browser_session_manager import BrowserSessionManager
from site_navigation_session import SiteNavigationSession, NavigationIntent
from telemetry_graph import TelemetryGraph, create_telemetry_graph
from devpost_state_model import DevPostStateModel, create_state_model


def browser_connection_node(state: DevPostState) -> DevPostState:
    """
    Node: Browser Connection Management
    
    Handles connecting to existing browser or launching new one.
    Prioritizes existing Chrome instances with extensions.
    """
    
    print("🔌 Browser Connection Node")
    start_time = time.time()
    
    try:
        # Initialize browser session manager
        browser_manager = BrowserSessionManager()
        state["browser_session_manager"] = browser_manager
        
        # Attempt to connect to existing browser or launch new one
        browser = browser_manager.connect_or_launch_browser()
        
        if browser:
            state["browser_status"] = BrowserConnectionStatus.CONNECTED
            state["browser_port"] = browser_manager.connected_port
            state["session_preserved"] = True
            
            # Check if extensions are available (1Password, etc.)
            if browser_manager.connected_port:
                state["browser_status"] = BrowserConnectionStatus.EXTENSION_AVAILABLE
            
            state["messages"].append(
                AIMessage(content="✅ Browser connection established successfully")
            )
        else:
            state["browser_status"] = BrowserConnectionStatus.FAILED
            add_error(state, "Failed to establish browser connection")
            return state
        
        # Get the target DevPost page
        page = browser_manager.get_devpost_page()
        if page:
            state["target_page_url"] = page.url
            state["messages"].append(
                AIMessage(content=f"🎯 Target page identified: {page.url}")
            )
        else:
            add_error(state, "Failed to identify target DevPost page")
            return state
        
        # Update performance metrics
        connection_time = time.time() - start_time
        update_performance_metrics(state, {
            "browser_connection_time": connection_time,
            "browser_port": browser_manager.connected_port,
            "session_preserved": state["session_preserved"]
        })
        
        # Move to next phase
        update_phase(state, WorkflowPhase.PAGE_DETECTION)
        
    except Exception as e:
        add_error(state, f"Browser connection failed: {str(e)}")
        increment_recovery_attempts(state)
    
    return state


def page_detection_node(state: DevPostState) -> DevPostState:
    """
    Node: Page Detection and Analysis
    
    Analyzes the current page to determine type, state, and next actions.
    Performs blind detection without assumptions.
    """
    
    print("🔍 Page Detection Node")
    start_time = time.time()
    
    try:
        browser_manager = state.get("browser_session_manager")
        if not browser_manager or not browser_manager.context:
            add_error(state, "Browser not available for page detection")
            return state
        
        # Get current page
        pages = browser_manager.context.pages
        if not pages:
            add_error(state, "No pages available for detection")
            return state
        
        page = pages[0]  # Use first available page
        state["page_url"] = page.url
        state["page_title"] = page.title()
        
        # Initialize state model and telemetry graph if not exists
        if not state.get("state_model"):
            state_model = create_state_model()
            state["state_model"] = state_model
        
        if not state.get("telemetry_graph"):
            telemetry_graph = create_telemetry_graph(state["workflow_id"])
            state["telemetry_graph"] = telemetry_graph
        
        # Collect comprehensive page content
        page_content = page.evaluate("""
            () => {
                return {
                    url: window.location.href,
                    title: document.title,
                    forms: Array.from(document.forms).map(form => ({
                        id: form.id,
                        name: form.name,
                        action: form.action,
                        method: form.method,
                        fields: Array.from(form.elements).map(el => ({
                            name: el.name,
                            type: el.type,
                            id: el.id,
                            value: el.value,
                            required: el.required,
                            placeholder: el.placeholder
                        }))
                    })),
                    buttons: Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"]')).map(btn => ({
                        text: btn.textContent || btn.value,
                        type: btn.type,
                        id: btn.id,
                        className: btn.className,
                        disabled: btn.disabled
                    })),
                    navigation: Array.from(document.querySelectorAll('a, button')).map(link => ({
                        text: link.textContent?.trim(),
                        href: link.href,
                        className: link.className,
                        id: link.id
                    })),
                    pageText: document.body.innerText
                };
            }
        """)
        
        # Perform blind detection
        state_model = state["state_model"]
        detection_result = state_model.detect_current_condition(page_content)
        
        # Map detection result to page type
        if "login" in detection_result["page_type"].lower():
            state["current_page_type"] = PageDetectionResult.LOGIN_REQUIRED
        elif "project overview" in detection_result["page_type"].lower():
            state["current_page_type"] = PageDetectionResult.PROJECT_OVERVIEW
        elif "project details" in detection_result["page_type"].lower():
            state["current_page_type"] = PageDetectionResult.PROJECT_DETAILS
        elif "manage team" in detection_result["page_type"].lower():
            state["current_page_type"] = PageDetectionResult.MANAGE_TEAM
        elif "additional info" in detection_result["page_type"].lower():
            state["current_page_type"] = PageDetectionResult.ADDITIONAL_INFO
        elif "submission" in detection_result["page_type"].lower():
            state["current_page_type"] = PageDetectionResult.SUBMISSION_REVIEW
        else:
            state["current_page_type"] = PageDetectionResult.UNKNOWN
        
        # Capture screenshot and calculate visual hash
        screenshot_path = f"devpost_detection_{int(time.time())}.png"
        page.screenshot(path=screenshot_path)
        state["page_screenshot_path"] = screenshot_path
        
        # Calculate visual hash for comparison
        try:
            from PIL import Image
            import imagehash
            with Image.open(screenshot_path) as img:
                phash = imagehash.phash(img)
                state["page_visual_hash"] = str(phash)
        except ImportError:
            import hashlib
            with open(screenshot_path, 'rb') as f:
                state["page_visual_hash"] = hashlib.md5(f.read()).hexdigest()
        
        # Add page telemetry to graph
        telemetry_graph = state["telemetry_graph"]
        telemetry_graph.add_page_telemetry(
            url=page.url,
            title=page.title(),
            dom_structure=page_content,
            navigation_elements=page_content.get("navigation", []),
            form_data=page_content.get("forms", []),
            interactive_elements=page_content.get("buttons", []),
            screenshot=screenshot_path,
            visual_hash=state["page_visual_hash"]
        )
        
        # Update navigation history
        state["navigation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "url": page.url,
            "page_type": state["current_page_type"].value,
            "detection_result": detection_result
        })
        
        # Update performance metrics
        detection_time = time.time() - start_time
        update_performance_metrics(state, {
            "page_detection_time": detection_time,
            "page_type": state["current_page_type"].value,
            "forms_detected": len(page_content.get("forms", [])),
            "navigation_elements": len(page_content.get("navigation", [])),
            "visual_hash": state["page_visual_hash"]
        })
        
        state["messages"].append(
            AIMessage(content=f"🔍 Page detected as: {state['current_page_type'].value}")
        )
        
        # Determine next phase based on page type
        if state["current_page_type"] == PageDetectionResult.LOGIN_REQUIRED:
            update_phase(state, WorkflowPhase.ERROR_RECOVERY)
            set_user_input_required(state, True)
        elif state["current_page_type"] in [
            PageDetectionResult.PROJECT_OVERVIEW,
            PageDetectionResult.PROJECT_DETAILS,
            PageDetectionResult.MANAGE_TEAM,
            PageDetectionResult.ADDITIONAL_INFO
        ]:
            update_phase(state, WorkflowPhase.FORM_ANALYSIS)
        elif state["current_page_type"] == PageDetectionResult.SUBMISSION_REVIEW:
            update_phase(state, WorkflowPhase.VALIDATION)
        else:
            update_phase(state, WorkflowPhase.NAVIGATION)
        
    except Exception as e:
        add_error(state, f"Page detection failed: {str(e)}")
        increment_recovery_attempts(state)
    
    return state


def form_analysis_node(state: DevPostState) -> DevPostState:
    """
    Node: Form Analysis
    
    Analyzes forms on the current page and determines completion strategy.
    """
    
    print("📋 Form Analysis Node")
    start_time = time.time()
    
    try:
        browser_manager = state.get("browser_session_manager")
        if not browser_manager or not browser_manager.context:
            add_error(state, "Browser not available for form analysis")
            return state
        
        page = browser_manager.context.pages[0]
        
        # Initialize site navigation session if not exists
        if not state.get("site_navigation_session"):
            nav_session = SiteNavigationSession(
                session_id=state["workflow_id"],
                target_url=page.url
            )
            state["site_navigation_session"] = nav_session
        
        # Get detailed form information
        form_info = page.evaluate("""
            () => {
                const forms = Array.from(document.forms);
                return forms.map(form => ({
                    id: form.id,
                    name: form.name,
                    action: form.action,
                    method: form.method,
                    fields: Array.from(form.elements).map(el => ({
                        name: el.name,
                        type: el.type,
                        id: el.id,
                        value: el.value,
                        required: el.required,
                        placeholder: el.placeholder,
                        options: el.tagName === 'SELECT' ? Array.from(el.options).map(opt => ({
                            value: opt.value,
                            text: opt.text
                        })) : null
                    }))
                }));
            }
        """)
        
        # Analyze each form
        for form in form_info:
            form_name = form.get("name") or form.get("id") or "unknown_form"
            
            # Determine form type based on fields and context
            form_type = "unknown"
            if any("project" in field.get("name", "").lower() for field in form["fields"]):
                if "description" in str([f.get("name", "") for f in form["fields"]]).lower():
                    form_type = "project_details"
                else:
                    form_type = "project_overview"
            elif any("team" in field.get("name", "").lower() for field in form["fields"]):
                form_type = "manage_team"
            elif any("additional" in field.get("name", "").lower() for field in form["fields"]):
                form_type = "additional_info"
            
            # Store form data
            state["form_data"][form_name] = {
                "form_info": form,
                "form_type": form_type,
                "fields": form["fields"],
                "completion_strategy": "auto_fill" if form_type != "unknown" else "manual_review"
            }
            
            # Update form completion status
            if form_type != "unknown":
                update_form_status(state, form_type, FormCompletionStatus.IN_PROGRESS)
        
        # Update performance metrics
        analysis_time = time.time() - start_time
        update_performance_metrics(state, {
            "form_analysis_time": analysis_time,
            "forms_analyzed": len(form_info),
            "forms_identified": len([f for f in state["form_data"].values() if f["form_type"] != "unknown"])
        })
        
        state["messages"].append(
            AIMessage(content=f"📋 Analyzed {len(form_info)} forms, identified {len([f for f in state['form_data'].values() if f['form_type'] != 'unknown'])} known form types")
        )
        
        # Move to form population phase
        update_phase(state, WorkflowPhase.FORM_POPULATION)
        
    except Exception as e:
        add_error(state, f"Form analysis failed: {str(e)}")
        increment_recovery_attempts(state)
    
    return state


def form_population_node(state: DevPostState) -> DevPostState:
    """
    Node: Form Population
    
    Populates forms with Beast Mode project data.
    """
    
    print("✏️ Form Population Node")
    start_time = time.time()
    
    try:
        browser_manager = state.get("browser_session_manager")
        if not browser_manager or not browser_manager.context:
            add_error(state, "Browser not available for form population")
            return state
        
        page = browser_manager.context.pages[0]
        
        # Beast Mode project data
        project_data = {
            "project_overview": {
                "name": "Beast Mode Framework",
                "tagline": "Systematic AI-Powered Development Framework",
                "description": "A comprehensive framework that transforms software development through systematic AI integration, domain-driven design, and collaborative automation.",
                "built_with": ["Python", "FastAPI", "Playwright", "LangGraph", "Redis"],
                "github_url": "https://github.com/beast-mode/framework",
                "demo_url": "https://beast-mode.dev"
            },
            "project_details": {
                "detailed_description": """
                Beast Mode Framework is a revolutionary development platform that addresses the core challenges in modern software development:

                🎯 **Systematic Approach**: Instead of ad-hoc AI tools, Beast Mode provides a structured framework with clear patterns, workflows, and best practices.

                🏗️ **Domain-Driven Design Integration**: Built-in support for DDD concepts, bounded contexts, and domain modeling with AI assistance.

                🤖 **Intelligent Automation**: Advanced browser automation, form population, testing, and deployment workflows powered by LangGraph orchestration.

                🔄 **Reflective Development**: Self-monitoring, self-improving systems that learn from development patterns and optimize workflows.

                🚀 **Enterprise Ready**: Production-grade architecture with Redis, monitoring, error handling, and scalable deployment options.

                The framework includes modules for messaging, domain modeling, browser automation, and AI orchestration - making it the perfect foundation for any development team looking to leverage AI systematically.
                """,
                "challenges_faced": [
                    "Integrating multiple AI tools into a cohesive workflow",
                    "Maintaining code quality while accelerating development",
                    "Balancing automation with human oversight",
                    "Creating reusable patterns for different project types"
                ],
                "accomplishments": [
                    "Built comprehensive browser automation with Playwright integration",
                    "Implemented LangGraph orchestration for complex workflows",
                    "Created domain-driven design tooling with AI assistance",
                    "Developed reflective monitoring and optimization systems"
                ],
                "lessons_learned": [
                    "AI tools work best when integrated systematically rather than ad-hoc",
                    "Domain modeling with AI assistance significantly improves code quality",
                    "Browser automation requires robust error handling and recovery",
                    "Reflective systems provide valuable insights for continuous improvement"
                ]
            },
            "manage_team": {
                "team_members": [
                    {
                        "name": "Beast Mode Development Team",
                        "role": "Full-Stack Developer",
                        "email": "team@beastmode.dev",
                        "github": "beast-mode"
                    }
                ]
            },
            "additional_info": {
                "devpost_url": "https://devpost.com/software/beast-mode-framework",
                "demo_video": "https://youtube.com/watch?v=beast-mode-demo",
                "screenshots": [
                    "https://beast-mode.dev/screenshots/architecture.png",
                    "https://beast-mode.dev/screenshots/automation.png",
                    "https://beast-mode.dev/screenshots/ddd-tooling.png"
                ]
            }
        }
        
        # Populate each identified form
        forms_populated = 0
        for form_name, form_data in state["form_data"].items():
            form_type = form_data.get("form_type")
            
            if form_type in project_data:
                # Populate form fields
                for field in form_data["fields"]:
                    field_name = field.get("name", "").lower()
                    field_type = field.get("type", "")
                    
                    # Map field names to project data
                    if "name" in field_name and form_type == "project_overview":
                        page.fill(f'[name="{field["name"]}"]', project_data[form_type]["name"])
                    elif "tagline" in field_name and form_type == "project_overview":
                        page.fill(f'[name="{field["name"]}"]', project_data[form_type]["tagline"])
                    elif "description" in field_name:
                        if form_type == "project_overview":
                            page.fill(f'[name="{field["name"]}"]', project_data[form_type]["description"])
                        elif form_type == "project_details":
                            page.fill(f'[name="{field["name"]}"]', project_data[form_type]["detailed_description"])
                    elif "built" in field_name or "tech" in field_name:
                        if form_type == "project_overview":
                            page.fill(f'[name="{field["name"]}"]', ", ".join(project_data[form_type]["built_with"]))
                    elif "github" in field_name or "repo" in field_name:
                        if form_type == "project_overview":
                            page.fill(f'[name="{field["name"]}"]', project_data[form_type]["github_url"])
                    elif "demo" in field_name or "url" in field_name:
                        if form_type == "project_overview":
                            page.fill(f'[name="{field["name"]}"]', project_data[form_type]["demo_url"])
                    elif "challenge" in field_name:
                        if form_type == "project_details":
                            page.fill(f'[name="{field["name"]}"]', "\n".join([f"• {challenge}" for challenge in project_data[form_type]["challenges_faced"]]))
                    elif "accomplishment" in field_name:
                        if form_type == "project_details":
                            page.fill(f'[name="{field["name"]}"]', "\n".join([f"• {accomplishment}" for accomplishment in project_data[form_type]["accomplishments"]]))
                    elif "lesson" in field_name:
                        if form_type == "project_details":
                            page.fill(f'[name="{field["name"]}"]', "\n".join([f"• {lesson}" for lesson in project_data[form_type]["lessons_learned"]]))
                
                # Mark form as completed
                update_form_status(state, form_type, FormCompletionStatus.COMPLETED)
                forms_populated += 1
        
        # Update performance metrics
        population_time = time.time() - start_time
        update_performance_metrics(state, {
            "form_population_time": population_time,
            "forms_populated": forms_populated
        })
        
        state["messages"].append(
            AIMessage(content=f"✏️ Populated {forms_populated} forms with Beast Mode project data")
        )
        
        # Move to form submission phase
        update_phase(state, WorkflowPhase.FORM_SUBMISSION)
        
    except Exception as e:
        add_error(state, f"Form population failed: {str(e)}")
        increment_recovery_attempts(state)
    
    return state


def form_submission_node(state: DevPostState) -> DevPostState:
    """
    Node: Form Submission
    
    Handles saving and continuing through forms.
    """
    
    print("💾 Form Submission Node")
    start_time = time.time()
    
    try:
        browser_manager = state.get("browser_session_manager")
        if not browser_manager or not browser_manager.context:
            add_error(state, "Browser not available for form submission")
            return state
        
        page = browser_manager.context.pages[0]
        
        # Find and click save/continue buttons
        save_buttons = page.query_selector_all(
            'button:has-text("Save"), button:has-text("Continue"), button:has-text("Next"), '
            'input[type="submit"]:has-text("Save"), input[type="submit"]:has-text("Continue"), '
            'button[type="submit"], .save-button, .continue-button, .next-button'
        )
        
        if save_buttons:
            # Try to click the most relevant save button
            for button in save_buttons:
                button_text = button.text_content().lower()
                if any(keyword in button_text for keyword in ["save", "continue", "next"]):
                    button.click()
                    page.wait_for_load_state("networkidle")
                    
                    # Update navigation history
                    state["navigation_history"].append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "form_submission",
                        "button_clicked": button_text,
                        "url_after": page.url
                    })
                    
                    break
            
            # Mark all completed forms as submitted
            for form_type, status in state["form_completion_status"].items():
                if status == FormCompletionStatus.COMPLETED:
                    update_form_status(state, form_type, FormCompletionStatus.SUBMITTED)
            
            # Update performance metrics
            submission_time = time.time() - start_time
            update_performance_metrics(state, {
                "form_submission_time": submission_time,
                "buttons_found": len(save_buttons)
            })
            
            state["messages"].append(
                AIMessage(content="💾 Form submitted successfully, navigating to next step")
            )
            
            # Move to navigation phase to handle next page
            update_phase(state, WorkflowPhase.NAVIGATION)
        else:
            add_error(state, "No save/continue buttons found on page")
            return state
        
    except Exception as e:
        add_error(state, f"Form submission failed: {str(e)}")
        increment_recovery_attempts(state)
    
    return state


def navigation_node(state: DevPostState) -> DevPostState:
    """
    Node: Navigation Management
    
    Handles page navigation and routing decisions using session recovery insights.
    This implements the sophisticated navigation strategies you described:
    - Exact match navigation models
    - Visual similarity adaptation
    - Semantic navigation for dynamic content
    - Site-specific quirk handling
    """
    
    print("🧭 Navigation Node")
    start_time = time.time()
    
    try:
        browser_manager = state.get("browser_session_manager")
        if not browser_manager or not browser_manager.context:
            add_error(state, "Browser not available for navigation")
            return state
        
        page = browser_manager.context.pages[0]
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        # Check if we've reached the final submission page
        if "submission" in page.url.lower() or "review" in page.url.lower():
            update_phase(state, WorkflowPhase.VALIDATION)
            return state
        
        # Get navigation model from session recovery
        navigation_model = state.get("navigation_model", "fresh_model")
        session_recovery = state.get("session_recovery", {})
        
        print(f"🧭 Using navigation model: {navigation_model}")
        
        # Check if there are more forms to complete
        incomplete_forms = [
            form_type for form_type, status in state["form_completion_status"].items()
            if status in [FormCompletionStatus.NOT_STARTED, FormCompletionStatus.IN_PROGRESS]
        ]
        
        if incomplete_forms:
            # Apply navigation strategy based on session recovery insights
            navigation_success = False
            
            # Get multi-dimensional analysis from session recovery for nuanced strategies
            session_recovery = state.get("session_recovery", {})
            confidence = session_recovery.get("confidence", 0.0)
            overall_confidence = session_recovery.get("overall_confidence", confidence)
            primary_strategy = session_recovery.get("primary_strategy", "standard_navigation")
            test_plan = session_recovery.get("test_plan", [])
            
            # Use multi-dimensional analysis to select navigation strategy
            if primary_strategy == "high_confidence_navigation":
                # High confidence - use most appropriate strategy
                if navigation_model == "semantic_navigation":
                    navigation_success = _semantic_navigation(page, state)
                elif navigation_model == "adaptive_navigation":
                    navigation_success = _adaptive_navigation(page, state)
                elif navigation_model == "visual_adapted":
                    navigation_success = _visual_adapted_navigation(page, state)
                else:
                    navigation_success = _standard_navigation(page, state)
                    
            elif primary_strategy == "moderate_confidence_navigation":
                # Moderate confidence - use cautious approach
                navigation_success = _cautious_navigation(page, state)
                
            elif primary_strategy == "cautious_investigative_navigation":
                # Cautious - use investigative approach
                navigation_success = _investigative_navigation(page, state)
                
            elif primary_strategy == "exploratory_navigation":
                # Low confidence - use exploratory approach
                navigation_success = _exploratory_navigation(page, state, test_plan)
                
            else:
                # Fallback to confidence-based selection
                if confidence < 0.2:
                    navigation_success = _investigative_navigation(page, state)
                elif confidence < 0.4:
                    navigation_success = _cautious_navigation(page, state)
                else:
                    navigation_success = _standard_navigation(page, state)
            
            if navigation_success:
                # Move to page detection for the new page
                update_phase(state, WorkflowPhase.PAGE_DETECTION)
            else:
                # No clear navigation path, require user input
                set_user_input_required(state, True)
                state["next_action"] = "manual_navigation_required"
        else:
            # All forms completed, move to validation
            update_phase(state, WorkflowPhase.VALIDATION)
        
        # Update performance metrics
        navigation_time = time.time() - start_time
        update_performance_metrics(state, {
            "navigation_time": navigation_time,
            "incomplete_forms": len(incomplete_forms),
            "navigation_model_used": navigation_model
        })
        
        state["messages"].append(
            AIMessage(content=f"🧭 Navigation completed using {navigation_model}, {len(incomplete_forms)} forms remaining")
        )
        
    except Exception as e:
        add_error(state, f"Navigation failed: {str(e)}")
        increment_recovery_attempts(state)
    
    return state


def _semantic_navigation(page, state: DevPostState) -> bool:
    """Semantic navigation for dynamic content (LinkedIn mystery land scenario)"""
    
    print("🧭 Using semantic navigation strategy")
    
    # Look for navigation elements by semantic meaning rather than position
    semantic_selectors = [
        'a[href*="project"]',
        'a[href*="details"]', 
        'a[href*="team"]',
        'a[href*="additional"]',
        'button:has-text("Next")',
        'button:has-text("Continue")',
        '[data-testid*="next"]',
        '[data-testid*="continue"]'
    ]
    
    for selector in semantic_selectors:
        try:
            elements = page.query_selector_all(selector)
            if elements:
                # Click the first valid element
                elements[0].click()
                page.wait_for_load_state("networkidle")
                
                state["navigation_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "semantic_navigation",
                    "selector_used": selector,
                    "url_after": page.url
                })
                return True
        except:
            continue
    
    return False


def _adaptive_navigation(page, state: DevPostState) -> bool:
    """Adaptive navigation for site-specific quirks (DevPost quirks)"""
    
    print("🧭 Using adaptive navigation strategy")
    
    # Check for DevPost-specific quirks
    session_recovery = state.get("session_recovery", {})
    quirk_data = session_recovery.get("similarity_result", {}).get("matched_page_data", {})
    
    if quirk_data.get("quirk_type") == "devpost_manage_team_save_button":
        # Handle DevPost save button quirk
        return _handle_devpost_save_button_quirk(page, state)
    
    # Fall back to semantic navigation
    return _semantic_navigation(page, state)


def _handle_devpost_save_button_quirk(page, state: DevPostState) -> bool:
    """Handle the specific DevPost save button quirk"""
    
    print("🧭 Handling DevPost save button quirk")
    
    # Try multiple save button strategies
    save_strategies = [
        'button:has-text("Save & Continue")',
        'button:has-text("Save and Continue")', 
        'input[type="submit"][value*="Save"]',
        'button[type="submit"]',
        '.save-button',
        '.continue-button'
    ]
    
    for strategy in save_strategies:
        try:
            buttons = page.query_selector_all(strategy)
            if buttons:
                for button in buttons:
                    if not button.is_disabled():
                        button.click()
                        page.wait_for_load_state("networkidle", timeout=10000)
                        
                        state["navigation_history"].append({
                            "timestamp": datetime.now().isoformat(),
                            "action": "devpost_quirk_navigation",
                            "strategy_used": strategy,
                            "url_after": page.url
                        })
                        return True
        except:
            continue
    
    return False


def _visual_adapted_navigation(page, state: DevPostState) -> bool:
    """Visual similarity adapted navigation"""
    
    print("🧭 Using visual adapted navigation strategy")
    
    # Use existing navigation model but adapt for visual differences
    session_recovery = state.get("session_recovery", {})
    matched_data = session_recovery.get("similarity_result", {}).get("matched_page_data", {})
    
    if matched_data:
        # Look for similar navigation patterns
        existing_nav = matched_data.get("navigation_elements", [])
        
        # Find current navigation elements that match the pattern
        current_nav = page.evaluate("""
            () => Array.from(document.querySelectorAll('a, button')).map(el => ({
                text: el.textContent?.trim(),
                href: el.href || null,
                type: el.type || el.tagName.toLowerCase()
            }))
        """)
        
        # Match navigation elements by text similarity
        for existing_elem in existing_nav:
            existing_text = existing_elem.get("text", "").lower()
            for current_elem in current_nav:
                current_text = current_elem.get("text", "").lower()
                if existing_text and current_text and existing_text in current_text:
                    # Found similar navigation element
                    try:
                        element = page.query_selector(f'text="{current_elem["text"]}"')
                        if element:
                            element.click()
                            page.wait_for_load_state("networkidle")
                            
                            state["navigation_history"].append({
                                "timestamp": datetime.now().isoformat(),
                                "action": "visual_adapted_navigation",
                                "matched_text": current_text,
                                "url_after": page.url
                            })
                            return True
                    except:
                        continue
    
    # Fall back to semantic navigation
    return _semantic_navigation(page, state)


def _investigative_navigation(page, state: DevPostState) -> bool:
    """Investigative navigation for very uncertain states - "I'm gonna have to look around" """
    
    print("🔍 Using investigative navigation strategy - looking around carefully")
    
    # First, gather more information about the page
    page_info = page.evaluate("""
        () => {
            return {
                title: document.title,
                url: window.location.href,
                allLinks: Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.textContent?.trim(),
                    href: a.href,
                    visible: a.offsetParent !== null
                })),
                allButtons: Array.from(document.querySelectorAll('button, input[type="submit"]')).map(b => ({
                    text: b.textContent || b.value,
                    type: b.type,
                    visible: b.offsetParent !== null
                })),
                pageText: document.body.innerText.substring(0, 500) // First 500 chars
            };
        }
    """)
    
    # Log what we found for investigation
    print(f"🔍 Investigative findings:")
    print(f"   Title: {page_info['title']}")
    print(f"   URL: {page_info['url']}")
    print(f"   Links found: {len(page_info['allLinks'])}")
    print(f"   Buttons found: {len(page_info['allButtons'])}")
    print(f"   Page text preview: {page_info['pageText'][:100]}...")
    
    # Try to find navigation elements by analyzing the page content
    visible_links = [link for link in page_info['allLinks'] if link['visible'] and link['text']]
    visible_buttons = [btn for btn in page_info['allButtons'] if btn['visible'] and btn['text']]
    
    # Look for common navigation keywords in visible elements
    navigation_keywords = ["next", "continue", "project", "details", "team", "additional", "submit", "save"]
    
    for link in visible_links:
        link_text = link['text'].lower()
        if any(keyword in link_text for keyword in navigation_keywords):
            try:
                element = page.query_selector(f'a:has-text("{link["text"]}")')
                if element:
                    element.click()
                    page.wait_for_load_state("networkidle")
                    
                    state["navigation_history"].append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "investigative_navigation",
                        "link_clicked": link_text,
                        "url_after": page.url,
                        "investigation_data": page_info
                    })
                    return True
            except:
                continue
    
    # If no links worked, try buttons
    for button in visible_buttons:
        button_text = button['text'].lower()
        if any(keyword in button_text for keyword in navigation_keywords):
            try:
                element = page.query_selector(f'button:has-text("{button["text"]}"), input[value="{button["text"]}"]')
                if element:
                    element.click()
                    page.wait_for_load_state("networkidle")
                    
                    state["navigation_history"].append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "investigative_navigation",
                        "button_clicked": button_text,
                        "url_after": page.url,
                        "investigation_data": page_info
                    })
                    return True
            except:
                continue
    
    print("🔍 Investigation complete - no clear navigation path found")
    return False


def _cautious_navigation(page, state: DevPostState) -> bool:
    """Cautious navigation for moderately uncertain states - "I think I'm on the right track, but need to verify" """
    
    print("🤔 Using cautious navigation strategy - proceeding carefully")
    
    # Get session recovery data for context
    session_recovery = state.get("session_recovery", {})
    matched_data = session_recovery.get("similarity_result", {}).get("matched_page_data", {})
    
    # Start with standard navigation but with extra verification
    next_links = page.query_selector_all(
        'a:has-text("Next"), a:has-text("Continue"), a:has-text("Project"), '
        'a:has-text("Details"), a:has-text("Team"), a:has-text("Additional")'
    )
    
    if next_links:
        # Be more selective about which link to click
        for link in next_links:
            link_text = link.text_content().lower()
            link_href = link.get_attribute('href') or ''
            
            # Extra verification - check if this looks like a reasonable next step
            if any(keyword in link_text for keyword in ["next", "continue", "project", "details", "team", "additional"]):
                # Additional verification - make sure the link looks valid
                if link_href and not link_href.startswith('javascript:'):
                    try:
                        # Double-check the element is still valid
                        if link.is_visible() and not link.is_disabled():
                            print(f"🤔 Cautiously clicking: {link_text} -> {link_href}")
                            link.click()
                            page.wait_for_load_state("networkidle")
                            
                            state["navigation_history"].append({
                                "timestamp": datetime.now().isoformat(),
                                "action": "cautious_navigation",
                                "link_clicked": link_text,
                                "url_after": page.url,
                                "verification": "passed"
                            })
                            return True
                    except Exception as e:
                        print(f"🤔 Cautious navigation failed for {link_text}: {e}")
                        continue
    
    # If standard cautious navigation failed, try semantic navigation as fallback
    print("🤔 Standard cautious navigation failed, trying semantic approach")
    return _semantic_navigation(page, state)


def _exploratory_navigation(page, state: DevPostState, test_plan: List[str]) -> bool:
    """Exploratory navigation for low confidence states - "Let me test and see if it's like what I've seen before" """
    
    print("🔬 Using exploratory navigation strategy - testing context across dimensions")
    
    # Execute test plan from multi-dimensional analysis
    print(f"📋 Executing test plan: {', '.join(test_plan[:3])}...")
    
    # Comprehensive page exploration
    page_exploration = page.evaluate("""
        () => {
            return {
                title: document.title,
                url: window.location.href,
                allClickableElements: Array.from(document.querySelectorAll('a, button, input[type="submit"], input[type="button"], [onclick], [role="button"]')).map(el => ({
                    tagName: el.tagName,
                    text: el.textContent?.trim() || el.value || '',
                    href: el.href || null,
                    type: el.type || null,
                    className: el.className,
                    id: el.id,
                    visible: el.offsetParent !== null,
                    enabled: !el.disabled
                })),
                allForms: Array.from(document.forms).map(form => ({
                    id: form.id,
                    name: form.name,
                    action: form.action,
                    method: form.method,
                    fieldCount: form.elements.length
                })),
                pageStructure: {
                    headings: Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => h.textContent?.trim()),
                    paragraphs: Array.from(document.querySelectorAll('p')).length,
                    lists: Array.from(document.querySelectorAll('ul, ol')).length,
                    images: Array.from(document.querySelectorAll('img')).length
                },
                breadcrumbs: Array.from(document.querySelectorAll('[role="navigation"], .breadcrumb, .breadcrumbs')).map(nav => ({
                    text: nav.textContent?.trim(),
                    links: Array.from(nav.querySelectorAll('a')).map(a => a.textContent?.trim())
                })),
                progressIndicators: Array.from(document.querySelectorAll('.progress, .step, .indicator, [role="progressbar"]')).map(prog => ({
                    text: prog.textContent?.trim(),
                    value: prog.getAttribute('value') || prog.getAttribute('data-value')
                }))
            };
        }
    """)
    
    print(f"🔬 Exploratory findings:")
    print(f"   Title: {page_exploration['title']}")
    print(f"   Clickable elements: {len(page_exploration['allClickableElements'])}")
    print(f"   Forms: {len(page_exploration['allForms'])}")
    print(f"   Structure: {page_exploration['pageStructure']['headings'][:3]}...")
    
    # Try different navigation strategies based on exploration
    navigation_attempts = []
    
    # Strategy 1: Look for semantic navigation elements
    semantic_elements = [
        el for el in page_exploration['allClickableElements'] 
        if el['visible'] and el['enabled'] and any(
            keyword in el['text'].lower() 
            for keyword in ['next', 'continue', 'submit', 'save', 'project', 'details', 'team', 'additional']
        )
    ]
    
    if semantic_elements:
        navigation_attempts.append(("semantic", semantic_elements[0]))
    
    # Strategy 2: Look for form submission
    if page_exploration['allForms']:
        submit_buttons = [
            el for el in page_exploration['allClickableElements']
            if el['visible'] and el['enabled'] and el['type'] in ['submit', 'button'] and
            any(keyword in el['text'].lower() for keyword in ['submit', 'save', 'continue', 'next'])
        ]
        if submit_buttons:
            navigation_attempts.append(("form_submit", submit_buttons[0]))
    
    # Strategy 3: Look for breadcrumb navigation
    if page_exploration['breadcrumbs']:
        breadcrumb_links = []
        for breadcrumb in page_exploration['breadcrumbs']:
            breadcrumb_links.extend(breadcrumb['links'])
        if breadcrumb_links:
            # Try to find the next breadcrumb item
            for link_text in breadcrumb_links:
                if any(keyword in link_text.lower() for keyword in ['next', 'continue', 'project', 'details']):
                    navigation_attempts.append(("breadcrumb", {"text": link_text}))
                    break
    
    # Strategy 4: Look for progress indicators
    if page_exploration['progressIndicators']:
        # Look for "next step" in progress indicators
        for indicator in page_exploration['progressIndicators']:
            if indicator['text'] and any(keyword in indicator['text'].lower() for keyword in ['next', 'step', 'continue']):
                navigation_attempts.append(("progress", indicator))
    
    # Execute navigation attempts
    for strategy_name, element_data in navigation_attempts:
        try:
            print(f"🔬 Trying {strategy_name} navigation strategy...")
            
            if strategy_name == "semantic":
                # Click semantic element
                element = page.query_selector(f'text="{element_data["text"]}"')
                if element:
                    element.click()
                    page.wait_for_load_state("networkidle")
                    
                    state["navigation_history"].append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "exploratory_navigation",
                        "strategy": strategy_name,
                        "element_clicked": element_data["text"],
                        "url_after": page.url,
                        "exploration_data": page_exploration
                    })
                    return True
                    
            elif strategy_name == "form_submit":
                # Submit form
                element = page.query_selector(f'input[value="{element_data["text"]}"], button:has-text("{element_data["text"]}")')
                if element:
                    element.click()
                    page.wait_for_load_state("networkidle")
                    
                    state["navigation_history"].append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "exploratory_navigation",
                        "strategy": strategy_name,
                        "element_clicked": element_data["text"],
                        "url_after": page.url,
                        "exploration_data": page_exploration
                    })
                    return True
                    
        except Exception as e:
            print(f"🔬 {strategy_name} strategy failed: {e}")
            continue
    
    print("🔬 All exploratory navigation strategies failed")
    return False


def _standard_navigation(page, state: DevPostState) -> bool:
    """Standard navigation for fresh models or exact matches"""
    
    print("🧭 Using standard navigation strategy")
    
    # Look for navigation links to next form
    next_links = page.query_selector_all(
        'a:has-text("Next"), a:has-text("Continue"), a:has-text("Project"), '
        'a:has-text("Details"), a:has-text("Team"), a:has-text("Additional")'
    )
    
    if next_links:
        # Click the most relevant next link
        for link in next_links:
            link_text = link.text_content().lower()
            if any(keyword in link_text for keyword in ["next", "continue", "project", "details", "team", "additional"]):
                link.click()
                page.wait_for_load_state("networkidle")
                
                state["navigation_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "standard_navigation",
                    "link_clicked": link_text,
                    "url_after": page.url
                })
                return True
    
    return False


def validation_node(state: DevPostState) -> DevPostState:
    """
    Node: Validation and Quality Assurance
    
    Validates submission completeness and quality.
    """
    
    print("✅ Validation Node")
    start_time = time.time()
    
    try:
        browser_manager = state.get("browser_session_manager")
        if not browser_manager or not browser_manager.context:
            add_error(state, "Browser not available for validation")
            return state
        
        page = browser_manager.context.pages[0]
        
        # Check form completion status
        all_forms_completed = all(
            status in [FormCompletionStatus.COMPLETED, FormCompletionStatus.SUBMITTED]
            for status in state["form_completion_status"].values()
        )
        
        # Calculate quality score based on completion and data richness
        quality_score = 0.0
        if all_forms_completed:
            quality_score += 0.5
        
        # Check if all required project data is present
        required_data_present = all([
            state["form_data"].get("project_overview", {}).get("form_info"),
            state["form_data"].get("project_details", {}).get("form_info"),
        ])
        
        if required_data_present:
            quality_score += 0.3
        
        # Check for errors
        if not state["errors"]:
            quality_score += 0.2
        
        state["quality_score"] = quality_score
        state["submission_ready"] = quality_score >= 0.8
        
        # Store validation results
        state["validation_results"] = {
            "all_forms_completed": all_forms_completed,
            "required_data_present": required_data_present,
            "no_errors": not state["errors"],
            "quality_score": quality_score,
            "submission_ready": state["submission_ready"],
            "completed_forms": [
                form_type for form_type, status in state["form_completion_status"].items()
                if status in [FormCompletionStatus.COMPLETED, FormCompletionStatus.SUBMITTED]
            ]
        }
        
        # Update performance metrics
        validation_time = time.time() - start_time
        update_performance_metrics(state, {
            "validation_time": validation_time,
            "quality_score": quality_score,
            "submission_ready": state["submission_ready"]
        })
        
        if state["submission_ready"]:
            state["messages"].append(
                AIMessage(content=f"✅ Validation passed! Quality score: {quality_score:.2f}. Submission is ready.")
            )
            update_phase(state, WorkflowPhase.COMPLETION)
        else:
            state["messages"].append(
                AIMessage(content=f"⚠️ Validation issues found. Quality score: {quality_score:.2f}. Manual review recommended.")
            )
            set_user_input_required(state, True)
        
    except Exception as e:
        add_error(state, f"Validation failed: {str(e)}")
        increment_recovery_attempts(state)
    
    return state


def completion_node(state: DevPostState) -> DevPostState:
    """
    Node: Workflow Completion
    
    Finalizes the workflow and saves all data.
    """
    
    print("🎉 Completion Node")
    start_time = time.time()
    
    try:
        # Save all session data
        telemetry_graph = state.get("telemetry_graph")
        if telemetry_graph:
            telemetry_graph.save_graph()
            export_file = telemetry_graph.export_for_analysis()
            state["messages"].append(
                AIMessage(content=f"📊 Session data exported to: {export_file}")
            )
        
        # Calculate final session duration
        session_duration = time.time() - start_time
        state["session_duration"] = session_duration
        
        # Update final performance metrics
        update_performance_metrics(state, {
            "completion_time": session_duration,
            "total_workflow_time": (datetime.now() - state["workflow_start_time"]).total_seconds(),
            "forms_completed": len([
                f for f in state["form_completion_status"].values()
                if f in [FormCompletionStatus.COMPLETED, FormCompletionStatus.SUBMITTED]
            ]),
            "pages_visited": len(state["navigation_history"]),
            "errors_encountered": len(state["errors"])
        })
        
        # Save final state
        state_file = f"devpost_workflow_state_{state['workflow_id']}.json"
        from langgraph_devpost_state import save_state_to_file
        save_state_to_file(state, state_file)
        
        state["messages"].append(
            AIMessage(content=f"🎉 Workflow completed successfully! State saved to: {state_file}")
        )
        
        # Final summary
        summary = {
            "workflow_id": state["workflow_id"],
            "duration": session_duration,
            "quality_score": state["quality_score"],
            "forms_completed": len([
                f for f in state["form_completion_status"].values()
                if f in [FormCompletionStatus.COMPLETED, FormCompletionStatus.SUBMITTED]
            ]),
            "pages_visited": len(state["navigation_history"]),
            "errors": len(state["errors"])
        }
        
        print("🎉 Workflow Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        add_error(state, f"Completion failed: {str(e)}")
    
    return state


def error_recovery_node(state: DevPostState) -> DevPostState:
    """
    Node: Error Recovery
    
    Handles errors and recovery attempts.
    """
    
    print("🔄 Error Recovery Node")
    
    try:
        if state["recovery_attempts"] >= state["max_recovery_attempts"]:
            state["messages"].append(
                AIMessage(content="❌ Maximum recovery attempts exceeded. Manual intervention required.")
            )
            set_user_input_required(state, True)
            return state
        
        # Reset recovery attempts on successful recovery
        reset_recovery_attempts(state)
        
        # Try to recover based on error type
        if "browser" in str(state["errors"]).lower():
            update_phase(state, WorkflowPhase.BROWSER_CONNECTION)
        elif "page" in str(state["errors"]).lower():
            update_phase(state, WorkflowPhase.PAGE_DETECTION)
        elif "form" in str(state["errors"]).lower():
            update_phase(state, WorkflowPhase.FORM_ANALYSIS)
        else:
            update_phase(state, WorkflowPhase.NAVIGATION)
        
        state["messages"].append(
            AIMessage(content=f"🔄 Recovery attempt {state['recovery_attempts'] + 1}/{state['max_recovery_attempts']}")
        )
        
    except Exception as e:
        add_error(state, f"Error recovery failed: {str(e)}")
    
    return state
