#!/usr/bin/env python3
"""
RC1 Link Reference Updater Agent
Beast Mode Full Compliance Execution

This agent updates all broken references and links after migration
to ensure zero broken links and maintain document relationships.
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ReferenceMatch:
    """Represents a found reference in a document"""
    file_path: str
    line_number: int
    original_text: str
    reference_type: str  # 'markdown_link', 'include', 'reference', 'path'
    target_file: str
    new_target_file: Optional[str] = None
    needs_update: bool = True
    confidence: float = 1.0


@dataclass
class ReferenceUpdate:
    """Represents an update to a reference"""
    file_path: str
    line_number: int
    original_text: str
    updated_text: str
    reference_type: str
    old_target: str
    new_target: str
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class ReferenceUpdateSummary:
    """Summary of reference updates performed"""
    total_files_scanned: int
    total_references_found: int
    total_references_updated: int
    total_references_failed: int
    broken_links_fixed: int
    update_errors: List[str]
    warnings: List[str]
    execution_time: float


class LinkReferenceUpdaterAgent:
    """
    Link Reference Updater Agent - Beast Mode Execution
    
    Responsibilities:
    - Scan all documents for references
    - Update internal links to new locations
    - Fix cross-references between documents
    - Validate link integrity
    - Update navigation structures
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        self.logs_dir = self.migration_dir / "logs"
        
        # Create necessary directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Reference patterns
        self.reference_patterns = {
            'markdown_link': r'\[([^\]]+)\]\(([^)]+)\)',
            'include': r'(?:include|reference|see also)[:\s]+([^\n]+)',
            'path_reference': r'([a-zA-Z0-9_/-]+\.md)',
            'relative_path': r'\.\.?/[a-zA-Z0-9_/-]+\.md',
            'absolute_path': r'/[a-zA-Z0-9_/-]+\.md'
        }
        
        # File mapping for migration
        self.file_mapping: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}
        
        # Update tracking
        self.reference_matches: List[ReferenceMatch] = []
        self.reference_updates: List[ReferenceUpdate] = []
        self.update_errors: List[str] = []
        self.warnings: List[str] = []
        
        logger.info("Link Reference Updater Agent initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Docs directory: {self.docs_dir}")
    
    def load_migration_strategy(self, strategy_file: str) -> Dict[str, Any]:
        """Load migration strategy to understand file movements"""
        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
            
            # Build file mapping
            for plan in strategy.get('file_plans', []):
                source_path = plan['source_path']
                target_path = plan['target_path']
                self.file_mapping[source_path] = target_path
                self.reverse_mapping[target_path] = source_path
            
            logger.info(f"Loaded migration strategy with {len(self.file_mapping)} file mappings")
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to load migration strategy: {e}")
            raise
    
    def scan_document_references(self, file_path: str) -> List[ReferenceMatch]:
        """Scan a single document for references"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            references = []
            
            for line_num, line in enumerate(lines, 1):
                # Check each reference pattern
                for ref_type, pattern in self.reference_patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    
                    for match in matches:
                        if ref_type == 'markdown_link':
                            # Extract link text and URL
                            link_text = match.group(1)
                            link_url = match.group(2)
                            
                            # Check if it's a markdown file reference
                            if link_url.endswith('.md') or '.md#' in link_url:
                                target_file = self._extract_target_file(link_url)
                                if target_file:
                                    references.append(ReferenceMatch(
                                        file_path=file_path,
                                        line_number=line_num,
                                        original_text=match.group(0),
                                        reference_type=ref_type,
                                        target_file=target_file,
                                        needs_update=self._needs_update(target_file)
                                    ))
                        
                        elif ref_type in ['include', 'path_reference']:
                            # Extract file reference
                            target_file = match.group(1).strip()
                            if target_file.endswith('.md'):
                                references.append(ReferenceMatch(
                                    file_path=file_path,
                                    line_number=line_num,
                                    original_text=match.group(0),
                                    reference_type=ref_type,
                                    target_file=target_file,
                                    needs_update=self._needs_update(target_file)
                                ))
                        
                        elif ref_type in ['relative_path', 'absolute_path']:
                            # Extract path reference
                            target_file = match.group(0)
                            if target_file.endswith('.md'):
                                references.append(ReferenceMatch(
                                    file_path=file_path,
                                    line_number=line_num,
                                    original_text=match.group(0),
                                    reference_type=ref_type,
                                    target_file=target_file,
                                    needs_update=self._needs_update(target_file)
                                ))
            
            return references
            
        except Exception as e:
            logger.error(f"Failed to scan references in {file_path}: {e}")
            return []
    
    def _extract_target_file(self, link_url: str) -> Optional[str]:
        """Extract target file from link URL"""
        # Remove anchors
        if '#' in link_url:
            link_url = link_url.split('#')[0]
        
        # Remove query parameters
        if '?' in link_url:
            link_url = link_url.split('?')[0]
        
        # Return if it's a markdown file
        if link_url.endswith('.md'):
            return link_url
        
        return None
    
    def _needs_update(self, target_file: str) -> bool:
        """Check if a target file needs reference update"""
        # Check if target file was moved
        for old_path, new_path in self.file_mapping.items():
            if target_file in old_path or old_path in target_file:
                return True
        
        # Check if it's a relative reference that might be broken
        if target_file.startswith('./') or target_file.startswith('../'):
            return True
        
        return False
    
    def find_new_target_path(self, old_target: str, source_file: str) -> Optional[str]:
        """Find new target path for a reference"""
        # Direct mapping
        if old_target in self.file_mapping:
            return self.file_mapping[old_target]
        
        # Check for partial matches
        for old_path, new_path in self.file_mapping.items():
            if old_target in old_path:
                # Calculate relative path from source to new target
                source_path = Path(source_file)
                target_path = Path(new_path)
                
                try:
                    relative_path = os.path.relpath(target_path, source_path.parent)
                    return relative_path
                except ValueError:
                    # Paths on different drives, use absolute path
                    return str(target_path)
        
        # Check if target file exists in new structure
        target_name = Path(old_target).name
        for new_path in self.file_mapping.values():
            if Path(new_path).name == target_name:
                source_path = Path(source_file)
                target_path = Path(new_path)
                
                try:
                    relative_path = os.path.relpath(target_path, source_path.parent)
                    return relative_path
                except ValueError:
                    return str(target_path)
        
        return None
    
    def update_reference(self, reference: ReferenceMatch) -> ReferenceUpdate:
        """Update a single reference"""
        try:
            new_target = self.find_new_target_path(reference.target_file, reference.file_path)
            
            if not new_target:
                return ReferenceUpdate(
                    file_path=reference.file_path,
                    line_number=reference.line_number,
                    original_text=reference.original_text,
                    updated_text=reference.original_text,
                    reference_type=reference.reference_type,
                    old_target=reference.target_file,
                    new_target="",
                    success=False,
                    error_message="Could not find new target path"
                )
            
            # Generate updated text based on reference type
            updated_text = self._generate_updated_text(
                reference.original_text,
                reference.reference_type,
                reference.target_file,
                new_target
            )
            
            return ReferenceUpdate(
                file_path=reference.file_path,
                line_number=reference.line_number,
                original_text=reference.original_text,
                updated_text=updated_text,
                reference_type=reference.reference_type,
                old_target=reference.target_file,
                new_target=new_target,
                success=True
            )
            
        except Exception as e:
            return ReferenceUpdate(
                file_path=reference.file_path,
                line_number=reference.line_number,
                original_text=reference.original_text,
                updated_text=reference.original_text,
                reference_type=reference.reference_type,
                old_target=reference.target_file,
                new_target="",
                success=False,
                error_message=str(e)
            )
    
    def _generate_updated_text(self, original_text: str, ref_type: str, old_target: str, new_target: str) -> str:
        """Generate updated text for a reference"""
        if ref_type == 'markdown_link':
            # Update markdown link: [text](old_path) -> [text](new_path)
            return re.sub(r'\[([^\]]+)\]\([^)]+\)', rf'[\1]({new_target})', original_text)
        
        elif ref_type in ['include', 'path_reference']:
            # Update include/reference: old_path -> new_path
            return original_text.replace(old_target, new_target)
        
        elif ref_type in ['relative_path', 'absolute_path']:
            # Update path reference
            return original_text.replace(old_target, new_target)
        
        return original_text
    
    def apply_reference_updates(self, updates: List[ReferenceUpdate]) -> bool:
        """Apply reference updates to files"""
        logger.info(f"Applying {len(updates)} reference updates...")
        
        # Group updates by file
        file_updates = {}
        for update in updates:
            if update.file_path not in file_updates:
                file_updates[update.file_path] = []
            file_updates[update.file_path].append(update)
        
        success_count = 0
        error_count = 0
        
        for file_path, file_update_list in file_updates.items():
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Apply updates (sort by line number descending to avoid offset issues)
                file_update_list.sort(key=lambda x: x.line_number, reverse=True)
                
                for update in file_update_list:
                    if update.success and update.line_number <= len(lines):
                        # Update the line
                        lines[update.line_number - 1] = lines[update.line_number - 1].replace(
                            update.original_text, update.updated_text
                        )
                        success_count += 1
                    else:
                        error_count += 1
                        self.update_errors.append(f"Failed to update {file_path}:{update.line_number}")
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                logger.info(f"Updated {len(file_update_list)} references in {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to update references in {file_path}: {e}")
                error_count += len(file_update_list)
                self.update_errors.append(f"Failed to update {file_path}: {e}")
        
        logger.info(f"Reference updates applied: {success_count} successful, {error_count} failed")
        return error_count == 0
    
    def scan_all_documents(self) -> List[ReferenceMatch]:
        """Scan all documents for references"""
        logger.info("Scanning all documents for references...")
        
        all_references = []
        scanned_files = 0
        
        # Scan all markdown files in docs directory
        for md_file in self.docs_dir.rglob("*.md"):
            if md_file.is_file():
                references = self.scan_document_references(str(md_file))
                all_references.extend(references)
                scanned_files += 1
        
        # Also scan any remaining markdown files in project root
        for md_file in self.project_root.glob("*.md"):
            if md_file.is_file():
                references = self.scan_document_references(str(md_file))
                all_references.extend(references)
                scanned_files += 1
        
        self.reference_matches = all_references
        
        logger.info(f"Scanned {scanned_files} files, found {len(all_references)} references")
        return all_references
    
    def update_all_references(self, strategy_file: str) -> ReferenceUpdateSummary:
        """Update all references based on migration strategy"""
        start_time = datetime.now()
        
        logger.info("Starting reference update process...")
        
        # Load migration strategy
        self.load_migration_strategy(strategy_file)
        
        # Scan all documents
        references = self.scan_all_documents()
        
        # Filter references that need updates
        references_to_update = [ref for ref in references if ref.needs_update]
        
        logger.info(f"Found {len(references_to_update)} references that need updates")
        
        # Update references
        updates = []
        for reference in references_to_update:
            update = self.update_reference(reference)
            updates.append(update)
        
        # Apply updates
        success = self.apply_reference_updates(updates)
        
        # Calculate summary
        execution_time = (datetime.now() - start_time).total_seconds()
        
        summary = ReferenceUpdateSummary(
            total_files_scanned=len(set(ref.file_path for ref in references)),
            total_references_found=len(references),
            total_references_updated=len([u for u in updates if u.success]),
            total_references_failed=len([u for u in updates if not u.success]),
            broken_links_fixed=len([u for u in updates if u.success]),
            update_errors=self.update_errors,
            warnings=self.warnings,
            execution_time=execution_time
        )
        
        # Save update results
        self.save_update_results(summary, updates)
        
        logger.info(f"Reference update completed in {execution_time:.2f}s")
        return summary
    
    def save_update_results(self, summary: ReferenceUpdateSummary, updates: List[ReferenceUpdate]) -> str:
        """Save reference update results to file"""
        results_file = self.logs_dir / f"reference_updates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Prepare results data
        results_data = {
            'summary': asdict(summary),
            'updates': [asdict(update) for update in updates],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Reference update results saved to: {results_file}")
        return str(results_file)
    
    def validate_links(self) -> Dict[str, Any]:
        """Validate that all links are working after updates"""
        logger.info("Validating links after updates...")
        
        validation_results = {
            'total_links_checked': 0,
            'working_links': 0,
            'broken_links': 0,
            'broken_link_details': []
        }
        
        # Re-scan all documents
        references = self.scan_all_documents()
        
        for reference in references:
            validation_results['total_links_checked'] += 1
            
            # Check if target file exists
            target_path = self._resolve_target_path(reference.target_file, reference.file_path)
            
            if target_path and Path(target_path).exists():
                validation_results['working_links'] += 1
            else:
                validation_results['broken_links'] += 1
                validation_results['broken_link_details'].append({
                    'file': reference.file_path,
                    'line': reference.line_number,
                    'target': reference.target_file,
                    'resolved_path': target_path
                })
        
        logger.info(f"Link validation complete: {validation_results['working_links']} working, {validation_results['broken_links']} broken")
        return validation_results
    
    def _resolve_target_path(self, target_file: str, source_file: str) -> Optional[str]:
        """Resolve target file path relative to source file"""
        try:
            source_path = Path(source_file)
            
            if target_file.startswith('/'):
                # Absolute path
                return target_file
            elif target_file.startswith('./') or target_file.startswith('../'):
                # Relative path
                return str(source_path.parent / target_file)
            else:
                # Simple filename or relative path
                return str(source_path.parent / target_file)
        except Exception:
            return None


def main():
    """Main execution function for Link Reference Updater Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RC1 Link Reference Updater Agent')
    parser.add_argument('--strategy-file', required=True, help='Path to migration strategy file')
    parser.add_argument('--scan-only', action='store_true', help='Only scan for references, do not update')
    parser.add_argument('--validate', action='store_true', help='Validate links after updates')
    
    args = parser.parse_args()
    
    print("🤖 RC1 Link Reference Updater Agent - Beast Mode Execution")
    print("=" * 70)
    
    # Initialize agent
    updater = LinkReferenceUpdaterAgent()
    
    if args.scan_only:
        print(f"🔍 Scanning references in documents...")
        references = updater.scan_all_documents()
        
        print(f"\n📊 Scan Results:")
        print(f"  - Total references found: {len(references)}")
        print(f"  - References needing updates: {len([r for r in references if r.needs_update])}")
        
        # Show some examples
        print(f"\n📋 Sample References:")
        for ref in references[:10]:
            print(f"  - {ref.file_path}:{ref.line_number} - {ref.reference_type} - {ref.target_file}")
        
        return
    
    if args.validate:
        print(f"🔍 Validating links...")
        results = updater.validate_links()
        
        print(f"\n📊 Validation Results:")
        print(f"  - Total links checked: {results['total_links_checked']}")
        print(f"  - Working links: {results['working_links']}")
        print(f"  - Broken links: {results['broken_links']}")
        
        if results['broken_link_details']:
            print(f"\n❌ Broken Links:")
            for detail in results['broken_link_details'][:5]:
                print(f"  - {detail['file']}:{detail['line']} -> {detail['target']}")
        
        return
    
    # Update references
    print(f"📁 Strategy file: {args.strategy_file}")
    
    summary = updater.update_all_references(args.strategy_file)
    
    # Report results
    print("\n✅ Link Reference Updater Agent Complete!")
    print(f"📊 Files scanned: {summary.total_files_scanned}")
    print(f"🔗 References found: {summary.total_references_found}")
    print(f"✅ References updated: {summary.total_references_updated}")
    print(f"❌ References failed: {summary.total_references_failed}")
    print(f"🔧 Broken links fixed: {summary.broken_links_fixed}")
    print(f"⏱️  Execution time: {summary.execution_time:.2f}s")
    
    if summary.update_errors:
        print(f"\n❌ Update Errors ({len(summary.update_errors)}):")
        for error in summary.update_errors[:5]:
            print(f"  - {error}")
        if len(summary.update_errors) > 5:
            print(f"  ... and {len(summary.update_errors) - 5} more errors")
    
    if summary.warnings:
        print(f"\n⚠️  Warnings ({len(summary.warnings)}):")
        for warning in summary.warnings[:5]:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()

