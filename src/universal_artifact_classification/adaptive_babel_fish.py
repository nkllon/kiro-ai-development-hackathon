"""
The Adaptive Babel Fish - Learning, adaptive artifact classification system.

This system learns, adapts, creates heuristic rules for efficiency, detects anomalies,
and conforms to the universe as it discovers it.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.beast_mode.core.reflective_module import ReflectiveModule
from .models import (
    ArtifactUnderstanding, 
    ClassificationResult, 
    LearningEvent,
    ModelConfig
)
from .transfer_learning_engine import TransferLearningEngine
from .heuristic_engine import HeuristicGenerationEngine
from .anomaly_detector import AnomalyDetectionSystem
from .continuous_learning import ContinuousLearningEngine


logger = logging.getLogger(__name__)


class AdaptiveBabelFish(ReflectiveModule):
    """
    The learning, adaptive artifact classifier that serves as our universal Babel Fish.
    
    Unlike static classification systems, this Babel Fish:
    - Learns and adapts with each classification
    - Creates heuristic rules for efficiency
    - Detects anomalies for learning opportunities
    - Conforms to the universe as it discovers it
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        super().__init__()
        self.config = config or ModelConfig()
        
        # Initialize core engines
        self.transfer_learning_engine = TransferLearningEngine(self.config)
        self.heuristic_engine = HeuristicGenerationEngine()
        self.anomaly_detector = AnomalyDetectionSystem(self.config.confidence_threshold)
        self.learning_engine = ContinuousLearningEngine()
        
        # Performance tracking
        self.classification_count = 0
        self.heuristic_hits = 0
        self.learning_events: List[LearningEvent] = []
        
        logger.info("Adaptive Babel Fish initialized - ready to learn and adapt")
    
    def understand_artifact(self, artifact_path: Path) -> ArtifactUnderstanding:
        """
        Understand artifact using adaptive intelligence.
        
        This is the core method that embodies the Babel Fish philosophy:
        1. Try efficient heuristics first
        2. Fall back to deep learning for complex cases
        3. Detect anomalies and learn from them
        4. Generate new heuristics for efficiency
        """
        start_time = time.time()
        self.classification_count += 1
        
        try:
            # Phase 1: Try efficient heuristics first
            quick_result = self.heuristic_engine.quick_classify(artifact_path)
            if quick_result and quick_result.confidence > self.config.heuristic_threshold:
                self.heuristic_hits += 1
                processing_time = (time.time() - start_time) * 1000
                
                return ArtifactUnderstanding(
                    primary_type=quick_result.predicted_type,
                    confidence=quick_result.confidence,
                    semantic_features={},
                    learned_patterns=[],
                    heuristic_rules_used=quick_result.features_used,
                    anomaly_indicators=[],
                    learning_opportunities=[],
                    explanation=f"Fast heuristic classification ({processing_time:.1f}ms)"
                )
            
            # Phase 2: Deep learning for complex cases
            deep_result = self.transfer_learning_engine.classify_artifact(artifact_path)
            processing_time = (time.time() - start_time) * 1000
            
            # Phase 3: Detect anomalies and learn
            anomaly_indicators = []
            learning_opportunities = []
            
            if self.anomaly_detector.is_anomaly(deep_result):
                anomaly_indicators = self.anomaly_detector.get_anomaly_indicators(deep_result)
                learning_event = self.learning_engine.learn_from_anomaly(artifact_path, deep_result)
                if learning_event:
                    self.learning_events.append(learning_event)
                    learning_opportunities = learning_event.patterns_discovered
            
            # Phase 4: Generate new heuristics for efficiency
            self.heuristic_engine.update_rules(artifact_path, deep_result)
            
            return ArtifactUnderstanding(
                primary_type=deep_result.predicted_type,
                confidence=deep_result.confidence,
                semantic_features=self.transfer_learning_engine.get_semantic_features(artifact_path),
                learned_patterns=learning_opportunities,
                heuristic_rules_used=[],
                anomaly_indicators=anomaly_indicators,
                learning_opportunities=learning_opportunities,
                explanation=f"Deep learning classification ({processing_time:.1f}ms)"
            )
            
        except Exception as e:
            logger.error(f"Error understanding artifact {artifact_path}: {e}")
            # Fallback to basic classification
            return ArtifactUnderstanding(
                primary_type="unknown",
                confidence=0.0,
                semantic_features={},
                learned_patterns=[],
                heuristic_rules_used=[],
                anomaly_indicators=["classification_error"],
                learning_opportunities=["error_recovery"],
                explanation=f"Classification failed: {str(e)}"
            )
    
    def get_efficiency_metrics(self) -> Dict[str, Any]:
        """Get efficiency metrics for the Babel Fish"""
        if self.classification_count == 0:
            return {"error": "No classifications performed yet"}
        
        heuristic_efficiency = (self.heuristic_hits / self.classification_count) * 100
        
        return {
            "total_classifications": self.classification_count,
            "heuristic_hits": self.heuristic_hits,
            "heuristic_efficiency_percent": heuristic_efficiency,
            "learning_events": len(self.learning_events),
            "active_heuristic_rules": self.heuristic_engine.get_rule_count(),
            "anomalies_detected": len([e for e in self.learning_events if e.anomalies_detected])
        }
    
    def adapt_to_domain(self, training_examples: List[Any]) -> Dict[str, Any]:
        """Adapt the Babel Fish to a new domain using training examples"""
        logger.info(f"Adapting Babel Fish to new domain with {len(training_examples)} examples")
        
        # Use transfer learning engine for domain adaptation
        adaptation_result = self.transfer_learning_engine.adapt_to_domain(training_examples)
        
        # Update learning engine with new domain patterns
        self.learning_engine.update_domain_patterns(training_examples)
        
        return {
            "adaptation_complete": True,
            "examples_processed": len(training_examples),
            "new_patterns_learned": adaptation_result.get("patterns_learned", 0),
            "accuracy_improvement": adaptation_result.get("accuracy_delta", 0.0)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the Adaptive Babel Fish"""
        base_health = super().health_check()
        
        babel_fish_health = {
            "transfer_learning_engine": self.transfer_learning_engine.is_healthy(),
            "heuristic_engine": self.heuristic_engine.is_healthy(),
            "anomaly_detector": self.anomaly_detector.is_healthy(),
            "learning_engine": self.learning_engine.is_healthy(),
            "efficiency_metrics": self.get_efficiency_metrics()
        }
        
        return {**base_health, "babel_fish": babel_fish_health}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of the Adaptive Babel Fish"""
        return {
            "artifact_classification": True,
            "transfer_learning": True,
            "heuristic_generation": True,
            "anomaly_detection": True,
            "continuous_learning": True,
            "domain_adaptation": True,
            "supported_models": ["microsoft/codebert-base", "microsoft/graphcodebert-base"],
            "supported_artifact_types": self.transfer_learning_engine.artifact_categories
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status"""
        return {
            "overall_status": "healthy" if all([
                self.transfer_learning_engine.is_healthy(),
                self.heuristic_engine.is_healthy(),
                self.anomaly_detector.is_healthy(),
                self.learning_engine.is_healthy()
            ]) else "degraded",
            "components": {
                "transfer_learning": "healthy" if self.transfer_learning_engine.is_healthy() else "unhealthy",
                "heuristics": "healthy" if self.heuristic_engine.is_healthy() else "unhealthy", 
                "anomaly_detection": "healthy" if self.anomaly_detector.is_healthy() else "unhealthy",
                "learning": "healthy" if self.learning_engine.is_healthy() else "unhealthy"
            },
            "metrics": self.get_efficiency_metrics()
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": "AdaptiveBabelFish",
            "version": "1.0.0",
            "description": "Learning, adaptive artifact classification system",
            "type": "universal_classifier",
            "base_model": self.config.base_model_name,
            "confidence_threshold": self.config.confidence_threshold,
            "heuristic_threshold": self.config.heuristic_threshold
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Handle graceful degradation when components fail"""
        degradation_actions = []
        
        # Check each component and plan degradation
        if not self.transfer_learning_engine.is_healthy():
            degradation_actions.append("fallback_to_heuristics_only")
        
        if not self.heuristic_engine.is_healthy():
            degradation_actions.append("disable_fast_path_optimization")
        
        if not self.anomaly_detector.is_healthy():
            degradation_actions.append("disable_anomaly_learning")
        
        if not self.learning_engine.is_healthy():
            degradation_actions.append("disable_continuous_learning")
        
        return {
            "degradation_level": len(degradation_actions),
            "actions_taken": degradation_actions,
            "fallback_available": True,  # Always have basic classification
            "core_functionality": "maintained"
        }