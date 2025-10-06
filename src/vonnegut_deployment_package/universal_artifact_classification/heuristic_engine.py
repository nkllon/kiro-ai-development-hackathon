"""
Heuristic Generation Engine - Creates efficient rules from learned patterns.

This engine generates fast heuristic rules from successful classifications,
enabling the Babel Fish to become more efficient over time.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict, Counter
from datetime import datetime

from .models import ClassificationResult, HeuristicRule


logger = logging.getLogger(__name__)


class HeuristicGenerationEngine:
    """
    Generates efficient heuristic rules from learned patterns.
    
    The engine learns from successful classifications and creates fast-path
    rules that can handle common cases without deep learning inference.
    """
    
    def __init__(self):
        self.rules: Dict[str, HeuristicRule] = {}
        self.pattern_frequency: Dict[str, Counter] = defaultdict(Counter)
        self.classification_history: List[ClassificationResult] = []
        
        # Initialize with basic heuristic rules
        self._initialize_basic_rules()
        
        logger.info("Heuristic Generation Engine initialized")
    
    def _initialize_basic_rules(self):
        """Initialize with basic, high-confidence heuristic rules"""
        basic_rules = [
            {
                "pattern": "extension:.py",
                "classification": "source_code",
                "confidence": 0.98
            },
            {
                "pattern": "extension:.js",
                "classification": "source_code", 
                "confidence": 0.97
            },
            {
                "pattern": "filename:dockerfile",
                "classification": "configuration",
                "confidence": 0.99
            },
            {
                "pattern": "filename:readme.md",
                "classification": "documentation",
                "confidence": 0.99
            },
            {
                "pattern": "extension:.json",
                "classification": "configuration",
                "confidence": 0.85
            },
            {
                "pattern": "in_tests_directory",
                "classification": "test_file",
                "confidence": 0.92
            },
            {
                "pattern": "prefix:test_",
                "classification": "test_file",
                "confidence": 0.95
            }
        ]
        
        for i, rule_data in enumerate(basic_rules):
            rule = HeuristicRule(
                rule_id=f"basic_{i}",
                pattern=rule_data["pattern"],
                classification=rule_data["classification"],
                confidence_threshold=rule_data["confidence"],
                accuracy_rate=rule_data["confidence"],
                usage_count=0,
                created_at=datetime.now(),
                last_validated=datetime.now()
            )
            self.rules[rule.rule_id] = rule
    
    def quick_classify(self, artifact_path: Path) -> Optional[ClassificationResult]:
        """
        Attempt quick classification using heuristic rules.
        
        Returns classification if a high-confidence rule matches,
        otherwise returns None to trigger deep learning.
        """
        # Extract basic patterns from artifact
        patterns = self._extract_patterns(artifact_path)
        
        # Find matching rules
        best_rule = None
        best_confidence = 0.0
        
        for rule in self.rules.values():
            if self._pattern_matches(rule.pattern, patterns):
                if rule.confidence_threshold > best_confidence:
                    best_rule = rule
                    best_confidence = rule.confidence_threshold
        
        if best_rule and best_confidence > 0.95:  # High confidence threshold
            # Update usage count
            best_rule.usage_count += 1
            
            return ClassificationResult(
                artifact_path=str(artifact_path),
                predicted_type=best_rule.classification,
                confidence=best_rule.confidence_threshold,
                alternative_types=[],
                features_used=[best_rule.pattern],
                requires_review=False,
                processing_time_ms=0.0,  # Will be set by caller
                model_used="heuristic"
            )
        
        return None
    
    def update_rules(self, artifact_path: Path, classification_result: ClassificationResult):
        """
        Learn new heuristic rules from successful classifications.
        
        Analyzes successful deep learning classifications to extract
        patterns that can be turned into efficient heuristic rules.
        """
        # Store classification history
        self.classification_history.append(classification_result)
        
        # Only learn from high-confidence classifications
        if classification_result.confidence < 0.90:
            return
        
        # Extract patterns from this successful classification
        patterns = self._extract_patterns(Path(classification_result.artifact_path))
        
        # Update pattern frequency for this classification type
        for pattern in patterns:
            self.pattern_frequency[classification_result.predicted_type][pattern] += 1
        
        # Generate new rules if we have enough evidence
        self._generate_new_rules()
    
    def _extract_patterns(self, artifact_path: Path) -> List[str]:
        """Extract patterns from artifact path and basic properties"""
        patterns = []
        
        # File extension pattern
        if artifact_path.suffix:
            patterns.append(f"extension:{artifact_path.suffix.lower()}")
        
        # Filename pattern
        patterns.append(f"filename:{artifact_path.name.lower()}")
        
        # Directory patterns
        parts = artifact_path.parts
        if len(parts) > 1:
            patterns.append(f"parent_dir:{parts[-2].lower()}")
        
        # Special filename patterns
        name_lower = artifact_path.name.lower()
        if "test" in name_lower:
            patterns.append("contains:test")
        if "config" in name_lower:
            patterns.append("contains:config")
        if "readme" in name_lower:
            patterns.append("contains:readme")
        if name_lower.startswith("test_"):
            patterns.append("prefix:test_")
        if name_lower.endswith("_test.py"):
            patterns.append("suffix:_test.py")
        
        # Test directory patterns
        path_str = str(artifact_path).lower()
        if "/test" in path_str or "\\test" in path_str:
            patterns.append("in_test_directory")
        if "/tests/" in path_str or "\\tests\\" in path_str:
            patterns.append("in_tests_directory")
        
        return patterns
    
    def _pattern_matches(self, rule_pattern: str, artifact_patterns: List[str]) -> bool:
        """Check if a rule pattern matches any of the artifact patterns"""
        return rule_pattern in artifact_patterns
    
    def _generate_new_rules(self):
        """Generate new heuristic rules from pattern frequency analysis"""
        min_frequency = 5  # Minimum occurrences to create a rule
        min_accuracy = 0.85  # Minimum accuracy to create a rule
        
        for classification_type, pattern_counter in self.pattern_frequency.items():
            for pattern, frequency in pattern_counter.items():
                if frequency >= min_frequency:
                    # Calculate accuracy for this pattern
                    accuracy = self._calculate_pattern_accuracy(pattern, classification_type)
                    
                    if accuracy >= min_accuracy:
                        # Create new rule if it doesn't exist
                        rule_id = f"learned_{pattern}_{classification_type}"
                        
                        if rule_id not in self.rules:
                            new_rule = HeuristicRule(
                                rule_id=rule_id,
                                pattern=pattern,
                                classification=classification_type,
                                confidence_threshold=accuracy,
                                accuracy_rate=accuracy,
                                usage_count=0,
                                created_at=datetime.now(),
                                last_validated=datetime.now()
                            )
                            
                            self.rules[rule_id] = new_rule
                            logger.info(f"Generated new heuristic rule: {pattern} -> {classification_type} ({accuracy:.2f})")
    
    def _calculate_pattern_accuracy(self, pattern: str, classification_type: str) -> float:
        """Calculate accuracy of a pattern for a specific classification type"""
        pattern_matches = 0
        correct_matches = 0
        
        for result in self.classification_history:
            artifact_patterns = self._extract_patterns(Path(result.artifact_path))
            
            if pattern in artifact_patterns:
                pattern_matches += 1
                if result.predicted_type == classification_type:
                    correct_matches += 1
        
        if pattern_matches == 0:
            return 0.0
        
        return correct_matches / pattern_matches
    
    def get_rule_count(self) -> int:
        """Get the number of active heuristic rules"""
        return len(self.rules)
    
    def get_efficiency_stats(self) -> Dict[str, any]:
        """Get efficiency statistics for heuristic rules"""
        total_usage = sum(rule.usage_count for rule in self.rules.values())
        
        if not self.rules:
            return {"total_rules": 0, "total_usage": 0}
        
        most_used = max(self.rules.values(), key=lambda r: r.usage_count)
        avg_accuracy = sum(rule.accuracy_rate for rule in self.rules.values()) / len(self.rules)
        
        return {
            "total_rules": len(self.rules),
            "total_usage": total_usage,
            "most_used_rule": {
                "pattern": most_used.pattern,
                "usage_count": most_used.usage_count,
                "accuracy": most_used.accuracy_rate
            },
            "average_accuracy": avg_accuracy,
            "classifications_processed": len(self.classification_history)
        }
    
    def is_healthy(self) -> bool:
        """Check if the heuristic engine is healthy"""
        return len(self.rules) > 0