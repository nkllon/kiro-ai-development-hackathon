#!/usr/bin/env python3
"""
Domain operations for model CRUD system.
Single responsibility: Domain-specific operations (list-domains, list-domain-requirements).
"""

import json
import csv
import sys
from pathlib import Path
from typing import Dict, Any, List


class DomainOperations:
    """Handles domain-specific operations."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.registry_file = self.project_root / "project_model_registry.json"

    def load_project_model(self) -> Dict[str, Any]:
        """Load the project model registry."""
        if not self.registry_file.exists():
            raise FileNotFoundError("project_model_registry.json not found")

        with open(self.registry_file, "r") as f:
            return json.load(f)

    def list_domains(self) -> str:
        """List all domains in the project model."""
        try:
            project_model = self.load_project_model()
            domains = project_model.get("domains", {})
            domain_architecture = project_model.get("domain_architecture", {})

            if not domains:
                return "📋 No domains found in project model registry"

            output = []
            output.append("📋 Project Domains:")
            output.append("=" * 50)

            # Group domains by architecture category
            categorized_domains = set()

            for category, category_info in domain_architecture.items():
                if category_info is None:
                    continue
                category_domains = category_info.get("domains", [])
                if category_domains:
                    output.append(f"\n🏗️  {category.replace('_', ' ').title()}:")
                    output.append(f"   Purpose: {category_info.get('description', 'N/A')}")
                    output.append("   Domains:")

                    for domain_name in category_domains:
                        domain_info = domains.get(domain_name, {})
                        if domain_info and domain_info.get("description"):
                            output.append(f"     • {domain_name}")
                            output.append(f"       - {domain_info['description']}")
                        else:
                            output.append(f"     • {domain_name}")
                        categorized_domains.add(domain_name)

            # Show uncategorized domains
            uncategorized = set(domains.keys()) - categorized_domains
            if uncategorized:
                output.append(f"\n📁 Uncategorized Domains:")
                for domain_name in sorted(uncategorized):
                    domain_info = domains.get(domain_name, {})
                    output.append(f"     • {domain_name}")
                    if domain_info and domain_info.get("description"):
                        output.append(f"       - {domain_info['description']}")

            # Summary
            output.append(f"\n📊 Summary:")
            output.append(f"   Total Domains: {len(domains)}")
            output.append(f"   Categorized: {len(domains) - len(uncategorized)}")
            output.append(f"   Uncategorized: {len(uncategorized)}")

            return "\n".join(output)

        except Exception as e:
            import traceback

            return f"❌ Error loading domains: {e}\n🔍 Error details: {traceback.format_exc()}"

    def list_domain_requirements(
        self,
        domain: str = None,
        search: str = None,
        category: str = None,
        format: str = "text",
    ) -> str:
        """List domain requirements with filtering options."""
        try:
            project_model = self.load_project_model()
            domains = project_model.get("domains", {})
            domain_architecture = project_model.get("domain_architecture", {})
            requirements_traceability = project_model.get("requirements_traceability", [])

            if not domains and not requirements_traceability:
                return "📋 No domains or requirements found in project model registry"

            # Filter domains if specified
            if domain:
                if domain not in domains:
                    return f"❌ Domain '{domain}' not found"
                domains_to_show = {domain: domains[domain]}
            else:
                domains_to_show = domains

            # Filter by category if specified
            if category:
                if category not in domain_architecture:
                    return f"❌ Category '{category}' not found"
                category_domains = domain_architecture[category].get("domains", [])
                domains_to_show = {k: v for k, v in domains_to_show.items() if k in category_domains}

                # Filter by search term if specified
                if search:
                    search_term = search.lower()
                    filtered_domains = {}
                    filtered_requirements = []

                    # Search in domains
                    for domain_name, domain_info in domains_to_show.items():
                        if domain_info and isinstance(domain_info, dict):
                            reqs = domain_info.get("requirements", [])
                            # Check if search term appears in domain name or requirements
                            if search_term in domain_name.lower() or any(search_term in req.lower() for req in reqs):
                                filtered_domains[domain_name] = domain_info

                    # Search in requirements_traceability
                    for req in requirements_traceability:
                        if isinstance(req, dict):
                            req_text = f"{req.get('title', '')} {req.get('description', '')} {req.get('requirement', '')}".lower()
                            if search_term in req_text:
                                filtered_requirements.append(req)

                    domains_to_show = filtered_domains
                    requirements_traceability = filtered_requirements

            # Output format handling
            if format == "json":
                return self._format_json_with_traceability(domains_to_show, requirements_traceability)
            elif format == "csv":
                return self._format_csv_with_traceability(domains_to_show, requirements_traceability)
            else:  # text format
                return self._format_text_with_traceability(domains_to_show, requirements_traceability)

        except Exception as e:
            import traceback

            return f"❌ Error loading domain requirements: {e}\n🔍 Error details: {traceback.format_exc()}"

    def _format_json_with_traceability(
        self,
        domains_to_show: Dict[str, Any],
        requirements_traceability: List[Dict[str, Any]],
    ) -> str:
        """Format output as JSON including both domains and traceability."""
        output_data = {
            "domains": {},
            "requirements_traceability": requirements_traceability,
        }

        for domain_name, domain_info in domains_to_show.items():
            if domain_info and isinstance(domain_info, dict):
                output_data["domains"][domain_name] = {
                    "requirements": domain_info.get("requirements", []),
                    "description": domain_info.get("description", ""),
                    "patterns": domain_info.get("patterns", []),
                    "linter": domain_info.get("linter", "N/A"),
                    "formatter": domain_info.get("formatter", "N/A"),
                    "validator": domain_info.get("validator", "N/A"),
                }
        return json.dumps(output_data, indent=2)

    def _format_csv_with_traceability(
        self,
        domains_to_show: Dict[str, Any],
        requirements_traceability: List[Dict[str, Any]],
    ) -> str:
        """Format output as CSV including both domains and traceability."""
        output = []
        writer = csv.writer(output)
        writer.writerow(["Type", "Source", "ID", "Title", "Description"])

        # Domain requirements
        for domain_name, domain_info in domains_to_show.items():
            if domain_info and isinstance(domain_info, dict):
                reqs = domain_info.get("requirements", [])
                for req in reqs:
                    writer.writerow(["Domain Requirement", domain_name, "", "", req])

        # Traceability requirements
        for req in requirements_traceability:
            if isinstance(req, dict):
                writer.writerow(
                    [
                        "Traceability Requirement",
                        req.get("collection", "requirements_traceability"),
                        req.get("id", ""),
                        req.get("title", ""),
                        req.get("description", ""),
                    ]
                )

        return "".join(output)

    def _format_text_with_traceability(
        self,
        domains_to_show: Dict[str, Any],
        requirements_traceability: List[Dict[str, Any]],
    ) -> str:
        """Format output as text including both domains and traceability."""
        output = []
        output.append("📋 Domain Requirements:")
        output.append("=" * 60)

        # Domain requirements
        for domain_name, domain_info in domains_to_show.items():
            if domain_info and isinstance(domain_info, dict):
                reqs = domain_info.get("requirements", [])
                if reqs:
                    output.append(f"\n🏗️  {domain_name} ({len(reqs)} requirements):")
                    if domain_info.get("description"):
                        output.append(f"   Description: {domain_info['description']}")
                    output.append("   Requirements:")
                    for i, req in enumerate(reqs, 1):
                        output.append(f"     {i}. {req}")

                    # Traceability requirements
            if requirements_traceability:
                output.append(f"\n📋 Requirements Traceability ({len(requirements_traceability)} items):")
                output.append("=" * 60)

                for i, req in enumerate(requirements_traceability, 1):
                    if isinstance(req, dict):
                        # Use 'requirement' field as primary, fallback to 'title' or 'description'
                        title = req.get("requirement") or req.get("title") or "Untitled"
                        output.append(f"\n📝 {i}. {title}")
                        if req.get("id"):
                            output.append(f"   ID: {req['id']}")
                        if req.get("description") and req.get("description") != title:
                            output.append(f"   Description: {req['description']}")
                        if req.get("domain"):
                            output.append(f"   Domain: {req['domain']}")
                        if req.get("implementation"):
                            output.append(f"   Implementation: {req['implementation']}")
                        if req.get("test"):
                            output.append(f"   Test: {req['test']}")
                        if req.get("collection"):
                            output.append(f"   Collection: {req['collection']}")

        # Summary
        output.append(f"\n📊 Summary:")
        domain_count = len(domains_to_show)
        domain_req_count = sum(len(domain_info.get("requirements", [])) for domain_info in domains_to_show.values() if domain_info and isinstance(domain_info, dict))
        traceability_count = len(requirements_traceability)

        output.append(f"   Domains: {domain_count}")
        output.append(f"   Domain Requirements: {domain_req_count}")
        output.append(f"   Traceability Requirements: {traceability_count}")
        output.append(f"   Total Requirements: {domain_req_count + traceability_count}")

        return "\n".join(output)


def create_domain_operations() -> DomainOperations:
    """Factory function to create domain operations instance."""
    return DomainOperations()
