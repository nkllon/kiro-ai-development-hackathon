#!/usr/bin/env python3
"""
File Organization Cleanup - Systematic file organization and cleanup.

This script organizes files into proper directories, removes temporary files,
and creates a clean project structure suitable for public release.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class FileOperation:
    """Represents a file operation to be performed."""
    operation: str  # move, delete, archive
    source_path: str
    target_path: str = ""
    reason: str = ""
    size_mb: float = 0.0

class FileOrganizationCleanup:
    """Handles systematic file organization and cleanup."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.operations: List[FileOperation] = []
        
        # Create archive directory for moved files
        self.archive_dir = self.project_root / "archive"
        
        # Files and directories to delete completely
        self.delete_patterns = [
            # Temporary and cache files
            r".*\.DS_Store$",
            r".*\.log$",
            r".*\.pid$",
            r".*\.cache$",
            r".*\.tmp$",
            r".*\.temp$",
            
            # Backup files
            r".*\.backup.*$",
            r".*\.bak$",
            r".*\.security_backup$",
            
            # Database files (should use Docker volumes)
            r".*\.db$",
            r".*\.sqlite.*$",
            r".*\.db-shm$",
            r".*\.db-wal$",
            
            # Build artifacts
            r".*/__pycache__/.*",
            r".*\.pyc$",
            r".*\.pyo$",
            r".*\.egg-info/.*",
            
            # Screenshots and timestamped images in root
            r"^[^/]*_\d{10,}\.png$",
            r"^[^/]*_\d{8}_\d{6}\.png$",
            r"^screenshot_.*\.png$",
            r"^after_.*\.png$",
            r"^before_.*\.png$",
            r"^current_.*\.png$",
            r"^page_.*\.png$",
            
            # Large backup and deployment directories
            r"^.*backup.*/$",
            r"^.*_backup_.*/$",
            r"^\.repair_backups.*/$",
            r"^migration_backups/$",
            r"^docker-migration-backup.*/$",
            r"^observatory_backup.*/$",
            r"^poe_deployment.*/$",
            r"^vonnegut_deployment_package/$",
            r"^vonnegut_container_deployment/$",
            r"^vonnegut_deployment/$",
            
            # Node modules (can be reinstalled)
            r"^node_modules/$",
            
            # Deployment volatile data
            r"deployment/.*/prometheus-data/.*",
            r"deployment/.*/grafana-data/.*",
            r"deployment/.*/logs/.*"
        ]
        
        # Directories to archive (move to archive/)
        self.archive_patterns = [
            r"^scripts-archive/$",
            r"^assessment-results/$",
            r"^audit_reports/$",
            r"^reports/$",
            r"^logs/$",
            r"^empirical_data/$",
            r"^validation_evidence/$",
            r"^test_evidence/$",
            r"^metrics_data/$",
            r"^beast_mode_metrics/$",
            r"^parallel_execution_logs/$",
            r"^cloudflare_parallel_logs/$",
            r"^kiro_outputs/$",
            r"^investigation/$",
            r"^learning_patterns/$",
            r"^patterns/$",
            r"^demo_project/$",
            r"^demo_spores/$",
            r"^spores/$",
            r"^hackathons/$",
            r"^brownfield_analysis/$",
            r"^ontology/$"
        ]
        
        # Files to move to appropriate directories
        self.move_patterns = {
            # Root level files that should be in scripts/
            r"^[^/]*\.py$": "scripts/",
            r"^[^/]*\.sh$": "scripts/",
            
            # Configuration files
            r"^[^/]*-config\..*$": "config/",
            r"^[^/]*\.conf$": "config/",
            r"^prometheus.*\.yml$": "config/",
            r"^.*-config\.yml$": "config/",
            r"^.*-config\.yaml$": "config/",
            
            # Documentation files
            r"^[^/]*\.md$": "docs/",
            r"^.*\.pdf$": "docs/assets/",
            
            # Data files
            r"^[^/]*\.json$": "data/",
            r"^[^/]*\.jsonl$": "data/",
            
            # Docker files
            r"^docker-compose.*\.yml$": "deployment/",
            r"^Dockerfile.*$": "deployment/"
        }
        
        # Essential files to keep in root
        self.keep_in_root = {
            "README.md", "LICENSE", "Makefile", "pyproject.toml", 
            "requirements.txt", ".gitignore", ".env.example",
            "docker-compose.yml", "Dockerfile"
        }

    def get_file_size_mb(self, path: Path) -> float:
        """Get file size in MB."""
        try:
            if path.is_file():
                return path.stat().st_size / (1024 * 1024)
            elif path.is_dir():
                total_size = 0
                for item in path.rglob("*"):
                    if item.is_file():
                        try:
                            total_size += item.stat().st_size
                        except (OSError, PermissionError):
                            continue
                return total_size / (1024 * 1024)
        except (OSError, PermissionError):
            return 0.0
        return 0.0

    def should_delete(self, path: Path) -> bool:
        """Check if file/directory should be deleted."""
        relative_path = str(path.relative_to(self.project_root))
        
        for pattern in self.delete_patterns:
            if re.match(pattern, relative_path):
                return True
        return False

    def should_archive(self, path: Path) -> bool:
        """Check if directory should be archived."""
        relative_path = str(path.relative_to(self.project_root))
        
        for pattern in self.archive_patterns:
            if re.match(pattern, relative_path):
                return True
        return False

    def get_move_target(self, path: Path) -> str:
        """Get target directory for file that should be moved."""
        relative_path = str(path.relative_to(self.project_root))
        
        # Don't move essential files
        if path.name in self.keep_in_root:
            return ""
        
        for pattern, target_dir in self.move_patterns.items():
            if re.match(pattern, relative_path):
                return target_dir
        
        return ""

    def plan_operations(self) -> None:
        """Plan all file operations."""
        print("📋 Planning file operations...")
        
        # Get all top-level items
        for item in self.project_root.iterdir():
            if item.name.startswith('.git'):
                continue  # Skip .git directory
            
            relative_path = str(item.relative_to(self.project_root))
            size_mb = self.get_file_size_mb(item)
            
            # Check what to do with this item
            if self.should_delete(item):
                self.operations.append(FileOperation(
                    operation="delete",
                    source_path=relative_path,
                    reason="Temporary/cache/backup file",
                    size_mb=size_mb
                ))
            elif self.should_archive(item):
                target_path = f"archive/{item.name}"
                self.operations.append(FileOperation(
                    operation="archive",
                    source_path=relative_path,
                    target_path=target_path,
                    reason="Development artifact",
                    size_mb=size_mb
                ))
            else:
                # Check if file should be moved
                move_target = self.get_move_target(item)
                if move_target and item.is_file():
                    target_path = f"{move_target}{item.name}"
                    self.operations.append(FileOperation(
                        operation="move",
                        source_path=relative_path,
                        target_path=target_path,
                        reason="Better organization",
                        size_mb=size_mb
                    ))

    def execute_operations(self) -> Dict:
        """Execute all planned operations."""
        print("🔧 Executing file operations...")
        
        # Create necessary directories
        self.archive_dir.mkdir(exist_ok=True)
        (self.project_root / "config").mkdir(exist_ok=True)
        (self.project_root / "data").mkdir(exist_ok=True)
        (self.project_root / "deployment").mkdir(exist_ok=True)
        
        executed = {"delete": 0, "archive": 0, "move": 0}
        total_size_freed = 0.0
        
        for operation in self.operations:
            source_path = self.project_root / operation.source_path
            
            try:
                if operation.operation == "delete":
                    if source_path.exists():
                        if source_path.is_dir():
                            shutil.rmtree(source_path)
                        else:
                            source_path.unlink()
                        print(f"   🗑️  Deleted: {operation.source_path}")
                        executed["delete"] += 1
                        total_size_freed += operation.size_mb
                
                elif operation.operation == "archive":
                    if source_path.exists():
                        target_path = self.project_root / operation.target_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        if source_path.is_dir():
                            shutil.move(str(source_path), str(target_path))
                        else:
                            shutil.move(str(source_path), str(target_path))
                        
                        print(f"   📦 Archived: {operation.source_path} -> {operation.target_path}")
                        executed["archive"] += 1
                
                elif operation.operation == "move":
                    if source_path.exists():
                        target_path = self.project_root / operation.target_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Check if target already exists
                        if target_path.exists():
                            print(f"   ⚠️  Target exists, skipping: {operation.target_path}")
                        else:
                            shutil.move(str(source_path), str(target_path))
                            print(f"   📁 Moved: {operation.source_path} -> {operation.target_path}")
                            executed["move"] += 1
                            
            except (OSError, PermissionError) as e:
                print(f"   ❌ Failed to {operation.operation} {operation.source_path}: {e}")
        
        return {
            "operations_executed": executed,
            "total_size_freed_mb": total_size_freed,
            "operations_planned": len(self.operations)
        }

    def create_project_structure_doc(self) -> None:
        """Create documentation of the new project structure."""
        structure_doc = """# Project Structure

This document describes the organized structure of the Beast Mode AI Development Framework.

## Root Directory
```
kiro-ai-development-hackathon/
├── README.md                   # Main project documentation
├── LICENSE                     # Project license
├── pyproject.toml             # Python project configuration
├── requirements.txt           # Python dependencies
├── Makefile                   # Build and development commands
├── .gitignore                 # Git ignore patterns
├── .env.example              # Environment variables template
├── docker-compose.yml        # Docker composition (if present)
└── Dockerfile               # Docker configuration (if present)
```

## Source Code (`src/`)
All source code is organized in the `src/` directory with clear module separation:

- `src/beast_mode/` - Core Beast Mode framework
- `src/rm_ddd/` - Reflective Module DDD implementation
- `src/ai_memory_palace/` - AI Memory Palace system
- `src/dag_orchestration/` - DAG orchestration system
- `src/cms_platform/` - CMS platform implementation
- And other specialized modules...

## Examples (`examples/`)
Working examples and demonstrations:

- `examples/notebook/` - Jupyter notebook examples
- `examples/*.py` - Python example scripts
- Each example includes documentation and usage instructions

## Documentation (`docs/`)
Comprehensive documentation:

- `docs/README.md` - Documentation index
- `docs/api/` - API documentation
- `docs/guides/` - User guides and tutorials
- `docs/architecture/` - Architecture documentation

## Tests (`tests/`)
Test suite mirroring the source structure:

- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/fixtures/` - Test fixtures and data

## Configuration (`config/`)
Configuration files and templates:

- Configuration files for various services
- Environment-specific configurations
- Service configuration templates

## Data (`data/`)
Data files and datasets:

- Sample data for examples
- Configuration data
- Non-sensitive data files

## Deployment (`deployment/`)
Deployment configurations and scripts:

- Docker configurations
- Kubernetes manifests
- Deployment scripts and documentation

## Archive (`archive/`)
Archived development artifacts:

- Historical development files
- Backup directories
- Legacy code and experiments
- Assessment results and reports

## Kiro Configuration (`.kiro/`)
Kiro-specific configuration and specifications:

- `.kiro/specs/` - Feature specifications
- `.kiro/steering/` - AI assistant steering rules
- `.kiro/hooks/` - Agent automation hooks

## Scripts (`scripts/`)
Utility and automation scripts:

- Development and maintenance scripts
- Deployment automation
- Analysis and reporting tools
"""
        
        with open(self.project_root / "docs" / "PROJECT_STRUCTURE.md", 'w') as f:
            f.write(structure_doc)
        
        print("   📚 Created project structure documentation")

    def print_summary(self, results: Dict) -> None:
        """Print operation summary."""
        print("\n" + "="*60)
        print("🗂️  FILE ORGANIZATION SUMMARY")
        print("="*60)
        
        print(f"\n📊 Operations Executed:")
        print(f"   Files deleted: {results['operations_executed']['delete']}")
        print(f"   Items archived: {results['operations_executed']['archive']}")
        print(f"   Files moved: {results['operations_executed']['move']}")
        print(f"   Total operations planned: {results['operations_planned']}")
        
        print(f"\n💾 Space Optimization:")
        print(f"   Space freed: {results['total_size_freed_mb']:.1f} MB")
        
        # Show some examples of operations
        delete_ops = [op for op in self.operations if op.operation == "delete"]
        if delete_ops:
            print(f"\n🗑️  Examples of deleted items:")
            for op in delete_ops[:5]:
                print(f"   {op.source_path} ({op.size_mb:.1f} MB) - {op.reason}")
        
        archive_ops = [op for op in self.operations if op.operation == "archive"]
        if archive_ops:
            print(f"\n📦 Examples of archived items:")
            for op in archive_ops[:5]:
                print(f"   {op.source_path} -> {op.target_path}")
        
        move_ops = [op for op in self.operations if op.operation == "move"]
        if move_ops:
            print(f"\n📁 Examples of moved items:")
            for op in move_ops[:5]:
                print(f"   {op.source_path} -> {op.target_path}")
        
        print(f"\n✅ File organization completed successfully!")
        print("📝 Next steps:")
        print("   1. Review the new project structure")
        print("   2. Update any broken import paths")
        print("   3. Test that examples and scripts still work")
        print("   4. Update documentation with new structure")
        
        print("\n" + "="*60)

def main():
    """Main execution function."""
    print("🚀 Starting File Organization Cleanup...")
    
    organizer = FileOrganizationCleanup()
    
    # Plan operations
    organizer.plan_operations()
    
    # Execute operations
    results = organizer.execute_operations()
    
    # Create documentation
    print("\n📚 Creating project structure documentation...")
    organizer.create_project_structure_doc()
    
    # Print summary
    organizer.print_summary(results)
    
    # Save operation log
    operation_log = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "operations": [
            {
                "operation": op.operation,
                "source_path": op.source_path,
                "target_path": op.target_path,
                "reason": op.reason,
                "size_mb": op.size_mb
            }
            for op in organizer.operations
        ]
    }
    
    with open("file_organization_log.json", 'w') as f:
        json.dump(operation_log, f, indent=2)
    
    print(f"\n📄 Operation log saved to file_organization_log.json")
    
    return 0

if __name__ == "__main__":
    exit(main())