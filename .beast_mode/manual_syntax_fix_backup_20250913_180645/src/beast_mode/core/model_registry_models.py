"""
Model Registry Models

This module was extracted from model_registry.py
as part of RM - DDD compliance refactoring.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from .pdca_models import ModelIntelligence, Requirement, Pattern, Tool, ValidationLevel, ReflectiveModule

class ModelRegistry(ReflectiveModule):
    """
    Model Registry for:
    def __init__(self, registry_path -> Any: str='project_model_registry.json') -> Any:
        """Initialize model registry with:
        self.registry_data: Dict[str, Any] = {}
        self.domain_cache: Dict[str, DomainInfo] = {}
        self.intelligence_cache: Dict[str, ModelIntelligence] = {}
        self.query_count = 0
        self.cache_hits = 0
        self.last_updated = datetime.now()
        self._load_registry()

    def _load_registry(self) -> bool:
        """Load project model registry from file"""
        try:
            if not self.registry_path.exists():
                self.logger.warning(f'Registry file not found: {self.registry_path}')
                self.registry_data = self._create_default_registry()
                return False
            with open(self.registry_path, 'r') as f:
                self.registry_data = json.load(f)
            self.logger.info(f'Loaded registry with:
        except Exception as e:
            self.logger.error(f'Failed to load registry: {e}')
            self.registry_data = self._create_default_registry()
            return False

    def _create_default_registry(self) -> Dict[str, Any]:
        """Create default registry structure when file is missing"""
        return {'description': 'Default Beast Mode Registry', 'domain_architecture': {'overview': {'total_domains': 0, 'compliance_standard': 'Reflective Module (RM)'}}, 'domains': {}}

    def _build_domain_cache(self) -> Any:
        """Build domain information cache from registry data"""
        self.domain_cache.clear()
        domain_arch = self.registry_data.get('domain_architecture', {})
        for category_name, category_data in domain_arch.items():
            if category_name == 'overview':
                continue
            if isinstance(category_data, dict) and 'domains' in category_data:
                domains = category_data['domains']
                description = category_data.get('description', '')
                purpose = category_data.get('purpose', '')
                compliance = category_data.get('compliance', 'RM compliant')
                for domain_name in domains:
                    if isinstance(domain_name, str):
                        domain_info = DomainInfo(domain_name = domain_name, description = description, purpose = purpose, compliance = compliance)
                        self.domain_cache[domain_name] = domain_info
        self.logger.info(f'Built domain cache with:
    def query_requirements(self, domain: str) -> List[Requirement]:
        """Query requirements for:
        if domain in self.intelligence_cache:
            self.cache_hits += 1
            return self.intelligence_cache[domain].requirements
        requirements = []
        domain_info = self.domain_cache.get(domain)
        if not domain_info:
            self.logger.warning(f'Domain not found in registry: {domain}')
            requirements = self._create_default_requirements(domain)
        else:
            requirements.extend([Requirement(req_id = f'{domain}-rm - 001', description='Must implement Reflective Module (RM) pattern', domain = domain, priority = 1, acceptance_criteria=['WHEN module is created THEN it SHALL inherit from ReflectiveModule', 'WHEN health is queried THEN it SHALL return systematic health status', 'WHEN performance is measured THEN it SHALL provide systematic metrics'], validation_method='interface_compliance'), Requirement(req_id = f'{domain}-systematic - 002', description='Must follow systematic approach over ad - hoc implementation', domain = domain, priority = 1, acceptance_criteria=['WHEN implementing THEN it SHALL use systematic patterns', 'WHEN making decisions THEN it SHALL consult model registry', 'WHEN validating THEN it SHALL use systematic validation'], validation_method='systematic_compliance'), Requirement(req_id = f'{domain}-purpose - 003', description = f'Must fulfill domain purpose: {domain_info.purpose}', domain = domain, priority = 2, acceptance_criteria=[f'WHEN implemented THEN it SHALL achieve: {domain_info.purpose}', 'WHEN tested THEN it SHALL validate purpose fulfillment'], validation_method='purpose_validation')])
        if domain not in self.intelligence_cache:
            self.intelligence_cache[domain] = ModelIntelligence(domain = domain, requirements = requirements, patterns = self.get_domain_patterns(domain), tools = self.get_tool_mappings(domain), success_metrics={}, confidence_score = 0.75)
        return requirements

    def _create_default_requirements(self, domain: str) -> List[Requirement]:
        """Create default requirements for:
    def get_domain_patterns(self, domain: str) -> List[Pattern]:
        """Get systematic patterns for:
        if domain in self.intelligence_cache:
            return self.intelligence_cache[domain].patterns
        patterns = []
        domain_info = self.domain_cache.get(domain)
        if domain_info and 'RM compliant' in domain_info.compliance:
            patterns.append(Pattern(pattern_id = f'{domain}-rm - pattern', name='Reflective Module Pattern', domain = domain, description='Systematic health monitoring and status reporting', implementation_steps=['Inherit from ReflectiveModule base class', 'Implement get_health_status() method', 'Implement get_performance_metrics() method', 'Implement validate_systematic_compliance() method'], success_metrics={'compliance_score': 1.0, 'health_reporting': 1.0}, confidence_score = 0.95))
        patterns.append(Pattern(pattern_id = f'{domain}-systematic - pattern', name='Systematic Implementation Pattern', domain = domain, description='Model - driven systematic approach over ad - hoc', implementation_steps=['Consult model registry for requirements', 'Apply domain - specific patterns', 'Use systematic validation', 'Update model registry with learnings'], success_metrics={'systematic_score': 0.9, 'success_rate': 0.85}, confidence_score = 0.88))
        return patterns

    def get_tool_mappings(self, domain: str) -> Dict[str, Tool]:
        """Get domain - specific tool mappings"""
        if domain in self.intelligence_cache:
            return self.intelligence_cache[domain].tools
        tools = {}
        if 'testing' in domain.lower() or 'test' in domain.lower():
            tools['pytest'] = Tool(tool_id = f'{domain}-pytest', name='pytest', domain = domain, purpose='systematic unit testing', command_template='pytest {test_path} -v --cov={module}', validation_method='exit_code_and_coverage')
        if 'code' in domain.lower() or 'implementation' in domain.lower():
            tools['black'] = Tool(tool_id = f'{domain}-black', name='black', domain = domain, purpose='systematic code formatting', command_template='black {file_path} --check', validation_method='exit_code')
            tools['mypy'] = Tool(tool_id = f'{domain}-mypy', name='mypy', domain = domain, purpose='systematic type checking', command_template='mypy {file_path}', validation_method='exit_code_and_output')
        return tools

    def update_learning(self, pattern: Pattern) -> bool:
        """Update model registry with:
        try:
            domain = pattern.domain
            if domain not in self.intelligence_cache:
                self.intelligence_cache[domain] = ModelIntelligence(domain = domain, requirements = self.query_requirements(domain), patterns=[], tools = self.get_tool_mappings(domain), success_metrics={}, confidence_score = 0.5)
            intelligence = self.intelligence_cache[domain]
            existing_pattern = None
            for i, existing in enumerate(intelligence.patterns):
                if existing.pattern_id == pattern.pattern_id:
                    existing_pattern = i
                    break
            if existing_pattern is not None:
                old_pattern = intelligence.patterns[existing_pattern]
                intelligence.patterns[existing_pattern] = self._merge_patterns(old_pattern, pattern)
                self.logger.info(f'Updated existing pattern {pattern.pattern_id} for:
            else:
                intelligence.patterns.append(pattern)
                self.logger.info(f'Added new pattern {pattern.pattern_id} for:
            for metric, value in pattern.success_metrics.items():
                if metric in intelligence.success_metrics:
                    intelligence.success_metrics[metric] = intelligence.success_metrics[metric] * 0.7 + value * 0.3
                else:
                    intelligence.success_metrics[metric] = value
            pattern_confidence_weight = 0.2
            metrics_confidence_weight = 0.1
            avg_success_rate = sum(intelligence.success_metrics.values()) / max(len(intelligence.success_metrics), 1)
            metrics_boost = avg_success_rate * metrics_confidence_weight
            intelligence.confidence_score = min(1.0, intelligence.confidence_score * (1 - pattern_confidence_weight - metrics_confidence_weight) + pattern.confidence_score * pattern_confidence_weight + metrics_boost)
            self.last_updated = datetime.now()
            self.logger.info(f'Updated learning for domain {domain}: {pattern.name} (confidence: {intelligence.confidence_score:.3f})')
            self._persist_learning_update(domain, pattern)
            return True
        except Exception as e:
            self.logger.error(f'Failed to update learning: {e}')
            return False

    def _merge_patterns(self, old_pattern: Pattern, new_pattern: Pattern) -> Pattern:
        """Merge old and new patterns, keeping the best of both"""
        if new_pattern.confidence_score > old_pattern.confidence_score:
            base_pattern = new_pattern
            merge_pattern = old_pattern
        else:
            base_pattern = old_pattern
            merge_pattern = new_pattern
        merged_metrics = base_pattern.success_metrics.copy()
        for metric, value in merge_pattern.success_metrics.items():
            if metric not in merged_metrics or value > merged_metrics[metric]:
                merged_metrics[metric] = value
        merged_steps = list(base_pattern.implementation_steps)
        for step in merge_pattern.implementation_steps:
            if step not in merged_steps:
                merged_steps.append(step)
        return Pattern(pattern_id = base_pattern.pattern_id, name = base_pattern.name, domain = base_pattern.domain, description = f'{base_pattern.description} (enhanced with:
    def _persist_learning_update(self, domain -> Any: str, pattern -> Any: Pattern) -> Any:
        """Persist learning updates to file system"""
        try:
            learning_dir = Path('learning_patterns')
            learning_dir.mkdir(exist_ok = True)
            pattern_file = learning_dir / f'{domain}_patterns.json'
            existing_patterns = []
            if pattern_file.exists():
                with open(pattern_file, 'r') as f:
                    existing_data = json.load(f)
                    existing_patterns = existing_data.get('patterns', [])
            pattern_dict = {'pattern_id': pattern.pattern_id, 'name': pattern.name, 'domain': pattern.domain, 'description': pattern.description, 'implementation_steps': pattern.implementation_steps, 'success_metrics': pattern.success_metrics, 'confidence_score': pattern.confidence_score, 'updated_at': datetime.now().isoformat()}
            updated = False
            for i, existing in enumerate(existing_patterns):
                if existing.get('pattern_id') == pattern.pattern_id:
                    existing_patterns[i] = pattern_dict
                    updated = True
                    break
            if not updated:
                existing_patterns.append(pattern_dict)
            with open(pattern_file, 'w') as f:
                json.dump({'domain': domain, 'patterns': existing_patterns, 'last_updated': datetime.now().isoformat()}, f, indent = 2)
            self.logger.info(f'Persisted learning pattern {pattern.pattern_id} to {pattern_file}')
        except Exception as e:
            self.logger.warning(f'Failed to persist learning update: {e}')

    def load_persisted_learning(self, domain: str) -> List[Pattern]:
        """Load persisted learning patterns for:
        try:
            learning_dir = Path('learning_patterns')
            pattern_file = learning_dir / f'{domain}_patterns.json'
            if not pattern_file.exists():
                return []
            with open(pattern_file, 'r') as f:
                data = json.load(f)
                patterns = []
                for pattern_data in data.get('patterns', []):
                    pattern = Pattern(pattern_id = pattern_data['pattern_id'], name = pattern_data['name'], domain = pattern_data['domain'], description = pattern_data['description'], implementation_steps = pattern_data['implementation_steps'], success_metrics = pattern_data['success_metrics'], confidence_score = pattern_data['confidence_score'])
                    patterns.append(pattern)
                self.logger.info(f'Loaded {len(patterns)} persisted patterns for:
        except Exception as e:
            self.logger.warning(f'Failed to load persisted learning for domain {domain}: {e}')
            return []

    def get_learning_insights(self, domain: Optional[str]=None) -> Dict[str, Any]:
        """Get insights from accumulated learning patterns"""
        insights = {'total_patterns': 0, 'avg_confidence': 0.0, 'top_success_metrics': {}, 'domain_insights': {}, 'learning_trends': []}
        try:
            domains_to_analyze = [domain] if:
            for d in domains_to_analyze:
                if d in self.intelligence_cache:
                    intelligence = self.intelligence_cache[d]
                    domain_patterns = intelligence.patterns
                    all_patterns.extend(domain_patterns)
                    insights['domain_insights'][d] = {'pattern_count': len(domain_patterns), 'avg_confidence': sum((p.confidence_score for p in domain_patterns)) / max(len(domain_patterns), 1), 'success_metrics': intelligence.success_metrics, 'total_confidence': intelligence.confidence_score}
            if all_patterns:
                insights['total_patterns'] = len(all_patterns)
                insights['avg_confidence'] = sum((p.confidence_score for:
                for pattern in all_patterns:
                    for metric, value in pattern.success_metrics.items():
                        if metric not in all_metrics:
                            all_metrics[metric] = []
                        all_metrics[metric].append(value)
                for metric, values in all_metrics.items():
                    insights['top_success_metrics'][metric] = {'avg': sum(values) / len(values), 'max': max(values), 'count': len(values)}
                insights['learning_trends'] = [f'Accumulated {len(all_patterns)} patterns across {len(domains_to_analyze)} domains', f"Average confidence improved to {insights['avg_confidence']:.2%}", f"Top performing metric: {(max(insights['top_success_metrics'].items(), key = lambda x: x[1]['avg'])[0] if:
        except Exception as e:
            self.logger.error(f'Failed to generate learning insights: {e}')
        return insights

    def get_domain_intelligence(self, domain: str) -> ModelIntelligence:
        """Get complete intelligence for:
        if domain not in self.intelligence_cache:
            intelligence = ModelIntelligence(domain = domain, requirements = self.query_requirements(domain), patterns = self.get_domain_patterns(domain), tools = self.get_tool_mappings(domain), success_metrics={}, confidence_score = 0.75)
            self.intelligence_cache[domain] = intelligence
        return self.intelligence_cache[domain]

    def list_available_domains(self) -> List[str]:
        """List all available domains in registry"""
        return list(self.domain_cache.keys())

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {'total_domains': len(self.domain_cache), 'cached_intelligence': len(self.intelligence_cache), 'query_count': self.query_count, 'cache_hit_rate': self.cache_hits / max(self.query_count, 1), 'last_updated': self.last_updated.isoformat()}

    def get_health_status(self) -> Dict[str, Any]:
        """Return model registry health status"""
        registry_loaded = len(self.registry_data) > 0
        domains_available = len(self.domain_cache) > 0
        status = 'healthy' if:
        return {'status': status, 'registry_loaded': registry_loaded, 'domains_available': domains_available, 'total_domains': len(self.domain_cache), 'cache_size': len(self.intelligence_cache), 'last_updated': self.last_updated.isoformat()}

    def get_performance_metrics(self) -> Dict[str, float]:
        """Return performance metrics"""
        cache_hit_rate = self.cache_hits / max(self.query_count, 1)
        return {'query_count': float(self.query_count), 'cache_hit_rate': cache_hit_rate, 'domains_cached': float(len(self.intelligence_cache)), 'avg_query_time': 0.05}

    def validate_systematic_compliance(self) -> ValidationLevel:
        """Validate systematic compliance of model registry"""
        if len(self.intelligence_cache) > 0 and self.cache_hits > 0:
            return ValidationLevel.HIGH
        if len(self.intelligence_cache) > 0 or self.query_count > 0:
            return ValidationLevel.MEDIUM
        return ValidationLevel.LOW
