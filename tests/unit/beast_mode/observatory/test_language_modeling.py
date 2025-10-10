"""
Unit tests for the Ubiquitous Language Modeling Framework.
"""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path

from src.beast_mode.observatory.language_modeling import (
    DomainLanguageModel,
    TermDefinition,
    ConceptModel,
    ConceptRelationship,
    AggregationRule,
    DisplayPreferences,
    UbiquitousLanguageEngine,
    ValidationResult,
    DomainType,
    MetricType,
    AggregationFunction
)


class TestTermDefinition:
    """Test TermDefinition dataclass."""
    
    def test_valid_term_creation(self):
        """Test creating a valid term definition."""
        term = TermDefinition(
            technical_name="cpu_usage_percent",
            business_name="CPU Utilization",
            description="Percentage of CPU capacity being used",
            context="System performance monitoring",
            domain=DomainType.DEVOPS
        )
        
        assert term.technical_name == "cpu_usage_percent"
        assert term.business_name == "CPU Utilization"
        assert term.domain == DomainType.DEVOPS
        assert isinstance(term.created_at, datetime)
    
    def test_term_validation_errors(self):
        """Test term definition validation."""
        with pytest.raises(ValueError, match="Both technical_name and business_name are required"):
            TermDefinition(
                technical_name="",
                business_name="CPU Utilization",
                description="Test description",
                context="Test context",
                domain=DomainType.DEVOPS
            )
        
        with pytest.raises(ValueError, match="Description is required"):
            TermDefinition(
                technical_name="cpu_usage",
                business_name="CPU Utilization",
                description="",
                context="Test context",
                domain=DomainType.DEVOPS
            )


class TestAggregationRule:
    """Test AggregationRule dataclass."""
    
    def test_valid_aggregation_rule(self):
        """Test creating a valid aggregation rule."""
        rule = AggregationRule(
            metric_name="avg_response_time",
            source_metrics=["response_time_ms"],
            aggregation_function=AggregationFunction.AVERAGE,
            window_size_seconds=300,
            business_context="API performance monitoring"
        )
        
        errors = rule.validate()
        assert len(errors) == 0
        assert rule.metric_name == "avg_response_time"
        assert rule.aggregation_function == AggregationFunction.AVERAGE
    
    def test_aggregation_rule_validation(self):
        """Test aggregation rule validation."""
        # Missing metric name
        rule = AggregationRule(
            metric_name="",
            source_metrics=["test"],
            aggregation_function=AggregationFunction.AVERAGE
        )
        errors = rule.validate()
        assert "Metric name is required" in errors
        
        # Missing source metrics for non-calculated function
        rule = AggregationRule(
            metric_name="test_metric",
            source_metrics=[],
            aggregation_function=AggregationFunction.AVERAGE
        )
        errors = rule.validate()
        assert "Source metrics required for non-calculated aggregations" in errors
        
        # Missing calculation logic for calculated function
        rule = AggregationRule(
            metric_name="calculated_metric",
            source_metrics=[],
            aggregation_function=AggregationFunction.CALCULATED,
            calculation_logic=None
        )
        errors = rule.validate()
        assert "Calculation logic required for calculated aggregations" in errors
        
        # Invalid window size
        rule = AggregationRule(
            metric_name="test_metric",
            source_metrics=["test"],
            aggregation_function=AggregationFunction.AVERAGE,
            window_size_seconds=0
        )
        errors = rule.validate()
        assert "Window size must be positive" in errors


class TestConceptModel:
    """Test ConceptModel dataclass."""
    
    def test_concept_creation(self):
        """Test creating a concept model."""
        relationship = ConceptRelationship(
            source_concept="patient_throughput",
            target_concept="bed_occupancy",
            relationship_type="depends_on",
            description="Patient throughput depends on bed availability"
        )
        
        concept = ConceptModel(
            name="patient_throughput",
            definition="Rate of patient admissions and discharges",
            domain=DomainType.HEALTHCARE,
            metric_type=MetricType.RATE,
            unit="patients/hour",
            normal_range={"min": 5, "max": 20},
            alert_thresholds={"warning": 25, "critical": 30},
            relationships=[relationship]
        )
        
        assert concept.name == "patient_throughput"
        assert concept.domain == DomainType.HEALTHCARE
        assert concept.metric_type == MetricType.RATE
        assert len(concept.relationships) == 1
        assert concept.relationships[0].relationship_type == "depends_on"


class TestDomainLanguageModel:
    """Test DomainLanguageModel dataclass."""
    
    def test_model_creation(self):
        """Test creating a domain language model."""
        model = DomainLanguageModel(
            domain=DomainType.HEALTHCARE,
            name="Hospital Monitoring",
            description="Language model for hospital monitoring systems"
        )
        
        assert model.domain == DomainType.HEALTHCARE
        assert model.name == "Hospital Monitoring"
        assert len(model.terminology) == 0
        assert len(model.concepts) == 0
    
    def test_add_term(self):
        """Test adding terms to language model."""
        model = DomainLanguageModel(
            domain=DomainType.HEALTHCARE,
            name="Test Model",
            description="Test description"
        )
        
        term = TermDefinition(
            technical_name="bed_occupancy_rate",
            business_name="Bed Occupancy Rate",
            description="Percentage of beds currently occupied",
            context="Capacity management",
            domain=DomainType.GENERIC  # Will be updated to match model
        )
        
        model.add_term(term)
        
        assert len(model.terminology) == 1
        assert "bed_occupancy_rate" in model.terminology
        assert model.terminology["bed_occupancy_rate"].domain == DomainType.HEALTHCARE
    
    def test_add_concept(self):
        """Test adding concepts to language model."""
        model = DomainLanguageModel(
            domain=DomainType.FINANCE,
            name="Trading System",
            description="Financial trading monitoring"
        )
        
        concept = ConceptModel(
            name="trade_volume",
            definition="Number of trades executed per time period",
            domain=DomainType.GENERIC  # Will be updated
        )
        
        model.add_concept(concept)
        
        assert len(model.concepts) == 1
        assert "trade_volume" in model.concepts
        assert model.concepts["trade_volume"].domain == DomainType.FINANCE
    
    def test_add_aggregation_rule(self):
        """Test adding aggregation rules to language model."""
        model = DomainLanguageModel(
            domain=DomainType.MANUFACTURING,
            name="Production Line",
            description="Manufacturing monitoring"
        )
        
        rule = AggregationRule(
            metric_name="production_efficiency",
            source_metrics=["units_produced", "target_production"],
            aggregation_function=AggregationFunction.CALCULATED,
            calculation_logic="units_produced / target_production * 100"
        )
        
        model.add_aggregation_rule(rule)
        
        assert len(model.aggregation_rules) == 1
        assert "production_efficiency" in model.aggregation_rules
        assert model.aggregation_rules["production_efficiency"].domain == DomainType.MANUFACTURING
    
    def test_business_name_mapping(self):
        """Test mapping between technical and business names."""
        model = DomainLanguageModel(
            domain=DomainType.DEVOPS,
            name="System Monitoring",
            description="DevOps monitoring"
        )
        
        term = TermDefinition(
            technical_name="memory_usage_bytes",
            business_name="Memory Consumption",
            description="Amount of memory being used",
            context="Resource monitoring",
            domain=DomainType.DEVOPS
        )
        
        model.add_term(term)
        
        # Test technical to business mapping
        business_name = model.get_business_name("memory_usage_bytes")
        assert business_name == "Memory Consumption"
        
        # Test unknown technical name
        unknown_business = model.get_business_name("unknown_metric")
        assert unknown_business == "unknown_metric"
        
        # Test business to technical mapping
        technical_name = model.get_technical_name("Memory Consumption")
        assert technical_name == "memory_usage_bytes"
        
        # Test unknown business name
        unknown_technical = model.get_technical_name("Unknown Metric")
        assert unknown_technical is None
    
    def test_model_validation(self):
        """Test language model validation."""
        # Empty model
        empty_model = DomainLanguageModel(
            domain=DomainType.GENERIC,
            name="Empty Model",
            description="Empty test model"
        )
        
        result = empty_model.validate()
        assert not result.is_valid
        assert "Language model is empty" in result.errors[0]
        
        # Valid model
        valid_model = DomainLanguageModel(
            domain=DomainType.HEALTHCARE,
            name="Valid Model",
            description="Valid test model"
        )
        
        term = TermDefinition(
            technical_name="patient_count",
            business_name="Patient Count",
            description="Number of patients",
            context="Census tracking",
            domain=DomainType.HEALTHCARE
        )
        valid_model.add_term(term)
        
        result = valid_model.validate()
        assert result.is_valid
        assert len(result.errors) == 0


class TestUbiquitousLanguageEngine:
    """Test UbiquitousLanguageEngine class."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = UbiquitousLanguageEngine()
        assert len(engine.get_available_models()) == 0
    
    def test_create_domain_model(self):
        """Test creating domain models."""
        engine = UbiquitousLanguageEngine()
        
        model = engine.create_domain_model(
            domain=DomainType.HEALTHCARE,
            name="Hospital System",
            description="Hospital monitoring language"
        )
        
        assert model.domain == DomainType.HEALTHCARE
        assert model.name == "Hospital System"
        
        available_models = engine.get_available_models()
        assert len(available_models) == 1
        assert "healthcare:Hospital System" in available_models
    
    def test_load_model(self):
        """Test loading models by key."""
        engine = UbiquitousLanguageEngine()
        
        # Create a model
        model = engine.create_domain_model(
            domain=DomainType.FINANCE,
            name="Trading System",
            description="Financial trading monitoring"
        )
        
        # Load the model
        loaded_model = engine.load_model("finance:Trading System")
        assert loaded_model is not None
        assert loaded_model.name == "Trading System"
        
        # Try to load non-existent model
        missing_model = engine.load_model("nonexistent:model")
        assert missing_model is None
    
    def test_technical_to_business_mapping(self):
        """Test mapping technical terms to business terms."""
        engine = UbiquitousLanguageEngine()
        
        model = engine.create_domain_model(
            domain=DomainType.RETAIL,
            name="Store Operations",
            description="Retail store monitoring"
        )
        
        # Add some terms
        terms = [
            TermDefinition(
                technical_name="sales_per_hour",
                business_name="Hourly Sales Volume",
                description="Sales volume per hour",
                context="Sales tracking",
                domain=DomainType.RETAIL
            ),
            TermDefinition(
                technical_name="customer_count",
                business_name="Customer Traffic",
                description="Number of customers in store",
                context="Traffic monitoring",
                domain=DomainType.RETAIL
            )
        ]
        
        for term in terms:
            model.add_term(term)
        
        # Test mapping
        technical_terms = ["sales_per_hour", "customer_count", "unknown_metric"]
        mapping = engine.map_technical_to_business(model, technical_terms)
        
        assert mapping["sales_per_hour"] == "Hourly Sales Volume"
        assert mapping["customer_count"] == "Customer Traffic"
        assert mapping["unknown_metric"] == "unknown_metric"  # Unchanged
    
    def test_model_persistence(self):
        """Test saving and loading models from files."""
        engine = UbiquitousLanguageEngine()
        
        # Create a model with content
        model = engine.create_domain_model(
            domain=DomainType.EDUCATION,
            name="School System",
            description="Educational institution monitoring"
        )
        
        term = TermDefinition(
            technical_name="student_attendance_rate",
            business_name="Student Attendance Rate",
            description="Percentage of students attending classes",
            context="Academic performance",
            domain=DomainType.EDUCATION
        )
        model.add_term(term)
        
        concept = ConceptModel(
            name="academic_performance",
            definition="Overall measure of student academic success",
            domain=DomainType.EDUCATION,
            metric_type=MetricType.GAUGE,
            unit="percentage"
        )
        model.add_concept(concept)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Save model
            success = engine.save_model(model, temp_path)
            assert success
            assert temp_path.exists()
            
            # Load model
            loaded_model = engine.load_model_from_file(temp_path)
            assert loaded_model is not None
            assert loaded_model.name == "School System"
            assert loaded_model.domain == DomainType.EDUCATION
            assert len(loaded_model.terminology) == 1
            assert len(loaded_model.concepts) == 1
            assert "student_attendance_rate" in loaded_model.terminology
            assert "academic_performance" in loaded_model.concepts
            
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
    
    def test_merge_language_models(self):
        """Test merging multiple language models."""
        engine = UbiquitousLanguageEngine()
        
        # Create first model
        model1 = engine.create_domain_model(
            domain=DomainType.HEALTHCARE,
            name="Hospital A",
            description="Hospital A monitoring"
        )
        
        term1 = TermDefinition(
            technical_name="bed_occupancy",
            business_name="Bed Occupancy",
            description="Number of occupied beds",
            context="Capacity management",
            domain=DomainType.HEALTHCARE
        )
        model1.add_term(term1)
        
        # Create second model
        model2 = engine.create_domain_model(
            domain=DomainType.HEALTHCARE,
            name="Hospital B",
            description="Hospital B monitoring"
        )
        
        term2 = TermDefinition(
            technical_name="patient_throughput",
            business_name="Patient Flow",
            description="Rate of patient admissions/discharges",
            context="Flow management",
            domain=DomainType.HEALTHCARE
        )
        model2.add_term(term2)
        
        # Add conflicting term with same technical name
        term3 = TermDefinition(
            technical_name="bed_occupancy",
            business_name="Bed Utilization",  # Different business name
            description="Bed usage rate",
            context="Utilization tracking",
            domain=DomainType.HEALTHCARE
        )
        model2.add_term(term3)
        
        # Merge models
        merged_model = engine.merge_language_models(
            models=[model1, model2],
            target_domain=DomainType.HEALTHCARE,
            target_name="Merged Hospital System"
        )
        
        assert merged_model.name == "Merged Hospital System"
        assert merged_model.domain == DomainType.HEALTHCARE
        assert len(merged_model.terminology) == 2  # bed_occupancy and patient_throughput
        
        # Check conflict resolution - should have added synonym
        bed_occupancy_term = merged_model.terminology["bed_occupancy"]
        assert "Bed Utilization" in bed_occupancy_term.synonyms
    
    def test_validation_integration(self):
        """Test validation through the engine."""
        engine = UbiquitousLanguageEngine()
        
        model = engine.create_domain_model(
            domain=DomainType.MANUFACTURING,
            name="Factory System",
            description="Manufacturing monitoring"
        )
        
        # Add invalid aggregation rule
        invalid_rule = AggregationRule(
            metric_name="",  # Invalid - empty name
            source_metrics=[],
            aggregation_function=AggregationFunction.AVERAGE
        )
        
        with pytest.raises(ValueError):
            model.add_aggregation_rule(invalid_rule)
        
        # Add valid content
        term = TermDefinition(
            technical_name="production_rate",
            business_name="Production Rate",
            description="Units produced per hour",
            context="Production monitoring",
            domain=DomainType.MANUFACTURING
        )
        model.add_term(term)
        
        # Validate through engine
        result = engine.validate_language_consistency(model)
        assert result.is_valid
        assert len(result.errors) == 0


if __name__ == "__main__":
    pytest.main([__file__])