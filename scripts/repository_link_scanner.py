#!/usr/bin/env python3
"""
Repository Link Scanner
Comprehensive link checking for all file types in the repository
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from urllib.parse import urlparse
import logging
import subprocess
import time
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepositoryLinkScanner:
    """Comprehensive repository link scanner"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.broken_links = []
        self.checked_files = 0
        self.total_links = 0
        
        # Caching and rate limiting
        self.link_cache = {}  # Cache for checked links
        self.cache_file = self.repo_root / "link_cache.json"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        self.load_cache()
        
        # Link patterns for different file types
        self.link_patterns = {
            'markdown': [
                r'\[([^\]]+)\]\(([^)]+)\)',  # [text](link)
                r'!\[([^\]]*)\]\(([^)]+)\)',  # ![alt](image)
                r'<([^>]+)>',  # <url>
            ],
            'html': [
                r'href=["\']([^"\']+)["\']',  # href="url"
                r'src=["\']([^"\']+)["\']',   # src="url"
                r'<a[^>]+href=["\']([^"\']+)["\']',  # <a href="url">
            ],
            'json': [
                r'"(https?://[^"]+)"',  # "http://..."
                r'"(/[^"]+\.(?:md|html|py|json|yaml|yml))"',  # "/path/file.ext"
            ],
            'yaml': [
                r'"(https?://[^"]+)"',  # "http://..."
                r'"(/[^"]+\.(?:md|html|py|json|yaml|yml))"',  # "/path/file.ext"
            ],
            'python': [
                r'"(https?://[^"]+)"',  # "http://..."
                r'"(/[^"]+\.(?:md|html|py|json|yaml|yml))"',  # "/path/file.ext"
                r'open\(["\']([^"\']+)["\']',  # open("file")
            ],
            'text': [
                r'https?://[^\s]+',  # http://...
                r'/[^\s]+\.(?:md|html|py|json|yaml|yml)',  # /path/file.ext
            ]
        }
        
        # File extensions to check
        self.file_extensions = {
            '.md': 'markdown',
            '.html': 'html',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.py': 'python',
            '.txt': 'text',
            '.sh': 'text',
            '.yml': 'yaml'
        }
    
    def scan_repository(self) -> Dict[str, any]:
        """Scan entire repository for broken links"""
        logger.info("🔍 Starting comprehensive repository link scan...")
        
        results = {
            'start_time': None,
            'end_time': None,
            'total_files_scanned': 0,
            'total_links_found': 0,
            'broken_links': [],
            'file_scan_results': {},
            'summary': {}
        }
        
        try:
            results['start_time'] = self._get_timestamp()
            
            # Find all files to scan
            files_to_scan = self._find_files_to_scan()
            results['total_files_scanned'] = len(files_to_scan)
            
            logger.info(f"Found {len(files_to_scan)} files to scan")
            
            # Scan each file
            for file_path in files_to_scan:
                file_results = self._scan_file(file_path)
                results['file_scan_results'][str(file_path)] = file_results
                results['total_links_found'] += file_results['links_found']
                
                if file_results['broken_links']:
                    results['broken_links'].extend(file_results['broken_links'])
            
            # Generate summary
            results['summary'] = self._generate_summary(results)
            results['end_time'] = self._get_timestamp()
            
            logger.info(f"✅ Repository scan complete: {results['total_links_found']} links found, {len(results['broken_links'])} broken")
            
        except Exception as e:
            logger.error(f"❌ Repository scan failed: {e}")
            results['error'] = str(e)
            results['end_time'] = self._get_timestamp()
        
        return results
    
    def _find_files_to_scan(self) -> List[Path]:
        """Find all files that might contain links"""
        files_to_scan = []
        
        for ext, file_type in self.file_extensions.items():
            pattern = f"**/*{ext}"
            files = list(self.repo_root.glob(pattern))
            
            # Filter out certain directories
            filtered_files = []
            for file_path in files:
                if self._should_scan_file(file_path):
                    filtered_files.append(file_path)
            
            files_to_scan.extend(filtered_files)
            logger.info(f"Found {len(filtered_files)} {file_type} files")
        
        return files_to_scan
    
    def load_cache(self):
        """Load link cache from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.link_cache = json.load(f)
                logger.info(f"Loaded {len(self.link_cache)} cached link checks")
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
            self.link_cache = {}
    
    def save_cache(self):
        """Save link cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.link_cache, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.link_cache)} cached link checks")
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def _get_cache_key(self, link: str) -> str:
        """Generate cache key for link"""
        return hashlib.md5(link.encode()).hexdigest()
    
    def _rate_limit(self):
        """Rate limiting to avoid being blocked"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned"""
        # Skip certain directories
        skip_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
            'env', '.env', 'build', 'dist', '.pytest_cache',
            'migrations', 'logs', 'backups'
        }
        
        # Check if any parent directory is in skip list
        for part in file_path.parts:
            if part in skip_dirs:
                return False
        
        # Skip very large files (>10MB)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            return False
        
        return True
    
    def _scan_file(self, file_path: Path) -> Dict[str, any]:
        """Scan a single file for links"""
        file_results = {
            'file_path': str(file_path),
            'file_type': self._get_file_type(file_path),
            'links_found': 0,
            'broken_links': [],
            'valid_links': [],
            'error': None
        }
        
        try:
            # Read file content
            content = self._read_file_content(file_path)
            if content is None:
                file_results['error'] = "Could not read file content"
                return file_results
            
            # Extract links based on file type
            file_type = file_results['file_type']
            if file_type in self.link_patterns:
                links = self._extract_links(content, file_type)
                file_results['links_found'] = len(links)
                
                # Check each link
                for link in links:
                    link_result = self._check_link(link, file_path)
                    if link_result['is_broken']:
                        file_results['broken_links'].append(link_result)
                    else:
                        file_results['valid_links'].append(link_result)
            
        except Exception as e:
            file_results['error'] = str(e)
            logger.error(f"Error scanning {file_path}: {e}")
        
        return file_results
    
    def _get_file_type(self, file_path: Path) -> str:
        """Get file type based on extension"""
        ext = file_path.suffix.lower()
        return self.file_extensions.get(ext, 'text')
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return None
    
    def _extract_links(self, content: str, file_type: str) -> List[str]:
        """Extract links from content based on file type"""
        links = []
        patterns = self.link_patterns.get(file_type, [])
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns with groups, take the link part
                    link = match[1] if len(match) > 1 else match[0]
                else:
                    link = match
                
                if link and link.strip():
                    links.append(link.strip())
        
        return list(set(links))  # Remove duplicates
    
    def _check_link(self, link: str, source_file: Path) -> Dict[str, any]:
        """Check if a link is broken with caching"""
        result = {
            'link': link,
            'source_file': str(source_file),
            'is_broken': False,
            'error_type': None,
            'error_message': None,
            'from_cache': False
        }
        
        # Check cache first
        cache_key = self._get_cache_key(link)
        if cache_key in self.link_cache:
            cached_result = self.link_cache[cache_key]
            result.update(cached_result)
            result['from_cache'] = True
            logger.debug(f"Using cached result for: {link}")
            return result
        
        try:
            # Parse URL
            parsed = urlparse(link)
            
            if parsed.scheme in ['http', 'https']:
                # External URL - check if accessible with rate limiting
                self._rate_limit()
                result['is_broken'] = not self._check_external_url(link)
                if result['is_broken']:
                    result['error_type'] = 'external_unreachable'
                    result['error_message'] = f"External URL not accessible: {link}"
            
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
                    result['error_message'] = f"File not found: {target_path}"
                elif target_path.is_dir():
                    result['is_broken'] = True
                    result['error_type'] = 'is_directory'
                    result['error_message'] = f"Path is directory, not file: {target_path}"
            
            else:
                # Other schemes (mailto, tel, etc.)
                result['is_broken'] = False
                result['error_type'] = 'other_scheme'
                result['error_message'] = f"Other scheme: {parsed.scheme}"
            
            # Cache the result
            self.link_cache[cache_key] = {
                'is_broken': result['is_broken'],
                'error_type': result['error_type'],
                'error_message': result['error_message']
            }
        
        except Exception as e:
            result['is_broken'] = True
            result['error_type'] = 'parse_error'
            result['error_message'] = f"Error parsing link: {e}"
            
            # Cache the error result too
            self.link_cache[cache_key] = {
                'is_broken': result['is_broken'],
                'error_type': result['error_type'],
                'error_message': result['error_message']
            }
        
        return result
    
    def _check_external_url(self, url: str) -> bool:
        """Check if external URL is accessible"""
        try:
            import requests
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except:
            return False
    
    def _generate_summary(self, results: Dict[str, any]) -> Dict[str, any]:
        """Generate summary of scan results"""
        total_files = results['total_files_scanned']
        total_links = results['total_links_found']
        broken_links = results['broken_links']
        
        # Count by file type
        file_type_counts = {}
        broken_by_type = {}
        
        for file_path, file_results in results['file_scan_results'].items():
            file_type = file_results['file_type']
            file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
            
            if file_results['broken_links']:
                broken_by_type[file_type] = broken_by_type.get(file_type, 0) + len(file_results['broken_links'])
        
        # Count by error type
        error_type_counts = {}
        for broken_link in broken_links:
            error_type = broken_link['error_type']
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
        
        return {
            'total_files_scanned': total_files,
            'total_links_found': total_links,
            'total_broken_links': len(broken_links),
            'broken_link_percentage': (len(broken_links) / total_links * 100) if total_links > 0 else 0,
            'file_type_counts': file_type_counts,
            'broken_links_by_type': broken_by_type,
            'error_type_counts': error_type_counts,
            'scan_success': len(broken_links) == 0
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_results(self, results: Dict[str, any], output_file: str = None) -> str:
        """Save scan results to file"""
        if output_file is None:
            output_file = self.repo_root / "link_scan_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_file}")
        return str(output_file)
    
    def print_summary(self, results: Dict[str, any]):
        """Print scan summary"""
        summary = results['summary']
        
        print("\n" + "="*60)
        print("🔍 REPOSITORY LINK SCAN SUMMARY")
        print("="*60)
        print(f"Files Scanned: {summary['total_files_scanned']}")
        print(f"Links Found: {summary['total_links_found']}")
        print(f"Broken Links: {summary['total_broken_links']}")
        print(f"Broken Link %: {summary['broken_link_percentage']:.2f}%")
        print(f"Scan Success: {'✅ YES' if summary['scan_success'] else '❌ NO'}")
        
        if summary['file_type_counts']:
            print(f"\n📁 Files by Type:")
            for file_type, count in summary['file_type_counts'].items():
                broken = summary['broken_links_by_type'].get(file_type, 0)
                print(f"  {file_type}: {count} files ({broken} broken links)")
        
        if summary['error_type_counts']:
            print(f"\n❌ Error Types:")
            for error_type, count in summary['error_type_counts'].items():
                print(f"  {error_type}: {count}")
        
        if results['broken_links']:
            print(f"\n🔗 Broken Links:")
            for broken_link in results['broken_links'][:10]:  # Show first 10
                print(f"  ❌ {broken_link['link']}")
                print(f"     Source: {broken_link['source_file']}")
                print(f"     Error: {broken_link['error_message']}")
                print()
            
            if len(results['broken_links']) > 10:
                print(f"  ... and {len(results['broken_links']) - 10} more")
        
        print("="*60)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Repository Link Scanner")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scanner = RepositoryLinkScanner(args.repo_root)
    results = scanner.scan_repository()
    
    # Save results
    output_file = scanner.save_results(results, args.output)
    
    # Print summary
    scanner.print_summary(results)
    
    return 0 if results['summary']['scan_success'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
