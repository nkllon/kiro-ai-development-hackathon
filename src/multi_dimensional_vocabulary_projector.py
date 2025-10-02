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
        """Load vocabulary from JSON file with enhanced error handling."""
        try:
            if not self.vocabulary_file.exists():
                raise error_handler.handle_file_error(
                    str(self.vocabulary_file), 
                    "vocabulary loading", 
                    FileNotFoundError(f"Vocabulary file not found: {self.vocabulary_file}")
                )
            
            with open(self.vocabulary_file, 'r') as f:
                data = json.load(f)
                
        except json.JSONDecodeError as e:
            raise error_handler.handle_validation_error(
                str(self.vocabulary_file),
                f"Invalid JSON format: {e}",
                e
            )
        except Exception as e:
            if isinstance(e, VocabularyProjectorError):
                raise
            raise error_handler.handle_file_error(
                str(self.vocabulary_file),
                "vocabulary loading",
                e
            )
            
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
        """Generate all vocabulary projections with enhanced error handling."""
        print("🔍 Generating multi-dimensional vocabulary projections...")
        
        failed_projections = []
        
        try:
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
        
        for dimension, projection_content in projections.items():
            try:
                filename = f"vocabulary_{dimension}.md"
                filepath = self.output_dir / filename
                
                # Ensure output directory exists
                self.output_dir.mkdir(parents=True, exist_ok=True)
                
                with open(filepath, 'w') as f:
                    f.write(projection_content)
                
                print(f"✅ Generated: {filepath}")
                
            except Exception as e:
                error = error_handler.handle_projection_error(dimension, e)
                failed_projections.append((dimension, error))
                print(f"❌ Failed to generate {dimension}: {error.message}")
                
                # Log suggestions
                if error.details.get("suggestions"):
                    for suggestion in error.details["suggestions"]:
                        print(f"   💡 {suggestion}")
        
        # Report any failures
        if failed_projections:
            print(f"\n⚠️  {len(failed_projections)} projections failed:")
            for dimension, error in failed_projections:
                print(f"   • {dimension}: {error.message}")
        
        except Exception as e:
            raise error_handler.handle_projection_error("all_projections", e)
        
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


import argparse
import sys
from typing import Optional, List

class VocabularyProjectorCLI:
    """Command-line interface for Multi-Dimensional Vocabulary Projector."""
    
    def __init__(self):
        self.projector = None
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Multi-Dimensional Vocabulary Projector",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s                                    # Generate all projections
  %(prog)s --vocabulary custom_vocab.json    # Use custom vocabulary
  %(prog)s --output-dir custom_output/       # Custom output directory
  %(prog)s --dimensions category context     # Generate specific projections
  %(prog)s --validate-only                   # Validate vocabulary without generating
  %(prog)s --batch vocab1.json vocab2.json  # Process multiple vocabularies
  %(prog)s --watch                           # Watch for changes and regenerate
            """
        )
        
        # Input options
        parser.add_argument(
            "--vocabulary", "-v",
            type=str,
            default="docs/ubiquitous_language_vocabulary.json",
            help="Path to vocabulary JSON file (default: docs/ubiquitous_language_vocabulary.json)"
        )
        
        parser.add_argument(
            "--output-dir", "-o",
            type=str,
            default="docs/vocabulary_projections",
            help="Output directory for projections (default: docs/vocabulary_projections)"
        )
        
        # Projection selection
        parser.add_argument(
            "--dimensions", "-d",
            nargs="+",
            choices=["category", "context", "alphabetical", "relationships", 
                    "complexity", "stakeholder", "implementation_phase", "domain_boundary"],
            help="Specific projection dimensions to generate (default: all)"
        )
        
        # Operation modes
        parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Validate vocabulary file without generating projections"
        )
        
        parser.add_argument(
            "--batch",
            nargs="+",
            help="Process multiple vocabulary files"
        )
        
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Watch vocabulary file for changes and regenerate automatically"
        )
        
        # Output options
        parser.add_argument(
            "--verbose", "-V",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--quiet", "-q",
            action="store_true",
            help="Suppress non-error output"
        )
        
        parser.add_argument(
            "--format",
            choices=["markdown", "html", "json"],
            default="markdown",
            help="Output format (default: markdown)"
        )
        
        return parser
    
    def validate_vocabulary(self, vocab_file: str) -> bool:
        """Validate vocabulary file."""
        try:
            projector = MultiDimensionalVocabularyProjector(vocab_file)
            projector.load_vocabulary()
            
            if not projector.vocabulary:
                print(f"❌ No vocabulary loaded from {vocab_file}")
                return False
            
            print(f"✅ Vocabulary validation passed: {len(projector.vocabulary)} terms")
            return True
            
        except Exception as e:
            print(f"❌ Vocabulary validation failed: {e}")
            return False
    
    def process_single_vocabulary(self, vocab_file: str, output_dir: str, 
                                dimensions: Optional[List[str]] = None) -> bool:
        """Process a single vocabulary file."""
        try:
            projector = MultiDimensionalVocabularyProjector(vocab_file)
            projector.output_dir = Path(output_dir)
            projector.output_dir.mkdir(parents=True, exist_ok=True)
            
            projector.load_vocabulary()
            
            if not projector.vocabulary:
                print(f"❌ No vocabulary loaded from {vocab_file}")
                return False
            
            if dimensions:
                # Generate specific dimensions
                print(f"📊 Generating {len(dimensions)} specific projections...")
                for dimension in dimensions:
                    method_name = f"project_by_{dimension}"
                    if hasattr(projector, method_name):
                        method = getattr(projector, method_name)
                        content = method()
                        
                        filename = f"vocabulary_by_{dimension}.md"
                        filepath = projector.output_dir / filename
                        
                        with open(filepath, 'w') as f:
                            f.write(content)
                        
                        print(f"✅ Generated: {filepath}")
                    else:
                        print(f"⚠️  Unknown dimension: {dimension}")
            else:
                # Generate all projections
                projector.generate_all_projections()
            
            return True
            
        except Exception as e:
            print(f"❌ Processing failed for {vocab_file}: {e}")
            return False
    
    def watch_mode(self, vocab_file: str, output_dir: str, dimensions: Optional[List[str]] = None):
        """Watch vocabulary file for changes."""
        import time
        import os
from datetime import datetime
        
        print(f"👁️  Watching {vocab_file} for changes...")
        print("Press Ctrl+C to stop")
        
        last_modified = 0
        
        try:
            while True:
                try:
                    current_modified = os.path.getmtime(vocab_file)
                    
                    if current_modified > last_modified:
                        print(f"🔄 Change detected in {vocab_file}")
                        if self.process_single_vocabulary(vocab_file, output_dir, dimensions):
                            print("✅ Projections updated")
                        else:
                            print("❌ Update failed")
                        
                        last_modified = current_modified
                    
                    time.sleep(1)  # Check every second
                    
                except FileNotFoundError:
                    print(f"⚠️  File not found: {vocab_file}")
                    time.sleep(5)  # Wait longer if file doesn't exist
                    
        except KeyboardInterrupt:
            print("\n👋 Watch mode stopped")
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run CLI interface."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Set up logging level
        if parsed_args.quiet:
            import logging
            logging.getLogger().setLevel(logging.ERROR)
        elif parsed_args.verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
        try:
            # Validate-only mode
            if parsed_args.validate_only:
                if parsed_args.batch:
                    success = all(self.validate_vocabulary(f) for f in parsed_args.batch)
                else:
                    success = self.validate_vocabulary(parsed_args.vocabulary)
                return 0 if success else 1
            
            # Batch processing mode
            if parsed_args.batch:
                print(f"📦 Processing {len(parsed_args.batch)} vocabulary files...")
                success_count = 0
                
                for vocab_file in parsed_args.batch:
                    print(f"\n🔄 Processing: {vocab_file}")
                    if self.process_single_vocabulary(vocab_file, parsed_args.output_dir, parsed_args.dimensions):
                        success_count += 1
                
                print(f"\n📊 Batch processing complete: {success_count}/{len(parsed_args.batch)} successful")
                return 0 if success_count == len(parsed_args.batch) else 1
            
            # Watch mode
            if parsed_args.watch:
                self.watch_mode(parsed_args.vocabulary, parsed_args.output_dir, parsed_args.dimensions)
                return 0
            
            # Standard processing
            return 0 if self.process_single_vocabulary(
                parsed_args.vocabulary, 
                parsed_args.output_dir, 
                parsed_args.dimensions
            ) else 1
            
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1

def main_cli():
    """CLI entry point."""
    cli = VocabularyProjectorCLI()
    return cli.run()


    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics."""
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "vocabulary_file": {
                "path": str(self.vocabulary_file),
                "exists": self.vocabulary_file.exists(),
                "size": self.vocabulary_file.stat().st_size if self.vocabulary_file.exists() else 0,
                "readable": os.access(self.vocabulary_file, os.R_OK) if self.vocabulary_file.exists() else False
            },
            "output_directory": {
                "path": str(self.output_dir),
                "exists": self.output_dir.exists(),
                "writable": os.access(self.output_dir, os.W_OK) if self.output_dir.exists() else False
            },
            "vocabulary_data": {
                "loaded": len(self.vocabulary) > 0,
                "term_count": len(self.vocabulary),
                "categories": list(set(term.category for term in self.vocabulary.values())) if self.vocabulary else []
            },
            "system": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd()
            }
        }
        
        return diagnostics
    
    def print_diagnostics(self):
        """Print diagnostic information."""
        diagnostics = self.run_diagnostics()
        
        print("🔍 Vocabulary Projector Diagnostics")
        print("=" * 40)
        
        # Vocabulary file info
        vocab_info = diagnostics["vocabulary_file"]
        print(f"📄 Vocabulary File:")
        print(f"   Path: {vocab_info['path']}")
        print(f"   Exists: {'✅' if vocab_info['exists'] else '❌'}")
        if vocab_info['exists']:
            print(f"   Size: {vocab_info['size']} bytes")
            print(f"   Readable: {'✅' if vocab_info['readable'] else '❌'}")
        
        # Output directory info
        output_info = diagnostics["output_directory"]
        print(f"\n📁 Output Directory:")
        print(f"   Path: {output_info['path']}")
        print(f"   Exists: {'✅' if output_info['exists'] else '❌'}")
        if output_info['exists']:
            print(f"   Writable: {'✅' if output_info['writable'] else '❌'}")
        
        # Vocabulary data info
        vocab_data = diagnostics["vocabulary_data"]
        print(f"\n📚 Vocabulary Data:")
        print(f"   Loaded: {'✅' if vocab_data['loaded'] else '❌'}")
        print(f"   Terms: {vocab_data['term_count']}")
        if vocab_data['categories']:
            print(f"   Categories: {', '.join(vocab_data['categories'])}")
        
        # System info
        system_info = diagnostics["system"]
        print(f"\n🖥️  System:")
        print(f"   Python: {system_info['python_version'].split()[0]}")
        print(f"   Platform: {system_info['platform']}")
        print(f"   Working Dir: {system_info['working_directory']}")
    
    def validate_system_health(self) -> bool:
        """Validate system health and readiness."""
        print("🏥 Checking system health...")
        
        issues = []
        
        try:
            # Check vocabulary file
            if not self.vocabulary_file.exists():
                issues.append(f"Vocabulary file not found: {self.vocabulary_file}")
            elif not os.access(self.vocabulary_file, os.R_OK):
                issues.append(f"Cannot read vocabulary file: {self.vocabulary_file}")
            
            # Check output directory
            if not self.output_dir.exists():
                try:
                    self.output_dir.mkdir(parents=True, exist_ok=True)
                    print("✅ Created output directory")
                except Exception as e:
                    issues.append(f"Cannot create output directory: {e}")
            elif not os.access(self.output_dir, os.W_OK):
                issues.append(f"Cannot write to output directory: {self.output_dir}")
            
            # Check vocabulary loading
            if not self.vocabulary:
                try:
                    self.load_vocabulary()
                    if not self.vocabulary:
                        issues.append("No vocabulary terms loaded")
                except Exception as e:
                    issues.append(f"Cannot load vocabulary: {e}")
            
            if issues:
                print("❌ System health check failed:")
                for issue in issues:
                    print(f"   • {issue}")
                return False
            else:
                print("✅ System health check passed")
                return True
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

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
    # Check if CLI arguments provided
    if len(sys.argv) > 1:
        sys.exit(main_cli())
    else:
        main()




# TODO: CLI implementation placeholder added during simulation


# TODO: CLI implementation placeholder added during simulation
