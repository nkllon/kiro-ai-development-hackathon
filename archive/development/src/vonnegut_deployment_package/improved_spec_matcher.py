#!/usr/bin/env python3
"""
Improved Spec-Implementation Matcher
===================================

Enhanced deterministic matching logic that focuses on semantic relationships
rather than just path and name similarity.
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class SemanticMatch:
    """A semantic match between spec and implementation."""
    spec_path: str
    impl_path: str
    confidence: float
    semantic_keywords: List[str]
    domain_keywords: List[str]
    functional_keywords: List[str]
    technical_keywords: List[str]
    match_reasons: List[str]


class ImprovedSpecMatcher:
    """
    Enhanced spec-implementation matcher using semantic analysis.
    """
    
    def __init__(self):
        # Define semantic keyword groups for better matching
        self.domain_keywords = {
            'governance': ['governance', 'compliance', 'audit', 'policy', 'rule', 'validation', 'check'],
            'orchestration': ['orchestration', 'orchestrator', 'workflow', 'pipeline', 'dag', 'task', 'job'],
            'testing': ['test', 'testing', 'pytest', 'unittest', 'validation', 'verify', 'check'],
            'monitoring': ['monitor', 'monitoring', 'health', 'status', 'metrics', 'observability'],
            'infrastructure': ['infrastructure', 'deploy', 'deployment', 'service', 'system', 'server'],
            'makefile': ['makefile', 'make', 'target', 'build', 'compile', 'automation'],
            'framework': ['framework', 'engine', 'system', 'platform', 'architecture'],
            'scheduling': ['scheduler', 'schedule', 'daemon', 'background', 'cron', 'periodic'],
            'analysis': ['analyzer', 'analysis', 'scanner', 'scan', 'discovery', 'detection']
        }
        
        self.functional_keywords = {
            'creation': ['create', 'generate', 'build', 'make', 'construct'],
            'execution': ['run', 'execute', 'start', 'launch', 'invoke'],
            'management': ['manage', 'control', 'handle', 'process', 'operate'],
            'validation': ['validate', 'verify', 'check', 'test', 'audit'],
            'monitoring': ['monitor', 'watch', 'track', 'observe', 'report'],
            'configuration': ['config', 'configure', 'setup', 'initialize', 'prepare']
        }
        
        self.technical_keywords = {
            'python': ['python', 'py', 'class', 'function', 'method', 'module'],
            'makefile': ['makefile', 'mk', 'target', 'phony', 'recipe'],
            'async': ['async', 'await', 'asyncio', 'concurrent', 'parallel'],
            'data': ['json', 'yaml', 'csv', 'data', 'config', 'settings'],
            'web': ['http', 'api', 'rest', 'endpoint', 'server', 'client'],
            'file': ['file', 'path', 'directory', 'folder', 'io', 'read', 'write']
        }
    
    def find_matches(self, spec_files: List[Path], impl_files: List[Path]) -> List[SemanticMatch]:
        """Find semantic matches between specs and implementations."""
        matches = []
        
        for spec_file in spec_files:
            spec_analysis = self._analyze_spec_file(spec_file)
            
            for impl_file in impl_files:
                impl_analysis = self._analyze_impl_file(impl_file)
                
                match = self._calculate_semantic_match(spec_file, impl_file, spec_analysis, impl_analysis)
                
                if match.confidence > 0.3:  # Threshold for considering a match
                    matches.append(match)
        
        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        return matches
    
    def _analyze_spec_file(self, spec_file: Path) -> Dict:
        """Analyze specification file for semantic content."""
        try:
            # Try multiple encodings to handle problematic files
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    content = spec_file.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # Last resort: read as bytes and decode with errors='ignore'
                content = spec_file.read_text(encoding='utf-8', errors='ignore')
            
            analysis = {
                'file_path': str(spec_file),
                'raw_keywords': self._extract_raw_keywords(content),
                'domain_keywords': self._extract_domain_keywords(content),
                'functional_keywords': self._extract_functional_keywords(content),
                'technical_keywords': self._extract_technical_keywords(content),
                'user_stories': self._extract_user_stories(content),
                'acceptance_criteria': self._extract_acceptance_criteria(content),
                'system_components': self._extract_system_components(content)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spec {spec_file}: {e}")
            return {'file_path': str(spec_file), 'raw_keywords': [], 'domain_keywords': [], 
                   'functional_keywords': [], 'technical_keywords': [], 'user_stories': [],
                   'acceptance_criteria': [], 'system_components': []}
    
    def _analyze_impl_file(self, impl_file: Path) -> Dict:
        """Analyze implementation file for semantic content."""
        try:
            # Try multiple encodings to handle problematic files
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    content = impl_file.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # Last resort: read as bytes and decode with errors='ignore'
                content = impl_file.read_text(encoding='utf-8', errors='ignore')
            
            analysis = {
                'file_path': str(impl_file),
                'raw_keywords': self._extract_raw_keywords(content),
                'domain_keywords': self._extract_domain_keywords(content),
                'functional_keywords': self._extract_functional_keywords(content),
                'technical_keywords': self._extract_technical_keywords(content),
                'class_names': [],
                'function_names': [],
                'imports': [],
                'targets': []  # For Makefiles
            }
            
            # File-type specific analysis
            if impl_file.suffix == '.py':
                python_analysis = self._analyze_python_file(content)
                analysis.update(python_analysis)
            elif impl_file.suffix == '.mk' or impl_file.name.endswith('Makefile'):
                makefile_analysis = self._analyze_makefile(content)
                analysis.update(makefile_analysis)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing impl {impl_file}: {e}")
            return {'file_path': str(impl_file), 'raw_keywords': [], 'domain_keywords': [], 
                   'functional_keywords': [], 'technical_keywords': [], 'class_names': [],
                   'function_names': [], 'imports': [], 'targets': []}
    
    def _extract_raw_keywords(self, content: str) -> List[str]:
        """Extract raw keywords from content."""
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
        
        # Extract identifiers
        identifiers = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]*\b', content)
        keywords.extend(identifiers)
        
        # Clean and normalize
        cleaned = []
        for keyword in keywords:
            clean = re.sub(r'[^\w\s]', '', keyword.lower().strip())
            if clean and len(clean) > 2:
                cleaned.append(clean)
        
        return list(set(cleaned))
    
    def _extract_domain_keywords(self, content: str) -> List[str]:
        """Extract domain-specific keywords."""
        found_keywords = []
        content_lower = content.lower()
        
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found_keywords.append(f"{domain}:{keyword}")
        
        return found_keywords
    
    def _extract_functional_keywords(self, content: str) -> List[str]:
        """Extract functional keywords."""
        found_keywords = []
        content_lower = content.lower()
        
        for function, keywords in self.functional_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found_keywords.append(f"{function}:{keyword}")
        
        return found_keywords
    
    def _extract_technical_keywords(self, content: str) -> List[str]:
        """Extract technical keywords."""
        found_keywords = []
        content_lower = content.lower()
        
        for tech, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found_keywords.append(f"{tech}:{keyword}")
        
        return found_keywords
    
    def _extract_user_stories(self, content: str) -> List[str]:
        """Extract user stories from spec content."""
        user_stories = re.findall(r'As a ([^,]+), I want ([^,]+), so that ([^.]+)', content, re.IGNORECASE)
        return [f"{role}|{want}|{benefit}" for role, want, benefit in user_stories]
    
    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract acceptance criteria from spec content."""
        criteria = re.findall(r'WHEN ([^T]+) THEN ([^S]+) SHALL ([^.]+)', content, re.IGNORECASE)
        return [f"{when}|{then}|{shall}" for when, then, shall in criteria]
    
    def _extract_system_components(self, content: str) -> List[str]:
        """Extract system component names from spec content."""
        # Look for capitalized system names
        components = re.findall(r'\b([A-Z][a-zA-Z]*(?:System|Engine|Manager|Orchestrator|Framework|Service))\b', content)
        
        # Look for specific patterns
        patterns = [
            r'Observatory',
            r'Beast Mode',
            r'DAG Orchestration',
            r'Infrastructure',
            r'Makefile System',
            r'Governance'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            components.extend(matches)
        
        return list(set(components))
    
    def _analyze_python_file(self, content: str) -> Dict:
        """Analyze Python file specifically."""
        analysis = {
            'class_names': [],
            'function_names': [],
            'imports': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['class_names'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    analysis['function_names'].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
        except:
            pass
        
        return analysis
    
    def _analyze_makefile(self, content: str) -> Dict:
        """Analyze Makefile specifically."""
        analysis = {
            'targets': [],
            'variables': []
        }
        
        # Extract targets
        targets = re.findall(r'^([a-zA-Z][a-zA-Z0-9_-]*)\s*:', content, re.MULTILINE)
        analysis['targets'] = targets
        
        # Extract variables
        variables = re.findall(r'^([A-Z_]+)\s*[?:]?=', content, re.MULTILINE)
        analysis['variables'] = variables
        
        return analysis
    
    def _calculate_semantic_match(self, spec_file: Path, impl_file: Path, 
                                spec_analysis: Dict, impl_analysis: Dict) -> SemanticMatch:
        """Calculate semantic match between spec and implementation."""
        
        # Calculate keyword overlaps
        domain_overlap = self._calculate_overlap(spec_analysis['domain_keywords'], impl_analysis['domain_keywords'])
        functional_overlap = self._calculate_overlap(spec_analysis['functional_keywords'], impl_analysis['functional_keywords'])
        technical_overlap = self._calculate_overlap(spec_analysis['technical_keywords'], impl_analysis['technical_keywords'])
        raw_overlap = self._calculate_overlap(spec_analysis['raw_keywords'], impl_analysis['raw_keywords'])
        
        # Calculate component-specific matches
        component_matches = self._find_component_matches(spec_analysis, impl_analysis)
        
        # Calculate confidence score with weighted components
        confidence = (
            domain_overlap * 0.4 +      # Domain keywords are most important
            functional_overlap * 0.25 + # Functional keywords are important
            technical_overlap * 0.15 +  # Technical keywords help
            raw_overlap * 0.1 +         # Raw keywords provide baseline
            component_matches * 0.1     # Component matches are bonus
        )
        
        # Generate match reasons
        match_reasons = []
        if domain_overlap > 0.3:
            match_reasons.append(f"Strong domain keyword overlap ({domain_overlap:.1%})")
        if functional_overlap > 0.3:
            match_reasons.append(f"Strong functional keyword overlap ({functional_overlap:.1%})")
        if technical_overlap > 0.3:
            match_reasons.append(f"Strong technical keyword overlap ({technical_overlap:.1%})")
        if component_matches > 0.3:
            match_reasons.append(f"Component name matches ({component_matches:.1%})")
        
        # Find specific matching keywords
        semantic_keywords = list(set(spec_analysis['domain_keywords']).intersection(set(impl_analysis['domain_keywords'])))
        domain_keywords = list(set(spec_analysis['functional_keywords']).intersection(set(impl_analysis['functional_keywords'])))
        functional_keywords = list(set(spec_analysis['technical_keywords']).intersection(set(impl_analysis['technical_keywords'])))
        technical_keywords = list(set(spec_analysis['raw_keywords']).intersection(set(impl_analysis['raw_keywords'])))
        
        return SemanticMatch(
            spec_path=str(spec_file),
            impl_path=str(impl_file),
            confidence=min(confidence, 1.0),
            semantic_keywords=semantic_keywords,
            domain_keywords=domain_keywords,
            functional_keywords=functional_keywords,
            technical_keywords=technical_keywords[:10],  # Limit to top 10
            match_reasons=match_reasons
        )
    
    def _calculate_overlap(self, list1: List[str], list2: List[str]) -> float:
        """Calculate overlap ratio between two lists."""
        if not list1 or not list2:
            return 0.0
        
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _find_component_matches(self, spec_analysis: Dict, impl_analysis: Dict) -> float:
        """Find matches between system components mentioned in spec and implementation."""
        spec_components = set(comp.lower() for comp in spec_analysis.get('system_components', []))
        
        # Check implementation for component references
        impl_components = set()
        
        # Add class names
        for class_name in impl_analysis.get('class_names', []):
            impl_components.add(class_name.lower())
        
        # Add function names
        for func_name in impl_analysis.get('function_names', []):
            impl_components.add(func_name.lower())
        
        # Add targets (for Makefiles)
        for target in impl_analysis.get('targets', []):
            impl_components.add(target.lower())
        
        # Add file path components
        impl_path = Path(impl_analysis['file_path'])
        for part in impl_path.parts:
            impl_components.add(part.lower())
        
        if not spec_components or not impl_components:
            return 0.0
        
        intersection = spec_components.intersection(impl_components)
        return len(intersection) / max(len(spec_components), len(impl_components))


def test_improved_matcher():
    """Test the improved matcher with our known pairs."""
    matcher = ImprovedSpecMatcher()
    
    # Test with our known pairs
    spec_files = [
        Path(".kiro/specs/comprehensive-makefile-system/requirements.md"),
        Path(".kiro/specs/comprehensive-makefile-system/design.md")
    ]
    
    impl_files = [
        Path("makefiles/governance.mk"),
        Path("scripts/background_governance_scheduler.py"),
        Path("scripts/orphaned_solution_scanner.py")
    ]
    
    # Filter to existing files
    existing_specs = [f for f in spec_files if f.exists()]
    existing_impls = [f for f in impl_files if f.exists()]
    
    print(f"🔍 Testing improved matcher with {len(existing_specs)} specs and {len(existing_impls)} implementations")
    
    matches = matcher.find_matches(existing_specs, existing_impls)
    
    print(f"\n📊 Found {len(matches)} potential matches:")
    
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match.confidence:.1%} confidence")
        print(f"   Spec: {match.spec_path}")
        print(f"   Impl: {match.impl_path}")
        print(f"   Reasons: {', '.join(match.match_reasons)}")
        print(f"   Domain keywords: {len(match.domain_keywords)} matches")
        print(f"   Functional keywords: {len(match.functional_keywords)} matches")
        print(f"   Technical keywords: {len(match.technical_keywords)} matches")
        
        if match.semantic_keywords:
            print(f"   Semantic matches: {', '.join(match.semantic_keywords[:5])}")
    
    return matches


if __name__ == "__main__":
    test_improved_matcher()