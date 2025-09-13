"""
Design Validator Core Core Core

This module was extracted from design_validator_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Design_Validator - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for design_validator.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/beast_mode/compliance/rdi/design_validator_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.459518
"""



import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity

class ComponentType(Enum):
    """Types of design components that can be validated."""
    CLASS = 'class'
    FUNCTION = 'function'
    METHOD = 'method'
    MODULE = 'module'
    INTERFACE = 'interface'
    DATA_MODEL = 'data_model'

@dataclass
class DesignComponent:
    """Represents a component defined in design documents."""
    name: str
    component_type: ComponentType
    description: str
    methods: List[str]
    attributes: List[str]
    file_path: str
    line_number: int
    metadata: Dict[str, Any]

@dataclass
class ImplementationComponent:
    """Represents a component found in implementation code."""
    name: str
    component_type: ComponentType
    methods: List[str]
    attributes: List[str]
    file_path: str
    line_number: int
    docstring: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class AlignmentResult:
    """Results of design-implementation alignment analysis."""
    total_design_components: int
    implemented_components: int
    missing_implementations: List[DesignComponent]
    extra_implementations: List[ImplementationComponent]
    misaligned_components: List[Tuple[DesignComponent, ImplementationComponent]]
    alignment_score: float
    issues: List[ComplianceIssue]

class DesignValidator(ComplianceValidator):
    """
    Validates implementation alignment with design specifications.
    
    This class validates that:
    1. All design components have corresponding implementations
    2. Implementations match design specifications
    3. No unauthorized implementations exist
    4. Component interfaces match design specifications
    """

    def __init__(self, repository_path: str):
        """
        Initialize the DesignValidator.
        
        Args:
            repository_path: Path to the repository root
        """
        self.repository_path = Path(repository_path)
        self.design_cache: Optional[Dict[str, DesignComponent]] = None
        self.implementation_cache: Optional[Dict[str, ImplementationComponent]] = None

    def validate(self, target: str) -> List[ComplianceIssue]:
        """
        Validate design-implementation alignment for the given target.
        
        Args:
            target: Path to analyze (file or directory)
            
        Returns:
            List of compliance issues found
        """
        target_path = Path(target) if isinstance(target, str) else target
        if self.design_cache is None:
            self.design_cache = self._load_design_components()
        if self.implementation_cache is None:
            self.implementation_cache = self._load_implementation_components(target_path)
        alignment_result = self._analyze_alignment()
        return alignment_result.issues

    def get_validator_name(self) -> str:
        """Get the name of this validator."""
        return 'DesignValidator'

    def analyze_alignment(self, target_path: Optional[str]=None) -> AlignmentResult:
        """
        Perform comprehensive design-implementation alignment analysis.
        
        Args:
            target_path: Specific path to analyze, or None for full repository
            
        Returns:
            Detailed alignment analysis results
        """
        if self.design_cache is None:
            self.design_cache = self._load_design_components()
        analysis_path = Path(target_path) if target_path else self.repository_path
        if self.implementation_cache is None:
            self.implementation_cache = self._load_implementation_components(analysis_path)
        return self._analyze_alignment()

    def _load_design_components(self) -> Dict[str, DesignComponent]:
        """
        Load all design components from design documents.
        
        Returns:
            Dictionary mapping component names to design components
        """
        components = {}
        design_files = []
        for pattern in ['**/design.md', '**/design/*.md', '**/*design*.md']:
            design_files.extend(self.repository_path.glob(pattern))
        for design_file in design_files:
            try:
                file_components = self._parse_design_file(design_file)
                components.update(file_components)
            except Exception as e:
                print(f'Warning: Failed to parse design file {design_file}: {e}')
        return components

    def _parse_design_file(self, file_path: Path) -> Dict[str, DesignComponent]:
        """
        Parse a design document to extract component definitions.
        
        Args:
            file_path: Path to the design file
            
        Returns:
            Dictionary of design components
        """
        components = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return components
        current_component = None
        in_code_block = False
        code_block_content = []
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if line_stripped.startswith('```'):
                if in_code_block:
                    if code_block_content:
                        parsed_components = self._parse_code_block(code_block_content, file_path, line_num)
                        if current_component and current_component.name in parsed_components:
                            code_component = parsed_components[current_component.name]
                            current_component.methods = code_component.methods
                            current_component.attributes = code_component.attributes
                            current_component.metadata.update(code_component.metadata)
                        else:
                            components.update(parsed_components)
                    code_block_content = []
                in_code_block = not in_code_block
                continue
            if in_code_block:
                code_block_content.append(line)
                continue
            component_match = self._match_component_header(line_stripped)
            if component_match:
                if current_component:
                    components[current_component.name] = current_component
                component_name, component_type = component_match
                current_component = DesignComponent(name=component_name, component_type=component_type, description='', methods=[], attributes=[], file_path=str(file_path), line_number=line_num, metadata={})
            elif current_component and line_stripped:
                if line_stripped.startswith('**Purpose**:') or line_stripped.startswith('Purpose:'):
                    current_component.description = line_stripped
        if current_component:
            components[current_component.name] = current_component
        return components

    def _match_component_header(self, line: str) -> Optional[Tuple[str, ComponentType]]:
        """
        Match component headers in design documents.
        
        Args:
            line: Line to check for component headers
            
        Returns:
            Tuple of (component_name, component_type) if matched, None otherwise
        """
        class_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+class|\\s+Class)', line, re.IGNORECASE)
        if class_match:
            return (class_match.group(1), ComponentType.CLASS)
        interface_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+interface|\\s+Interface)', line, re.IGNORECASE)
        if interface_match:
            return (interface_match.group(1), ComponentType.INTERFACE)
        component_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)', line)
        if component_match:
            component_name = component_match.group(1)
            if component_name.endswith('Validator') or component_name.endswith('Analyzer') or component_name.endswith('Orchestrator') or component_name.endswith('Manager') or component_name.endswith('Handler') or component_name.endswith('Controller'):
                return (component_name, ComponentType.CLASS)
            elif component_name.endswith('Model') or component_name.endswith('Data'):
                return (component_name, ComponentType.DATA_MODEL)
            else:
                return (component_name, ComponentType.MODULE)
        return None

    def _parse_code_block(self, code_lines: List[str], file_path: Path, line_num: int) -> Dict[str, DesignComponent]:
        """
        Parse code blocks in design documents to extract component definitions.
        
        Args:
            code_lines: Lines of code from the code block
            file_path: Path to the design file
            line_num: Line number where the code block ends
            
        Returns:
            Dictionary of design components found in the code block
        """
        components = {}
        code_content = '\n'.join(code_lines)
        class_matches = re.finditer('class\\s+(\\w+)(?:\\([^)]*\\))?:', code_content, re.MULTILINE)
        for match in class_matches:
            class_name = match.group(1)
            methods = []
            class_start = match.end()
            lines_after_class = code_content[class_start:].split('\n')
            class_content_lines = []
            for line in lines_after_class:
                if line.strip() == '':
                    class_content_lines.append(line)
                    continue
                elif line.startswith('    ') or line.startswith('\t'):
                    class_content_lines.append(line)
                else:
                    break
            class_content = '\n'.join(class_content_lines)
            method_matches = re.findall('\\n\\s+def\\s+(\\w+)', class_content)
            methods.extend(method_matches)
            components[class_name] = DesignComponent(name=class_name, component_type=ComponentType.CLASS, description=f'Class defined in design document', methods=methods, attributes=[], file_path=str(file_path), line_number=line_num, metadata={'from_code_block': True})
        lines = code_content.split('\n')
        in_class = False
        class_indent_level = 0
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if line.strip():
                indent_level = len(line) - len(line.lstrip())
            else:
                continue
            if stripped_line.startswith('class '):
                in_class = True
                class_indent_level = indent_level
                continue
            elif in_class and indent_level <= class_indent_level and stripped_line:
                in_class = False
            if stripped_line.startswith('def ') and (not in_class):
                func_match = re.search('def\\s+(\\w+)', stripped_line)
                if func_match:
                    function_name = func_match.group(1)
                    if not any((function_name in comp.methods for comp in components.values())):
                        components[function_name] = DesignComponent(name=function_name, component_type=ComponentType.FUNCTION, description=f'Function defined in design document', methods=[], attributes=[], file_path=str(file_path), line_number=line_num, metadata={'from_code_block': True})
        return components

    def _load_implementation_components(self, target_path: Path) -> Dict[str, ImplementationComponent]:
        """
        Load implementation components from source code.
        
        Args:
            target_path: Path to search for implementations
            
        Returns:
            Dictionary mapping component names to implementation components
        """
        components = {}
        if target_path.is_file() and target_path.suffix == '.py':
            files_to_analyze = [target_path]
        else:
            files_to_analyze = list(target_path.glob('**/*.py'))
        for py_file in files_to_analyze:
            try:
                file_components = self._parse_implementation_file(py_file)
                components.update(file_components)
            except Exception as e:
                print(f'Warning: Failed to parse implementation file {py_file}: {e}')
        return components

    def _parse_implementation_file(self, file_path: Path) -> Dict[str, ImplementationComponent]:
        """
        Parse a Python implementation file to extract components.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary of implementation components
        """
        components = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return components
        class_matches = re.finditer('^class\\s+(\\w+)(?:\\([^)]*\\))?:', content, re.MULTILINE)
        for match in class_matches:
            class_name = match.group(1)
            class_line = content[:match.start()].count('\n') + 1
            methods, attributes = self._extract_class_members(content, match.start())
            docstring = self._extract_docstring(content, match.end())
            components[class_name] = ImplementationComponent(name=class_name, component_type=ComponentType.CLASS, methods=methods, attributes=attributes, file_path=str(file_path), line_number=class_line, docstring=docstring, metadata={})
        function_matches = re.finditer('^def\\s+(\\w+)', content, re.MULTILINE)
        for match in function_matches:
            function_name = match.group(1)
            function_line = content[:match.start()].count('\n') + 1
            if self._is_method_in_class(content, match.start()):
                continue
            docstring = self._extract_docstring(content, match.end())
            components[function_name] = ImplementationComponent(name=function_name, component_type=ComponentType.FUNCTION, methods=[], attributes=[], file_path=str(file_path), line_number=function_line, docstring=docstring, metadata={})
        return components

    def _extract_class_members(self, content: str, class_start: int) -> Tuple[List[str], List[str]]:
        """
        Extract methods and attributes from a class definition.
        
        Args:
            content: Full file content
            class_start: Starting position of the class definition
            
        Returns:
            Tuple of (methods, attributes)
        """
        methods = []
        attributes = []
        class_content = content[class_start:]
        method_matches = re.finditer('^\\s+def\\s+(\\w+)', class_content, re.MULTILINE)
        for match in method_matches:
            methods.append(match.group(1))
        attr_matches = re.finditer('^\\s+self\\.(\\w+)\\s*=', class_content, re.MULTILINE)
        for match in attr_matches:
            if match.group(1) not in attributes:
                attributes.append(match.group(1))
        return (methods, attributes)

    def _extract_docstring(self, content: str, start_pos: int) -> Optional[str]:
        """
        Extract docstring from a function or class definition.
        
        Args:
            content: Full file content
            start_pos: Position after the definition line
            
        Returns:
            Docstring if found, None otherwise
        """
        remaining_content = content[start_pos:]
        docstring_match = re.search(':\\s*\\n\\s*"""(.*?)"""', remaining_content, re.DOTALL)
        if docstring_match:
            return docstring_match.group(1).strip()
        docstring_match = re.search(":\\s*\\n\\s*'''(.*?)'''", remaining_content, re.DOTALL)
        if docstring_match:
            return docstring_match.group(1).strip()
        single_line_match = re.search(':\\s*\\n\\s*"([^"]*)"', remaining_content)
        if single_line_match:
            return single_line_match.group(1).strip()
        single_line_match = re.search(":\\s*\\n\\s*'([^']*)'", remaining_content)
        if single_line_match:
            return single_line_match.group(1).strip()
        return None

    def _is_method_in_class(self, content: str, function_start: int) -> bool:
        """
        Check if a function definition is inside a class.
        
        Args:
            content: Full file content
            function_start: Starting position of the function definition
            
        Returns:
            True if the function is a method inside a class
        """
        before_function = content[:function_start]
        function_line_start = before_function.rfind('\n') + 1
        function_line = content[function_line_start:function_start + 20]
        function_indent = len(function_line) - len(function_line.lstrip())
        return function_indent > 0

    def _analyze_alignment(self) -> AlignmentResult:
        """
        Analyze alignment between design and implementation components.
        
        Returns:
            Alignment analysis results
        """
        missing_implementations = []
        extra_implementations = []
        misaligned_components = []
        for design_name, design_comp in self.design_cache.items():
            if design_name not in self.implementation_cache:
                missing_implementations.append(design_comp)
            else:
                impl_comp = self.implementation_cache[design_name]
                if not self._components_aligned(design_comp, impl_comp):
                    misaligned_components.append((design_comp, impl_comp))
        for impl_name, impl_comp in self.implementation_cache.items():
            if impl_name not in self.design_cache:
                if not self._is_utility_component(impl_comp):
                    extra_implementations.append(impl_comp)
        total_design_components = len(self.design_cache)
        implemented_components = len(self.design_cache) - len(missing_implementations)
        alignment_score = implemented_components / total_design_components * 100 if total_design_components > 0 else 100
        if misaligned_components:
            alignment_penalty = len(misaligned_components) / total_design_components * 20
            alignment_score = max(0, alignment_score - alignment_penalty)
        issues = self._generate_alignment_issues(missing_implementations, extra_implementations, misaligned_components, alignment_score)
        return AlignmentResult(total_design_components=total_design_components, implemented_components=implemented_components, missing_implementations=missing_implementations, extra_implementations=extra_implementations, misaligned_components=misaligned_components, alignment_score=alignment_score, issues=issues)

    def _components_aligned(self, design_comp: DesignComponent, impl_comp: ImplementationComponent) -> bool:
        """
        Check if design and implementation components are properly aligned.
        
        Args:
            design_comp: Design component specification
            impl_comp: Implementation component
            
        Returns:
            True if components are aligned
        """
        if design_comp.component_type != impl_comp.component_type:
            return False
        if design_comp.component_type == ComponentType.CLASS:
            design_methods = set(design_comp.methods)
            impl_methods = set(impl_comp.methods)
            impl_public_methods = {m for m in impl_methods if not m.startswith('_')}
            missing_methods = design_methods - impl_public_methods
            if missing_methods:
                return False
        return True

    def _is_utility_component(self, impl_comp: ImplementationComponent) -> bool:
        """
        Check if an implementation component is a utility component that doesn't need design specification.
        
        Args:
            impl_comp: Implementation component to check
            
        Returns:
            True if it's a utility component
        """
        if impl_comp.name.startswith('_'):
            return True
        utility_names = {'main', 'setup', 'teardown', 'helper', 'util', 'test_'}
        if any((util in impl_comp.name.lower() for util in utility_names)):
            return True
        if impl_comp.name.startswith('test_') or 'test' in impl_comp.file_path.lower():
            return True
        return False

    def _generate_alignment_issues(self, missing_implementations: List[DesignComponent], extra_implementations: List[ImplementationComponent], misaligned_components: List[Tuple[DesignComponent, ImplementationComponent]], alignment_score: float) -> List[ComplianceIssue]:
        """
        Generate compliance issues based on alignment analysis.
        
        Args:
            missing_implementations: Components missing from implementation
            extra_implementations: Extra implementations not in design
            misaligned_components: Components with alignment issues
            alignment_score: Overall alignment score
            
        Returns:
            List of compliance issues
        """
        issues = []
        if missing_implementations:
            affected_files = list(set((comp.file_path for comp in missing_implementations)))
            missing_names = [comp.name for comp in missing_implementations]
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(missing_implementations)} design components without implementations', affected_files=affected_files, remediation_steps=[f"Implement missing components: {', '.join(missing_names)}", 'Ensure all design components have corresponding implementations', 'Review design documents and create implementation files'], estimated_effort='High', blocking_merge=len(missing_implementations) > 3, metadata={'missing_components': missing_names, 'count': len(missing_implementations)}))
        if extra_implementations:
            affected_files = list(set((comp.file_path for comp in extra_implementations)))
            extra_names = [comp.name for comp in extra_implementations]
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.MEDIUM, description=f'Found {len(extra_implementations)} implementations not specified in design', affected_files=affected_files, remediation_steps=[f"Review extra implementations: {', '.join(extra_names)}", 'Add design specifications for legitimate implementations', 'Remove unauthorized implementations or update design documents'], estimated_effort='Medium', blocking_merge=False, metadata={'extra_components': extra_names, 'count': len(extra_implementations)}))
        if misaligned_components:
            affected_files = list(set((impl.file_path for _, impl in misaligned_components)))
            misaligned_names = [design.name for design, _ in misaligned_components]
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(misaligned_components)} components with design-implementation misalignment', affected_files=affected_files, remediation_steps=[f"Fix alignment issues in components: {', '.join(misaligned_names)}", 'Ensure implementations match design specifications', 'Update implementations or design documents to align'], estimated_effort='Medium', blocking_merge=len(misaligned_components) > 2, metadata={'misaligned_components': misaligned_names, 'count': len(misaligned_components)}))
        if alignment_score < 80.0:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH if alignment_score < 60.0 else IssueSeverity.MEDIUM, description=f'Low design-implementation alignment score: {alignment_score:.1f}%', affected_files=[], remediation_steps=['Improve design-implementation alignment', 'Ensure all design components are implemented', 'Review and update design or implementation as needed', f'Target: Achieve >80% alignment (currently {alignment_score:.1f}%)'], estimated_effort='High', blocking_merge=alignment_score < 60.0, metadata={'alignment_score': alignment_score, 'target_score': 80.0}))
        return issues

def __init__(self, repository_path: str):
    """
        Initialize the DesignValidator.
        
        Args:
            repository_path: Path to the repository root
        """
    self.repository_path = Path(repository_path)
    self.design_cache: Optional[Dict[str, DesignComponent]] = None
    self.implementation_cache: Optional[Dict[str, ImplementationComponent]] = None

def get_validator_name(self) -> str:
    """Get the name of this validator."""
    return 'DesignValidator'

def analyze_alignment(self, target_path: Optional[str]=None) -> AlignmentResult:
    """
        Perform comprehensive design-implementation alignment analysis.
        
        Args:
            target_path: Specific path to analyze, or None for full repository
            
        Returns:
            Detailed alignment analysis results
        """
    if self.design_cache is None:
        self.design_cache = self._load_design_components()
    analysis_path = Path(target_path) if target_path else self.repository_path
    if self.implementation_cache is None:
        self.implementation_cache = self._load_implementation_components(analysis_path)
    return self._analyze_alignment()

def _load_design_components(self) -> Dict[str, DesignComponent]:
    """
        Load all design components from design documents.
        
        Returns:
            Dictionary mapping component names to design components
        """
    components = {}
    design_files = []
    for pattern in ['**/design.md', '**/design/*.md', '**/*design*.md']:
        design_files.extend(self.repository_path.glob(pattern))
    for design_file in design_files:
        try:
            file_components = self._parse_design_file(design_file)
            components.update(file_components)
        except Exception as e:
            print(f'Warning: Failed to parse design file {design_file}: {e}')
    return components

def _match_component_header(self, line: str) -> Optional[Tuple[str, ComponentType]]:
    """
        Match component headers in design documents.
        
        Args:
            line: Line to check for component headers
            
        Returns:
            Tuple of (component_name, component_type) if matched, None otherwise
        """
    class_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+class|\\s+Class)', line, re.IGNORECASE)
    if class_match:
        return (class_match.group(1), ComponentType.CLASS)
    interface_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+interface|\\s+Interface)', line, re.IGNORECASE)
    if interface_match:
        return (interface_match.group(1), ComponentType.INTERFACE)
    component_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)', line)
    if component_match:
        component_name = component_match.group(1)
        if component_name.endswith('Validator') or component_name.endswith('Analyzer') or component_name.endswith('Orchestrator') or component_name.endswith('Manager') or component_name.endswith('Handler') or component_name.endswith('Controller'):
            return (component_name, ComponentType.CLASS)
        elif component_name.endswith('Model') or component_name.endswith('Data'):
            return (component_name, ComponentType.DATA_MODEL)
        else:
            return (component_name, ComponentType.MODULE)
    return None

def _load_implementation_components(self, target_path: Path) -> Dict[str, ImplementationComponent]:
    """
        Load implementation components from source code.
        
        Args:
            target_path: Path to search for implementations
            
        Returns:
            Dictionary mapping component names to implementation components
        """
    components = {}
    if target_path.is_file() and target_path.suffix == '.py':
        files_to_analyze = [target_path]
    else:
        files_to_analyze = list(target_path.glob('**/*.py'))
    for py_file in files_to_analyze:
        try:
            file_components = self._parse_implementation_file(py_file)
            components.update(file_components)
        except Exception as e:
            print(f'Warning: Failed to parse implementation file {py_file}: {e}')
    return components

def _extract_class_members(self, content: str, class_start: int) -> Tuple[List[str], List[str]]:
    """
        Extract methods and attributes from a class definition.
        
        Args:
            content: Full file content
            class_start: Starting position of the class definition
            
        Returns:
            Tuple of (methods, attributes)
        """
    methods = []
    attributes = []
    class_content = content[class_start:]
    method_matches = re.finditer('^\\s+def\\s+(\\w+)', class_content, re.MULTILINE)
    for match in method_matches:
        methods.append(match.group(1))
    attr_matches = re.finditer('^\\s+self\\.(\\w+)\\s*=', class_content, re.MULTILINE)
    for match in attr_matches:
        if match.group(1) not in attributes:
            attributes.append(match.group(1))
    return (methods, attributes)

def _extract_docstring(self, content: str, start_pos: int) -> Optional[str]:
    """
        Extract docstring from a function or class definition.
        
        Args:
            content: Full file content
            start_pos: Position after the definition line
            
        Returns:
            Docstring if found, None otherwise
        """
    remaining_content = content[start_pos:]
    docstring_match = re.search(':\\s*\\n\\s*"""(.*?)"""', remaining_content, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    docstring_match = re.search(":\\s*\\n\\s*'''(.*?)'''", remaining_content, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    single_line_match = re.search(':\\s*\\n\\s*"([^"]*)"', remaining_content)
    if single_line_match:
        return single_line_match.group(1).strip()
    single_line_match = re.search(":\\s*\\n\\s*'([^']*)'", remaining_content)
    if single_line_match:
        return single_line_match.group(1).strip()
    return None

def _is_method_in_class(self, content: str, function_start: int) -> bool:
    """
        Check if a function definition is inside a class.
        
        Args:
            content: Full file content
            function_start: Starting position of the function definition
            
        Returns:
            True if the function is a method inside a class
        """
    before_function = content[:function_start]
    function_line_start = before_function.rfind('\n') + 1
    function_line = content[function_line_start:function_start + 20]
    function_indent = len(function_line) - len(function_line.lstrip())
    return function_indent > 0

def _analyze_alignment(self) -> AlignmentResult:
    """
        Analyze alignment between design and implementation components.
        
        Returns:
            Alignment analysis results
        """
    missing_implementations = []
    extra_implementations = []
    misaligned_components = []
    for design_name, design_comp in self.design_cache.items():
        if design_name not in self.implementation_cache:
            missing_implementations.append(design_comp)
        else:
            impl_comp = self.implementation_cache[design_name]
            if not self._components_aligned(design_comp, impl_comp):
                misaligned_components.append((design_comp, impl_comp))
    for impl_name, impl_comp in self.implementation_cache.items():
        if impl_name not in self.design_cache:
            if not self._is_utility_component(impl_comp):
                extra_implementations.append(impl_comp)
    total_design_components = len(self.design_cache)
    implemented_components = len(self.design_cache) - len(missing_implementations)
    alignment_score = implemented_components / total_design_components * 100 if total_design_components > 0 else 100
    if misaligned_components:
        alignment_penalty = len(misaligned_components) / total_design_components * 20
        alignment_score = max(0, alignment_score - alignment_penalty)
    issues = self._generate_alignment_issues(missing_implementations, extra_implementations, misaligned_components, alignment_score)
    return AlignmentResult(total_design_components=total_design_components, implemented_components=implemented_components, missing_implementations=missing_implementations, extra_implementations=extra_implementations, misaligned_components=misaligned_components, alignment_score=alignment_score, issues=issues)

def _components_aligned(self, design_comp: DesignComponent, impl_comp: ImplementationComponent) -> bool:
    """
        Check if design and implementation components are properly aligned.
        
        Args:
            design_comp: Design component specification
            impl_comp: Implementation component
            
        Returns:
            True if components are aligned
        """
    if design_comp.component_type != impl_comp.component_type:
        return False
    if design_comp.component_type == ComponentType.CLASS:
        design_methods = set(design_comp.methods)
        impl_methods = set(impl_comp.methods)
        impl_public_methods = {m for m in impl_methods if not m.startswith('_')}
        missing_methods = design_methods - impl_public_methods
        if missing_methods:
            return False
    return True

def _generate_alignment_issues(self, missing_implementations: List[DesignComponent], extra_implementations: List[ImplementationComponent], misaligned_components: List[Tuple[DesignComponent, ImplementationComponent]], alignment_score: float) -> List[ComplianceIssue]:
    """
        Generate compliance issues based on alignment analysis.
        
        Args:
            missing_implementations: Components missing from implementation
            extra_implementations: Extra implementations not in design
            misaligned_components: Components with alignment issues
            alignment_score: Overall alignment score
            
        Returns:
            List of compliance issues
        """
    issues = []
    if missing_implementations:
        affected_files = list(set((comp.file_path for comp in missing_implementations)))
        missing_names = [comp.name for comp in missing_implementations]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(missing_implementations)} design components without implementations', affected_files=affected_files, remediation_steps=[f"Implement missing components: {', '.join(missing_names)}", 'Ensure all design components have corresponding implementations', 'Review design documents and create implementation files'], estimated_effort='High', blocking_merge=len(missing_implementations) > 3, metadata={'missing_components': missing_names, 'count': len(missing_implementations)}))
    if extra_implementations:
        affected_files = list(set((comp.file_path for comp in extra_implementations)))
        extra_names = [comp.name for comp in extra_implementations]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.MEDIUM, description=f'Found {len(extra_implementations)} implementations not specified in design', affected_files=affected_files, remediation_steps=[f"Review extra implementations: {', '.join(extra_names)}", 'Add design specifications for legitimate implementations', 'Remove unauthorized implementations or update design documents'], estimated_effort='Medium', blocking_merge=False, metadata={'extra_components': extra_names, 'count': len(extra_implementations)}))
    if misaligned_components:
        affected_files = list(set((impl.file_path for _, impl in misaligned_components)))
        misaligned_names = [design.name for design, _ in misaligned_components]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(misaligned_components)} components with design-implementation misalignment', affected_files=affected_files, remediation_steps=[f"Fix alignment issues in components: {', '.join(misaligned_names)}", 'Ensure implementations match design specifications', 'Update implementations or design documents to align'], estimated_effort='Medium', blocking_merge=len(misaligned_components) > 2, metadata={'misaligned_components': misaligned_names, 'count': len(misaligned_components)}))
    if alignment_score < 80.0:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH if alignment_score < 60.0 else IssueSeverity.MEDIUM, description=f'Low design-implementation alignment score: {alignment_score:.1f}%', affected_files=[], remediation_steps=['Improve design-implementation alignment', 'Ensure all design components are implemented', 'Review and update design or implementation as needed', f'Target: Achieve >80% alignment (currently {alignment_score:.1f}%)'], estimated_effort='High', blocking_merge=alignment_score < 60.0, metadata={'alignment_score': alignment_score, 'target_score': 80.0}))
    return issues

def __init__(self, repository_path: str):
    """
        Initialize the DesignValidator.
        
        Args:
            repository_path: Path to the repository root
        """
    self.repository_path = Path(repository_path)
    self.design_cache: Optional[Dict[str, DesignComponent]] = None
    self.implementation_cache: Optional[Dict[str, ImplementationComponent]] = None

def get_validator_name(self) -> str:
    """Get the name of this validator."""
    return 'DesignValidator'

def analyze_alignment(self, target_path: Optional[str]=None) -> AlignmentResult:
    """
        Perform comprehensive design-implementation alignment analysis.
        
        Args:
            target_path: Specific path to analyze, or None for full repository
            
        Returns:
            Detailed alignment analysis results
        """
    if self.design_cache is None:
        self.design_cache = self._load_design_components()
    analysis_path = Path(target_path) if target_path else self.repository_path
    if self.implementation_cache is None:
        self.implementation_cache = self._load_implementation_components(analysis_path)
    return self._analyze_alignment()

def _load_design_components(self) -> Dict[str, DesignComponent]:
    """
        Load all design components from design documents.
        
        Returns:
            Dictionary mapping component names to design components
        """
    components = {}
    design_files = []
    for pattern in ['**/design.md', '**/design/*.md', '**/*design*.md']:
        design_files.extend(self.repository_path.glob(pattern))
    for design_file in design_files:
        try:
            file_components = self._parse_design_file(design_file)
            components.update(file_components)
        except Exception as e:
            print(f'Warning: Failed to parse design file {design_file}: {e}')
    return components

def _match_component_header(self, line: str) -> Optional[Tuple[str, ComponentType]]:
    """
        Match component headers in design documents.
        
        Args:
            line: Line to check for component headers
            
        Returns:
            Tuple of (component_name, component_type) if matched, None otherwise
        """
    class_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+class|\\s+Class)', line, re.IGNORECASE)
    if class_match:
        return (class_match.group(1), ComponentType.CLASS)
    interface_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+interface|\\s+Interface)', line, re.IGNORECASE)
    if interface_match:
        return (interface_match.group(1), ComponentType.INTERFACE)
    component_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)', line)
    if component_match:
        component_name = component_match.group(1)
        if component_name.endswith('Validator') or component_name.endswith('Analyzer') or component_name.endswith('Orchestrator') or component_name.endswith('Manager') or component_name.endswith('Handler') or component_name.endswith('Controller'):
            return (component_name, ComponentType.CLASS)
        elif component_name.endswith('Model') or component_name.endswith('Data'):
            return (component_name, ComponentType.DATA_MODEL)
        else:
            return (component_name, ComponentType.MODULE)
    return None

def _load_implementation_components(self, target_path: Path) -> Dict[str, ImplementationComponent]:
    """
        Load implementation components from source code.
        
        Args:
            target_path: Path to search for implementations
            
        Returns:
            Dictionary mapping component names to implementation components
        """
    components = {}
    if target_path.is_file() and target_path.suffix == '.py':
        files_to_analyze = [target_path]
    else:
        files_to_analyze = list(target_path.glob('**/*.py'))
    for py_file in files_to_analyze:
        try:
            file_components = self._parse_implementation_file(py_file)
            components.update(file_components)
        except Exception as e:
            print(f'Warning: Failed to parse implementation file {py_file}: {e}')
    return components

def _extract_class_members(self, content: str, class_start: int) -> Tuple[List[str], List[str]]:
    """
        Extract methods and attributes from a class definition.
        
        Args:
            content: Full file content
            class_start: Starting position of the class definition
            
        Returns:
            Tuple of (methods, attributes)
        """
    methods = []
    attributes = []
    class_content = content[class_start:]
    method_matches = re.finditer('^\\s+def\\s+(\\w+)', class_content, re.MULTILINE)
    for match in method_matches:
        methods.append(match.group(1))
    attr_matches = re.finditer('^\\s+self\\.(\\w+)\\s*=', class_content, re.MULTILINE)
    for match in attr_matches:
        if match.group(1) not in attributes:
            attributes.append(match.group(1))
    return (methods, attributes)

def _extract_docstring(self, content: str, start_pos: int) -> Optional[str]:
    """
        Extract docstring from a function or class definition.
        
        Args:
            content: Full file content
            start_pos: Position after the definition line
            
        Returns:
            Docstring if found, None otherwise
        """
    remaining_content = content[start_pos:]
    docstring_match = re.search(':\\s*\\n\\s*"""(.*?)"""', remaining_content, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    docstring_match = re.search(":\\s*\\n\\s*'''(.*?)'''", remaining_content, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    single_line_match = re.search(':\\s*\\n\\s*"([^"]*)"', remaining_content)
    if single_line_match:
        return single_line_match.group(1).strip()
    single_line_match = re.search(":\\s*\\n\\s*'([^']*)'", remaining_content)
    if single_line_match:
        return single_line_match.group(1).strip()
    return None

def _is_method_in_class(self, content: str, function_start: int) -> bool:
    """
        Check if a function definition is inside a class.
        
        Args:
            content: Full file content
            function_start: Starting position of the function definition
            
        Returns:
            True if the function is a method inside a class
        """
    before_function = content[:function_start]
    function_line_start = before_function.rfind('\n') + 1
    function_line = content[function_line_start:function_start + 20]
    function_indent = len(function_line) - len(function_line.lstrip())
    return function_indent > 0

def _analyze_alignment(self) -> AlignmentResult:
    """
        Analyze alignment between design and implementation components.
        
        Returns:
            Alignment analysis results
        """
    missing_implementations = []
    extra_implementations = []
    misaligned_components = []
    for design_name, design_comp in self.design_cache.items():
        if design_name not in self.implementation_cache:
            missing_implementations.append(design_comp)
        else:
            impl_comp = self.implementation_cache[design_name]
            if not self._components_aligned(design_comp, impl_comp):
                misaligned_components.append((design_comp, impl_comp))
    for impl_name, impl_comp in self.implementation_cache.items():
        if impl_name not in self.design_cache:
            if not self._is_utility_component(impl_comp):
                extra_implementations.append(impl_comp)
    total_design_components = len(self.design_cache)
    implemented_components = len(self.design_cache) - len(missing_implementations)
    alignment_score = implemented_components / total_design_components * 100 if total_design_components > 0 else 100
    if misaligned_components:
        alignment_penalty = len(misaligned_components) / total_design_components * 20
        alignment_score = max(0, alignment_score - alignment_penalty)
    issues = self._generate_alignment_issues(missing_implementations, extra_implementations, misaligned_components, alignment_score)
    return AlignmentResult(total_design_components=total_design_components, implemented_components=implemented_components, missing_implementations=missing_implementations, extra_implementations=extra_implementations, misaligned_components=misaligned_components, alignment_score=alignment_score, issues=issues)

def _components_aligned(self, design_comp: DesignComponent, impl_comp: ImplementationComponent) -> bool:
    """
        Check if design and implementation components are properly aligned.
        
        Args:
            design_comp: Design component specification
            impl_comp: Implementation component
            
        Returns:
            True if components are aligned
        """
    if design_comp.component_type != impl_comp.component_type:
        return False
    if design_comp.component_type == ComponentType.CLASS:
        design_methods = set(design_comp.methods)
        impl_methods = set(impl_comp.methods)
        impl_public_methods = {m for m in impl_methods if not m.startswith('_')}
        missing_methods = design_methods - impl_public_methods
        if missing_methods:
            return False
    return True

def _generate_alignment_issues(self, missing_implementations: List[DesignComponent], extra_implementations: List[ImplementationComponent], misaligned_components: List[Tuple[DesignComponent, ImplementationComponent]], alignment_score: float) -> List[ComplianceIssue]:
    """
        Generate compliance issues based on alignment analysis.
        
        Args:
            missing_implementations: Components missing from implementation
            extra_implementations: Extra implementations not in design
            misaligned_components: Components with alignment issues
            alignment_score: Overall alignment score
            
        Returns:
            List of compliance issues
        """
    issues = []
    if missing_implementations:
        affected_files = list(set((comp.file_path for comp in missing_implementations)))
        missing_names = [comp.name for comp in missing_implementations]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(missing_implementations)} design components without implementations', affected_files=affected_files, remediation_steps=[f"Implement missing components: {', '.join(missing_names)}", 'Ensure all design components have corresponding implementations', 'Review design documents and create implementation files'], estimated_effort='High', blocking_merge=len(missing_implementations) > 3, metadata={'missing_components': missing_names, 'count': len(missing_implementations)}))
    if extra_implementations:
        affected_files = list(set((comp.file_path for comp in extra_implementations)))
        extra_names = [comp.name for comp in extra_implementations]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.MEDIUM, description=f'Found {len(extra_implementations)} implementations not specified in design', affected_files=affected_files, remediation_steps=[f"Review extra implementations: {', '.join(extra_names)}", 'Add design specifications for legitimate implementations', 'Remove unauthorized implementations or update design documents'], estimated_effort='Medium', blocking_merge=False, metadata={'extra_components': extra_names, 'count': len(extra_implementations)}))
    if misaligned_components:
        affected_files = list(set((impl.file_path for _, impl in misaligned_components)))
        misaligned_names = [design.name for design, _ in misaligned_components]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(misaligned_components)} components with design-implementation misalignment', affected_files=affected_files, remediation_steps=[f"Fix alignment issues in components: {', '.join(misaligned_names)}", 'Ensure implementations match design specifications', 'Update implementations or design documents to align'], estimated_effort='Medium', blocking_merge=len(misaligned_components) > 2, metadata={'misaligned_components': misaligned_names, 'count': len(misaligned_components)}))
    if alignment_score < 80.0:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH if alignment_score < 60.0 else IssueSeverity.MEDIUM, description=f'Low design-implementation alignment score: {alignment_score:.1f}%', affected_files=[], remediation_steps=['Improve design-implementation alignment', 'Ensure all design components are implemented', 'Review and update design or implementation as needed', f'Target: Achieve >80% alignment (currently {alignment_score:.1f}%)'], estimated_effort='High', blocking_merge=alignment_score < 60.0, metadata={'alignment_score': alignment_score, 'target_score': 80.0}))
    return issues

def __init__(self, repository_path: str):
    """
        Initialize the DesignValidator.
        
        Args:
            repository_path: Path to the repository root
        """
    self.repository_path = Path(repository_path)
    self.design_cache: Optional[Dict[str, DesignComponent]] = None
    self.implementation_cache: Optional[Dict[str, ImplementationComponent]] = None

def get_validator_name(self) -> str:
    """Get the name of this validator."""
    return 'DesignValidator'

def analyze_alignment(self, target_path: Optional[str]=None) -> AlignmentResult:
    """
        Perform comprehensive design-implementation alignment analysis.
        
        Args:
            target_path: Specific path to analyze, or None for full repository
            
        Returns:
            Detailed alignment analysis results
        """
    if self.design_cache is None:
        self.design_cache = self._load_design_components()
    analysis_path = Path(target_path) if target_path else self.repository_path
    if self.implementation_cache is None:
        self.implementation_cache = self._load_implementation_components(analysis_path)
    return self._analyze_alignment()

def _load_design_components(self) -> Dict[str, DesignComponent]:
    """
        Load all design components from design documents.
        
        Returns:
            Dictionary mapping component names to design components
        """
    components = {}
    design_files = []
    for pattern in ['**/design.md', '**/design/*.md', '**/*design*.md']:
        design_files.extend(self.repository_path.glob(pattern))
    for design_file in design_files:
        try:
            file_components = self._parse_design_file(design_file)
            components.update(file_components)
        except Exception as e:
            print(f'Warning: Failed to parse design file {design_file}: {e}')
    return components

def _match_component_header(self, line: str) -> Optional[Tuple[str, ComponentType]]:
    """
        Match component headers in design documents.
        
        Args:
            line: Line to check for component headers
            
        Returns:
            Tuple of (component_name, component_type) if matched, None otherwise
        """
    class_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+class|\\s+Class)', line, re.IGNORECASE)
    if class_match:
        return (class_match.group(1), ComponentType.CLASS)
    interface_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)(?:\\s+interface|\\s+Interface)', line, re.IGNORECASE)
    if interface_match:
        return (interface_match.group(1), ComponentType.INTERFACE)
    component_match = re.search('###?\\s+\\d*\\.?\\s*(\\w+)', line)
    if component_match:
        component_name = component_match.group(1)
        if component_name.endswith('Validator') or component_name.endswith('Analyzer') or component_name.endswith('Orchestrator') or component_name.endswith('Manager') or component_name.endswith('Handler') or component_name.endswith('Controller'):
            return (component_name, ComponentType.CLASS)
        elif component_name.endswith('Model') or component_name.endswith('Data'):
            return (component_name, ComponentType.DATA_MODEL)
        else:
            return (component_name, ComponentType.MODULE)
    return None

def _load_implementation_components(self, target_path: Path) -> Dict[str, ImplementationComponent]:
    """
        Load implementation components from source code.
        
        Args:
            target_path: Path to search for implementations
            
        Returns:
            Dictionary mapping component names to implementation components
        """
    components = {}
    if target_path.is_file() and target_path.suffix == '.py':
        files_to_analyze = [target_path]
    else:
        files_to_analyze = list(target_path.glob('**/*.py'))
    for py_file in files_to_analyze:
        try:
            file_components = self._parse_implementation_file(py_file)
            components.update(file_components)
        except Exception as e:
            print(f'Warning: Failed to parse implementation file {py_file}: {e}')
    return components

def _extract_class_members(self, content: str, class_start: int) -> Tuple[List[str], List[str]]:
    """
        Extract methods and attributes from a class definition.
        
        Args:
            content: Full file content
            class_start: Starting position of the class definition
            
        Returns:
            Tuple of (methods, attributes)
        """
    methods = []
    attributes = []
    class_content = content[class_start:]
    method_matches = re.finditer('^\\s+def\\s+(\\w+)', class_content, re.MULTILINE)
    for match in method_matches:
        methods.append(match.group(1))
    attr_matches = re.finditer('^\\s+self\\.(\\w+)\\s*=', class_content, re.MULTILINE)
    for match in attr_matches:
        if match.group(1) not in attributes:
            attributes.append(match.group(1))
    return (methods, attributes)

def _extract_docstring(self, content: str, start_pos: int) -> Optional[str]:
    """
        Extract docstring from a function or class definition.
        
        Args:
            content: Full file content
            start_pos: Position after the definition line
            
        Returns:
            Docstring if found, None otherwise
        """
    remaining_content = content[start_pos:]
    docstring_match = re.search(':\\s*\\n\\s*"""(.*?)"""', remaining_content, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    docstring_match = re.search(":\\s*\\n\\s*'''(.*?)'''", remaining_content, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    single_line_match = re.search(':\\s*\\n\\s*"([^"]*)"', remaining_content)
    if single_line_match:
        return single_line_match.group(1).strip()
    single_line_match = re.search(":\\s*\\n\\s*'([^']*)'", remaining_content)
    if single_line_match:
        return single_line_match.group(1).strip()
    return None

def _is_method_in_class(self, content: str, function_start: int) -> bool:
    """
        Check if a function definition is inside a class.
        
        Args:
            content: Full file content
            function_start: Starting position of the function definition
            
        Returns:
            True if the function is a method inside a class
        """
    before_function = content[:function_start]
    function_line_start = before_function.rfind('\n') + 1
    function_line = content[function_line_start:function_start + 20]
    function_indent = len(function_line) - len(function_line.lstrip())
    return function_indent > 0

def _analyze_alignment(self) -> AlignmentResult:
    """
        Analyze alignment between design and implementation components.
        
        Returns:
            Alignment analysis results
        """
    missing_implementations = []
    extra_implementations = []
    misaligned_components = []
    for design_name, design_comp in self.design_cache.items():
        if design_name not in self.implementation_cache:
            missing_implementations.append(design_comp)
        else:
            impl_comp = self.implementation_cache[design_name]
            if not self._components_aligned(design_comp, impl_comp):
                misaligned_components.append((design_comp, impl_comp))
    for impl_name, impl_comp in self.implementation_cache.items():
        if impl_name not in self.design_cache:
            if not self._is_utility_component(impl_comp):
                extra_implementations.append(impl_comp)
    total_design_components = len(self.design_cache)
    implemented_components = len(self.design_cache) - len(missing_implementations)
    alignment_score = implemented_components / total_design_components * 100 if total_design_components > 0 else 100
    if misaligned_components:
        alignment_penalty = len(misaligned_components) / total_design_components * 20
        alignment_score = max(0, alignment_score - alignment_penalty)
    issues = self._generate_alignment_issues(missing_implementations, extra_implementations, misaligned_components, alignment_score)
    return AlignmentResult(total_design_components=total_design_components, implemented_components=implemented_components, missing_implementations=missing_implementations, extra_implementations=extra_implementations, misaligned_components=misaligned_components, alignment_score=alignment_score, issues=issues)

def _components_aligned(self, design_comp: DesignComponent, impl_comp: ImplementationComponent) -> bool:
    """
        Check if design and implementation components are properly aligned.
        
        Args:
            design_comp: Design component specification
            impl_comp: Implementation component
            
        Returns:
            True if components are aligned
        """
    if design_comp.component_type != impl_comp.component_type:
        return False
    if design_comp.component_type == ComponentType.CLASS:
        design_methods = set(design_comp.methods)
        impl_methods = set(impl_comp.methods)
        impl_public_methods = {m for m in impl_methods if not m.startswith('_')}
        missing_methods = design_methods - impl_public_methods
        if missing_methods:
            return False
    return True

def _generate_alignment_issues(self, missing_implementations: List[DesignComponent], extra_implementations: List[ImplementationComponent], misaligned_components: List[Tuple[DesignComponent, ImplementationComponent]], alignment_score: float) -> List[ComplianceIssue]:
    """
        Generate compliance issues based on alignment analysis.
        
        Args:
            missing_implementations: Components missing from implementation
            extra_implementations: Extra implementations not in design
            misaligned_components: Components with alignment issues
            alignment_score: Overall alignment score
            
        Returns:
            List of compliance issues
        """
    issues = []
    if missing_implementations:
        affected_files = list(set((comp.file_path for comp in missing_implementations)))
        missing_names = [comp.name for comp in missing_implementations]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(missing_implementations)} design components without implementations', affected_files=affected_files, remediation_steps=[f"Implement missing components: {', '.join(missing_names)}", 'Ensure all design components have corresponding implementations', 'Review design documents and create implementation files'], estimated_effort='High', blocking_merge=len(missing_implementations) > 3, metadata={'missing_components': missing_names, 'count': len(missing_implementations)}))
    if extra_implementations:
        affected_files = list(set((comp.file_path for comp in extra_implementations)))
        extra_names = [comp.name for comp in extra_implementations]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.MEDIUM, description=f'Found {len(extra_implementations)} implementations not specified in design', affected_files=affected_files, remediation_steps=[f"Review extra implementations: {', '.join(extra_names)}", 'Add design specifications for legitimate implementations', 'Remove unauthorized implementations or update design documents'], estimated_effort='Medium', blocking_merge=False, metadata={'extra_components': extra_names, 'count': len(extra_implementations)}))
    if misaligned_components:
        affected_files = list(set((impl.file_path for _, impl in misaligned_components)))
        misaligned_names = [design.name for design, _ in misaligned_components]
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH, description=f'Found {len(misaligned_components)} components with design-implementation misalignment', affected_files=affected_files, remediation_steps=[f"Fix alignment issues in components: {', '.join(misaligned_names)}", 'Ensure implementations match design specifications', 'Update implementations or design documents to align'], estimated_effort='Medium', blocking_merge=len(misaligned_components) > 2, metadata={'misaligned_components': misaligned_names, 'count': len(misaligned_components)}))
    if alignment_score < 80.0:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT, severity=IssueSeverity.HIGH if alignment_score < 60.0 else IssueSeverity.MEDIUM, description=f'Low design-implementation alignment score: {alignment_score:.1f}%', affected_files=[], remediation_steps=['Improve design-implementation alignment', 'Ensure all design components are implemented', 'Review and update design or implementation as needed', f'Target: Achieve >80% alignment (currently {alignment_score:.1f}%)'], estimated_effort='High', blocking_merge=alignment_score < 60.0, metadata={'alignment_score': alignment_score, 'target_score': 80.0}))
    return issues
