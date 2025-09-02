#!/usr/bin/env python3
"""
Advanced Neo4j Integration

Enhanced graph operations, cross-domain analysis, and performance optimization.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any


class AdvancedNeo4jIntegration:
    """Advanced Neo4j operations and analysis"""

    def __init__(self, model_file: str = "project_model_registry.json"):
        self.model_file = Path(model_file)
        self.model_data = None
        self.neo4j_uri = "neo4j://localhost:7687"

    def load_model(self) -> None:
        """Load the project model with credential mappings"""
        if not self.model_file.exists():
            msg = f"Model file not found: {self.model_file}"
            raise FileNotFoundError(msg)

        with open(self.model_file) as f:
            self.model_data = json.load(f)
        print(f"✅ Loaded model: {self.model_file}")

    def get_credentials(self) -> dict[str, str]:
        """Get Neo4j credentials using 1Password item pointers"""
        credential_mappings = self.model_data.get("credential_mappings", {})

        if not credential_mappings:
            msg = "No credential mappings found in project model"
            raise ValueError(msg)

        # Use 1Password CLI to get actual values
        credentials = {}
        for key, op_pointer in credential_mappings.items():
            if key.startswith("neo4j_"):
                try:
                    # Extract the actual value from 1Password
                    result = subprocess.run(
                        ["op", "read", op_pointer],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    credentials[key] = result.stdout.strip()
                    print(f"✅ Retrieved {key} from 1Password")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Could not retrieve {key}: {e}")
                    # Fallback to environment variable
                    env_key = key.upper()
                    credentials[key] = os.getenv(env_key, "")
                    if credentials[key]:
                        print(f"✅ Retrieved {key} from environment variable {env_key}")

        return credentials

    def execute_cypher_query(self, query: str, credentials: dict[str, str]) -> list[dict[str, Any]]:
        """Execute Cypher query with secure credentials"""
        username = credentials.get("neo4j_username", "neo4j")
        password = credentials.get("neo4j_password", "")

        if not password:
            msg = "Neo4j password not available"
            raise ValueError(msg)

        cmd = ["cypher-shell", "-u", username, "-p", password, query]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return self._parse_cypher_output(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Neo4j query failed: {e}")
            return []

    def _parse_cypher_output(self, output: str) -> list[dict[str, Any]]:
        """Parse cypher-shell output into structured data"""
        lines = output.strip().split("\n")
        if len(lines) < 3:
            return []

        data_lines = lines[2:-1]
        results = []

        for line in data_lines:
            if line.strip() and "|" in line:
                parts = [part.strip().strip('"') for part in line.split("|")]
                if len(parts) >= 2:
                    # Create result dict based on number of columns
                    result_dict = {}
                    for i, part in enumerate(parts):
                        result_dict[f"col_{i}"] = part
                    results.append(result_dict)

        return results

    def analyze_graph_structure(self, credentials: dict[str, str]) -> dict[str, Any]:
        """Analyze the complete graph structure"""
        print("🔍 Analyzing Neo4j graph structure...")

        analysis = {}

        # 1. Node count by type
        node_query = "MATCH (n) RETURN labels(n) as labels, count(n) as count ORDER BY count DESC"
        node_results = self.execute_cypher_query(node_query, credentials)
        analysis["node_distribution"] = node_results

        # 2. Relationship count by type
        rel_query = "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC"
        rel_results = self.execute_cypher_query(rel_query, credentials)
        analysis["relationship_distribution"] = rel_results

        # 3. Graph density
        density_query = """
        MATCH (n)
        WITH count(n) as nodeCount
        MATCH ()-[r]->()
        WITH nodeCount, count(r) as relCount
        RETURN nodeCount, relCount,
               CASE WHEN nodeCount > 1
                    THEN toFloat(relCount) / (nodeCount * (nodeCount - 1))
                    ELSE 0
               END as density
        """
        density_results = self.execute_cypher_query(density_query, credentials)
        analysis["graph_density"] = density_results

        # 4. Connected components
        components_query = """
        MATCH (n)
        WITH collect(n) as nodes
        CALL gds.alpha.scc.stream('neo4j', {nodeLabels: ['*']})
        YIELD nodeId, componentId
        RETURN componentId, count(nodeId) as size
        ORDER BY size DESC
        """
        try:
            components_results = self.execute_cypher_query(components_query, credentials)
            analysis["connected_components"] = components_results
        except Exception:
            analysis["connected_components"] = [{"note": "GDS library not available"}]

        return analysis

    def discover_cross_domain_patterns(self, credentials: dict[str, str]) -> dict[str, Any]:
        """Discover patterns across different domains"""
        print("🔗 Discovering cross-domain patterns...")

        patterns = {}

        # 1. Rule sharing patterns
        rule_patterns_query = """
        MATCH (d1:Domain)-[:CONTAINS]->(r1:Rule)
        MATCH (d2:Domain)-[:CONTAINS]->(r2:Rule)
        WHERE d1 <> d2 AND r1.type = r2.type
        RETURN d1.name as domain1, d2.name as domain2, r1.type as rule_type,
               count(*) as shared_rules
        ORDER BY shared_rules DESC
        """
        rule_patterns = self.execute_cypher_query(rule_patterns_query, credentials)
        patterns["rule_sharing"] = rule_patterns

        # 2. Emoji pattern analysis
        emoji_patterns_query = """
        MATCH (r:Rule)
        WHERE r.emoji IS NOT NULL
        RETURN r.emoji as emoji, count(*) as usage_count,
               collect(DISTINCT r.type) as rule_types
        ORDER BY usage_count DESC
        """
        emoji_patterns = self.execute_cypher_query(emoji_patterns_query, credentials)
        patterns["emoji_patterns"] = emoji_patterns

        # 3. Domain complexity analysis
        complexity_query = """
        MATCH (d:Domain)-[:CONTAINS]->(r:Rule)
        RETURN d.name as domain, count(r) as rule_count,
               collect(DISTINCT r.type) as rule_types,
               collect(DISTINCT r.emoji) as emojis
        ORDER BY rule_count DESC
        """
        complexity_patterns = self.execute_cypher_query(complexity_query, credentials)
        patterns["domain_complexity"] = complexity_patterns

        return patterns

    def optimize_neo4j_performance(self, credentials: dict[str, str]) -> dict[str, Any]:
        """Analyze and suggest Neo4j performance optimizations"""
        print("⚡ Analyzing Neo4j performance...")

        optimizations = {}

        # 1. Index analysis
        index_query = "SHOW INDEXES"
        try:
            index_results = self.execute_cypher_query(index_query, credentials)
            optimizations["current_indexes"] = index_results
        except Exception:
            optimizations["current_indexes"] = [{"note": "Index query not supported"}]

        # 2. Query performance analysis
        performance_query = """
        CALL dbms.listQueries() YIELD queryId, query, parameters, username,
             startTime, elapsedTime, status
        RETURN queryId, query, elapsedTime, status
        ORDER BY elapsedTime DESC
        LIMIT 10
        """
        try:
            performance_results = self.execute_cypher_query(performance_query, credentials)
            optimizations["query_performance"] = performance_results
        except Exception:
            optimizations["query_performance"] = [{"note": "Performance monitoring not available"}]

        # 3. Memory usage
        memory_query = "CALL dbms.listConfig('dbms.memory') YIELD name, value"
        try:
            memory_results = self.execute_cypher_query(memory_query, credentials)
            optimizations["memory_config"] = memory_results
        except Exception:
            optimizations["memory_config"] = [{"note": "Memory config not accessible"}]

        return optimizations

    def create_advanced_visualizations(self, analysis_data: dict[str, Any]) -> None:
        """Create advanced visualization data for external tools"""
        print("📊 Creating advanced visualization data...")

        viz_dir = Path("data/visualizations")
        viz_dir.mkdir(parents=True, exist_ok=True)

        # 1. Graph structure summary
        structure_summary = """# Advanced Neo4j Graph Analysis

## Graph Structure Analysis

### Node Distribution
"""

        if "node_distribution" in analysis_data:
            for node in analysis_data["node_distribution"]:
                structure_summary += f"- {node.get('col_0', 'Unknown')}: {node.get('col_1', 'Unknown')} nodes\n"

        structure_summary += """

### Relationship Distribution
"""

        if "relationship_distribution" in analysis_data:
            for rel in analysis_data["relationship_distribution"]:
                structure_summary += f"- {rel.get('col_0', 'Unknown')}: {rel.get('col_1', 'Unknown')} relationships\n"

        structure_summary += """

### Graph Metrics
"""

        if "graph_density" in analysis_data:
            for metric in analysis_data["graph_density"]:
                structure_summary += f"- Nodes: {metric.get('col_0', 'Unknown')}\n"
                structure_summary += f"- Relationships: {metric.get('col_1', 'Unknown')}\n"
                structure_summary += f"- Density: {metric.get('col_2', 'Unknown')}\n"

        with open(viz_dir / "ADVANCED_NEO4J_ANALYSIS.md", "w") as f:
            f.write(structure_summary)

        # 2. Cross-domain patterns
        if "rule_sharing" in analysis_data:
            patterns_summary = "# Cross-Domain Pattern Analysis\n\n"
            patterns_summary += "## Rule Sharing Patterns\n\n"

            for pattern in analysis_data["rule_sharing"]:
                patterns_summary += f"- **{pattern.get('col_0', 'Unknown')} ↔ {pattern.get('col_1', 'Unknown')}**: "
                patterns_summary += f"{pattern.get('col_3', 'Unknown')} shared {pattern.get('col_2', 'Unknown')} rules\n"

            with open(viz_dir / "CROSS_DOMAIN_PATTERNS.md", "w") as f:
                f.write(patterns_summary)

        print(f"📄 Advanced analysis files created in {viz_dir}")

    def run_advanced_analysis(self) -> None:
        """Run the complete advanced Neo4j analysis"""
        try:
            # Get credentials securely
            credentials = self.get_credentials()

            print("🚀 Starting Advanced Neo4j Integration Analysis...")
            print("=" * 60)

            # 1. Graph structure analysis
            graph_analysis = self.analyze_graph_structure(credentials)
            print(f"✅ Graph structure analysis complete: {len(graph_analysis)} metrics")

            # 2. Cross-domain pattern discovery
            cross_domain_patterns = self.discover_cross_domain_patterns(credentials)
            print(f"✅ Cross-domain pattern discovery complete: {len(cross_domain_patterns)} pattern types")

            # 3. Performance optimization analysis
            performance_analysis = self.optimize_neo4j_performance(credentials)
            print(f"✅ Performance analysis complete: {len(performance_analysis)} optimization areas")

            # 4. Create advanced visualizations
            all_analysis = {
                **graph_analysis,
                **cross_domain_patterns,
                **performance_analysis,
            }

            self.create_advanced_visualizations(all_analysis)

            print("\n🎉 Advanced Neo4j Integration Complete!")
            print("📊 Check the 'data/visualizations' directory for detailed analysis")

            # Update project model
            self._update_project_model()

        except Exception as e:
            print(f"❌ Advanced Neo4j analysis failed: {e}")
            raise

    def _update_project_model(self) -> None:
        """Update the project model with advanced integration results"""
        try:
            # Add advanced integration phase
            advanced_phase = {
                "advanced_neo4j_integration": {
                    "status": "completed",
                    "next_phase": "graph_ml_integration",
                    "completed_tasks": [
                        "graph_structure_analysis",
                        "cross_domain_patterns",
                        "performance_optimization",
                        "advanced_visualizations",
                    ],
                    "requirements": [
                        "complex_cypher_queries",
                        "graph_algorithms",
                        "performance_monitoring",
                        "pattern_discovery",
                    ],
                }
            }

            # Update model
            with open(self.model_file) as f:
                current_model = json.load(f)

            current_model.update(advanced_phase)

            with open(self.model_file, "w") as f:
                json.dump(current_model, f, indent=2)

            print("✅ Project model updated with advanced integration phase")

        except Exception as e:
            print(f"⚠️  Could not update project model: {e}")


def main():
    """Main execution function"""
    integration = AdvancedNeo4jIntegration()

    try:
        integration.load_model()
        integration.run_advanced_analysis()

    except Exception as e:
        print(f"❌ Advanced Neo4j integration failed: {e}")


if __name__ == "__main__":
    main()
