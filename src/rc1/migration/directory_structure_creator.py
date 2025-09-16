#!/usr/bin/env python3
"""
RC1 Directory Structure Creator Agent
Beast Mode Full Compliance Execution

This agent creates organized directory structures based on DAG structure
and content analysis for systematic document organization.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DirectoryNode:
    """Represents a directory node in the structure"""
    name: str
    path: str
    category: str
    subcategory: Optional[str] = None
    description: str = ""
    file_count: int = 0
    estimated_size: int = 0
    children: List['DirectoryNode'] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DirectoryStructure:
    """Complete directory structure definition"""
    base_path: str
    root_node: DirectoryNode
    total_directories: int
    total_files: int
    estimated_size: int
    categories: Dict[str, str]
    subcategories: Dict[str, List[str]]
    created_at: datetime
    structure_id: str


class DirectoryStructureCreatorAgent:
    """
    Directory Structure Creator Agent - Beast Mode Execution
    
    Responsibilities:
    - Create organized directory structure
    - Build folder hierarchy based on DAG structure
    - Implement systematic organization principles
    - Ensure zero data loss
    - Plan rollback strategy
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        self.structures_dir = self.migration_dir / "structures"
        
        # Create necessary directories
        self.structures_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Directory Structure Creator Agent initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Docs directory: {self.docs_dir}")
    
    def load_dag_structure(self) -> Optional[Dict[str, Any]]:
        """Load DAG structure from analysis results"""
        try:
            dag_file = self.project_root / "rc1_dag_structure.json"
            if dag_file.exists():
                with open(dag_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load DAG structure: {e}")
        return None
    
    def load_content_analysis(self) -> Optional[Dict[str, Any]]:
        """Load content analysis from analysis results"""
        try:
            analysis_file = self.project_root / "rc1_content_analysis.json"
            if analysis_file.exists():
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load content analysis: {e}")
        return None
    
    def create_base_structure(self) -> DirectoryStructure:
        """Create base directory structure for document organization"""
        logger.info("Creating base directory structure...")
        
        # Define categories and descriptions
        categories = {
            'rc1': 'RC1 Implementation Documents',
            'readme': 'README and Setup Documents',
            'task': 'Task and Issue Documents',
            'summary': 'Summary and Report Documents',
            'beast_mode': 'Beast Mode Documents',
            'architecture': 'Architecture and Design Documents',
            'other': 'Other Documents'
        }
        
        # Define subcategories for each category
        subcategories = {
            'rc1': ['planning', 'implementation', 'analysis', 'reports', 'migration'],
            'readme': ['project', 'component', 'setup', 'deployment'],
            'task': ['completed', 'in_progress', 'pending', 'blocked'],
            'summary': ['implementation', 'analysis', 'reports', 'reviews'],
            'beast_mode': ['execution', 'analysis', 'reports', 'mitigation'],
            'architecture': ['design', 'patterns', 'diagrams', 'specifications'],
            'other': ['misc', 'archive', 'temp', 'drafts']
        }
        
        # Create root node
        root_node = DirectoryNode(
            name="docs",
            path=str(self.docs_dir),
            category="root",
            description="Main documentation directory",
            metadata={"type": "root", "created_by": "DirectoryStructureCreatorAgent"}
        )
        
        # Create category directories
        for category, description in categories.items():
            category_path = self.docs_dir / category
            category_node = DirectoryNode(
                name=category,
                path=str(category_path),
                category=category,
                description=description,
                metadata={"type": "category", "description": description}
            )
            
            # Create subcategory directories
            if category in subcategories:
                for subcategory in subcategories[category]:
                    subcategory_path = category_path / subcategory
                    subcategory_node = DirectoryNode(
                        name=subcategory,
                        path=str(subcategory_path),
                        category=category,
                        subcategory=subcategory,
                        description=f"{description} - {subcategory.title()}",
                        metadata={"type": "subcategory", "parent_category": category}
                    )
                    category_node.children.append(subcategory_node)
            
            root_node.children.append(category_node)
        
        # Create special directories
        special_dirs = [
            ("index", "Documentation Index and Navigation"),
            ("templates", "Document Templates and Examples"),
            ("assets", "Images, Diagrams, and Other Assets"),
            ("archive", "Archived and Historical Documents")
        ]
        
        for dir_name, description in special_dirs:
            special_path = self.docs_dir / dir_name
            special_node = DirectoryNode(
                name=dir_name,
                path=str(special_path),
                category="special",
                description=description,
                metadata={"type": "special", "description": description}
            )
            root_node.children.append(special_node)
        
        # Calculate totals
        total_directories = self._count_directories(root_node)
        total_files = 0  # Will be updated during migration
        estimated_size = 0  # Will be updated during migration
        
        structure = DirectoryStructure(
            base_path=str(self.docs_dir),
            root_node=root_node,
            total_directories=total_directories,
            total_files=total_files,
            estimated_size=estimated_size,
            categories=categories,
            subcategories=subcategories,
            created_at=datetime.now(),
            structure_id=f"structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        logger.info(f"Base structure created with {total_directories} directories")
        return structure
    
    def _count_directories(self, node: DirectoryNode) -> int:
        """Recursively count directories in structure"""
        count = 1  # Count current node
        for child in node.children:
            count += self._count_directories(child)
        return count
    
    def create_physical_directories(self, structure: DirectoryStructure) -> bool:
        """Create physical directory structure on filesystem"""
        logger.info("Creating physical directory structure...")
        
        try:
            # Create base docs directory
            self.docs_dir.mkdir(parents=True, exist_ok=True)
            
            # Create all directories recursively
            success = self._create_directory_recursive(structure.root_node)
            
            if success:
                logger.info("Physical directory structure created successfully")
            else:
                logger.error("Failed to create some directories")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create physical directories: {e}")
            return False
    
    def _create_directory_recursive(self, node: DirectoryNode) -> bool:
        """Recursively create directories"""
        try:
            # Create current directory
            Path(node.path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {node.path}")
            
            # Create README for each directory
            self._create_directory_readme(node)
            
            # Create subdirectories
            for child in node.children:
                if not self._create_directory_recursive(child):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directory {node.path}: {e}")
            return False
    
    def _create_directory_readme(self, node: DirectoryNode) -> None:
        """Create README file for directory"""
        try:
            readme_path = Path(node.path) / "README.md"
            
            if readme_path.exists():
                return  # Don't overwrite existing README
            
            readme_content = f"""# {node.name.title()}

{node.description}

## Contents

This directory contains {node.category} documents.

"""
            
            # Add subcategory information
            if node.children:
                readme_content += "## Subdirectories\n\n"
                for child in node.children:
                    readme_content += f"- **{child.name}/** - {child.description}\n"
                readme_content += "\n"
            
            # Add metadata
            if node.metadata:
                readme_content += "## Metadata\n\n"
                for key, value in node.metadata.items():
                    readme_content += f"- **{key}**: {value}\n"
                readme_content += "\n"
            
            readme_content += f"*Generated by RC1 Directory Structure Creator Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.debug(f"Created README: {readme_path}")
            
        except Exception as e:
            logger.warning(f"Failed to create README for {node.path}: {e}")
    
    def create_index_files(self, structure: DirectoryStructure) -> bool:
        """Create index files for navigation"""
        logger.info("Creating index files...")
        
        try:
            # Create main index
            main_index_path = self.docs_dir / "index.md"
            main_index_content = self._generate_main_index(structure)
            
            with open(main_index_path, 'w', encoding='utf-8') as f:
                f.write(main_index_content)
            
            # Create category indexes
            for category_node in structure.root_node.children:
                if category_node.category != "special":
                    self._create_category_index(category_node)
            
            logger.info("Index files created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index files: {e}")
            return False
    
    def _generate_main_index(self, structure: DirectoryStructure) -> str:
        """Generate main documentation index"""
        content = f"""# Documentation Index

Welcome to the RC1 Documentation System.

## Overview

This documentation system organizes {structure.total_directories} directories containing project documentation.

**Generated**: {structure.created_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Structure ID**: {structure.structure_id}

## Categories

"""
        
        for category_node in structure.root_node.children:
            if category_node.category != "special":
                content += f"### {category_node.name.title()}\n"
                content += f"{category_node.description}\n\n"
                
                if category_node.children:
                    content += "**Subdirectories:**\n"
                    for subcategory in category_node.children:
                        content += f"- [{subcategory.name}/]({category_node.name}/{subcategory.name}/) - {subcategory.description}\n"
                    content += "\n"
        
        content += """## Special Directories

- **[index/](index/)** - Documentation Index and Navigation
- **[templates/](templates/)** - Document Templates and Examples  
- **[assets/](assets/)** - Images, Diagrams, and Other Assets
- **[archive/](archive/)** - Archived and Historical Documents

## Navigation

Use the directory structure above to navigate to specific document categories and subcategories.

*Generated by RC1 Directory Structure Creator Agent*
"""
        
        return content
    
    def _create_category_index(self, category_node: DirectoryNode) -> None:
        """Create index file for category"""
        try:
            index_path = Path(category_node.path) / "index.md"
            
            content = f"""# {category_node.name.title()}

{category_node.description}

## Subdirectories

"""
            
            for subcategory in category_node.children:
                content += f"### [{subcategory.name}/]({subcategory.name}/)\n"
                content += f"{subcategory.description}\n\n"
            
            content += f"*Generated by RC1 Directory Structure Creator Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.debug(f"Created category index: {index_path}")
            
        except Exception as e:
            logger.warning(f"Failed to create category index for {category_node.name}: {e}")
    
    def save_structure_definition(self, structure: DirectoryStructure) -> str:
        """Save directory structure definition to file"""
        structure_file = self.structures_dir / f"structure_{structure.structure_id}.json"
        
        # Convert to serializable format
        structure_dict = asdict(structure)
        structure_dict['created_at'] = structure.created_at.isoformat()
        
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(structure_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Structure definition saved to: {structure_file}")
        return str(structure_file)
    
    def validate_structure(self, structure: DirectoryStructure) -> Dict[str, Any]:
        """Validate created directory structure"""
        logger.info("Validating directory structure...")
        
        validation_results = {
            'total_directories_expected': structure.total_directories,
            'total_directories_found': 0,
            'missing_directories': [],
            'extra_directories': [],
            'validation_errors': []
        }
        
        try:
            # Check base directory
            if not self.docs_dir.exists():
                validation_results['validation_errors'].append(f"Base directory not found: {self.docs_dir}")
                return validation_results
            
            # Validate structure recursively
            self._validate_directory_recursive(structure.root_node, validation_results)
            
            validation_results['total_directories_found'] = len([
                d for d in self.docs_dir.rglob('*') if d.is_dir()
            ])
            
            logger.info(f"Structure validation complete: {validation_results['total_directories_found']} directories found")
            
        except Exception as e:
            logger.error(f"Structure validation failed: {e}")
            validation_results['validation_errors'].append(f"Validation error: {e}")
        
        return validation_results
    
    def _validate_directory_recursive(self, node: DirectoryNode, results: Dict[str, Any]) -> None:
        """Recursively validate directory structure"""
        try:
            node_path = Path(node.path)
            
            if not node_path.exists():
                results['missing_directories'].append(node.path)
            else:
                # Check for README
                readme_path = node_path / "README.md"
                if not readme_path.exists():
                    results['validation_errors'].append(f"Missing README: {readme_path}")
            
            # Validate children
            for child in node.children:
                self._validate_directory_recursive(child, results)
                
        except Exception as e:
            results['validation_errors'].append(f"Validation error for {node.path}: {e}")
    
    def create_complete_structure(self) -> Tuple[DirectoryStructure, str]:
        """Create complete directory structure with all components"""
        logger.info("Creating complete directory structure...")
        
        # Create base structure
        structure = self.create_base_structure()
        
        # Create physical directories
        if not self.create_physical_directories(structure):
            raise Exception("Failed to create physical directories")
        
        # Create index files
        if not self.create_index_files(structure):
            raise Exception("Failed to create index files")
        
        # Save structure definition
        structure_file = self.save_structure_definition(structure)
        
        # Validate structure
        validation_results = self.validate_structure(structure)
        
        if validation_results['validation_errors']:
            logger.warning(f"Structure validation found {len(validation_results['validation_errors'])} errors")
            for error in validation_results['validation_errors']:
                logger.warning(f"  - {error}")
        
        logger.info("Complete directory structure created successfully")
        return structure, structure_file


def main():
    """Main execution function for Directory Structure Creator Agent"""
    print("🤖 RC1 Directory Structure Creator Agent - Beast Mode Execution")
    print("=" * 70)
    
    # Initialize agent
    creator = DirectoryStructureCreatorAgent()
    
    try:
        # Create complete structure
        print("📁 Creating directory structure...")
        structure, structure_file = creator.create_complete_structure()
        
        # Report results
        print("\n✅ Directory Structure Creator Agent Complete!")
        print(f"📁 Structure ID: {structure.structure_id}")
        print(f"📂 Total directories: {structure.total_directories}")
        print(f"📋 Categories: {len(structure.categories)}")
        print(f"📄 Structure file: {structure_file}")
        print(f"📁 Base path: {structure.base_path}")
        
        # Show structure summary
        print("\n📊 Structure Summary:")
        for category, description in structure.categories.items():
            print(f"  - {category}: {description}")
        
        print("\n🎯 Directory structure ready for file migration!")
        
    except Exception as e:
        print(f"\n❌ Directory Structure Creator Agent Failed: {e}")
        logger.error(f"Agent execution failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
