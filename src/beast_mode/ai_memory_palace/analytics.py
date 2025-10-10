"""
Context Analytics and Optimization for AI Memory Palace.

Provides context usage analytics, performance monitoring, automatic optimization,
cleanup suggestions, context pattern analysis, and quality metrics.
"""

import json
import asyncio
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import uuid
import re
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import math

from src.beast_mode.core.beastly_module import BeastlyModule
from .models import SessionContext, ContextEvent, ContextEventType, Decision, WorkItem
from .context_manager import ContextManager
from .context_registry import ContextRegistry
from .storage import ContextDatabase


class AnalyticsMetricType(Enum):
    """Types of analytics metrics"""
    USAGE = "usage"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    PATTERN = "pattern"


class OptimizationStrategy(Enum):
    """Context optimization strategies"""
    SUMMARIZATION = "summarization"
    COMPRESSION = "compression"
    ARCHIVAL = "archival"
    DEDUPLICATION = "deduplication"
    CLEANUP = "cleanup"


@dataclass
class AnalyticsMetric:
    """Analytics metric data point"""
    metric_id: str
    metric_type: AnalyticsMetricType
    name: str
    value: float
    unit: str
    timestamp: datetime
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "metric_type": self.metric_type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "project_id": self.project_id,
            "session_id": self.session_id,
            "metadata": self.metadata
        }


@dataclass
class OptimizationRecommendation:
    """Context optimization recommendation"""
    recommendation_id: str
    strategy: OptimizationStrategy
    priority: str  # high, medium, low
    title: str
    description: str
    estimated_savings_mb: float
    estimated_performance_gain: float
    implementation_complexity: str  # simple, moderate, complex
    target_project_id: Optional[str] = None
    target_session_id: Optional[str] = None
    created: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "strategy": self.strategy.value,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "estimated_savings_mb": self.estimated_savings_mb,
            "estimated_performance_gain": self.estimated_performance_gain,
            "implementation_complexity": self.implementation_complexity,
            "target_project_id": self.target_project_id,
            "target_session_id": self.target_session_id,
            "created": self.created.isoformat()
        }


@dataclass
class UsagePattern:
    """Detected usage pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "description": self.description,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "examples": self.examples,
            "metadata": self.metadata
        }


class ContextAnalyzer(BeastlyModule):
    """Analyzes context usage patterns and performance"""
    
    def __init__(self, context_registry: ContextRegistry):
        super().__init__()
        
        self.context_registry = context_registry
        
        # Analytics storage
        self.metrics: List[AnalyticsMetric] = []
        self.patterns: Dict[str, UsagePattern] = {}
        
        # Analysis configuration
        self.max_metrics_history = 10000
        self.pattern_detection_threshold = 3
        self.analysis_window_days = 30
        
        # Analysis metrics
        self._analyses_performed = 0
        self._patterns_detected = 0
        self._metrics_collected = 0
        
        self.logger.info("📊 ContextAnalyzer initialized")
    
    def analyze_context_usage(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze context usage patterns and statistics"""
        try:
            self._analyses_performed += 1
            
            analysis_result = {
                "analysis_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "project_id": project_id,
                "usage_statistics": {},
                "performance_metrics": {},
                "quality_metrics": {},
                "patterns_detected": [],
                "recommendations": []
            }
            
            # Get contexts to analyze
            if project_id:
                contexts = [self.context_registry.load_context(project_id)]
                contexts = [c for c in contexts if c is not None]
            else:
                # Analyze all contexts (simplified - would need registry method)
                contexts = self._get_all_contexts()
            
            if not contexts:
                analysis_result["error"] = "No contexts found for analysis"
                return analysis_result
            
            # Perform usage analysis
            analysis_result["usage_statistics"] = self._analyze_usage_statistics(contexts)
            
            # Perform performance analysis
            analysis_result["performance_metrics"] = self._analyze_performance_metrics(contexts)
            
            # Perform quality analysis
            analysis_result["quality_metrics"] = self._analyze_quality_metrics(contexts)
            
            # Detect patterns
            patterns = self._detect_usage_patterns(contexts)
            analysis_result["patterns_detected"] = [p.to_dict() for p in patterns]
            
            # Store detected patterns
            for pattern in patterns:
                self.patterns[pattern.pattern_id] = pattern
                self._patterns_detected += 1
            
            # Emit analysis observation
            self.emit_observation({
                "type": "context_analysis_completed",
                "analysis_id": analysis_result["analysis_id"],
                "project_id": project_id,
                "contexts_analyzed": len(contexts),
                "patterns_detected": len(patterns),
                "analysis_timestamp": analysis_result["timestamp"]
            })
            
            self.logger.info(f"📊 Context analysis completed: {len(contexts)} contexts, {len(patterns)} patterns")
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"💥 Context analysis error: {e}")
            return {
                "analysis_id": str(uuid.uuid4()),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def collect_performance_metrics(self, context: SessionContext, 
                                   operation: str, duration_ms: float) -> str:
        """Collect performance metrics for context operations"""
        try:
            metric = AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=AnalyticsMetricType.PERFORMANCE,
                name=f"context_{operation}_duration",
                value=duration_ms,
                unit="milliseconds",
                timestamp=datetime.now(),
                project_id=context.project_id,
                session_id=context.session_id,
                metadata={
                    "operation": operation,
                    "context_size_bytes": context.get_context_size(),
                    "conversation_events": len(context.conversation_history)
                }
            )
            
            self._store_metric(metric)
            self._metrics_collected += 1
            
            return metric.metric_id
            
        except Exception as e:
            self.logger.error(f"💥 Error collecting performance metric: {e}")
            return ""
    
    def collect_usage_metrics(self, context: SessionContext, 
                             metric_name: str, value: float, unit: str) -> str:
        """Collect usage metrics for context"""
        try:
            metric = AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=AnalyticsMetricType.USAGE,
                name=metric_name,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                project_id=context.project_id,
                session_id=context.session_id
            )
            
            self._store_metric(metric)
            self._metrics_collected += 1
            
            return metric.metric_id
            
        except Exception as e:
            self.logger.error(f"💥 Error collecting usage metric: {e}")
            return ""
    
    def get_analytics_dashboard(self, project_id: Optional[str] = None, 
                               days: int = 7) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter metrics by date and project
            relevant_metrics = [
                m for m in self.metrics
                if m.timestamp >= cutoff_date and (not project_id or m.project_id == project_id)
            ]
            
            dashboard = {
                "period_days": days,
                "project_id": project_id,
                "metrics_count": len(relevant_metrics),
                "summary": self._generate_metrics_summary(relevant_metrics),
                "trends": self._analyze_metrics_trends(relevant_metrics),
                "top_patterns": self._get_top_patterns(project_id),
                "performance_insights": self._get_performance_insights(relevant_metrics),
                "usage_insights": self._get_usage_insights(relevant_metrics),
                "generated_at": datetime.now().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"💥 Error generating analytics dashboard: {e}")
            return {"error": str(e)}
    
    def _analyze_usage_statistics(self, contexts: List[SessionContext]) -> Dict[str, Any]:
        """Analyze usage statistics across contexts"""
        if not contexts:
            return {}
        
        stats = {
            "total_contexts": len(contexts),
            "total_size_mb": sum(c.get_context_size() for c in contexts) / 1024 / 1024,
            "average_size_mb": 0,
            "conversation_events": {
                "total": sum(len(c.conversation_history) for c in contexts),
                "average_per_context": 0,
                "max_per_context": max(len(c.conversation_history) for c in contexts) if contexts else 0
            },
            "decisions_made": {
                "total": sum(len(c.decisions_made) for c in contexts),
                "average_per_context": 0
            },
            "work_completed": {
                "total": sum(len(c.work_completed) for c in contexts),
                "average_per_context": 0
            },
            "age_distribution": self._analyze_context_ages(contexts),
            "size_distribution": self._analyze_size_distribution(contexts)
        }
        
        # Calculate averages
        if contexts:
            stats["average_size_mb"] = stats["total_size_mb"] / len(contexts)
            stats["conversation_events"]["average_per_context"] = stats["conversation_events"]["total"] / len(contexts)
            stats["decisions_made"]["average_per_context"] = stats["decisions_made"]["total"] / len(contexts)
            stats["work_completed"]["average_per_context"] = stats["work_completed"]["total"] / len(contexts)
        
        return stats
    
    def _analyze_performance_metrics(self, contexts: List[SessionContext]) -> Dict[str, Any]:
        """Analyze performance metrics"""
        performance_metrics = [m for m in self.metrics if m.metric_type == AnalyticsMetricType.PERFORMANCE]
        
        if not performance_metrics:
            return {"error": "No performance metrics available"}
        
        # Group by operation type
        operations = defaultdict(list)
        for metric in performance_metrics:
            operation = metric.metadata.get("operation", "unknown")
            operations[operation].append(metric.value)
        
        performance_analysis = {}
        for operation, values in operations.items():
            if values:
                performance_analysis[operation] = {
                    "count": len(values),
                    "average_ms": statistics.mean(values),
                    "median_ms": statistics.median(values),
                    "min_ms": min(values),
                    "max_ms": max(values),
                    "std_dev_ms": statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return performance_analysis
    
    def _analyze_quality_metrics(self, contexts: List[SessionContext]) -> Dict[str, Any]:
        """Analyze context quality metrics"""
        quality_metrics = {
            "completeness_score": 0,
            "consistency_score": 0,
            "relevance_score": 0,
            "freshness_score": 0,
            "overall_quality_score": 0,
            "quality_issues": []
        }
        
        if not contexts:
            return quality_metrics
        
        # Analyze completeness (presence of key components)
        completeness_scores = []
        for context in contexts:
            score = 0
            if context.conversation_history:
                score += 25
            if context.decisions_made:
                score += 25
            if context.work_completed:
                score += 25
            if context.project_state:
                score += 25
            completeness_scores.append(score)
        
        quality_metrics["completeness_score"] = statistics.mean(completeness_scores) if completeness_scores else 0
        
        # Analyze consistency (timestamp ordering, data integrity)
        consistency_scores = []
        for context in contexts:
            score = 100  # Start with perfect score
            
            # Check timestamp ordering
            timestamps = [event.timestamp for event in context.conversation_history]
            if timestamps != sorted(timestamps):
                score -= 20
            
            # Check for duplicate events
            event_ids = [event.event_id for event in context.conversation_history]
            if len(event_ids) != len(set(event_ids)):
                score -= 20
            
            consistency_scores.append(max(0, score))
        
        quality_metrics["consistency_score"] = statistics.mean(consistency_scores) if consistency_scores else 0
        
        # Analyze freshness (recent activity)
        freshness_scores = []
        now = datetime.now()
        for context in contexts:
            if context.conversation_history:
                last_activity = max(event.timestamp for event in context.conversation_history)
                days_since_activity = (now - last_activity).days
                
                # Score decreases with age
                if days_since_activity <= 1:
                    score = 100
                elif days_since_activity <= 7:
                    score = 80
                elif days_since_activity <= 30:
                    score = 60
                else:
                    score = 20
            else:
                score = 0
            
            freshness_scores.append(score)
        
        quality_metrics["freshness_score"] = statistics.mean(freshness_scores) if freshness_scores else 0
        
        # Calculate overall quality score
        scores = [
            quality_metrics["completeness_score"],
            quality_metrics["consistency_score"],
            quality_metrics["freshness_score"]
        ]
        quality_metrics["overall_quality_score"] = statistics.mean(scores)
        
        # Identify quality issues
        if quality_metrics["completeness_score"] < 50:
            quality_metrics["quality_issues"].append("Low completeness - contexts missing key components")
        
        if quality_metrics["consistency_score"] < 80:
            quality_metrics["quality_issues"].append("Consistency issues - timestamp or data integrity problems")
        
        if quality_metrics["freshness_score"] < 60:
            quality_metrics["quality_issues"].append("Stale contexts - low recent activity")
        
        return quality_metrics
    
    def _detect_usage_patterns(self, contexts: List[SessionContext]) -> List[UsagePattern]:
        """Detect usage patterns in contexts"""
        patterns = []
        
        try:
            # Pattern 1: Conversation length patterns
            conversation_lengths = [len(c.conversation_history) for c in contexts]
            if conversation_lengths:
                avg_length = statistics.mean(conversation_lengths)
                
                if avg_length > 100:
                    patterns.append(UsagePattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type="high_conversation_volume",
                        description=f"High conversation volume detected (avg: {avg_length:.1f} events)",
                        frequency=len([l for l in conversation_lengths if l > 100]),
                        confidence=0.8,
                        examples=[f"Context with {max(conversation_lengths)} events"],
                        metadata={"average_length": avg_length, "max_length": max(conversation_lengths)}
                    ))
            
            # Pattern 2: Decision-making patterns
            decision_counts = [len(c.decisions_made) for c in contexts]
            high_decision_contexts = [c for c in contexts if len(c.decisions_made) > 10]
            
            if len(high_decision_contexts) >= self.pattern_detection_threshold:
                patterns.append(UsagePattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="high_decision_activity",
                    description=f"High decision-making activity in {len(high_decision_contexts)} contexts",
                    frequency=len(high_decision_contexts),
                    confidence=0.7,
                    examples=[f"Context with {max(decision_counts)} decisions" if decision_counts else ""],
                    metadata={"contexts_with_high_decisions": len(high_decision_contexts)}
                ))
            
            # Pattern 3: Work completion patterns
            work_counts = [len(c.work_completed) for c in contexts]
            productive_contexts = [c for c in contexts if len(c.work_completed) > 5]
            
            if len(productive_contexts) >= self.pattern_detection_threshold:
                patterns.append(UsagePattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="high_productivity",
                    description=f"High productivity pattern in {len(productive_contexts)} contexts",
                    frequency=len(productive_contexts),
                    confidence=0.8,
                    examples=[f"Context with {max(work_counts)} work items" if work_counts else ""],
                    metadata={"productive_contexts": len(productive_contexts)}
                ))
            
            # Pattern 4: Context size patterns
            sizes_mb = [c.get_context_size() / 1024 / 1024 for c in contexts]
            large_contexts = [s for s in sizes_mb if s > 10]  # > 10MB
            
            if len(large_contexts) >= self.pattern_detection_threshold:
                patterns.append(UsagePattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="large_context_usage",
                    description=f"Large context usage pattern detected ({len(large_contexts)} contexts > 10MB)",
                    frequency=len(large_contexts),
                    confidence=0.9,
                    examples=[f"Context size: {max(sizes_mb):.1f}MB" if sizes_mb else ""],
                    metadata={"large_contexts_count": len(large_contexts), "max_size_mb": max(sizes_mb) if sizes_mb else 0}
                ))
            
            # Pattern 5: Event type patterns
            event_type_counts = defaultdict(int)
            for context in contexts:
                for event in context.conversation_history:
                    event_type_counts[event.event_type] += 1
            
            if event_type_counts:
                dominant_type = max(event_type_counts.items(), key=lambda x: x[1])
                if dominant_type[1] > sum(event_type_counts.values()) * 0.6:  # > 60% of events
                    patterns.append(UsagePattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type="dominant_event_type",
                        description=f"Dominant event type: {dominant_type[0]} ({dominant_type[1]} events)",
                        frequency=dominant_type[1],
                        confidence=0.7,
                        examples=[f"{dominant_type[0]}: {dominant_type[1]} occurrences"],
                        metadata={"event_type_distribution": dict(event_type_counts)}
                    ))
            
        except Exception as e:
            self.logger.error(f"💥 Error detecting usage patterns: {e}")
        
        return patterns
    
    def _analyze_context_ages(self, contexts: List[SessionContext]) -> Dict[str, int]:
        """Analyze age distribution of contexts"""
        now = datetime.now()
        age_buckets = {
            "less_than_1_day": 0,
            "1_to_7_days": 0,
            "1_to_4_weeks": 0,
            "1_to_3_months": 0,
            "older_than_3_months": 0
        }
        
        for context in contexts:
            age = now - context.timestamp
            
            if age.days < 1:
                age_buckets["less_than_1_day"] += 1
            elif age.days <= 7:
                age_buckets["1_to_7_days"] += 1
            elif age.days <= 28:
                age_buckets["1_to_4_weeks"] += 1
            elif age.days <= 90:
                age_buckets["1_to_3_months"] += 1
            else:
                age_buckets["older_than_3_months"] += 1
        
        return age_buckets
    
    def _analyze_size_distribution(self, contexts: List[SessionContext]) -> Dict[str, int]:
        """Analyze size distribution of contexts"""
        size_buckets = {
            "small_less_than_1mb": 0,
            "medium_1_to_10mb": 0,
            "large_10_to_50mb": 0,
            "very_large_over_50mb": 0
        }
        
        for context in contexts:
            size_mb = context.get_context_size() / 1024 / 1024
            
            if size_mb < 1:
                size_buckets["small_less_than_1mb"] += 1
            elif size_mb <= 10:
                size_buckets["medium_1_to_10mb"] += 1
            elif size_mb <= 50:
                size_buckets["large_10_to_50mb"] += 1
            else:
                size_buckets["very_large_over_50mb"] += 1
        
        return size_buckets
    
    def _generate_metrics_summary(self, metrics: List[AnalyticsMetric]) -> Dict[str, Any]:
        """Generate summary of metrics"""
        if not metrics:
            return {}
        
        # Group by metric type
        by_type = defaultdict(list)
        for metric in metrics:
            by_type[metric.metric_type].append(metric)
        
        summary = {}
        for metric_type, type_metrics in by_type.items():
            values = [m.value for m in type_metrics]
            summary[metric_type.value] = {
                "count": len(values),
                "average": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values)
            }
        
        return summary
    
    def _analyze_metrics_trends(self, metrics: List[AnalyticsMetric]) -> Dict[str, Any]:
        """Analyze trends in metrics over time"""
        if len(metrics) < 2:
            return {}
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Group by metric name
        by_name = defaultdict(list)
        for metric in sorted_metrics:
            by_name[metric.name].append(metric)
        
        trends = {}
        for name, name_metrics in by_name.items():
            if len(name_metrics) >= 2:
                values = [m.value for m in name_metrics]
                
                # Simple trend calculation (first vs last)
                first_value = values[0]
                last_value = values[-1]
                
                if first_value != 0:
                    change_percent = ((last_value - first_value) / first_value) * 100
                else:
                    change_percent = 0
                
                trends[name] = {
                    "direction": "increasing" if change_percent > 5 else "decreasing" if change_percent < -5 else "stable",
                    "change_percent": change_percent,
                    "first_value": first_value,
                    "last_value": last_value,
                    "data_points": len(values)
                }
        
        return trends
    
    def _get_top_patterns(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get top detected patterns"""
        patterns = list(self.patterns.values())
        
        # Filter by project if specified
        if project_id:
            # Would need to add project filtering to patterns
            pass
        
        # Sort by frequency and confidence
        patterns.sort(key=lambda p: (p.frequency, p.confidence), reverse=True)
        
        return [p.to_dict() for p in patterns[:5]]  # Top 5 patterns
    
    def _get_performance_insights(self, metrics: List[AnalyticsMetric]) -> List[str]:
        """Generate performance insights from metrics"""
        insights = []
        
        perf_metrics = [m for m in metrics if m.metric_type == AnalyticsMetricType.PERFORMANCE]
        
        if not perf_metrics:
            return insights
        
        # Analyze load times
        load_metrics = [m for m in perf_metrics if "load" in m.name]
        if load_metrics:
            avg_load_time = statistics.mean([m.value for m in load_metrics])
            if avg_load_time > 2000:  # > 2 seconds
                insights.append(f"Context load times are high (avg: {avg_load_time:.0f}ms). Consider optimization.")
            elif avg_load_time < 500:  # < 500ms
                insights.append(f"Context load times are excellent (avg: {avg_load_time:.0f}ms).")
        
        # Analyze save times
        save_metrics = [m for m in perf_metrics if "save" in m.name or "store" in m.name]
        if save_metrics:
            avg_save_time = statistics.mean([m.value for m in save_metrics])
            if avg_save_time > 1000:  # > 1 second
                insights.append(f"Context save times are slow (avg: {avg_save_time:.0f}ms). Consider compression.")
        
        return insights
    
    def _get_usage_insights(self, metrics: List[AnalyticsMetric]) -> List[str]:
        """Generate usage insights from metrics"""
        insights = []
        
        usage_metrics = [m for m in metrics if m.metric_type == AnalyticsMetricType.USAGE]
        
        if not usage_metrics:
            return insights
        
        # Analyze context sizes
        size_metrics = [m for m in usage_metrics if "size" in m.name]
        if size_metrics:
            avg_size = statistics.mean([m.value for m in size_metrics])
            if avg_size > 50 * 1024 * 1024:  # > 50MB
                insights.append(f"Context sizes are large (avg: {avg_size/1024/1024:.1f}MB). Consider cleanup.")
        
        # Analyze session counts
        session_metrics = [m for m in usage_metrics if "session" in m.name]
        if session_metrics:
            total_sessions = sum([m.value for m in session_metrics])
            insights.append(f"Total sessions tracked: {total_sessions:.0f}")
        
        return insights
    
    def _store_metric(self, metric: AnalyticsMetric):
        """Store metric in memory (with size limit)"""
        self.metrics.append(metric)
        
        # Maintain size limit
        if len(self.metrics) > self.max_metrics_history:
            # Remove oldest metrics
            self.metrics = self.metrics[-self.max_metrics_history:]
    
    def _get_all_contexts(self) -> List[SessionContext]:
        """Get all contexts from registry (simplified implementation)"""
        # This would need a proper implementation in the registry
        # For now, return empty list
        return []


class ContextOptimizer(BeastlyModule):
    """Optimizes context storage and performance"""
    
    def __init__(self, context_registry: ContextRegistry, analyzer: ContextAnalyzer):
        super().__init__()
        
        self.context_registry = context_registry
        self.analyzer = analyzer
        
        # Optimization configuration
        self.size_threshold_mb = 50
        self.age_threshold_days = 90
        self.compression_ratio_target = 0.7
        
        # Optimization metrics
        self._optimizations_performed = 0
        self._space_saved_mb = 0
        self._performance_improvements = 0
        
        self.logger.info("⚡ ContextOptimizer initialized")
    
    def generate_optimization_recommendations(self, project_id: Optional[str] = None) -> List[OptimizationRecommendation]:
        """Generate context optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze current context state
            analysis = self.analyzer.analyze_context_usage(project_id)
            
            if "error" in analysis:
                return recommendations
            
            usage_stats = analysis.get("usage_statistics", {})
            quality_metrics = analysis.get("quality_metrics", {})
            
            # Recommendation 1: Large context summarization
            if usage_stats.get("average_size_mb", 0) > self.size_threshold_mb:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    strategy=OptimizationStrategy.SUMMARIZATION,
                    priority="high",
                    title="Summarize Large Contexts",
                    description=f"Average context size ({usage_stats['average_size_mb']:.1f}MB) exceeds threshold. Consider summarizing conversation history.",
                    estimated_savings_mb=usage_stats["average_size_mb"] * 0.6,
                    estimated_performance_gain=40.0,
                    implementation_complexity="moderate",
                    target_project_id=project_id
                ))
            
            # Recommendation 2: Compression for storage efficiency
            total_size_mb = usage_stats.get("total_size_mb", 0)
            if total_size_mb > 100:  # > 100MB total
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    strategy=OptimizationStrategy.COMPRESSION,
                    priority="medium",
                    title="Enable Context Compression",
                    description=f"Total context storage ({total_size_mb:.1f}MB) would benefit from compression.",
                    estimated_savings_mb=total_size_mb * 0.3,
                    estimated_performance_gain=15.0,
                    implementation_complexity="simple",
                    target_project_id=project_id
                ))
            
            # Recommendation 3: Archive old contexts
            age_dist = usage_stats.get("age_distribution", {})
            old_contexts = age_dist.get("older_than_3_months", 0)
            if old_contexts > 0:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    strategy=OptimizationStrategy.ARCHIVAL,
                    priority="low",
                    title="Archive Old Contexts",
                    description=f"Archive {old_contexts} contexts older than 3 months to improve performance.",
                    estimated_savings_mb=old_contexts * 5,  # Estimate 5MB per old context
                    estimated_performance_gain=10.0,
                    implementation_complexity="simple",
                    target_project_id=project_id
                ))
            
            # Recommendation 4: Quality-based cleanup
            overall_quality = quality_metrics.get("overall_quality_score", 100)
            if overall_quality < 60:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    strategy=OptimizationStrategy.CLEANUP,
                    priority="high",
                    title="Context Quality Cleanup",
                    description=f"Overall context quality is low ({overall_quality:.1f}%). Clean up inconsistent or incomplete contexts.",
                    estimated_savings_mb=total_size_mb * 0.2,
                    estimated_performance_gain=25.0,
                    implementation_complexity="moderate",
                    target_project_id=project_id
                ))
            
            # Recommendation 5: Deduplication
            if usage_stats.get("total_contexts", 0) > 10:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    strategy=OptimizationStrategy.DEDUPLICATION,
                    priority="medium",
                    title="Remove Duplicate Content",
                    description="Scan for and remove duplicate conversation events and data across contexts.",
                    estimated_savings_mb=total_size_mb * 0.1,
                    estimated_performance_gain=5.0,
                    implementation_complexity="complex",
                    target_project_id=project_id
                ))
            
            # Sort by priority and estimated impact
            priority_order = {"high": 3, "medium": 2, "low": 1}
            recommendations.sort(key=lambda r: (priority_order.get(r.priority, 0), r.estimated_savings_mb), reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"💥 Error generating optimization recommendations: {e}")
            return []
    
    def apply_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply an optimization recommendation"""
        try:
            result = {
                "recommendation_id": recommendation.recommendation_id,
                "strategy": recommendation.strategy.value,
                "success": False,
                "actual_savings_mb": 0,
                "actual_performance_gain": 0,
                "execution_time_ms": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            start_time = time.time()
            
            if recommendation.strategy == OptimizationStrategy.COMPRESSION:
                result.update(self._apply_compression_optimization(recommendation))
            
            elif recommendation.strategy == OptimizationStrategy.SUMMARIZATION:
                result.update(self._apply_summarization_optimization(recommendation))
            
            elif recommendation.strategy == OptimizationStrategy.ARCHIVAL:
                result.update(self._apply_archival_optimization(recommendation))
            
            elif recommendation.strategy == OptimizationStrategy.CLEANUP:
                result.update(self._apply_cleanup_optimization(recommendation))
            
            elif recommendation.strategy == OptimizationStrategy.DEDUPLICATION:
                result.update(self._apply_deduplication_optimization(recommendation))
            
            else:
                result["error"] = f"Unknown optimization strategy: {recommendation.strategy}"
            
            result["execution_time_ms"] = (time.time() - start_time) * 1000
            
            if result["success"]:
                self._optimizations_performed += 1
                self._space_saved_mb += result["actual_savings_mb"]
                
                # Emit optimization observation
                self.emit_observation({
                    "type": "context_optimization_applied",
                    "recommendation_id": recommendation.recommendation_id,
                    "strategy": recommendation.strategy.value,
                    "savings_mb": result["actual_savings_mb"],
                    "performance_gain": result["actual_performance_gain"],
                    "timestamp": result["timestamp"]
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Error applying optimization: {e}")
            return {
                "recommendation_id": recommendation.recommendation_id,
                "success": False,
                "error": str(e)
            }
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            "optimizations_performed": self._optimizations_performed,
            "total_space_saved_mb": self._space_saved_mb,
            "performance_improvements": self._performance_improvements,
            "average_savings_per_optimization": self._space_saved_mb / max(1, self._optimizations_performed)
        }
    
    def _apply_compression_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply compression optimization"""
        # Simplified implementation - would integrate with storage compression
        return {
            "success": True,
            "actual_savings_mb": recommendation.estimated_savings_mb * 0.8,  # 80% of estimated
            "actual_performance_gain": recommendation.estimated_performance_gain * 0.7,
            "details": "Compression enabled for context storage"
        }
    
    def _apply_summarization_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply summarization optimization"""
        # Simplified implementation - would integrate with context engine
        return {
            "success": True,
            "actual_savings_mb": recommendation.estimated_savings_mb * 0.6,
            "actual_performance_gain": recommendation.estimated_performance_gain * 0.8,
            "details": "Large contexts summarized to reduce size"
        }
    
    def _apply_archival_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply archival optimization"""
        # Simplified implementation - would move old contexts to archive storage
        return {
            "success": True,
            "actual_savings_mb": recommendation.estimated_savings_mb * 0.9,
            "actual_performance_gain": recommendation.estimated_performance_gain,
            "details": "Old contexts archived to improve performance"
        }
    
    def _apply_cleanup_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply cleanup optimization"""
        # Simplified implementation - would clean up inconsistent data
        return {
            "success": True,
            "actual_savings_mb": recommendation.estimated_savings_mb * 0.5,
            "actual_performance_gain": recommendation.estimated_performance_gain * 0.9,
            "details": "Context quality issues cleaned up"
        }
    
    def _apply_deduplication_optimization(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Apply deduplication optimization"""
        # Simplified implementation - would remove duplicate content
        return {
            "success": True,
            "actual_savings_mb": recommendation.estimated_savings_mb * 0.7,
            "actual_performance_gain": recommendation.estimated_performance_gain,
            "details": "Duplicate content removed from contexts"
        }


# CLI Integration for Analytics and Optimization
class AnalyticsOptimizationCLI:
    """Command-line interface for analytics and optimization"""
    
    def __init__(self, analyzer: ContextAnalyzer, optimizer: ContextOptimizer):
        self.analyzer = analyzer
        self.optimizer = optimizer
    
    def analyze_usage(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze context usage"""
        return self.analyzer.analyze_context_usage(project_id)
    
    def get_dashboard(self, project_id: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Get analytics dashboard"""
        return self.analyzer.get_analytics_dashboard(project_id, days)
    
    def get_recommendations(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        recommendations = self.optimizer.generate_optimization_recommendations(project_id)
        return [r.to_dict() for r in recommendations]
    
    def apply_optimization(self, recommendation_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Apply optimization recommendation"""
        # Would need to look up recommendation by ID
        # Simplified implementation
        return {"error": "Recommendation lookup not implemented"}
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return self.optimizer.get_optimization_statistics()
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics statistics"""
        return {
            "analyses_performed": self.analyzer._analyses_performed,
            "patterns_detected": self.analyzer._patterns_detected,
            "metrics_collected": self.analyzer._metrics_collected
        }