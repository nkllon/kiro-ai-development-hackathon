#!/usr/bin/env python3
"""
Rule Firing Identifier - Identifies which Cursor rules are firing

This script analyzes the project model and identifies which rules should be
applying to different file types and operations, with emoji prefixes for
easy identification.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class RuleFiringIdentifier:
    """Identifies which Cursor rules are firing based on project model"""

    def __init__(self, project_model_path: str = "project_model_registry.json"):
        """Initialize the rule firing identifier"""
        self.project_model_path = Path(project_model_path)
        self.project_model = self._load_project_model()
        self.cursor_rules = self._extract_cursor_rules()

    def _load_project_model(self) -> dict[str, Any]:
        """Load the project model registry"""
        try:
            with open(self.project_model_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load project model: {e}")
            return {}

    def _extract_cursor_rules(self) -> dict[str, Any]:
        """Extract cursor rules configuration from project model"""
        if "domain_architecture" in self.project_model:
            for section_name, section in self.project_model["domain_architecture"].items():
                if section_name == "cursor_rules":
                    return section
        return {}

    def get_rule_emoji(self, rule_name: str) -> str:
        """Get the emoji prefix for a rule"""
        if "emoji_prefixes" in self.cursor_rules:
            return self.cursor_rules["emoji_prefixes"].get(rule_name, "📋")
        return "📋"

    def identify_firing_rules(self, file_path: str, operation: str = None) -> list[dict[str, Any]]:
        """Identify which rules should be firing for a given file and operation"""
        firing_rules = []

        # Check each rule domain
        for rule_name in self.cursor_rules.get("domains", []):
            rule_config = self._get_rule_config(rule_name)
            if rule_config and self._should_rule_fire(rule_name, rule_config, file_path, operation):
                emoji = self.get_rule_emoji(rule_name)
                firing_rules.append(
                    {
                        "rule_name": rule_name,
                        "emoji": emoji,
                        "description": rule_config.get("description", ""),
                        "reason": self._get_firing_reason(rule_name, file_path, operation),
                    }
                )

        return firing_rules

    def _get_rule_config(self, rule_name: str) -> Optional[dict[str, Any]]:
        """Get configuration for a specific rule"""
        # This would need to parse the actual .mdc files
        # For now, return basic info
        return {
            "description": f"Rule for {rule_name}",
            "alwaysApply": False,
            "globs": "*.py,*.md,*.yaml",
        }

    def _should_rule_fire(
        self,
        rule_name: str,
        rule_config: dict[str, Any],
        file_path: str,
        operation: str = None,
    ) -> bool:
        """Determine if a rule should fire for the given file and operation"""

        # Always apply rules fire regardless of file
        if rule_config.get("alwaysApply", False):
            return True

        # Check glob patterns
        globs = rule_config.get("globs", "")
        if globs and self._file_matches_globs(file_path, globs):
            return True

        # Check operation-specific rules
        if operation:
            if self._operation_matches_rule(rule_name, operation):
                return True

        return False

    def _file_matches_globs(self, file_path: str, globs: str) -> bool:
        """Check if file matches glob patterns"""
        if not globs:
            return False

        # Simple glob matching (could be enhanced with proper glob library)
        glob_patterns = globs.split(",")
        for pattern in glob_patterns:
            pattern = pattern.strip()
            if pattern.startswith("**/"):
                # Recursive pattern
                if file_path.endswith(pattern[3:]):
                    return True
            elif pattern.startswith("*"):
                # Wildcard pattern
                if file_path.endswith(pattern[1:]):
                    return True
            elif pattern in file_path:
                return True

        return False

    def _operation_matches_rule(self, rule_name: str, operation: str) -> bool:
        """Check if operation matches rule purpose"""
        operation_lower = operation.lower()

        # Map operations to rules
        operation_rule_mapping = {
            "git": ["make_first_enforcement", "pr_procedure_enforcement"],
            "security": ["security"],
            "linting": ["python_quality_enforcement", "intelligent_linter_prevention"],
            "formatting": ["deterministic_editing", "python_quality_enforcement"],
            "package": ["package_management_uv"],
            "testing": ["ghostbusters", "call_more_ghostbusters"],
            "model": ["model_first_enforcement", "model_driven_enforcement"],
            "cleanup": ["cleanup_before_next_thing"],
            "investigation": ["investigation_analysis", "intelligent_policy"],
        }

        for op_key, rule_list in operation_rule_mapping.items():
            if op_key in operation_lower:
                if rule_name in rule_list:
                    return True

        return False

    def _get_firing_reason(self, rule_name: str, file_path: str, operation: str = None) -> str:
        """Get the reason why a rule is firing"""
        if operation:
            return f"Operation '{operation}' matches rule purpose"
        return f"File '{file_path}' matches rule globs"

    def print_firing_rules(self, file_path: str, operation: str = None):
        """Print which rules are firing with emoji prefixes"""
        firing_rules = self.identify_firing_rules(file_path, operation)

        if not firing_rules:
            print("🤷 No rules firing for this context")
            return

        print(f"🎯 Rules firing for {file_path}" + (f" during {operation}" if operation else ""))
        print("=" * 60)

        for rule in firing_rules:
            print(f"{rule['emoji']} {rule['rule_name']}")
            print(f"   📝 {rule['description']}")
            print(f"   🎯 {rule['reason']}")
            print()

    def get_rule_summary(self) -> dict[str, Any]:
        """Get summary of all available rules"""
        return {
            "total_rules": len(self.cursor_rules.get("domains", [])),
            "rules": [{"name": rule_name, "emoji": self.get_rule_emoji(rule_name)} for rule_name in self.cursor_rules.get("domains", [])],
        }


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Identify which Cursor rules are firing")
    parser.add_argument("--file", "-f", help="File path to check")
    parser.add_argument("--operation", "-o", help="Operation being performed")
    parser.add_argument("--summary", "-s", action="store_true", help="Show rule summary")

    args = parser.parse_args()

    identifier = RuleFiringIdentifier()

    if args.summary:
        summary = identifier.get_rule_summary()
        print(f"🎯 Cursor Rules Summary ({summary['total_rules']} rules)")
        print("=" * 40)
        for rule in summary["rules"]:
            print(f"{rule['emoji']} {rule['name']}")

    elif args.file:
        identifier.print_firing_rules(args.file, args.operation)

    else:
        # Interactive mode
        print("🎯 Rule Firing Identifier")
        print("=" * 30)

        file_path = input("Enter file path (or press Enter to skip): ").strip()
        operation = input("Enter operation (or press Enter to skip): ").strip()

        if file_path:
            identifier.print_firing_rules(file_path, operation if operation else None)
        else:
            summary = identifier.get_rule_summary()
            print(f"📊 Available Rules: {summary['total_rules']}")
            for rule in summary["rules"]:
                print(f"{rule['emoji']} {rule['name']}")


if __name__ == "__main__":
    main()
