#!/usr/bin/env python3
"""
RC1 Migration Planner Agent
Beast Mode Full Compliance Execution

This agent designs comprehensive migration strategy using DAG structure
and content analysis to organize 256+ root directory files.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FileMigrationPlan:
    """Plan for migrating a single file"""
    source_path: str
    target_path: str
    category: str
    priority: int
    dependencies: List[str]
    estimated_size: int
    migration_reason: str
    backup_required: bool = True
    reference_updates_needed: bool = True


@dataclass
class DirectoryStructure:
    """Planned directory structure for organized documents"""
    base_path: str
    categories: Dict[str, str]
    subcategories: Dict[str, List[str]]
    total_files: int
    estimated_size: int


@dataclass
class MigrationStrategy:
    """Complete migration strategy"""
    strategy_id: str
    created_at: datetime
    total_files: int
    directory_structure: DirectoryStructure
    file_plans: List[FileMigrationPlan]
    execution_phases: List[str]
    rollback_plan: Dict[str, Any]
    validation_checks: List[str]


class MigrationPlannerAgent:
    """
    Migration Planner Agent - Beast Mode Execution
    
    Responsibilities:
    - Analyze current file distribution (256 in root)
    - Design organized directory structure
    - Create file movement mapping
    - Plan reference update strategy
    - Generate migration execution plan
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.docs_dir = self.project_root / "docs"
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        
        # Load existing analysis data
        self.scan_results = self._load_scan_results()
        self.content_analysis = self._load_content_analysis()
        self.dag_structure = self._load_dag_structure()
        
        logger.info("Migration Planner Agent initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Scan results loaded: {len(self.scan_results) if self.scan_results else 0} files")
    
    def _load_scan_results(self) -> Optional[Dict[str, Any]]:
        """Load scan results from JSON file"""
        try:
            scan_file = self.project_root / "rc1_scan_results.json"
            if scan_file.exists():
                with open(scan_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load scan results: {e}")
        return None
    
    def _load_content_analysis(self) -> Optional[Dict[str, Any]]:
        """Load content analysis from JSON file"""
        try:
            analysis_file = self.project_root / "rc1_content_analysis.json"
            if analysis_file.exists():
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load content analysis: {e}")
        return None
    
    def _load_dag_structure(self) -> Optional[Dict[str, Any]]:
        """Load DAG structure from JSON file"""
        try:
            dag_file = self.project_root / "rc1_dag_structure.json"
            if dag_file.exists():
                with open(dag_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load DAG structure: {e}")
        return None
    
    def analyze_root_files(self) -> List[Dict[str, Any]]:
        """Analyze files in root directory that need migration"""
        logger.info("Analyzing root directory files...")
        
        root_files = []
        root_path = self.project_root
        
        # Find all markdown files in root directory
        for file_path in root_path.glob("*.md"):
            if file_path.is_file():
                file_info = self._analyze_file(file_path)
                root_files.append(file_info)
        
        logger.info(f"Found {len(root_files)} markdown files in root directory")
        return root_files
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for migration planning"""
        try:
            stat = file_path.stat()
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Basic file analysis
            file_info = {
                'path': str(file_path),
                'name': file_path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'lines': len(content.splitlines()),
                'category': self._categorize_file(file_path.name, content),
                'priority': self._calculate_priority(file_path.name, content),
                'dependencies': self._extract_dependencies(content),
                'references': self._extract_references(content)
            }
            
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': 0,
                'category': 'unknown',
                'priority': 5,
                'dependencies': [],
                'references': []
            }
    
    def _categorize_file(self, filename: str, content: str) -> str:
        """Categorize file based on name and content patterns"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # RC1 files
        if any(pattern in filename_lower for pattern in ['rc1', 'migration', 'implementation']):
            return 'rc1'
        
        # README files
        if any(pattern in filename_lower for pattern in ['readme', 'setup', 'install', 'guide']):
            return 'readme'
        
        # Task files
        if any(pattern in filename_lower for pattern in ['task', 'todo', 'issue', 'bug']):
            return 'task'
        
        # Summary files
        if any(pattern in filename_lower for pattern in ['summary', 'report', 'analysis', 'complete']):
            return 'summary'
        
        # Beast Mode files
        if 'beast' in filename_lower or 'beast' in content_lower:
            return 'beast_mode'
        
        # Architecture files
        if any(pattern in filename_lower for pattern in ['arch', 'design', 'structure']):
            return 'architecture'
        
        # Default to other
        return 'other'
    
    def _calculate_priority(self, filename: str, content: str) -> int:
        """Calculate migration priority (1=highest, 5=lowest)"""
        filename_lower = filename.lower()
        
        # High priority files
        if any(pattern in filename_lower for pattern in ['rc1', 'migration', 'critical', 'urgent']):
            return 1
        
        # Medium-high priority
        if any(pattern in filename_lower for pattern in ['readme', 'setup', 'main']):
            return 2
        
        # Medium priority
        if any(pattern in filename_lower for pattern in ['task', 'issue', 'bug']):
            return 3
        
        # Lower priority
        if any(pattern in filename_lower for pattern in ['summary', 'report', 'analysis']):
            return 4
        
        # Default priority
        return 5
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract file dependencies from content"""
        dependencies = []
        
        # Look for markdown links
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for _, link in markdown_links:
            if link.endswith('.md'):
                dependencies.append(link)
        
        # Look for includes or references
        include_patterns = re.findall(r'(?:include|reference|see also)[:\s]+([^\n]+)', content, re.IGNORECASE)
        for pattern in include_patterns:
            if '.md' in pattern:
                dependencies.append(pattern.strip())
        
        return dependencies
    
    def _extract_references(self, content: str) -> List[str]:
        """Extract file references from content"""
        references = []
        
        # Look for file references
        file_refs = re.findall(r'([a-zA-Z0-9_-]+\.md)', content)
        references.extend(file_refs)
        
        # Look for path references
        path_refs = re.findall(r'([a-zA-Z0-9_/-]+\.md)', content)
        references.extend(path_refs)
        
        return list(set(references))  # Remove duplicates
    
    def design_directory_structure(self) -> DirectoryStructure:
        """Design organized directory structure for documents"""
        logger.info("Designing directory structure...")
        
        # Base structure
        base_path = str(self.docs_dir)
        
        categories = {
            'rc1': 'RC1 Implementation Documents',
            'readme': 'README and Setup Documents',
            'task': 'Task and Issue Documents',
            'summary': 'Summary and Report Documents',
            'beast_mode': 'Beast Mode Documents',
            'architecture': 'Architecture and Design Documents',
            'other': 'Other Documents'
        }
        
        subcategories = {
            'rc1': ['planning', 'implementation', 'analysis', 'reports'],
            'readme': ['project', 'component', 'setup'],
            'task': ['completed', 'in_progress', 'pending'],
            'summary': ['implementation', 'analysis', 'reports'],
            'beast_mode': ['execution', 'analysis', 'reports'],
            'architecture': ['design', 'patterns', 'diagrams'],
            'other': ['misc', 'archive', 'temp']
        }
        
        # Calculate totals
        root_files = self.analyze_root_files()
        total_files = len(root_files)
        estimated_size = sum(f.get('size', 0) for f in root_files)
        
        structure = DirectoryStructure(
            base_path=base_path,
            categories=categories,
            subcategories=subcategories,
            total_files=total_files,
            estimated_size=estimated_size
        )
        
        logger.info(f"Directory structure designed for {total_files} files")
        return structure
    
    def create_file_migration_plans(self) -> List[FileMigrationPlan]:
        """Create migration plans for all root files"""
        logger.info("Creating file migration plans...")
        
        root_files = self.analyze_root_files()
        directory_structure = self.design_directory_structure()
        file_plans = []
        
        for file_info in root_files:
            # Determine target path
            category = file_info['category']
            subcategory = self._determine_subcategory(file_info, directory_structure)
            
            target_path = self._build_target_path(
                directory_structure.base_path,
                category,
                subcategory,
                file_info['name']
            )
            
            # Create migration plan
            plan = FileMigrationPlan(
                source_path=file_info['path'],
                target_path=target_path,
                category=category,
                priority=file_info['priority'],
                dependencies=file_info['dependencies'],
                estimated_size=file_info['size'],
                migration_reason=f"Organize {category} document",
                backup_required=True,
                reference_updates_needed=len(file_info['references']) > 0
            )
            
            file_plans.append(plan)
        
        # Sort by priority
        file_plans.sort(key=lambda x: x.priority)
        
        logger.info(f"Created {len(file_plans)} file migration plans")
        return file_plans
    
    def _determine_subcategory(self, file_info: Dict[str, Any], structure: DirectoryStructure) -> str:
        """Determine appropriate subcategory for file"""
        category = file_info['category']
        filename = file_info['name'].lower()
        
        if category in structure.subcategories:
            subcats = structure.subcategories[category]
            
            # Try to match filename patterns to subcategories
            for subcat in subcats:
                if subcat in filename:
                    return subcat
            
            # Default to first subcategory
            return subcats[0]
        
        return 'misc'
    
    def _build_target_path(self, base_path: str, category: str, subcategory: str, filename: str) -> str:
        """Build target path for file migration"""
        return os.path.join(base_path, category, subcategory, filename)
    
    def generate_migration_strategy(self) -> MigrationStrategy:
        """Generate complete migration strategy"""
        logger.info("Generating migration strategy...")
        
        # Create components
        directory_structure = self.design_directory_structure()
        file_plans = self.create_file_migration_plans()
        
        # Define execution phases
        execution_phases = [
            "Phase 1: Create directory structure",
            "Phase 2: Backup existing files",
            "Phase 3: Execute file migration",
            "Phase 4: Update references and links",
            "Phase 5: Validate migration success",
            "Phase 6: Cleanup and optimization"
        ]
        
        # Create rollback plan
        rollback_plan = {
            "backup_location": str(self.migration_dir / "backups"),
            "restore_script": "restore_migration.py",
            "validation_script": "validate_rollback.py",
            "estimated_restore_time": "5-10 minutes"
        }
        
        # Define validation checks
        validation_checks = [
            "All files moved to correct locations",
            "Directory structure created correctly",
            "No broken internal links",
            "File integrity maintained",
            "References updated correctly",
            "System functionality preserved"
        ]
        
        strategy = MigrationStrategy(
            strategy_id=f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            created_at=datetime.now(),
            total_files=len(file_plans),
            directory_structure=directory_structure,
            file_plans=file_plans,
            execution_phases=execution_phases,
            rollback_plan=rollback_plan,
            validation_checks=validation_checks
        )
        
        logger.info(f"Migration strategy generated: {strategy.strategy_id}")
        return strategy
    
    def save_migration_strategy(self, strategy: MigrationStrategy) -> str:
        """Save migration strategy to file"""
        strategy_file = self.migration_dir / f"migration_strategy_{strategy.strategy_id}.json"
        
        # Convert to serializable format
        strategy_dict = asdict(strategy)
        strategy_dict['created_at'] = strategy.created_at.isoformat()
        
        with open(strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Migration strategy saved to: {strategy_file}")
        return str(strategy_file)
    
    def generate_execution_plan(self, strategy: MigrationStrategy) -> str:
        """Generate human-readable execution plan"""
        logger.info("Generating execution plan...")
        
        plan_content = f"""# RC1 Migration Execution Plan
## Strategy ID: {strategy.strategy_id}
## Generated: {strategy.created_at.strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- **Total Files**: {strategy.total_files}
- **Estimated Size**: {strategy.directory_structure.estimated_size:,} bytes
- **Categories**: {len(strategy.directory_structure.categories)}

## Directory Structure
"""
        
        for category, description in strategy.directory_structure.categories.items():
            plan_content += f"- **{category}**: {description}\n"
            if category in strategy.directory_structure.subcategories:
                for subcat in strategy.directory_structure.subcategories[category]:
                    plan_content += f"  - {subcat}/\n"
        
        plan_content += "\n## Execution Phases\n"
        for i, phase in enumerate(strategy.execution_phases, 1):
            plan_content += f"{i}. {phase}\n"
        
        plan_content += "\n## File Migration Plans\n"
        for plan in strategy.file_plans[:10]:  # Show first 10
            plan_content += f"- **{plan.source_path}** → **{plan.target_path}**\n"
            plan_content += f"  - Category: {plan.category}\n"
            plan_content += f"  - Priority: {plan.priority}\n"
            plan_content += f"  - Size: {plan.estimated_size:,} bytes\n"
            plan_content += f"  - Dependencies: {len(plan.dependencies)}\n"
            plan_content += f"  - References: {plan.reference_updates_needed}\n\n"
        
        if len(strategy.file_plans) > 10:
            plan_content += f"... and {len(strategy.file_plans) - 10} more files\n\n"
        
        plan_content += "\n## Validation Checks\n"
        for check in strategy.validation_checks:
            plan_content += f"- [ ] {check}\n"
        
        plan_content += f"\n## Rollback Plan\n"
        plan_content += f"- **Backup Location**: {strategy.rollback_plan['backup_location']}\n"
        plan_content += f"- **Restore Script**: {strategy.rollback_plan['restore_script']}\n"
        plan_content += f"- **Estimated Restore Time**: {strategy.rollback_plan['estimated_restore_time']}\n"
        
        # Save execution plan
        plan_file = self.migration_dir / f"execution_plan_{strategy.strategy_id}.md"
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        logger.info(f"Execution plan saved to: {plan_file}")
        return str(plan_file)


def main():
    """Main execution function for Migration Planner Agent"""
    print("🤖 RC1 Migration Planner Agent - Beast Mode Execution")
    print("=" * 60)
    
    # Initialize agent
    planner = MigrationPlannerAgent()
    
    # Generate migration strategy
    print("📊 Analyzing current state...")
    strategy = planner.generate_migration_strategy()
    
    # Save strategy
    print("💾 Saving migration strategy...")
    strategy_file = planner.save_migration_strategy(strategy)
    
    # Generate execution plan
    print("📋 Generating execution plan...")
    plan_file = planner.generate_execution_plan(strategy)
    
    # Report results
    print("\n✅ Migration Planner Agent Complete!")
    print(f"📁 Strategy file: {strategy_file}")
    print(f"📋 Execution plan: {plan_file}")
    print(f"📊 Total files to migrate: {strategy.total_files}")
    print(f"📂 Categories: {len(strategy.directory_structure.categories)}")
    print(f"🎯 Priority files: {len([p for p in strategy.file_plans if p.priority <= 2])}")
    
    return strategy


if __name__ == "__main__":
    main()
