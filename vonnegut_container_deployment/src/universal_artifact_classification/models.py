"""
Data models for the Adaptive Babel Fish classification system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional


@dataclass
class ArtifactUnderstanding:
    """Complete understanding of an artifact by the Babel Fish"""
    primary_type: str
    confidence: float
    semantic_features: Dict[str, float]
    learned_patterns: List[str]
    heuristic_rules_used: List[str]
    anomaly_indicators: List[str]
    learning_opportunities: List[str]
    explanation: str


@dataclass
class ClassificationResult:
    """Result of artifact classification"""
    artifact_path: str
    predicted_type: str
    confidence: float
    alternative_types: List[Tuple[str, float]]
    features_used: List[str]
    requires_review: bool
    processing_time_ms: float
    model_used: str  # "heuristic" or "deep_learning"


@dataclass
class LearningEvent:
    """Record of learning from classification experience"""
    artifact_path: str
    classification_result: ClassificationResult
    patterns_discovered: List[str]
    heuristics_generated: List[str]
    anomalies_detected: List[str]
    learning_value: float
    timestamp: datetime


@dataclass
class HeuristicRule:
    """Efficient rule generated from learned patterns"""
    rule_id: str
    pattern: str
    classification: str
    confidence_threshold: float
    accuracy_rate: float
    usage_count: int
    created_at: datetime
    last_validated: datetime


@dataclass
class ModelConfig:
    """Configuration for the Adaptive Babel Fish"""
    base_model_name: str = "microsoft/codebert-base"
    confidence_threshold: float = 0.85
    heuristic_threshold: float = 0.95
    max_sequence_length: int = 512
    batch_size: int = 16
    learning_rate: float = 2e-5
    cache_size: int = 1000
    enable_gpu: bool = True