#!/usr/bin/env python3
"""
Simple Repository Link Checker
Uses existing tools and packages for link checking
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleLinkChecker:
    """Simple link checker using existing tools"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.results = {
            'broken_links': [],
            'total_files': 0,
            'total_links': 0
        }
    
    def check_markdown_links(self) -> Dict[str, any]:
        """Check markdown links using markdown-link-check"""
        logger.info("🔍 Checking markdown links...")
        
        try:
            # Find all markdown files
            md_files = list(self.repo_root.rglob("*.md"))
            logger.info(f"Found {len(md_files)} markdown files")
            
            broken_links = []
            total_links = 0
            
            for md_file in md_files:
                logger.info(f"Checking: {md_file}")
                
                # Use markdown-link-check if available
                try:
                    result = subprocess.run([
                        'npx', 'markdown-link-check', str(md_file), '--json'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        # Parse JSON output
                        try:
                            data = json.loads(result.stdout)
                            total_links += len(data.get('links', []))
                            
                            for link in data.get('links', []):
                                if link.get('status') != 'OK':
                                    broken_links.append({
                                        'file': str(md_file),
                                        'link': link.get('href', ''),
                                        'status': link.get('status', ''),
                                        'error': link.get('error', '')
                                    })
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse JSON output for {md_file}")
                    
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    # Fallback to simple grep-based checking
                    logger.info(f"Using fallback method for {md_file}")
                    file_broken_links = self._check_markdown_file_simple(md_file)
                    broken_links.extend(file_broken_links)
                    total_links += len(file_broken_links)
            
            return {
                'broken_links': broken_links,
                'total_links': total_links,
                'method': 'markdown-link-check'
            }
            
        except Exception as e:
            logger.error(f"Error checking markdown links: {e}")
            return {'broken_links': [], 'total_links': 0, 'error': str(e)}
    
    def _check_markdown_file_simple(self, md_file: Path) -> List[Dict]:
        """Simple markdown link checking using grep"""
        broken_links = []
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find markdown links
            import re
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(link_pattern, content)
            
            for text, link in matches:
                if self._is_broken_link(link, md_file):
                    broken_links.append({
                        'file': str(md_file),
                        'link': link,
                        'text': text,
                        'error': 'File not found or inaccessible'
                    })
        
        except Exception as e:
            logger.error(f"Error checking {md_file}: {e}")
        
        return broken_links
    
    def _is_broken_link(self, link: str, source_file: Path) -> bool:
        """Check if a link is broken (local files only)"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(link)
            
            # Skip external URLs
            if parsed.scheme in ['http', 'https', 'mailto', 'tel']:
                return False
            
            # Check local files
            if link.startswith('/'):
                target_path = Path(link)
            else:
                target_path = source_file.parent / link
            
            return not target_path.exists()
        
        except:
            return True
    
    def check_with_linkchecker(self) -> Dict[str, any]:
        """Check links using linkchecker tool"""
        logger.info("🔍 Checking links with linkchecker...")
        
        try:
            # Run linkchecker
            result = subprocess.run([
                'linkchecker', 
                '--check-extern', 
                '--no-warnings',
                '--ignore-url=^mailto:',
                '--ignore-url=^tel:',
                '--output=json',
                str(self.repo_root)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Parse JSON output
                try:
                    data = json.loads(result.stdout)
                    broken_links = []
                    
                    for item in data:
                        if item.get('result') != 'OK':
                            broken_links.append({
                                'url': item.get('url', ''),
                                'file': item.get('filename', ''),
                                'result': item.get('result', ''),
                                'error': item.get('info', '')
                            })
                    
                    return {
                        'broken_links': broken_links,
                        'total_links': len(data),
                        'method': 'linkchecker'
                    }
                
                except json.JSONDecodeError:
                    logger.warning("Could not parse linkchecker JSON output")
                    return {'broken_links': [], 'total_links': 0, 'error': 'JSON parse error'}
            else:
                logger.warning(f"linkchecker failed: {result.stderr}")
                return {'broken_links': [], 'total_links': 0, 'error': result.stderr}
        
        except FileNotFoundError:
            logger.warning("linkchecker not found, trying alternative method")
            return self.check_markdown_links()
        except subprocess.TimeoutExpired:
            logger.warning("linkchecker timed out")
            return {'broken_links': [], 'total_links': 0, 'error': 'Timeout'}
        except Exception as e:
            logger.error(f"Error running linkchecker: {e}")
            return {'broken_links': [], 'total_links': 0, 'error': str(e)}
    
    def check_with_grep(self) -> Dict[str, any]:
        """Simple grep-based link checking"""
        logger.info("🔍 Checking links with grep...")
        
        try:
            # Find all files with potential links
            file_types = ['*.md', '*.html', '*.json', '*.yaml', '*.yml', '*.py', '*.txt']
            all_files = []
            
            for pattern in file_types:
                files = list(self.repo_root.rglob(pattern))
                all_files.extend(files)
            
            logger.info(f"Found {len(all_files)} files to check")
            
            broken_links = []
            total_links = 0
            
            for file_path in all_files:
                if self._should_skip_file(file_path):
                    continue
                
                file_broken_links = self._check_file_links(file_path)
                broken_links.extend(file_broken_links)
                total_links += len(file_broken_links)
            
            return {
                'broken_links': broken_links,
                'total_links': total_links,
                'method': 'grep'
            }
        
        except Exception as e:
            logger.error(f"Error with grep method: {e}")
            return {'broken_links': [], 'total_links': 0, 'error': str(e)}
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.env', 'build', 'dist'}
        
        for part in file_path.parts:
            if part in skip_dirs:
                return True
        
        # Skip very large files
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return True
        except:
            pass
        
        return False
    
    def _check_file_links(self, file_path: Path) -> List[Dict]:
        """Check links in a single file"""
        broken_links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find various link patterns
            import re
            
            # Markdown links
            md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for text, link in md_links:
                if self._is_broken_link(link, file_path):
                    broken_links.append({
                        'file': str(file_path),
                        'link': link,
                        'text': text,
                        'type': 'markdown'
                    })
            
            # HTML links
            html_links = re.findall(r'href=["\']([^"\']+)["\']', content)
            for link in html_links:
                if self._is_broken_link(link, file_path):
                    broken_links.append({
                        'file': str(file_path),
                        'link': link,
                        'type': 'html'
                    })
            
            # JSON/YAML file paths
            if file_path.suffix in ['.json', '.yaml', '.yml']:
                file_paths = re.findall(r'"(/[^"]+\.(?:md|html|py|json|yaml|yml))"', content)
                for link in file_paths:
                    if self._is_broken_link(link, file_path):
                        broken_links.append({
                            'file': str(file_path),
                            'link': link,
                            'type': 'file_path'
                        })
        
        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")
        
        return broken_links
    
    def run_comprehensive_check(self) -> Dict[str, any]:
        """Run comprehensive link check using best available method"""
        logger.info("🚀 Starting comprehensive link check...")
        
        # Try different methods in order of preference
        methods = [
            ('linkchecker', self.check_with_linkchecker),
            ('markdown-link-check', self.check_markdown_links),
            ('grep', self.check_with_grep)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying method: {method_name}")
                result = method_func()
                
                if result.get('error'):
                    logger.warning(f"Method {method_name} failed: {result['error']}")
                    continue
                
                logger.info(f"✅ Method {method_name} completed successfully")
                result['method_used'] = method_name
                return result
            
            except Exception as e:
                logger.warning(f"Method {method_name} failed with exception: {e}")
                continue
        
        # If all methods fail
        logger.error("All link checking methods failed")
        return {
            'broken_links': [],
            'total_links': 0,
            'error': 'All methods failed',
            'method_used': 'none'
        }
    
    def print_summary(self, results: Dict[str, any]):
        """Print summary of results"""
        print("\n" + "="*60)
        print("🔍 REPOSITORY LINK CHECK SUMMARY")
        print("="*60)
        print(f"Method Used: {results.get('method_used', 'unknown')}")
        print(f"Total Links: {results.get('total_links', 0)}")
        print(f"Broken Links: {len(results.get('broken_links', []))}")
        
        if results.get('error'):
            print(f"Error: {results['error']}")
        
        if results.get('broken_links'):
            print(f"\n❌ Broken Links:")
            for link in results['broken_links'][:10]:  # Show first 10
                print(f"  File: {link.get('file', 'unknown')}")
                print(f"  Link: {link.get('link', 'unknown')}")
                if link.get('text'):
                    print(f"  Text: {link.get('text', '')}")
                if link.get('error'):
                    print(f"  Error: {link.get('error', '')}")
                print()
            
            if len(results['broken_links']) > 10:
                print(f"  ... and {len(results['broken_links']) - 10} more")
        
        print("="*60)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Repository Link Checker")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--method", choices=['linkchecker', 'markdown-link-check', 'grep', 'auto'], 
                       default='auto', help="Link checking method to use")
    
    args = parser.parse_args()
    
    checker = SimpleLinkChecker(args.repo_root)
    
    if args.method == 'auto':
        results = checker.run_comprehensive_check()
    elif args.method == 'linkchecker':
        results = checker.check_with_linkchecker()
    elif args.method == 'markdown-link-check':
        results = checker.check_markdown_links()
    elif args.method == 'grep':
        results = checker.check_with_grep()
    
    checker.print_summary(results)
    
    return 0 if not results.get('broken_links') else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
