"""
Anomaly Detection System - Identifies exceptions and learning opportunities.

This system detects when classifications are anomalous, indicating potential
learning opportunities or edge cases that need attention.
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta

from .models import ClassificationResult


logger = logging.getLogger(__name__)


class AnomalyDetectionSystem:
    """
    Detects anomalies in classification results to identify learning opportunities.
    
    Anomalies include:
    - Low confidence classifications
    - Pattern deviations from known types
    - Unusual feature combinations
    - Domain drift indicators
    """
    
    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold
        self.classification_history = deque(maxlen=1000)  # Keep last 1000 classifications
        self.type_patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.confidence_history: Dict[str, List[float]] = defaultdict(list)
        
        logger.info(f"Anomaly Detection System initialized with confidence threshold {confidence_threshold}")
    
    def is_anomaly(self, classification_result: ClassificationResult) -> bool:
        """
        Determine if a classification result is anomalous.
        
        Returns True if the result should be flagged for learning or review.
        """
        anomaly_indicators = []
        
        # Check confidence-based anomalies
        if self._is_low_confidence_anomaly(classification_result):
            anomaly_indicators.append("low_confidence")
        
        # Check pattern deviation anomalies
        if self._is_pattern_deviation_anomaly(classification_result):
            anomaly_indicators.append("pattern_deviation")
        
        # Check feature combination anomalies
        if self._is_feature_combination_anomaly(classification_result):
            anomaly_indicators.append("unusual_features")
        
        # Check domain drift anomalies
        if self._is_domain_drift_anomaly(classification_result):
            anomaly_indicators.append("domain_drift")
        
        # Store classification in history
        self.classification_history.append(classification_result)
        self._update_patterns(classification_result)
        
        return len(anomaly_indicators) > 0
    
    def get_anomaly_indicators(self, classification_result: ClassificationResult) -> List[str]:
        """Get specific anomaly indicators for a classification result"""
        indicators = []
        
        if self._is_low_confidence_anomaly(classification_result):
            indicators.append("low_confidence")
        
        if self._is_pattern_deviation_anomaly(classification_result):
            indicators.append("pattern_deviation")
        
        if self._is_feature_combination_anomaly(classification_result):
            indicators.append("unusual_features")
        
        if self._is_domain_drift_anomaly(classification_result):
            indicators.append("domain_drift")
        
        return indicators
    
    def _is_low_confidence_anomaly(self, result: ClassificationResult) -> bool:
        """Check if confidence is anomalously low"""
        return result.confidence < self.confidence_threshold
    
    def _is_pattern_deviation_anomaly(self, result: ClassificationResult) -> bool:
        """Check if the result deviates from known patterns for this type"""
        predicted_type = result.predicted_type
        
        # If we don't have enough history for this type, not an anomaly
        if predicted_type not in self.type_patterns or len(self.type_patterns[predicted_type]) < 5:
            return False
        
        # Check if features used are unusual for this type
        common_features = set(self.type_patterns[predicted_type].keys())
        result_features = set(result.features_used)
        
        # If less than 50% overlap with common features, it's a deviation
        if len(common_features) > 0:
            overlap = len(common_features.intersection(result_features))
            overlap_ratio = overlap / len(common_features)
            return overlap_ratio < 0.5
        
        return False
    
    def _is_feature_combination_anomaly(self, result: ClassificationResult) -> bool:
        """Check if the combination of features is unusual"""
        # For now, flag if using fallback or extension-only classification
        return result.model_used in ["fallback", "extension_fallback"]
    
    def _is_domain_drift_anomaly(self, result: ClassificationResult) -> bool:
        """Check if there's evidence of domain drift"""
        predicted_type = result.predicted_type
        
        # Track confidence trends for this type
        self.confidence_history[predicted_type].append(result.confidence)
        
        # Keep only recent history (last 50 classifications)
        if len(self.confidence_history[predicted_type]) > 50:
            self.confidence_history[predicted_type] = self.confidence_history[predicted_type][-50:]
        
        # Check if confidence is trending downward
        if len(self.confidence_history[predicted_type]) >= 10:
            recent_avg = sum(self.confidence_history[predicted_type][-10:]) / 10
            older_avg = sum(self.confidence_history[predicted_type][-20:-10]) / 10 if len(self.confidence_history[predicted_type]) >= 20 else recent_avg
            
            # If recent confidence is significantly lower, might be domain drift
            return recent_avg < older_avg - 0.1
        
        return False
    
    def _update_patterns(self, result: ClassificationResult):
        """Update pattern tracking for anomaly detection"""
        predicted_type = result.predicted_type
        
        # Track feature usage for this type
        for feature in result.features_used:
            self.type_patterns[predicted_type][feature] += 1
    
    def get_anomaly_stats(self) -> Dict[str, Any]:
        """Get statistics about detected anomalies"""
        if not self.classification_history:
            return {"total_classifications": 0, "anomalies_detected": 0}
        
        total_classifications = len(self.classification_history)
        anomaly_count = 0
        anomaly_types = defaultdict(int)
        
        for result in self.classification_history:
            indicators = self.get_anomaly_indicators(result)
            if indicators:
                anomaly_count += 1
                for indicator in indicators:
                    anomaly_types[indicator] += 1
        
        anomaly_rate = (anomaly_count / total_classifications) * 100 if total_classifications > 0 else 0
        
        return {
            "total_classifications": total_classifications,
            "anomalies_detected": anomaly_count,
            "anomaly_rate_percent": anomaly_rate,
            "anomaly_types": dict(anomaly_types),
            "confidence_threshold": self.confidence_threshold
        }
    
    def get_learning_opportunities(self) -> List[Dict[str, Any]]:
        """Get specific learning opportunities from detected anomalies"""
        opportunities = []
        
        # Find low confidence classifications that could benefit from training
        for result in self.classification_history:
            if result.confidence < self.confidence_threshold:
                opportunities.append({
                    "type": "low_confidence_training",
                    "artifact_path": result.artifact_path,
                    "predicted_type": result.predicted_type,
                    "confidence": result.confidence,
                    "priority": 1.0 - result.confidence  # Lower confidence = higher priority
                })
        
        # Sort by priority (highest first)
        opportunities.sort(key=lambda x: x["priority"], reverse=True)
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def is_healthy(self) -> bool:
        """Check if the anomaly detection system is healthy"""
        return True  # Simple health check - could be enhanced