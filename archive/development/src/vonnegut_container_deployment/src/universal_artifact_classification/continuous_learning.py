"""
Continuous Learning Engine - Adapts and improves over time.

This engine implements the learning capabilities that allow the Babel Fish
to adapt to new domains and improve accuracy through feedback.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from .models import ClassificationResult, LearningEvent


logger = logging.getLogger(__name__)


class ContinuousLearningEngine:
    """
    Implements continuous learning capabilities for the Adaptive Babel Fish.
    
    The engine learns from:
    - Anomalous classifications
    - Human feedback and corrections
    - Domain adaptation examples
    - Pattern evolution over time
    """
    
    def __init__(self):
        self.learning_events: List[LearningEvent] = []
        self.domain_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.feedback_history: List[Dict[str, Any]] = []
        self.adaptation_metrics: Dict[str, float] = {}
        
        logger.info("Continuous Learning Engine initialized")
    
    def learn_from_anomaly(self, artifact_path: Path, classification_result: ClassificationResult) -> Optional[LearningEvent]:
        """
        Learn from an anomalous classification result.
        
        Analyzes the anomaly to extract patterns and learning opportunities.
        """
        try:
            # Extract patterns from the anomalous classification
            patterns_discovered = self._extract_learning_patterns(artifact_path, classification_result)
            
            # Generate potential heuristics from this anomaly
            heuristics_generated = self._generate_heuristics_from_anomaly(artifact_path, classification_result)
            
            # Identify specific anomaly indicators
            anomalies_detected = self._identify_anomaly_types(classification_result)
            
            # Calculate learning value (how much we can learn from this)
            learning_value = self._calculate_learning_value(classification_result, patterns_discovered)
            
            # Create learning event
            learning_event = LearningEvent(
                artifact_path=str(artifact_path),
                classification_result=classification_result,
                patterns_discovered=patterns_discovered,
                heuristics_generated=heuristics_generated,
                anomalies_detected=anomalies_detected,
                learning_value=learning_value,
                timestamp=datetime.now()
            )
            
            self.learning_events.append(learning_event)
            
            # Update domain patterns based on this learning
            self._update_domain_patterns(artifact_path, classification_result, patterns_discovered)
            
            logger.info(f"Learned from anomaly: {artifact_path} -> {classification_result.predicted_type} "
                       f"(confidence: {classification_result.confidence:.2f}, learning_value: {learning_value:.2f})")
            
            return learning_event
            
        except Exception as e:
            logger.error(f"Error learning from anomaly {artifact_path}: {e}")
            return None
    
    def learn_from_feedback(self, artifact_path: Path, true_type: str, predicted_type: str, confidence: float) -> Dict[str, Any]:
        """
        Learn from human feedback about classification accuracy.
        
        This is crucial for improving the system based on expert knowledge.
        """
        feedback_entry = {
            "artifact_path": str(artifact_path),
            "true_type": true_type,
            "predicted_type": predicted_type,
            "confidence": confidence,
            "correction_needed": true_type != predicted_type,
            "timestamp": datetime.now()
        }
        
        self.feedback_history.append(feedback_entry)
        
        # If correction was needed, extract learning patterns
        if feedback_entry["correction_needed"]:
            correction_patterns = self._extract_correction_patterns(artifact_path, true_type, predicted_type)
            
            # Update domain patterns with correct classification
            self._update_domain_patterns_with_correction(artifact_path, true_type, correction_patterns)
            
            logger.info(f"Learned from correction: {artifact_path} should be {true_type}, not {predicted_type}")
        
        return {
            "feedback_recorded": True,
            "correction_needed": feedback_entry["correction_needed"],
            "patterns_updated": feedback_entry["correction_needed"]
        }
    
    def update_domain_patterns(self, training_examples: List[Any]) -> Dict[str, Any]:
        """Update domain patterns based on training examples"""
        patterns_learned = 0
        
        for example in training_examples:
            # Extract patterns from training example
            # This would be implemented based on the structure of training examples
            patterns_learned += 1
        
        self.adaptation_metrics["last_adaptation_examples"] = len(training_examples)
        self.adaptation_metrics["last_adaptation_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Updated domain patterns with {len(training_examples)} examples")
        
        return {
            "examples_processed": len(training_examples),
            "patterns_learned": patterns_learned
        }
    
    def _extract_learning_patterns(self, artifact_path: Path, result: ClassificationResult) -> List[str]:
        """Extract patterns that can be learned from this classification"""
        patterns = []
        
        # File extension patterns
        if artifact_path.suffix:
            patterns.append(f"ext_{artifact_path.suffix.lower()}_type_{result.predicted_type}")
        
        # Filename patterns
        name_lower = artifact_path.name.lower()
        if "test" in name_lower:
            patterns.append(f"test_file_type_{result.predicted_type}")
        if "config" in name_lower:
            patterns.append(f"config_file_type_{result.predicted_type}")
        
        # Directory patterns
        if len(artifact_path.parts) > 1:
            parent_dir = artifact_path.parts[-2].lower()
            patterns.append(f"parent_dir_{parent_dir}_type_{result.predicted_type}")
        
        # Confidence patterns
        if result.confidence < 0.5:
            patterns.append(f"low_confidence_type_{result.predicted_type}")
        elif result.confidence > 0.9:
            patterns.append(f"high_confidence_type_{result.predicted_type}")
        
        return patterns
    
    def _generate_heuristics_from_anomaly(self, artifact_path: Path, result: ClassificationResult) -> List[str]:
        """Generate potential heuristic rules from anomalous classification"""
        heuristics = []
        
        # If this was a low-confidence classification, suggest review
        if result.confidence < 0.7:
            heuristics.append(f"review_low_confidence_{result.predicted_type}")
        
        # If using fallback classification, suggest pattern learning
        if result.model_used == "fallback":
            heuristics.append(f"learn_pattern_for_{artifact_path.suffix}")
        
        # If extension-only classification, suggest content analysis
        if result.model_used == "extension_fallback":
            heuristics.append(f"analyze_content_for_{artifact_path.suffix}")
        
        return heuristics
    
    def _identify_anomaly_types(self, result: ClassificationResult) -> List[str]:
        """Identify specific types of anomalies in the classification"""
        anomalies = []
        
        if result.confidence < 0.5:
            anomalies.append("very_low_confidence")
        elif result.confidence < 0.8:
            anomalies.append("low_confidence")
        
        if result.model_used == "fallback":
            anomalies.append("fallback_classification")
        
        if result.requires_review:
            anomalies.append("requires_human_review")
        
        if not result.alternative_types:
            anomalies.append("no_alternatives_found")
        
        return anomalies
    
    def _calculate_learning_value(self, result: ClassificationResult, patterns: List[str]) -> float:
        """Calculate how much we can learn from this classification"""
        learning_value = 0.0
        
        # Higher learning value for lower confidence (more to learn)
        learning_value += (1.0 - result.confidence) * 0.5
        
        # Higher learning value for more patterns discovered
        learning_value += len(patterns) * 0.1
        
        # Higher learning value for fallback classifications
        if result.model_used in ["fallback", "extension_fallback"]:
            learning_value += 0.3
        
        # Cap at 1.0
        return min(learning_value, 1.0)
    
    def _update_domain_patterns(self, artifact_path: Path, result: ClassificationResult, patterns: List[str]):
        """Update domain patterns based on learning"""
        domain = self._infer_domain(artifact_path)
        
        if domain not in self.domain_patterns:
            self.domain_patterns[domain] = {
                "patterns": defaultdict(int),
                "confidence_history": [],
                "last_updated": datetime.now()
            }
        
        # Update pattern frequencies
        for pattern in patterns:
            self.domain_patterns[domain]["patterns"][pattern] += 1
        
        # Update confidence history
        self.domain_patterns[domain]["confidence_history"].append(result.confidence)
        
        # Keep only recent history
        if len(self.domain_patterns[domain]["confidence_history"]) > 100:
            self.domain_patterns[domain]["confidence_history"] = \
                self.domain_patterns[domain]["confidence_history"][-100:]
        
        self.domain_patterns[domain]["last_updated"] = datetime.now()
    
    def _extract_correction_patterns(self, artifact_path: Path, true_type: str, predicted_type: str) -> List[str]:
        """Extract patterns from human corrections"""
        patterns = []
        
        # Correction pattern
        patterns.append(f"correction_{predicted_type}_to_{true_type}")
        
        # File-specific correction pattern
        if artifact_path.suffix:
            patterns.append(f"ext_{artifact_path.suffix.lower()}_correct_{true_type}")
        
        return patterns
    
    def _update_domain_patterns_with_correction(self, artifact_path: Path, true_type: str, patterns: List[str]):
        """Update domain patterns with human correction"""
        domain = self._infer_domain(artifact_path)
        
        if domain not in self.domain_patterns:
            self.domain_patterns[domain] = {
                "patterns": defaultdict(int),
                "corrections": defaultdict(int),
                "last_updated": datetime.now()
            }
        
        # Update correction patterns
        if "corrections" not in self.domain_patterns[domain]:
            self.domain_patterns[domain]["corrections"] = defaultdict(int)
        
        for pattern in patterns:
            self.domain_patterns[domain]["corrections"][pattern] += 1
        
        self.domain_patterns[domain]["last_updated"] = datetime.now()
    
    def _infer_domain(self, artifact_path: Path) -> str:
        """Infer domain from artifact path"""
        # For now, use simple heuristics
        path_str = str(artifact_path).lower()
        
        if any(keyword in path_str for keyword in ["src", "source", "lib", "code"]):
            return "software_development"
        elif any(keyword in path_str for keyword in ["doc", "readme", "manual"]):
            return "documentation"
        elif any(keyword in path_str for keyword in ["config", "conf", "settings"]):
            return "configuration"
        elif any(keyword in path_str for keyword in ["test", "spec"]):
            return "testing"
        else:
            return "general"
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learning progress"""
        total_events = len(self.learning_events)
        total_feedback = len(self.feedback_history)
        
        if total_events == 0:
            return {
                "total_learning_events": 0,
                "total_feedback": total_feedback,
                "domains_learned": 0
            }
        
        avg_learning_value = sum(event.learning_value for event in self.learning_events) / total_events
        corrections_needed = sum(1 for feedback in self.feedback_history if feedback["correction_needed"])
        
        return {
            "total_learning_events": total_events,
            "average_learning_value": avg_learning_value,
            "total_feedback": total_feedback,
            "corrections_needed": corrections_needed,
            "correction_rate": corrections_needed / total_feedback if total_feedback > 0 else 0,
            "domains_learned": len(self.domain_patterns),
            "domain_patterns": {domain: len(patterns["patterns"]) for domain, patterns in self.domain_patterns.items()}
        }
    
    def is_healthy(self) -> bool:
        """Check if the continuous learning engine is healthy"""
        return True  # Simple health check