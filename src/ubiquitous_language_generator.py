#!/usr/bin/env python3
"""
Ubiquitous Language Generator
============================

Generates a comprehensive ubiquitous language vocabulary for the Beast Mode Framework
based on the project's ontology and domain analysis.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Create systematic vocabulary for domain-driven development
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class VocabularyTerm:
    """A vocabulary term in the ubiquitous language."""
    term: str
    definition: str
    category: str
    context: str
    related_terms: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)

class UbiquitousLanguageGenerator:
    """Generates comprehensive ubiquitous language vocabulary."""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root)
        self.vocabulary: Dict[str, VocabularyTerm] = {}
        
    def generate_vocabulary(self) -> Dict[str, VocabularyTerm]:
        """Generate comprehensive ubiquitous language vocabulary."""
        
        # Core Beast Mode Framework Terms
        self._add_core_framework_terms()
        
        # Reflective Module Architecture Terms
        self._add_reflective_module_terms()
        
        # Domain-Driven Design Terms
        self._add_ddd_terms()
        
        # PDCA and Systematic Development Terms
        self._add_pdca_terms()
        
        # Quality and Governance Terms
        self._add_quality_governance_terms()
        
        # AI and Automation Terms
        self._add_ai_automation_terms()
        
        # Infrastructure and Operations Terms
        self._add_infrastructure_terms()
        
        # Competitive and Strategic Terms
        self._add_competitive_terms()
        
        return self.vocabulary
    
    def _add_core_framework_terms(self):
        """Add core Beast Mode Framework terms."""
        
        terms = [
            VocabularyTerm(
                term="Beast Mode Framework",
                definition="A systematic development engine that transforms regular hackathons into structured domination through PDCA cycles, tool health management, and model-driven decision making.",
                category="Core Framework",
                context="The foundational systematic approach to development",
                related_terms=["PDCA Orchestrator", "Tool Health Manager", "Project Registry"],
                examples=["Beast Mode methodology", "Beast Mode systematic approach"]
            ),
            VocabularyTerm(
                term="Systematic Superiority",
                definition="Demonstrable performance advantages over ad-hoc approaches through measurable metrics and systematic validation.",
                category="Core Framework",
                context="The primary goal of Beast Mode methodology",
                related_terms=["Ad-hoc Approach", "Metrics Collection", "Comparative Analysis"],
                antonyms=["Ad-hoc Approach"]
            ),
            VocabularyTerm(
                term="Ad-hoc Approach",
                definition="Unstructured development methodology that relies on guesswork, workarounds, and reactive problem-solving without systematic planning or measurement.",
                category="Core Framework",
                context="The approach Beast Mode systematically replaces",
                related_terms=["Workaround", "Guesswork", "Reactive Development"],
                antonyms=["Systematic Superiority", "Beast Mode Framework"]
            ),
            VocabularyTerm(
                term="Fix Tools First",
                definition="Core principle of repairing actual problems systematically rather than implementing workarounds.",
                category="Core Framework",
                context="Primary principle of Beast Mode methodology",
                related_terms=["Systematic Repair", "Root Cause Analysis", "Tool Health"],
                antonyms=["Workaround"]
            ),
            VocabularyTerm(
                term="Model-Driven Intelligence",
                definition="Using project registry data and domain knowledge instead of guesswork for decision making.",
                category="Core Framework",
                context="Decision making approach in Beast Mode",
                related_terms=["Project Registry", "Domain Knowledge", "Intelligence Engine"],
                antonyms=["Guesswork"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def _add_reflective_module_terms(self):
        """Add Reflective Module Architecture terms."""
        
        terms = [
            VocabularyTerm(
                term="ReflectiveModule",
                definition="Base class for all modules that can discover their own capabilities, monitor their health, and adapt at runtime.",
                category="Reflective Architecture",
                context="Core architectural pattern",
                related_terms=["ModuleCapability", "ModuleHealth", "ModuleStatus"],
                examples=["ReflectiveModule base class", "ReflectiveModule pattern"]
            ),
            VocabularyTerm(
                term="ModuleCapability",
                definition="Enumeration of capabilities that a module can provide, enabling dynamic capability discovery.",
                category="Reflective Architecture",
                context="Module capability definition",
                related_terms=["ReflectiveModule", "Capability Discovery", "Module Interface"]
            ),
            VocabularyTerm(
                term="ModuleHealth",
                definition="Health status of a module including healthy, degraded, unhealthy, and unknown states.",
                category="Reflective Architecture",
                context="Module health monitoring",
                related_terms=["HealthStatus", "ModuleStatus", "Health Monitoring"]
            ),
            VocabularyTerm(
                term="ModuleStatus",
                definition="Operational status of a module including healthy, warning, error, and unknown states.",
                category="Reflective Architecture",
                context="Module operational status",
                related_terms=["ModuleHealth", "Status Monitoring", "Module State"]
            ),
            VocabularyTerm(
                term="Capability Discovery",
                definition="Process by which modules automatically discover and register their capabilities at runtime.",
                category="Reflective Architecture",
                context="Dynamic capability management",
                related_terms=["ReflectiveModule", "ModuleCapability", "Runtime Adaptation"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def _add_ddd_terms(self):
        """Add Domain-Driven Design terms."""
        
        terms = [
            VocabularyTerm(
                term="BoundedContext",
                definition="A boundary within which a particular domain model is defined and applicable.",
                category="Domain-Driven Design",
                context="Strategic design pattern",
                related_terms=["Domain Model", "Ubiquitous Language", "Context Map"],
                examples=["User Management BoundedContext", "Order Processing BoundedContext"]
            ),
            VocabularyTerm(
                term="Ubiquitous Language",
                definition="A common language used by all team members to connect all activities of the team with the software.",
                category="Domain-Driven Design",
                context="Team communication and modeling",
                related_terms=["Domain Expert", "BoundedContext", "Domain Model"]
            ),
            VocabularyTerm(
                term="AggregateRoot",
                definition="An entity that controls access to a set of related objects and ensures consistency within the aggregate boundary.",
                category="Domain-Driven Design",
                context="Tactical design pattern",
                related_terms=["Entity", "Value Object", "Domain Event"],
                examples=["Order AggregateRoot", "User AggregateRoot"]
            ),
            VocabularyTerm(
                term="DomainEvent",
                definition="An event that represents something significant that happened in the domain.",
                category="Domain-Driven Design",
                context="Event-driven architecture",
                related_terms=["AggregateRoot", "Event Sourcing", "Domain Service"]
            ),
            VocabularyTerm(
                term="DomainService",
                definition="A service that represents a domain concept that doesn't naturally fit as an entity or value object.",
                category="Domain-Driven Design",
                context="Domain logic organization",
                related_terms=["Domain Model", "Business Logic", "Stateless Service"]
            ),
            VocabularyTerm(
                term="ValueObject",
                definition="An object that is defined by its attributes rather than its identity and is immutable.",
                category="Domain-Driven Design",
                context="Tactical design pattern",
                related_terms=["Entity", "AggregateRoot", "Immutability"]
            ),
            VocabularyTerm(
                term="Entity",
                definition="An object that has a distinct identity that runs through time and different states.",
                category="Domain-Driven Design",
                context="Tactical design pattern",
                related_terms=["ValueObject", "AggregateRoot", "Identity"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def _add_pdca_terms(self):
        """Add PDCA and systematic development terms."""
        
        terms = [
            VocabularyTerm(
                term="PDCA Cycle",
                definition="Plan-Do-Check-Act cycle for continuous improvement and systematic problem solving.",
                category="Systematic Development",
                context="Continuous improvement methodology",
                related_terms=["Plan", "Do", "Check", "Act", "Continuous Improvement"]
            ),
            VocabularyTerm(
                term="Plan",
                definition="First phase of PDCA cycle where objectives and processes are established.",
                category="Systematic Development",
                context="PDCA cycle phase",
                related_terms=["PDCA Cycle", "Objectives", "Process Design"]
            ),
            VocabularyTerm(
                term="Do",
                definition="Second phase of PDCA cycle where the plan is implemented on a small scale.",
                category="Systematic Development",
                context="PDCA cycle phase",
                related_terms=["PDCA Cycle", "Implementation", "Pilot Testing"]
            ),
            VocabularyTerm(
                term="Check",
                definition="Third phase of PDCA cycle where results are measured and compared against expected outcomes.",
                category="Systematic Development",
                context="PDCA cycle phase",
                related_terms=["PDCA Cycle", "Measurement", "Validation", "Metrics"]
            ),
            VocabularyTerm(
                term="Act",
                definition="Fourth phase of PDCA cycle where improvements are standardized and next cycle is planned.",
                category="Systematic Development",
                context="PDCA cycle phase",
                related_terms=["PDCA Cycle", "Standardization", "Improvement"]
            ),
            VocabularyTerm(
                term="Root Cause Analysis",
                definition="Systematic process of identifying the underlying causes of problems rather than just symptoms.",
                category="Systematic Development",
                context="Problem solving methodology",
                related_terms=["Problem Solving", "Systematic Analysis", "Root Cause"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def _add_quality_governance_terms(self):
        """Add quality and governance terms."""
        
        terms = [
            VocabularyTerm(
                term="Quality Gate",
                definition="A checkpoint in the development process where quality criteria must be met before proceeding.",
                category="Quality Assurance",
                context="Quality control mechanism",
                related_terms=["Quality Criteria", "Validation", "Checkpoint"]
            ),
            VocabularyTerm(
                term="Validation",
                definition="Process of checking that something meets specified requirements and quality standards.",
                category="Quality Assurance",
                context="Quality assurance process",
                related_terms=["Quality Gate", "Requirements", "Verification"]
            ),
            VocabularyTerm(
                term="Compliance",
                definition="Adherence to established standards, rules, or requirements.",
                category="Quality Assurance",
                context="Standards adherence",
                related_terms=["Standards", "Requirements", "Adherence"]
            ),
            VocabularyTerm(
                term="Governance",
                definition="Framework of rules, practices, and processes used to direct and control an organization.",
                category="Governance",
                context="Organizational control",
                related_terms=["Framework", "Rules", "Control", "Management"]
            ),
            VocabularyTerm(
                term="Metrics",
                definition="Quantifiable measures used to track and assess performance, quality, or progress.",
                category="Quality Assurance",
                context="Performance measurement",
                related_terms=["Measurement", "Performance", "Assessment"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def _add_ai_automation_terms(self):
        """Add AI and automation terms."""
        
        terms = [
            VocabularyTerm(
                term="Ghostbusters Agent",
                definition="AI agent that specializes in identifying and resolving specific types of problems or tasks.",
                category="AI Automation",
                context="AI agent specialization",
                related_terms=["AI Agent", "Problem Resolution", "Specialization"]
            ),
            VocabularyTerm(
                term="AI Orchestration",
                definition="Coordination and management of multiple AI agents to work together on complex tasks.",
                category="AI Automation",
                context="AI coordination",
                related_terms=["AI Agent", "Coordination", "Task Management"]
            ),
            VocabularyTerm(
                term="Intelligence Engine",
                definition="Core system that processes domain knowledge and provides intelligent decision support.",
                category="AI Automation",
                context="AI decision support",
                related_terms=["Domain Knowledge", "Decision Support", "AI Processing"]
            ),
            VocabularyTerm(
                term="Model-Driven Decision",
                definition="Decision making process based on data models and domain knowledge rather than intuition.",
                category="AI Automation",
                context="AI-assisted decision making",
                related_terms=["Data Model", "Domain Knowledge", "Decision Making"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def _add_infrastructure_terms(self):
        """Add infrastructure and operations terms."""
        
        terms = [
            VocabularyTerm(
                term="Project Registry",
                definition="Centralized repository of project information, capabilities, and relationships.",
                category="Infrastructure",
                context="Project information management",
                related_terms=["Repository", "Project Information", "Centralized Storage"]
            ),
            VocabularyTerm(
                term="Health Monitoring",
                definition="Continuous monitoring of system and component health status.",
                category="Infrastructure",
                context="System monitoring",
                related_terms=["ModuleHealth", "Status Monitoring", "System Health"]
            ),
            VocabularyTerm(
                term="Service Interface",
                definition="Contract that defines how services interact with each other.",
                category="Infrastructure",
                context="Service communication",
                related_terms=["API", "Contract", "Service Communication"]
            ),
            VocabularyTerm(
                term="Deployment",
                definition="Process of making software available for use in a specific environment.",
                category="Infrastructure",
                context="Software delivery",
                related_terms=["Release", "Environment", "Software Delivery"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def _add_competitive_terms(self):
        """Add competitive and strategic terms."""
        
        terms = [
            VocabularyTerm(
                term="Competitive Intelligence",
                definition="Information about competitors and market conditions used for strategic decision making.",
                category="Competitive Strategy",
                context="Strategic planning",
                related_terms=["Market Analysis", "Competitor Analysis", "Strategic Planning"]
            ),
            VocabularyTerm(
                term="Market Domination",
                definition="Achieving superior market position through systematic competitive advantages.",
                category="Competitive Strategy",
                context="Competitive positioning",
                related_terms=["Competitive Advantage", "Market Position", "Superiority"]
            ),
            VocabularyTerm(
                term="Systematic Advantage",
                definition="Competitive advantage gained through systematic processes and methodologies.",
                category="Competitive Strategy",
                context="Competitive differentiation",
                related_terms=["Systematic Superiority", "Competitive Advantage", "Methodology"]
            )
        ]
        
        for term in terms:
            self.vocabulary[term.term] = term
    
    def generate_markdown_vocabulary(self) -> str:
        """Generate markdown documentation of the vocabulary."""
        
        markdown = "# Ubiquitous Language Vocabulary\n\n"
        markdown += "**Generated:** 2025-01-27\n"
        markdown += "**Purpose:** Systematic vocabulary for domain-driven development\n\n"
        markdown += "This document establishes the foundational vocabulary and conceptual framework for the Beast Mode Framework, ensuring consistent terminology across all stakeholders and providing a shared mental model for systematic development superiority.\n\n"
        
        # Group by category
        categories = {}
        for term in self.vocabulary.values():
            if term.category not in categories:
                categories[term.category] = []
            categories[term.category].append(term)
        
        # Generate sections for each category
        for category, terms in sorted(categories.items()):
            markdown += f"## {category}\n\n"
            
            for term in sorted(terms, key=lambda t: t.term):
                markdown += f"### {term.term}\n\n"
                markdown += f"**Definition:** {term.definition}\n\n"
                markdown += f"**Context:** {term.context}\n\n"
                
                if term.related_terms:
                    markdown += f"**Related Terms:** {', '.join(term.related_terms)}\n\n"
                
                if term.synonyms:
                    markdown += f"**Synonyms:** {', '.join(term.synonyms)}\n\n"
                
                if term.antonyms:
                    markdown += f"**Antonyms:** {', '.join(term.antonyms)}\n\n"
                
                if term.examples:
                    markdown += f"**Examples:**\n"
                    for example in term.examples:
                        markdown += f"- {example}\n"
                    markdown += "\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def generate_json_vocabulary(self) -> str:
        """Generate JSON representation of the vocabulary."""
        
        vocabulary_data = {}
        for term_name, term in self.vocabulary.items():
            vocabulary_data[term_name] = {
                "term": term.term,
                "definition": term.definition,
                "category": term.category,
                "context": term.context,
                "related_terms": term.related_terms,
                "examples": term.examples,
                "synonyms": term.synonyms,
                "antonyms": term.antonyms
            }
        
        return json.dumps(vocabulary_data, indent=2)

def main():
    """Generate ubiquitous language vocabulary."""
    generator = UbiquitousLanguageGenerator()
    
    print("🔍 Generating ubiquitous language vocabulary...")
    vocabulary = generator.generate_vocabulary()
    
    print(f"📚 Generated {len(vocabulary)} vocabulary terms")
    
    # Generate markdown documentation
    markdown_content = generator.generate_markdown_vocabulary()
    
    # Save markdown file
    output_file = Path("docs/ubiquitous_language_vocabulary.md")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(markdown_content)
    
    print(f"✅ Markdown vocabulary saved to: {output_file}")
    
    # Generate JSON vocabulary
    json_content = generator.generate_json_vocabulary()
    
    # Save JSON file
    json_file = Path("docs/ubiquitous_language_vocabulary.json")
    with open(json_file, 'w') as f:
        f.write(json_content)
    
    print(f"✅ JSON vocabulary saved to: {json_file}")
    
    # Print summary by category
    categories = {}
    for term in vocabulary.values():
        if term.category not in categories:
            categories[term.category] = 0
        categories[term.category] += 1
    
    print(f"\n📊 Vocabulary by category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} terms")

if __name__ == "__main__":
    main()


