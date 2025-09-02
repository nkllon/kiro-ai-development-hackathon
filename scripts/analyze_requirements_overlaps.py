#!/usr/bin/env python3
"""
Analyze domain requirements for overlaps.
"""

from src.round_trip_engineering.tools import get_model_registry
from collections import defaultdict
import re


def analyze_requirements_overlaps():
    """Analyze domain requirements for overlapping patterns."""

    # Load project model
    registry = get_model_registry()
    manager = registry.get_model("project")
    model_data = manager.load_model()
    domains = model_data.get("domains", {})

    print("🔍 Analyzing domain requirements for overlaps:")

    # Extract requirements by domain
    requirements_by_domain = {}
    for domain_name, domain_info in domains.items():
        if domain_info and isinstance(domain_info, dict):
            reqs = domain_info.get("requirements", [])
            if reqs:
                requirements_by_domain[domain_name] = reqs
                print(f"  {domain_name}: {len(reqs)} requirements")

    print(f"\n📊 Total domains with requirements: {len(requirements_by_domain)}")

    # Find overlapping requirements
    requirement_patterns = defaultdict(list)

    for domain, reqs in requirements_by_domain.items():
        for req in reqs:
            # Extract key terms from requirements
            req_lower = req.lower()

            # Common patterns to look for
            patterns = [
                "validation",
                "testing",
                "security",
                "logging",
                "profiling",
                "model",
                "crud",
                "registry",
                "backup",
                "environment",
                "reflective",
                "module",
                "compliance",
                "quality",
                "linting",
                "formatting",
                "documentation",
                "deployment",
                "monitoring",
            ]

            for pattern in patterns:
                if pattern in req_lower:
                    requirement_patterns[pattern].append((domain, req))

    print("\n🎯 OVERLAPPING REQUIREMENTS ANALYSIS:")
    print("=" * 60)

    # Show overlaps by pattern
    for pattern, occurrences in requirement_patterns.items():
        if len(occurrences) > 1:  # Only show actual overlaps
            print(f"\n🔗 {pattern.upper()} (Found in {len(occurrences)} domains):")
            for domain, req in occurrences:
                print(f"  • {domain}: {req}")

    # Show domains with most requirements
    print(f"\n📈 DOMAINS WITH MOST REQUIREMENTS:")
    print("=" * 60)

    sorted_domains = sorted(requirements_by_domain.items(), key=lambda x: len(x[1]), reverse=True)

    for domain, reqs in sorted_domains[:10]:  # Top 10
        print(f"\n🏗️  {domain} ({len(reqs)} requirements):")
        for req in reqs:
            print(f"    - {req}")

    # Find potential consolidation opportunities
    print(f"\n💡 POTENTIAL CONSOLIDATION OPPORTUNITIES:")
    print("=" * 60)

    # Look for domains with similar requirement patterns
    domain_similarities = defaultdict(list)

    for domain1, reqs1 in requirements_by_domain.items():
        for domain2, reqs2 in requirements_by_domain.items():
            if domain1 != domain2:
                # Count common requirement terms
                req1_terms = set()
                req2_terms = set()

                for req in reqs1:
                    req1_terms.update(req.lower().split())
                for req in reqs2:
                    req2_terms.update(req.lower().split())

                common_terms = req1_terms.intersection(req2_terms)
                if len(common_terms) >= 3:  # At least 3 common terms
                    similarity_score = len(common_terms) / max(len(req1_terms), len(req2_terms))
                    if similarity_score > 0.3:  # 30% similarity threshold
                        domain_similarities[domain1].append((domain2, similarity_score))

    for domain, similarities in domain_similarities.items():
        if similarities:
            print(f"\n🔗 {domain} has high similarity with:")
            for similar_domain, score in sorted(similarities, key=lambda x: x[1], reverse=True):
                print(f"    • {similar_domain} ({score:.1%} similarity)")


if __name__ == "__main__":
    analyze_requirements_overlaps()
