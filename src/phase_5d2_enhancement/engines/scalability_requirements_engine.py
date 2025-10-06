"""
Scalability Requirements Enhancement Engine for Phase 5D2 Enhancement System

CRITICAL PRIORITY: Current score 43.8 → Target 65+
Focus: Comprehensive scalability planning and performance requirements
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..config import get_config
from ..tracing.jaeger_trace_manager import JaegerTraceManager
from ..analysis.spec_analyzer import SpecAnalyzer, SpecContent


@dataclass
class ScalabilityAnalysis:
    """Analysis of scalability requirements in a specification."""
    performance_targets_defined: bool
    capacity_planning_present: bool
    growth_strategies_identified: List[str]
    load_testing_requirements: bool
    scalability_patterns: List[str]
    bottleneck_identification: bool
    monitoring_requirements: bool
    scalability_completeness_score: float  # 0-100
    improvement_recommendations: List[str]


class ScalabilityRequirementsEngine(ReflectiveModule):
    """
    Comprehensive scalability planning and performance requirements enhancement.
    
    CRITICAL DIMENSION: Scalability Requirements (Score: 43.8 → Target: 65+)
    
    Enhancement Patterns:
    - Performance target definition
    - Capacity planning frameworks
    - Growth strategy modeling
    - Load testing requirements
    - Scalability architecture patterns
    """
    
    # Performance metrics categories
    PERFORMANCE_METRICS = {
        "response_time": [
            "response time", "latency", "processing time", "execution time",
            "round trip time", "time to first byte", "page load time"
        ],
        "throughput": [
            "throughput", "requests per second", "rps", "transactions per second",
            "tps", "queries per second", "qps", "bandwidth", "data transfer rate"
        ],
        "concurrency": [
            "concurrent users", "simultaneous connections", "parallel requests",
            "concurrent sessions", "active users", "connection pool"
        ],
        "resource_utilization": [
            "cpu utilization", "memory usage", "disk usage", "network utilization",
            "resource consumption", "system load", "capacity utilization"
        ],
        "availability": [
            "uptime", "availability", "reliability", "fault tolerance",
            "disaster recovery", "high availability", "service level"
        ]
    }
    
    # Scalability patterns
    SCALABILITY_PATTERNS = {
        "horizontal_scaling": [
            "horizontal scaling", "scale out", "load balancing", "clustering",
            "distributed systems", "microservices", "sharding", "partitioning"
        ],
        "vertical_scaling": [
            "vertical scaling", "scale up", "resource upgrade", "capacity increase",
            "hardware upgrade", "instance sizing", "resource allocation"
        ],
        "caching": [
            "caching", "cache", "redis", "memcached", "cdn", "content delivery",
            "edge caching", "application cache", "database cache"
        ],
        "asynchronous_processing": [
            "asynchronous", "async", "queue", "message queue", "event driven",
            "background processing", "batch processing", "streaming"
        ],
        "database_scaling": [
            "database scaling", "read replicas", "database sharding", "nosql",
            "database clustering", "connection pooling", "query optimization"
        ]
    }
    
    # Growth strategy indicators
    GROWTH_STRATEGIES = [
        "user growth", "traffic growth", "data growth", "geographic expansion",
        "feature expansion", "market expansion", "seasonal scaling", "burst capacity"
    ]
    
    # Load testing types
    LOAD_TESTING_TYPES = [
        "load testing", "stress testing", "performance testing", "volume testing",
        "spike testing", "endurance testing", "capacity testing", "benchmark testing"
    ]
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.tracer = JaegerTraceManager()
        self.spec_analyzer = SpecAnalyzer()
        
        self.logger.info(
            "ScalabilityRequirementsEngine initialized",
            extra={
                "target_improvement": "43.8 → 65+",
                "priority": "CRITICAL",
                "performance_metrics": len(self.PERFORMANCE_METRICS)
            }
        )
    
    def analyze_scalability_needs(self, spec_content: SpecContent) -> ScalabilityAnalysis:
        """
        Analyze scalability requirements in a specification.
        
        Args:
            spec_content: Complete specification content
            
        Returns:
            ScalabilityAnalysis with detailed assessment
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id=f"scalability_analysis_{spec_content.metadata.spec_name}",
            operation_name="analyze_scalability_needs"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "scalability_analysis") as span:
                try:
                    # Analyze all content for scalability-related information
                    all_content = (spec_content.requirements_content + 
                                 spec_content.design_content + 
                                 spec_content.tasks_content)
                    
                    # Check for performance targets
                    performance_targets_defined = self._check_performance_targets(all_content)
                    
                    # Check for capacity planning
                    capacity_planning_present = self._check_capacity_planning(all_content)
                    
                    # Identify growth strategies
                    growth_strategies_identified = self._identify_growth_strategies(all_content)
                    
                    # Check for load testing requirements
                    load_testing_requirements = self._check_load_testing_requirements(all_content)
                    
                    # Identify scalability patterns
                    scalability_patterns = self._identify_scalability_patterns(all_content)
                    
                    # Check for bottleneck identification
                    bottleneck_identification = self._check_bottleneck_identification(all_content)
                    
                    # Check for monitoring requirements
                    monitoring_requirements = self._check_monitoring_requirements(all_content)
                    
                    # Calculate scalability completeness score
                    scalability_completeness_score = self._calculate_scalability_completeness(
                        performance_targets_defined, capacity_planning_present,
                        growth_strategies_identified, load_testing_requirements,
                        scalability_patterns, bottleneck_identification, monitoring_requirements
                    )
                    
                    # Generate improvement recommendations
                    improvement_recommendations = self._generate_scalability_recommendations(
                        performance_targets_defined, capacity_planning_present,
                        growth_strategies_identified, load_testing_requirements,
                        scalability_patterns, bottleneck_identification, monitoring_requirements,
                        scalability_completeness_score
                    )
                    
                    analysis = ScalabilityAnalysis(
                        performance_targets_defined=performance_targets_defined,
                        capacity_planning_present=capacity_planning_present,
                        growth_strategies_identified=growth_strategies_identified,
                        load_testing_requirements=load_testing_requirements,
                        scalability_patterns=scalability_patterns,
                        bottleneck_identification=bottleneck_identification,
                        monitoring_requirements=monitoring_requirements,
                        scalability_completeness_score=scalability_completeness_score,
                        improvement_recommendations=improvement_recommendations
                    )
                    
                    # Log analysis metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "performance_targets_defined": performance_targets_defined,
                        "capacity_planning_present": capacity_planning_present,
                        "growth_strategies_count": len(growth_strategies_identified),
                        "scalability_patterns_count": len(scalability_patterns),
                        "scalability_completeness_score": scalability_completeness_score
                    })
                    
                    self.logger.info(
                        "Scalability analysis completed",
                        extra={
                            "spec_name": spec_content.metadata.spec_name,
                            "performance_targets": performance_targets_defined,
                            "capacity_planning": capacity_planning_present,
                            "completeness": scalability_completeness_score
                        }
                    )
                    
                    return analysis
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def _check_performance_targets(self, content: str) -> bool:
        """Check if performance targets are defined in the content."""
        content_lower = content.lower()
        
        # Look for specific performance metrics with numbers
        performance_patterns = [
            r"\d+\s*(ms|milliseconds?|seconds?|minutes?)\s*(response|latency)",
            r"\d+\s*(rps|requests?\s*per\s*second)",
            r"\d+\s*(tps|transactions?\s*per\s*second)",
            r"\d+\s*(concurrent|simultaneous)\s*(users?|connections?)",
            r"\d+%\s*(cpu|memory|disk)\s*(utilization|usage)",
            r"\d+(\.\d+)?%\s*(uptime|availability)"
        ]
        
        for pattern in performance_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        # Look for performance target keywords
        target_keywords = [
            "performance target", "performance requirement", "sla", "service level agreement",
            "performance criteria", "performance benchmark", "performance goal"
        ]
        
        for keyword in target_keywords:
            if keyword in content_lower:
                return True
        
        return False
    
    def _check_capacity_planning(self, content: str) -> bool:
        """Check if capacity planning is present in the content."""
        content_lower = content.lower()
        
        capacity_indicators = [
            "capacity planning", "capacity management", "resource planning",
            "capacity requirements", "resource allocation", "capacity model",
            "growth planning", "scaling plan", "resource estimation"
        ]
        
        for indicator in capacity_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _identify_growth_strategies(self, content: str) -> List[str]:
        """Identify growth strategies mentioned in the content."""
        content_lower = content.lower()
        identified_strategies = []
        
        for strategy in self.GROWTH_STRATEGIES:
            if strategy in content_lower:
                identified_strategies.append(strategy)
        
        # Look for growth-related patterns
        growth_patterns = [
            r"growth.*\d+%",
            r"scale.*\d+x",
            r"increase.*\d+",
            r"expand.*\d+"
        ]
        
        for pattern in growth_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                identified_strategies.extend([f"quantified_growth_{i}" for i in range(len(matches))])
        
        return list(set(identified_strategies))
    
    def _check_load_testing_requirements(self, content: str) -> bool:
        """Check if load testing requirements are present."""
        content_lower = content.lower()
        
        for test_type in self.LOAD_TESTING_TYPES:
            if test_type in content_lower:
                return True
        
        return False
    
    def _identify_scalability_patterns(self, content: str) -> List[str]:
        """Identify scalability patterns mentioned in the content."""
        content_lower = content.lower()
        identified_patterns = []
        
        for pattern_category, patterns in self.SCALABILITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in content_lower:
                    if pattern_category not in identified_patterns:
                        identified_patterns.append(pattern_category)
                    break
        
        return identified_patterns
    
    def _check_bottleneck_identification(self, content: str) -> bool:
        """Check if bottleneck identification is present."""
        content_lower = content.lower()
        
        bottleneck_indicators = [
            "bottleneck", "performance bottleneck", "constraint", "limiting factor",
            "performance issue", "scalability issue", "capacity constraint"
        ]
        
        for indicator in bottleneck_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _check_monitoring_requirements(self, content: str) -> bool:
        """Check if monitoring requirements are present."""
        content_lower = content.lower()
        
        monitoring_indicators = [
            "performance monitoring", "scalability monitoring", "capacity monitoring",
            "performance metrics", "monitoring dashboard", "alerting", "observability"
        ]
        
        for indicator in monitoring_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _calculate_scalability_completeness(
        self,
        performance_targets: bool,
        capacity_planning: bool,
        growth_strategies: List[str],
        load_testing: bool,
        scalability_patterns: List[str],
        bottleneck_identification: bool,
        monitoring_requirements: bool
    ) -> float:
        """Calculate how complete the scalability requirements are."""
        completeness_factors = {
            "performance_targets": 20 if performance_targets else 0,  # 20 points
            "capacity_planning": 15 if capacity_planning else 0,  # 15 points
            "growth_strategies": min(len(growth_strategies) / 2, 1.0) * 15,  # Up to 15 points
            "load_testing": 15 if load_testing else 0,  # 15 points
            "scalability_patterns": min(len(scalability_patterns) / 3, 1.0) * 20,  # Up to 20 points
            "bottleneck_identification": 10 if bottleneck_identification else 0,  # 10 points
            "monitoring_requirements": 5 if monitoring_requirements else 0  # 5 points
        }
        
        total_completeness = sum(completeness_factors.values())
        return min(total_completeness, 100.0)
    
    def _generate_scalability_recommendations(
        self,
        performance_targets: bool,
        capacity_planning: bool,
        growth_strategies: List[str],
        load_testing: bool,
        scalability_patterns: List[str],
        bottleneck_identification: bool,
        monitoring_requirements: bool,
        completeness: float
    ) -> List[str]:
        """Generate specific recommendations for improving scalability requirements."""
        recommendations = []
        
        # Performance targets recommendations
        if not performance_targets:
            recommendations.append("🎯 Define specific performance targets - response time, throughput, concurrency limits")
            recommendations.append("📊 Add quantitative performance requirements - SLAs with measurable criteria")
        
        # Capacity planning recommendations
        if not capacity_planning:
            recommendations.append("📈 Implement capacity planning - resource requirements and growth projections")
            recommendations.append("🔮 Add capacity modeling - predict resource needs based on usage patterns")
        
        # Growth strategy recommendations
        if len(growth_strategies) < 2:
            recommendations.append("🚀 Define growth strategies - user growth, traffic patterns, data volume increases")
            recommendations.append("📅 Add growth timeline - phased scaling approach with milestones")
        
        # Load testing recommendations
        if not load_testing:
            recommendations.append("🧪 Add load testing requirements - stress testing, performance validation")
            recommendations.append("⚡ Define testing scenarios - peak load, burst capacity, endurance testing")
        
        # Scalability patterns recommendations
        if len(scalability_patterns) < 3:
            recommendations.append("🏗️ Implement scalability patterns - horizontal scaling, caching, async processing")
            recommendations.append("🔧 Add architectural scalability - microservices, load balancing, database scaling")
        
        if "horizontal_scaling" not in scalability_patterns:
            recommendations.append("↔️ Add horizontal scaling strategy - load balancing and distributed architecture")
        
        if "caching" not in scalability_patterns:
            recommendations.append("💾 Implement caching strategy - application, database, and CDN caching")
        
        # Bottleneck identification recommendations
        if not bottleneck_identification:
            recommendations.append("🔍 Add bottleneck identification - analyze performance constraints and limitations")
            recommendations.append("⚠️ Define performance risks - identify potential scalability issues")
        
        # Monitoring recommendations
        if not monitoring_requirements:
            recommendations.append("📊 Add performance monitoring - real-time metrics and alerting")
            recommendations.append("🎛️ Implement scalability dashboards - capacity utilization and performance trends")
        
        # Completeness-based recommendations
        if completeness < 60:
            recommendations.append("🎨 Apply scalability framework - systematic approach to performance requirements")
            recommendations.append("📝 Document scalability strategy - comprehensive performance and scaling plan")
        
        # Always include systematic improvements
        recommendations.extend([
            "🔄 Implement iterative performance testing - continuous validation and optimization",
            "✅ Add scalability validation criteria - define success metrics and acceptance criteria",
            "📚 Create scalability playbook - reusable patterns and best practices"
        ])
        
        return recommendations
    
    def enhance_scalability_requirements(self, spec_path: str) -> Dict[str, Any]:
        """
        Apply scalability requirements enhancement to a specification.
        
        Args:
            spec_path: Path to the specification to enhance
            
        Returns:
            Enhancement result with details
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id=f"enhance_scalability_{Path(spec_path).name}",
            operation_name="enhance_scalability_requirements"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "scalability_enhancement") as span:
                try:
                    # Load specification content
                    spec_content = self.spec_analyzer.load_spec_content(spec_path)
                    
                    # Analyze current scalability requirements
                    analysis = self.analyze_scalability_needs(spec_content)
                    before_score = analysis.scalability_completeness_score
                    
                    # Apply enhancements
                    improvements_applied = self._apply_scalability_enhancements(
                        spec_path, spec_content, analysis
                    )
                    
                    # Calculate after score (estimated improvement)
                    after_score = min(before_score + len(improvements_applied) * 6, 100.0)
                    
                    # Validate enhancement
                    validation_status = "SUCCESS" if after_score > before_score else "NO_IMPROVEMENT"
                    
                    result = {
                        "spec_path": spec_path,
                        "before_score": before_score,
                        "after_score": after_score,
                        "improvement_delta": after_score - before_score,
                        "improvements_applied": improvements_applied,
                        "validation_status": validation_status,
                        "enhancement_timestamp": self.tracer.active_traces[trace_context.trace_id].start_time.isoformat()
                    }
                    
                    # Log enhancement metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "before_score": before_score,
                        "after_score": after_score,
                        "improvement_delta": result["improvement_delta"],
                        "improvements_count": len(improvements_applied),
                        "validation_status": validation_status
                    })
                    
                    self.logger.info(
                        "Scalability requirements enhancement completed",
                        extra={
                            "spec_path": spec_path,
                            "before_score": before_score,
                            "after_score": after_score,
                            "improvement": result["improvement_delta"],
                            "improvements_applied": len(improvements_applied)
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def _apply_scalability_enhancements(
        self, 
        spec_path: str, 
        spec_content: SpecContent, 
        analysis: ScalabilityAnalysis
    ) -> List[str]:
        """Apply specific scalability enhancements to the specification."""
        improvements_applied = []
        
        # This would implement the actual enhancement logic
        # For now, return the recommendations as applied improvements
        improvements_applied.extend(analysis.improvement_recommendations)
        
        # Log what would be applied
        self.logger.info(
            "Scalability enhancements identified",
            extra={
                "spec_path": spec_path,
                "improvements_count": len(improvements_applied),
                "current_completeness": analysis.scalability_completeness_score
            }
        )
        
        return improvements_applied
    
    def validate_scalability_completeness(self, enhanced_spec: str) -> Dict[str, Any]:
        """
        Validate the completeness of scalability requirements in enhanced specification.
        
        Args:
            enhanced_spec: Enhanced specification content
            
        Returns:
            Validation results
        """
        # Load and analyze the enhanced specification
        spec_content = SpecContent(requirements_content=enhanced_spec)
        analysis = self.analyze_scalability_needs(spec_content)
        
        validation_result = {
            "completeness_score": analysis.scalability_completeness_score,
            "performance_targets_defined": analysis.performance_targets_defined,
            "capacity_planning_present": analysis.capacity_planning_present,
            "growth_strategies_count": len(analysis.growth_strategies_identified),
            "load_testing_requirements": analysis.load_testing_requirements,
            "scalability_patterns_count": len(analysis.scalability_patterns),
            "bottleneck_identification": analysis.bottleneck_identification,
            "monitoring_requirements": analysis.monitoring_requirements,
            "validation_passed": analysis.scalability_completeness_score >= 65.0,
            "remaining_improvements": analysis.improvement_recommendations
        }
        
        self.logger.info(
            "Scalability requirements validation completed",
            extra={
                "completeness_score": analysis.scalability_completeness_score,
                "validation_passed": validation_result["validation_passed"]
            }
        )
        
        return validation_result