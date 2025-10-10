#!/usr/bin/env python3
"""
Test Form Interrogation
=======================

Test script for DevPost form interrogation with human-in-the-middle authentication.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test form interrogation with authenticated DevPost submission pages
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from devpost_integration.form_interrogation import DevPostFormInterrogation

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_form_interrogation_sync(submission_url: str):
    """Test sync form interrogation."""
    print("🧪 Testing Sync Form Interrogation")
    print("=" * 50)

    try:
        with DevPostFormInterrogation(headless=False) as interrogation:
            print(f"🌐 Interrogating form at: {submission_url}")
            print("👤 Please log in to DevPost in the browser window that opens...")
            print("📝 Navigate to your submission page and press Enter when ready...")

            # Wait for user to authenticate and navigate
            input(
                "Press Enter when you're on the submission page and ready to interrogate..."
            )

            # Interrogate the form
            model = interrogation.interrogate_submission_form_sync(submission_url)

            # Display results
            print("\n✅ Form Interrogation Complete!")
            print("=" * 50)
            print(f"🏆 Hackathon: {model.hackathon_title}")
            print(f"🆔 Hackathon ID: {model.hackathon_id}")
            print(f"🔗 Submission URL: {model.submission_url}")
            print(f"📋 Sections: {len(model.sections)}")
            print(f"📝 Total Fields: {len(model.all_fields)}")

            # Display sections and fields
            for i, section in enumerate(model.sections, 1):
                print(f"\n📋 Section {i}: {section.title}")
                print(f"   Description: {section.description}")
                print(f"   Fields: {len(section.fields)}")

                for j, field in enumerate(section.fields, 1):
                    print(f"   {j}. {field.label} ({field.field_type})")
                    print(f"      Name: {field.name}")
                    print(f"      Required: {field.required}")
                    if field.current_value:
                        print(f"      Current Value: {field.current_value}")
                    if field.placeholder:
                        print(f"      Placeholder: {field.placeholder}")
                    if field.options:
                        print(
                            f"      Options: {', '.join(field.options[:3])}{'...' if len(field.options) > 3 else ''}"
                        )
                    if field.validation_rules:
                        print(f"      Validation: {', '.join(field.validation_rules)}")
                    if field.help_text:
                        print(
                            f"      Help: {field.help_text[:50]}{'...' if len(field.help_text) > 50 else ''}"
                        )
                    print()

            # Save model to file
            model_file = f"devpost_submission_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            model_data = {
                "hackathon_id": model.hackathon_id,
                "hackathon_title": model.hackathon_title,
                "submission_url": model.submission_url,
                "sections": [
                    {
                        "name": section.name,
                        "title": section.title,
                        "description": section.description,
                        "order": section.order,
                        "required": section.required,
                        "fields": [
                            {
                                "name": field.name,
                                "field_type": field.field_type,
                                "label": field.label,
                                "placeholder": field.placeholder,
                                "required": field.required,
                                "current_value": field.current_value,
                                "options": field.options,
                                "validation_rules": field.validation_rules,
                                "help_text": field.help_text,
                                "section": field.section,
                            }
                            for field in section.fields
                        ],
                    }
                    for section in model.sections
                ],
                "all_fields": [
                    {
                        "name": field.name,
                        "field_type": field.field_type,
                        "label": field.label,
                        "placeholder": field.placeholder,
                        "required": field.required,
                        "current_value": field.current_value,
                        "options": field.options,
                        "validation_rules": field.validation_rules,
                        "help_text": field.help_text,
                        "section": field.section,
                    }
                    for field in model.all_fields
                ],
                "form_metadata": model.form_metadata,
                "extracted_at": model.extracted_at.isoformat(),
            }

            with open(model_file, "w") as f:
                json.dump(model_data, f, indent=2)

            print(f"💾 Model saved to: {model_file}")

            return model

    except Exception as e:
        print(f"❌ Form interrogation failed: {e}")
        return None


async def test_form_interrogation_async(submission_url: str):
    """Test async form interrogation."""
    print("🧪 Testing Async Form Interrogation")
    print("=" * 50)

    try:
        async with DevPostFormInterrogation(headless=False) as interrogation:
            print(f"🌐 Interrogating form at: {submission_url}")
            print("👤 Please log in to DevPost in the browser window that opens...")
            print("📝 Navigate to your submission page and press Enter when ready...")

            # Wait for user to authenticate and navigate
            input(
                "Press Enter when you're on the submission page and ready to interrogate..."
            )

            # Interrogate the form
            model = await interrogation.interrogate_submission_form_async(
                submission_url
            )

            # Display results
            print("\n✅ Form Interrogation Complete!")
            print("=" * 50)
            print(f"🏆 Hackathon: {model.hackathon_title}")
            print(f"🆔 Hackathon ID: {model.hackathon_id}")
            print(f"🔗 Submission URL: {model.submission_url}")
            print(f"📋 Sections: {len(model.sections)}")
            print(f"📝 Total Fields: {len(model.all_fields)}")

            return model

    except Exception as e:
        print(f"❌ Form interrogation failed: {e}")
        return None


def main():
    """Main test function."""
    print("🎯 DevPost Form Interrogation Test")
    print("=" * 60)
    print(
        "This test will help you build a complete model of your DevPost submission form."
    )
    print("You'll need to authenticate with DevPost in the browser window that opens.")
    print()

    # Get submission URL from user
    submission_url = input("Enter your DevPost submission URL: ").strip()

    if not submission_url:
        print("❌ No URL provided. Exiting.")
        return

    if not submission_url.startswith("http"):
        submission_url = "https://" + submission_url

    print(f"\n🌐 Will interrogate: {submission_url}")
    print()

    # Ask user which mode to use
    mode = input("Choose mode (sync/async) [sync]: ").strip().lower() or "sync"

    if mode == "async":
        print("\n🚀 Starting async form interrogation...")
        model = asyncio.run(test_form_interrogation_async(submission_url))
    else:
        print("\n🚀 Starting sync form interrogation...")
        model = test_form_interrogation_sync(submission_url)

    if model:
        print("\n🎉 Form interrogation successful!")
        print("You now have a complete model of your DevPost submission form.")
        print("This model can be used to:")
        print("  • Understand all required fields")
        print("  • See current values you've already filled")
        print("  • Generate automated form filling")
        print("  • Validate your submission before submitting")
    else:
        print("\n❌ Form interrogation failed.")
        print("Please check the URL and try again.")


if __name__ == "__main__":
    main()
