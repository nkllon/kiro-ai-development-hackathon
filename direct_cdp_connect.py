#!/usr/bin/env python3
"""
Direct CDP Connect
=================

Connect directly to the DevPost page using Chrome DevTools Protocol.
This bypasses Playwright's CDP connection issues.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Direct CDP connection to DevPost page
"""

import sys
import json
import time
import requests
import websocket
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def get_devpost_page_info():
    """Get the DevPost page info from the debugging port."""
    try:
        response = requests.get("http://localhost:9222/json")
        pages = response.json()
        
        # Find the DevPost page
        for page in pages:
            if "devpost.com" in page["url"] and "submission" in page["url"]:
                return page
        
        # If no DevPost page found, return the first page
        if pages:
            return pages[0]
        
        return None
    except Exception as e:
        print(f"❌ Failed to get page info: {e}")
        return None

def send_cdp_command(ws, method, params=None):
    """Send a CDP command and return the response."""
    command = {
        "id": int(time.time() * 1000),
        "method": method,
        "params": params or {}
    }
    
    ws.send(json.dumps(command))
    response = ws.recv()
    return json.loads(response)

def main():
    """Connect to the DevPost page using direct CDP."""
    print("🔌 Direct CDP Connect to DevPost Page")
    print("=" * 50)
    
    # Get page info
    page_info = get_devpost_page_info()
    if not page_info:
        print("❌ No pages found!")
        return
    
    print(f"📄 Found page: {page_info['title']}")
    print(f"🔗 URL: {page_info['url']}")
    print(f"🆔 ID: {page_info['id']}")
    print(f"🔌 WebSocket: {page_info['webSocketDebuggerUrl']}")
    
    try:
        # Connect to the page via WebSocket
        print("🔍 Connecting to page via WebSocket...")
        ws = websocket.WebSocket()
        ws.connect(page_info['webSocketDebuggerUrl'])
        print("✅ Connected to page!")
        
        # Enable runtime and DOM
        print("🔧 Enabling runtime and DOM...")
        send_cdp_command(ws, "Runtime.enable")
        send_cdp_command(ws, "DOM.enable")
        send_cdp_command(ws, "Page.enable")
        print("✅ Runtime and DOM enabled!")
        
        # Get page title and URL
        print("📄 Getting page info...")
        title_result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": "document.title"
        })
        url_result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": "window.location.href"
        })
        
        title = title_result.get("result", {}).get("value", "Unknown")
        url = url_result.get("result", {}).get("value", "Unknown")
        
        print(f"📄 Title: {title}")
        print(f"🔗 URL: {url}")
        
        # Count elements
        print("📊 Counting elements...")
        
        # Count forms
        forms_result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": "document.querySelectorAll('form').length"
        })
        form_count = forms_result.get("result", {}).get("value", 0)
        
        # Count buttons
        buttons_result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": "document.querySelectorAll('button, input[type=\"button\"], input[type=\"submit\"]').length"
        })
        button_count = buttons_result.get("result", {}).get("value", 0)
        
        # Count inputs
        inputs_result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": "document.querySelectorAll('input, textarea, select').length"
        })
        input_count = inputs_result.get("result", {}).get("value", 0)
        
        # Count links
        links_result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": "document.querySelectorAll('a').length"
        })
        link_count = links_result.get("result", {}).get("value", 0)
        
        # Count images
        images_result = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": "document.querySelectorAll('img').length"
        })
        image_count = images_result.get("result", {}).get("value", 0)
        
        print(f"\n📊 Elements found:")
        print(f"   Forms: {form_count}")
        print(f"   Buttons: {button_count}")
        print(f"   Inputs: {input_count}")
        print(f"   Links: {link_count}")
        print(f"   Images: {image_count}")
        
        # Analyze forms
        if form_count > 0:
            print(f"\n📝 Form Analysis:")
            
            # Get form details
            forms_info = send_cdp_command(ws, "Runtime.evaluate", {
                "expression": """
                Array.from(document.querySelectorAll('form')).map((form, index) => ({
                    index: index + 1,
                    id: form.id || 'form_' + (index + 1),
                    className: form.className || '',
                    action: form.action || '',
                    method: form.method || 'get',
                    fieldCount: form.querySelectorAll('input, textarea, select').length
                }))
                """
            })
            
            forms_data = forms_info.get("result", {}).get("value", [])
            for form in forms_data:
                print(f"   Form {form['index']}: {form['id']}")
                print(f"      Class: {form['className']}")
                print(f"      Action: {form['action']}")
                print(f"      Method: {form['method']}")
                print(f"      Fields: {form['fieldCount']}")
                
                # Get field details for this form
                if form['fieldCount'] > 0:
                    fields_info = send_cdp_command(ws, "Runtime.evaluate", {
                        "expression": f"""
                        Array.from(document.querySelectorAll('form')[{form['index']-1}].querySelectorAll('input, textarea, select')).slice(0, 10).map((field, index) => {{
                            const label = field.id ? document.querySelector('label[for=\"' + field.id + '\"]') : null;
                            return {{
                                index: index + 1,
                                type: field.type || field.tagName.toLowerCase(),
                                name: field.name || '',
                                id: field.id || '',
                                label: label ? label.textContent.trim() : 'Unlabeled',
                                placeholder: field.placeholder || '',
                                value: field.value || '',
                                required: field.hasAttribute('required')
                            }};
                        }})
                        """
                    })
                    
                    fields_data = fields_info.get("result", {}).get("value", [])
                    for field in fields_data:
                        print(f"      Field {field['index']}: {field['label']} ({field['type']})")
                        if field['name']:
                            print(f"         Name: {field['name']}")
                        if field['placeholder']:
                            print(f"         Placeholder: {field['placeholder']}")
                        if field['value']:
                            print(f"         Value: {field['value'][:50]}...")
                        if field['required']:
                            print(f"         Required: Yes")
        
        # Analyze buttons
        if button_count > 0:
            print(f"\n🔘 Button Analysis:")
            
            # Get button details
            buttons_info = send_cdp_command(ws, "Runtime.evaluate", {
                "expression": """
                Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).slice(0, 15).map((button, index) => ({
                    index: index + 1,
                    text: button.textContent.trim(),
                    type: button.type || 'button',
                    className: button.className || '',
                    visible: button.offsetParent !== null,
                    enabled: !button.disabled
                }))
                """
            })
            
            buttons_data = buttons_info.get("result", {}).get("value", [])
            for button in buttons_data:
                if button['text'] and len(button['text']) < 100:
                    status = "✅" if button['visible'] and button['enabled'] else "❌"
                    print(f"   {status} {button['text']} (type: {button['type']})")
                    if button['className']:
                        print(f"      Classes: {button['className']}")
        
        # Look for navigation elements
        print(f"\n🧭 Navigation Analysis:")
        
        # Find navigation buttons
        nav_buttons_info = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": """
            Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).filter(button => {
                const text = button.textContent.trim().toLowerCase();
                const navKeywords = ['next', 'continue', 'back', 'previous', 'submit', 'save', 'finish', 'complete', 'go', 'click', 'start', 'begin'];
                return navKeywords.some(keyword => text.includes(keyword));
            }).map((button, index) => ({
                index: index + 1,
                text: button.textContent.trim(),
                type: button.type || 'button',
                visible: button.offsetParent !== null,
                enabled: !button.disabled
            }))
            """
        })
        
        nav_buttons_data = nav_buttons_info.get("result", {}).get("value", [])
        if nav_buttons_data:
            print(f"   Found {len(nav_buttons_data)} navigation buttons:")
            for nav in nav_buttons_data:
                status = "✅" if nav['visible'] and nav['enabled'] else "❌"
                print(f"      {status} {nav['text']} ({nav['type']})")
        else:
            print("   No obvious navigation buttons found")
        
        # Take screenshot
        print(f"\n📸 Taking screenshot...")
        try:
            screenshot_result = send_cdp_command(ws, "Page.captureScreenshot", {
                "format": "png"
            })
            
            if "result" in screenshot_result and "data" in screenshot_result["result"]:
                screenshot_data = screenshot_result["result"]["data"]
                
                # Save screenshot
                timestamp = int(time.time())
                url_parts = url.split("/")
                hackathon_id = url_parts[-3] if len(url_parts) > 3 else "unknown"
                submission_id = url_parts[-2] if len(url_parts) > 2 else "unknown"
                page_title = title.replace(" ", "_").replace("/", "_")[:20]
                
                filename = f"cdp_analysis_{hackathon_id}_{submission_id}_{page_title}_{timestamp}.png"
                
                import base64
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(screenshot_data))
                
                print(f"📸 Screenshot: {filename}")
            else:
                print("❌ Screenshot failed")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
        
        # Interactive mode
        print(f"\n🎮 Interactive Mode")
        print("Commands: analyze, screenshot, navigate, quit")
        
        while True:
            try:
                command = input("🔧 Command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "analyze":
                    # Re-analyze
                    forms_result = send_cdp_command(ws, "Runtime.evaluate", {
                        "expression": "document.querySelectorAll('form').length"
                    })
                    buttons_result = send_cdp_command(ws, "Runtime.evaluate", {
                        "expression": "document.querySelectorAll('button, input[type=\"button\"], input[type=\"submit\"]').length"
                    })
                    form_count = forms_result.get("result", {}).get("value", 0)
                    button_count = buttons_result.get("result", {}).get("value", 0)
                    print(f"📊 Current state: {form_count} forms, {button_count} buttons")
                elif command == "screenshot":
                    try:
                        screenshot_result = send_cdp_command(ws, "Page.captureScreenshot", {
                            "format": "png"
                        })
                        
                        if "result" in screenshot_result and "data" in screenshot_result["result"]:
                            screenshot_data = screenshot_result["result"]["data"]
                            timestamp = int(time.time())
                            filename = f"interactive_screenshot_{timestamp}.png"
                            
                            import base64
                            with open(filename, "wb") as f:
                                f.write(base64.b64decode(screenshot_data))
                            
                            print(f"📸 Screenshot: {filename}")
                        else:
                            print("❌ Screenshot failed")
                    except Exception as e:
                        print(f"❌ Screenshot failed: {e}")
                elif command == "navigate":
                    if nav_buttons_data:
                        print("🧭 Available navigation buttons:")
                        for i, nav in enumerate(nav_buttons_data, 1):
                            print(f"   {i}. {nav['text']}")
                        
                        try:
                            choice = int(input("Choose button (number): ")) - 1
                            if 0 <= choice < len(nav_buttons_data):
                                print(f"🔄 Clicking: {nav_buttons_data[choice]['text']}")
                                
                                # Click the button
                                click_result = send_cdp_command(ws, "Runtime.evaluate", {
                                    "expression": f"""
                                    document.querySelectorAll('button, input[type="button"], input[type="submit"]')[{choice}].click()
                                    """
                                })
                                
                                # Wait a moment for navigation
                                time.sleep(2)
                                
                                # Re-analyze
                                print("🔄 Page changed, re-analyzing...")
                                forms_result = send_cdp_command(ws, "Runtime.evaluate", {
                                    "expression": "document.querySelectorAll('form').length"
                                })
                                buttons_result = send_cdp_command(ws, "Runtime.evaluate", {
                                    "expression": "document.querySelectorAll('button, input[type=\"button\"], input[type=\"submit\"]').length"
                                })
                                form_count = forms_result.get("result", {}).get("value", 0)
                                button_count = buttons_result.get("result", {}).get("value", 0)
                                
                                # Get new URL and title
                                url_result = send_cdp_command(ws, "Runtime.evaluate", {
                                    "expression": "window.location.href"
                                })
                                title_result = send_cdp_command(ws, "Runtime.evaluate", {
                                    "expression": "document.title"
                                })
                                
                                new_url = url_result.get("result", {}).get("value", "Unknown")
                                new_title = title_result.get("result", {}).get("value", "Unknown")
                                
                                print(f"📊 New state: {form_count} forms, {button_count} buttons")
                                print(f"📄 New URL: {new_url}")
                                print(f"📄 New title: {new_title}")
                            else:
                                print("❌ Invalid choice")
                        except ValueError:
                            print("❌ Invalid input")
                    else:
                        print("❌ No navigation buttons available")
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Close WebSocket
        ws.close()
        print("🔌 Connection closed")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

