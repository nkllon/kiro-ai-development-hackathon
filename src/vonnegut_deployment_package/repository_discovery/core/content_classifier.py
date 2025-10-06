#!/usr/bin/env python3
"""
Content Classifier - Repository Discovery System
===============================================

Classifies repository content types with confidence scoring and batch processing.
Follows RM-DDD patterns with complete monitoring integration.

Author: Repository Discovery System
Date: 2025-01-16
Version: 1.0
"""

import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)


class ContentType(Enum):
    """Repository content types"""
    SPECIFICATION = "specification"
    SOURCE_CODE = "source_code"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    SCRIPT = "script"
    TEST = "test"
    CONFIGURATION = "configuration"
    DATA = "data"
    UNKNOWN = "unknown"


@dataclass
class ClassificationResult:
    """Result of content classification"""
    file_path: Path
    primary_type: ContentType
    confidence: float
    alternative_types: List[Tuple[ContentType, float]]
    classification_reasons: List[str]
    metadata: Dict[str, Any]


@dataclass
class ClassificationBatch:
    """Batch classification results"""
    batch_id: str
    results: List[ClassificationResult]
    total_files: int
    processing_time: float
    average_confidence: float
    accuracy_metrics: Dict[str, float]


class ContentClassifier(ReflectiveModule):
    """
    Content Classifier - RM-DDD Compliant
    
    Classifies repository content types with confidence scoring.
    Provides systematic classification using pattern matching and heuristics.
    
    Single Responsibility: Classify repository content types with confidence
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "ContentClassifier"
        self._config = config or {}
        self._logger = logging.getLogger(f"repository_discovery.core.{self.__class__.__name__}")
        
        # Classification patterns
        self._init_classification_patterns()
        
        # Performance tracking
        self._classification_count = 0
        self._total_processing_time = 0.0
        
        self._logger.info(f"ContentClassifier initialized")
    
    def _init_classification_patterns(self):
        """Initialize classification patterns and rules"""
        self._file_extension_patterns = {
            ContentType.SPECIFICATION: {
                'extensions': ['.md', '.txt', '.rst'],
                'path_patterns': [r'.*spec.*', r'.*requirement.*', r'.*\.kiro/specs/.*'],
                'content_patterns': [
                    r'# Requirements?',
                    r'## User Story',
                    r'### Acceptance Criteria',
                    r'WHEN.*THEN.*SHALL'
                ]
            },
            ContentType.SOURCE_CODE: {
                'extensions': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'],
                'path_patterns': [r'.*src/.*', r'.*lib/.*'],
                'content_patterns': [
                    r'class\s+\w+',
                    r'def\s+\w+',
                    r'function\s+\w+',
                    r'import\s+\w+'
                ]
            },
            ContentType.DOCUMENTATION: {
                'extensions': ['.md', '.rst', '.txt', '.adoc'],
                'path_patterns': [r'.*docs?/.*', r'.*README.*', r'.*CHANGELOG.*'],
                'content_patterns': [
                    r'# .*Documentation',
                    r'## Installation',
                    r'## Usage',
                    r'## API'
                ]
            },
            ContentType.ANALYSIS: {
                'extensions': ['.json', '.md', '.txt', '.py'],
                'path_patterns': [r'.*analysis.*', r'.*report.*', r'.*summary.*'],
                'content_patterns': [
                    r'.*analysis.*',
                    r'.*report.*',
                    r'.*summary.*',
                    r'.*metrics.*'
                ]
            },
            ContentType.SCRIPT: {
                'extensions': ['.py', '.sh', '.bash', '.ps1', '.bat'],
                'path_patterns': [r'.*scripts?/.*', r'.*bin/.*', r'.*tools?/.*'],
                'content_patterns': [
                    r'#!/.*',
                    r'if __name__ == ["\']__main__["\']',
                    r'@click\.command',
                    r'argparse\.'
                ]
            },
            ContentType.TEST: {
                'extensions': ['.py', '.js', '.ts', '.java'],
                'path_patterns': [r'.*tests?/.*', r'.*test_.*', r'.*_test\..*'],
                'content_patterns': [
                    r'def test_',
                    r'class Test',
                    r'@pytest\.',
                    r'unittest\.',
                    r'assert\s+'
                ]
            },
            ContentType.CONFIGURATION: {
                'extensions': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml'],
                'path_patterns': [r'.*config.*', r'.*\.kiro/.*', r'.*deployment/.*'],
                'content_patterns': [
                    r'\[.*\]',  # INI sections
                    r'.*:\s*.*',  # YAML/JSON key-value
                    r'version\s*=',
                    r'dependencies'
                ],
                'exclusion_extensions': ['.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.zip', '.tar', '.gz'],
                'exclusion_patterns': [r'.*\.html?$', r'.*\.(png|jpg|jpeg|gif|svg)$', r'.*\.(pdf|zip|tar|gz)$']
            },
            ContentType.DATA: {
                'extensions': ['.csv', '.json', '.xml', '.sql', '.db'],
                'path_patterns': [r'.*data/.*', r'.*fixtures?/.*'],
                'content_patterns': [
                    r'CREATE TABLE',
                    r'INSERT INTO',
                    r'SELECT.*FROM',
                    r'<\?xml'
                ]
            }
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ContentClassifier",
            "version": "1.0.0",
            "description": "Classifies repository content types with confidence scoring",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "classifications_performed": self._classification_count,
            "average_processing_time": self._get_average_processing_time()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Test classification capability
            test_path = Path("test.py")
            result = self._classify_single_file(test_path, "def test_function(): pass")
            
            if result.confidence > 0.5:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = ["Low classification confidence in test"]
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Classification failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, use only file extensions
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY
            ]
            
            degraded_capabilities = [
                ModuleCapability.DATA_PROCESSING,  # May lose content analysis
                ModuleCapability.VALIDATION  # May lose confidence scoring
            ]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def classify_content_types(
        self,
        file_paths: List[Path],
        batch_size: int = 100,
        confidence_threshold: float = 0.7,
        include_alternatives: bool = True
    ) -> ClassificationBatch:
        """
        Classify content types with confidence scoring and batch processing.
        
        Args:
            file_paths: List of file paths to classify
            batch_size: Number of files to process in each batch
            confidence_threshold: Minimum confidence for primary classification
            include_alternatives: Whether to include alternative classifications
            
        Returns:
            ClassificationBatch with results and metrics
        """
        with self.trace_operation("classify_content_types") as trace:
            try:
                import time
                start_time = time.time()
                
                batch_id = f"batch_{int(start_time)}"
                results = []
                
                # Process files in batches
                for i in range(0, len(file_paths), batch_size):
                    batch_files = file_paths[i:i + batch_size]
                    
                    for file_path in batch_files:
                        try:
                            # Read file content if possible
                            content = self._read_file_safely(file_path)
                            result = self._classify_single_file(
                                file_path, 
                                content, 
                                confidence_threshold,
                                include_alternatives
                            )
                            results.append(result)
                            
                        except Exception as e:
                            # Create unknown classification for failed files
                            result = ClassificationResult(
                                file_path=file_path,
                                primary_type=ContentType.UNKNOWN,
                                confidence=0.0,
                                alternative_types=[],
                                classification_reasons=[f"Classification failed: {str(e)}"],
                                metadata={"error": str(e)}
                            )
                            results.append(result)
                
                processing_time = time.time() - start_time
                
                # Calculate metrics
                confidences = [r.confidence for r in results]
                average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                accuracy_metrics = self._calculate_accuracy_metrics(results)
                
                batch = ClassificationBatch(
                    batch_id=batch_id,
                    results=results,
                    total_files=len(file_paths),
                    processing_time=processing_time,
                    average_confidence=average_confidence,
                    accuracy_metrics=accuracy_metrics
                )
                
                # Update performance tracking
                self._classification_count += len(results)
                self._total_processing_time += processing_time
                
                trace.output_result = {
                    'batch_id': batch_id,
                    'files_processed': len(results),
                    'average_confidence': average_confidence,
                    'processing_time': processing_time
                }
                
                self._logger.info(f"Classified {len(results)} files in {processing_time:.2f}s")
                return batch
                
            except Exception as e:
                self._logger.error(f"Batch classification failed: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                raise
    
    def get_classification_confidence(self, file_path: Path) -> float:
        """Get confidence score for single file classification"""
        with self.trace_operation("get_classification_confidence") as trace:
            try:
                content = self._read_file_safely(file_path)
                result = self._classify_single_file(file_path, content)
                
                trace.output_result = {
                    'file_path': str(file_path),
                    'confidence': result.confidence,
                    'primary_type': result.primary_type.value
                }
                
                return result.confidence
                
            except Exception as e:
                self._logger.error(f"Failed to get confidence for {file_path}: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                return 0.0
    
    def _classify_single_file(
        self, 
        file_path: Path, 
        content: Optional[str] = None,
        confidence_threshold: float = 0.7,
        include_alternatives: bool = True
    ) -> ClassificationResult:
        """Classify a single file with confidence scoring"""
        
        # Handle non-existent files
        if not file_path.exists():
            return ClassificationResult(
                file_path=file_path,
                primary_type=ContentType.UNKNOWN,
                confidence=0.0,
                alternative_types=[],
                classification_reasons=["File does not exist"],
                metadata={"file_size": 0, "has_content": False, "content_length": 0}
            )
        
        # Calculate scores for each content type
        type_scores = {}
        all_reasons = {}
        
        for content_type, patterns in self._file_extension_patterns.items():
            score = 0.0
            reasons = []
            
            # Check exclusions first - if file matches exclusion, skip this content type
            if 'exclusion_extensions' in patterns:
                if file_path.suffix.lower() in patterns['exclusion_extensions']:
                    type_scores[content_type] = 0.0
                    all_reasons[content_type] = [f"Excluded by extension {file_path.suffix}"]
                    continue
            
            if 'exclusion_patterns' in patterns:
                excluded = False
                for exclusion_pattern in patterns['exclusion_patterns']:
                    if re.search(exclusion_pattern, str(file_path), re.IGNORECASE):
                        type_scores[content_type] = 0.0
                        all_reasons[content_type] = [f"Excluded by pattern {exclusion_pattern}"]
                        excluded = True
                        break
                if excluded:
                    continue
            
            # Check file extension (30% weight)
            if file_path.suffix.lower() in patterns['extensions']:
                score += 0.3
                reasons.append(f"Extension {file_path.suffix} matches {content_type.value}")
            
            # Check path patterns (25% weight)
            for path_pattern in patterns['path_patterns']:
                if re.search(path_pattern, str(file_path), re.IGNORECASE):
                    score += 0.25
                    reasons.append(f"Path matches {content_type.value} pattern")
                    break
            
            # Check content patterns (45% weight)
            if content:
                content_matches = 0
                for content_pattern in patterns['content_patterns']:
                    if re.search(content_pattern, content, re.IGNORECASE | re.MULTILINE):
                        content_matches += 1
                
                if content_matches > 0:
                    content_score = min(0.45, content_matches * 0.15)
                    score += content_score
                    reasons.append(f"Content matches {content_matches} {content_type.value} patterns")
            
            type_scores[content_type] = score
            all_reasons[content_type] = reasons
        
        # Find primary type and alternatives
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_type, primary_score = sorted_types[0]
        
        # Special handling for test files - prioritize test classification if path indicates test
        if "test" in str(file_path).lower() and ContentType.TEST in type_scores:
            test_score = type_scores[ContentType.TEST]
            if test_score > 0.5:  # Strong test indicators
                primary_type = ContentType.TEST
                primary_score = test_score
        
        # If primary score is too low, classify as unknown
        if primary_score < 0.2:
            primary_type = ContentType.UNKNOWN
            primary_score = 0.0
            classification_reasons = ["No strong classification patterns found"]
        else:
            # Use reasons from the primary type
            classification_reasons = all_reasons.get(primary_type, [])
        
        # Get alternatives if requested
        alternative_types = []
        if include_alternatives:
            for content_type, score in sorted_types[1:4]:  # Top 3 alternatives
                if score > 0.1 and content_type != primary_type:  # Only include meaningful alternatives
                    alternative_types.append((content_type, score))
        
        return ClassificationResult(
            file_path=file_path,
            primary_type=primary_type,
            confidence=primary_score,
            alternative_types=alternative_types,
            classification_reasons=classification_reasons,
            metadata={
                "file_size": self._get_file_size(file_path),
                "has_content": content is not None,
                "content_length": len(content) if content else 0
            }
        )
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Safely read file content for classification"""
        try:
            if not file_path.exists():
                return None
            
            # Skip binary files and very large files
            if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
                return None
            
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(8192)  # Read first 8KB for classification
                
        except Exception:
            return None
    
    def _get_file_size(self, file_path: Path) -> int:
        """Get file size safely"""
        try:
            return file_path.stat().st_size
        except Exception:
            return 0
    
    def _calculate_accuracy_metrics(self, results: List[ClassificationResult]) -> Dict[str, float]:
        """Calculate accuracy metrics for batch"""
        if not results:
            return {}
        
        # Count classifications by type
        type_counts = {}
        confidence_by_type = {}
        
        for result in results:
            content_type = result.primary_type
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
            
            if content_type not in confidence_by_type:
                confidence_by_type[content_type] = []
            confidence_by_type[content_type].append(result.confidence)
        
        # Calculate metrics
        metrics = {
            "total_files": len(results),
            "unknown_ratio": type_counts.get(ContentType.UNKNOWN, 0) / len(results),
            "high_confidence_ratio": len([r for r in results if r.confidence > 0.7]) / len(results)
        }
        
        # Add per-type confidence averages
        for content_type, confidences in confidence_by_type.items():
            avg_confidence = sum(confidences) / len(confidences)
            metrics[f"{content_type.value}_avg_confidence"] = avg_confidence
        
        return metrics
    
    def _get_average_processing_time(self) -> float:
        """Get average processing time per file"""
        if self._classification_count == 0:
            return 0.0
        return self._total_processing_time / self._classification_count