#!/usr/bin/env python3
"""
Simple Domain Vocabulary Expansion Tool
Expands domain vocabulary without external dependencies by:
- Extracting terms from existing interfaces
- Building term frequency analysis
- Creating domain-specific taxonomies
- Expanding ubiquitous language indexing
"""

import ast
import os
import re
import json
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter


class SimpleDomainExpander:
    """Simple domain vocabulary expander without external dependencies."""

    def __init__(self):
        self.stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
        }

        self.domain_terms = set()
        self.ubiquitous_language = set()
        self.term_frequencies = Counter()
        self.term_co_occurrences = defaultdict(Counter)
        self.semantic_relationships = defaultdict(set)

        # Initialize with existing vocabulary
        self._initialize_base_vocabulary()

    def _initialize_base_vocabulary(self):
        """Initialize with base domain vocabulary."""
        self.domain_terms.update(
            [
                # Core Software Engineering
                "abstraction",
                "encapsulation",
                "inheritance",
                "polymorphism",
                "composition",
                "aggregation",
                "delegation",
                "facade",
                "adapter",
                "observer",
                "strategy",
                "factory",
                "singleton",
                "builder",
                "prototype",
                "command",
                "state",
                # Architecture Patterns
                "microservices",
                "monolith",
                "service_mesh",
                "api_gateway",
                "event_driven",
                "domain_driven",
                "test_driven",
                "behavior_driven",
                "clean_architecture",
                "hexagonal",
                "onion",
                "layered",
                "pipeline",
                "middleware",
                "plugin",
                # Development Practices
                "continuous_integration",
                "continuous_deployment",
                "continuous_delivery",
                "devops",
                "site_reliability",
                "infrastructure_as_code",
                "gitops",
                "agile",
                "scrum",
                "kanban",
                "lean",
                "extreme_programming",
                "pair_programming",
                # Quality Assurance
                "unit_testing",
                "integration_testing",
                "system_testing",
                "acceptance_testing",
                "performance_testing",
                "security_testing",
                "load_testing",
                "stress_testing",
                "code_review",
                "static_analysis",
                "dynamic_analysis",
                "profiling",
                # Data & Storage
                "relational",
                "nosql",
                "document",
                "key_value",
                "graph",
                "time_series",
                "data_lake",
                "data_warehouse",
                "etl",
                "elt",
                "streaming",
                "batch",
                "transaction",
                "consistency",
                "availability",
                "partition_tolerance",
                # Security & Compliance
                "authentication",
                "authorization",
                "encryption",
                "decryption",
                "hashing",
                "digital_signature",
                "certificate",
                "oauth",
                "saml",
                "jwt",
                "rbac",
                "audit_trail",
                "compliance",
                "gdpr",
                "sox",
                "hipaa",
                "pci_dss",
                # Monitoring & Observability
                "metrics",
                "logging",
                "tracing",
                "alerting",
                "dashboard",
                "visualization",
                "apm",
                "rum",
                "synthetic_monitoring",
                "distributed_tracing",
                "correlation",
                "anomaly_detection",
                "root_cause_analysis",
                "incident_response",
                # AI & Machine Learning
                "supervised_learning",
                "unsupervised_learning",
                "reinforcement_learning",
                "neural_network",
                "deep_learning",
                "transformer",
                "attention",
                "embedding",
                "feature_engineering",
                "model_training",
                "hyperparameter_tuning",
                "model_deployment",
                "mlops",
                "model_serving",
                "a_b_testing",
            ]
        )

        self.ubiquitous_language.update(
            [
                # Project-specific terms
                "kiro_ai",
                "development_hackathon",
                "competitive_launch",
                "rc0",
                "beast_mode_framework",
                "systematic_superiority",
                "zero_technical_debt",
                "claude_simone",
                "ai_assisted_development",
                "mcp_server",
                "github_integration",
                # Framework-specific terms
                "reflective_module",
                "interface_registry",
                "governance_system",
                "duplicate_prevention",
                "rm_ddd_compliance",
                "rdi_standard",
                "domain_driven_design",
                "ubiquitous_language",
                "bounded_context",
                # Integration-specific terms
                "project_management",
                "task_orchestration",
                "sprint_coordination",
                "demo_framework",
                "competitive_advantage",
                "velocity_improvement",
                "quality_gates",
                "systematic_validation",
                "performance_monitoring",
                # Architecture-specific terms
                "microservices_architecture",
                "event_sourcing",
                "cqrs_pattern",
                "hexagonal_architecture",
                "clean_code",
                "solid_principles",
                "dependency_injection",
                "inversion_of_control",
                "separation_of_concerns",
            ]
        )

    def extract_terms_from_code(self, file_path: str) -> Dict[str, Any]:
        """Extract domain terms from code files."""
        terms = {
            "class_names": set(),
            "method_names": set(),
            "variable_names": set(),
            "docstring_terms": set(),
            "comment_terms": set(),
            "import_terms": set(),
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Extract class names
                if isinstance(node, ast.ClassDef):
                    terms["class_names"].add(node.name)
                    # Extract docstring terms
                    if node.docstring:
                        terms["docstring_terms"].update(
                            self._extract_terms_from_text(node.docstring)
                        )

                # Extract method names
                elif isinstance(node, ast.FunctionDef):
                    terms["method_names"].add(node.name)
                    # Extract docstring terms
                    if node.docstring:
                        terms["docstring_terms"].update(
                            self._extract_terms_from_text(node.docstring)
                        )

                # Extract variable names
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            terms["variable_names"].add(target.id)

                # Extract import terms
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            terms["import_terms"].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            terms["import_terms"].add(node.module)
                        for alias in node.names:
                            terms["import_terms"].add(alias.name)

            # Extract terms from comments
            lines = content.split("\n")
            for line in lines:
                if line.strip().startswith("#"):
                    terms["comment_terms"].update(self._extract_terms_from_text(line))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return terms

    def _extract_terms_from_text(self, text: str) -> Set[str]:
        """Extract meaningful terms from text."""
        terms = set()

        # Clean and tokenize text
        text = re.sub(r"[^\w\s]", " ", text.lower())
        words = re.findall(r"\b[a-z_]{2,}\b", text)

        for word in words:
            if word not in self.stop_words and len(word) > 2:
                terms.add(word)

        return terms

    def build_term_relationships(self, all_terms: Dict[str, Dict[str, Set[str]]]):
        """Build semantic relationships between terms."""
        print("🔗 Building term relationships...")

        # Count term frequencies
        for file_path, terms_data in all_terms.items():
            for category, terms in terms_data.items():
                for term in terms:
                    self.term_frequencies[term] += 1

        # Build co-occurrence matrix
        for file_path, terms_data in all_terms.items():
            file_terms = set()
            for category, terms in terms_data.items():
                file_terms.update(terms)

            # Create co-occurrence relationships
            term_list = list(file_terms)
            for i, term1 in enumerate(term_list):
                for term2 in term_list[i + 1 :]:
                    self.term_co_occurrences[term1][term2] += 1
                    self.term_co_occurrences[term2][term1] += 1

        # Build semantic relationships
        for term, co_occurrences in self.term_co_occurrences.items():
            # Find terms that frequently co-occur
            top_co_occurrences = co_occurrences.most_common(5)
            for related_term, count in top_co_occurrences:
                if count > 2:  # Threshold for meaningful relationships
                    self.semantic_relationships[term].add(related_term)

    def generate_domain_taxonomy(self) -> Dict[str, Any]:
        """Generate domain-specific taxonomy."""
        taxonomy = {
            "architecture_patterns": [],
            "development_practices": [],
            "quality_metrics": [],
            "integration_patterns": [],
            "security_concepts": [],
            "monitoring_concepts": [],
            "ai_ml_terms": [],
            "project_specific": [],
        }

        # Categorize terms based on patterns
        for term in self.domain_terms:
            if any(
                pattern in term for pattern in ["pattern", "architecture", "design"]
            ):
                taxonomy["architecture_patterns"].append(term)
            elif any(pattern in term for pattern in ["test", "quality", "metric"]):
                taxonomy["quality_metrics"].append(term)
            elif any(pattern in term for pattern in ["integration", "api", "service"]):
                taxonomy["integration_patterns"].append(term)
            elif any(pattern in term for pattern in ["security", "auth", "encrypt"]):
                taxonomy["security_concepts"].append(term)
            elif any(pattern in term for pattern in ["monitor", "log", "metric"]):
                taxonomy["monitoring_concepts"].append(term)
            elif any(pattern in term for pattern in ["ai", "ml", "neural", "model"]):
                taxonomy["ai_ml_terms"].append(term)
            else:
                taxonomy["development_practices"].append(term)

        # Add project-specific terms
        taxonomy["project_specific"] = list(self.ubiquitous_language)

        return taxonomy

    def expand_vocabulary_from_codebase(self, root_path: str = "src") -> None:
        """Expand vocabulary by analyzing the entire codebase."""
        print("🔍 Expanding domain vocabulary from codebase...")

        all_terms = {}
        total_files = 0

        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    total_files += 1

                    terms = self.extract_terms_from_code(file_path)
                    all_terms[file_path] = terms

        print(f"📁 Files analyzed: {total_files}")

        # Build relationships
        self.build_term_relationships(all_terms)

        # Extract new terms
        new_domain_terms = set()
        new_ubiquitous_terms = set()

        for file_path, terms_data in all_terms.items():
            for category, terms in terms_data.items():
                for term in terms:
                    if (
                        term not in self.domain_terms
                        and term not in self.ubiquitous_language
                    ):
                        # Determine if it's a domain term or ubiquitous language
                        if self._is_domain_term(term):
                            new_domain_terms.add(term)
                        elif self._is_ubiquitous_language_term(term):
                            new_ubiquitous_terms.add(term)

        self.domain_terms.update(new_domain_terms)
        self.ubiquitous_language.update(new_ubiquitous_terms)

        print(f"📚 New domain terms: {len(new_domain_terms)}")
        print(f"🗣️  New ubiquitous language terms: {len(new_ubiquitous_terms)}")
        print(f"📚 Total domain terms: {len(self.domain_terms)}")
        print(f"🗣️  Total ubiquitous language terms: {len(self.ubiquitous_language)}")
        print(f"🔗 Term relationships: {len(self.semantic_relationships)}")

    def _is_domain_term(self, term: str) -> bool:
        """Determine if a term is a domain term."""
        # Check if term appears frequently
        if self.term_frequencies[term] < 3:
            return False

        # Check if term has meaningful relationships
        if len(self.semantic_relationships[term]) == 0:
            return False

        # Check if term is technical
        technical_patterns = [
            "api",
            "service",
            "manager",
            "handler",
            "controller",
            "processor",
            "validator",
            "transformer",
            "converter",
            "mapper",
            "adapter",
            "repository",
            "factory",
            "builder",
            "observer",
            "strategy",
            "test",
            "mock",
            "stub",
            "fixture",
            "assertion",
            "coverage",
            "engine",
            "system",
            "framework",
            "library",
            "tool",
            "utility",
        ]

        return any(pattern in term for pattern in technical_patterns)

    def _is_ubiquitous_language_term(self, term: str) -> bool:
        """Determine if a term is ubiquitous language."""
        # Check if term appears frequently
        if self.term_frequencies[term] < 5:
            return False

        # Check if term is project-specific
        project_patterns = [
            "kiro",
            "simone",
            "claude",
            "devpost",
            "hackathon",
            "beast",
            "systematic",
            "superiority",
            "competitive",
            "launch",
            "rc0",
            "reflective",
            "module",
            "governance",
            "compliance",
            "registry",
            "integration",
            "adapter",
            "mcp",
            "github",
            "ai_assisted",
        ]

        return any(pattern in term for pattern in project_patterns)

    def save_expanded_vocabulary(
        self, output_file: str = ".beast_mode/expanded_domain_vocabulary.json"
    ):
        """Save expanded vocabulary to file."""
        taxonomy = self.generate_domain_taxonomy()

        data = {
            "domain_terms": sorted(list(self.domain_terms)),
            "ubiquitous_language": sorted(list(self.ubiquitous_language)),
            "term_frequencies": dict(self.term_frequencies.most_common(100)),
            "semantic_relationships": {
                term: list(relationships)
                for term, relationships in self.semantic_relationships.items()
            },
            "taxonomy": taxonomy,
            "statistics": {
                "total_domain_terms": len(self.domain_terms),
                "total_ubiquitous_terms": len(self.ubiquitous_language),
                "total_relationships": len(self.semantic_relationships),
                "most_frequent_terms": dict(self.term_frequencies.most_common(20)),
            },
        }

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Expanded vocabulary saved to {output_file}")

        return data


def main():
    """Main execution function."""
    print("🚀 Simple Domain Vocabulary Expansion Tool")
    print("=" * 50)

    expander = SimpleDomainExpander()
    expander.expand_vocabulary_from_codebase()

    # Save expanded vocabulary
    data = expander.save_expanded_vocabulary()

    # Display summary
    print(f"\n📊 Expansion Summary:")
    print(f"   Domain terms: {data['statistics']['total_domain_terms']}")
    print(
        f"   Ubiquitous language terms: {data['statistics']['total_ubiquitous_terms']}"
    )
    print(f"   Semantic relationships: {data['statistics']['total_relationships']}")

    print(f"\n🔝 Most frequent terms:")
    for term, count in data["statistics"]["most_frequent_terms"].items():
        print(f"   {term}: {count}")

    print(f"\n🏷️  Taxonomy categories:")
    for category, terms in data["taxonomy"].items():
        print(f"   {category}: {len(terms)} terms")

    print(f"\n🎉 Domain vocabulary expansion complete!")


if __name__ == "__main__":
    main()
