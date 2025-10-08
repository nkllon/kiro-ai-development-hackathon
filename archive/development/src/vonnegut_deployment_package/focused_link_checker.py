#!/usr/bin/env python3
"""
Focused Link Checker for Repository
Checks document links and artifact links with more precise patterns
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedLinkChecker:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.broken_links = []
        self.checked_files = 0
        self.total_links = 0
        
        # More precise patterns for different types of links
        self.link_patterns = {
            'markdown': [
                r'\[([^\]]+)\]\(([^)]+)\)',  # [text](link)
                r'!\[([^\]]*)\]\(([^)]+)\)',  # ![alt](image)
            ],
            'html': [
                r'href=["\']([^"\']+)["\']',  # href="link"
                r'src=["\']([^"\']+)["\']',   # src="link"
            ],
            'json': [
                r'"path":\s*"([^"]+)"',  # Path references
                r'"file":\s*"([^"]+)"',  # File references
                r'"url":\s*"([^"]+)"',   # URL references
                r'"implementation_path":\s*"([^"]+)"',  # Implementation paths
            ],
            'yaml': [
                r'["\']([^"\']*\.(?:md|html|py|json|yaml|yml|txt|png|jpg|jpeg|gif|svg))["\']',  # File references
            ],
            'text': [
                r'https?://[^\s]+',  # HTTP/HTTPS URLs
            ]
        }
        
        # File extensions to check
        self.file_extensions = {
            '.md': 'markdown',
            '.html': 'html',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.txt': 'text',
        }

    def is_absolute_url(self, link: str) -> bool:
        """Check if link is an absolute URL"""
        try:
            result = urlparse(link)
            return bool(result.scheme and result.netloc)
        except:
            return False

    def is_external_link(self, link: str) -> bool:
        """Check if link is external (not relative to repo)"""
        if self.is_absolute_url(link):
            return True
        
        # Check if it starts with common external patterns
        external_patterns = ['http://', 'https://', 'ftp://', 'mailto:', 'tel:']
        return any(link.startswith(pattern) for pattern in external_patterns)

    def resolve_relative_path(self, file_path: Path, link: str) -> Path:
        """Resolve relative path from file location"""
        if link.startswith('/'):
            # Absolute path from repo root
            return self.repo_root / link.lstrip('/')
        else:
            # Relative path from file location
            return file_path.parent / link

    def check_file_exists(self, file_path: Path) -> bool:
        """Check if file exists"""
        return file_path.exists()

    def is_valid_file_reference(self, link: str) -> bool:
        """Check if link looks like a valid file reference"""
        # Skip obvious non-file references
        skip_patterns = [
            r'^[a-zA-Z_][a-zA-Z0-9_]*$',  # Just variable names
            r'^\d+$',  # Just numbers
            r'^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*$',  # Module names
            r'^[a-zA-Z_][a-zA-Z0-9_]*\(',  # Function calls
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, link):
                return False
        
        # Must contain a file extension or be a clear path
        file_extensions = ['.md', '.html', '.py', '.json', '.yaml', '.yml', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.svg']
        return any(link.endswith(ext) for ext in file_extensions) or '/' in link

    def check_link(self, file_path: Path, link: str, context: str = "") -> Dict:
        """Check a single link and return result"""
        result = {
            'file': str(file_path.relative_to(self.repo_root)),
            'link': link,
            'context': context,
            'status': 'unknown',
            'resolved_path': None,
            'error': None
        }
        
        try:
            if self.is_external_link(link):
                result['status'] = 'external'
                result['resolved_path'] = link
            else:
                # Only check if it looks like a file reference
                if not self.is_valid_file_reference(link):
                    result['status'] = 'skipped'
                    result['resolved_path'] = link
                    return result
                
                resolved_path = self.resolve_relative_path(file_path, link)
                result['resolved_path'] = str(resolved_path.relative_to(self.repo_root))
                
                if self.check_file_exists(resolved_path):
                    result['status'] = 'valid'
                else:
                    result['status'] = 'broken'
                    result['error'] = f"File not found: {resolved_path}"
                    
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result

    def extract_links_from_content(self, content: str, file_type: str) -> List[Tuple[str, str]]:
        """Extract links from file content based on file type"""
        links = []
        patterns = self.link_patterns.get(file_type, [])
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) >= 2:
                    # Pattern with groups (text, link)
                    link = match.group(2)
                    context = match.group(1)
                else:
                    # Pattern with single group (link)
                    link = match.group(1)
                    context = ""
                
                # Clean up the link
                link = link.strip()
                if link and not link.startswith('#'):  # Skip anchor links
                    links.append((link, context))
        
        return links

    def check_file(self, file_path: Path) -> List[Dict]:
        """Check all links in a single file"""
        file_results = []
        
        try:
            # Determine file type
            file_ext = file_path.suffix.lower()
            file_type = self.file_extensions.get(file_ext, 'text')
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract links
            links = self.extract_links_from_content(content, file_type)
            
            # Check each link
            for link, context in links:
                result = self.check_link(file_path, link, context)
                file_results.append(result)
                
                if result['status'] in ['broken', 'error']:
                    self.broken_links.append(result)
                
                self.total_links += 1
            
            self.checked_files += 1
            
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
            file_results.append({
                'file': str(file_path.relative_to(self.repo_root)),
                'link': 'FILE_READ_ERROR',
                'context': '',
                'status': 'error',
                'resolved_path': None,
                'error': str(e)
            })
        
        return file_results

    def check_repository(self) -> Dict:
        """Check all files in repository"""
        logger.info("Starting focused link check...")
        
        all_results = []
        
        # Find all files to check
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                if file_ext in self.file_extensions:
                    # Skip certain directories
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    if 'node_modules' in file_path.parts:
                        continue
                    if '__pycache__' in file_path.parts:
                        continue
                    if 'migration_backups' in file_path.parts:
                        continue
                    if 'src/rc1/migration/backups' in file_path.parts:
                        continue
                    
                    logger.info(f"Checking {file_path.relative_to(self.repo_root)}")
                    file_results = self.check_file(file_path)
                    all_results.extend(file_results)
        
        # Generate summary
        summary = {
            'total_files_checked': self.checked_files,
            'total_links_found': self.total_links,
            'broken_links': len(self.broken_links),
            'external_links': len([r for r in all_results if r['status'] == 'external']),
            'valid_links': len([r for r in all_results if r['status'] == 'valid']),
            'skipped_links': len([r for r in all_results if r['status'] == 'skipped']),
            'error_links': len([r for r in all_results if r['status'] == 'error']),
            'broken_links_details': self.broken_links,
            'all_results': all_results
        }
        
        return summary

    def generate_report(self, summary: Dict, output_file: str = None):
        """Generate a focused report"""
        report_lines = [
            "# Focused Link Check Report",
            f"Generated: {Path().cwd()}",
            "",
            "## Summary",
            f"- Total files checked: {summary['total_files_checked']}",
            f"- Total links found: {summary['total_links_found']}",
            f"- Valid links: {summary['valid_links']}",
            f"- External links: {summary['external_links']}",
            f"- Skipped links: {summary['skipped_links']}",
            f"- Broken links: {summary['broken_links']}",
            f"- Error links: {summary['error_links']}",
            "",
        ]
        
        if summary['broken_links'] > 0:
            report_lines.extend([
                "## Broken Links",
                ""
            ])
            
            # Group by file
            broken_by_file = {}
            for link in summary['broken_links_details']:
                file_path = link['file']
                if file_path not in broken_by_file:
                    broken_by_file[file_path] = []
                broken_by_file[file_path].append(link)
            
            for file_path, links in broken_by_file.items():
                report_lines.extend([
                    f"### {file_path}",
                    ""
                ])
                for link in links:
                    report_lines.extend([
                        f"- **Link**: `{link['link']}`",
                        f"  - **Context**: {link['context']}",
                        f"  - **Resolved Path**: {link['resolved_path']}",
                        f"  - **Error**: {link['error']}",
                        ""
                    ])
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report saved to {output_file}")
        else:
            print(report_content)

def main():
    """Main function"""
    repo_root = "/Users/lou/kiro-2/kiro-ai-development-hackathon"
    
    checker = FocusedLinkChecker(repo_root)
    summary = checker.check_repository()
    
    # Generate report
    report_file = os.path.join(repo_root, "focused_link_check_report.md")
    checker.generate_report(summary, report_file)
    
    # Print summary
    print(f"\n{'='*60}")
    print("FOCUSED LINK CHECK SUMMARY")
    print(f"{'='*60}")
    print(f"Files checked: {summary['total_files_checked']}")
    print(f"Total links: {summary['total_links_found']}")
    print(f"Valid links: {summary['valid_links']}")
    print(f"External links: {summary['external_links']}")
    print(f"Skipped links: {summary['skipped_links']}")
    print(f"Broken links: {summary['broken_links']}")
    print(f"Error links: {summary['error_links']}")
    print(f"{'='*60}")
    
    if summary['broken_links'] > 0:
        print(f"\n⚠️  Found {summary['broken_links']} broken links!")
        print(f"Detailed report saved to: {report_file}")
    else:
        print("\n✅ All links are valid!")

if __name__ == "__main__":
    main()
