#!/usr/bin/env python3
"""
Multi-Dimensional Vocabulary Projector
=====================================

Projects the ubiquitous language vocabulary across multiple dimensions
to create comprehensive markdown documentation from different perspectives.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Create multi-dimensional vocabulary projections
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class VocabularyTerm:
    """A vocabulary term in the ubiquitous language."""
    term: str
    definition: str
    category: str
    context: str
    related_terms: List[str]
    examples: List[str]
    synonyms: List[str]
    antonyms: List[str]

class ProjectionDimension(Enum):
    """Different dimensions for projecting vocabulary."""
    BY_CATEGORY = "by_category"
    BY_CONTEXT = "by_context"
    BY_ALPHABETICAL = "by_alphabetical"
    BY_RELATIONSHIPS = "by_relationships"
    BY_COMPLEXITY = "by_complexity"
    BY_STAKEHOLDER = "by_stakeholder"
    BY_IMPLEMENTATION_PHASE = "by_implementation_phase"
    BY_DOMAIN_BOUNDARY = "by_domain_boundary"

class MultiDimensionalVocabularyProjector:
    """Projects vocabulary across multiple dimensions."""
    
    def __init__(self, vocabulary_file: str = "docs/ubiquitous_language_vocabulary.json"):
        self.vocabulary_file = Path(vocabulary_file)
        self.vocabulary: Dict[str, VocabularyTerm] = {}
        self.output_dir = Path("docs/vocabulary_projections")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_vocabulary(self) -> None:
        """Load vocabulary from JSON file."""
        if not self.vocabulary_file.exists():
            print(f"❌ Vocabulary file not found: {self.vocabulary_file}")
            return
            
        with open(self.vocabulary_file, 'r') as f:
            data = json.load(f)
            
        for term_name, term_data in data.items():
            self.vocabulary[term_name] = VocabularyTerm(
                term=term_data["term"],
                definition=term_data["definition"],
                category=term_data["category"],
                context=term_data["context"],
                related_terms=term_data["related_terms"],
                examples=term_data["examples"],
                synonyms=term_data["synonyms"],
                antonyms=term_data["antonyms"]
            )
        
        print(f"✅ Loaded {len(self.vocabulary)} vocabulary terms")
    
    def project_by_category(self) -> str:
        """Project vocabulary by category dimension."""
        categories = {}
        for term in self.vocabulary.values():
            if term.category not in categories:
                categories[term.category] = []
            categories[term.category].append(term)
        
        markdown = "# Vocabulary by Category\n\n"
        markdown += "**Projection Dimension:** Category-based organization\n"
        markdown += "**Purpose:** Group terms by their primary functional category\n\n"
        
        for category, terms in sorted(categories.items()):
            markdown += f"## {category}\n\n"
            markdown += f"**{len(terms)} terms** in this category\n\n"
            
            for term in sorted(terms, key=lambda t: t.term):
                markdown += f"### {term.term}\n"
                markdown += f"*{term.context}*\n\n"
                markdown += f"{term.definition}\n\n"
                
                if term.related_terms:
                    markdown += f"**Related:** {', '.join(term.related_terms)}\n\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def project_by_context(self) -> str:
        """Project vocabulary by context dimension."""
        contexts = {}
        for term in self.vocabulary.values():
            if term.context not in contexts:
                contexts[term.context] = []
            contexts[term.context].append(term)
        
        markdown = "# Vocabulary by Context\n\n"
        markdown += "**Projection Dimension:** Context-based organization\n"
        markdown += "**Purpose:** Group terms by their usage context and domain\n\n"
        
        for context, terms in sorted(contexts.items()):
            markdown += f"## {context}\n\n"
            markdown += f"**{len(terms)} terms** in this context\n\n"
            
            for term in sorted(terms, key=lambda t: t.term):
                markdown += f"### {term.term}\n"
                markdown += f"*{term.category}*\n\n"
                markdown += f"{term.definition}\n\n"
                
                if term.examples:
                    markdown += f"**Examples:**\n"
                    for example in term.examples:
                        markdown += f"- {example}\n"
                    markdown += "\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def project_by_alphabetical(self) -> str:
        """Project vocabulary by alphabetical dimension."""
        markdown = "# Vocabulary Alphabetically\n\n"
        markdown += "**Projection Dimension:** Alphabetical organization\n"
        markdown += "**Purpose:** Quick reference lookup by term name\n\n"
        
        for term_name in sorted(self.vocabulary.keys()):
            term = self.vocabulary[term_name]
            markdown += f"## {term.term}\n\n"
            markdown += f"**Category:** {term.category}\n"
            markdown += f"**Context:** {term.context}\n\n"
            markdown += f"{term.definition}\n\n"
            
            if term.related_terms:
                markdown += f"**Related Terms:** {', '.join(term.related_terms)}\n\n"
            
            if term.synonyms:
                markdown += f"**Synonyms:** {', '.join(term.synonyms)}\n\n"
            
            if term.antonyms:
                markdown += f"**Antonyms:** {', '.join(term.antonyms)}\n\n"
            
            markdown += "---\n\n"
        
        return markdown
    
    def project_by_relationships(self) -> str:
        """Project vocabulary by relationship dimension."""
        markdown = "# Vocabulary by Relationships\n\n"
        markdown += "**Projection Dimension:** Relationship-based organization\n"
        markdown += "**Purpose:** Show how terms connect and relate to each other\n\n"
        
        # Build relationship graph
        relationships = {}
        for term in self.vocabulary.values():
            relationships[term.term] = {
                'related_to': term.related_terms,
                'synonyms': term.synonyms,
                'antonyms': term.antonyms,
                'category': term.category,
                'context': term.context
            }
        
        # Find highly connected terms
        highly_connected = []
        for term_name, rels in relationships.items():
            total_connections = len(rels['related_to']) + len(rels['synonyms']) + len(rels['antonyms'])
            if total_connections >= 3:
                highly_connected.append((term_name, total_connections))
        
        highly_connected.sort(key=lambda x: x[1], reverse=True)
        
        markdown += "## Highly Connected Terms\n\n"
        markdown += "Terms with 3+ relationships:\n\n"
        
        for term_name, connection_count in highly_connected:
            term = self.vocabulary[term_name]
            markdown += f"### {term.term} ({connection_count} connections)\n\n"
            markdown += f"**Definition:** {term.definition}\n\n"
            
            if term.related_terms:
                markdown += f"**Related Terms:** {', '.join(term.related_terms)}\n\n"
            
            if term.synonyms:
                markdown += f"**Synonyms:** {', '.join(term.synonyms)}\n\n"
            
            if term.antonyms:
                markdown += f"**Antonyms:** {', '.join(term.antonyms)}\n\n"
            
            markdown += "---\n\n"
        
        # Show relationship clusters
        markdown += "## Relationship Clusters\n\n"
        
        # Group by category and show internal relationships
        categories = {}
        for term in self.vocabulary.values():
            if term.category not in categories:
                categories[term.category] = []
            categories[term.category].append(term)
        
        for category, terms in sorted(categories.items()):
            if len(terms) < 2:
                continue
                
            markdown += f"### {category} Cluster\n\n"
            
            # Find internal relationships within category
            internal_relations = []
            for term in terms:
                for related in term.related_terms:
                    if related in [t.term for t in terms]:
                        internal_relations.append((term.term, related))
            
            if internal_relations:
                markdown += "**Internal Relationships:**\n"
                for term1, term2 in internal_relations:
                    markdown += f"- {term1} ↔ {term2}\n"
                markdown += "\n"
            
            markdown += "---\n\n"
        
        return markdown
    
    def project_by_complexity(self) -> str:
        """Project vocabulary by complexity dimension."""
        markdown = "# Vocabulary by Complexity\n\n"
        markdown += "**Projection Dimension:** Complexity-based organization\n"
        markdown += "**Purpose:** Organize terms from simple to complex concepts\n\n"
        
        # Define complexity levels based on various factors
        complexity_levels = {
            "Basic": [],
            "Intermediate": [],
            "Advanced": [],
            "Expert": []
        }
        
        for term in self.vocabulary.values():
            # Simple heuristic for complexity
            complexity_score = 0
            
            # Length of definition
            complexity_score += len(term.definition) // 50
            
            # Number of related terms
            complexity_score += len(term.related_terms)
            
            # Number of examples
            complexity_score += len(term.examples)
            
            # Category complexity
            if term.category in ["Core Framework", "Reflective Architecture"]:
                complexity_score += 1
            elif term.category in ["Domain-Driven Design", "Systematic Development"]:
                complexity_score += 2
            elif term.category in ["AI Automation", "Competitive Strategy"]:
                complexity_score += 3
            
            # Assign to complexity level
            if complexity_score <= 2:
                complexity_levels["Basic"].append(term)
            elif complexity_score <= 4:
                complexity_levels["Intermediate"].append(term)
            elif complexity_score <= 6:
                complexity_levels["Advanced"].append(term)
            else:
                complexity_levels["Expert"].append(term)
        
        for level, terms in complexity_levels.items():
            if not terms:
                continue
                
            markdown += f"## {level} Level\n\n"
            markdown += f"**{len(terms)} terms** at this complexity level\n\n"
            
            for term in sorted(terms, key=lambda t: t.term):
                markdown += f"### {term.term}\n"
                markdown += f"*{term.category} - {term.context}*\n\n"
                markdown += f"{term.definition}\n\n"
                
                if term.related_terms:
                    markdown += f"**Related:** {', '.join(term.related_terms)}\n\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def project_by_stakeholder(self) -> str:
        """Project vocabulary by stakeholder dimension."""
        markdown = "# Vocabulary by Stakeholder\n\n"
        markdown += "**Projection Dimension:** Stakeholder-based organization\n"
        markdown += "**Purpose:** Organize terms by who uses them most\n\n"
        
        stakeholder_mapping = {
            "Developers": ["Reflective Architecture", "Domain-Driven Design", "Infrastructure"],
            "Architects": ["Core Framework", "Domain-Driven Design", "Governance"],
            "Product Managers": ["Core Framework", "Competitive Strategy", "Quality Assurance"],
            "DevOps Engineers": ["Infrastructure", "Quality Assurance", "Systematic Development"],
            "AI Engineers": ["AI Automation", "Core Framework", "Systematic Development"],
            "Business Stakeholders": ["Competitive Strategy", "Core Framework", "Quality Assurance"]
        }
        
        for stakeholder, relevant_categories in stakeholder_mapping.items():
            relevant_terms = []
            for term in self.vocabulary.values():
                if term.category in relevant_categories:
                    relevant_terms.append(term)
            
            if not relevant_terms:
                continue
                
            markdown += f"## {stakeholder}\n\n"
            markdown += f"**Relevant Categories:** {', '.join(relevant_categories)}\n"
            markdown += f"**{len(relevant_terms)} terms** relevant to this stakeholder\n\n"
            
            for term in sorted(relevant_terms, key=lambda t: t.term):
                markdown += f"### {term.term}\n"
                markdown += f"*{term.category}*\n\n"
                markdown += f"{term.definition}\n\n"
                
                if term.examples:
                    markdown += f"**Examples:**\n"
                    for example in term.examples:
                        markdown += f"- {example}\n"
                    markdown += "\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def project_by_implementation_phase(self) -> str:
        """Project vocabulary by implementation phase dimension."""
        markdown = "# Vocabulary by Implementation Phase\n\n"
        markdown += "**Projection Dimension:** Implementation phase organization\n"
        markdown += "**Purpose:** Organize terms by when they're needed in implementation\n\n"
        
        phase_mapping = {
            "Foundation Phase": ["Core Framework", "Reflective Architecture"],
            "Design Phase": ["Domain-Driven Design", "Quality Assurance"],
            "Development Phase": ["Systematic Development", "Infrastructure"],
            "AI Integration Phase": ["AI Automation", "Core Framework"],
            "Deployment Phase": ["Infrastructure", "Quality Assurance"],
            "Competitive Phase": ["Competitive Strategy", "Governance"]
        }
        
        for phase, relevant_categories in phase_mapping.items():
            relevant_terms = []
            for term in self.vocabulary.values():
                if term.category in relevant_categories:
                    relevant_terms.append(term)
            
            if not relevant_terms:
                continue
                
            markdown += f"## {phase}\n\n"
            markdown += f"**Relevant Categories:** {', '.join(relevant_categories)}\n"
            markdown += f"**{len(relevant_terms)} terms** needed in this phase\n\n"
            
            for term in sorted(relevant_terms, key=lambda t: t.term):
                markdown += f"### {term.term}\n"
                markdown += f"*{term.category} - {term.context}*\n\n"
                markdown += f"{term.definition}\n\n"
                
                if term.related_terms:
                    markdown += f"**Related:** {', '.join(term.related_terms)}\n\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def project_by_domain_boundary(self) -> str:
        """Project vocabulary by domain boundary dimension."""
        markdown = "# Vocabulary by Domain Boundary\n\n"
        markdown += "**Projection Dimension:** Domain boundary organization\n"
        markdown += "**Purpose:** Organize terms by their domain boundaries and contexts\n\n"
        
        domain_boundaries = {
            "Core Domain": ["Core Framework", "Reflective Architecture"],
            "Supporting Domain": ["Infrastructure", "Quality Assurance"],
            "Generic Domain": ["Domain-Driven Design", "Systematic Development"],
            "AI Domain": ["AI Automation"],
            "Strategic Domain": ["Competitive Strategy", "Governance"]
        }
        
        for boundary, relevant_categories in domain_boundaries.items():
            relevant_terms = []
            for term in self.vocabulary.values():
                if term.category in relevant_categories:
                    relevant_terms.append(term)
            
            if not relevant_terms:
                continue
                
            markdown += f"## {boundary}\n\n"
            markdown += f"**Relevant Categories:** {', '.join(relevant_categories)}\n"
            markdown += f"**{len(relevant_terms)} terms** in this domain boundary\n\n"
            
            for term in sorted(relevant_terms, key=lambda t: t.term):
                markdown += f"### {term.term}\n"
                markdown += f"*{term.category} - {term.context}*\n\n"
                markdown += f"{term.definition}\n\n"
                
                if term.related_terms:
                    markdown += f"**Related:** {', '.join(term.related_terms)}\n\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def generate_all_projections(self) -> None:
        """Generate all vocabulary projections."""
        print("🔍 Generating multi-dimensional vocabulary projections...")
        
        projections = {
            "by_category": self.project_by_category(),
            "by_context": self.project_by_context(),
            "by_alphabetical": self.project_by_alphabetical(),
            "by_relationships": self.project_by_relationships(),
            "by_complexity": self.project_by_complexity(),
            "by_stakeholder": self.project_by_stakeholder(),
            "by_implementation_phase": self.project_by_implementation_phase(),
            "by_domain_boundary": self.project_by_domain_boundary()
        }
        
        for dimension, content in projections.items():
            filename = f"vocabulary_{dimension}.md"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"✅ Generated: {filepath}")
        
        # Generate index
        self._generate_projection_index(projections)
    
    def _generate_projection_index(self, projections: Dict[str, str]) -> None:
        """Generate index of all projections."""
        markdown = "# Multi-Dimensional Vocabulary Projections\n\n"
        markdown += "**Generated:** 2025-01-27\n"
        markdown += "**Purpose:** Multiple perspectives on ubiquitous language vocabulary\n\n"
        markdown += "This directory contains the ubiquitous language vocabulary projected across multiple dimensions to provide different perspectives and organizational structures.\n\n"
        
        markdown += "## Available Projections\n\n"
        
        projection_descriptions = {
            "by_category": "Groups terms by their primary functional category (Core Framework, DDD, etc.)",
            "by_context": "Organizes terms by their usage context and domain",
            "by_alphabetical": "Alphabetical listing for quick reference lookup",
            "by_relationships": "Shows how terms connect and relate to each other",
            "by_complexity": "Organizes terms from simple to complex concepts",
            "by_stakeholder": "Groups terms by who uses them most (Developers, Architects, etc.)",
            "by_implementation_phase": "Organizes terms by when they're needed in implementation",
            "by_domain_boundary": "Groups terms by their domain boundaries and contexts"
        }
        
        for dimension, description in projection_descriptions.items():
            filename = f"vocabulary_{dimension}.md"
            markdown += f"### [{dimension.replace('_', ' ').title()}]({filename})\n"
            markdown += f"{description}\n\n"
        
        # Save index
        index_path = self.output_dir / "README.md"
        with open(index_path, 'w') as f:
            f.write(markdown)
        
        print(f"✅ Generated projection index: {index_path}")

def main():
    """Generate multi-dimensional vocabulary projections."""
    projector = MultiDimensionalVocabularyProjector()
    
    print("📚 Loading vocabulary...")
    projector.load_vocabulary()
    
    if not projector.vocabulary:
        print("❌ No vocabulary loaded. Exiting.")
        return
    
    print("🎯 Generating projections...")
    projector.generate_all_projections()
    
    print(f"\n✅ All projections generated in: {projector.output_dir}")

if __name__ == "__main__":
    main()
