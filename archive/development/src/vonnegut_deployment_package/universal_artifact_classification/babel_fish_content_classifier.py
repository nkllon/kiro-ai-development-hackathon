"""
Babel Fish Content Classifier - Adaptive replacement for ContentClassifier.

This class provides a drop-in replacement for the existing ContentClassifier
using the Adaptive Babel Fish for superior accuracy and learning capabilities.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.repository_discovery.core.content_classifier import (
    ContentType, 
    ClassificationResult as OriginalClassificationResult,
    ClassificationBatch
)
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)

from .adaptive_babel_fish import AdaptiveBabelFish
from .models import ModelConfig


logger = logging.getLogger(__name__)


class BabelFishContentClassifier(ReflectiveModule):
    """
    Babel Fish Content Classifier - Drop-in replacement for ContentClassifier.
    
    Uses the Adaptive Babel Fish for superior classification accuracy with
    learning and adaptation capabilities while maintaining the same interface.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "BabelFishContentClassifier"
        self._config = config or {}
        self._logger = logging.getLogger(f"universal_artifact_classification.{self.__class__.__name__}")
        
        # Initialize Babel Fish with configuration
        babel_fish_config = ModelConfig(
            enable_gpu=self._config.get("enable_gpu", False),
            confidence_threshold=self._config.get("confidence_threshold", 0.85),
            heuristic_threshold=self._config.get("heuristic_threshold", 0.95)
        )
        
        self.babel_fish = AdaptiveBabelFish(babel_fish_config)
        
        # Performance tracking
        self._classification_count = 0
        self._total_processing_time = 0.0
        
        # Type mapping from Babel Fish to ContentType
        self._type_mapping = {
            "source_code": ContentType.SOURCE_CODE,
            "configuration": ContentType.CONFIGURATION,
            "documentation": ContentType.DOCUMENTATION,
            "build_script": ContentType.SCRIPT,
            "test_file": ContentType.TEST,
            "data_file": ContentType.DATA,
            "binary": ContentType.DATA,
            "unknown": ContentType.UNKNOWN
        }
        
        self._logger.info("BabelFishContentClassifier initialized with Adaptive Babel Fish")
    
    def classify_file(self, file_path: Path) -> OriginalClassificationResult:
        """
        Classify a single file using the Adaptive Babel Fish.
        
        Maintains compatibility with the original ContentClassifier interface.
        """
        start_time = datetime.now()
        
        try:
            # Use Babel Fish to understand the artifact
            understanding = self.babel_fish.understand_artifact(file_path)
            
            # Map Babel Fish type to ContentType
            primary_type = self._type_mapping.get(understanding.primary_type, ContentType.UNKNOWN)
            
            # Generate alternative types based on confidence
            alternative_types = self._generate_alternatives(understanding, primary_type)
            
            # Create classification reasons from Babel Fish explanation
            classification_reasons = [
                understanding.explanation,
                f"Confidence: {understanding.confidence:.2f}",
                f"Rules used: {len(understanding.heuristic_rules_used)}"
            ]
            
            if understanding.anomaly_indicators:
                classification_reasons.append(f"Anomalies: {', '.join(understanding.anomaly_indicators)}")
            
            # Create metadata from Babel Fish features
            metadata = {
                "babel_fish_confidence": understanding.confidence,
                "semantic_features": understanding.semantic_features,
                "heuristic_rules_used": understanding.heuristic_rules_used,
                "anomaly_indicators": understanding.anomaly_indicators,
                "learning_opportunities": understanding.learning_opportunities,
                "babel_fish_type": understanding.primary_type
            }
            
            # Update performance tracking
            processing_time = (datetime.now() - start_time).total_seconds()
            self._classification_count += 1
            self._total_processing_time += processing_time
            
            return OriginalClassificationResult(
                file_path=file_path,
                primary_type=primary_type,
                confidence=understanding.confidence,
                alternative_types=alternative_types,
                classification_reasons=classification_reasons,
                metadata=metadata
            )
            
        except Exception as e:
            self._logger.error(f"Error classifying {file_path}: {e}")
            
            # Fallback classification
            return OriginalClassificationResult(
                file_path=file_path,
                primary_type=ContentType.UNKNOWN,
                confidence=0.1,
                alternative_types=[],
                classification_reasons=[f"Classification failed: {str(e)}"],
                metadata={"error": str(e)}
            )
    
    def classify_batch(self, file_paths: List[Path], batch_id: str = None) -> ClassificationBatch:
        """
        Classify multiple files in batch using the Adaptive Babel Fish.
        
        Maintains compatibility with the original ContentClassifier interface.
        """
        if batch_id is None:
            batch_id = f"babel_fish_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_time = datetime.now()
        results = []
        
        for file_path in file_paths:
            result = self.classify_file(file_path)
            results.append(result)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate batch metrics
        confidences = [r.confidence for r in results]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Get Babel Fish efficiency metrics
        babel_fish_metrics = self.babel_fish.get_efficiency_metrics()
        
        accuracy_metrics = {
            "average_confidence": average_confidence,
            "heuristic_efficiency": babel_fish_metrics.get("heuristic_efficiency_percent", 0.0),
            "total_classifications": babel_fish_metrics.get("total_classifications", 0),
            "learning_events": babel_fish_metrics.get("learning_events", 0)
        }
        
        return ClassificationBatch(
            batch_id=batch_id,
            results=results,
            total_files=len(file_paths),
            processing_time=processing_time,
            average_confidence=average_confidence,
            accuracy_metrics=accuracy_metrics
        )
    
    def _generate_alternatives(self, understanding, primary_type: ContentType) -> List[Tuple[ContentType, float]]:
        """Generate alternative classifications based on Babel Fish understanding"""
        alternatives = []
        
        # If confidence is low, suggest other possibilities
        if understanding.confidence < 0.8:
            # Add some reasonable alternatives based on the primary type
            if primary_type == ContentType.SOURCE_CODE:
                alternatives.append((ContentType.SCRIPT, understanding.confidence * 0.8))
                alternatives.append((ContentType.TEST, understanding.confidence * 0.6))
            elif primary_type == ContentType.DOCUMENTATION:
                alternatives.append((ContentType.SPECIFICATION, understanding.confidence * 0.7))
            elif primary_type == ContentType.CONFIGURATION:
                alternatives.append((ContentType.DATA, understanding.confidence * 0.6))
        
        return alternatives
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics including Babel Fish metrics"""
        babel_fish_metrics = self.babel_fish.get_efficiency_metrics()
        
        return {
            "total_classifications": self._classification_count,
            "total_processing_time": self._total_processing_time,
            "average_processing_time": (
                self._total_processing_time / self._classification_count 
                if self._classification_count > 0 else 0.0
            ),
            "babel_fish_metrics": babel_fish_metrics,
            "learning_stats": self.babel_fish.learning_engine.get_learning_stats(),
            "heuristic_stats": self.babel_fish.heuristic_engine.get_efficiency_stats()
        }
    
    # ReflectiveModule implementation
    def get_health(self) -> ModuleHealth:
        """Get health status of the Babel Fish classifier"""
        babel_fish_health = self.babel_fish.get_health_status()
        
        status = ModuleStatus.HEALTHY if babel_fish_health["overall_status"] == "healthy" else ModuleStatus.DEGRADED
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            last_check=datetime.now(),
            metrics={
                "classification_count": self._classification_count,
                "babel_fish_health": babel_fish_health,
                "average_processing_time": (
                    self._total_processing_time / self._classification_count 
                    if self._classification_count > 0 else 0.0
                )
            }
        )
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get capabilities of the Babel Fish classifier"""
        babel_fish_capabilities = self.babel_fish.get_capabilities()
        
        return [
            ModuleCapability(
                name="file_classification",
                description="Classify individual files using Adaptive Babel Fish",
                enabled=True
            ),
            ModuleCapability(
                name="batch_classification", 
                description="Classify multiple files in batch",
                enabled=True
            ),
            ModuleCapability(
                name="adaptive_learning",
                description="Learn and adapt classification patterns over time",
                enabled=babel_fish_capabilities.get("continuous_learning", False)
            ),
            ModuleCapability(
                name="anomaly_detection",
                description="Detect classification anomalies for learning",
                enabled=babel_fish_capabilities.get("anomaly_detection", False)
            ),
            ModuleCapability(
                name="heuristic_optimization",
                description="Generate efficient heuristic rules for fast classification",
                enabled=babel_fish_capabilities.get("heuristic_generation", False)
            )
        ]
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Handle graceful degradation when Babel Fish components fail"""
        babel_fish_degradation = self.babel_fish.graceful_degradation()
        
        return GracefulDegradationResult(
            success=True,
            degradation_level=babel_fish_degradation["degradation_level"],
            fallback_capabilities=["basic_extension_classification"],
            performance_impact=f"Degradation level: {babel_fish_degradation['degradation_level']}/4",
            recovery_actions=babel_fish_degradation["actions_taken"]
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status"""
        babel_fish_health = self.babel_fish.get_health_status()
        
        return {
            "module_id": self.module_id,
            "status": babel_fish_health["overall_status"],
            "classification_count": self._classification_count,
            "average_processing_time": (
                self._total_processing_time / self._classification_count 
                if self._classification_count > 0 else 0.0
            ),
            "babel_fish_components": babel_fish_health["components"],
            "babel_fish_metrics": babel_fish_health["metrics"]
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        babel_fish_info = self.babel_fish.get_module_info()
        
        return {
            "name": "BabelFishContentClassifier",
            "version": "1.0.0",
            "description": "Adaptive content classifier using Babel Fish technology",
            "type": "content_classifier",
            "babel_fish_info": babel_fish_info,
            "interface_compatibility": "ContentClassifier",
            "enhanced_features": [
                "adaptive_learning",
                "anomaly_detection", 
                "heuristic_optimization",
                "multi_model_support"
            ]
        }