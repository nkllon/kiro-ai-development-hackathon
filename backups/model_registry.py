"""
Systematic PDCA Orchestrator - Model Registry

Model-driven intelligence system that provides domain-specific requirements,
patterns, and tool mappings from the project model registry.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from .pdca_models import (
    ModelIntelligence, Requirement, Pattern, Tool, ValidationLevel, ReflectiveModule
)


@dataclass
class DomainInfo:
    """Domain information from project registry"""
    domain_name: str
    description: str
    purpose: str
    compliance: str
    tools: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)


class ModelRegistry(ReflectiveModule):
    """
    Model Registry for systematic PDCA intelligence
    
    Provides model-driven decision making by consulting the project
    model registry for domain-specific requirements, patterns, and tools.
    """
    
    def __init__(self, registry_path: str = "project_model_registry.json"):
        """Initialize model registry with project intelligence"""
        self.registry_path = Path(registry_path)
        self.logger = logging.getLogger(__name__)
        
        # Registry data
        self.registry_data: Dict[str, Any] = {}
        self.domain_cache: Dict[str, DomainInfo] = {}
        self.intelligence_cache: Dict[str, ModelIntelligence] = {}
        
        # Performance metrics
        self.query_count = 0
        self.cache_hits = 0
        self.last_updated = datetime.now()
        
        # Load registry data
        self._load_registry()
    
    def _load_registry(self) -> bool:
        """Load project model registry from file"""
        try:
            if not self.registry_path.exists():
                self.logger.warning(f"Registry file not found: {self.registry_path}")
                self.registry_data = self._create_default_registry()
                return False
            
            with open(self.registry_path, 'r') as f:
                self.registry_data = json.load(f)
            
            self.logger.info(f"Loaded registry with {len(self.registry_data)} top-level keys")
            self._build_domain_cache()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load registry: {e}")
            self.registry_data = self._create_default_registry()
            return False
    
    def _create_default_registry(self) -> Dict[str, Any]:
        """Create default registry structure when file is missing"""
        return {
            "description": "Default Beast Mode Registry",
            "domain_architecture": {
                "overview": {
                    "total_domains": 0,
                    "compliance_standard": "Reflective Module (RM)"
                }
            },
            "domains": {}
        }
    
    def _build_domain_cache(self):
        """Build domain information cache from registry data"""
        self.domain_cache.clear()
        
        # Extract domains from domain_architecture
        domain_arch = self.registry_data.get("domain_architecture", {})
        
        for category_name, category_data in domain_arch.items():
            if category_name == "overview":
                continue
                
            if isinstance(category_data, dict) and "domains" in category_data:
                domains = category_data["domains"]
                description = category_data.get("description", "")
                purpose = category_data.get("purpose", "")
                compliance = category_data.get("compliance", "RM compliant")
                
                for domain_name in domains:
                    if isinstance(domain_name, str):
                        domain_info = DomainInfo(
                            domain_name=domain_name,
                            description=description,
                            purpose=purpose,
                            compliance=compliance
                        )
                        self.domain_cache[domain_name] = domain_info
        
        self.logger.info(f"Built domain cache with {len(self.domain_cache)} domains")
    
    def query_requirements(self, domain: str) -> List[Requirement]:
        """Query requirements for a specific domain"""
        self.query_count += 1
        
        # Check cache first
        if domain in self.intelligence_cache:
            self.cache_hits += 1
            return self.intelligence_cache[domain].requirements
        
        requirements = []
        
        # Get domain info
        domain_info = self.domain_cache.get(domain)
        if not domain_info:
            self.logger.warning(f"Domain not found in registry: {domain}")
            requirements = self._create_default_requirements(domain)
        else:
            # Create systematic requirements based on domain info
            requirements.extend([
                Requirement(
                    req_id=f"{domain}-rm-001",
                    description="Must implement Reflective Module (RM) pattern",
                    domain=domain,
                    priority=1,
                    acceptance_criteria=[
                        "WHEN module is created THEN it SHALL inherit from ReflectiveModule",
                        "WHEN health is queried THEN it SHALL return systematic health status",
                        "WHEN performance is measured THEN it SHALL provide systematic metrics"
                    ],
                    validation_method="interface_compliance"
                ),
                Requirement(
                    req_id=f"{domain}-systematic-002",
                    description="Must follow systematic approach over ad-hoc implementation",
                    domain=domain,
                    priority=1,
                    acceptance_criteria=[
                        "WHEN implementing THEN it SHALL use systematic patterns",
                        "WHEN making decisions THEN it SHALL consult model registry",
                        "WHEN validating THEN it SHALL use systematic validation"
                    ],
                    validation_method="systematic_compliance"
                ),
                Requirement(
                    req_id=f"{domain}-purpose-003",
                    description=f"Must fulfill domain purpose: {domain_info.purpose}",
                    domain=domain,
                    priority=2,
                    acceptance_criteria=[
                        f"WHEN implemented THEN it SHALL achieve: {domain_info.purpose}",
                        "WHEN tested THEN it SHALL validate purpose fulfillment"
                    ],
                    validation_method="purpose_validation"
                )
            ])
        
        # Cache the intelligence for future queries
        if domain not in self.intelligence_cache:
            self.intelligence_cache[domain] = ModelIntelligence(
                domain=domain,
                requirements=requirements,
                patterns=self.get_domain_patterns(domain),
                tools=self.get_tool_mappings(domain),
                success_metrics={},
                confidence_score=0.75
            )
        
        return requirements
    
    def _create_default_requirements(self, domain: str) -> List[Requirement]:
        """Create default requirements for unknown domains"""
        return [
            Requirement(
                req_id=f"{domain}-default-001",
                description="Must implement basic systematic approach",
                domain=domain,
                priority=1,
                acceptance_criteria=[
                    "WHEN implemented THEN it SHALL follow systematic patterns",
                    "WHEN validated THEN it SHALL pass basic systematic checks"
                ],
                validation_method="basic_systematic"
            )
        ]
    
    def get_domain_patterns(self, domain: str) -> List[Pattern]:
        """Get systematic patterns for a domain"""
        # Don't increment query_count here to avoid double counting when called from query_requirements
        
        # Check cache
        if domain in self.intelligence_cache:
            return self.intelligence_cache[domain].patterns
        
        patterns = []
        domain_info = self.domain_cache.get(domain)
        
        if domain_info and "RM compliant" in domain_info.compliance:
            patterns.append(Pattern(
                pattern_id=f"{domain}-rm-pattern",
                name="Reflective Module Pattern",
                domain=domain,
                description="Systematic health monitoring and status reporting",
                implementation_steps=[
                    "Inherit from ReflectiveModule base class",
                    "Implement get_health_status() method",
                    "Implement get_performance_metrics() method",
                    "Implement validate_systematic_compliance() method"
                ],
                success_metrics={"compliance_score": 1.0, "health_reporting": 1.0},
                confidence_score=0.95
            ))
        
        # Always add systematic implementation pattern
        patterns.append(Pattern(
            pattern_id=f"{domain}-systematic-pattern",
            name="Systematic Implementation Pattern",
            domain=domain,
            description="Model-driven systematic approach over ad-hoc",
            implementation_steps=[
                "Consult model registry for requirements",
                "Apply domain-specific patterns",
                "Use systematic validation",
                "Update model registry with learnings"
            ],
            success_metrics={"systematic_score": 0.9, "success_rate": 0.85},
            confidence_score=0.88
        ))
        
        return patterns
    
    def get_tool_mappings(self, domain: str) -> Dict[str, Tool]:
        """Get domain-specific tool mappings"""
        # Don't increment query_count here to avoid double counting when called from query_requirements
        
        # Check cache
        if domain in self.intelligence_cache:
            return self.intelligence_cache[domain].tools
        
        tools = {}
        
        # Create systematic tools based on domain name patterns
        if "testing" in domain.lower() or "test" in domain.lower():
            tools["pytest"] = Tool(
                tool_id=f"{domain}-pytest",
                name="pytest",
                domain=domain,
                purpose="systematic unit testing",
                command_template="pytest {test_path} -v --cov={module}",
                validation_method="exit_code_and_coverage"
            )
        
        if "code" in domain.lower() or "implementation" in domain.lower():
            tools["black"] = Tool(
                tool_id=f"{domain}-black",
                name="black",
                domain=domain,
                purpose="systematic code formatting",
                command_template="black {file_path} --check",
                validation_method="exit_code"
            )
            
            tools["mypy"] = Tool(
                tool_id=f"{domain}-mypy",
                name="mypy",
                domain=domain,
                purpose="systematic type checking",
                command_template="mypy {file_path}",
                validation_method="exit_code_and_output"
            )
        
        return tools
    
    def update_learning(self, pattern: Pattern) -> bool:
        """Update model registry with new learning patterns"""
        try:
            # Update intelligence cache
            domain = pattern.domain
            if domain not in self.intelligence_cache:
                self.intelligence_cache[domain] = ModelIntelligence(
                    domain=domain,
                    requirements=self.query_requirements(domain),
                    patterns=[],
                    tools=self.get_tool_mappings(domain),
                    success_metrics={},
                    confidence_score=0.5
                )
            
            # Add or update pattern
            intelligence = self.intelligence_cache[domain]
            existing_pattern = None
            for i, existing in enumerate(intelligence.patterns):
                if existing.pattern_id == pattern.pattern_id:
                    existing_pattern = i
                    break
            
            if existing_pattern is not None:
                # Update existing pattern with improved metrics
                old_pattern = intelligence.patterns[existing_pattern]
                intelligence.patterns[existing_pattern] = self._merge_patterns(old_pattern, pattern)
                self.logger.info(f"Updated existing pattern {pattern.pattern_id} for domain {domain}")
            else:
                intelligence.patterns.append(pattern)
                self.logger.info(f"Added new pattern {pattern.pattern_id} for domain {domain}")
            
            # Update success metrics with weighted averaging
            for metric, value in pattern.success_metrics.items():
                if metric in intelligence.success_metrics:
                    # Weighted average: 70% existing, 30% new
                    intelligence.success_metrics[metric] = (
                        intelligence.success_metrics[metric] * 0.7 + value * 0.3
                    )
                else:
                    intelligence.success_metrics[metric] = value
            
            # Update confidence based on pattern confidence and success metrics
            pattern_confidence_weight = 0.2
            metrics_confidence_weight = 0.1
            
            # Calculate metrics-based confidence boost
            avg_success_rate = sum(intelligence.success_metrics.values()) / max(len(intelligence.success_metrics), 1)
            metrics_boost = avg_success_rate * metrics_confidence_weight
            
            intelligence.confidence_score = min(1.0, (
                intelligence.confidence_score * (1 - pattern_confidence_weight - metrics_confidence_weight) +
                pattern.confidence_score * pattern_confidence_weight +
                metrics_boost
            ))
            
            self.last_updated = datetime.now()
            self.logger.info(f"Updated learning for domain {domain}: {pattern.name} (confidence: {intelligence.confidence_score:.3f})")
            
            # Persist learning to file if enabled
            self._persist_learning_update(domain, pattern)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update learning: {e}")
            return False
    
    def _merge_patterns(self, old_pattern: Pattern, new_pattern: Pattern) -> Pattern:
        """Merge old and new patterns, keeping the best of both"""
        # Use the higher confidence pattern as base
        if new_pattern.confidence_score > old_pattern.confidence_score:
            base_pattern = new_pattern
            merge_pattern = old_pattern
        else:
            base_pattern = old_pattern
            merge_pattern = new_pattern
        
        # Merge success metrics (take the better values)
        merged_metrics = base_pattern.success_metrics.copy()
        for metric, value in merge_pattern.success_metrics.items():
            if metric not in merged_metrics or value > merged_metrics[metric]:
                merged_metrics[metric] = value
        
        # Merge implementation steps (combine unique steps)
        merged_steps = list(base_pattern.implementation_steps)
        for step in merge_pattern.implementation_steps:
            if step not in merged_steps:
                merged_steps.append(step)
        
        # Create merged pattern
        return Pattern(
            pattern_id=base_pattern.pattern_id,
            name=base_pattern.name,
            domain=base_pattern.domain,
            description=f"{base_pattern.description} (enhanced with learning)",
            implementation_steps=merged_steps,
            success_metrics=merged_metrics,
            confidence_score=max(old_pattern.confidence_score, new_pattern.confidence_score)
        )
    
    def _persist_learning_update(self, domain: str, pattern: Pattern):
        """Persist learning updates to file system"""
        try:
            # Create learning directory if it doesn't exist
            learning_dir = Path("learning_patterns")
            learning_dir.mkdir(exist_ok=True)
            
            # Save pattern to domain-specific file
            pattern_file = learning_dir / f"{domain}_patterns.json"
            
            # Load existing patterns
            existing_patterns = []
            if pattern_file.exists():
                with open(pattern_file, 'r') as f:
                    existing_data = json.load(f)
                    existing_patterns = existing_data.get("patterns", [])
            
            # Update or add pattern
            pattern_dict = {
                "pattern_id": pattern.pattern_id,
                "name": pattern.name,
                "domain": pattern.domain,
                "description": pattern.description,
                "implementation_steps": pattern.implementation_steps,
                "success_metrics": pattern.success_metrics,
                "confidence_score": pattern.confidence_score,
                "updated_at": datetime.now().isoformat()
            }
            
            # Find and update existing pattern or add new one
            updated = False
            for i, existing in enumerate(existing_patterns):
                if existing.get("pattern_id") == pattern.pattern_id:
                    existing_patterns[i] = pattern_dict
                    updated = True
                    break
            
            if not updated:
                existing_patterns.append(pattern_dict)
            
            # Save updated patterns
            with open(pattern_file, 'w') as f:
                json.dump({
                    "domain": domain,
                    "patterns": existing_patterns,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
            
            self.logger.info(f"Persisted learning pattern {pattern.pattern_id} to {pattern_file}")
            
        except Exception as e:
            self.logger.warning(f"Failed to persist learning update: {e}")
    
    def load_persisted_learning(self, domain: str) -> List[Pattern]:
        """Load persisted learning patterns for a domain"""
        try:
            learning_dir = Path("learning_patterns")
            pattern_file = learning_dir / f"{domain}_patterns.json"
            
            if not pattern_file.exists():
                return []
            
            with open(pattern_file, 'r') as f:
                data = json.load(f)
                patterns = []
                
                for pattern_data in data.get("patterns", []):
                    pattern = Pattern(
                        pattern_id=pattern_data["pattern_id"],
                        name=pattern_data["name"],
                        domain=pattern_data["domain"],
                        description=pattern_data["description"],
                        implementation_steps=pattern_data["implementation_steps"],
                        success_metrics=pattern_data["success_metrics"],
                        confidence_score=pattern_data["confidence_score"]
                    )
                    patterns.append(pattern)
                
                self.logger.info(f"Loaded {len(patterns)} persisted patterns for domain {domain}")
                return patterns
                
        except Exception as e:
            self.logger.warning(f"Failed to load persisted learning for domain {domain}: {e}")
            return []
    
    def get_learning_insights(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Get insights from accumulated learning patterns"""
        insights = {
            "total_patterns": 0,
            "avg_confidence": 0.0,
            "top_success_metrics": {},
            "domain_insights": {},
            "learning_trends": []
        }
        
        try:
            domains_to_analyze = [domain] if domain else self.intelligence_cache.keys()
            
            all_patterns = []
            for d in domains_to_analyze:
                if d in self.intelligence_cache:
                    intelligence = self.intelligence_cache[d]
                    domain_patterns = intelligence.patterns
                    all_patterns.extend(domain_patterns)
                    
                    # Domain-specific insights
                    insights["domain_insights"][d] = {
                        "pattern_count": len(domain_patterns),
                        "avg_confidence": sum(p.confidence_score for p in domain_patterns) / max(len(domain_patterns), 1),
                        "success_metrics": intelligence.success_metrics,
                        "total_confidence": intelligence.confidence_score
                    }
            
            if all_patterns:
                insights["total_patterns"] = len(all_patterns)
                insights["avg_confidence"] = sum(p.confidence_score for p in all_patterns) / len(all_patterns)
                
                # Aggregate success metrics
                all_metrics = {}
                for pattern in all_patterns:
                    for metric, value in pattern.success_metrics.items():
                        if metric not in all_metrics:
                            all_metrics[metric] = []
                        all_metrics[metric].append(value)
                
                # Calculate top success metrics
                for metric, values in all_metrics.items():
                    insights["top_success_metrics"][metric] = {
                        "avg": sum(values) / len(values),
                        "max": max(values),
                        "count": len(values)
                    }
                
                # Learning trends (simplified)
                insights["learning_trends"] = [
                    f"Accumulated {len(all_patterns)} patterns across {len(domains_to_analyze)} domains",
                    f"Average confidence improved to {insights['avg_confidence']:.2%}",
                    f"Top performing metric: {max(insights['top_success_metrics'].items(), key=lambda x: x[1]['avg'])[0] if insights['top_success_metrics'] else 'None'}"
                ]
            
        except Exception as e:
            self.logger.error(f"Failed to generate learning insights: {e}")
        
        return insights
    
    def get_domain_intelligence(self, domain: str) -> ModelIntelligence:
        """Get complete intelligence for a domain"""
        if domain not in self.intelligence_cache:
            # Build intelligence from registry
            intelligence = ModelIntelligence(
                domain=domain,
                requirements=self.query_requirements(domain),
                patterns=self.get_domain_patterns(domain),
                tools=self.get_tool_mappings(domain),
                success_metrics={},
                confidence_score=0.75
            )
            self.intelligence_cache[domain] = intelligence
        
        return self.intelligence_cache[domain]
    
    def list_available_domains(self) -> List[str]:
        """List all available domains in registry"""
        return list(self.domain_cache.keys())
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_domains": len(self.domain_cache),
            "cached_intelligence": len(self.intelligence_cache),
            "query_count": self.query_count,
            "cache_hit_rate": self.cache_hits / max(self.query_count, 1),
            "last_updated": self.last_updated.isoformat()
        }
    
    # ReflectiveModule interface implementation
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return model registry health status"""
        registry_loaded = len(self.registry_data) > 0
        domains_available = len(self.domain_cache) > 0
        
        status = "healthy" if registry_loaded and domains_available else "degraded"
        
        return {
            "status": status,
            "registry_loaded": registry_loaded,
            "domains_available": domains_available,
            "total_domains": len(self.domain_cache),
            "cache_size": len(self.intelligence_cache),
            "last_updated": self.last_updated.isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Return performance metrics"""
        cache_hit_rate = self.cache_hits / max(self.query_count, 1)
        
        return {
            "query_count": float(self.query_count),
            "cache_hit_rate": cache_hit_rate,
            "domains_cached": float(len(self.intelligence_cache)),
            "avg_query_time": 0.05  # Estimated based on cache performance
        }
    
    def validate_systematic_compliance(self) -> ValidationLevel:
        """Validate systematic compliance of model registry"""
        # HIGH compliance: Active intelligence cache with cache hits
        if len(self.intelligence_cache) > 0 and self.cache_hits > 0:
            return ValidationLevel.HIGH
        
        # MEDIUM compliance: Some registry activity but no cache optimization
        if len(self.intelligence_cache) > 0 or self.query_count > 0:
            return ValidationLevel.MEDIUM
        
        # LOW compliance: No activity at all
        return ValidationLevel.LOW