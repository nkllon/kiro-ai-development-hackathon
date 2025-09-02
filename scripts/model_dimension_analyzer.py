#!/usr/bin/env python3
"""
Model Dimension Analyzer

Analyzes project model dimensions and creates meta-model queries using Graph() API at third meta level
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Set


class Load_Model:
    """Analyzes project model dimensions and creates meta-model queries using Graph() API at third meta level"""

    def __init__(self, model_file: str = "project_model_registry.json"):
        self.model_file = Path(model_file)
        self.model_data = None
        self.dimensions = defaultdict(set)

    def load_model(self) -> None:
        """Load the project model"""
        if not self.model_file.exists():
            msg = f"Model file not found: {self.model_file}"
            raise FileNotFoundError(msg)

        with open(self.model_file) as f:
            self.model_data = json.load(f)
        print(f"✅ Loaded model: {self.model_file}")

    def analyze_dimensions(self) -> dict[str, set[str]]:
        """Analyze all dimensions in the model"""
        if not self.model_data:
            msg = "Model not loaded"
            raise ValueError(msg)

        print("🔍 Analyzing model dimensions...")

        # Top-level dimensions
        self.dimensions["top_level"] = set(self.model_data.keys())

        # Domain dimensions
        if "domains" in self.model_data:
            self.dimensions["domains"] = set(self.model_data["domains"].keys())

        # Meta dimensions
        if "meta" in self.model_data:
            self.dimensions["meta"] = set(self.model_data["meta"].keys())

        # Cursor rules dimensions
        if "cursor_rules" in self.model_data:
            cursor_rules = self.model_data["cursor_rules"]
            if "domains" in cursor_rules:
                self.dimensions["cursor_rules_domains"] = set(cursor_rules["domains"])
            if "emoji_prefixes" in cursor_rules:
                self.dimensions["cursor_rules_emoji"] = set(cursor_rules["emoji_prefixes"].keys())

        # Neo4j integration dimensions
        if "neo4j_integration" in self.model_data:
            neo4j = self.model_data["neo4j_integration"]
            if "domains" in neo4j:
                self.dimensions["neo4j_domains"] = set(neo4j["domains"])
            if "requirements" in neo4j:
                self.dimensions["neo4j_requirements"] = {str(i) for i in range(len(neo4j["requirements"]))}
            if "completed_tasks" in neo4j:
                self.dimensions["neo4j_completed_tasks"] = {str(i) for i in range(len(neo4j["completed_tasks"]))}

        # Analyze domain structures
        self._analyze_domain_structures()

        return dict(self.dimensions)

    def _analyze_domain_structures(self) -> None:
        """Analyze the structure of individual domains"""
        if "domains" not in self.model_data:
            return

        for domain_name, domain_data in self.model_data["domains"].items():
            if isinstance(domain_data, dict):
                # Domain structure dimensions
                domain_keys = set(domain_data.keys())
                self.dimensions[f"domain_{domain_name}_structure"] = domain_keys

                # Patterns and content indicators
                if "patterns" in domain_data:
                    self.dimensions[f"domain_{domain_name}_patterns"] = {str(i) for i in range(len(domain_data["patterns"]))}
                if "content_indicators" in domain_data:
                    self.dimensions[f"domain_{domain_name}_indicators"] = {str(i) for i in range(len(domain_data["content_indicators"]))}
                if "requirements" in domain_data:
                    self.dimensions[f"domain_{domain_name}_requirements"] = {str(i) for i in range(len(domain_data["requirements"]))}

                # Package potential if exists
                if "package_potential" in domain_data:
                    package_keys = set(domain_data["package_potential"].keys())
                    self.dimensions[f"domain_{domain_name}_package"] = package_keys

    def generate_neo4j_meta_query(self) -> str:
        """Generate Cypher query to discover model dimensions in Neo4j"""
        return """
// Meta-Model Discovery Query
// This query discovers all dimensions and relationships in the project model

// 1. Discover all node types
MATCH (n)
RETURN DISTINCT labels(n) as node_types, count(n) as count
ORDER BY count DESC;

// 2. Discover all relationship types
MATCH ()-[r]->()
RETURN DISTINCT type(r) as relationship_types, count(r) as count
ORDER BY count DESC;

// 3. Discover domain structure
MATCH (d:Domain)
RETURN d.name as domain_name,
       d.description as description,
       d.status as status,
       d.priority as priority,
       size([(d)-[:CONTAINS]->(r:Rule) | r]) as rule_count;

// 4. Discover rule patterns
MATCH (r:Rule)
RETURN r.type as rule_type,
       r.emoji as emoji,
       count(r) as count
ORDER BY count DESC;

// 5. Discover package potential
MATCH (d:Domain)
WHERE d.package_potential IS NOT NULL
RETURN d.name as domain_name,
       d.package_potential.score as score,
       d.package_potential.pypi_ready as pypi_ready,
       d.package_potential.package_name as package_name
ORDER BY d.package_potential.score DESC;

// 6. Discover model completeness
MATCH (d:Domain)
RETURN d.status as status, count(d) as count
ORDER BY count DESC;

// 7. Discover cross-domain relationships
MATCH (d1:Domain)-[:RELATES_TO]->(d2:Domain)
RETURN d1.name as source_domain, d2.name as target_domain, type(RELATES_TO) as relationship_type;

// 8. Discover model metadata
MATCH (m:Meta)
RETURN m.model_type as model_type,
       m.model_completeness as completeness,
       m.domain_coverage as coverage,
       m.test_coverage as test_coverage;
"""

    def generate_json_meta_query(self) -> dict[str, Any]:
        """Generate JSON query structure to discover model dimensions"""
        return {
            "meta_model_discovery": {
                "top_level_dimensions": list(self.dimensions.get("top_level", [])),
                "domain_count": len(self.dimensions.get("domains", [])),
                "cursor_rules_count": len(self.dimensions.get("cursor_rules_domains", [])),
                "meta_dimensions": list(self.dimensions.get("meta", [])),
                "total_dimensions": sum(len(dims) for dims in self.dimensions.values()),
                "dimension_breakdown": {name: list(dims) for name, dims in self.dimensions.items()},
            }
        }

    def print_dimension_summary(self) -> None:
        """Print a summary of all discovered dimensions"""
        print("\n" + "=" * 60)
        print("📊 MODEL DIMENSION ANALYSIS SUMMARY")
        print("=" * 60)

        total_dimensions = sum(len(dims) for dims in self.dimensions.values())
        print(f"🎯 Total Dimensions Discovered: {total_dimensions}")
        print(f"🏗️  Top-Level Categories: {len(self.dimensions.get('top_level', []))}")
        print(f"🌐 Domain Categories: {len(self.dimensions.get('domains', []))}")
        print(f"📋 Cursor Rules: {len(self.dimensions.get('cursor_rules_domains', []))}")
        print(f"🔧 Meta Categories: {len(self.dimensions.get('meta', []))}")

        print("\n📋 DETAILED BREAKDOWN:")
        for category, dims in self.dimensions.items():
            if dims:
                print(f"  {category}: {len(dims)} dimensions")
                if len(dims) <= 10:  # Show details for small categories
                    for dim in sorted(dims):
                        print(f"    - {dim}")
                else:
                    print(f"    - {', '.join(sorted(list(dims)[:5]))}... and {len(dims) - 5} more")

        print("\n🚀 NEXT STEPS:")
        print("  1. Run Neo4j meta-query to discover database dimensions")
        print("  2. Validate JSON dimensions against Neo4j data")
        print("  3. Identify gaps and missing dimensions")
        print("  4. Update model registry with discovered dimensions")


def main():
    """Main execution function"""
    analyzer = Load_Model()

    try:
        analyzer.load_model()
        analyzer.analyze_dimensions()
        analyzer.print_dimension_summary()

        # Generate queries
        neo4j_query = analyzer.generate_neo4j_meta_query()
        json_query = analyzer.generate_json_meta_query()

        # Save queries
        with open("neo4j_meta_query.cypher", "w") as f:
            f.write(neo4j_query)

        with open("json_meta_query.json", "w") as f:
            json.dump(json_query, f, indent=2)

        print("\n✅ Generated queries:")
        print("  📄 Neo4j: neo4j_meta_query.cypher")
        print("  📄 JSON: json_meta_query.json")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")


if __name__ == "__main__":
    main()
