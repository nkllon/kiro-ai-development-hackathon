#!/usr/bin/env python3
"""
Documentation Index Generator
============================

Creates comprehensive documentation indexes that work with GitHub's native navigation.
Generates organized directory structures and README files for easy browsing.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Make all 141+ markdown files discoverable through GitHub navigation
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass
class DocumentInfo:
    """Information about a markdown document."""
    path: Path
    title: str
    description: str
    category: str
    subcategory: str
    audience: List[str]
    status: str
    last_modified: datetime
    size: int
    word_count: int
    has_toc: bool
    has_examples: bool
    has_code: bool

class DocumentCategory(Enum):
    """Document categories for organization."""
    ARCHITECTURE = "Architecture"
    DESIGN = "Design"
    REQUIREMENTS = "Requirements"
    IMPLEMENTATION = "Implementation"
    API = "API Reference"
    GUIDES = "Guides"
    PROCEDURES = "Procedures"
    TESTING = "Testing"
    DEPLOYMENT = "Deployment"
    GOVERNANCE = "Governance"
    ONTOLOGY = "Ontology"
    VOCABULARY = "Vocabulary"
    DIAGRAMS = "Diagrams"
    EXAMPLES = "Examples"
    RESEARCH = "Research"
    TROUBLESHOOTING = "Troubleshooting"
    STANDARDS = "Standards"

class DocumentationIndexGenerator:
    """Generates comprehensive documentation indexes for GitHub navigation."""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root)
        self.docs_dir = self.repository_root / "docs"
        self.diagrams_dir = self.repository_root / "diagrams"
        self.document_index: Dict[str, DocumentInfo] = {}
        
    def discover_documents(self) -> Dict[str, DocumentInfo]:
        """Discover all markdown documents and extract metadata."""
        print("🔍 Discovering all markdown documents...")
        
        # Find all markdown files
        markdown_files = []
        for root, dirs, files in os.walk(self.repository_root):
            # Skip certain directories
            if any(skip in root for skip in ['.git', '.venv', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.md') and not file.startswith('.'):
                    markdown_files.append(Path(root) / file)
        
        print(f"📄 Found {len(markdown_files)} markdown files")
        
        # Process each file
        for file_path in markdown_files:
            try:
                doc_info = self._extract_document_info(file_path)
                if doc_info:
                    self.document_index[str(file_path)] = doc_info
            except Exception as e:
                print(f"⚠️  Error processing {file_path}: {e}")
        
        print(f"✅ Processed {len(self.document_index)} documents")
        return self.document_index
    
    def _extract_document_info(self, file_path: Path) -> Optional[DocumentInfo]:
        """Extract metadata from a markdown document."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file stats
            stat = file_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size
            
            # Extract title (first # heading)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file_path.stem.replace('_', ' ').title()
            
            # Extract description (first paragraph after title)
            description = self._extract_description(content)
            
            # Determine category based on path and content
            category, subcategory = self._categorize_document(file_path, content)
            
            # Determine audience
            audience = self._determine_audience(content, file_path)
            
            # Determine status
            status = self._determine_status(content, file_path)
            
            # Analyze content features
            has_toc = bool(re.search(r'## Table of Contents|## Contents|## TOC', content, re.IGNORECASE))
            has_examples = bool(re.search(r'```|## Examples|### Examples', content))
            has_code = bool(re.search(r'```(python|bash|javascript|typescript|yaml|json)', content))
            
            # Count words
            word_count = len(content.split())
            
            return DocumentInfo(
                path=file_path,
                title=title,
                description=description,
                category=category,
                subcategory=subcategory,
                audience=audience,
                status=status,
                last_modified=last_modified,
                size=size,
                word_count=word_count,
                has_toc=has_toc,
                has_examples=has_examples,
                has_code=has_code
            )
            
        except Exception as e:
            print(f"⚠️  Error extracting info from {file_path}: {e}")
            return None
    
    def _extract_description(self, content: str) -> str:
        """Extract description from markdown content."""
        # Look for description in frontmatter
        frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            desc_match = re.search(r'description:\s*["\']?([^"\']+)["\']?', frontmatter_match.group(1), re.IGNORECASE)
            if desc_match:
                return desc_match.group(1).strip()
        
        # Look for description after title
        lines = content.split('\n')
        in_description = False
        description_lines = []
        
        for line in lines:
            if line.startswith('# '):
                in_description = True
                continue
            elif line.startswith('##') or line.startswith('#'):
                break
            elif in_description and line.strip():
                description_lines.append(line.strip())
                if len(description_lines) >= 3:  # Limit to first few lines
                    break
        
        description = ' '.join(description_lines)
        return description[:200] + '...' if len(description) > 200 else description
    
    def _categorize_document(self, file_path: Path, content: str) -> Tuple[str, str]:
        """Categorize document based on path and content."""
        path_str = str(file_path).lower()
        
        # Determine category
        if 'design/' in path_str:
            category = DocumentCategory.DESIGN.value
        elif 'requirements/' in path_str:
            category = DocumentCategory.REQUIREMENTS.value
        elif 'implementation/' in path_str:
            category = DocumentCategory.IMPLEMENTATION.value
        elif 'api' in path_str or 'reference' in path_str:
            category = DocumentCategory.API.value
        elif 'guide' in path_str or 'tutorial' in path_str:
            category = DocumentCategory.GUIDES.value
        elif 'procedure' in path_str:
            category = DocumentCategory.PROCEDURES.value
        elif 'test' in path_str:
            category = DocumentCategory.TESTING.value
        elif 'deploy' in path_str:
            category = DocumentCategory.DEPLOYMENT.value
        elif 'governance' in path_str:
            category = DocumentCategory.GOVERNANCE.value
        elif 'ontology' in path_str or 'beastmaster' in path_str:
            category = DocumentCategory.ONTOLOGY.value
        elif 'vocabulary' in path_str:
            category = DocumentCategory.VOCABULARY.value
        elif 'diagram' in path_str:
            category = DocumentCategory.DIAGRAMS.value
        elif 'example' in path_str:
            category = DocumentCategory.EXAMPLES.value
        elif 'research' in path_str or 'analysis' in path_str:
            category = DocumentCategory.RESEARCH.value
        elif 'troubleshoot' in path_str or 'debug' in path_str:
            category = DocumentCategory.TROUBLESHOOTING.value
        elif 'standard' in path_str:
            category = DocumentCategory.STANDARDS.value
        else:
            category = DocumentCategory.ARCHITECTURE.value
        
        # Determine subcategory
        if 'design/' in path_str:
            subcategory = file_path.parts[-2] if len(file_path.parts) > 1 else 'General'
        elif 'requirements/' in path_str:
            subcategory = file_path.parts[-2] if len(file_path.parts) > 1 else 'General'
        else:
            subcategory = 'General'
        
        return category, subcategory
    
    def _determine_audience(self, content: str, file_path: Path) -> List[str]:
        """Determine target audience for the document."""
        audience = []
        content_lower = content.lower()
        path_lower = str(file_path).lower()
        
        if any(term in content_lower for term in ['developer', 'coding', 'implementation', 'code']):
            audience.append('Developers')
        if any(term in content_lower for term in ['architect', 'architecture', 'design', 'system']):
            audience.append('Architects')
        if any(term in content_lower for term in ['product', 'business', 'stakeholder', 'manager']):
            audience.append('Product Managers')
        if any(term in content_lower for term in ['devops', 'deployment', 'operations', 'infrastructure']):
            audience.append('DevOps Engineers')
        if any(term in content_lower for term in ['ai', 'ml', 'agent', 'intelligence']):
            audience.append('AI Engineers')
        if any(term in content_lower for term in ['user', 'end-user', 'interface', 'ui']):
            audience.append('End Users')
        
        # Default audience if none detected
        if not audience:
            if 'design/' in path_lower:
                audience = ['Architects', 'Developers']
            elif 'requirements/' in path_lower:
                audience = ['Product Managers', 'Architects']
            elif 'implementation/' in path_lower:
                audience = ['Developers']
            else:
                audience = ['All']
        
        return audience
    
    def _determine_status(self, content: str, file_path: Path) -> str:
        """Determine document status."""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['draft', 'wip', 'work in progress']):
            return 'Draft'
        elif any(term in content_lower for term in ['deprecated', 'obsolete', 'outdated']):
            return 'Deprecated'
        elif any(term in content_lower for term in ['stable', 'production', 'release']):
            return 'Stable'
        elif any(term in content_lower for term in ['beta', 'experimental', 'preview']):
            return 'Beta'
        else:
            return 'Active'
    
    def generate_category_indexes(self) -> None:
        """Generate README files for each category directory."""
        print("📚 Generating category indexes...")
        
        # Group documents by category
        categories = {}
        for doc in self.document_index.values():
            if doc.category not in categories:
                categories[doc.category] = []
            categories[doc.category].append(doc)
        
        # Generate index for each category
        for category, docs in categories.items():
            self._generate_category_readme(category, docs)
        
        # Generate main docs README
        self._generate_main_docs_readme(categories)
    
    def _generate_category_readme(self, category: str, docs: List[DocumentInfo]) -> None:
        """Generate README for a specific category."""
        # Create category directory if it doesn't exist
        category_dir = self.docs_dir / category.lower().replace(' ', '_')
        category_dir.mkdir(exist_ok=True)
        
        # Sort documents
        docs.sort(key=lambda d: (d.subcategory, d.title))
        
        # Generate README content
        readme_content = f"# {category} Documentation\n\n"
        readme_content += f"**{len(docs)} documents** in this category\n\n"
        
        # Group by subcategory
        subcategories = {}
        for doc in docs:
            if doc.subcategory not in subcategories:
                subcategories[doc.subcategory] = []
            subcategories[doc.subcategory].append(doc)
        
        for subcategory, subdocs in subcategories.items():
            if subcategory != 'General':
                readme_content += f"## {subcategory}\n\n"
            
            for doc in subdocs:
                # Calculate relative path
                rel_path = doc.path.relative_to(self.repository_root)
                
                readme_content += f"### [{doc.title}]({rel_path})\n"
                readme_content += f"*{doc.description}*\n\n"
                
                # Add metadata
                metadata = []
                if doc.audience:
                    metadata.append(f"**Audience:** {', '.join(doc.audience)}")
                if doc.status != 'Active':
                    metadata.append(f"**Status:** {doc.status}")
                if doc.has_examples:
                    metadata.append("**Has Examples**")
                if doc.has_code:
                    metadata.append("**Has Code**")
                if doc.word_count > 1000:
                    metadata.append(f"**Length:** {doc.word_count} words")
                
                if metadata:
                    readme_content += f"{' • '.join(metadata)}\n\n"
                
                readme_content += "---\n\n"
        
        # Save README
        readme_path = category_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Generated {category} index: {readme_path}")
    
    def _generate_main_docs_readme(self, categories: Dict[str, List[DocumentInfo]]) -> None:
        """Generate main docs README."""
        readme_content = "# Documentation Index\n\n"
        readme_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        readme_content += f"**Total Documents:** {len(self.document_index)}\n\n"
        readme_content += "This directory contains comprehensive documentation for the Beast Mode Framework and RM-DDD SDK.\n\n"
        
        # Add quick navigation
        readme_content += "## 🚀 Quick Navigation\n\n"
        readme_content += "| Category | Documents | Description |\n"
        readme_content += "|----------|-----------|-------------|\n"
        
        for category, docs in sorted(categories.items()):
            category_dir = category.lower().replace(' ', '_')
            description = self._get_category_description(category)
            readme_content += f"| [{category}]({category_dir}/README.md) | {len(docs)} | {description} |\n"
        
        readme_content += "\n## 📋 All Documents\n\n"
        
        # List all documents by category
        for category, docs in sorted(categories.items()):
            readme_content += f"### {category} ({len(docs)} documents)\n\n"
            
            for doc in sorted(docs, key=lambda d: d.title):
                rel_path = doc.path.relative_to(self.repository_root)
                readme_content += f"- [{doc.title}]({rel_path}) - {doc.description}\n"
            
            readme_content += "\n"
        
        # Add statistics
        readme_content += "## 📊 Documentation Statistics\n\n"
        
        # Audience breakdown
        audience_count = {}
        for doc in self.document_index.values():
            for audience in doc.audience:
                audience_count[audience] = audience_count.get(audience, 0) + 1
        
        readme_content += "### By Audience\n"
        for audience, count in sorted(audience_count.items(), key=lambda x: x[1], reverse=True):
            readme_content += f"- **{audience}:** {count} documents\n"
        
        readme_content += "\n### By Status\n"
        status_count = {}
        for doc in self.document_index.values():
            status_count[doc.status] = status_count.get(doc.status, 0) + 1
        
        for status, count in sorted(status_count.items(), key=lambda x: x[1], reverse=True):
            readme_content += f"- **{status}:** {count} documents\n"
        
        # Save main README
        main_readme_path = self.docs_dir / "README.md"
        with open(main_readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Generated main docs index: {main_readme_path}")
    
    def _get_category_description(self, category: str) -> str:
        """Get description for a category."""
        descriptions = {
            "Architecture": "System architecture and design patterns",
            "Design": "Detailed design specifications and patterns",
            "Requirements": "Functional and non-functional requirements",
            "Implementation": "Implementation guides and examples",
            "API Reference": "API documentation and references",
            "Guides": "User guides and tutorials",
            "Procedures": "Operational procedures and workflows",
            "Testing": "Testing strategies and procedures",
            "Deployment": "Deployment guides and configurations",
            "Governance": "Governance frameworks and policies",
            "Ontology": "Semantic frameworks and ontologies",
            "Vocabulary": "Ubiquitous language and terminology",
            "Diagrams": "Architecture and system diagrams",
            "Examples": "Code examples and use cases",
            "Research": "Research findings and analysis",
            "Troubleshooting": "Debugging and troubleshooting guides",
            "Standards": "Coding and documentation standards"
        }
        return descriptions.get(category, "Documentation in this category")
    
    def generate_navigation_structure(self) -> None:
        """Generate navigation structure for GitHub browsing."""
        print("🗂️  Generating navigation structure...")
        
        # Create navigation directories
        nav_dirs = [
            "by-audience",
            "by-status", 
            "by-features",
            "recent-updates"
        ]
        
        for nav_dir in nav_dirs:
            nav_path = self.docs_dir / nav_dir
            nav_path.mkdir(exist_ok=True)
            self._generate_navigation_readme(nav_dir, nav_path)
    
    def _generate_navigation_readme(self, nav_type: str, nav_path: Path) -> None:
        """Generate navigation-specific README."""
        readme_content = f"# Documentation by {nav_type.replace('-', ' ').title()}\n\n"
        
        if nav_type == "by-audience":
            # Group by audience
            audience_groups = {}
            for doc in self.document_index.values():
                for audience in doc.audience:
                    if audience not in audience_groups:
                        audience_groups[audience] = []
                    audience_groups[audience].append(doc)
            
            for audience, docs in sorted(audience_groups.items()):
                readme_content += f"## {audience} ({len(docs)} documents)\n\n"
                for doc in sorted(docs, key=lambda d: d.title):
                    rel_path = doc.path.relative_to(self.repository_root)
                    readme_content += f"- [{doc.title}]({rel_path}) - {doc.description}\n"
                readme_content += "\n"
        
        elif nav_type == "by-status":
            # Group by status
            status_groups = {}
            for doc in self.document_index.values():
                if doc.status not in status_groups:
                    status_groups[doc.status] = []
                status_groups[doc.status].append(doc)
            
            for status, docs in sorted(status_groups.items()):
                readme_content += f"## {status} ({len(docs)} documents)\n\n"
                for doc in sorted(docs, key=lambda d: d.title):
                    rel_path = doc.path.relative_to(self.repository_root)
                    readme_content += f"- [{doc.title}]({rel_path}) - {doc.description}\n"
                readme_content += "\n"
        
        elif nav_type == "by-features":
            # Group by features
            feature_groups = {
                "Has Examples": [],
                "Has Code": [],
                "Has Table of Contents": [],
                "Long Documents (1000+ words)": [],
                "Short Documents (<500 words)": []
            }
            
            for doc in self.document_index.values():
                if doc.has_examples:
                    feature_groups["Has Examples"].append(doc)
                if doc.has_code:
                    feature_groups["Has Code"].append(doc)
                if doc.has_toc:
                    feature_groups["Has Table of Contents"].append(doc)
                if doc.word_count >= 1000:
                    feature_groups["Long Documents (1000+ words)"].append(doc)
                elif doc.word_count < 500:
                    feature_groups["Short Documents (<500 words)"].append(doc)
            
            for feature, docs in feature_groups.items():
                if docs:
                    readme_content += f"## {feature} ({len(docs)} documents)\n\n"
                    for doc in sorted(docs, key=lambda d: d.title):
                        rel_path = doc.path.relative_to(self.repository_root)
                        readme_content += f"- [{doc.title}]({rel_path}) - {doc.description}\n"
                    readme_content += "\n"
        
        elif nav_type == "recent-updates":
            # Sort by last modified
            recent_docs = sorted(self.document_index.values(), 
                               key=lambda d: d.last_modified, reverse=True)[:20]
            
            readme_content += "## Most Recently Updated Documents\n\n"
            for doc in recent_docs:
                rel_path = doc.path.relative_to(self.repository_root)
                date_str = doc.last_modified.strftime('%Y-%m-%d')
                readme_content += f"- [{doc.title}]({rel_path}) - *Updated {date_str}*\n"
                readme_content += f"  {doc.description}\n\n"
        
        # Save navigation README
        nav_readme_path = nav_path / "README.md"
        with open(nav_readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Generated {nav_type} navigation: {nav_readme_path}")

def main():
    """Generate comprehensive documentation index system."""
    generator = DocumentationIndexGenerator()
    
    print("🚀 Starting comprehensive documentation index generation...")
    
    # Discover all documents
    documents = generator.discover_documents()
    
    if not documents:
        print("❌ No documents found. Exiting.")
        return
    
    # Generate category indexes
    generator.generate_category_indexes()
    
    # Generate navigation structure
    generator.generate_navigation_structure()
    
    print(f"\n✅ Documentation index system generated!")
    print(f"📊 Total documents processed: {len(documents)}")
    print(f"📁 Check the docs/ directory for organized navigation")

if __name__ == "__main__":
    main()


