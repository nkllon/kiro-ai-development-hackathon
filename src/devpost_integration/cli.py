#!/usr/bin/env python3
"""
DevPost Integration CLI
=======================

Command line interface for DevPost integration.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide CLI interface for DevPost integration
"""

import argparse
import json
import sys
from typing import Dict, Any, List
from datetime import datetime
from .reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
)


class Unknown:
    """Unknown class for backward compatibility."""

    pass


class DevPostCLI(ReflectiveModule):
    """DevPost Integration CLI class."""

    def __init__(self):
        super().__init__()
        self.module_id = "devpost_cli"
        self.capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
        self.dependencies = []

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "interface_type": self.__class__.__name__,
            "version": "1.0.0",
            "dependencies": self.dependencies,
            "capabilities": [cap.value for cap in self.capabilities],
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return self.capabilities

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=100.0,
            issues=[],
            last_check=datetime.now(),
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        return {
            "success": True,
            "degraded_capabilities": [],
            "remaining_capabilities": [cap.value for cap in self.capabilities],
        }

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="DevPost Integration CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument("--version", action="version", version="1.0.0")

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Browser automation commands
        extract_parser = subparsers.add_parser(
            "extract", help="Extract data from DevPost"
        )
        extract_parser.add_argument("url", help="DevPost URL to extract from")
        extract_parser.add_argument(
            "--type",
            choices=["hackathon", "project"],
            default="hackathon",
            help="Type of data to extract",
        )
        extract_parser.set_defaults(func=self.extract_command)

        search_parser = subparsers.add_parser("search", help="Search for hackathons")
        search_parser.add_argument("query", help="Search query")
        search_parser.add_argument(
            "--limit", type=int, default=10, help="Maximum number of results"
        )
        search_parser.set_defaults(func=self.search_command)

        # Form interrogation commands
        interrogate_parser = subparsers.add_parser(
            "interrogate", help="Interrogate DevPost submission form"
        )
        interrogate_parser.add_argument("url", help="DevPost submission URL")
        interrogate_parser.add_argument(
            "--output", help="Output file for form model (JSON)"
        )
        interrogate_parser.add_argument(
            "--headless", action="store_true", help="Run in headless mode"
        )
        interrogate_parser.set_defaults(func=self.interrogate_command)

        # Status command
        status_parser = subparsers.add_parser("status", help="Show module status")
        status_parser.set_defaults(func=self.status_command)

        return parser

    def extract_command(self, args) -> Dict[str, Any]:
        """Extract data from DevPost using browser automation."""
        from .hybrid_integration import DevPostHybridIntegration

        try:
            with DevPostHybridIntegration() as integration:
                if args.type == "hackathon":
                    result = integration.extract_hackathon_data_sync(args.url)
                else:
                    result = integration.extract_project_data_sync(args.url)

                if result.success:
                    return {
                        "success": True,
                        "data": result.data,
                        "method_used": result.method_used,
                    }
                else:
                    return {"success": False, "error": result.error}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_command(self, args) -> Dict[str, Any]:
        """Search for hackathons using browser automation."""
        from .hybrid_integration import DevPostHybridIntegration

        try:
            with DevPostHybridIntegration() as integration:
                hackathons = integration.search_hackathons(
                    query=args.query, limit=args.limit
                )
                return {
                    "success": True,
                    "hackathons": hackathons,
                    "count": len(hackathons),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def interrogate_command(self, args) -> Dict[str, Any]:
        """Interrogate DevPost submission form to build a complete model."""
        from .form_interrogation import DevPostFormInterrogation
        import json
        from datetime import datetime

        try:
            print(f"🎯 Interrogating DevPost submission form at: {args.url}")
            print("👤 Please log in to DevPost in the browser window that opens...")
            print("📝 Navigate to your submission page and press Enter when ready...")

            # Wait for user to authenticate and navigate
            input(
                "Press Enter when you're on the submission page and ready to interrogate..."
            )

            # Interrogate the form
            with DevPostFormInterrogation(headless=args.headless) as interrogation:
                model = interrogation.interrogate_submission_form_sync(args.url)

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
                            print(
                                f"      Validation: {', '.join(field.validation_rules)}"
                            )
                        if field.help_text:
                            print(
                                f"      Help: {field.help_text[:50]}{'...' if len(field.help_text) > 50 else ''}"
                            )
                        print()

                # Prepare model data for JSON serialization
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

                # Save model to file
                output_file = (
                    args.output
                    or f"devpost_submission_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(output_file, "w") as f:
                    json.dump(model_data, f, indent=2)

                print(f"💾 Model saved to: {output_file}")

                return {
                    "success": True,
                    "model": model_data,
                    "output_file": output_file,
                    "sections_count": len(model.sections),
                    "fields_count": len(model.all_fields),
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def status_command(self, args) -> Dict[str, Any]:
        """Status command handler."""
        return {
            "module_id": self.module_id,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
        }


def main() -> None:
    """Main CLI entry point."""
    cli = DevPostCLI()
    parser = cli.create_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        result = args.func(args)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
