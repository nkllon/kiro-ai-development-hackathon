#!/usr/bin/env python3
"""
DevPost Submission Form Interrogation
=====================================

Deep analysis of the current DevPost submission to identify gaps and weaknesses.
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def interrogate_form(page):
    """Deep interrogation of the DevPost submission form."""
    print("\n🔍 DEEP FORM INTERROGATION")
    print("=" * 50)
    
    # Get all form elements
    forms = page.query_selector_all("form")
    inputs = page.query_selector_all("input, textarea, select")
    buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
    
    print(f"📊 Form Elements Found:")
    print(f"   Forms: {len(forms)}")
    print(f"   Inputs: {len(inputs)}")
    print(f"   Buttons: {len(buttons)}")
    
    # Analyze each form
    form_data = {}
    for i, form in enumerate(forms, 1):
        print(f"\n📝 FORM {i} ANALYSIS:")
        
        form_info = {
            "id": form.get_attribute("id") or f"form_{i}",
            "action": form.get_attribute("action") or "",
            "method": form.get_attribute("method") or "GET",
            "class": form.get_attribute("class") or "",
            "fields": []
        }
        
        # Get all fields in this form
        fields = form.query_selector_all("input, textarea, select")
        print(f"   Fields in form: {len(fields)}")
        
        for j, field in enumerate(fields, 1):
            try:
                field_info = {
                    "tag": field.evaluate("el => el.tagName").lower(),
                    "type": field.get_attribute("type") or "text",
                    "name": field.get_attribute("name") or "",
                    "id": field.get_attribute("id") or "",
                    "placeholder": field.get_attribute("placeholder") or "",
                    "value": field.get_attribute("value") or "",
                    "required": field.get_attribute("required") is not None,
                    "disabled": field.get_attribute("disabled") is not None,
                    "class": field.get_attribute("class") or ""
                }
                
                # Get current content for text fields
                if field_info["tag"] in ["input", "textarea"]:
                    try:
                        current_value = field.input_value()
                        if current_value:
                            field_info["current_value"] = current_value
                    except:
                        pass
                
                # Get label text
                label_text = "Unlabeled"
                if field_info["id"]:
                    label_elem = page.query_selector(f"label[for='{field_info['id']}']")
                    if label_elem:
                        label_text = label_elem.text_content().strip()
                
                field_info["label"] = label_text
                form_info["fields"].append(field_info)
                
                # Print field details
                status = "✅" if field_info["current_value"] else "❌"
                print(f"      {status} Field {j}: {label_text}")
                print(f"         Type: {field_info['type']}, Name: {field_info['name']}")
                if field_info.get("current_value"):
                    preview = field_info["current_value"][:100] + "..." if len(field_info["current_value"]) > 100 else field_info["current_value"]
                    print(f"         Value: {preview}")
                elif field_info["placeholder"]:
                    print(f"         Placeholder: {field_info['placeholder']}")
                if field_info["required"]:
                    print(f"         ⚠️  REQUIRED FIELD")
                    
            except Exception as e:
                print(f"      ❌ Error analyzing field {j}: {e}")
        
        form_data[f"form_{i}"] = form_info
    
    return form_data


def check_submission_completeness(page):
    """Check how complete the current submission is."""
    print("\n📋 SUBMISSION COMPLETENESS CHECK")
    print("=" * 50)
    
    # Key fields to check for DevPost submissions
    required_fields = [
        ("project_name", ["project name", "title", "name"]),
        ("elevator_pitch", ["elevator pitch", "tagline", "description"]),
        ("description", ["description", "about", "details"]),
        ("built_with", ["built with", "technologies", "tools"]),
        ("try_it_out", ["try it out", "demo", "url"]),
        ("learn_more", ["learn more", "github", "repository"]),
        ("video", ["video", "demo video", "presentation"]),
        ("images", ["images", "screenshots", "media"])
    ]
    
    completeness_score = 0
    total_fields = len(required_fields)
    field_status = {}
    
    for field_type, keywords in required_fields:
        found = False
        value = ""
        
        for keyword in keywords:
            # Look for elements containing this keyword
            elements = page.query_selector_all(f"*:has-text('{keyword}')")
            
            for element in elements:
                # Check if this element is near an input field
                nearby_inputs = element.query_selector_all("input, textarea, select")
                if nearby_inputs:
                    for input_elem in nearby_inputs:
                        try:
                            input_value = input_elem.input_value()
                            if input_value and len(input_value.strip()) > 0:
                                found = True
                                value = input_value
                                break
                        except:
                            pass
                
                if found:
                    break
            
            if found:
                break
        
        field_status[field_type] = {
            "found": found,
            "value": value,
            "keywords_searched": keywords
        }
        
        if found:
            completeness_score += 1
            status = "✅"
            preview = value[:50] + "..." if len(value) > 50 else value
        else:
            status = "❌"
            preview = "EMPTY"
        
        print(f"   {status} {field_type.replace('_', ' ').title()}: {preview}")
    
    completion_percentage = (completeness_score / total_fields) * 100
    print(f"\n📊 COMPLETION SCORE: {completeness_score}/{total_fields} ({completion_percentage:.1f}%)")
    
    if completion_percentage < 50:
        print("🚨 CRITICAL: Submission is severely incomplete!")
    elif completion_percentage < 75:
        print("⚠️  WARNING: Submission needs significant work")
    elif completion_percentage < 90:
        print("📝 GOOD: Submission is mostly complete with minor gaps")
    else:
        print("✅ EXCELLENT: Submission is nearly complete")
    
    return field_status, completion_percentage


def analyze_content_quality(page, field_status):
    """Analyze the quality of content in filled fields."""
    print("\n📝 CONTENT QUALITY ANALYSIS")
    print("=" * 50)
    
    quality_issues = []
    
    for field_type, status in field_status.items():
        if status["found"] and status["value"]:
            value = status["value"]
            
            # Check length
            if len(value.strip()) < 10:
                quality_issues.append(f"{field_type}: Too short ({len(value)} chars)")
            
            # Check for placeholder text
            if any(placeholder in value.lower() for placeholder in ["placeholder", "enter your", "type here"]):
                quality_issues.append(f"{field_type}: Contains placeholder text")
            
            # Check for generic content
            generic_phrases = ["lorem ipsum", "todo", "tbd", "coming soon", "to be determined"]
            if any(phrase in value.lower() for phrase in generic_phrases):
                quality_issues.append(f"{field_type}: Contains generic placeholder content")
            
            # Field-specific quality checks
            if field_type == "project_name":
                if len(value) < 3:
                    quality_issues.append(f"{field_type}: Project name too short")
            
            elif field_type == "elevator_pitch":
                if len(value) < 20:
                    quality_issues.append(f"{field_type}: Elevator pitch too brief")
                if not any(word in value.lower() for word in ["ai", "machine learning", "artificial intelligence"]):
                    quality_issues.append(f"{field_type}: Doesn't mention AI/Kiro focus")
            
            elif field_type == "description":
                if len(value) < 100:
                    quality_issues.append(f"{field_type}: Description too brief")
                if "kiro" not in value.lower():
                    quality_issues.append(f"{field_type}: Doesn't mention Kiro IDE")
    
    if quality_issues:
        print("🚨 QUALITY ISSUES FOUND:")
        for issue in quality_issues:
            print(f"   ❌ {issue}")
    else:
        print("✅ No major quality issues detected")
    
    return quality_issues


def main():
    """Main interrogation function."""
    print("🔍 DEVPOST SUBMISSION FORM INTERROGATION")
    print("=" * 60)
    
    try:
        # Start Playwright
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.new_page()
        
        # Navigate to DevPost
        devpost_url = "https://kiro.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Submissions+open&_gl=1*1b0lbpj*_gcl_au*MTEzNDU0OTI1Mi4xNzU2NDA5NzU1*_ga*MTA2NTYyNjg3OS4xNzU2NDA5NzU1*_ga_0YHJK3Y10M*czE3NTc5NjE1MTAkbzMwJGcwJHQxNzU3OTYxNTEwJGo2MCRsMCRoMA.."
        
        print(f"🌐 Navigating to DevPost...")
        page.goto(devpost_url)
        page.wait_for_load_state("networkidle", timeout=30000)
        
        print(f"📄 Page loaded: {page.title()}")
        
        # Take screenshot
        timestamp = int(time.time())
        screenshot_path = f"submission_analysis_{timestamp}.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Interrogate forms
        form_data = interrogate_form(page)
        
        # Check completeness
        field_status, completion_percentage = check_submission_completeness(page)
        
        # Analyze content quality
        quality_issues = analyze_content_quality(page, field_status)
        
        # Save detailed report
        report = {
            "timestamp": time.time(),
            "url": page.url,
            "title": page.title(),
            "completion_percentage": completion_percentage,
            "form_data": form_data,
            "field_status": field_status,
            "quality_issues": quality_issues,
            "screenshot_path": screenshot_path
        }
        
        report_path = f"submission_interrogation_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        # Summary
        print(f"\n🎯 INTERROGATION SUMMARY")
        print("=" * 50)
        print(f"Completion: {completion_percentage:.1f}%")
        print(f"Quality Issues: {len(quality_issues)}")
        print(f"Forms Found: {len(form_data)}")
        
        if completion_percentage < 75:
            print("\n🚨 RECOMMENDATION: Focus on filling missing required fields first")
        if quality_issues:
            print("📝 RECOMMENDATION: Address content quality issues")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
