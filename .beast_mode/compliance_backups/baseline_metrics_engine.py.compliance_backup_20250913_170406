"""
Beast Mode Framework - Baseline Metrics Engine
Implements performance baseline establishment and metrics collection
Requirements: R8.1, R8.2, R8.3, R8.4, R8.5, DR1, Constraint C-07
"""

import time
import json
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import concurrent.futures
import threading
from pathlib import Path

from ..core.reflective_module import ReflectiveModule, HealthStatus

@dataclass
class MeasurementCategory:
    name: str
    description: str
    unit: str
    baseline_samples: List[float]
    systematic_samples: List[float]
    
@dataclass
class PerformanceMetrics:
    category: str
    baseline_mean: float
    systematic_mean: float
    improvement_ratio: float
    statistical_significance: float
    sample_count: int
    timestamp: datetime

@dataclass
class SuperiorityEvidence:
    problem_resolution_speed: PerformanceMetrics
    tool_health_performance: PerformanceMetrics  
    decision_success_rates: PerformanceMetrics
    development_velocity: PerformanceMetrics
    overall_superiority_score: float
    evidence_quality_score: float

class BaselineMetricsEngine(ReflectiveModule):
    """
    Establishes performance baseline and collects metrics for systematic vs ad-hoc comparison
    Addresses UK-05 (Unknown performance baseline) and UC-04 (Measurable superiority)
    """
    
    def __init__(self):
        super().__init__("baseline_metrics_engine")
        self.measurement_categories = {
            'problem_resolution_speed': MeasurementCategory(
                name='problem_resolution_speed',
                description='Time from problem identification to resolution',
                unit='seconds',
                baseline_samples=[],
                systematic_samples=[]
            ),
            'tool_health_performance': MeasurementCategory(
                name='tool_health_performance', 
                description='Tool failure frequency and repair effectiveness',
                unit='success_rate',
                baseline_samples=[],
                systematic_samples=[]
            ),
            'decision_success_rates': MeasurementCategory(
                name='decision_success_rates',
                description='Accuracy and effectiveness of decision outcomes', 
                unit='success_rate',
                baseline_samples=[],
                systematic_samples=[]
            ),
            'development_velocity': MeasurementCategory(
                name='development_velocity',
                description='Feature completion time and quality metrics',
                unit='features_per_hour',
                baseline_samples=[],
                systematic_samples=[]
            )
        }
        
        self.concurrent_measurements = 0
        self.max_concurrent_measurements = 1000  # Constraint C-07
        self.measurement_lock = threading.Lock()
        self.metrics_storage_path = Path("metrics_data")
        self.metrics_storage_path.mkdir(exist_ok=True)
        
        # Initialize health indicators
        self._update_health_indicator(
            "concurrent_capacity", 
            HealthStatus.HEALTHY, 
            f"0/{self.max_concurrent_measurements}",
            "Ready for concurrent measurements"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems (GKE)"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "measurement_categories": list(self.measurement_categories.keys()),
            "concurrent_measurements": self.concurrent_measurements,
            "max_capacity": self.max_concurrent_measurements,
            "capacity_utilization": f"{(self.concurrent_measurements/self.max_concurrent_measurements)*100:.1f}%",
            "total_baseline_samples": sum(len(cat.baseline_samples) for cat in self.measurement_categories.values()),
            "total_systematic_samples": sum(len(cat.systematic_samples) for cat in self.measurement_categories.values()),
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment based on capacity and operational status"""
        capacity_ok = self.concurrent_measurements < self.max_concurrent_measurements * 0.9
        storage_ok = self.metrics_storage_path.exists() and self.metrics_storage_path.is_dir()
        return capacity_ok and storage_ok and not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {
            "concurrent_capacity": {
                "status": "healthy" if self.concurrent_measurements < self.max_concurrent_measurements * 0.8 else "degraded",
                "current": self.concurrent_measurements,
                "maximum": self.max_concurrent_measurements,
                "utilization_percent": (self.concurrent_measurements/self.max_concurrent_measurements)*100
            },
            "storage_health": {
                "status": "healthy" if self.metrics_storage_path.exists() else "unhealthy",
                "path": str(self.metrics_storage_path),
                "writable": self.metrics_storage_path.is_dir() if self.metrics_storage_path.exists() else False
            },
            "measurement_readiness": {
                "status": "healthy" if len(self.measurement_categories) == 4 else "degraded",
                "categories_configured": len(self.measurement_categories),
                "expected_categories": 4
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Performance baseline establishment and metrics collection"""
        return "performance_baseline_establishment_and_metrics_collection"
        
    def _check_boundary_violations(self) -> List[str]:
        """Check for architectural boundary violations"""
        violations = []
        
        # Should not implement business logic beyond metrics
        # Should not handle tool repair or decision making
        # Should delegate to specialized analysis tools
        
        return violations  # No violations in current implementation
        
    def establish_baseline_measurement(self, category: str, approach_type: str, measurement_value: float) -> bool:
        """
        Record a baseline measurement for systematic vs ad-hoc comparison
        
        Args:
            category: One of the measurement categories
            approach_type: 'baseline' (ad-hoc) or 'systematic'  
            measurement_value: The measured value
            
        Returns:
            bool: Success status
        """
        if category not in self.measurement_categories:
            self.logger.error(f"Unknown measurement category: {category}")
            return False
            
        # Check concurrent measurement capacity (Constraint C-07)
        with self.measurement_lock:
            if self.concurrent_measurements >= self.max_concurrent_measurements:
                self.logger.warning("Maximum concurrent measurements reached")
                return False
                
            self.concurrent_measurements += 1
            
        try:
            # Record the measurement
            if approach_type == 'baseline':
                self.measurement_categories[category].baseline_samples.append(measurement_value)
            elif approach_type == 'systematic':
                self.measurement_categories[category].systematic_samples.append(measurement_value)
            else:
                self.logger.error(f"Invalid approach_type: {approach_type}")
                return False
                
            # Persist measurement
            self._persist_measurement(category, approach_type, measurement_value)
            
            # Update health indicators
            self._update_health_indicator(
                "concurrent_capacity",
                HealthStatus.HEALTHY if self.concurrent_measurements < self.max_concurrent_measurements * 0.8 else HealthStatus.DEGRADED,
                f"{self.concurrent_measurements}/{self.max_concurrent_measurements}",
                f"Concurrent measurements: {self.concurrent_measurements}"
            )
            
            return True
            
        finally:
            with self.measurement_lock:
                self.concurrent_measurements -= 1
                
    def _persist_measurement(self, category: str, approach_type: str, value: float):
        """Persist measurement to storage for analysis"""
        measurement_data = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "approach_type": approach_type,
            "value": value
        }
        
        file_path = self.metrics_storage_path / f"{category}_{approach_type}_measurements.jsonl"
        with open(file_path, 'a') as f:
            f.write(json.dumps(measurement_data) + '\n')
            
    def calculate_performance_metrics(self, category: str) -> Optional[PerformanceMetrics]:
        """
        Calculate performance metrics for a measurement category
        Returns statistical comparison of systematic vs baseline approaches
        """
        if category not in self.measurement_categories:
            return None
            
        cat_data = self.measurement_categories[category]
        
        if len(cat_data.baseline_samples) < 3 or len(cat_data.systematic_samples) < 3:
            self.logger.warning(f"Insufficient samples for {category}: baseline={len(cat_data.baseline_samples)}, systematic={len(cat_data.systematic_samples)}")
            return None
            
        baseline_mean = statistics.mean(cat_data.baseline_samples)
        systematic_mean = statistics.mean(cat_data.systematic_samples)
        
        # Calculate improvement ratio (systematic should be better)
        if category in ['problem_resolution_speed']:
            # Lower is better for time-based metrics
            improvement_ratio = baseline_mean / systematic_mean if systematic_mean > 0 else 0
        else:
            # Higher is better for success rates and velocity
            improvement_ratio = systematic_mean / baseline_mean if baseline_mean > 0 else 0
            
        # Simple statistical significance test (t-test approximation)
        baseline_std = statistics.stdev(cat_data.baseline_samples) if len(cat_data.baseline_samples) > 1 else 0
        systematic_std = statistics.stdev(cat_data.systematic_samples) if len(cat_data.systematic_samples) > 1 else 0
        
        # Simplified significance calculation
        pooled_std = (baseline_std + systematic_std) / 2
        mean_difference = abs(systematic_mean - baseline_mean)
        statistical_significance = mean_difference / pooled_std if pooled_std > 0 else 0
        
        return PerformanceMetrics(
            category=category,
            baseline_mean=baseline_mean,
            systematic_mean=systematic_mean,
            improvement_ratio=improvement_ratio,
            statistical_significance=statistical_significance,
            sample_count=len(cat_data.baseline_samples) + len(cat_data.systematic_samples),
            timestamp=datetime.now()
        )
        
    def generate_superiority_evidence(self) -> Optional[SuperiorityEvidence]:
        """
        Generate comprehensive superiority evidence for Beast Mode vs ad-hoc approaches
        Required by R8.5 - provide concrete metrics proving Beast Mode superiority
        """
        metrics = {}
        
        for category in self.measurement_categories.keys():
            perf_metrics = self.calculate_performance_metrics(category)
            if perf_metrics:
                metrics[category] = perf_metrics
                
        if len(metrics) < 4:
            self.logger.warning("Insufficient metrics for superiority evidence generation")
            return None
            
        # Calculate overall superiority score
        improvement_ratios = [m.improvement_ratio for m in metrics.values()]
        overall_superiority_score = statistics.mean(improvement_ratios)
        
        # Calculate evidence quality score based on sample sizes and statistical significance
        significance_scores = [m.statistical_significance for m in metrics.values()]
        sample_scores = [min(1.0, m.sample_count / 20) for m in metrics.values()]  # 20 samples = full score
        evidence_quality_score = (statistics.mean(significance_scores) + statistics.mean(sample_scores)) / 2
        
        return SuperiorityEvidence(
            problem_resolution_speed=metrics['problem_resolution_speed'],
            tool_health_performance=metrics['tool_health_performance'],
            decision_success_rates=metrics['decision_success_rates'], 
            development_velocity=metrics['development_velocity'],
            overall_superiority_score=overall_superiority_score,
            evidence_quality_score=evidence_quality_score
        )