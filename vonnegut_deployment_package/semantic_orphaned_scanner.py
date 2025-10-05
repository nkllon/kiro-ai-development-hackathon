#!/usr/bin/env python3
"""
Semantic Orphaned Solution Scanner
=================================

Uses semantic analysis to find implementations without corresponding specifications.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from improved_spec_matcher import ImprovedSpecMatcher, SemanticMatch


class SemanticOrphanedScanner:
    """
    Scanner that uses semantic analysis to identify orphaned solutions.
    """
    
    def __init__(self, repository_path: str = "."):
        self.repository_path = Path(repository_path)
        self.matcher = ImprovedSpecMatcher()
        
        # Minimum thresholds for considering something "implemented"
        self.min_lines = 50
        self.min_functions = 3
        self.min_complexity = 5
        
        # Confidence threshold for considering a spec-impl match
        self.match_threshold = 0.35
    
    def scan_repository(self) -> Dict[str, Any]:
        """Perform semantic scan for orphaned solutions."""
        print("🔍 Semantic Orphaned Solution Scan")
        print("=" * 50)
        
        # Discover implementations and specs
        implementations = self._discover_implementations()
        specifications = self._discover_specifications()
        
        print(f"📊 Found {len(implementations)} implementations and {len(specifications)} specifications")
        
        # Find semantic matches
        matches = self.matcher.find_matches(specifications, implementations)
        
        # Identify orphaned solutions
        orphaned_solutions = self._identify_orphaned_solutions(implementations, matches)
        
        # Generate report
        report = self._generate_report(implementations, specifications, matches, orphaned_solutions)
        
        return report
    
    def _discover_implementations(self) -> List[Path]:
        """Discover implementation files that are substantial enough to need specs."""
        implementations = []
        
        # Search patterns for implementations
        search_patterns = [
            "src/**/*.py",
            "scripts/**/*.py", 
            "makefiles/**/*.mk",
            "*.py"
        ]
        
        exclude_patterns = [
            "**/test_*.py",
            "**/*_test.py", 
            "**/tests/**",
            "**/__pycache__/**",
            "**/.git/**",
            "**/node_modules/**"
        ]
        
        for pattern in search_patterns:
            for file_path in self.repository_path.glob(pattern):
                # Check if should exclude
                should_exclude = any(file_path.match(exclude) for exclude in exclude_patterns)
                if should_exclude:
                    continue
                
                # Check if substantial enough
                if self._is_substantial_implementation(file_path):
                    implementations.append(file_path)
        
        print(f"📁 Discovered {len(implementations)} substantial implementations")
        return implementations
    
    def _discover_specifications(self) -> List[Path]:
        """Discover specification files."""
        specifications = []
        
        # Search patterns for specs
        search_patterns = [
            ".kiro/specs/**/*.md",
            "docs/**/*.md",
            "**/*requirements*.md",
            "**/*design*.md", 
            "**/*tasks*.md",
            "**/*specification*.md"
        ]
        
        for pattern in search_patterns:
            for file_path in self.repository_path.glob(pattern):
                if file_path.exists() and file_path.stat().st_size > 100:  # At least 100 bytes
                    specifications.append(file_path)
        
        print(f"📋 Discovered {len(specifications)} specification files")
        return specifications
    
    def _is_substantial_implementation(self, file_path: Path) -> bool:
        """Check if implementation is substantial enough to need a spec."""
        try:
            # Try multiple encodings to handle problematic files
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    content = file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # Last resort: read as bytes and decode with errors='ignore'
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Basic size check
            line_count = len(content.splitlines())
            if line_count < self.min_lines:
                return False
            
            # Check for complexity indicators
            if file_path.suffix == '.py':
                return self._is_substantial_python(content)
            elif file_path.suffix == '.mk' or file_path.name.endswith('Makefile'):
                return self._is_substantial_makefile(content)
            else:
                return line_count > 100  # Generic threshold
                
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return False
    
    def _is_substantial_python(self, content: str) -> bool:
        """Check if Python file is substantial."""
        # Count functions and classes
        function_count = content.count("def ")
        class_count = content.count("class ")
        
        # Look for complexity indicators
        has_imports = "import " in content
        has_docstrings = '"""' in content or "'''" in content
        has_error_handling = "try:" in content or "except" in content
        has_async = "async " in content or "await " in content
        
        # Calculate complexity score
        complexity_score = (
            function_count +
            class_count * 2 +
            (1 if has_imports else 0) +
            (1 if has_docstrings else 0) +
            (1 if has_error_handling else 0) +
            (1 if has_async else 0)
        )
        
        return complexity_score >= self.min_complexity
    
    def _is_substantial_makefile(self, content: str) -> bool:
        """Check if Makefile is substantial."""
        # Count targets and variables
        target_count = len([line for line in content.split('\n') if ':' in line and not line.strip().startswith('#')])
        variable_count = len([line for line in content.split('\n') if '=' in line and not line.strip().startswith('#')])
        
        return target_count >= 5 or variable_count >= 3
    
    def _identify_orphaned_solutions(self, implementations: List[Path], matches: List[SemanticMatch]) -> List[Dict[str, Any]]:
        """Identify implementations that don't have adequate specification coverage."""
        orphaned_solutions = []
        
        # Create lookup of implementations that have matches
        matched_implementations = set()
        for match in matches:
            if match.confidence >= self.match_threshold:
                matched_implementations.add(match.impl_path)
        
        # Find orphaned implementations
        for impl_path in implementations:
            impl_path_str = str(impl_path)
            
            if impl_path_str not in matched_implementations:
                # This implementation has no adequate spec match
                orphaned_solution = {
                    'implementation_path': impl_path_str,
                    'file_type': impl_path.suffix,
                    'size_lines': self._get_line_count(impl_path),
                    'complexity_score': self._calculate_complexity_score(impl_path),
                    'suggested_spec_location': self._suggest_spec_location(impl_path),
                    'priority': self._calculate_priority(impl_path),
                    'estimated_effort_hours': self._estimate_effort(impl_path)
                }
                orphaned_solutions.append(orphaned_solution)
        
        # Sort by priority (high priority first)
        orphaned_solutions.sort(key=lambda x: (x['priority'], -x['complexity_score']))
        
        print(f"🚨 Identified {len(orphaned_solutions)} orphaned solutions")
        return orphaned_solutions
    
    def _get_line_count(self, file_path: Path) -> int:
        """Get line count for file."""
        try:
            # Try multiple encodings
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    content = file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return len(content.splitlines())
        except:
            return 0
    
    def _calculate_complexity_score(self, file_path: Path) -> int:
        """Calculate complexity score for implementation."""
        try:
            # Try multiple encodings
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    content = file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if file_path.suffix == '.py':
                return self._calculate_python_complexity(content)
            elif file_path.suffix == '.mk' or file_path.name.endswith('Makefile'):
                return self._calculate_makefile_complexity(content)
            else:
                return len(content.splitlines()) // 10  # Generic complexity
                
        except:
            return 1
    
    def _calculate_python_complexity(self, content: str) -> int:
        """Calculate Python file complexity."""
        complexity = 0
        
        # Count various complexity indicators
        complexity += content.count("def ") * 2
        complexity += content.count("class ") * 3
        complexity += content.count("if ") 
        complexity += content.count("for ")
        complexity += content.count("while ")
        complexity += content.count("try:")
        complexity += content.count("async ")
        
        return complexity
    
    def _calculate_makefile_complexity(self, content: str) -> int:
        """Calculate Makefile complexity."""
        lines = content.split('\n')
        
        target_count = len([line for line in lines if ':' in line and not line.strip().startswith('#')])
        variable_count = len([line for line in lines if '=' in line and not line.strip().startswith('#')])
        command_count = len([line for line in lines if line.strip().startswith('@')])
        
        return target_count * 2 + variable_count + command_count
    
    def _suggest_spec_location(self, impl_path: Path) -> str:
        """Suggest where specification should be created."""
        # Extract meaningful name from implementation
        name_parts = []
        
        # Add path components
        for part in impl_path.parts:
            if part not in ['src', 'scripts', 'makefiles']:
                name_parts.append(part)
        
        # Clean up the name
        if impl_path.suffix:
            name_parts[-1] = impl_path.stem  # Remove extension
        
        # Convert to kebab-case
        spec_name = '-'.join(name_parts).lower().replace('_', '-')
        
        return f".kiro/specs/{spec_name}/requirements.md"
    
    def _calculate_priority(self, impl_path: Path) -> int:
        """Calculate priority for creating specification (1=high, 2=medium, 3=low)."""
        priority_score = 0
        
        # High priority indicators
        if 'system' in str(impl_path).lower():
            priority_score += 3
        if 'engine' in str(impl_path).lower():
            priority_score += 3
        if 'orchestrator' in str(impl_path).lower():
            priority_score += 3
        if 'framework' in str(impl_path).lower():
            priority_score += 2
        if 'manager' in str(impl_path).lower():
            priority_score += 2
        
        # Size-based priority
        line_count = self._get_line_count(impl_path)
        if line_count > 500:
            priority_score += 3
        elif line_count > 200:
            priority_score += 2
        elif line_count > 100:
            priority_score += 1
        
        # Complexity-based priority
        complexity = self._calculate_complexity_score(impl_path)
        if complexity > 50:
            priority_score += 3
        elif complexity > 20:
            priority_score += 2
        elif complexity > 10:
            priority_score += 1
        
        # Convert score to priority level
        if priority_score >= 6:
            return 1  # High priority
        elif priority_score >= 3:
            return 2  # Medium priority
        else:
            return 3  # Low priority
    
    def _estimate_effort(self, impl_path: Path) -> int:
        """Estimate effort in hours to create specification."""
        base_hours = 2
        
        line_count = self._get_line_count(impl_path)
        complexity = self._calculate_complexity_score(impl_path)
        
        # Add hours based on size and complexity
        base_hours += line_count // 100
        base_hours += complexity // 10
        
        # File type adjustments
        if impl_path.suffix == '.py':
            base_hours += 1  # Python files need more detailed specs
        elif impl_path.suffix == '.mk':
            base_hours += 2  # Makefiles are complex to specify
        
        return min(base_hours, 20)  # Cap at 20 hours
    
    def _generate_report(self, implementations: List[Path], specifications: List[Path], 
                        matches: List[SemanticMatch], orphaned_solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive scan report."""
        
        # Calculate coverage statistics
        total_implementations = len(implementations)
        matched_implementations = len(set(match.impl_path for match in matches if match.confidence >= self.match_threshold))
        coverage_percentage = (matched_implementations / total_implementations * 100) if total_implementations > 0 else 0
        
        # Priority distribution
        high_priority = len([o for o in orphaned_solutions if o['priority'] == 1])
        medium_priority = len([o for o in orphaned_solutions if o['priority'] == 2])
        low_priority = len([o for o in orphaned_solutions if o['priority'] == 3])
        
        # Effort estimation
        total_effort = sum(o['estimated_effort_hours'] for o in orphaned_solutions)
        
        report = {
            'scan_metadata': {
                'timestamp': datetime.now().isoformat(),
                'repository_path': str(self.repository_path),
                'scanner_type': 'semantic',
                'match_threshold': self.match_threshold
            },
            'discovery_summary': {
                'total_implementations': total_implementations,
                'total_specifications': len(specifications),
                'semantic_matches_found': len(matches),
                'high_confidence_matches': len([m for m in matches if m.confidence >= self.match_threshold])
            },
            'coverage_analysis': {
                'matched_implementations': matched_implementations,
                'orphaned_implementations': len(orphaned_solutions),
                'coverage_percentage': coverage_percentage
            },
            'priority_distribution': {
                'high_priority_orphans': high_priority,
                'medium_priority_orphans': medium_priority,
                'low_priority_orphans': low_priority
            },
            'effort_estimation': {
                'total_estimated_hours': total_effort,
                'average_hours_per_orphan': total_effort / len(orphaned_solutions) if orphaned_solutions else 0
            },
            'semantic_matches': [
                {
                    'spec_path': match.spec_path,
                    'impl_path': match.impl_path,
                    'confidence': match.confidence,
                    'match_reasons': match.match_reasons,
                    'semantic_keywords': match.semantic_keywords[:5],  # Top 5
                    'domain_keywords': match.domain_keywords[:5]
                }
                for match in matches if match.confidence >= self.match_threshold
            ],
            'orphaned_solutions': orphaned_solutions,
            'recommendations': self._generate_recommendations(orphaned_solutions, coverage_percentage)
        }
        
        return report
    
    def scan_repository_chunked(self, chunk_size: int = 50) -> Dict[str, Any]:
        """Perform chunked semantic scan for large repositories."""
        print("🔍 Chunked Semantic Orphaned Solution Scan")
        print("=" * 50)
        
        # Discover all files first
        implementations = self._discover_implementations()
        specifications = self._discover_specifications()
        
        print(f"📊 Found {len(implementations)} implementations and {len(specifications)} specifications")
        print(f"📦 Processing in chunks of {chunk_size} implementations")
        
        # Process implementations in chunks
        all_matches = []
        all_orphaned_solutions = []
        
        for i in range(0, len(implementations), chunk_size):
            chunk_impls = implementations[i:i + chunk_size]
            chunk_num = (i // chunk_size) + 1
            total_chunks = (len(implementations) + chunk_size - 1) // chunk_size
            
            print(f"📦 Processing chunk {chunk_num}/{total_chunks} ({len(chunk_impls)} implementations)")
            
            # Find semantic matches for this chunk
            chunk_matches = self.matcher.find_matches(specifications, chunk_impls)
            all_matches.extend(chunk_matches)
            
            # Identify orphaned solutions in this chunk
            chunk_orphaned = self._identify_orphaned_solutions(chunk_impls, chunk_matches)
            all_orphaned_solutions.extend(chunk_orphaned)
            
            print(f"   Found {len(chunk_matches)} matches, {len(chunk_orphaned)} orphans")
        
        print(f"\n📊 Chunked scan complete:")
        print(f"   Total matches: {len(all_matches)}")
        print(f"   Total orphans: {len(all_orphaned_solutions)}")
        
        # Generate comprehensive report
        report = self._generate_report(implementations, specifications, all_matches, all_orphaned_solutions)
        report['scan_metadata']['chunked'] = True
        report['scan_metadata']['chunk_size'] = chunk_size
        
        return report
    
    def _generate_recommendations(self, orphaned_solutions: List[Dict[str, Any]], coverage_percentage: float) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if coverage_percentage < 70:
            recommendations.append(f"Specification coverage is {coverage_percentage:.1f}% - target 80%+ for good governance")
        
        high_priority_count = len([o for o in orphaned_solutions if o['priority'] == 1])
        if high_priority_count > 0:
            recommendations.append(f"Immediately create specifications for {high_priority_count} high-priority orphaned solutions")
        
        total_effort = sum(o['estimated_effort_hours'] for o in orphaned_solutions)
        if total_effort > 40:
            recommendations.append(f"Consider allocating {total_effort} hours of team time for specification creation")
        
        # Specific recommendations for top orphans
        top_orphans = sorted(orphaned_solutions, key=lambda x: (x['priority'], -x['complexity_score']))[:3]
        for orphan in top_orphans:
            recommendations.append(f"Priority: Create spec for {orphan['implementation_path']} ({orphan['estimated_effort_hours']}h estimated)")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], output_path: str = None):
        """Save scan report to file."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/semantic_orphaned_scan_{timestamp}.json"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Report saved to {output_file}")
        return output_file
    
    def generate_markdown_report(self, report: Dict[str, Any], output_path: str = None):
        """Generate human-readable markdown report."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/semantic_orphaned_scan_{timestamp}.md"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = self._format_markdown_report(report)
        
        with open(output_file, 'w') as f:
            f.write(md_content)
        
        print(f"📋 Markdown report saved to {output_file}")
        return output_file
    
    def _format_markdown_report(self, report: Dict[str, Any]) -> str:
        """Format report as markdown."""
        md = f"""# Semantic Orphaned Solutions Scan Report

**Scan Date**: {report['scan_metadata']['timestamp']}  
**Repository**: {report['scan_metadata']['repository_path']}  
**Scanner Type**: {report['scan_metadata']['scanner_type']}  
**Match Threshold**: {report['scan_metadata']['match_threshold']}  

## Executive Summary

- **Total Implementations**: {report['discovery_summary']['total_implementations']}
- **Total Specifications**: {report['discovery_summary']['total_specifications']}
- **Specification Coverage**: {report['coverage_analysis']['coverage_percentage']:.1f}%
- **Orphaned Solutions**: {report['coverage_analysis']['orphaned_implementations']}
- **High Priority Orphans**: {report['priority_distribution']['high_priority_orphans']}
- **Estimated Effort**: {report['effort_estimation']['total_estimated_hours']} hours

## Coverage Analysis

- **Matched Implementations**: {report['coverage_analysis']['matched_implementations']}
- **Orphaned Implementations**: {report['coverage_analysis']['orphaned_implementations']}
- **Coverage Percentage**: {report['coverage_analysis']['coverage_percentage']:.1f}%

## Priority Distribution

- **High Priority**: {report['priority_distribution']['high_priority_orphans']} orphans
- **Medium Priority**: {report['priority_distribution']['medium_priority_orphans']} orphans  
- **Low Priority**: {report['priority_distribution']['low_priority_orphans']} orphans

## Semantic Matches Found

"""
        
        for i, match in enumerate(report['semantic_matches'], 1):
            md += f"""
### {i}. {match['confidence']:.1%} Confidence Match

- **Spec**: `{match['spec_path']}`
- **Implementation**: `{match['impl_path']}`
- **Reasons**: {', '.join(match['match_reasons'])}
- **Semantic Keywords**: {', '.join(match['semantic_keywords'])}
- **Domain Keywords**: {', '.join(match['domain_keywords'])}

"""
        
        md += f"""
## Orphaned Solutions Requiring Specifications

"""
        
        for i, orphan in enumerate(report['orphaned_solutions'], 1):
            priority_emoji = "🚨" if orphan['priority'] == 1 else "⚠️" if orphan['priority'] == 2 else "ℹ️"
            priority_text = "HIGH" if orphan['priority'] == 1 else "MEDIUM" if orphan['priority'] == 2 else "LOW"
            
            md += f"""
### {i}. {priority_emoji} {priority_text} PRIORITY

- **Implementation**: `{orphan['implementation_path']}`
- **File Type**: {orphan['file_type']}
- **Size**: {orphan['size_lines']} lines
- **Complexity Score**: {orphan['complexity_score']}
- **Suggested Spec Location**: `{orphan['suggested_spec_location']}`
- **Estimated Effort**: {orphan['estimated_effort_hours']} hours

"""
        
        md += f"""
## Recommendations

{chr(10).join(f'- {rec}' for rec in report['recommendations'])}

## Next Steps

1. **Immediate**: Address high-priority orphaned solutions
2. **Short-term**: Create specifications for medium-priority orphans
3. **Long-term**: Establish governance process to prevent future orphans

---

*This report was generated by the Semantic Orphaned Solutions Scanner using advanced semantic matching algorithms.*
"""
        
        return md


def main():
    """Main entry point for semantic orphaned scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic Orphaned Solutions Scanner")
    parser.add_argument("--chunked", action="store_true", help="Run in chunked mode for large repositories")
    parser.add_argument("--chunk-size", type=int, default=50, help="Number of implementations per chunk")
    parser.add_argument("--repository", default=".", help="Repository path to scan")
    
    args = parser.parse_args()
    
    scanner = SemanticOrphanedScanner(args.repository)
    
    if args.chunked:
        print(f"🔍 Running chunked semantic scan (chunk size: {args.chunk_size})")
        report = scanner.scan_repository_chunked(args.chunk_size)
    else:
        print("🔍 Running full semantic scan")
        report = scanner.scan_repository()
    
    # Save reports
    json_file = scanner.save_report(report)
    md_file = scanner.generate_markdown_report(report)
    
    # Print summary
    print(f"\n📊 Semantic Scan Results:")
    print(f"   Coverage: {report['coverage_analysis']['coverage_percentage']:.1f}%")
    print(f"   Orphaned Solutions: {report['coverage_analysis']['orphaned_implementations']}")
    print(f"   High Priority: {report['priority_distribution']['high_priority_orphans']}")
    print(f"   Total Effort: {report['effort_estimation']['total_estimated_hours']} hours")
    
    if report['recommendations']:
        print(f"\n💡 Top Recommendations:")
        for rec in report['recommendations'][:3]:
            print(f"   - {rec}")
    
    print(f"\n📄 Reports saved:")
    print(f"   JSON: {json_file}")
    print(f"   Markdown: {md_file}")
    
    return report


if __name__ == "__main__":
    main()