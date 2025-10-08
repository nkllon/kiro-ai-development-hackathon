#!/usr/bin/env python3
"""
Spec-Implementation Validator
============================

Validates that our deterministic matching logic correctly identifies
known spec-implementation pairs. This helps us tune the matching
algorithms before deploying the orphaned solutions scanner.
"""

import ast
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class KnownPair:
    """A known spec-implementation pair for validation."""
    spec_path: str
    implementation_path: str
    relationship_type: str  # "direct", "partial", "related"
    confidence_expected: float  # What confidence score we expect
    notes: str = ""


@dataclass
class ValidationResult:
    """Result of validating a known pair."""
    pair: KnownPair
    detected: bool
    confidence_score: float
    confidence_delta: float  # difference from expected
    matching_keywords: List[str]
    path_similarity: float
    name_similarity: float
    issues: List[str]


class SpecImplementationValidator:
    """
    Validates spec-implementation matching logic using known pairs.
    """
    
    def __init__(self, repository_path: str = "."):
        self.repository_path = Path(repository_path)
        
        # Define known spec-implementation pairs for validation
        self.known_pairs = [
            KnownPair(
                spec_path=".kiro/specs/comprehensive-makefile-system/requirements.md",
                implementation_path="makefiles/governance.mk",
                relationship_type="direct",
                confidence_expected=0.8,
                notes="Makefile system spec should match governance makefile"
            ),
            KnownPair(
                spec_path=".kiro/specs/comprehensive-makefile-system/design.md",
                implementation_path="scripts/background_governance_scheduler.py",
                relationship_type="partial",
                confidence_expected=0.6,
                notes="Design should partially match scheduler implementation"
            ),
            # Add more known pairs as we discover them
        ]
    
    def validate_all_pairs(self) -> List[ValidationResult]:
        """Validate all known pairs and return results."""
        results = []
        
        for pair in self.known_pairs:
            result = self._validate_pair(pair)
            results.append(result)
        
        return results
    
    def _validate_pair(self, pair: KnownPair) -> ValidationResult:
        """Validate a single known pair."""
        issues = []
        
        # Check if files exist
        spec_file = self.repository_path / pair.spec_path
        impl_file = self.repository_path / pair.implementation_path
        
        if not spec_file.exists():
            issues.append(f"Spec file not found: {pair.spec_path}")
        if not impl_file.exists():
            issues.append(f"Implementation file not found: {pair.implementation_path}")
        
        if issues:
            return ValidationResult(
                pair=pair,
                detected=False,
                confidence_score=0.0,
                confidence_delta=-pair.confidence_expected,
                matching_keywords=[],
                path_similarity=0.0,
                name_similarity=0.0,
                issues=issues
            )
        
        # Extract keywords and calculate similarities
        spec_keywords = self._extract_spec_keywords(spec_file)
        impl_keywords = self._extract_impl_keywords(impl_file)
        
        matching_keywords = list(set(spec_keywords).intersection(set(impl_keywords)))
        path_similarity = self._calculate_path_similarity(pair.spec_path, pair.implementation_path)
        name_similarity = self._calculate_name_similarity(pair.spec_path, pair.implementation_path)
        
        # Calculate overall confidence score using our matching logic
        confidence_score = self._calculate_confidence_score(
            spec_keywords, impl_keywords, path_similarity, name_similarity
        )
        
        # Determine if pair was "detected" (confidence above threshold)
        detected = confidence_score >= 0.3  # Same threshold as in scanner
        
        confidence_delta = confidence_score - pair.confidence_expected
        
        return ValidationResult(
            pair=pair,
            detected=detected,
            confidence_score=confidence_score,
            confidence_delta=confidence_delta,
            matching_keywords=matching_keywords,
            path_similarity=path_similarity,
            name_similarity=name_similarity,
            issues=issues
        )
    
    def _extract_spec_keywords(self, spec_file: Path) -> List[str]:
        """Extract keywords from specification file."""
        try:
            content = spec_file.read_text(encoding='utf-8')
            keywords = []
            
            # Extract from headers
            headers = re.findall(r'^#+\s*(.+)$', content, re.MULTILINE)
            keywords.extend(headers)
            
            # Extract from bold text
            bold_text = re.findall(r'\*\*([^*]+)\*\*', content)
            keywords.extend(bold_text)
            
            # Extract from code blocks
            code_blocks = re.findall(r'`([^`]+)`', content)
            keywords.extend(code_blocks)
            
            # Extract technical terms
            tech_terms = re.findall(
                r'\b(makefile|governance|orchestrat|schedul|task|test|system|framework|engine|manager|controller)\w*\b', 
                content, re.IGNORECASE
            )
            keywords.extend(tech_terms)
            
            # Extract from filename
            filename_parts = spec_file.stem.split('-')
            keywords.extend(filename_parts)
            
            # Clean and normalize keywords
            cleaned_keywords = []
            for keyword in keywords:
                cleaned = re.sub(r'[^\w\s]', '', keyword.lower().strip())
                if cleaned and len(cleaned) > 2:
                    cleaned_keywords.append(cleaned)
            
            return list(set(cleaned_keywords))
            
        except Exception as e:
            print(f"Error extracting spec keywords from {spec_file}: {e}")
            return []
    
    def _extract_impl_keywords(self, impl_file: Path) -> List[str]:
        """Extract keywords from implementation file."""
        try:
            content = impl_file.read_text(encoding='utf-8')
            keywords = []
            
            # Handle different file types
            if impl_file.suffix == '.py':
                keywords.extend(self._extract_python_keywords(content))
            elif impl_file.suffix == '.mk' or impl_file.name.endswith('Makefile'):
                keywords.extend(self._extract_makefile_keywords(content))
            else:
                # Generic text extraction
                keywords.extend(self._extract_generic_keywords(content))
            
            # Extract from filename and path
            path_parts = impl_file.parts
            keywords.extend(path_parts)
            
            filename_parts = impl_file.stem.split('_')
            keywords.extend(filename_parts)
            
            # Clean and normalize keywords
            cleaned_keywords = []
            for keyword in keywords:
                cleaned = re.sub(r'[^\w\s]', '', str(keyword).lower().strip())
                if cleaned and len(cleaned) > 2:
                    cleaned_keywords.append(cleaned)
            
            return list(set(cleaned_keywords))
            
        except Exception as e:
            print(f"Error extracting impl keywords from {impl_file}: {e}")
            return []
    
    def _extract_python_keywords(self, content: str) -> List[str]:
        """Extract keywords from Python code."""
        keywords = []
        
        try:
            tree = ast.parse(content)
            
            # Extract class and function names
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    keywords.append(node.name)
                    # Split CamelCase
                    camel_parts = re.findall(r'[A-Z][a-z]*', node.name)
                    keywords.extend(camel_parts)
                elif isinstance(node, ast.FunctionDef):
                    keywords.append(node.name)
                    # Split snake_case
                    snake_parts = node.name.split('_')
                    keywords.extend(snake_parts)
        except:
            pass
        
        # Extract from comments and docstrings
        comments = re.findall(r'#\s*(.+)', content)
        keywords.extend(comments)
        
        docstrings = re.findall(r'"""([^"]+)"""', content, re.DOTALL)
        keywords.extend(docstrings)
        
        # Extract imports
        imports = re.findall(r'from\s+([^\s]+)\s+import|import\s+([^\s]+)', content)
        for imp in imports:
            keywords.extend([i for i in imp if i])
        
        return keywords
    
    def _extract_makefile_keywords(self, content: str) -> List[str]:
        """Extract keywords from Makefile content."""
        keywords = []
        
        # Extract target names
        targets = re.findall(r'^([a-zA-Z][a-zA-Z0-9_-]*)\s*:', content, re.MULTILINE)
        keywords.extend(targets)
        
        # Extract variable names
        variables = re.findall(r'^([A-Z_]+)\s*[?:]?=', content, re.MULTILINE)
        keywords.extend(variables)
        
        # Extract from comments
        comments = re.findall(r'#\s*(.+)', content)
        keywords.extend(comments)
        
        # Extract common makefile terms
        makefile_terms = re.findall(
            r'\b(test|build|clean|install|deploy|run|start|stop|check|validate|governance)\b', 
            content, re.IGNORECASE
        )
        keywords.extend(makefile_terms)
        
        return keywords
    
    def _extract_generic_keywords(self, content: str) -> List[str]:
        """Extract keywords from generic text content."""
        keywords = []
        
        # Extract words that look like identifiers
        identifiers = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]*\b', content)
        keywords.extend(identifiers)
        
        return keywords
    
    def _calculate_path_similarity(self, spec_path: str, impl_path: str) -> float:
        """Calculate similarity between spec and implementation paths."""
        spec_parts = set(Path(spec_path).parts)
        impl_parts = set(Path(impl_path).parts)
        
        if not spec_parts or not impl_parts:
            return 0.0
        
        intersection = spec_parts.intersection(impl_parts)
        union = spec_parts.union(impl_parts)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_name_similarity(self, spec_path: str, impl_path: str) -> float:
        """Calculate name similarity between spec and implementation."""
        spec_name = Path(spec_path).stem
        impl_name = Path(impl_path).stem
        
        # Convert to word sets
        spec_words = set(re.findall(r'\w+', spec_name.lower()))
        impl_words = set(re.findall(r'\w+', impl_name.lower()))
        
        if not spec_words or not impl_words:
            return 0.0
        
        intersection = spec_words.intersection(impl_words)
        union = spec_words.union(impl_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_confidence_score(self, spec_keywords: List[str], impl_keywords: List[str], 
                                  path_similarity: float, name_similarity: float) -> float:
        """Calculate confidence score using our matching logic."""
        # Keyword matching score
        spec_set = set(kw.lower() for kw in spec_keywords)
        impl_set = set(kw.lower() for kw in impl_keywords)
        
        if not spec_set or not impl_set:
            keyword_score = 0.0
        else:
            intersection = spec_set.intersection(impl_set)
            keyword_score = len(intersection) / min(len(spec_set), len(impl_set))
        
        # Weighted combination (same as in scanner)
        confidence_score = (
            keyword_score * 0.4 +      # 40% keyword matching
            path_similarity * 0.3 +    # 30% path similarity  
            name_similarity * 0.3      # 30% name similarity
        )
        
        return min(confidence_score, 1.0)
    
    def generate_validation_report(self, results: List[ValidationResult]) -> Dict:
        """Generate comprehensive validation report."""
        total_pairs = len(results)
        detected_pairs = len([r for r in results if r.detected])
        
        # Calculate accuracy metrics
        true_positives = len([r for r in results if r.detected and r.pair.relationship_type in ["direct", "partial"]])
        false_negatives = len([r for r in results if not r.detected and r.pair.relationship_type in ["direct", "partial"]])
        
        precision = true_positives / detected_pairs if detected_pairs > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Confidence score analysis
        confidence_scores = [r.confidence_score for r in results]
        confidence_deltas = [r.confidence_delta for r in results]
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        avg_delta = sum(confidence_deltas) / len(confidence_deltas) if confidence_deltas else 0.0
        
        # Issues analysis
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        report = {
            'summary': {
                'total_pairs': total_pairs,
                'detected_pairs': detected_pairs,
                'detection_rate': detected_pairs / total_pairs if total_pairs > 0 else 0.0,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score
            },
            'confidence_analysis': {
                'average_confidence': avg_confidence,
                'average_delta': avg_delta,
                'confidence_scores': confidence_scores,
                'confidence_deltas': confidence_deltas
            },
            'issues': {
                'total_issues': len(all_issues),
                'issue_counts': issue_counts
            },
            'detailed_results': [asdict(result) for result in results],
            'recommendations': self._generate_recommendations(results)
        }
        
        return report
    
    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Analyze common issues
        low_confidence_results = [r for r in results if r.confidence_score < r.pair.confidence_expected]
        high_delta_results = [r for r in results if abs(r.confidence_delta) > 0.3]
        
        if low_confidence_results:
            recommendations.append(f"Improve matching for {len(low_confidence_results)} pairs with low confidence scores")
        
        if high_delta_results:
            recommendations.append(f"Adjust confidence calculation for {len(high_delta_results)} pairs with high deltas")
        
        # Analyze keyword matching effectiveness
        keyword_scores = []
        for result in results:
            if result.pair.spec_path and result.pair.implementation_path:
                spec_file = self.repository_path / result.pair.spec_path
                impl_file = self.repository_path / result.pair.implementation_path
                if spec_file.exists() and impl_file.exists():
                    keyword_match_ratio = len(result.matching_keywords) / max(1, len(result.matching_keywords) + 5)  # Rough estimate
                    keyword_scores.append(keyword_match_ratio)
        
        if keyword_scores and sum(keyword_scores) / len(keyword_scores) < 0.3:
            recommendations.append("Improve keyword extraction algorithms - low keyword matching rates detected")
        
        # Path similarity analysis
        path_similarities = [r.path_similarity for r in results]
        if path_similarities and sum(path_similarities) / len(path_similarities) < 0.2:
            recommendations.append("Improve path similarity calculation - paths not matching well")
        
        # Name similarity analysis  
        name_similarities = [r.name_similarity for r in results]
        if name_similarities and sum(name_similarities) / len(name_similarities) < 0.2:
            recommendations.append("Improve name similarity calculation - names not matching well")
        
        return recommendations
    
    def save_validation_report(self, report: Dict, output_path: str = "reports/validation_report.json"):
        """Save validation report to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Validation report saved to {output_file}")
    
    def generate_markdown_report(self, report: Dict, output_path: str = "reports/validation_report.md"):
        """Generate human-readable markdown validation report."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = f"""
# Spec-Implementation Matching Validation Report

## Summary

- **Total Pairs Tested**: {report['summary']['total_pairs']}
- **Detection Rate**: {report['summary']['detection_rate']:.1%}
- **Precision**: {report['summary']['precision']:.1%}
- **Recall**: {report['summary']['recall']:.1%}
- **F1 Score**: {report['summary']['f1_score']:.3f}

## Confidence Analysis

- **Average Confidence**: {report['confidence_analysis']['average_confidence']:.3f}
- **Average Delta**: {report['confidence_analysis']['average_delta']:.3f}

## Detailed Results

"""
        
        for i, result in enumerate(report['detailed_results'], 1):
            pair = result['pair']
            status = "✅ DETECTED" if result['detected'] else "❌ MISSED"
            
            md_content += f"""
### {i}. {status} - {pair['relationship_type'].title()} Relationship

- **Spec**: `{pair['spec_path']}`
- **Implementation**: `{pair['implementation_path']}`
- **Expected Confidence**: {pair['confidence_expected']:.3f}
- **Actual Confidence**: {result['confidence_score']:.3f}
- **Delta**: {result['confidence_delta']:+.3f}
- **Path Similarity**: {result['path_similarity']:.3f}
- **Name Similarity**: {result['name_similarity']:.3f}
- **Matching Keywords**: {len(result['matching_keywords'])} keywords
- **Issues**: {len(result['issues'])} issues

"""
            
            if result['matching_keywords']:
                md_content += f"**Keywords**: {', '.join(result['matching_keywords'][:10])}\n\n"
            
            if result['issues']:
                md_content += f"**Issues**: {'; '.join(result['issues'])}\n\n"
        
        md_content += f"""
## Issues Summary

- **Total Issues**: {report['issues']['total_issues']}

"""
        
        for issue, count in report['issues']['issue_counts'].items():
            md_content += f"- {issue}: {count} occurrences\n"
        
        md_content += f"""

## Recommendations

{chr(10).join(f'- {rec}' for rec in report['recommendations'])}

---

*This validation report helps tune the deterministic spec-implementation matching algorithms.*
"""
        
        with open(output_file, 'w') as f:
            f.write(md_content)
        
        print(f"Markdown validation report saved to {output_file}")


def main():
    """Main entry point for validation."""
    validator = SpecImplementationValidator()
    
    print("🔍 Validating spec-implementation matching logic...")
    results = validator.validate_all_pairs()
    
    print(f"📊 Validation complete - tested {len(results)} known pairs")
    
    # Generate comprehensive report
    report = validator.generate_validation_report(results)
    
    # Save reports
    validator.save_validation_report(report)
    validator.generate_markdown_report(report)
    
    # Print summary
    print(f"\n📈 Validation Results:")
    print(f"   Detection Rate: {report['summary']['detection_rate']:.1%}")
    print(f"   Precision: {report['summary']['precision']:.1%}")
    print(f"   Recall: {report['summary']['recall']:.1%}")
    print(f"   F1 Score: {report['summary']['f1_score']:.3f}")
    print(f"   Average Confidence: {report['confidence_analysis']['average_confidence']:.3f}")
    
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
    
    return report


if __name__ == "__main__":
    main()