"""
Ubiquitous Language Modeling Framework - Core infrastructure for domain-specific monitoring terminology.

This module provides the foundational framework for discovering, modeling, and managing
domain-specific monitoring languages across different industries and enterprises.
"""

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union, Callable
import yaml

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Standard metric types for monitoring systems."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    DERIVED = "derived"
    BINARY = "binary"
    RATE = "rate"


class AggregationFunction(Enum):
    """Supported aggregation functions for metric processing."""
    AVERAGE = "avg"
    MAXIMUM = "max"
    MINIMUM = "min"
    SUM = "sum"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    LAST = "last"
    FIRST = "first"
    CALCULATED = "calculated"


class DomainType(Enum):
    """Supported industry domains with specific monitoring languages."""
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    MANUFACTURING = "manufacturing"
    DEVOPS = "devops"
    RETAIL = "retail"
    EDUCATION = "education"
    GOVERNMENT = "government"
    GENERIC = "generic"


@dataclass
class TermDefinition:
    """Definition of a domain-specific monitoring term."""
    technical_name: str
    business_name: str
    description: str
    context: str
    domain: DomainType
    synonyms: List[str] = field(default_factory=list)
    related_terms: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate term definition after initialization."""
        if not self.technical_name or not self.business_name:
            raise ValueError("Both technical_name and business_name are required")
        if not self.description:
            raise ValueError("Description is required for term definition")


@dataclass
class ConceptRelationship:
    """Relationship between monitoring concepts."""
    source_concept: str
    target_concept: str
    relationship_type: str  # "depends_on", "derives_from", "aggregates", "composes"
    description: str
    strength: float = 1.0  # 0.0 to 1.0, strength of relationship
    bidirectional: bool = False


@dataclass
class AggregationRule:
    """Rule for aggregating metrics with domain-specific logic."""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    source_metrics: List[str] = field(default_factory=list)
    aggregation_function: AggregationFunction = AggregationFunction.AVERAGE
    window_size_seconds: int = 300  # 5 minutes default
    calculation_logic: Optional[str] = None  # Python expression or function name
    business_context: str = ""
    domain: DomainType = DomainType.GENERIC
    created_at: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> List[str]:
        """Validate aggregation rule and return any errors."""
        errors = []
        
        if not self.metric_name:
            errors.append("Metric name is required")
        
        if not self.source_metrics and self.aggregation_function != AggregationFunction.CALCULATED:
            errors.append("Source metrics required for non-calculated aggregations")
        
        if self.aggregation_function == AggregationFunction.CALCULATED and not self.calculation_logic:
            errors.append("Calculation logic required for calculated aggregations")
        
        if self.window_size_seconds <= 0:
            errors.append("Window size must be positive")
        
        return errors


@dataclass
class ConceptModel:
    """Model of a monitoring concept with business meaning."""
    name: str
    definition: str
    domain: DomainType
    properties: Dict[str, Any] = field(default_factory=dict)
    business_rules: List[str] = field(default_factory=list)
    calculation_logic: Optional[str] = None
    metric_type: MetricType = MetricType.GAUGE
    unit: str = ""
    normal_range: Optional[Dict[str, float]] = None  # {"min": 0, "max": 100}
    alert_thresholds: Optional[Dict[str, float]] = None  # {"warning": 80, "critical": 95}
    relationships: List[ConceptRelationship] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DisplayPreferences:
    """Display preferences for domain-specific monitoring interfaces."""
    chart_colors: Dict[str, str] = field(default_factory=dict)
    label_formats: Dict[str, str] = field(default_factory=dict)
    unit_displays: Dict[str, str] = field(default_factory=dict)
    dashboard_layout: Dict[str, Any] = field(default_factory=dict)
    alert_formats: Dict[str, str] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of language model validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DomainLanguageModel:
    """Complete language model for a specific monitoring domain."""
    domain: DomainType
    name: str
    description: str
    version: str = "1.0.0"
    terminology: Dict[str, TermDefinition] = field(default_factory=dict)
    concepts: Dict[str, ConceptModel] = field(default_factory=dict)
    aggregation_rules: Dict[str, AggregationRule] = field(default_factory=dict)
    display_preferences: DisplayPreferences = field(default_factory=DisplayPreferences)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_term(self, term: TermDefinition) -> None:
        """Add a term definition to the language model."""
        if term.technical_name in self.terminology:
            logger.warning(f"Overwriting existing term: {term.technical_name}")
        
        term.domain = self.domain
        term.updated_at = datetime.now()
        self.terminology[term.technical_name] = term
        self.updated_at = datetime.now()
    
    def add_concept(self, concept: ConceptModel) -> None:
        """Add a concept model to the language model."""
        if concept.name in self.concepts:
            logger.warning(f"Overwriting existing concept: {concept.name}")
        
        concept.domain = self.domain
        concept.updated_at = datetime.now()
        self.concepts[concept.name] = concept
        self.updated_at = datetime.now()
    
    def add_aggregation_rule(self, rule: AggregationRule) -> None:
        """Add an aggregation rule to the language model."""
        errors = rule.validate()
        if errors:
            raise ValueError(f"Invalid aggregation rule: {errors}")
        
        rule.domain = self.domain
        self.aggregation_rules[rule.metric_name] = rule
        self.updated_at = datetime.now()
    
    def get_business_name(self, technical_name: str) -> str:
        """Get business name for a technical term."""
        term = self.terminology.get(technical_name)
        return term.business_name if term else technical_name
    
    def get_technical_name(self, business_name: str) -> Optional[str]:
        """Get technical name for a business term."""
        for tech_name, term in self.terminology.items():
            if term.business_name.lower() == business_name.lower():
                return tech_name
        return None
    
    def validate(self) -> ValidationResult:
        """Validate the language model for consistency and completeness."""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for empty model
        if not self.terminology and not self.concepts:
            errors.append("Language model is empty - no terminology or concepts defined")
        
        # Validate terminology
        for tech_name, term in self.terminology.items():
            if term.domain != self.domain:
                warnings.append(f"Term '{tech_name}' has mismatched domain: {term.domain} vs {self.domain}")
        
        # Validate concepts
        for concept_name, concept in self.concepts.items():
            if concept.domain != self.domain:
                warnings.append(f"Concept '{concept_name}' has mismatched domain: {concept.domain} vs {self.domain}")
            
            # Check for orphaned relationships
            for rel in concept.relationships:
                if rel.target_concept not in self.concepts:
                    warnings.append(f"Concept '{concept_name}' references unknown concept: {rel.target_concept}")
        
        # Validate aggregation rules
        for rule_name, rule in self.aggregation_rules.items():
            rule_errors = rule.validate()
            if rule_errors:
                errors.extend([f"Rule '{rule_name}': {error}" for error in rule_errors])
        
        # Check for naming conflicts
        business_names = [term.business_name for term in self.terminology.values()]
        if len(business_names) != len(set(business_names)):
            warnings.append("Duplicate business names found in terminology")
        
        # Suggestions for improvement
        if len(self.terminology) < 5:
            suggestions.append("Consider adding more terminology definitions for better coverage")
        
        if not self.aggregation_rules:
            suggestions.append("Consider adding aggregation rules for metric processing")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


class UbiquitousLanguageEngine:
    """
    Engine for creating, managing, and processing ubiquitous language models.
    
    Features:
    - Domain-specific language model creation and validation
    - Terminology mapping between technical and business terms
    - Language model persistence and loading
    - Cross-domain language translation and merging
    """
    
    def __init__(self):
        self._models: Dict[str, DomainLanguageModel] = {}
        self._model_cache: Dict[str, datetime] = {}
        
        logger.info("🗣️ UbiquitousLanguageEngine initialized")
    
    def create_domain_model(self, domain: DomainType, name: str, description: str) -> DomainLanguageModel:
        """Create a new domain language model."""
        model = DomainLanguageModel(
            domain=domain,
            name=name,
            description=description
        )
        
        model_key = f"{domain.value}:{name}"
        self._models[model_key] = model
        self._model_cache[model_key] = datetime.now()
        
        logger.info(f"📝 Created domain language model: {model_key}")
        return model
    
    def load_model(self, model_key: str) -> Optional[DomainLanguageModel]:
        """Load a language model by key."""
        return self._models.get(model_key)
    
    def save_model(self, model: DomainLanguageModel, file_path: Path) -> bool:
        """Save a language model to file."""
        try:
            # Convert to serializable format
            model_dict = self._model_to_dict(model)
            
            # Save as YAML for human readability
            with open(file_path, 'w') as f:
                yaml.dump(model_dict, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"💾 Saved language model to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save language model: {e}")
            return False
    
    def load_model_from_file(self, file_path: Path) -> Optional[DomainLanguageModel]:
        """Load a language model from file."""
        try:
            with open(file_path, 'r') as f:
                model_dict = yaml.safe_load(f)
            
            model = self._dict_to_model(model_dict)
            
            model_key = f"{model.domain.value}:{model.name}"
            self._models[model_key] = model
            self._model_cache[model_key] = datetime.now()
            
            logger.info(f"📂 Loaded language model from: {file_path}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load language model from {file_path}: {e}")
            return None
    
    def map_technical_to_business(self, model: DomainLanguageModel, technical_terms: List[str]) -> Dict[str, str]:
        """Map technical terms to business terms using the language model."""
        mapping = {}
        
        for tech_term in technical_terms:
            business_term = model.get_business_name(tech_term)
            mapping[tech_term] = business_term
        
        return mapping
    
    def validate_language_consistency(self, model: DomainLanguageModel) -> ValidationResult:
        """Validate language model for consistency and completeness."""
        return model.validate()
    
    def merge_language_models(self, models: List[DomainLanguageModel], target_domain: DomainType, target_name: str) -> DomainLanguageModel:
        """Merge multiple language models into a unified model."""
        merged_model = DomainLanguageModel(
            domain=target_domain,
            name=target_name,
            description=f"Merged model from {len(models)} source models"
        )
        
        # Merge terminology
        for model in models:
            for tech_name, term in model.terminology.items():
                if tech_name not in merged_model.terminology:
                    # Create a copy with updated domain
                    merged_term = TermDefinition(
                        technical_name=term.technical_name,
                        business_name=term.business_name,
                        description=term.description,
                        context=f"{term.context} (from {model.domain.value})",
                        domain=target_domain,
                        synonyms=term.synonyms.copy(),
                        related_terms=term.related_terms.copy(),
                        examples=term.examples.copy()
                    )
                    merged_model.add_term(merged_term)
                else:
                    # Handle conflicts by adding synonyms
                    existing_term = merged_model.terminology[tech_name]
                    if term.business_name not in existing_term.synonyms:
                        existing_term.synonyms.append(term.business_name)
        
        # Merge concepts
        for model in models:
            for concept_name, concept in model.concepts.items():
                if concept_name not in merged_model.concepts:
                    # Create a copy with updated domain
                    merged_concept = ConceptModel(
                        name=concept.name,
                        definition=concept.definition,
                        domain=target_domain,
                        properties=concept.properties.copy(),
                        business_rules=concept.business_rules.copy(),
                        calculation_logic=concept.calculation_logic,
                        metric_type=concept.metric_type,
                        unit=concept.unit,
                        normal_range=concept.normal_range.copy() if concept.normal_range else None,
                        alert_thresholds=concept.alert_thresholds.copy() if concept.alert_thresholds else None,
                        relationships=concept.relationships.copy()
                    )
                    merged_model.add_concept(merged_concept)
        
        # Merge aggregation rules
        for model in models:
            for rule_name, rule in model.aggregation_rules.items():
                if rule_name not in merged_model.aggregation_rules:
                    # Create a copy with updated domain
                    merged_rule = AggregationRule(
                        metric_name=rule.metric_name,
                        source_metrics=rule.source_metrics.copy(),
                        aggregation_function=rule.aggregation_function,
                        window_size_seconds=rule.window_size_seconds,
                        calculation_logic=rule.calculation_logic,
                        business_context=rule.business_context,
                        domain=target_domain
                    )
                    merged_model.add_aggregation_rule(merged_rule)
        
        logger.info(f"🔀 Merged {len(models)} language models into: {target_domain.value}:{target_name}")
        return merged_model
    
    def get_available_models(self) -> List[str]:
        """Get list of available language model keys."""
        return list(self._models.keys())
    
    def _model_to_dict(self, model: DomainLanguageModel) -> Dict[str, Any]:
        """Convert language model to serializable dictionary."""
        model_dict = asdict(model)
        
        # Convert enums to strings
        model_dict['domain'] = model.domain.value
        
        # Convert datetime objects to ISO strings
        model_dict['created_at'] = model.created_at.isoformat()
        model_dict['updated_at'] = model.updated_at.isoformat()
        
        # Convert terminology
        for term_name, term_data in model_dict['terminology'].items():
            term_data['domain'] = term_data['domain'].value if hasattr(term_data['domain'], 'value') else term_data['domain']
            term_data['created_at'] = term_data['created_at'].isoformat() if isinstance(term_data['created_at'], datetime) else term_data['created_at']
            term_data['updated_at'] = term_data['updated_at'].isoformat() if isinstance(term_data['updated_at'], datetime) else term_data['updated_at']
        
        # Convert concepts
        for concept_name, concept_data in model_dict['concepts'].items():
            concept_data['domain'] = concept_data['domain'].value if hasattr(concept_data['domain'], 'value') else concept_data['domain']
            concept_data['metric_type'] = concept_data['metric_type'].value if hasattr(concept_data['metric_type'], 'value') else concept_data['metric_type']
            concept_data['created_at'] = concept_data['created_at'].isoformat() if isinstance(concept_data['created_at'], datetime) else concept_data['created_at']
            concept_data['updated_at'] = concept_data['updated_at'].isoformat() if isinstance(concept_data['updated_at'], datetime) else concept_data['updated_at']
        
        # Convert aggregation rules
        for rule_name, rule_data in model_dict['aggregation_rules'].items():
            rule_data['aggregation_function'] = rule_data['aggregation_function'].value if hasattr(rule_data['aggregation_function'], 'value') else rule_data['aggregation_function']
            rule_data['domain'] = rule_data['domain'].value if hasattr(rule_data['domain'], 'value') else rule_data['domain']
            rule_data['created_at'] = rule_data['created_at'].isoformat() if isinstance(rule_data['created_at'], datetime) else rule_data['created_at']
        
        return model_dict
    
    def _dict_to_model(self, model_dict: Dict[str, Any]) -> DomainLanguageModel:
        """Convert dictionary to language model object."""
        # Convert domain enum
        domain = DomainType(model_dict['domain'])
        
        # Create base model
        model = DomainLanguageModel(
            domain=domain,
            name=model_dict['name'],
            description=model_dict['description'],
            version=model_dict.get('version', '1.0.0'),
            created_at=datetime.fromisoformat(model_dict['created_at']),
            updated_at=datetime.fromisoformat(model_dict['updated_at']),
            metadata=model_dict.get('metadata', {})
        )
        
        # Load terminology
        for term_name, term_data in model_dict.get('terminology', {}).items():
            term = TermDefinition(
                technical_name=term_data['technical_name'],
                business_name=term_data['business_name'],
                description=term_data['description'],
                context=term_data['context'],
                domain=DomainType(term_data['domain']),
                synonyms=term_data.get('synonyms', []),
                related_terms=term_data.get('related_terms', []),
                examples=term_data.get('examples', []),
                created_at=datetime.fromisoformat(term_data['created_at']),
                updated_at=datetime.fromisoformat(term_data['updated_at'])
            )
            model.terminology[term_name] = term
        
        # Load concepts
        for concept_name, concept_data in model_dict.get('concepts', {}).items():
            relationships = []
            for rel_data in concept_data.get('relationships', []):
                relationships.append(ConceptRelationship(
                    source_concept=rel_data['source_concept'],
                    target_concept=rel_data['target_concept'],
                    relationship_type=rel_data['relationship_type'],
                    description=rel_data['description'],
                    strength=rel_data.get('strength', 1.0),
                    bidirectional=rel_data.get('bidirectional', False)
                ))
            
            concept = ConceptModel(
                name=concept_data['name'],
                definition=concept_data['definition'],
                domain=DomainType(concept_data['domain']),
                properties=concept_data.get('properties', {}),
                business_rules=concept_data.get('business_rules', []),
                calculation_logic=concept_data.get('calculation_logic'),
                metric_type=MetricType(concept_data.get('metric_type', 'gauge')),
                unit=concept_data.get('unit', ''),
                normal_range=concept_data.get('normal_range'),
                alert_thresholds=concept_data.get('alert_thresholds'),
                relationships=relationships,
                created_at=datetime.fromisoformat(concept_data['created_at']),
                updated_at=datetime.fromisoformat(concept_data['updated_at'])
            )
            model.concepts[concept_name] = concept
        
        # Load aggregation rules
        for rule_name, rule_data in model_dict.get('aggregation_rules', {}).items():
            rule = AggregationRule(
                rule_id=rule_data.get('rule_id', str(uuid.uuid4())),
                metric_name=rule_data['metric_name'],
                source_metrics=rule_data.get('source_metrics', []),
                aggregation_function=AggregationFunction(rule_data['aggregation_function']),
                window_size_seconds=rule_data.get('window_size_seconds', 300),
                calculation_logic=rule_data.get('calculation_logic'),
                business_context=rule_data.get('business_context', ''),
                domain=DomainType(rule_data['domain']),
                created_at=datetime.fromisoformat(rule_data['created_at'])
            )
            model.aggregation_rules[rule_name] = rule
        
        # Load display preferences
        if 'display_preferences' in model_dict:
            prefs_data = model_dict['display_preferences']
            model.display_preferences = DisplayPreferences(
                chart_colors=prefs_data.get('chart_colors', {}),
                label_formats=prefs_data.get('label_formats', {}),
                unit_displays=prefs_data.get('unit_displays', {}),
                dashboard_layout=prefs_data.get('dashboard_layout', {}),
                alert_formats=prefs_data.get('alert_formats', {})
            )
        
        return model