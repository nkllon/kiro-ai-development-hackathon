#!/usr/bin/env python3
"""
Confidence Scorer - Phase 5 Task 5.3 Component

Calculates confidence scores for validation results based on
multiple factors and provides systematic confidence assessment.
"""

import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ConfidenceLevel(Enum):
    """Confidence level categories."""
    VERY_HIGH = "very_high"    # 0.90 - 1.00
    HIGH = "high"              # 0.75 - 0.89
    MEDIUM = "medium"          # 0.50 - 0.74
    LOW = "low"                # 0.25 - 0.49
    VERY_LOW = "very_low"      # 0.00 - 0.24


@dataclass
class ConfidenceFactors:
    """Factors that contribute to confidence scoring."""
    data_freshness: float = 1.0      # How recent is the data (0-1)
    sample_size: float = 1.0         # Adequacy of sample size (0-1)
    consistency: float = 1.0         # Consistency across measurements (0-1)
    validation_coverage: float = 1.0  # Coverage of validation checks (0-1)
    automation_level: float = 1.0    # Level of automation (0-1)
    historical_accuracy: float = 1.0 # Historical accuracy of similar validations (0-1)
    cross_validation: float = 1.0    # Cross-validation with other sources (0-1)
    error_rate: float = 0.0          # Error rate (0-1, inverted for scoring)


@dataclass
class ConfidenceScore:
    """Represents a confidence score calculation."""
    score_id: str
    target: str  # What is being scored
    overall_score: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    factors: ConfidenceFactors
    timestamp: datetime
    calculation_method: str
    details: Dict[str, Any]
    recommendations: List[str] = None


@dataclass
class ConfidenceWeights:
    """Weights for different confidence factors."""
    data_freshness: float = 0.15
    sample_size: float = 0.20
    consistency: float = 0.20
    validation_coverage: float = 0.15
    automation_level: float = 0.10
    historical_accuracy: float = 0.10
    cross_validation: float = 0.05
    error_rate: float = 0.05


class ConfidenceScorer(ReflectiveModule):
    """
    Systematic confidence scoring for validation results.
    
    Calculates confidence scores based on multiple factors including
    data freshness, sample size, consistency, and validation coverage.
    """
    
    def __init__(self, default_weights: Optional[ConfidenceWeights] = None):
        super().__init__()
        self.weights = default_weights or ConfidenceWeights()
        self.confidence_scores: List[ConfidenceScore] = []
        self.historical_data: Dict[str, List[float]] = {}
        self.max_history_size = 5000
        
        # Confidence thresholds
        self.confidence_thresholds = {
            ConfidenceLevel.VERY_HIGH: 0.90,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.MEDIUM: 0.50,
            ConfidenceLevel.LOW: 0.25,
            ConfidenceLevel.VERY_LOW: 0.00
        }
        
        # Register capabilities
        self.register_capability('confidence_scoring', {
            'description': 'Systematic confidence scoring for validation results',
            'calculation_methods': ['weighted_average', 'bayesian', 'ensemble'],
            'confidence_levels': len(self.confidence_thresholds)
        })
    
    def calculate_confidence_score(self, target: str, factors: ConfidenceFactors,
                                 method: str = 'weighted_average',
                                 additional_data: Optional[Dict[str, Any]] = None) -> ConfidenceScore:
        """Calculate confidence score for a target using specified method."""
        score_id = f"{target}_{int(datetime.now().timestamp())}"
        
        try:
            if method == 'weighted_average':
                score, details = self._calculate_weighted_average(factors)
            elif method == 'bayesian':
                score, details = self._calculate_bayesian_score(target, factors, additional_data)
            elif method == 'ensemble':
                score, details = self._calculate_ensemble_score(target, factors, additional_data)
            else:
                raise ValueError(f"Unknown calculation method: {method}")
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(factors, score, confidence_level)
            
            # Create confidence score object
            confidence_score = ConfidenceScore(
                score_id=score_id,
                target=target,
                overall_score=score,
                confidence_level=confidence_level,
                factors=factors,
                timestamp=datetime.now(),
                calculation_method=method,
                details=details,
                recommendations=recommendations
            )
            
            # Store in history
            self.confidence_scores.append(confidence_score)
            
            # Update historical data
            if target not in self.historical_data:
                self.historical_data[target] = []
            self.historical_data[target].append(score)
            
            # Trim history if needed
            if len(self.confidence_scores) > self.max_history_size:
                self.confidence_scores = self.confidence_scores[-self.max_history_size:]
            
            if len(self.historical_data[target]) > 100:  # Keep last 100 scores per target
                self.historical_data[target] = self.historical_data[target][-100:]
            
            self.logger.debug(f"Calculated confidence score for {target}: {score:.3f} ({confidence_level.value})")
            
            return confidence_score
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence score for {target}: {e}")
            
            # Return low confidence score on error
            return ConfidenceScore(
                score_id=score_id,
                target=target,
                overall_score=0.1,
                confidence_level=ConfidenceLevel.VERY_LOW,
                factors=factors,
                timestamp=datetime.now(),
                calculation_method=method,
                details={'error': str(e)},
                recommendations=['Fix calculation error', 'Verify input data']
            )
    
    def _calculate_weighted_average(self, factors: ConfidenceFactors) -> Tuple[float, Dict[str, Any]]:
        """Calculate confidence score using weighted average method."""
        # Convert error rate to positive contribution (1 - error_rate)
        adjusted_error_rate = 1.0 - factors.error_rate
        
        # Calculate weighted sum
        weighted_sum = (
            factors.data_freshness * self.weights.data_freshness +
            factors.sample_size * self.weights.sample_size +
            factors.consistency * self.weights.consistency +
            factors.validation_coverage * self.weights.validation_coverage +
            factors.automation_level * self.weights.automation_level +
            factors.historical_accuracy * self.weights.historical_accuracy +
            factors.cross_validation * self.weights.cross_validation +
            adjusted_error_rate * self.weights.error_rate
        )
        
        # Normalize by sum of weights
        total_weight = sum([
            self.weights.data_freshness,
            self.weights.sample_size,
            self.weights.consistency,
            self.weights.validation_coverage,
            self.weights.automation_level,
            self.weights.historical_accuracy,
            self.weights.cross_validation,
            self.weights.error_rate
        ])
        
        score = weighted_sum / total_weight
        
        details = {
            'method': 'weighted_average',
            'weighted_sum': weighted_sum,
            'total_weight': total_weight,
            'factor_contributions': {
                'data_freshness': factors.data_freshness * self.weights.data_freshness,
                'sample_size': factors.sample_size * self.weights.sample_size,
                'consistency': factors.consistency * self.weights.consistency,
                'validation_coverage': factors.validation_coverage * self.weights.validation_coverage,
                'automation_level': factors.automation_level * self.weights.automation_level,
                'historical_accuracy': factors.historical_accuracy * self.weights.historical_accuracy,
                'cross_validation': factors.cross_validation * self.weights.cross_validation,
                'error_rate': adjusted_error_rate * self.weights.error_rate
            }
        }
        
        return max(0.0, min(1.0, score)), details
    
    def _calculate_bayesian_score(self, target: str, factors: ConfidenceFactors,
                                additional_data: Optional[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """Calculate confidence score using Bayesian approach."""
        # Start with prior probability based on historical data
        if target in self.historical_data and self.historical_data[target]:
            prior = statistics.mean(self.historical_data[target])
        else:
            prior = 0.5  # Neutral prior
        
        # Calculate likelihood based on current factors
        likelihood = self._calculate_weighted_average(factors)[0]
        
        # Simple Bayesian update (can be made more sophisticated)
        # P(confidence|evidence) ∝ P(evidence|confidence) * P(confidence)
        
        # Weight the prior based on amount of historical data
        historical_weight = min(len(self.historical_data.get(target, [])) / 10.0, 1.0)
        current_weight = 1.0 - historical_weight
        
        # Bayesian update
        posterior = (prior * historical_weight + likelihood * current_weight)
        
        details = {
            'method': 'bayesian',
            'prior': prior,
            'likelihood': likelihood,
            'posterior': posterior,
            'historical_weight': historical_weight,
            'current_weight': current_weight,
            'historical_samples': len(self.historical_data.get(target, []))
        }
        
        return max(0.0, min(1.0, posterior)), details
    
    def _calculate_ensemble_score(self, target: str, factors: ConfidenceFactors,
                                additional_data: Optional[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """Calculate confidence score using ensemble of methods."""
        # Calculate using different methods
        weighted_score, weighted_details = self._calculate_weighted_average(factors)
        bayesian_score, bayesian_details = self._calculate_bayesian_score(target, factors, additional_data)
        
        # Simple ensemble: average of methods
        ensemble_score = (weighted_score + bayesian_score) / 2.0
        
        # Could add more sophisticated ensemble methods here
        # e.g., weighted by historical performance of each method
        
        details = {
            'method': 'ensemble',
            'weighted_average_score': weighted_score,
            'bayesian_score': bayesian_score,
            'ensemble_score': ensemble_score,
            'method_details': {
                'weighted_average': weighted_details,
                'bayesian': bayesian_details
            }
        }
        
        return max(0.0, min(1.0, ensemble_score)), details
    
    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level category from score."""
        if score >= self.confidence_thresholds[ConfidenceLevel.VERY_HIGH]:
            return ConfidenceLevel.VERY_HIGH
        elif score >= self.confidence_thresholds[ConfidenceLevel.HIGH]:
            return ConfidenceLevel.HIGH
        elif score >= self.confidence_thresholds[ConfidenceLevel.MEDIUM]:
            return ConfidenceLevel.MEDIUM
        elif score >= self.confidence_thresholds[ConfidenceLevel.LOW]:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_recommendations(self, factors: ConfidenceFactors, score: float,
                                confidence_level: ConfidenceLevel) -> List[str]:
        """Generate recommendations to improve confidence score."""
        recommendations = []
        
        # Check each factor and suggest improvements
        if factors.data_freshness < 0.7:
            recommendations.append("Update data more frequently to improve freshness")
        
        if factors.sample_size < 0.6:
            recommendations.append("Increase sample size for more reliable results")
        
        if factors.consistency < 0.7:
            recommendations.append("Investigate inconsistencies in measurements")
        
        if factors.validation_coverage < 0.8:
            recommendations.append("Expand validation coverage to include more checks")
        
        if factors.automation_level < 0.5:
            recommendations.append("Increase automation to reduce manual errors")
        
        if factors.historical_accuracy < 0.7:
            recommendations.append("Review and improve validation methods based on historical performance")
        
        if factors.cross_validation < 0.6:
            recommendations.append("Add cross-validation with independent sources")
        
        if factors.error_rate > 0.1:
            recommendations.append("Reduce error rate through improved validation procedures")
        
        # Overall confidence recommendations
        if confidence_level == ConfidenceLevel.VERY_LOW:
            recommendations.append("Critical: Multiple factors need improvement before results can be trusted")
        elif confidence_level == ConfidenceLevel.LOW:
            recommendations.append("Significant improvements needed in key confidence factors")
        elif confidence_level == ConfidenceLevel.MEDIUM:
            recommendations.append("Consider improving weakest factors to increase confidence")
        
        return recommendations
    
    def calculate_validation_confidence(self, validation_results: List[Dict[str, Any]],
                                      target: str) -> ConfidenceScore:
        """Calculate confidence score for validation results."""
        if not validation_results:
            return self.calculate_confidence_score(
                target=target,
                factors=ConfidenceFactors(
                    sample_size=0.0,
                    validation_coverage=0.0
                )
            )
        
        # Analyze validation results to determine factors
        factors = self._analyze_validation_results(validation_results)
        
        return self.calculate_confidence_score(
            target=target,
            factors=factors,
            method='ensemble',
            additional_data={'validation_results': validation_results}
        )
    
    def _analyze_validation_results(self, validation_results: List[Dict[str, Any]]) -> ConfidenceFactors:
        """Analyze validation results to determine confidence factors."""
        if not validation_results:
            return ConfidenceFactors()
        
        # Data freshness - based on timestamps
        timestamps = []
        for result in validation_results:
            if 'timestamp' in result:
                try:
                    if isinstance(result['timestamp'], str):
                        timestamp = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
                    else:
                        timestamp = result['timestamp']
                    timestamps.append(timestamp)
                except:
                    pass
        
        if timestamps:
            latest_timestamp = max(timestamps)
            age_hours = (datetime.now() - latest_timestamp).total_seconds() / 3600
            data_freshness = max(0.0, 1.0 - (age_hours / 24.0))  # Decay over 24 hours
        else:
            data_freshness = 0.5  # Unknown
        
        # Sample size - based on number of results
        sample_size = min(1.0, len(validation_results) / 10.0)  # Optimal at 10+ samples
        
        # Consistency - based on result variance
        success_rates = []
        for result in validation_results:
            if 'status' in result:
                success_rates.append(1.0 if result['status'] in ['passed', 'success'] else 0.0)
            elif 'accuracy_score' in result:
                success_rates.append(result['accuracy_score'])
        
        if len(success_rates) > 1:
            consistency = 1.0 - min(1.0, statistics.stdev(success_rates))
        else:
            consistency = 1.0 if success_rates else 0.0
        
        # Validation coverage - based on types of validations
        validation_types = set()
        for result in validation_results:
            if 'validation_type' in result:
                validation_types.add(result['validation_type'])
            elif 'type' in result:
                validation_types.add(result['type'])
        
        expected_types = {'endpoint', 'websocket', 'service', 'documentation', 'security'}
        validation_coverage = len(validation_types) / len(expected_types)
        
        # Automation level - based on automated vs manual results
        automated_count = 0
        for result in validation_results:
            if result.get('automated', True):  # Default to automated
                automated_count += 1
        
        automation_level = automated_count / len(validation_results)
        
        # Historical accuracy - use default for now
        historical_accuracy = 0.8
        
        # Cross validation - check for multiple validation sources
        sources = set()
        for result in validation_results:
            if 'source' in result:
                sources.add(result['source'])
        
        cross_validation = min(1.0, len(sources) / 3.0)  # Optimal at 3+ sources
        
        # Error rate - based on failed validations
        failed_count = len([r for r in validation_results if r.get('status') in ['failed', 'error']])
        error_rate = failed_count / len(validation_results)
        
        return ConfidenceFactors(
            data_freshness=data_freshness,
            sample_size=sample_size,
            consistency=consistency,
            validation_coverage=validation_coverage,
            automation_level=automation_level,
            historical_accuracy=historical_accuracy,
            cross_validation=cross_validation,
            error_rate=error_rate
        )
    
    def calculate_documentation_confidence(self, documentation_metrics: Dict[str, Any],
                                         target: str) -> ConfidenceScore:
        """Calculate confidence score for documentation accuracy."""
        # Extract factors from documentation metrics
        factors = ConfidenceFactors()
        
        # Data freshness - based on last update time
        if 'last_updated' in documentation_metrics:
            try:
                last_updated = datetime.fromisoformat(documentation_metrics['last_updated'])
                age_hours = (datetime.now() - last_updated).total_seconds() / 3600
                factors.data_freshness = max(0.0, 1.0 - (age_hours / 168.0))  # Decay over 1 week
            except:
                factors.data_freshness = 0.5
        
        # Sample size - based on number of documents or validations
        if 'document_count' in documentation_metrics:
            factors.sample_size = min(1.0, documentation_metrics['document_count'] / 20.0)
        
        # Consistency - based on accuracy variance across documents
        if 'accuracy_scores' in documentation_metrics:
            scores = documentation_metrics['accuracy_scores']
            if len(scores) > 1:
                factors.consistency = 1.0 - min(1.0, statistics.stdev(scores))
            else:
                factors.consistency = 1.0 if scores else 0.0
        
        # Validation coverage - based on coverage metrics
        if 'coverage_percentage' in documentation_metrics:
            factors.validation_coverage = documentation_metrics['coverage_percentage'] / 100.0
        
        # Automation level - based on automated validation percentage
        if 'automated_percentage' in documentation_metrics:
            factors.automation_level = documentation_metrics['automated_percentage'] / 100.0
        
        # Error rate - based on validation failures
        if 'error_rate' in documentation_metrics:
            factors.error_rate = documentation_metrics['error_rate']
        
        return self.calculate_confidence_score(
            target=target,
            factors=factors,
            method='weighted_average',
            additional_data=documentation_metrics
        )
    
    def get_confidence_trend(self, target: str, days: int = 7) -> Dict[str, Any]:
        """Get confidence trend for a target over specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get scores for the target within the time period
        target_scores = [
            score for score in self.confidence_scores
            if score.target == target and score.timestamp > cutoff_date
        ]
        
        if not target_scores:
            return {'target': target, 'trend': [], 'summary': 'No data available'}
        
        # Sort by timestamp
        target_scores.sort(key=lambda x: x.timestamp)
        
        # Create trend data
        trend_data = [
            {
                'timestamp': score.timestamp.isoformat(),
                'score': score.overall_score,
                'confidence_level': score.confidence_level.value
            }
            for score in target_scores
        ]
        
        # Calculate trend statistics
        scores = [score.overall_score for score in target_scores]
        trend_direction = 'stable'
        
        if len(scores) >= 2:
            # Simple linear trend
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            if second_avg > first_avg + 0.05:
                trend_direction = 'improving'
            elif second_avg < first_avg - 0.05:
                trend_direction = 'declining'
        
        return {
            'target': target,
            'trend': trend_data,
            'summary': {
                'total_scores': len(target_scores),
                'latest_score': scores[-1],
                'average_score': statistics.mean(scores),
                'trend_direction': trend_direction,
                'score_range': [min(scores), max(scores)]
            }
        }
    
    def get_confidence_summary(self) -> Dict[str, Any]:
        """Get overall confidence scoring summary."""
        if not self.confidence_scores:
            return {
                'total_scores': 0,
                'targets_scored': 0,
                'average_confidence': 0.0
            }
        
        # Overall statistics
        all_scores = [score.overall_score for score in self.confidence_scores]
        
        # Confidence level distribution
        level_counts = {}
        for level in ConfidenceLevel:
            level_counts[level.value] = len([
                score for score in self.confidence_scores 
                if score.confidence_level == level
            ])
        
        # Target statistics
        target_stats = {}
        for target in self.historical_data:
            if self.historical_data[target]:
                target_stats[target] = {
                    'score_count': len(self.historical_data[target]),
                    'average_score': statistics.mean(self.historical_data[target]),
                    'latest_score': self.historical_data[target][-1]
                }
        
        return {
            'total_scores': len(self.confidence_scores),
            'targets_scored': len(self.historical_data),
            'average_confidence': statistics.mean(all_scores),
            'confidence_distribution': level_counts,
            'target_statistics': target_stats,
            'calculation_methods_used': list(set(score.calculation_method for score in self.confidence_scores))
        }
    
    def set_confidence_weights(self, weights: ConfidenceWeights):
        """Set custom confidence factor weights."""
        # Validate weights sum to approximately 1.0
        total_weight = sum([
            weights.data_freshness,
            weights.sample_size,
            weights.consistency,
            weights.validation_coverage,
            weights.automation_level,
            weights.historical_accuracy,
            weights.cross_validation,
            weights.error_rate
        ])
        
        if abs(total_weight - 1.0) > 0.01:
            self.logger.warning(f"Confidence weights sum to {total_weight}, not 1.0")
        
        self.weights = weights
        self.logger.info("Updated confidence scoring weights")
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'total_scores': len(self.confidence_scores),
            'targets_tracked': len(self.historical_data),
            'calculation_methods': ['weighted_average', 'bayesian', 'ensemble']
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,
            'weights_configured': True,
            'thresholds_configured': len(self.confidence_thresholds) > 0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get confidence scoring metrics."""
        summary = self.get_confidence_summary()
        
        return {
            'confidence_scorer_total_scores': summary['total_scores'],
            'confidence_scorer_targets_scored': summary['targets_scored'],
            'confidence_scorer_average_confidence': summary['average_confidence']
        }


# Example usage and testing
if __name__ == "__main__":
    def main():
        # Create confidence scorer
        scorer = ConfidenceScorer()
        
        # Example 1: Calculate confidence for validation results
        validation_results = [
            {'status': 'passed', 'timestamp': datetime.now().isoformat(), 'validation_type': 'endpoint'},
            {'status': 'passed', 'timestamp': datetime.now().isoformat(), 'validation_type': 'websocket'},
            {'status': 'failed', 'timestamp': datetime.now().isoformat(), 'validation_type': 'service'}
        ]
        
        confidence = scorer.calculate_validation_confidence(validation_results, 'test_system')
        print(f"Validation confidence: {confidence.overall_score:.3f} ({confidence.confidence_level.value})")
        print(f"Recommendations: {confidence.recommendations}")
        
        # Example 2: Calculate confidence with custom factors
        custom_factors = ConfidenceFactors(
            data_freshness=0.9,
            sample_size=0.8,
            consistency=0.95,
            validation_coverage=0.7,
            automation_level=0.85,
            historical_accuracy=0.8,
            cross_validation=0.6,
            error_rate=0.05
        )
        
        confidence = scorer.calculate_confidence_score('custom_test', custom_factors, 'ensemble')
        print(f"Custom confidence: {confidence.overall_score:.3f} ({confidence.confidence_level.value})")
        
        # Example 3: Get confidence summary
        summary = scorer.get_confidence_summary()
        print(f"Summary: {summary}")
    
    main()