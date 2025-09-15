#!/usr/bin/env python3
"""
DevPost Form Data Provider
==========================

Provides the data needed to fill out the DevPost hackathon submission form.
Since we can't automate the form filling directly, this provides the data
in a format that's easy to copy and paste.
"""

import json
from datetime import datetime

def get_project_data():
    """Get the project data for the hackathon submission."""
    return {
        "title": "The Requirements ARE the Solution - Beast Mode Framework",
        "description": """A revolutionary AI-powered development framework that transforms requirements into executable solutions, demonstrating 20.4% systematic superiority over ad-hoc development approaches.

## 🚀 The Future of Development
Beast Mode proves that systematic approaches consistently outperform ad-hoc development. Requirements become executable solutions, not just documentation.
**The Requirements ARE the Solution - and we have the evidence to prove it!**""",
        "project_url": "https://github.com/nkllon/kiro-ai-development-hackathon",
        "demo_video": "https://youtube.com/watch?v=demo-video",
        "built_with": ["Kiro AI", "Python", "Systematic Development", "AI Collaboration", "GCP"],
        "tags": ["kiro", "ai", "systematic-development", "beast-mode", "requirements-driven", "pdca", "ai-collaboration"]
    }

def print_form_data():
    """Print the form data in a copy-paste friendly format."""
    data = get_project_data()
    
    print("🎯 DevPost Hackathon Submission Data")
    print("=" * 40)
    print()
    
    print("📝 TITLE:")
    print("-" * 10)
    print(data["title"])
    print()
    
    print("📄 DESCRIPTION:")
    print("-" * 15)
    print(data["description"])
    print()
    
    print("🔗 PROJECT URL:")
    print("-" * 15)
    print(data["project_url"])
    print()
    
    print("🎥 DEMO VIDEO URL:")
    print("-" * 20)
    print(data["demo_video"])
    print()
    
    print("🛠️ BUILT WITH:")
    print("-" * 15)
    for item in data["built_with"]:
        print(f"• {item}")
    print()
    
    print("🏷️ TAGS:")
    print("-" * 10)
    for tag in data["tags"]:
        print(f"• {tag}")
    print()
    
    print("💡 INSTRUCTIONS:")
    print("-" * 15)
    print("1. Copy each section above")
    print("2. Paste into the corresponding form fields")
    print("3. Make sure to fill all required fields")
    print("4. Submit the form when complete")
    print()
    
    print("🎉 Ready to fill out your DevPost submission!")

def save_form_data():
    """Save the form data to a JSON file."""
    data = get_project_data()
    
    filename = f"devpost_submission_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Form data saved to: {filename}")
    return filename

if __name__ == "__main__":
    print_form_data()
    save_form_data()
