"""
Minimal working Deployment Data Governance Auditor implementation.

This provides the core functionality to detect and report deployment data violations
based on the governance rules from the January 27, 2025 incident.
"""

import os
import glob
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class DeploymentDataAuditor:
    """Simple deployment data governance auditor."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Forbidden patterns from governance rules
        self.forbidden_patterns = {
            'database_files': ['*.db', '*.sqlite*', '*.sql'],
            'time_series_data': ['*prometheus-data*', '*grafana-data*'],
            'log_files': ['*.log', 'logs/', 'log/'],
            'cache_files': ['cache/', 'tmp/', 'temp/', '*.cache'],
            'runtime_state': ['*.pid', '*.sock', '*.lock'],
            'binary_executables': ['*.exe', '*.bin', '*.so', '*.dll']
        }
    
    def scan_directory(self, directory: str) -> Dict[str, Any]:
        """Scan directory for governance violations."""
        violations = []
        total_files = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    total_files += 1
                    file_path = os.path.join(root, file)
                    
                    # Check against forbidden patterns
                    for category, patterns in self.forbidden_patterns.items():
                        for pattern in patterns:
                            if self._matches_pattern(file_path, pattern):
                                violations.append({
                                    'file_path': file_path,
                                    'category': category,
                                    'pattern': pattern,
                                    'detected_at': datetime.now().isoformat()
                                })
                                break
        
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
        
        return {
            'scan_timestamp': datetime.now().isoformat(),
            'directory': directory,
            'total_files_scanned': total_files,
            'violations_found': len(violations),
            'violations': violations
        }
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches forbidden pattern."""
        file_path_lower = file_path.lower()
        pattern_lower = pattern.lower()
        
        if pattern_lower.endswith('/'):
            return pattern_lower[:-1] in file_path_lower
        elif '*' in pattern_lower:
            import fnmatch
            return fnmatch.fnmatch(file_path_lower, pattern_lower)
        else:
            return pattern_lower in file_path_lower
    
    def generate_gitignore_patterns(self, violations: List[Dict]) -> List[str]:
        """Generate .gitignore patterns for violations."""
        patterns = set()
        
        for violation in violations:
            pattern = violation['pattern']
            if pattern not in patterns:
                patterns.add(pattern)
        
        return sorted(list(patterns))


def main():
    """CLI entry point for quick testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auditor.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    auditor = DeploymentDataAuditor()
    
    print(f"Scanning {directory} for deployment data violations...")
    result = auditor.scan_directory(directory)
    
    print(f"\nScan Results:")
    print(f"Files scanned: {result['total_files_scanned']}")
    print(f"Violations found: {result['violations_found']}")
    
    if result['violations']:
        print(f"\nViolations:")
        for violation in result['violations']:
            print(f"  {violation['file_path']} ({violation['category']})")
        
        print(f"\nSuggested .gitignore patterns:")
        patterns = auditor.generate_gitignore_patterns(result['violations'])
        for pattern in patterns:
            print(f"  {pattern}")


if __name__ == '__main__':
    main()