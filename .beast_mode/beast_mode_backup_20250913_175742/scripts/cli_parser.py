#!/usr/bin/env python3
"""
CLI parser for model CRUD operations.
Single responsibility: Argument parsing and validation.
"""

import argparse
import json
from typing import Dict, Any


class ModelCrudArgumentParser:
    """Parser for model CRUD CLI arguments."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all supported actions."""
        parser = argparse.ArgumentParser(
            description="Model CRUD operations via Model Registry",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # List all domains
  %(prog)s list-domains
  
  # List requirements for a specific domain
  %(prog)s list-domain-requirements --domain model_management
  
  # Add item to project model
  %(prog)s add-item --model-name project --id new_requirement --description "New requirement"
  
  # Search requirements across all domains
  %(prog)s list-domain-requirements --search "validation"
            """,
        )

        # Main action argument
        parser.add_argument(
            "action",
            choices=[
                "read",
                "register-model",
                "list-models",
                "unregister-model",
                "get-model-info",
                "list-domains",
                "list-domain-requirements",
                "add-item",
                "update-section",
                "remove-item",
                "add-section",
                "remove-section",
                "create-backup",
                "list-backups",
                "restore-backup",
                "validate",
            ],
            help="Action to perform",
        )

        # Model registry parameters (for registration only)
        parser.add_argument("--model-name", help="Model name")
        parser.add_argument(
            "--implementation",
            choices=[
                "json_model_manager",
                "neo4j_model_manager",
                "ontology_model_manager",
                "project_model_manager",
            ],
            help="Implementation name (for registration only)",
        )
        parser.add_argument("--config", help="JSON configuration (for registration only)")

        # Model CRUD Parameters (business operations - NO auth/config needed)
        parser.add_argument("--id", help="Item ID")
        parser.add_argument("--title", help="Item title")
        parser.add_argument("--description", help="Item description")
        parser.add_argument("--priority", help="Priority level")
        parser.add_argument("--collection", help="Collection name")
        parser.add_argument("--section", help="Section name")
        parser.add_argument("--updates", help="JSON updates")
        parser.add_argument("--backup-file", help="Backup file path")

        # Domain operation parameters
        parser.add_argument("--domain", help="Domain name for list-domain-requirements")
        parser.add_argument("--search", help="Search term for filtering requirements")
        parser.add_argument("--category", help="Category filter (demo_core, demo_tools, etc.)")
        parser.add_argument(
            "--format",
            choices=["text", "json", "csv"],
            default="text",
            help="Output format",
        )

        return parser

    def parse_args(self) -> argparse.Namespace:
        """Parse command line arguments."""
        return self.parser.parse_args()

    def validate_args(self, args: argparse.Namespace) -> tuple[bool, str]:
        """Validate arguments based on action type."""

        # Model registry operations
        if args.action == "register-model":
            if not all([args.model_name, args.implementation]):
                return (
                    False,
                    "--model-name and --implementation required for register-model",
                )
            if args.config:
                try:
                    json.loads(args.config)
                except json.JSONDecodeError:
                    return False, "Invalid --config JSON"

        elif args.action == "unregister-model":
            if not args.model_name:
                return False, "--model-name required for unregister-model"

        elif args.action == "get-model-info":
            if not args.model_name:
                return False, "--model-name required for get-model-info"

        # Business CRUD operations
        elif args.action in [
            "add-item",
            "update-section",
            "remove-item",
            "add-section",
            "remove-section",
            "create-backup",
            "list-backups",
            "restore-backup",
            "validate",
        ]:
            if not args.model_name:
                return False, f"--model-name required for {args.action}"

            # Specific validations for each action
            if args.action == "add-item":
                if not all([args.id, args.description]):
                    return False, "--id and --description required for add-item"

            elif args.action == "update-section":
                if not all([args.section, args.updates]):
                    return False, "--section and --updates required for update-section"
                try:
                    json.loads(args.updates)
                except json.JSONDecodeError:
                    return False, "Invalid --updates JSON"

            elif args.action == "remove-item":
                if not args.id:
                    return False, "--id required for remove-item"

            elif args.action == "add-section":
                if not all([args.section, args.updates]):
                    return False, "--section and --updates required for add-section"
                try:
                    json.loads(args.updates)
                except json.JSONDecodeError:
                    return False, "Invalid --updates JSON"

            elif args.action == "remove-section":
                if not args.section:
                    return False, "--section required for remove-section"

            elif args.action == "restore-backup":
                if not args.backup_file:
                    return False, "--backup-file required for restore-backup"

        return True, ""


def create_parser() -> ModelCrudArgumentParser:
    """Factory function to create parser instance."""
    return ModelCrudArgumentParser()
