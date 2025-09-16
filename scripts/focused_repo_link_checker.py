#!/usr/bin/env python3
"""
Focused Repository Link Checker
Only checks current files, not backups, and handles different link types properly
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedRepoLinkChecker:
    """Focused link checker for current repository files only"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.results = {
            'broken_links': [],
            'total_files': 0,
            'total_links': 0,
            'valid_links': 0
        }
    
    def check_current_files(self) -> Dict[str, any]:
        """Check links in current files only (not backups)"""
        logger.info("🔍 Checking links in current files...")
        
        # Find current files (exclude backup directories)
        current_files = self._find_current_files()
        logger.info(f"Found {len(current_files)} current files to check")
        
        broken_links = []
        total_links = 0
        valid_links = 0
        
        for file_path in current_files:
            file_results = self._check_file_links(file_path)
            broken_links.extend(file_results['broken_links'])
            total_links += file_results['total_links']
            valid_links += file_results['valid_links']
        
        return {
            'broken_links': broken_links,
            'total_links': total_links,
            'valid_links': valid_links,
            'total_files': len(current_files),
            'method': 'focused_current_files'
        }
    
    def _find_current_files(self) -> List[Path]:
        """Find current files, excluding backups and temporary files"""
        current_files = []
        
        # File patterns to check
        patterns = ['*.md', '*.html', '*.json', '*.yaml', '*.yml', '*.py', '*.txt']
        
        for pattern in patterns:
            files = list(self.repo_root.rglob(pattern))
            
            for file_path in files:
                if self._is_current_file(file_path):
                    current_files.append(file_path)
        
        return current_files
    
    def _is_current_file(self, file_path: Path) -> bool:
        """Check if file is a current file (not backup/temp)"""
        # Skip backup directories
        skip_dirs = {
            'migration_backups', 'backups', '__pycache__', '.git', 
            'node_modules', '.venv', 'venv', 'env', '.env', 
            'build', 'dist', '.pytest_cache', 'logs'
        }
        
        # Check if any parent directory is in skip list
        for part in file_path.parts:
            if part in skip_dirs:
                return False
        
        # Skip very large files
        try:
            if file_path.stat().st_size > 5 * 1024 * 1024:  # 5MB
                return False
        except:
            return False
        
        # Skip files in root that are likely temporary
        if file_path.parent == self.repo_root:
            if file_path.name.startswith('temp_') or file_path.name.startswith('tmp_'):
                return False
        
        return True
    
    def _check_file_links(self, file_path: Path) -> Dict[str, any]:
        """Check links in a single file"""
        broken_links = []
        total_links = 0
        valid_links = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check different link types based on file extension
            if file_path.suffix == '.md':
                md_results = self._check_markdown_links(content, file_path)
                broken_links.extend(md_results['broken_links'])
                total_links += md_results['total_links']
                valid_links += md_results['valid_links']
            
            elif file_path.suffix == '.html':
                html_results = self._check_html_links(content, file_path)
                broken_links.extend(html_results['broken_links'])
                total_links += html_results['total_links']
                valid_links += html_results['valid_links']
            
            elif file_path.suffix in ['.json', '.yaml', '.yml']:
                json_results = self._check_json_yaml_links(content, file_path)
                broken_links.extend(json_results['broken_links'])
                total_links += json_results['total_links']
                valid_links += json_results['valid_links']
            
            elif file_path.suffix == '.py':
                py_results = self._check_python_links(content, file_path)
                broken_links.extend(py_results['broken_links'])
                total_links += py_results['total_links']
                valid_links += py_results['valid_links']
        
        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")
        
        return {
            'broken_links': broken_links,
            'total_links': total_links,
            'valid_links': valid_links
        }
    
    def _check_markdown_links(self, content: str, file_path: Path) -> Dict[str, any]:
        """Check markdown links"""
        broken_links = []
        total_links = 0
        valid_links = 0
        
        # Markdown link pattern: [text](link)
        md_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(md_pattern, content)
        
        for text, link in matches:
            total_links += 1
            link_result = self._check_single_link(link, file_path, text)
            
            if link_result['is_broken']:
                broken_links.append(link_result)
            else:
                valid_links += 1
        
        return {
            'broken_links': broken_links,
            'total_links': total_links,
            'valid_links': valid_links
        }
    
    def _check_html_links(self, content: str, file_path: Path) -> Dict[str, any]:
        """Check HTML links"""
        broken_links = []
        total_links = 0
        valid_links = 0
        
        # HTML href pattern
        href_pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(href_pattern, content)
        
        for link in matches:
            total_links += 1
            link_result = self._check_single_link(link, file_path)
            
            if link_result['is_broken']:
                broken_links.append(link_result)
            else:
                valid_links += 1
        
        return {
            'broken_links': broken_links,
            'total_links': total_links,
            'valid_links': valid_links
        }
    
    def _check_json_yaml_links(self, content: str, file_path: Path) -> Dict[str, any]:
        """Check JSON/YAML file references"""
        broken_links = []
        total_links = 0
        valid_links = 0
        
        # Look for file paths in JSON/YAML
        file_path_pattern = r'"(/[^"]+\.(?:md|html|py|json|yaml|yml))"'
        matches = re.findall(file_path_pattern, content)
        
        for link in matches:
            total_links += 1
            link_result = self._check_single_link(link, file_path)
            
            if link_result['is_broken']:
                broken_links.append(link_result)
            else:
                valid_links += 1
        
        return {
            'broken_links': broken_links,
            'total_links': total_links,
            'valid_links': valid_links
        }
    
    def _check_python_links(self, content: str, file_path: Path) -> Dict[str, any]:
        """Check Python file references"""
        broken_links = []
        total_links = 0
        valid_links = 0
        
        # Look for file paths in Python strings
        file_path_pattern = r'["\']([^"\']+\.(?:md|html|py|json|yaml|yml))["\']'
        matches = re.findall(file_path_pattern, content)
        
        for link in matches:
            # Skip if it looks like a module import
            if '.' in link and not link.startswith('/') and not link.startswith('./'):
                continue
            
            total_links += 1
            link_result = self._check_single_link(link, file_path)
            
            if link_result['is_broken']:
                broken_links.append(link_result)
            else:
                valid_links += 1
        
        return {
            'broken_links': broken_links,
            'total_links': total_links,
            'valid_links': valid_links
        }
    
    def _check_single_link(self, link: str, source_file: Path, text: str = None) -> Dict[str, any]:
        """Check a single link"""
        result = {
            'file': str(source_file),
            'link': link,
            'text': text,
            'is_broken': False,
            'error_type': None,
            'error_message': None
        }
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(link)
            
            # Handle different link types
            if parsed.scheme in ['http', 'https']:
                # External URL - skip for now to avoid rate limiting
                result['is_broken'] = False
                result['error_type'] = 'external_skipped'
                result['error_message'] = 'External URL (not checked to avoid rate limiting)'
            
            elif parsed.scheme in ['mailto', 'tel', 'ftp']:
                # Other schemes - assume valid
                result['is_broken'] = False
                result['error_type'] = 'other_scheme'
                result['error_message'] = f'Other scheme: {parsed.scheme}'
            
            elif link.startswith('#'):
                # Anchor link - check if target exists in same file
                result['is_broken'] = not self._check_anchor_link(link, source_file)
                if result['is_broken']:
                    result['error_type'] = 'anchor_not_found'
                    result['error_message'] = f'Anchor not found: {link}'
            
            elif parsed.scheme == '' or parsed.scheme == 'file':
                # Local file path
                if link.startswith('/'):
                    # Absolute path
                    target_path = Path(link)
                else:
                    # Relative path
                    target_path = source_file.parent / link
                
                # Resolve path
                target_path = target_path.resolve()
                
                if not target_path.exists():
                    result['is_broken'] = True
                    result['error_type'] = 'file_not_found'
                    result['error_message'] = f'File not found: {target_path}'
                elif target_path.is_dir():
                    result['is_broken'] = True
                    result['error_type'] = 'is_directory'
                    result['error_message'] = f'Path is directory, not file: {target_path}'
            
            else:
                # Unknown scheme
                result['is_broken'] = False
                result['error_type'] = 'unknown_scheme'
                result['error_message'] = f'Unknown scheme: {parsed.scheme}'
        
        except Exception as e:
            result['is_broken'] = True
            result['error_type'] = 'parse_error'
            result['error_message'] = f'Error parsing link: {e}'
        
        return result
    
    def _check_anchor_link(self, anchor: str, source_file: Path) -> bool:
        """Check if anchor link exists in file"""
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for heading with the anchor ID
            anchor_id = anchor[1:]  # Remove #
            
            # Check for markdown headings
            heading_pattern = r'^#+\s+(.+)$'
            headings = re.findall(heading_pattern, content, re.MULTILINE)
            
            for heading in headings:
                # Convert heading to anchor ID (simplified)
                heading_id = re.sub(r'[^a-zA-Z0-9\s-]', '', heading.lower())
                heading_id = re.sub(r'\s+', '-', heading_id)
                
                if heading_id == anchor_id:
                    return True
            
            return False
        
        except:
            return False
    
    def print_summary(self, results: Dict[str, any]):
        """Print summary of results"""
        print("\n" + "="*60)
        print("🔍 FOCUSED REPOSITORY LINK CHECK SUMMARY")
        print("="*60)
        print(f"Method: {results.get('method', 'unknown')}")
        print(f"Files Checked: {results.get('total_files', 0)}")
        print(f"Total Links: {results.get('total_links', 0)}")
        print(f"Valid Links: {results.get('valid_links', 0)}")
        print(f"Broken Links: {len(results.get('broken_links', []))}")
        
        if results.get('broken_links'):
            print(f"\n❌ Broken Links:")
            for link in results['broken_links'][:20]:  # Show first 20
                print(f"  File: {link.get('file', 'unknown')}")
                print(f"  Link: {link.get('link', 'unknown')}")
                if link.get('text'):
                    print(f"  Text: {link.get('text', '')}")
                print(f"  Error: {link.get('error_message', '')}")
                print()
            
            if len(results['broken_links']) > 20:
                print(f"  ... and {len(results['broken_links']) - 20} more")
        else:
            print("\n✅ No broken links found!")
        
        print("="*60)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Focused Repository Link Checker")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    
    args = parser.parse_args()
    
    checker = FocusedRepoLinkChecker(args.repo_root)
    results = checker.check_current_files()
    checker.print_summary(results)
    
    return 0 if not results.get('broken_links') else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
