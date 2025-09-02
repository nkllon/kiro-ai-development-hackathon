#!/usr/bin/env python3
"""
Neo4j Proof of Concept - Graph Model Integration

This script demonstrates converting the project model to Neo4j graph structure
using our existing ArtifactForge infrastructure for round-trip validation.
"""

import json
from pathlib import Path
from typing import List

from src.artifact_forge.agents.artifact_detector import ArtifactDetector

# Import our existing ArtifactForge infrastructure
from src.artifact_forge.agents.artifact_parser import ArtifactParser


class Neo4jPOC:
    """Neo4j Proof of Concept using ArtifactForge infrastructure"""

    def __init__(self):
        """Initialize with ArtifactForge components"""
        self.parser = ArtifactParser()
        self.detector = ArtifactDetector()
        self.model = None

    def load_project_model(self, model_path: str = "project_model_registry.json") -> None:
        """Load the project model registry"""
        try:
            with open(model_path) as f:
                self.model = json.load(f)
            print(f"✅ Loaded project model from {model_path}")
        except Exception as e:
            print(f"❌ Failed to load project model: {e}")
            raise

    def validate_with_artifact_forge(self) -> bool:
        """Validate the project model using ArtifactForge infrastructure"""
        print("🔍 Validating project model with ArtifactForge...")

        try:
            # Use ArtifactForge to detect artifacts
            artifacts = self.detector.detect_artifacts(".")
            print(f"    ✅ Detected {len(artifacts)} artifacts")

            # Validate key files can be parsed
            validation_count = 0
            for artifact in artifacts[:5]:  # Test first 5
                try:
                    result = self.parser.parse_artifact(artifact.path, artifact.artifact_type)
                    if result:
                        validation_count += 1
                except Exception as e:
                    print(f"    ⚠️  Parse warning for {artifact.path}: {e}")

            print(f"    ✅ Successfully parsed {validation_count}/5 test artifacts")
            return validation_count > 0

        except Exception as e:
            print(f"    ❌ ArtifactForge validation failed: {e}")
            return False

    def generate_cypher_queries(self) -> list[str]:
        """Generate Cypher queries for Neo4j graph creation"""
        if not self.model:
            msg = "Project model not loaded"
            raise ValueError(msg)

        print("🔧 Generating Cypher queries...")
        queries = []

        # Create domain nodes
        queries.extend(self._create_domain_nodes())

        # Create rule nodes
        queries.extend(self._create_rule_nodes())

        # Create relationships
        queries.extend(self._create_relationships())

        # Add example queries
        queries.extend(self._generate_example_queries())

        print(f"    ✅ Generated {len(queries)} Cypher queries")
        return queries

    def _create_domain_nodes(self) -> list[str]:
        """Create Cypher queries for domain nodes"""
        queries = []

        # Get cursor rules domain
        cursor_rules = self.model["domain_architecture"]["cursor_rules"]

        # Create cursor_rules domain - single line query
        domain_query = f"CREATE (cursor_rules:Domain {{name: 'cursor_rules', description: '{cursor_rules['description']}', status: '{cursor_rules['status']}', rule_firing_identification: {str(cursor_rules['rule_firing_identification']).lower()}}}) RETURN cursor_rules;"
        queries.append(domain_query)

        print("    ✅ Created cursor_rules domain")
        return queries

    def _create_rule_nodes(self) -> list[str]:
        """Create Cypher queries for rule nodes"""
        queries = []

        cursor_rules = self.model["domain_architecture"]["cursor_rules"]
        emoji_prefixes = cursor_rules["emoji_prefixes"]

        for rule_name, emoji in emoji_prefixes.items():
            # Get rule file content for description
            rule_file = f".cursor/rules/{rule_name.replace('_', '-')}.mdc"
            description = f"Rule: {rule_name}"

            try:
                if Path(rule_file).exists():
                    # Use ArtifactForge to parse the rule file
                    result = self.parser.parse_artifact(rule_file, "mdc")
                    if result and hasattr(result, "description"):
                        description = result.description
            except Exception:
                pass  # Use default description if parsing fails

            rule_query = f"CREATE ({rule_name}:Rule {{name: '{rule_name}', emoji: '{emoji}', description: '{description}', type: 'cursor_rule'}}) RETURN {rule_name};"
            queries.append(rule_query)

        print(f"    ✅ Created {len(emoji_prefixes)} rule nodes")
        return queries

    def _create_relationships(self) -> list[str]:
        """Create Cypher queries for relationships"""
        queries = []

        cursor_rules = self.model["domain_architecture"]["cursor_rules"]
        emoji_prefixes = cursor_rules["emoji_prefixes"]

        # Create CONTAINS relationships
        for rule_name in emoji_prefixes:
            relationship_query = f"MATCH (d:Domain {{name: 'cursor_rules'}}) MATCH (r:Rule {{name: '{rule_name}'}}) CREATE (d)-[:CONTAINS]->(r) RETURN d, r;"
            queries.append(relationship_query)

        print(f"    ✅ Created {len(emoji_prefixes)} CONTAINS relationships")
        return queries

    def _generate_example_queries(self) -> list[str]:
        """Generate example Cypher queries for analysis"""
        queries = [
            # Find all rules in cursor_rules domain
            "MATCH (d:Domain {name: 'cursor_rules'})-[:CONTAINS]->(r:Rule) RETURN d.name as domain, r.name as rule, r.emoji as emoji ORDER BY r.name;",
            # Find rules by emoji pattern
            "MATCH (r:Rule) WHERE r.emoji CONTAINS '🔒' OR r.emoji CONTAINS '🔧' RETURN r.name as rule, r.emoji as emoji, r.description as description;",
            # Count rules by domain
            "MATCH (d:Domain)-[:CONTAINS]->(r:Rule) RETURN d.name as domain, count(r) as rule_count ORDER BY rule_count DESC;",
        ]

        print("    ✅ Generated 3 example analysis queries")
        return queries

    def save_cypher_queries(self, queries: list[str], output_file: str = "neo4j_setup.cypher") -> None:
        """Save Cypher queries to file"""
        try:
            with open(output_file, "w") as f:
                f.write("-- Neo4j Setup Script\n")
                f.write("-- Generated from project_model_registry.json\n")
                f.write("-- Using ArtifactForge infrastructure\n")
                f.write("-- IMPORTANT: Each query ends with semicolon\n\n")

                for i, query in enumerate(queries, 1):
                    f.write(f"-- Query {i}\n")
                    # Ensure query ends with semicolon
                    query_text = query.strip()
                    if not query_text.endswith(";"):
                        query_text += ";"
                    f.write(query_text)
                    f.write("\n\n")

            print(f"✅ Saved {len(queries)} Cypher queries to {output_file}")
        except Exception as e:
            print(f"❌ Failed to save queries: {e}")
            raise

    def run_poc(self) -> None:
        """Run the complete Neo4j POC"""
        print("🚀 Starting Neo4j POC with ArtifactForge integration...")

        try:
            # Load project model
            self.load_project_model()

            # Validate with ArtifactForge
            if not self.validate_with_artifact_forge():
                print("⚠️  ArtifactForge validation had issues, but continuing...")

            # Generate Cypher queries
            queries = self.generate_cypher_queries()

            # Save queries
            self.save_cypher_queries(queries)

            print("🎉 Neo4j POC completed successfully!")
            print(f"📊 Generated {len(queries)} Cypher queries")
            print("🔗 Ready for Neo4j database integration")

        except Exception as e:
            print(f"❌ Neo4j POC failed: {e}")
            raise


def main():
    """Main execution function"""
    poc = Neo4jPOC()
    poc.run_poc()


if __name__ == "__main__":
    main()
