"""
FileChangeDetector - Advanced file change detection and analysis.

This module provides sophisticated file change detection capabilities
for the Beast Mode compliance checking system, including change categorization,
impact analysis, and task mapping.
"""

import logging
from pathlib import Path
from typing import List, Dict, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ...core.reflective_module import ReflectiveModule
from ..models import CommitInfo, FileChangeAnalysis


class ChangeType(Enum):
    """Types of file changes."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"
    COPIED = "copied"


class FileCategory(Enum):
    """Categories of files for impact analysis."""
    SOURCE_CODE = "source_code"
    TEST_CODE = "test_code"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    BUILD_SCRIPT = "build_script"
    DATA = "data"
    UNKNOWN = "unknown"


@dataclass
class FileChange:
    """Detailed information about a file change."""
    file_path: str
    change_type: ChangeType
    category: FileCategory
    lines_added: int = 0
    lines_deleted: int = 0
    old_path: Optional[str] = None  # For renames/moves
    commit_hash: str = ""
    impact_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskMapping:
    """Mapping between file changes and task completions."""
    task_id: str
    task_description: str
    confidence_score: float
    matching_files: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    completion_indicators: List[str] = field(default_factory=list)


@dataclass
class AdvancedFileChangeAnalysis:
    """Advanced file change analysis with categorization and impact assessment."""
    total_files_changed: int
    changes_by_type: Dict[ChangeType, List[FileChange]] = field(default_factory=dict)
    changes_by_category: Dict[FileCategory, List[FileChange]] = field(default_factory=dict)
    high_impact_changes: List[FileChange] = field(default_factory=list)
    task_mappings: List[TaskMapping] = field(default_factory=list)
    total_lines_added: int = 0
    total_lines_deleted: int = 0
    complexity_score: float = 0.0
    risk_assessment: str = "low"


class FileChangeDetector(ReflectiveModule):
    """
    Advanced file change detection and analysis component.
    
    Provides sophisticated analysis of file changes including categorization,
    impact assessment, and mapping to task completions.
    """
    
    def __init__(self, repository_path: str = "."):
        """
        Initialize the FileChangeDetector.
        
        Args:
            repository_path: Path to the git repository
        """
        super().__init__("FileChangeDetector")
        self.repository_path = Path(repository_path).resolve()
        self.logger = logging.getLogger(__name__)
        
        # Configuration for file categorization
        self._file_patterns = {
            FileCategory.SOURCE_CODE: [
                "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.h",
                "*.go", "*.rs", "*.rb", "*.php", "*.cs", "*.swift"
            ],
            FileCategory.TEST_CODE: [
                "test_*.py", "*_test.py", "tests/*", "test/*",
                "*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts"
            ],
            FileCategory.DOCUMENTATION: [
                "*.md", "*.rst", "*.txt", "docs/*", "README*",
                "CHANGELOG*", "LICENSE*", "*.adoc"
            ],
            FileCategory.CONFIGURATION: [
                "*.json", "*.yaml", "*.yml", "*.toml", "*.ini",
                "*.cfg", "*.conf", "pyproject.toml", "setup.py",
                "requirements*.txt", "Dockerfile*", "docker-compose*"
            ],
            FileCategory.BUILD_SCRIPT: [
                "Makefile", "*.mk", "*.sh", "*.bat", "*.ps1",
                "build.py", "setup.py", "*.gradle", "pom.xml"
            ]
        }
        
        # Task completion indicators
        self._task_indicators = {
            "implementation": [
                "class", "def ", "function", "interface", "implements"
            ],
            "testing": [
                "test_", "assert", "pytest", "unittest", "mock"
            ],
            "documentation": [
                "# ", "## ", "### ", "```", "docs/", "README"
            ],
            "configuration": [
                "config", "settings", "environment", "env"
            ]
        }
        
        self.logger.info(f"FileChangeDetector initialized for repository: {self.repository_path}")
    
    def analyze_file_changes(self, commits: List[CommitInfo]) -> AdvancedFileChangeAnalysis:
        """
        Perform advanced analysis of file changes across commits.
        
        Args:
            commits: List of commits to analyze
            
        Returns:
            Advanced file change analysis with categorization and impact assessment
        """
        self.logger.info(f"Performing advanced analysis of {len(commits)} commits")
        
        try:
            # Collect all file changes
            all_changes = []
            total_lines_added = 0
            total_lines_deleted = 0
            
            for commit in commits:
                changes = self._extract_file_changes_from_commit(commit)
                all_changes.extend(changes)
                
                for change in changes:
                    total_lines_added += change.lines_added
                    total_lines_deleted += change.lines_deleted
            
            # Categorize changes
            changes_by_type = self._categorize_by_type(all_changes)
            changes_by_category = self._categorize_by_file_type(all_changes)
            
            # Identify high-impact changes
            high_impact_changes = self._identify_high_impact_changes(all_changes)
            
            # Calculate complexity and risk
            complexity_score = self._calculate_complexity_score(all_changes)
            risk_assessment = self._assess_risk_level(all_changes, complexity_score)
            
            analysis = AdvancedFileChangeAnalysis(
                total_files_changed=len(all_changes),
                changes_by_type=changes_by_type,
                changes_by_category=changes_by_category,
                high_impact_changes=high_impact_changes,
                total_lines_added=total_lines_added,
                total_lines_deleted=total_lines_deleted,
                complexity_score=complexity_score,
                risk_assessment=risk_assessment
            )
            
            self.logger.info(
                f"Advanced analysis complete: {analysis.total_files_changed} files, "
                f"complexity: {analysis.complexity_score:.2f}, risk: {analysis.risk_assessment}"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in advanced file change analysis: {str(e)}")
            raise
    
    def map_changes_to_task_completions(
        self, 
        analysis: AdvancedFileChangeAnalysis,
        task_definitions: Optional[Dict[str, Dict[str, Any]]] = None,
        claimed_tasks: Optional[List[str]] = None
    ) -> List[TaskMapping]:
        """
        Map file changes to potential task completions with enhanced accuracy.
        
        Args:
            analysis: Advanced file change analysis
            task_definitions: Optional task definitions with patterns and indicators
            claimed_tasks: Optional list of claimed completed tasks to validate against
            
        Returns:
            List of task mappings with confidence scores and validation status
        """
        self.logger.info("Mapping file changes to task completions with enhanced validation")
        
        if task_definitions is None:
            task_definitions = self._get_default_task_definitions()
        
        task_mappings = []
        
        for task_id, task_config in task_definitions.items():
            mapping = self._analyze_task_completion_enhanced(
                task_id, 
                task_config, 
                analysis,
                claimed_tasks
            )
            
            if mapping.confidence_score > 0.1:  # Only include mappings with some confidence
                task_mappings.append(mapping)
        
        # Sort by confidence score
        task_mappings.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Add validation against claimed tasks
        if claimed_tasks:
            self._validate_claimed_vs_implemented(task_mappings, claimed_tasks)
        
        self.logger.info(f"Generated {len(task_mappings)} task mappings with enhanced validation")
        return task_mappings
    
    def detect_completion_evidence(
        self, 
        file_changes: List[FileChange],
        task_patterns: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Detect evidence of task completion in file changes.
        
        Args:
            file_changes: List of file changes to analyze
            task_patterns: Patterns to look for in files
            
        Returns:
            Dictionary mapping task types to evidence found
        """
        self.logger.info("Detecting completion evidence in file changes")
        
        evidence = {}
        
        for task_type, patterns in task_patterns.items():
            task_evidence = []
            
            for change in file_changes:
                if change.change_type in [ChangeType.ADDED, ChangeType.MODIFIED]:
                    # Check if file matches task patterns
                    if self._file_matches_task_patterns(change.file_path, patterns):
                        task_evidence.append(f"Modified {change.file_path}")
                    
                    # Look for content indicators (would need file content analysis)
                    content_indicators = self._detect_content_indicators(
                        change.file_path, 
                        self._task_indicators.get(task_type, [])
                    )
                    task_evidence.extend(content_indicators)
            
            if task_evidence:
                evidence[task_type] = task_evidence
        
        return evidence
    
    def calculate_change_impact(self, changes: List[FileChange]) -> Dict[str, float]:
        """
        Calculate the impact of file changes on different system areas.
        
        Args:
            changes: List of file changes
            
        Returns:
            Dictionary mapping impact areas to impact scores
        """
        impact_scores = {
            "core_functionality": 0.0,
            "test_coverage": 0.0,
            "documentation": 0.0,
            "configuration": 0.0,
            "build_system": 0.0
        }
        
        for change in changes:
            # Calculate base impact based on change type and size
            base_impact = self._calculate_base_impact(change)
            
            # Apply category-specific multipliers
            if change.category == FileCategory.SOURCE_CODE:
                impact_scores["core_functionality"] += base_impact * 1.0
            elif change.category == FileCategory.TEST_CODE:
                impact_scores["test_coverage"] += base_impact * 0.8
            elif change.category == FileCategory.DOCUMENTATION:
                impact_scores["documentation"] += base_impact * 0.5
            elif change.category == FileCategory.CONFIGURATION:
                impact_scores["configuration"] += base_impact * 0.7
            elif change.category == FileCategory.BUILD_SCRIPT:
                impact_scores["build_system"] += base_impact * 0.6
        
        # Normalize scores
        max_score = max(impact_scores.values()) if impact_scores.values() else 1.0
        if max_score > 0:
            for area in impact_scores:
                impact_scores[area] = impact_scores[area] / max_score
        
        return impact_scores
    
    def perform_comprehensive_file_change_analysis(
        self, 
        commits: List[CommitInfo],
        claimed_tasks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive file change analysis as required by task 2.2.
        
        This method specifically addresses the requirements:
        - Code file change analysis to identify modified, added, and deleted files
        - Implement mapping between file changes and claimed task completions
        
        Args:
            commits: List of commits to analyze
            claimed_tasks: Optional list of claimed completed tasks
            
        Returns:
            Comprehensive analysis results including file changes and task mappings
        """
        self.logger.info("Performing comprehensive file change analysis for task 2.2")
        
        try:
            # Step 1: Analyze file changes (modified, added, deleted)
            analysis = self.analyze_file_changes(commits)
            
            # Step 2: Map changes to task completions
            task_mappings = self.map_changes_to_task_completions(
                analysis, 
                claimed_tasks=claimed_tasks
            )
            
            # Step 3: Calculate impact scores
            all_changes = []
            for changes in analysis.changes_by_type.values():
                all_changes.extend(changes)
            
            impact_scores = self.calculate_change_impact(all_changes)
            
            # Step 4: Generate detailed file change breakdown
            file_change_breakdown = self._generate_file_change_breakdown(analysis)
            
            # Step 5: Validate task completion claims
            task_validation = self._validate_task_completion_claims(
                task_mappings, claimed_tasks
            )
            
            # Step 6: Generate accuracy metrics
            accuracy_metrics = self._calculate_detection_accuracy_metrics(
                analysis, task_mappings
            )
            
            # Calculate file counts from changes
            files_added = len([c for c in all_changes if c.change_type == ChangeType.ADDED])
            files_modified = len([c for c in all_changes if c.change_type == ChangeType.MODIFIED])
            files_deleted = len([c for c in all_changes if c.change_type == ChangeType.DELETED])
            
            comprehensive_results = {
                "analysis_summary": {
                    "total_commits_analyzed": len(commits),
                    "total_files_changed": analysis.total_files_changed,
                    "files_added": files_added,
                    "files_modified": files_modified, 
                    "files_deleted": files_deleted,
                    "complexity_score": analysis.complexity_score,
                    "risk_assessment": analysis.risk_assessment
                },
                "file_changes": {
                    "by_type": file_change_breakdown["by_type"],
                    "by_category": file_change_breakdown["by_category"],
                    "high_impact_changes": [
                        {
                            "file_path": change.file_path,
                            "change_type": change.change_type.value,
                            "category": change.category.value,
                            "impact_score": change.impact_score
                        }
                        for change in analysis.high_impact_changes
                    ]
                },
                "task_mappings": [
                    {
                        "task_id": mapping.task_id,
                        "description": mapping.task_description,
                        "confidence_score": mapping.confidence_score,
                        "matching_files": mapping.matching_files,
                        "evidence": mapping.evidence,
                        "completion_indicators": mapping.completion_indicators
                    }
                    for mapping in task_mappings
                ],
                "impact_analysis": impact_scores,
                "task_validation": task_validation,
                "accuracy_metrics": accuracy_metrics,
                "recommendations": self._generate_task_completion_recommendations(
                    task_mappings, claimed_tasks
                )
            }
            
            self.logger.info(
                f"Comprehensive analysis complete: {analysis.total_files_changed} files, "
                f"{len(task_mappings)} task mappings, "
                f"accuracy score: {accuracy_metrics.get('overall_accuracy', 0.0):.2f}"
            )
            
            return comprehensive_results
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive file change analysis: {str(e)}")
            raise
    
    # ReflectiveModule interface implementation
    def get_module_status(self) -> Dict[str, Any]:
        """Get the current status of the file change detector."""
        return {
            "module_name": "FileChangeDetector",
            "repository_path": str(self.repository_path),
            "file_categories": len(self._file_patterns),
            "task_indicators": len(self._task_indicators),
            "is_healthy": self.is_healthy()
        }
    
    def is_healthy(self) -> bool:
        """Check if the file change detector is healthy."""
        try:
            return (
                self.repository_path.exists() and
                self.repository_path.is_dir() and
                len(self._file_patterns) > 0 and
                len(self._task_indicators) > 0
            )
        except Exception:
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health metrics for operational visibility."""
        indicators = {}
        
        try:
            repo_exists = self.repository_path.exists()
            
            indicators["repository_accessible"] = {
                "status": "healthy" if repo_exists else "unhealthy",
                "value": repo_exists,
                "message": f"Repository at {self.repository_path} {'exists' if repo_exists else 'not found'}"
            }
            
            indicators["file_patterns_configured"] = {
                "status": "healthy" if self._file_patterns else "unhealthy",
                "value": len(self._file_patterns),
                "message": f"{len(self._file_patterns)} file pattern categories configured"
            }
            
            indicators["task_indicators_configured"] = {
                "status": "healthy" if self._task_indicators else "unhealthy",
                "value": len(self._task_indicators),
                "message": f"{len(self._task_indicators)} task indicator types configured"
            }
            
        except Exception as e:
            indicators["error"] = {
                "status": "unhealthy",
                "value": str(e),
                "message": f"Error getting health indicators: {str(e)}"
            }
        
        return indicators
    
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module."""
        return "Detect and analyze file changes with advanced categorization and task mapping"
    
    # Private helper methods
    def _extract_file_changes_from_commit(self, commit: CommitInfo) -> List[FileChange]:
        """Extract detailed file changes from a commit."""
        changes = []
        
        # Process added files
        for file_path in commit.added_files:
            change = FileChange(
                file_path=file_path,
                change_type=ChangeType.ADDED,
                category=self._categorize_file(file_path),
                commit_hash=commit.commit_hash
            )
            change.impact_score = self._calculate_base_impact(change)
            changes.append(change)
        
        # Process modified files
        for file_path in commit.modified_files:
            change = FileChange(
                file_path=file_path,
                change_type=ChangeType.MODIFIED,
                category=self._categorize_file(file_path),
                commit_hash=commit.commit_hash
            )
            change.impact_score = self._calculate_base_impact(change)
            changes.append(change)
        
        # Process deleted files
        for file_path in commit.deleted_files:
            change = FileChange(
                file_path=file_path,
                change_type=ChangeType.DELETED,
                category=self._categorize_file(file_path),
                commit_hash=commit.commit_hash
            )
            change.impact_score = self._calculate_base_impact(change)
            changes.append(change)
        
        return changes
    
    def _categorize_file(self, file_path: str) -> FileCategory:
        """Categorize a file based on its path and extension."""
        import fnmatch
        
        # Check more specific patterns first (test files, build scripts)
        priority_order = [
            FileCategory.TEST_CODE,
            FileCategory.BUILD_SCRIPT,
            FileCategory.DOCUMENTATION,
            FileCategory.CONFIGURATION,
            FileCategory.SOURCE_CODE,
            FileCategory.DATA
        ]
        
        for category in priority_order:
            if category in self._file_patterns:
                patterns = self._file_patterns[category]
                for pattern in patterns:
                    if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path.lower(), pattern.lower()):
                        return category
        
        return FileCategory.UNKNOWN
    
    def _categorize_by_type(self, changes: List[FileChange]) -> Dict[ChangeType, List[FileChange]]:
        """Categorize changes by change type."""
        categorized = {}
        
        for change in changes:
            if change.change_type not in categorized:
                categorized[change.change_type] = []
            categorized[change.change_type].append(change)
        
        return categorized
    
    def _categorize_by_file_type(self, changes: List[FileChange]) -> Dict[FileCategory, List[FileChange]]:
        """Categorize changes by file category."""
        categorized = {}
        
        for change in changes:
            if change.category not in categorized:
                categorized[change.category] = []
            categorized[change.category].append(change)
        
        return categorized
    
    def _identify_high_impact_changes(self, changes: List[FileChange]) -> List[FileChange]:
        """Identify high-impact changes based on various criteria."""
        high_impact = []
        
        # Calculate impact threshold (top 20% or minimum score of 0.7)
        impact_scores = [change.impact_score for change in changes]
        if impact_scores:
            threshold = max(0.7, sorted(impact_scores, reverse=True)[int(len(impact_scores) * 0.2)])
            high_impact = [change for change in changes if change.impact_score >= threshold]
        
        return high_impact
    
    def _calculate_complexity_score(self, changes: List[FileChange]) -> float:
        """Calculate overall complexity score for the changes."""
        if not changes:
            return 0.0
        
        # Factors contributing to complexity
        total_files = len(changes)
        source_files = len([c for c in changes if c.category == FileCategory.SOURCE_CODE])
        test_files = len([c for c in changes if c.category == FileCategory.TEST_CODE])
        config_files = len([c for c in changes if c.category == FileCategory.CONFIGURATION])
        
        # Weighted complexity calculation
        complexity = (
            source_files * 1.0 +
            test_files * 0.5 +
            config_files * 0.8 +
            (total_files - source_files - test_files - config_files) * 0.3
        )
        
        # Normalize to 0-10 scale
        return min(10.0, complexity / max(1, total_files) * 10)
    
    def _assess_risk_level(self, changes: List[FileChange], complexity_score: float) -> str:
        """Assess risk level based on changes and complexity."""
        high_impact_count = len([c for c in changes if c.impact_score > 0.7])
        source_changes = len([c for c in changes if c.category == FileCategory.SOURCE_CODE])
        
        if complexity_score > 7 or high_impact_count > 5 or source_changes > 10:
            return "high"
        elif complexity_score > 4 or high_impact_count > 2 or source_changes > 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_base_impact(self, change: FileChange) -> float:
        """Calculate base impact score for a file change."""
        # Base score by change type
        type_scores = {
            ChangeType.ADDED: 0.8,
            ChangeType.MODIFIED: 0.6,
            ChangeType.DELETED: 0.9,
            ChangeType.RENAMED: 0.4,
            ChangeType.COPIED: 0.3
        }
        
        # Category multipliers
        category_multipliers = {
            FileCategory.SOURCE_CODE: 1.0,
            FileCategory.TEST_CODE: 0.7,
            FileCategory.CONFIGURATION: 0.8,
            FileCategory.BUILD_SCRIPT: 0.6,
            FileCategory.DOCUMENTATION: 0.3,
            FileCategory.DATA: 0.4,
            FileCategory.UNKNOWN: 0.5
        }
        
        base_score = type_scores.get(change.change_type, 0.5)
        multiplier = category_multipliers.get(change.category, 0.5)
        
        return base_score * multiplier
    
    def _get_default_task_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get default task definitions for mapping with enhanced patterns."""
        return {
            "git_analysis_implementation": {
                "description": "Implement Git analysis capabilities",
                "task_type": "implementation",
                "file_patterns": [
                    "src/beast_mode/compliance/git/*",
                    "tests/*git*",
                    "tests/test_git_analyzer.py",
                    "tests/test_file_change_detector.py"
                ],
                "content_indicators": ["GitAnalyzer", "commit", "git", "FileChangeDetector"],
                "completion_threshold": 0.6
            },
            "file_change_detection": {
                "description": "Implement file change detection and mapping",
                "task_type": "implementation",
                "file_patterns": [
                    "src/beast_mode/compliance/git/file_change_detector.py",
                    "tests/test_file_change_detector.py"
                ],
                "content_indicators": ["FileChangeDetector", "map_changes_to_task", "analyze_file_changes"],
                "completion_threshold": 0.7
            },
            "rdi_validation_implementation": {
                "description": "Implement RDI validation system",
                "task_type": "implementation",
                "file_patterns": [
                    "src/beast_mode/compliance/rdi/*",
                    "tests/*rdi*"
                ],
                "content_indicators": ["RDI", "requirement", "design", "implementation", "traceability"],
                "completion_threshold": 0.6
            },
            "rm_validation_implementation": {
                "description": "Implement RM validation system",
                "task_type": "implementation",
                "file_patterns": [
                    "src/beast_mode/compliance/rm/*",
                    "tests/*rm*"
                ],
                "content_indicators": ["ReflectiveModule", "RM", "health", "registry", "interface"],
                "completion_threshold": 0.6
            },
            "compliance_orchestrator": {
                "description": "Implement compliance orchestration",
                "task_type": "implementation",
                "file_patterns": [
                    "src/beast_mode/compliance/orchestrator.py",
                    "tests/test_compliance_orchestrator.py"
                ],
                "content_indicators": ["ComplianceOrchestrator", "orchestrat", "workflow"],
                "completion_threshold": 0.6
            },
            "test_implementation": {
                "description": "Implement comprehensive tests",
                "task_type": "testing",
                "file_patterns": [
                    "tests/*",
                    "*test*.py"
                ],
                "content_indicators": ["test_", "assert", "pytest", "mock", "fixture"],
                "completion_threshold": 0.5
            },
            "documentation_updates": {
                "description": "Update documentation",
                "task_type": "documentation",
                "file_patterns": [
                    "docs/*",
                    "*.md",
                    "README*",
                    ".kiro/specs/*"
                ],
                "content_indicators": ["#", "##", "```", "documentation", "spec"],
                "completion_threshold": 0.4
            },
            "configuration_updates": {
                "description": "Update configuration files",
                "task_type": "configuration",
                "file_patterns": [
                    "*.json",
                    "*.yaml",
                    "*.yml",
                    "*.toml",
                    "pyproject.toml"
                ],
                "content_indicators": ["config", "settings", "dependencies"],
                "completion_threshold": 0.5
            }
        }
    
    def _analyze_task_completion_enhanced(
        self, 
        task_id: str, 
        task_config: Dict[str, Any], 
        analysis: AdvancedFileChangeAnalysis,
        claimed_tasks: Optional[List[str]] = None
    ) -> TaskMapping:
        """Enhanced analysis of potential task completion based on file changes."""
        matching_files = []
        evidence = []
        confidence_factors = []
        completion_indicators = []
        
        # Check file pattern matches
        file_patterns = task_config.get("file_patterns", [])
        all_changed_files = []
        
        for changes in analysis.changes_by_type.values():
            all_changed_files.extend([c.file_path for c in changes])
        
        # Enhanced file pattern matching with categorization
        for file_path in all_changed_files:
            if self._file_matches_task_patterns(file_path, file_patterns):
                matching_files.append(file_path)
                
                # Get the specific change for this file
                file_change = self._find_file_change_in_analysis(file_path, analysis)
                if file_change:
                    change_type_desc = f"{file_change.change_type.value}"
                    category_desc = f"{file_change.category.value}"
                    evidence.append(f"{change_type_desc.title()} {category_desc} file: {file_path}")
                    
                    # Add completion indicators based on file type and change
                    if file_change.category == FileCategory.TEST_CODE:
                        completion_indicators.append(f"Test implementation: {file_path}")
                    elif file_change.category == FileCategory.SOURCE_CODE:
                        completion_indicators.append(f"Source implementation: {file_path}")
                    elif file_change.category == FileCategory.DOCUMENTATION:
                        completion_indicators.append(f"Documentation update: {file_path}")
        
        # Calculate confidence based on file matches with enhanced scoring
        if file_patterns and matching_files:
            # Base confidence from file pattern matches
            file_match_confidence = min(1.0, len(matching_files) / len(file_patterns))
            
            # Boost confidence for high-impact changes
            high_impact_files = [f for f in matching_files 
                               if self._is_high_impact_file(f, analysis)]
            if high_impact_files:
                file_match_confidence *= 1.2  # 20% boost for high-impact files
            
            confidence_factors.append(min(1.0, file_match_confidence))
        
        # Enhanced content indicators analysis
        content_indicators = task_config.get("content_indicators", [])
        if content_indicators and matching_files:
            content_confidence = self._analyze_content_indicators(
                matching_files, content_indicators, analysis
            )
            confidence_factors.append(content_confidence)
        
        # Check for task completion patterns
        task_type = task_config.get("task_type", "implementation")
        pattern_confidence = self._analyze_task_completion_patterns(
            matching_files, task_type, analysis
        )
        if pattern_confidence > 0:
            confidence_factors.append(pattern_confidence)
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
        
        # Apply completion threshold with enhanced logic
        completion_threshold = task_config.get("completion_threshold", 0.5)
        if overall_confidence < completion_threshold:
            overall_confidence *= 0.7  # Less harsh penalty for enhanced analysis
        
        # Validate against claimed tasks if provided
        is_claimed = claimed_tasks and any(task_id in claimed for claimed in claimed_tasks)
        if is_claimed and overall_confidence < 0.3:
            evidence.append(f"WARNING: Task claimed as complete but low implementation evidence")
        elif not is_claimed and overall_confidence > 0.8:
            evidence.append(f"INFO: High implementation evidence but task not claimed as complete")
        
        return TaskMapping(
            task_id=task_id,
            task_description=task_config.get("description", task_id),
            confidence_score=overall_confidence,
            matching_files=matching_files,
            evidence=evidence,
            completion_indicators=completion_indicators
        )
    
    def _analyze_task_completion(
        self, 
        task_id: str, 
        task_config: Dict[str, Any], 
        analysis: AdvancedFileChangeAnalysis
    ) -> TaskMapping:
        """Legacy method - delegates to enhanced version for backward compatibility."""
        return self._analyze_task_completion_enhanced(task_id, task_config, analysis)
    
    def _file_matches_task_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if a file matches any of the task patterns."""
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False
    
    def _detect_content_indicators(self, file_path: str, indicators: List[str]) -> List[str]:
        """Detect content indicators in a file (placeholder implementation)."""
        # This would require actual file content analysis
        # For now, return placeholder based on file name
        detected = []
        
        for indicator in indicators:
            if indicator.lower() in file_path.lower():
                detected.append(f"Found indicator '{indicator}' in {file_path}")
        
        return detected
    
    def _find_file_change_in_analysis(self, file_path: str, analysis: AdvancedFileChangeAnalysis) -> Optional[FileChange]:
        """Find the FileChange object for a specific file path in the analysis."""
        for changes in analysis.changes_by_type.values():
            for change in changes:
                if change.file_path == file_path:
                    return change
        return None
    
    def _is_high_impact_file(self, file_path: str, analysis: AdvancedFileChangeAnalysis) -> bool:
        """Check if a file is considered high-impact based on the analysis."""
        for high_impact_change in analysis.high_impact_changes:
            if high_impact_change.file_path == file_path:
                return True
        return False
    
    def _analyze_content_indicators(
        self, 
        matching_files: List[str], 
        content_indicators: List[str], 
        analysis: AdvancedFileChangeAnalysis
    ) -> float:
        """Analyze content indicators in matching files to determine completion confidence."""
        if not matching_files or not content_indicators:
            return 0.0
        
        indicator_matches = 0
        total_possible_matches = len(matching_files) * len(content_indicators)
        
        for file_path in matching_files:
            # Check file name/path for indicators
            for indicator in content_indicators:
                if indicator.lower() in file_path.lower():
                    indicator_matches += 1
            
            # Check file category for implicit indicators
            file_change = self._find_file_change_in_analysis(file_path, analysis)
            if file_change:
                if file_change.category == FileCategory.TEST_CODE and "test" in content_indicators:
                    indicator_matches += 1
                elif file_change.category == FileCategory.SOURCE_CODE and any(
                    ind in content_indicators for ind in ["class", "function", "implementation"]
                ):
                    indicator_matches += 1
        
        return min(1.0, indicator_matches / max(1, total_possible_matches))
    
    def _analyze_task_completion_patterns(
        self, 
        matching_files: List[str], 
        task_type: str, 
        analysis: AdvancedFileChangeAnalysis
    ) -> float:
        """Analyze task completion patterns based on file changes and task type."""
        if not matching_files:
            return 0.0
        
        pattern_score = 0.0
        
        # Analyze patterns based on task type
        if task_type == "implementation":
            # Look for source + test file pairs
            source_files = [f for f in matching_files if self._is_source_file(f)]
            test_files = [f for f in matching_files if self._is_test_file(f)]
            
            if source_files and test_files:
                pattern_score += 0.8  # High score for implementation + tests
            elif source_files:
                pattern_score += 0.6  # Medium score for implementation only
            elif test_files:
                pattern_score += 0.4  # Lower score for tests only
        
        elif task_type == "testing":
            # Look for test files and test-related changes
            test_files = [f for f in matching_files if self._is_test_file(f)]
            pattern_score = min(1.0, len(test_files) / max(1, len(matching_files)))
        
        elif task_type == "documentation":
            # Look for documentation files
            doc_files = [f for f in matching_files if self._is_documentation_file(f)]
            pattern_score = min(1.0, len(doc_files) / max(1, len(matching_files)))
        
        elif task_type == "configuration":
            # Look for configuration files
            config_files = [f for f in matching_files if self._is_config_file(f)]
            pattern_score = min(1.0, len(config_files) / max(1, len(matching_files)))
        
        return pattern_score
    
    def _validate_claimed_vs_implemented(
        self, 
        task_mappings: List[TaskMapping], 
        claimed_tasks: List[str]
    ) -> None:
        """Validate claimed task completions against implementation evidence."""
        self.logger.info("Validating claimed tasks against implementation evidence")
        
        # Create mapping of task IDs to confidence scores
        implementation_evidence = {mapping.task_id: mapping.confidence_score 
                                 for mapping in task_mappings}
        
        for claimed_task in claimed_tasks:
            confidence = implementation_evidence.get(claimed_task, 0.0)
            
            # Find the corresponding task mapping
            task_mapping = next((m for m in task_mappings if m.task_id == claimed_task), None)
            
            if task_mapping:
                if confidence < 0.3:
                    task_mapping.evidence.append(
                        f"WARNING: Task claimed complete but low implementation evidence (confidence: {confidence:.2f})"
                    )
                elif confidence > 0.7:
                    task_mapping.evidence.append(
                        f"VALIDATED: Task completion claim supported by strong evidence (confidence: {confidence:.2f})"
                    )
                else:
                    task_mapping.evidence.append(
                        f"PARTIAL: Task completion claim has moderate evidence (confidence: {confidence:.2f})"
                    )
    
    def _is_source_file(self, file_path: str) -> bool:
        """Check if a file is a source code file."""
        return self._categorize_file(file_path) == FileCategory.SOURCE_CODE
    
    def _is_test_file(self, file_path: str) -> bool:
        """Check if a file is a test file."""
        return self._categorize_file(file_path) == FileCategory.TEST_CODE
    
    def _is_documentation_file(self, file_path: str) -> bool:
        """Check if a file is a documentation file."""
        return self._categorize_file(file_path) == FileCategory.DOCUMENTATION
    
    def _is_config_file(self, file_path: str) -> bool:
        """Check if a file is a configuration file."""
        return self._categorize_file(file_path) == FileCategory.CONFIGURATION
    
    def _generate_file_change_breakdown(self, analysis: AdvancedFileChangeAnalysis) -> Dict[str, Any]:
        """Generate detailed breakdown of file changes."""
        breakdown = {
            "by_type": {},
            "by_category": {}
        }
        
        # Breakdown by change type
        for change_type, changes in analysis.changes_by_type.items():
            breakdown["by_type"][change_type.value] = {
                "count": len(changes),
                "files": [change.file_path for change in changes],
                "total_impact": sum(change.impact_score for change in changes)
            }
        
        # Breakdown by file category
        for category, changes in analysis.changes_by_category.items():
            breakdown["by_category"][category.value] = {
                "count": len(changes),
                "files": [change.file_path for change in changes],
                "total_impact": sum(change.impact_score for change in changes)
            }
        
        return breakdown
    
    def _validate_task_completion_claims(
        self, 
        task_mappings: List[TaskMapping], 
        claimed_tasks: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Validate task completion claims against implementation evidence."""
        if not claimed_tasks:
            return {
                "validation_performed": False,
                "message": "No claimed tasks provided for validation"
            }
        
        validation_results = {
            "validation_performed": True,
            "total_claimed_tasks": len(claimed_tasks),
            "validated_tasks": [],
            "questionable_tasks": [],
            "missing_evidence_tasks": [],
            "unclaimed_implementations": []
        }
        
        # Create mapping for easy lookup
        mapping_by_task = {mapping.task_id: mapping for mapping in task_mappings}
        
        for claimed_task in claimed_tasks:
            mapping = mapping_by_task.get(claimed_task)
            
            if mapping:
                if mapping.confidence_score >= 0.7:
                    validation_results["validated_tasks"].append({
                        "task_id": claimed_task,
                        "confidence": mapping.confidence_score,
                        "status": "validated"
                    })
                elif mapping.confidence_score >= 0.3:
                    validation_results["questionable_tasks"].append({
                        "task_id": claimed_task,
                        "confidence": mapping.confidence_score,
                        "status": "questionable"
                    })
                else:
                    validation_results["missing_evidence_tasks"].append({
                        "task_id": claimed_task,
                        "confidence": mapping.confidence_score,
                        "status": "missing_evidence"
                    })
            else:
                validation_results["missing_evidence_tasks"].append({
                    "task_id": claimed_task,
                    "confidence": 0.0,
                    "status": "no_evidence"
                })
        
        # Find high-confidence mappings that weren't claimed
        claimed_task_ids = set(claimed_tasks)
        for mapping in task_mappings:
            if mapping.task_id not in claimed_task_ids and mapping.confidence_score >= 0.7:
                validation_results["unclaimed_implementations"].append({
                    "task_id": mapping.task_id,
                    "confidence": mapping.confidence_score,
                    "status": "unclaimed_but_implemented"
                })
        
        return validation_results
    
    def _calculate_detection_accuracy_metrics(
        self, 
        analysis: AdvancedFileChangeAnalysis, 
        task_mappings: List[TaskMapping]
    ) -> Dict[str, float]:
        """Calculate accuracy metrics for file change detection."""
        metrics = {
            "file_categorization_confidence": 0.0,
            "task_mapping_confidence": 0.0,
            "overall_accuracy": 0.0,
            "high_confidence_mappings_ratio": 0.0,
            "coverage_completeness": 0.0
        }
        
        # File categorization confidence (based on known vs unknown files)
        all_changes = []
        for changes in analysis.changes_by_type.values():
            all_changes.extend(changes)
        
        if all_changes:
            known_category_changes = [c for c in all_changes if c.category != FileCategory.UNKNOWN]
            metrics["file_categorization_confidence"] = len(known_category_changes) / len(all_changes)
        
        # Task mapping confidence
        if task_mappings:
            total_confidence = sum(mapping.confidence_score for mapping in task_mappings)
            metrics["task_mapping_confidence"] = total_confidence / len(task_mappings)
            
            # High confidence mappings ratio
            high_confidence_mappings = [m for m in task_mappings if m.confidence_score >= 0.7]
            metrics["high_confidence_mappings_ratio"] = len(high_confidence_mappings) / len(task_mappings)
        
        # Coverage completeness (how many files are covered by task mappings)
        if all_changes:
            mapped_files = set()
            for mapping in task_mappings:
                mapped_files.update(mapping.matching_files)
            
            total_files = set(change.file_path for change in all_changes)
            if total_files:
                metrics["coverage_completeness"] = len(mapped_files) / len(total_files)
        
        # Overall accuracy (weighted average)
        metrics["overall_accuracy"] = (
            metrics["file_categorization_confidence"] * 0.3 +
            metrics["task_mapping_confidence"] * 0.4 +
            metrics["coverage_completeness"] * 0.3
        )
        
        return metrics
    
    def _generate_task_completion_recommendations(
        self, 
        task_mappings: List[TaskMapping], 
        claimed_tasks: Optional[List[str]]
    ) -> List[str]:
        """Generate recommendations based on task completion analysis."""
        recommendations = []
        
        if not task_mappings:
            recommendations.append("No task mappings found - consider reviewing file change patterns")
            return recommendations
        
        # High confidence mappings
        high_confidence = [m for m in task_mappings if m.confidence_score >= 0.7]
        if high_confidence:
            recommendations.append(
                f"Found {len(high_confidence)} high-confidence task implementations"
            )
        
        # Low confidence mappings that are claimed
        if claimed_tasks:
            claimed_set = set(claimed_tasks)
            low_confidence_claimed = [
                m for m in task_mappings 
                if m.task_id in claimed_set and m.confidence_score < 0.3
            ]
            
            if low_confidence_claimed:
                recommendations.append(
                    f"Review {len(low_confidence_claimed)} claimed tasks with low implementation evidence"
                )
        
        # Unclaimed high-confidence implementations
        if claimed_tasks:
            claimed_set = set(claimed_tasks)
            unclaimed_high_confidence = [
                m for m in task_mappings 
                if m.task_id not in claimed_set and m.confidence_score >= 0.7
            ]
            
            if unclaimed_high_confidence:
                recommendations.append(
                    f"Consider claiming {len(unclaimed_high_confidence)} tasks with strong implementation evidence"
                )
        
        # File coverage recommendations
        total_files_mapped = sum(len(m.matching_files) for m in task_mappings)
        if total_files_mapped == 0:
            recommendations.append("No files mapped to tasks - review task patterns and file changes")
        elif total_files_mapped < 5:
            recommendations.append("Low file coverage in task mappings - consider expanding task patterns")
        
        return recommendations