#!/usr/bin/env python3
"""
Step Navigator
=============

Fixed navigator that only clicks actual step navigation links,
avoiding new tabs and hidden elements.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Navigate between DevPost form steps correctly
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from playwright.sync_api import sync_playwright
from devpost_state_model import DevPostStateModel, create_state_model
from telemetry_graph import TelemetryGraph, create_telemetry_graph

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def _calculate_image_hash(image_path: str) -> str:
    """Calculate perceptual hash for image comparison"""
    try:
        from PIL import Image
        import imagehash
        
        with Image.open(image_path) as img:
            # Use perceptual hash for robust comparison
            phash = imagehash.phash(img)
            return str(phash)
    except ImportError:
        # Fallback to simple file hash if PIL not available
        import hashlib
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"⚠️  Image hash error: {e}")
        return "unknown"


def _find_similar_pages(visual_hash: str, telemetry_graph: TelemetryGraph, threshold: int = 5) -> List[Dict[str, Any]]:
    """Find pages with similar visual content"""
    similar_pages = []
    
    if visual_hash == "unknown":
        return similar_pages
    
    try:
        from PIL import Image
        import imagehash
        
        current_hash = imagehash.hex_to_hash(visual_hash)
        
        for node_id, data in telemetry_graph.graph.nodes(data=True):
            if 'visual_hash' in data and data['visual_hash'] != "unknown":
                try:
                    node_hash = imagehash.hex_to_hash(data['visual_hash'])
                    distance = current_hash - node_hash
                    
                    if distance <= threshold:
                        similar_pages.append({
                            'node_id': node_id,
                            'url': data.get('url', ''),
                            'timestamp': data.get('timestamp', ''),
                            'distance': distance,
                            'screenshot': data.get('screenshot', '')
                        })
                except:
                    continue
        
        # Sort by similarity (lower distance = more similar)
        similar_pages.sort(key=lambda x: x['distance'])
        
    except ImportError:
        # Fallback to exact hash match if imagehash not available
        for node_id, data in telemetry_graph.graph.nodes(data=True):
            if data.get('visual_hash') == visual_hash and data.get('url') != telemetry_graph.current_page_hash:
                similar_pages.append({
                    'node_id': node_id,
                    'url': data.get('url', ''),
                    'timestamp': data.get('timestamp', ''),
                    'distance': 0,
                    'screenshot': data.get('screenshot', '')
                })
    
    return similar_pages


def _save_session_data(telemetry_graph: TelemetryGraph, state_model: DevPostStateModel, force: bool = False) -> bool:
    """Save session data with change detection"""
    if not force and not telemetry_graph.has_changes():
        print("ℹ️  No changes detected - nothing to save")
        return False
    
    print("💾 Saving session data...")
    
    # Save telemetry graph
    telemetry_graph.save_graph()
    
    # Save state model
    state_model.save_state()
    
    # Export comprehensive data for analysis
    export_file = telemetry_graph.export_for_analysis()
    
    # Get session summary
    summary = telemetry_graph.get_session_summary()
    print(f"📊 Session Summary:")
    print(f"   • Pages visited: {summary['total_pages_visited']}")
    print(f"   • Navigations: {summary['total_navigations']}")
    print(f"   • Success rate: {summary['success_rate']:.1f}%")
    print(f"   • Duration: {summary['session_duration']}")
    print(f"   • Export file: {export_file}")
    
    return True

def explore_from_here(page):
    """Comprehensive tree analysis - explore everything discoverable on the page."""
    print(f"\n🌳 EXPLORING FROM HERE - COMPREHENSIVE TREE ANALYSIS")
    print(f"{'='*70}")
    
    # Basic page info
    print(f"📄 Page: {page.title()}")
    print(f"🔗 URL: {page.url}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # DOM structure analysis
    print(f"\n🏗️  DOM STRUCTURE ANALYSIS")
    print(f"{'='*40}")
    
    # Get all elements by tag with comprehensive telemetry
    try:
        all_elements = page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                const tagCounts = {};
                const classCounts = {};
                const idCounts = {};
                const navigationElements = [];
                const formElements = [];
                const interactiveElements = [];
                
                elements.forEach(el => {
                    const tag = el.tagName.toLowerCase();
                    tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                    
                    // Handle className safely
                    if (el.className) {
                        const className = el.className.toString();
                        if (className && className !== '') {
                            className.split(' ').forEach(cls => {
                                if (cls.trim()) classCounts[cls.trim()] = (classCounts[cls.trim()] || 0) + 1;
                            });
                        }
                    }
                    
                    if (el.id) {
                        idCounts[el.id] = (idCounts[el.id] || 0) + 1;
                    }
                    
                    // Collect navigation telemetry
                    if (el.id === 'steps-navigation' || el.classList.contains('step') || el.classList.contains('navigation')) {
                        navigationElements.push({
                            tag: tag,
                            id: el.id || '',
                            className: el.className.toString() || '',
                            text: el.textContent?.trim() || '',
                            href: el.href || ''
                        });
                    }
                    
                    // Collect form telemetry
                    if (['form', 'input', 'textarea', 'select', 'button'].includes(tag)) {
                        formElements.push({
                            tag: tag,
                            id: el.id || '',
                            name: el.name || '',
                            type: el.type || '',
                            className: el.className.toString() || '',
                            value: el.value || '',
                            placeholder: el.placeholder || ''
                        });
                    }
                    
                    // Collect interactive telemetry
                    if (['button', 'a', 'input'].includes(tag) || el.onclick || el.getAttribute('onclick')) {
                        interactiveElements.push({
                            tag: tag,
                            id: el.id || '',
                            className: el.className.toString() || '',
                            text: el.textContent?.trim() || el.value || '',
                            href: el.href || '',
                            onclick: el.onclick ? 'present' : 'none'
                        });
                    }
                });
                
                return {
                    totalElements: elements.length,
                    tagCounts: tagCounts,
                    topClasses: Object.entries(classCounts).sort((a,b) => b[1] - a[1]).slice(0, 10),
                    topIds: Object.entries(idCounts).sort((a,b) => b[1] - a[1]).slice(0, 10),
                    navigationElements: navigationElements,
                    formElements: formElements,
                    interactiveElements: interactiveElements,
                    url: window.location.href,
                    title: document.title,
                    timestamp: new Date().toISOString()
                };
            }
        """)
    except Exception as e:
        print(f"❌ Error in DOM analysis: {e}")
        all_elements = {
            'totalElements': 0,
            'tagCounts': {},
            'topClasses': [],
            'topIds': [],
            'navigationElements': [],
            'formElements': [],
            'interactiveElements': [],
            'url': page.url,
            'title': page.title(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    print(f"📊 Total Elements: {all_elements['totalElements']}")
    print(f"\n🏷️  Top 10 Most Common Tags:")
    for tag, count in sorted(all_elements['tagCounts'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {tag}: {count}")
    
    print(f"\n🎨 Top 10 Most Common Classes:")
    for cls, count in all_elements['topClasses']:
        print(f"   .{cls}: {count}")
    
    print(f"\n🆔 Top 10 Most Common IDs:")
    for id_name, count in all_elements['topIds']:
        print(f"   #{id_name}: {count}")
    
    # Forms analysis
    print(f"\n📋 FORMS ANALYSIS")
    print(f"{'='*30}")
    forms = page.query_selector_all("form")
    print(f"📝 Total Forms: {len(forms)}")
    
    for i, form in enumerate(forms, 1):
        form_id = form.get_attribute("id") or "no-id"
        form_class = form.get_attribute("class") or "no-class"
        form_action = form.get_attribute("action") or "no-action"
        form_method = form.get_attribute("method") or "GET"
        
        print(f"\n   Form {i}:")
        print(f"      ID: {form_id}")
        print(f"      Class: {form_class}")
        print(f"      Action: {form_action}")
        print(f"      Method: {form_method}")
        
        # Form inputs
        inputs = form.query_selector_all("input, textarea, select")
        print(f"      Inputs: {len(inputs)}")
        for j, inp in enumerate(inputs, 1):
            inp_type = inp.get_attribute("type") or inp.tag_name
            inp_name = inp.get_attribute("name") or "no-name"
            inp_id = inp.get_attribute("id") or "no-id"
            inp_value = inp.get_attribute("value") or ""
            inp_placeholder = inp.get_attribute("placeholder") or ""
            is_required = inp.get_attribute("required") is not None
            
            print(f"         {j}. {inp_type}: {inp_name} | {inp_id}")
            if inp_value: print(f"            Value: '{inp_value}'")
            if inp_placeholder: print(f"            Placeholder: '{inp_placeholder}'")
            if is_required: print(f"            Required: Yes")
    
    # Interactive elements analysis
    print(f"\n🎮 INTERACTIVE ELEMENTS ANALYSIS")
    print(f"{'='*40}")
    
    buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
    links = page.query_selector_all("a")
    clickable = page.query_selector_all("[onclick], [role='button']")
    
    print(f"🔘 Buttons: {len(buttons)}")
    for i, btn in enumerate(buttons, 1):
        btn_text = btn.text_content().strip() or btn.get_attribute("value") or "no-text"
        btn_type = btn.get_attribute("type") or "button"
        btn_id = btn.get_attribute("id") or "no-id"
        btn_class = btn.get_attribute("class") or "no-class"
        is_disabled = btn.get_attribute("disabled") is not None
        is_visible = btn.is_visible()
        
        print(f"   {i}. {btn_text} ({btn_type})")
        print(f"      ID: {btn_id} | Class: {btn_class}")
        print(f"      Disabled: {is_disabled} | Visible: {is_visible}")
    
    print(f"\n🔗 Links: {len(links)}")
    for i, link in enumerate(links, 1):
        link_text = link.text_content().strip() or "no-text"
        link_href = link.get_attribute("href") or "no-href"
        link_target = link.get_attribute("target") or "same-window"
        is_visible = link.is_visible()
        
        print(f"   {i}. {link_text}")
        print(f"      Href: {link_href}")
        print(f"      Target: {link_target} | Visible: {is_visible}")
    
    # Navigation structure
    print(f"\n🧭 NAVIGATION STRUCTURE")
    print(f"{'='*30}")
    
    nav_elements = page.query_selector_all("nav, [role='navigation'], .nav, .navigation, #navigation")
    breadcrumbs = page.query_selector_all(".breadcrumb, .breadcrumbs, [aria-label*='breadcrumb']")
    menus = page.query_selector_all("menu, .menu, ul.menu, ol.menu")
    
    print(f"🧭 Navigation elements: {len(nav_elements)}")
    print(f"🍞 Breadcrumbs: {len(breadcrumbs)}")
    print(f"📋 Menus: {len(menus)}")
    
    # Step navigation specific
    step_nav = page.query_selector("#steps-navigation")
    if step_nav:
        step_links = step_nav.query_selector_all("a")
        print(f"\n📊 Step Navigation:")
        print(f"   Steps found: {len(step_links)}")
        for i, step in enumerate(step_links, 1):
            step_text = step.text_content().strip()
            step_href = step.get_attribute("href") or ""
            step_class = step.get_attribute("class") or ""
            is_visible = step.is_visible()
            is_enabled = step.is_enabled()
            
            print(f"   {i}. {step_text}")
            print(f"      Href: {step_href}")
            print(f"      Class: {step_class}")
            print(f"      Visible: {is_visible} | Enabled: {is_enabled}")
    
    # Content analysis
    print(f"\n📄 CONTENT ANALYSIS")
    print(f"{'='*25}")
    
    headings = page.query_selector_all("h1, h2, h3, h4, h5, h6")
    paragraphs = page.query_selector_all("p")
    lists = page.query_selector_all("ul, ol")
    images = page.query_selector_all("img")
    
    print(f"📝 Headings: {len(headings)}")
    for i, heading in enumerate(headings, 1):
        heading_text = heading.text_content().strip()
        heading_tag = heading.tag_name.lower()
        print(f"   {i}. <{heading_tag}> {heading_text}")
    
    print(f"\n📄 Paragraphs: {len(paragraphs)}")
    print(f"📋 Lists: {len(lists)}")
    print(f"🖼️  Images: {len(images)}")
    
    # JavaScript analysis
    print(f"\n⚡ JAVASCRIPT ANALYSIS")
    print(f"{'='*30}")
    
    scripts = page.query_selector_all("script")
    inline_scripts = [s for s in scripts if not s.get_attribute("src")]
    external_scripts = [s for s in scripts if s.get_attribute("src")]
    
    print(f"📜 Total Scripts: {len(scripts)}")
    print(f"📜 Inline Scripts: {len(inline_scripts)}")
    print(f"📜 External Scripts: {len(external_scripts)}")
    
    for i, script in enumerate(external_scripts, 1):
        script_src = script.get_attribute("src") or "no-src"
        print(f"   {i}. {script_src}")
    
    # Event listeners (basic detection)
    print(f"\n🎯 EVENT LISTENERS (Basic Detection)")
    print(f"{'='*40}")
    
    clickable_elements = page.query_selector_all("[onclick], [onchange], [onsubmit], [onload], button, a, input[type='button'], input[type='submit']")
    print(f"🎮 Elements with potential event listeners: {len(clickable_elements)}")
    
    # Accessibility analysis
    print(f"\n♿ ACCESSIBILITY ANALYSIS")
    print(f"{'='*30}")
    
    aria_elements = page.query_selector_all("[aria-label], [aria-labelledby], [aria-describedby], [role]")
    alt_images = page.query_selector_all("img[alt]")
    form_labels = page.query_selector_all("label")
    
    print(f"🎯 ARIA elements: {len(aria_elements)}")
    print(f"🖼️  Images with alt text: {len(alt_images)}")
    print(f"🏷️  Form labels: {len(form_labels)}")
    
    # Performance metrics
    print(f"\n⚡ PERFORMANCE METRICS")
    print(f"{'='*25}")
    
    try:
        metrics = page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    loadTime: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0,
                    domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : 0,
                    firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
                    firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
                };
            }
        """)
        
        print(f"⏱️  Load Time: {metrics['loadTime']:.2f}ms")
        print(f"⏱️  DOM Content Loaded: {metrics['domContentLoaded']:.2f}ms")
        print(f"⏱️  First Paint: {metrics['firstPaint']:.2f}ms")
        print(f"⏱️  First Contentful Paint: {metrics['firstContentfulPaint']:.2f}ms")
    except Exception as e:
        print(f"❌ Could not get performance metrics: {e}")
    
    # Take comprehensive screenshot
    timestamp = int(time.time())
    url_parts = page.url.split("/")
    hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
    submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
    page_title = page.title().replace(" ", "_").replace("/", "_")[:20]
    
    filename = f"explore_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
    page.screenshot(path=filename)
    print(f"\n📸 Comprehensive screenshot saved: {filename}")
    
    # Comprehensive Navigation Telemetry
    print(f"\n📊 COMPREHENSIVE NAVIGATION TELEMETRY")
    print(f"{'='*45}")
    
    print(f"🧭 Navigation Elements Found: {len(all_elements['navigationElements'])}")
    for i, nav in enumerate(all_elements['navigationElements'], 1):
        print(f"   {i}. {nav['tag']}: {nav['text']}")
        print(f"      ID: {nav['id']} | Class: {nav['className']}")
        if nav['href']: print(f"      Href: {nav['href']}")
    
    print(f"\n📋 Form Elements Found: {len(all_elements['formElements'])}")
    for i, form in enumerate(all_elements['formElements'], 1):
        print(f"   {i}. {form['tag']}: {form['name'] or form['id'] or 'unnamed'}")
        print(f"      Type: {form['type']} | Class: {form['className']}")
        if form['value']: print(f"      Value: '{form['value']}'")
        if form['placeholder']: print(f"      Placeholder: '{form['placeholder']}'")
    
    print(f"\n🎮 Interactive Elements Found: {len(all_elements['interactiveElements'])}")
    for i, interactive in enumerate(all_elements['interactiveElements'], 1):
        print(f"   {i}. {interactive['tag']}: {interactive['text']}")
        print(f"      ID: {interactive['id']} | Class: {interactive['className']}")
        if interactive['href']: print(f"      Href: {interactive['href']}")
        if interactive['onclick'] == 'present': print(f"      Has onclick handler")
    
    # Save telemetry to file
    timestamp = int(time.time())
    telemetry_file = f"devpost_telemetry_{timestamp}.json"
    with open(telemetry_file, 'w') as f:
        json.dump(all_elements, f, indent=2)
    print(f"\n💾 Complete telemetry saved to: {telemetry_file}")
    
    print(f"\n✅ EXPLORATION COMPLETE!")
    print(f"🌳 This page contains {all_elements['totalElements']} elements with rich interactive content")
    print(f"📊 Collected telemetry on {len(all_elements['navigationElements'])} nav, {len(all_elements['formElements'])} form, {len(all_elements['interactiveElements'])} interactive elements")

def navigate_devpost_steps():
    """Navigate between DevPost form steps correctly."""
    try:
        # Initialize state model and telemetry graph
        state_model = create_state_model()
        telemetry_graph = create_telemetry_graph(state_model.session_id)
        print(f"🎯 State Model initialized: {state_model.session_id}")
        print(f"📊 Telemetry Graph initialized: {telemetry_graph.session_id}")
        
        # Check session resume capability
        resume_info = state_model.check_session_resume_capability()
        if resume_info["can_resume"]:
            print("🔄 Session Resume Capability:")
            for instruction in resume_info["resume_instructions"]:
                print(f"   {instruction}")
            if resume_info["last_url"]:
                print(f"   🔗 Last URL: {resume_info['last_url']}")
        else:
            print("🆕 No previous session data found - starting fresh")
        
        playwright = sync_playwright().start()
        
        # DECISION 1: Is there a browser window? (Prefer existing Chrome with extensions)
        browser = None
        pages_info = []
        
        # Check multiple ports for existing Chrome instances
        chrome_ports = [9222, 9223, 9224, 9225, 9226]
        connected_port = None
        
        for port in chrome_ports:
            try:
                response = requests.get(f"http://localhost:{port}/json", timeout=2)
                if response.status_code == 200:
                    pages_info = response.json()
                    if pages_info:
                        print(f"✅ Found existing Chrome on port {port} with {len(pages_info)} tab(s)")
                        print("🔐 This Chrome instance should have all your extensions (including 1Password)")
                        
                        # Connect to existing browser
                        browser = playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
                        connected_port = port
                        break
            except:
                continue
        
        if not browser:
            print("❌ No existing Chrome instances found with debugging enabled")
            print("💡 TIP: Start Chrome with: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            
            # Check if we have existing session data to preserve
            import os
            user_data_path = "/tmp/devpost-browser"
            if os.path.exists(user_data_path):
                print("💾 Found existing browser session data - preserving cookies and login state")
            else:
                print("🆕 No existing session data - starting fresh")
            
            print("🔧 Starting new browser instance with session preservation...")
            print("⚠️  Note: New browser won't have your Chrome extensions")
            
            # Start a new browser instance with persistent data preservation
            browser = playwright.chromium.launch_persistent_context(
                user_data_dir="/tmp/devpost-browser",
                headless=False,
                # Preserve all session data, cookies, and login state
                args=[
                    "--remote-debugging-port=9222",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-web-security=false",  # Keep security features
                    "--disable-features=VizDisplayCompositor",  # Better compatibility
                    "--no-sandbox",  # Required for some environments
                    "--disable-dev-shm-usage"  # Better memory handling
                ],
                # Preserve login sessions and cookies
                accept_downloads=True,
                bypass_csp=True,
                # Don't clear any existing data
                ignore_default_args=["--disable-extensions"]
            )
            
            # Get pages info for the new browser
            try:
                response = requests.get("http://localhost:9222/json", timeout=3)
                pages_info = response.json()
                print(f"✅ New browser session established with {len(pages_info)} tab(s)!")
            except:
                pages_info = []
        
        # DECISION 2: Which window/tab to use?
        devpost_pages = [page for page in pages_info if "devpost.com" in page.get("url", "")]
        
        if not devpost_pages:
            print("❌ No DevPost tabs found!")
            print("📋 Available tabs:")
            for i, page in enumerate(pages_info):
                print(f"   {i+1}. {page.get('title', 'Untitled')} - {page.get('url', 'No URL')}")
            
            choice = input("🎯 Select tab number (or 'n' for new DevPost tab): ").strip()
            
            if choice.lower() == 'n':
                # Create new DevPost tab
                if hasattr(browser, 'new_page'):
                    target_page = browser.new_page()
                else:
                    target_page = browser.pages[0]
                target_page.goto("https://devpost.com")
                print("🌐 Opened new DevPost tab")
                input("👤 Please navigate to your submission page and press Enter...")
            else:
                try:
                    tab_index = int(choice) - 1
                    if 0 <= tab_index < len(pages_info):
                        if hasattr(browser, 'new_page'):
                            target_page = browser.new_page()
                        else:
                            target_page = browser.pages[0]
                        target_page.goto(pages_info[tab_index]["url"])
                        print(f"✅ Navigated to selected tab: {pages_info[tab_index]['title']}")
                    else:
                        print("❌ Invalid tab selection")
                        return
                except ValueError:
                    print("❌ Invalid input")
                    return
        else:
            print(f"🎯 Found {len(devpost_pages)} DevPost tab(s):")
            for i, page in enumerate(devpost_pages):
                status = "📍 CURRENT" if "submission" in page.get("url", "").lower() else "🌐 OPEN"
                print(f"   {i+1}. {page.get('title', 'Untitled')} - {status}")
                print(f"      {page.get('url', 'No URL')}")
            
            if len(devpost_pages) == 1:
                target_page_url = devpost_pages[0]["url"]
                print(f"🎯 Auto-selecting single DevPost tab: {target_page_url}")
            else:
                choice = input("🎯 Select DevPost tab number: ").strip()
                try:
                    tab_index = int(choice) - 1
                    if 0 <= tab_index < len(devpost_pages):
                        target_page_url = devpost_pages[tab_index]["url"]
                    else:
                        print("❌ Invalid selection")
                        return
                except ValueError:
                    print("❌ Invalid input")
                    return
            
            # Connect to the selected page
            target_page = None
            # Try to find existing page first
            for page in browser.pages:
                if page.url == target_page_url:
                    target_page = page
                    break
            
            # If not found, create new page and navigate
            if not target_page:
                if hasattr(browser, 'new_page'):
                    target_page = browser.new_page()
                else:
                    target_page = browser.pages[0]
                target_page.goto(target_page_url)
        
        print(f"📄 Target page: {target_page.title()}")
        print(f"🔗 URL: {target_page.url}")
        
        # Wait for page to be ready
        print("⏳ Waiting for page to be ready...")
        target_page.wait_for_load_state("networkidle")
        
        # Perform blind detection of current condition
        print("🔍 Performing blind condition detection...")
        page_content = target_page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                const navigationElements = [];
                const formElements = [];
                const interactiveElements = [];
                
                elements.forEach(el => {
                    // Navigation elements
                    if (el.id === 'steps-navigation' || el.classList.contains('step') || el.classList.contains('navigation')) {
                        navigationElements.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || '',
                            className: el.className.toString() || '',
                            text: el.textContent?.trim() || '',
                            href: el.href || ''
                        });
                    }
                    
                    // Form elements
                    if (['form', 'input', 'textarea', 'select', 'button'].includes(el.tagName.toLowerCase())) {
                        formElements.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || '',
                            name: el.name || '',
                            type: el.type || '',
                            className: el.className.toString() || '',
                            value: el.value || '',
                            placeholder: el.placeholder || ''
                        });
                    }
                    
                    // Interactive elements
                    if (['button', 'a', 'input'].includes(el.tagName.toLowerCase()) || el.onclick || el.getAttribute('onclick')) {
                        interactiveElements.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || '',
                            className: el.className.toString() || '',
                            text: el.textContent?.trim() || el.value || '',
                            href: el.href || '',
                            onclick: el.onclick ? 'present' : 'none'
                        });
                    }
                });
                
                return {
                    totalElements: elements.length,
                    navigationElements: navigationElements,
                    formElements: formElements,
                    interactiveElements: interactiveElements,
                    url: window.location.href,
                    title: document.title,
                    timestamp: new Date().toISOString()
                };
            }
        """)
        
        # Detect current condition blindly
        condition = state_model.detect_current_condition(
            target_page.url,
            target_page.title(),
            page_content
        )
        
        print(f"🎯 BLIND CONDITION DETECTION RESULTS:")
        print(f"   📋 Page Type: {condition['page_type']}")
        print(f"   📍 Current Step: {condition['current_step']}")
        print(f"   📊 Progress: {condition['progress']}")
        print(f"   📝 Form Status: {condition['form_status']}")
        print(f"   🎯 Confidence: {condition['confidence']}")
        
        if condition['recommendations']:
            print(f"   💡 Recommendations:")
            for rec in condition['recommendations']:
                print(f"      • {rec}")
        
        if condition['warnings']:
            print(f"   ⚠️  Warnings:")
            for warning in condition['warnings']:
                print(f"      • {warning}")
        
        # Initialize state model with detected condition
        state_model.update_page_state(target_page.url, target_page.title(), page_content)
        
        # Interactive navigation loop
        while True:
            print(f"\n{'='*60}")
            print(f"📄 Current page: {target_page.title()}")
            print(f"🔗 Current URL: {target_page.url}")
            
            # Update state model with current page data
            try:
                page_content = target_page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('*');
                        const tagCounts = {};
                        const navigationElements = [];
                        const formElements = [];
                        const interactiveElements = [];
                        
                        elements.forEach(el => {
                            const tag = el.tagName.toLowerCase();
                            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                            
                            // Navigation elements
                            if (el.id === 'steps-navigation' || el.classList.contains('step') || el.classList.contains('navigation')) {
                                navigationElements.push({
                                    tag: tag,
                                    id: el.id || '',
                                    className: el.className.toString() || '',
                                    text: el.textContent?.trim() || '',
                                    href: el.href || ''
                                });
                            }
                            
                            // Form elements
                            if (['form', 'input', 'textarea', 'select', 'button'].includes(tag)) {
                                formElements.push({
                                    tag: tag,
                                    id: el.id || '',
                                    name: el.name || '',
                                    type: el.type || '',
                                    className: el.className.toString() || '',
                                    value: el.value || '',
                                    placeholder: el.placeholder || ''
                                });
                            }
                            
                            // Interactive elements
                            if (['button', 'a', 'input'].includes(tag) || el.onclick || el.getAttribute('onclick')) {
                                interactiveElements.push({
                                    tag: tag,
                                    id: el.id || '',
                                    className: el.className.toString() || '',
                                    text: el.textContent?.trim() || el.value || '',
                                    href: el.href || '',
                                    onclick: el.onclick ? 'present' : 'none'
                                });
                            }
                        });
                        
                        return {
                            totalElements: elements.length,
                            tagCounts: tagCounts,
                            navigationElements: navigationElements,
                            formElements: formElements,
                            interactiveElements: interactiveElements,
                            url: window.location.href,
                            title: document.title,
                            timestamp: new Date().toISOString()
                        };
                    }
                """)
                
                # Update state model
                page_state = state_model.update_page_state(
                    target_page.url, 
                    target_page.title(), 
                    page_content
                )
                
                # Add comprehensive telemetry to graph on every page visit
                comprehensive_data = {
                    'url': target_page.url,
                    'title': target_page.title(),
                    'timestamp': datetime.now().isoformat(),
                    'page_type': page_state.page_type.value,
                    'current_step': page_state.current_step.text if page_state.current_step else 'unknown',
                    'form_status': page_state.form_status.value,
                    'totalElements': page_content.get('totalElements', 0),
                    'navigationElements': page_content.get('navigationElements', []),
                    'formElements': page_content.get('formElements', []),
                    'interactiveElements': page_content.get('interactiveElements', []),
                    'dom_structure': {
                        'tagCounts': page_content.get('tagCounts', {}),
                        'topClasses': page_content.get('topClasses', []),
                        'topIds': page_content.get('topIds', [])
                    }
                }
                
                page_hash = telemetry_graph.add_page_telemetry(comprehensive_data)
                
                # Capture screenshot for visual comparison
                timestamp = int(time.time())
                url_parts = target_page.url.split('/')
                hackathon_id = next((part for part in url_parts if 'hackathon' in part), 'unknown')
                submission_id = next((part for part in url_parts if part.isdigit()), 'unknown')
                page_title = page_state.page_type.value.replace('_', '-')
                
                screenshot_filename = f"page_{hackathon_id}_{submission_id}_{page_title}_{timestamp}_{page_hash}.png"
                target_page.screenshot(path=screenshot_filename)
                
                # Add screenshot info to telemetry
                comprehensive_data['screenshot'] = screenshot_filename
                comprehensive_data['visual_hash'] = _calculate_image_hash(screenshot_filename)
                
                # Check if we've seen this page before (visual comparison)
                similar_pages = _find_similar_pages(comprehensive_data['visual_hash'], telemetry_graph)
                if similar_pages:
                    print(f"🔍 Similar pages found: {len(similar_pages)} previous visits")
                    for similar in similar_pages[:3]:  # Show top 3 similar
                        print(f"   📸 {similar['timestamp']}: {similar['url']}")
                
                # Show state summary
                print(f"📊 Page Type: {page_state.page_type.value}")
                print(f"📍 Current Step: {page_state.current_step.text if page_state.current_step else 'Unknown'}")
                print(f"📋 Form Status: {page_state.form_status.value}")
                print(f"💾 Telemetry saved: {page_hash}")
                print(f"📸 Screenshot: {screenshot_filename}")
                
            except Exception as e:
                print(f"⚠️  State tracking error: {e}")
            
            # Get visible step navigation links
            step_links = target_page.query_selector_all("#steps-navigation a.step")
            visible_steps = []
            
            print(f"\n🎯 Available Step Navigation:")
            for i, step in enumerate(step_links, 1):
                text = step.text_content().strip()
                classes = step.get_attribute("class") or ""
                href = step.get_attribute("href") or ""
                is_visible = step.is_visible()
                is_enabled = step.is_enabled()
                
                if is_visible and is_enabled:
                    visible_steps.append(step)
                    status = "📍 CURRENT" if "current" in classes else "✅ COMPLETED" if "completed" in classes else "⏳ AVAILABLE"
                    print(f"   {i}. {text} [{classes}] {status}")
                    print(f"      -> {href}")
                else:
                    print(f"   {i}. {text} [{classes}] ❌ HIDDEN/DISABLED")
            
            # Get other navigation options and present as menu items
            other_buttons = target_page.query_selector_all("button, input[type='button'], input[type='submit']")
            other_options = []
            
            print(f"\n🔘 Other Navigation Options:")
            for button in other_buttons:
                text = button.text_content().strip()
                if text and button.is_visible() and button.is_enabled():
                    other_options.append(button)
                    print(f"   • {text} (button)")
            
            # Show menu with numbered options
            print(f"\n🎛️  Navigation Menu:")
            print(f"   1-{len(visible_steps)} - Click step link")
            
            # Add other navigation options as numbered menu items
            start_num = len(visible_steps) + 1
            for i, button in enumerate(other_options):
                text = button.text_content().strip()
                menu_num = start_num + i
                print(f"   {menu_num} - {text}")
            
            print(f"   s - Save & Continue")
            print(f"   a - Analyze page")
            print(f"   e - Explore from Here (comprehensive tree analysis)")
            print(f"   r - Refresh page")
            print(f"   t - Show state summary")
            print(f"   q - Quit")
            
            try:
                max_choice = len(visible_steps) + len(other_options)
                print(f"\n🎯 Choose navigation (1-{max_choice}, s, a, e, r, t, q): ", end="", flush=True)
                choice = input().strip().lower()
                
                if choice == 'q':
                    # Check if we have changes worth saving
                    if telemetry_graph.has_changes():
                        print("\n💾 Session has changes - would you like to save?")
                        save_choice = input("Save session data? (y/n/f for force save): ").strip().lower()
                        
                        if save_choice in ['y', 'yes', 'f', 'force']:
                            _save_session_data(telemetry_graph, state_model, force=(save_choice in ['f', 'force']))
                        else:
                            print("⚠️  Session data not saved")
                    else:
                        print("ℹ️  No changes to save")
                    
                    print("👋 Goodbye!")
                    break
                elif choice == 'a':
                    # Analyze page
                    print(f"\n🔍 Page Analysis:")
                    print(f"   Title: {target_page.title()}")
                    print(f"   URL: {target_page.url}")
                    
                    # Count elements
                    forms = target_page.query_selector_all("form")
                    inputs = target_page.query_selector_all("input, textarea, select")
                    buttons = target_page.query_selector_all("button, input[type='button'], input[type='submit']")
                    
                    print(f"   Forms: {len(forms)}")
                    print(f"   Inputs: {len(inputs)}")
                    print(f"   Buttons: {len(buttons)}")
                    
                    # Take screenshot
                    timestamp = int(time.time())
                    url_parts = target_page.url.split("/")
                    hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
                    submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
                    page_title = target_page.title().replace(" ", "_").replace("/", "_")[:20]
                    
                    filename = f"step_nav_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
                    target_page.screenshot(path=filename)
                    print(f"   📸 Screenshot: {filename}")
                
                elif choice == 'e':
                    # Explore from Here - Comprehensive tree analysis
                    print("🌳 Starting comprehensive exploration...")
                    explore_from_here(target_page)
                    
                    # Add comprehensive telemetry to graph
                    comprehensive_data = target_page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('*');
                            const comprehensiveData = {
                                url: window.location.href,
                                title: document.title,
                                timestamp: new Date().toISOString(),
                                totalElements: elements.length,
                                navigationElements: [],
                                formElements: [],
                                interactiveElements: [],
                                domStructure: {},
                                performanceMetrics: {
                                    loadTime: performance.timing ? 
                                        performance.timing.loadEventEnd - performance.timing.navigationStart : null,
                                    domContentLoaded: performance.timing ?
                                        performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart : null
                                }
                            };
                            
                            // Comprehensive element analysis
                            elements.forEach(el => {
                                const tag = el.tagName.toLowerCase();
                                const className = el.className.toString();
                                const id = el.id || '';
                                const text = el.textContent?.trim() || '';
                                
                                // Navigation elements
                                if (el.id === 'steps-navigation' || el.classList.contains('step') || 
                                    el.classList.contains('navigation') || tag === 'nav') {
                                    comprehensiveData.navigationElements.push({
                                        tag, id, className, text,
                                        href: el.href || '',
                                        isVisible: el.offsetParent !== null,
                                        isEnabled: !el.disabled
                                    });
                                }
                                
                                // Form elements
                                if (['form', 'input', 'textarea', 'select', 'button'].includes(tag)) {
                                    comprehensiveData.formElements.push({
                                        tag, id, className, text,
                                        name: el.name || '',
                                        type: el.type || '',
                                        value: el.value || '',
                                        placeholder: el.placeholder || '',
                                        required: el.required || false,
                                        isVisible: el.offsetParent !== null,
                                        isEnabled: !el.disabled
                                    });
                                }
                                
                                // Interactive elements
                                if (['button', 'a', 'input', 'select', 'textarea'].includes(tag) || 
                                    el.onclick || el.getAttribute('onclick')) {
                                    comprehensiveData.interactiveElements.push({
                                        tag, id, className, text,
                                        href: el.href || '',
                                        onclick: el.onclick ? 'present' : 'none',
                                        isVisible: el.offsetParent !== null,
                                        isEnabled: !el.disabled
                                    });
                                }
                            });
                            
                            // DOM structure analysis
                            comprehensiveData.domStructure = {
                                totalElements: elements.length,
                                tagDistribution: {},
                                classDistribution: {},
                                idDistribution: {}
                            };
                            
                            elements.forEach(el => {
                                const tag = el.tagName.toLowerCase();
                                comprehensiveData.domStructure.tagDistribution[tag] = 
                                    (comprehensiveData.domStructure.tagDistribution[tag] || 0) + 1;
                                
                                if (className && className !== '') {
                                    className.split(' ').forEach(cls => {
                                        if (cls.trim()) {
                                            comprehensiveData.domStructure.classDistribution[cls.trim()] = 
                                                (comprehensiveData.domStructure.classDistribution[cls.trim()] || 0) + 1;
                                        }
                                    });
                                }
                                
                                if (id) {
                                    comprehensiveData.domStructure.idDistribution[id] = 
                                        (comprehensiveData.domStructure.idDistribution[id] || 0) + 1;
                                }
                            });
                            
                            return comprehensiveData;
                        }
                    """)
                    
                    # Add to telemetry graph
                    page_hash = telemetry_graph.add_page_telemetry(comprehensive_data)
                    print(f"💾 Comprehensive telemetry added to graph: {page_hash}")
                    print(f"📊 Elements analyzed: {comprehensive_data['totalElements']}")
                    print(f"🧭 Navigation elements: {len(comprehensive_data['navigationElements'])}")
                    print(f"📋 Form elements: {len(comprehensive_data['formElements'])}")
                    print(f"🎮 Interactive elements: {len(comprehensive_data['interactiveElements'])}")
                
                elif choice == 'r':
                    # Refresh page
                    print(f"🔄 Refreshing page...")
                    target_page.reload(wait_until="networkidle")
                    print(f"✅ Page refreshed! New URL: {target_page.url}")
                elif choice == 't':
                    print(state_model.get_state_summary())
                    recommendations = state_model.get_navigation_recommendations()
                    print(f"\n🎯 Navigation Recommendations:")
                    for action in recommendations.get('next_actions', []):
                        print(f"   • {action}")
                    for warning in recommendations.get('warnings', []):
                        print(f"   ⚠️  {warning}")
                    print(f"\n📊 Progress: {recommendations['progress']['completion_percentage']:.1f}% complete")
                    
                elif choice == 's':
                    # Save & Continue - find save button properly
                    save_button = None
                    save_buttons = target_page.query_selector_all("button, input[type='button'], input[type='submit']")
                    
                    for button in save_buttons:
                        text = button.text_content().strip().lower()
                        if any(word in text for word in ["save", "continue", "submit"]):
                            save_button = button
                            break
                    
                    if save_button:
                        print(f"🔄 Clicking: {save_button.text_content().strip()}")
                        save_button.click()
                        target_page.wait_for_load_state("networkidle")
                        print(f"✅ Action completed! New URL: {target_page.url}")
                    else:
                        print("❌ No save/continue button found")
                
                elif choice.isdigit():
                    choice_num = int(choice)
                    # Check if it's a step link (1 to len(visible_steps))
                    if 1 <= choice_num <= len(visible_steps):
                        # Click step link
                        step_index = choice_num - 1
                        step = visible_steps[step_index]
                        text = step.text_content().strip()
                        href = step.get_attribute("href") or ""
                        
                        print(f"🔄 Clicking: {text}")
                        print(f"   -> {href}")
                        
                        step.click()
                        target_page.wait_for_load_state("networkidle")
                        print(f"✅ Navigation successful! New URL: {target_page.url}")
                    # Check if it's an other navigation option
                    elif len(visible_steps) + 1 <= choice_num <= max_choice:
                        # Click other navigation button
                        button_index = choice_num - len(visible_steps) - 1
                        button = other_options[button_index]
                        text = button.text_content().strip()
                        
                        print(f"🔄 Clicking: {text}")
                        
                        button.click()
                        target_page.wait_for_load_state("networkidle")
                        print(f"✅ Action completed! New URL: {target_page.url}")
                    else:
                        print(f"❌ Invalid choice number: {choice}")
                else:
                    print(f"❌ Invalid choice: {choice}")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    navigate_devpost_steps()
