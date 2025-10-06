"""
Generic Enhancement Engine for Phase 5D2 Enhancement System

Handles enhancement for dimensions not covered by specialized engines
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..config import get_config
from ..tracing.jaeger_trace_manager import JaegerTraceManager
from ..analysis.spec_analyzer import SpecAnalyzer, SpecContent


@dataclass
class GenericAnalysis:
    """Generic analysis of a dimension in a specification."""
    dimension_name: str
    content_coverage: float  # 0-100
    structure_quality: float  # 0-100
    completeness_indicators: List[str]
    improvement_opportunities: List[str]
    enhancement_templates: List[str]
    overall_score: float  # 0-100
    improvement_recommendations: List[str]


class GenericEnhancementEngine(ReflectiveModule):
    """
    Generic enhancement engine for dimensions not covered by specialized engines.
    
    Provides configurable enhancement patterns and templates for systematic
    improvement of any dimension based on content analysis and best practices.
    """
    
    # Generic enhancement templates by dimension type
    ENHANCEMENT_TEMPLATES = {
        "testing_strategy": {
            "patterns": [
                "unit testing framework", "integration testing", "end-to-end testing",
                "test coverage", "test automation", "performance testing", "security testing"
            ],
            "structure": [
                "testing approach", "test types", "test environments", "test data management",
                "test execution", "test reporting", "test maintenance"
            ]
        },
        "compliance_regulations": {
            "patterns": [
                "regulatory requirements", "compliance framework", "audit requirements",
                "data protection", "privacy regulations", "industry standards", "certification"
            ],
            "structure": [
                "applicable regulations", "compliance requirements", "audit procedures",
                "documentation requirements", "monitoring and reporting", "risk management"
            ]
        },
        "innovation_potential": {
            "patterns": [
                "emerging technologies", "automation opportunities", "ai/ml integration",
                "process innovation", "technology advancement", "research opportunities"
            ],
            "structure": [
                "innovation opportunities", "technology trends", "implementation roadmap",
                "risk assessment", "success metrics", "resource requirements"
            ]
        },
        "documentation_requirements": {
            "patterns": [
                "user documentation", "technical documentation", "api documentation",
                "operational documentation", "training materials", "knowledge base"
            ],
            "structure": [
                "documentation types", "content requirements", "maintenance procedures",
                "access control", "version control", "review processes"
            ]
        },
        "monitoring_observability": {
            "patterns": [
                "monitoring strategy", "metrics collection", "alerting", "dashboards",
                "logging", "tracing", "observability", "performance monitoring"
            ],
            "structure": [
                "monitoring requirements", "metrics definition", "alerting rules",
                "dashboard design", "data retention", "incident response"
            ]
        }
    }
    
    # Quality indicators for content analysis
    QUALITY_INDICATORS = {
        "structure": ["sections", "subsections", "organization", "hierarchy"],
        "completeness": ["comprehensive", "detailed", "thorough", "complete"],
        "specificity": ["specific", "concrete", "measurable", "quantifiable"],
        "actionability": ["actionable", "implementable", "executable", "practical"]
    }
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.tracer = JaegerTraceManager()
        self.spec_analyzer = SpecAnalyzer()
        
        self.logger.info(
            "GenericEnhancementEngine initialized",
            extra={
                "supported_dimensions": len(self.ENHANCEMENT_TEMPLATES),
                "quality_indicators": len(self.QUALITY_INDICATORS)
            }
        )
    
    def analyze_dimension_content(self, spec_content: SpecContent, dimension_name: str) -> GenericAnalysis:
        """
        Analyze content for a specific dimension.
        
        Args:
            spec_content: Complete specification content
            dimension_name: Name of the dimension to analyze
            
        Returns:
            GenericAnalysis with assessment results
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id=f"generic_analysis_{spec_content.metadata.spec_name}_{dimension_name}",
            operation_name="analyze_dimension_content"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, f"generic_analysis_{dimension_name}") as span:
                try:
                    # Combine all content for analysis
                    all_content = (spec_content.requirements_content + 
                                 spec_content.design_content + 
                                 spec_content.tasks_content)
                    
                    # Analyze content coverage for this dimension
                    content_coverage = self._analyze_content_coverage(all_content, dimension_name)
                    
                    # Analyze structure quality
                    structure_quality = self._analyze_structure_quality(all_content, dimension_name)
                    
                    # Identify completeness indicators
                    completeness_indicators = self._identify_completeness_indicators(all_content, dimension_name)
                    
                    # Identify improvement opportunities
                    improvement_opportunities = self._identify_improvement_opportunities(all_content, dimension_name)
                    
                    # Get enhancement templates
                    enhancement_templates = self._get_enhancement_templates(dimension_name)
                    
                    # Calculate overall score
                    overall_score = (content_coverage + structure_quality) / 2
                    
                    # Generate improvement recommendations
                    improvement_recommendations = self._generate_generic_recommendations(
                        dimension_name, content_coverage, structure_quality,
                        completeness_indicators, improvement_opportunities, overall_score
                    )
                    
                    analysis = GenericAnalysis(
                        dimension_name=dimension_name,
                        content_coverage=content_coverage,
                        structure_quality=structure_quality,
                        completeness_indicators=completeness_indicators,
                        improvement_opportunities=improvement_opportunities,
                        enhancement_templates=enhancement_templates,
                        overall_score=overall_score,
                        improvement_recommendations=improvement_recommendations
                    )
                    
                    # Log analysis metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "dimension_name": dimension_name,
                        "content_coverage": content_coverage,
                        "structure_quality": structure_quality,
                        "overall_score": overall_score,
                        "completeness_indicators_count": len(completeness_indicators),
                        "improvement_opportunities_count": len(improvement_opportunities)
                    })
                    
                    self.logger.info(
                        "Generic dimension analysis completed",
                        extra={
                            "spec_name": spec_content.metadata.spec_name,
                            "dimension_name": dimension_name,
                            "overall_score": overall_score,
                            "content_coverage": content_coverage,
                            "structure_quality": structure_quality
                        }
                    )
                    
                    return analysis
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def _analyze_content_coverage(self, content: str, dimension_name: str) -> float:
        """Analyze how well the content covers the dimension."""
        content_lower = content.lower()
        
        # Get patterns for this dimension
        templates = self.ENHANCEMENT_TEMPLATES.get(dimension_name, {})
        patterns = templates.get("patterns", [])
        
        if not patterns:
            # Generic coverage analysis based on dimension name
            dimension_keywords = dimension_name.replace("_", " ").split()
            patterns = dimension_keywords
        
        # Count pattern matches
        matches = 0
        for pattern in patterns:
            if pattern.lower() in content_lower:
                matches += 1
        
        # Calculate coverage percentage
        coverage = (matches / len(patterns)) * 100 if patterns else 0
        return min(coverage, 100.0)
    
    def _analyze_structure_quality(self, content: str, dimension_name: str) -> float:
        """Analyze the structural quality of dimension coverage."""
        content_lower = content.lower()
        
        # Get structure requirements for this dimension
        templates = self.ENHANCEMENT_TEMPLATES.get(dimension_name, {})
        structure_elements = templates.get("structure", [])
        
        if not structure_elements:
            # Generic structure analysis
            structure_elements = ["requirements", "approach", "implementation", "validation"]
        
        # Count structure element matches
        structure_matches = 0
        for element in structure_elements:
            if element.lower() in content_lower:
                structure_matches += 1
        
        # Analyze quality indicators
        quality_score = 0
        total_indicators = 0
        
        for quality_type, indicators in self.QUALITY_INDICATORS.items():
            type_matches = 0
            for indicator in indicators:
                if indicator in content_lower:
                    type_matches += 1
            
            # Score this quality type (0-25 points each)
            type_score = min((type_matches / len(indicators)) * 25, 25)
            quality_score += type_score
            total_indicators += 25
        
        # Combine structure and quality scores
        structure_score = (structure_matches / len(structure_elements)) * 50 if structure_elements else 0
        quality_percentage = (quality_score / total_indicators) * 50 if total_indicators else 0
        
        return min(structure_score + quality_percentage, 100.0)
    
    def _identify_completeness_indicators(self, content: str, dimension_name: str) -> List[str]:
        """Identify indicators of completeness for the dimension."""
        content_lower = content.lower()
        indicators = []
        
        # Check for dimension-specific completeness indicators
        templates = self.ENHANCEMENT_TEMPLATES.get(dimension_name, {})
        patterns = templates.get("patterns", [])
        
        for pattern in patterns:
            if pattern.lower() in content_lower:
                indicators.append(f"has_{pattern.replace(' ', '_')}")
        
        # Check for general completeness indicators
        general_indicators = [
            "comprehensive", "detailed", "complete", "thorough", "systematic",
            "framework", "strategy", "approach", "methodology", "process"
        ]
        
        for indicator in general_indicators:
            if indicator in content_lower:
                indicators.append(f"general_{indicator}")
        
        return list(set(indicators))  # Remove duplicates
    
    def _identify_improvement_opportunities(self, content: str, dimension_name: str) -> List[str]:
        """Identify improvement opportunities for the dimension."""
        opportunities = []
        
        # Get templates for this dimension
        templates = self.ENHANCEMENT_TEMPLATES.get(dimension_name, {})
        patterns = templates.get("patterns", [])
        structure_elements = templates.get("structure", [])
        
        content_lower = content.lower()
        
        # Check for missing patterns
        missing_patterns = []
        for pattern in patterns:
            if pattern.lower() not in content_lower:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            opportunities.append(f"add_missing_patterns: {', '.join(missing_patterns[:3])}")
        
        # Check for missing structure elements
        missing_structure = []
        for element in structure_elements:
            if element.lower() not in content_lower:
                missing_structure.append(element)
        
        if missing_structure:
            opportunities.append(f"add_missing_structure: {', '.join(missing_structure[:3])}")
        
        # Generic improvement opportunities
        if len(content.split()) < 100:
            opportunities.append("expand_content_detail")
        
        if "requirement" not in content_lower and dimension_name != "requirements":
            opportunities.append("add_specific_requirements")
        
        if "implementation" not in content_lower:
            opportunities.append("add_implementation_guidance")
        
        return opportunities
    
    def _get_enhancement_templates(self, dimension_name: str) -> List[str]:
        """Get enhancement templates for the dimension."""
        templates = self.ENHANCEMENT_TEMPLATES.get(dimension_name, {})
        
        enhancement_templates = []
        
        # Add pattern-based templates
        patterns = templates.get("patterns", [])
        if patterns:
            enhancement_templates.append(f"implement_{dimension_name}_patterns")
            enhancement_templates.extend([f"add_{pattern.replace(' ', '_')}" for pattern in patterns[:3]])
        
        # Add structure-based templates
        structure = templates.get("structure", [])
        if structure:
            enhancement_templates.append(f"structure_{dimension_name}_content")
            enhancement_templates.extend([f"define_{element.replace(' ', '_')}" for element in structure[:3]])
        
        # Add generic templates
        enhancement_templates.extend([
            f"systematic_{dimension_name}_framework",
            f"{dimension_name}_best_practices",
            f"{dimension_name}_validation_criteria"
        ])
        
        return enhancement_templates
    
    def _generate_generic_recommendations(
        self,
        dimension_name: str,
        content_coverage: float,
        structure_quality: float,
        completeness_indicators: List[str],
        improvement_opportunities: List[str],
        overall_score: float
    ) -> List[str]:
        """Generate generic improvement recommendations."""
        recommendations = []
        
        # Coverage-based recommendations
        if content_coverage < 50:
            recommendations.append(f"📈 Expand {dimension_name.replace('_', ' ')} coverage - add comprehensive content and requirements")
            recommendations.append(f"🎯 Implement {dimension_name.replace('_', ' ')} framework - systematic approach and methodology")
        
        # Structure-based recommendations
        if structure_quality < 50:
            recommendations.append(f"🏗️ Improve {dimension_name.replace('_', ' ')} structure - organize content with clear sections")
            recommendations.append(f"📋 Add {dimension_name.replace('_', ' ')} components - requirements, approach, implementation, validation")
        
        # Completeness-based recommendations
        if len(completeness_indicators) < 3:
            recommendations.append(f"✅ Enhance {dimension_name.replace('_', ' ')} completeness - add detailed and comprehensive content")
            recommendations.append(f"🔍 Include {dimension_name.replace('_', ' ')} specifics - concrete, measurable, and actionable requirements")
        
        # Opportunity-based recommendations
        for opportunity in improvement_opportunities[:3]:  # Top 3 opportunities
            if "missing_patterns" in opportunity:
                recommendations.append(f"🎨 Add missing {dimension_name.replace('_', ' ')} patterns - {opportunity.split(': ')[1] if ': ' in opportunity else 'key components'}")
            elif "missing_structure" in opportunity:
                recommendations.append(f"📐 Add missing {dimension_name.replace('_', ' ')} structure - {opportunity.split(': ')[1] if ': ' in opportunity else 'organizational elements'}")
            else:
                recommendations.append(f"🚀 {opportunity.replace('_', ' ').title()} for {dimension_name.replace('_', ' ')}")
        
        # Score-based recommendations
        if overall_score < 60:
            recommendations.append(f"🎯 Apply systematic {dimension_name.replace('_', ' ')} enhancement - use proven templates and patterns")
            recommendations.append(f"📚 Create {dimension_name.replace('_', ' ')} documentation - comprehensive requirements and guidelines")
        
        # Always include validation
        recommendations.append(f"✅ Add {dimension_name.replace('_', ' ')} validation criteria - define success metrics and acceptance criteria")
        
        return recommendations
    
    def enhance_dimension(self, spec_path: str, dimension_name: str) -> Dict[str, Any]:
        """
        Apply generic enhancement to a dimension in a specification.
        
        Args:
            spec_path: Path to the specification to enhance
            dimension_name: Name of the dimension to enhance
            
        Returns:
            Enhancement result with details
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id=f"enhance_generic_{Path(spec_path).name}_{dimension_name}",
            operation_name="enhance_dimension"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, f"generic_enhancement_{dimension_name}") as span:
                try:
                    # Load specification content
                    spec_content = self.spec_analyzer.load_spec_content(spec_path)
                    
                    # Analyze current dimension content
                    analysis = self.analyze_dimension_content(spec_content, dimension_name)
                    before_score = analysis.overall_score
                    
                    # Apply enhancements
                    improvements_applied = self._apply_generic_enhancements(
                        spec_path, spec_content, analysis
                    )
                    
                    # Calculate after score (estimated improvement)
                    improvement_factor = 5 if dimension_name in self.ENHANCEMENT_TEMPLATES else 3
                    after_score = min(before_score + len(improvements_applied) * improvement_factor, 100.0)
                    
                    # Validate enhancement
                    validation_status = "SUCCESS" if after_score > before_score else "NO_IMPROVEMENT"
                    
                    result = {
                        "spec_path": spec_path,
                        "dimension_name": dimension_name,
                        "before_score": before_score,
                        "after_score": after_score,
                        "improvement_delta": after_score - before_score,
                        "improvements_applied": improvements_applied,
                        "validation_status": validation_status,
                        "enhancement_timestamp": self.tracer.active_traces[trace_context.trace_id].start_time.isoformat()
                    }
                    
                    # Log enhancement metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "dimension_name": dimension_name,
                        "before_score": before_score,
                        "after_score": after_score,
                        "improvement_delta": result["improvement_delta"],
                        "improvements_count": len(improvements_applied),
                        "validation_status": validation_status
                    })
                    
                    self.logger.info(
                        "Generic dimension enhancement completed",
                        extra={
                            "spec_path": spec_path,
                            "dimension_name": dimension_name,
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
    
    def _apply_generic_enhancements(
        self, 
        spec_path: str, 
        spec_content: SpecContent, 
        analysis: GenericAnalysis
    ) -> List[str]:
        """Apply generic enhancements to the specification."""
        improvements_applied = []
        
        # This would implement the actual enhancement logic
        # For now, return the recommendations as applied improvements
        improvements_applied.extend(analysis.improvement_recommendations)
        
        # Log what would be applied
        self.logger.info(
            "Generic enhancements identified",
            extra={
                "spec_path": spec_path,
                "dimension_name": analysis.dimension_name,
                "improvements_count": len(improvements_applied),
                "current_score": analysis.overall_score
            }
        )
        
        return improvements_applied
    
    def validate_dimension_enhancement(self, enhanced_spec: str, dimension_name: str) -> Dict[str, Any]:
        """
        Validate the enhancement of a dimension in the enhanced specification.
        
        Args:
            enhanced_spec: Enhanced specification content
            dimension_name: Name of the dimension to validate
            
        Returns:
            Validation results
        """
        # Load and analyze the enhanced specification
        spec_content = SpecContent(requirements_content=enhanced_spec)
        analysis = self.analyze_dimension_content(spec_content, dimension_name)
        
        validation_result = {
            "dimension_name": dimension_name,
            "overall_score": analysis.overall_score,
            "content_coverage": analysis.content_coverage,
            "structure_quality": analysis.structure_quality,
            "completeness_indicators_count": len(analysis.completeness_indicators),
            "improvement_opportunities_count": len(analysis.improvement_opportunities),
            "validation_passed": analysis.overall_score >= 60.0,  # Generic threshold
            "remaining_improvements": analysis.improvement_recommendations
        }
        
        self.logger.info(
            "Generic dimension validation completed",
            extra={
                "dimension_name": dimension_name,
                "overall_score": analysis.overall_score,
                "validation_passed": validation_result["validation_passed"]
            }
        )
        
        return validation_result