#!/usr/bin/env python3
"""
Fast Model Updater

Bypasses slow JSON parsing for bulk model updates using direct string operations.
"""

import re
from pathlib import Path


def update_package_scores():
    """Update package scores in project_model_registry.json using fast string operations"""

    model_file = Path("project_model_registry.json")
    if not model_file.exists():
        print("❌ project_model_registry.json not found")
        return

    print("🚀 Fast model update starting...")

    # Read file as text for fast string operations
    content = model_file.read_text()

    # Define score updates (domain_name: new_score)
    score_updates = {
        "cursor_rules": 9,
        "neo4j_integration": 10,
        "ghostbusters": 10,
        "code_quality_system": 9,
        "intelligent_linter_system": 7,
        "artifact_forge": 6,
        "model_driven_projection": 7,
        "mdc_generator": 8,
        "security_first": 8,
        "healthcare_cdc": 7,
        "ghostbusters_api": 8,
        "ghostbusters_gcp": 7,
        "mcp_integration": 6,
        "rule_compliance": 6,
    }

    updates_applied = 0

    for domain_name, new_score in score_updates.items():
        # Simple pattern to find and replace score values
        old_pattern = rf'"score":\s*(\d+)'

        # Find all score fields in the file
        matches = re.finditer(old_pattern, content)

        for match in matches:
            # Check if this score is within the right domain context
            start_pos = max(0, match.start() - 200)  # Look back 200 chars
            end_pos = min(len(content), match.end() + 200)  # Look forward 200 chars
            context = content[start_pos:end_pos]

            # Check if this context contains our domain name
            if f'"{domain_name}"' in context:
                # Replace the score
                old_score = match.group(1)
                new_content = content[: match.start(1)] + str(new_score) + content[match.end(1) :]

                if new_content != content:
                    content = new_content
                    updates_applied += 1
                    print(f"  ✅ Updated {domain_name}: score {old_score} → {new_score}")
                    break  # Only update the first match for this domain
        else:
            print(f"  ❌ Domain {domain_name} not found or no package_potential")

    # Write updated content back
    if updates_applied > 0:
        model_file.write_text(content)
        print(f"\n🎉 Applied {updates_applied} score updates")
        print("✅ Model updated successfully!")
    else:
        print("\n⚠️  No updates were applied")


def add_missing_package_potential():
    """Add package_potential to domains that don't have it"""

    model_file = Path("project_model_registry.json")
    if not model_file.exists():
        print("❌ project_model_registry.json not found")
        return

    print("🔍 Adding missing package_potential fields...")

    # This is a simplified approach - in practice, we'd need more sophisticated parsing
    # For now, let's focus on the fast score updates

    print("📝 Note: Adding missing package_potential requires more complex parsing")
    print("💡 Consider using the existing search_replace tool for individual domains")


if __name__ == "__main__":
    print("🚀 Fast Model Updater")
    print("=" * 50)

    update_package_scores()

    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("  1. Test PyPI package generator")
    print("  2. Validate model in Neo4j")
    print("  3. Run round-trip tests")
