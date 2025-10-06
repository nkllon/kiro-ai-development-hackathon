#!/usr/bin/env python3
"""
Demonstration of the Ubiquitous Language Modeling Framework.

This script shows how to create domain-specific language models for different
industries and use them for monitoring integration.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.language_modeling import (
    UbiquitousLanguageEngine,
    TermDefinition,
    ConceptModel,
    ConceptRelationship,
    AggregationRule,
    DomainType,
    MetricType,
    AggregationFunction
)


def create_healthcare_model(engine: UbiquitousLanguageEngine):
    """Create a healthcare domain language model."""
    print("🏥 Creating Healthcare Domain Language Model...")
    
    model = engine.create_domain_model(
        domain=DomainType.HEALTHCARE,
        name="Hospital Operations",
        description="Language model for hospital monitoring and operations"
    )
    
    # Add healthcare terminology
    healthcare_terms = [
        TermDefinition(
            technical_name="bed_occupancy_rate",
            business_name="Bed Occupancy Rate",
            description="Percentage of hospital beds currently occupied by patients",
            context="Capacity management and resource planning",
            domain=DomainType.HEALTHCARE,
            synonyms=["Bed Utilization", "Census Rate"],
            examples=["85% bed occupancy indicates high capacity utilization"]
        ),
        TermDefinition(
            technical_name="patient_throughput",
            business_name="Patient Throughput",
            description="Rate of patient admissions and discharges per time period",
            context="Patient flow management",
            domain=DomainType.HEALTHCARE,
            synonyms=["Patient Flow", "Admission Rate"],
            examples=["12 patients/hour throughput during peak hours"]
        ),
        TermDefinition(
            technical_name="adverse_events_count",
            business_name="Patient Safety Events",
            description="Number of adverse events affecting patient safety",
            context="Quality and safety monitoring",
            domain=DomainType.HEALTHCARE,
            synonyms=["Safety Incidents", "Quality Events"],
            examples=["Zero adverse events is the target for patient safety"]
        )
    ]
    
    for term in healthcare_terms:
        model.add_term(term)
    
    # Add healthcare concepts
    patient_safety_concept = ConceptModel(
        name="patient_safety_score",
        definition="Composite score measuring overall patient safety performance",
        domain=DomainType.HEALTHCARE,
        metric_type=MetricType.GAUGE,
        unit="score (0-100)",
        normal_range={"min": 85, "max": 100},
        alert_thresholds={"warning": 80, "critical": 70},
        business_rules=[
            "Score must be calculated daily",
            "Adverse events reduce score by severity weight",
            "Perfect safety score is 100"
        ],
        calculation_logic="100 - (adverse_events_weight * severity_multiplier)"
    )
    
    model.add_concept(patient_safety_concept)
    
    # Add aggregation rules
    bed_utilization_rule = AggregationRule(
        metric_name="avg_bed_occupancy",
        source_metrics=["occupied_beds", "total_beds"],
        aggregation_function=AggregationFunction.CALCULATED,
        window_size_seconds=3600,  # 1 hour
        calculation_logic="(occupied_beds / total_beds) * 100",
        business_context="Average bed occupancy rate over time window"
    )
    
    model.add_aggregation_rule(bed_utilization_rule)
    
    print(f"   ✅ Added {len(model.terminology)} terms")
    print(f"   ✅ Added {len(model.concepts)} concepts")
    print(f"   ✅ Added {len(model.aggregation_rules)} aggregation rules")
    
    return model


def create_finance_model(engine: UbiquitousLanguageEngine):
    """Create a finance domain language model."""
    print("💰 Creating Finance Domain Language Model...")
    
    model = engine.create_domain_model(
        domain=DomainType.FINANCE,
        name="Trading System",
        description="Language model for financial trading system monitoring"
    )
    
    # Add finance terminology
    finance_terms = [
        TermDefinition(
            technical_name="trade_execution_latency",
            business_name="Trade Execution Time",
            description="Time taken to execute a trade order from submission to confirmation",
            context="Trading performance and market competitiveness",
            domain=DomainType.FINANCE,
            synonyms=["Order Latency", "Execution Speed"],
            examples=["Sub-millisecond execution time for high-frequency trading"]
        ),
        TermDefinition(
            technical_name="risk_exposure_amount",
            business_name="Risk Exposure",
            description="Total monetary value at risk across all trading positions",
            context="Risk management and regulatory compliance",
            domain=DomainType.FINANCE,
            synonyms=["Position Risk", "Market Exposure"],
            examples=["$10M risk exposure across equity positions"]
        ),
        TermDefinition(
            technical_name="settlement_failure_count",
            business_name="Settlement Failures",
            description="Number of trades that failed to settle within required timeframe",
            context="Operational risk and regulatory compliance",
            domain=DomainType.FINANCE,
            synonyms=["Failed Settlements", "Settlement Breaks"],
            examples=["Zero settlement failures required for regulatory compliance"]
        )
    ]
    
    for term in finance_terms:
        model.add_term(term)
    
    # Add finance concepts with relationships
    risk_relationship = ConceptRelationship(
        source_concept="trading_performance",
        target_concept="risk_management",
        relationship_type="depends_on",
        description="Trading performance metrics depend on effective risk management"
    )
    
    trading_performance_concept = ConceptModel(
        name="trading_performance",
        definition="Overall measure of trading system effectiveness and efficiency",
        domain=DomainType.FINANCE,
        metric_type=MetricType.GAUGE,
        unit="performance_score",
        normal_range={"min": 90, "max": 100},
        alert_thresholds={"warning": 85, "critical": 75},
        relationships=[risk_relationship],
        business_rules=[
            "Performance calculated every 15 minutes during trading hours",
            "Latency spikes reduce performance score",
            "Settlement failures have severe performance impact"
        ]
    )
    
    model.add_concept(trading_performance_concept)
    
    # Add complex aggregation rule
    performance_rule = AggregationRule(
        metric_name="trading_performance_score",
        source_metrics=["trade_execution_latency", "settlement_failure_count", "risk_exposure_amount"],
        aggregation_function=AggregationFunction.CALCULATED,
        window_size_seconds=900,  # 15 minutes
        calculation_logic="calculate_trading_performance(latency, failures, risk)",
        business_context="Composite trading system performance score"
    )
    
    model.add_aggregation_rule(performance_rule)
    
    print(f"   ✅ Added {len(model.terminology)} terms")
    print(f"   ✅ Added {len(model.concepts)} concepts")
    print(f"   ✅ Added {len(model.aggregation_rules)} aggregation rules")
    
    return model


def create_manufacturing_model(engine: UbiquitousLanguageEngine):
    """Create a manufacturing domain language model."""
    print("🏭 Creating Manufacturing Domain Language Model...")
    
    model = engine.create_domain_model(
        domain=DomainType.MANUFACTURING,
        name="Production Line",
        description="Language model for manufacturing production line monitoring"
    )
    
    # Add manufacturing terminology
    manufacturing_terms = [
        TermDefinition(
            technical_name="oee_percentage",
            business_name="Overall Equipment Effectiveness",
            description="Measure of manufacturing productivity combining availability, performance, and quality",
            context="Production efficiency and continuous improvement",
            domain=DomainType.MANUFACTURING,
            synonyms=["OEE", "Equipment Efficiency"],
            examples=["85% OEE indicates world-class manufacturing performance"]
        ),
        TermDefinition(
            technical_name="downtime_minutes",
            business_name="Production Downtime",
            description="Time when production equipment is not operating due to failures or maintenance",
            context="Equipment reliability and maintenance planning",
            domain=DomainType.MANUFACTURING,
            synonyms=["Equipment Downtime", "Unplanned Stops"],
            examples=["Minimize downtime to maximize production output"]
        ),
        TermDefinition(
            technical_name="quality_defect_rate",
            business_name="Quality Defect Rate",
            description="Percentage of produced units that do not meet quality standards",
            context="Quality control and process improvement",
            domain=DomainType.MANUFACTURING,
            synonyms=["Defect Rate", "Quality Issues"],
            examples=["Target defect rate below 0.1% for six-sigma quality"]
        )
    ]
    
    for term in manufacturing_terms:
        model.add_term(term)
    
    # Add manufacturing concept
    oee_concept = ConceptModel(
        name="overall_equipment_effectiveness",
        definition="Comprehensive measure of manufacturing performance",
        domain=DomainType.MANUFACTURING,
        metric_type=MetricType.GAUGE,
        unit="percentage",
        normal_range={"min": 75, "max": 95},
        alert_thresholds={"warning": 70, "critical": 60},
        business_rules=[
            "OEE = Availability × Performance × Quality",
            "Calculated every hour during production",
            "World-class OEE target is 85%"
        ],
        calculation_logic="(availability * performance * quality) / 100"
    )
    
    model.add_concept(oee_concept)
    
    # Add OEE calculation rule
    oee_rule = AggregationRule(
        metric_name="hourly_oee",
        source_metrics=["availability_percent", "performance_percent", "quality_percent"],
        aggregation_function=AggregationFunction.CALCULATED,
        window_size_seconds=3600,  # 1 hour
        calculation_logic="(availability * performance * quality) / 10000",
        business_context="Hourly Overall Equipment Effectiveness calculation"
    )
    
    model.add_aggregation_rule(oee_rule)
    
    print(f"   ✅ Added {len(model.terminology)} terms")
    print(f"   ✅ Added {len(model.concepts)} concepts")
    print(f"   ✅ Added {len(model.aggregation_rules)} aggregation rules")
    
    return model


def demonstrate_language_mapping(engine: UbiquitousLanguageEngine, model, domain_name: str):
    """Demonstrate technical to business language mapping."""
    print(f"\n📝 {domain_name} Language Mapping Examples:")
    
    # Get some technical terms from the model
    technical_terms = list(model.terminology.keys())[:3]  # First 3 terms
    
    mapping = engine.map_technical_to_business(model, technical_terms)
    
    for tech_term, business_term in mapping.items():
        print(f"   Technical: '{tech_term}' → Business: '{business_term}'")


def demonstrate_model_validation(model, domain_name: str):
    """Demonstrate model validation."""
    print(f"\n✅ Validating {domain_name} Model:")
    
    result = model.validate()
    
    if result.is_valid:
        print("   ✅ Model is valid!")
    else:
        print("   ❌ Model has validation errors:")
        for error in result.errors:
            print(f"      - {error}")
    
    if result.warnings:
        print("   ⚠️ Warnings:")
        for warning in result.warnings:
            print(f"      - {warning}")
    
    if result.suggestions:
        print("   💡 Suggestions:")
        for suggestion in result.suggestions:
            print(f"      - {suggestion}")


def demonstrate_model_merging(engine: UbiquitousLanguageEngine, models: list):
    """Demonstrate merging multiple domain models."""
    print("\n🔀 Demonstrating Model Merging...")
    
    merged_model = engine.merge_language_models(
        models=models,
        target_domain=DomainType.GENERIC,
        target_name="Enterprise Monitoring"
    )
    
    print(f"   ✅ Merged {len(models)} models into unified enterprise model")
    print(f"   📊 Total terminology: {len(merged_model.terminology)} terms")
    print(f"   🧠 Total concepts: {len(merged_model.concepts)} concepts")
    print(f"   ⚙️ Total aggregation rules: {len(merged_model.aggregation_rules)} rules")
    
    # Show some merged terminology
    print("\n   📝 Sample Merged Terminology:")
    for i, (tech_name, term) in enumerate(merged_model.terminology.items()):
        if i >= 5:  # Show first 5
            break
        print(f"      {term.domain.value}: '{tech_name}' → '{term.business_name}'")
    
    return merged_model


def main():
    """Main demonstration function."""
    print("🚀 Ubiquitous Language Modeling Framework Demonstration")
    print("=" * 60)
    
    # Initialize the language engine
    engine = UbiquitousLanguageEngine()
    
    # Create domain-specific models
    healthcare_model = create_healthcare_model(engine)
    finance_model = create_finance_model(engine)
    manufacturing_model = create_manufacturing_model(engine)
    
    print(f"\n📊 Created {len(engine.get_available_models())} domain models:")
    for model_key in engine.get_available_models():
        print(f"   - {model_key}")
    
    # Demonstrate language mapping for each domain
    demonstrate_language_mapping(engine, healthcare_model, "Healthcare")
    demonstrate_language_mapping(engine, finance_model, "Finance")
    demonstrate_language_mapping(engine, manufacturing_model, "Manufacturing")
    
    # Validate all models
    demonstrate_model_validation(healthcare_model, "Healthcare")
    demonstrate_model_validation(finance_model, "Finance")
    demonstrate_model_validation(manufacturing_model, "Manufacturing")
    
    # Demonstrate model merging
    all_models = [healthcare_model, finance_model, manufacturing_model]
    merged_model = demonstrate_model_merging(engine, all_models)
    
    # Validate merged model
    demonstrate_model_validation(merged_model, "Merged Enterprise")
    
    print("\n🎯 Key Benefits Demonstrated:")
    print("   ✅ Domain-specific terminology management")
    print("   ✅ Technical to business language mapping")
    print("   ✅ Complex aggregation rule definitions")
    print("   ✅ Model validation and consistency checking")
    print("   ✅ Cross-domain model merging capabilities")
    print("   ✅ Enterprise-ready language model persistence")
    
    print("\n💡 Next Steps:")
    print("   - Integrate with OpenMetrics discovery (Task 2)")
    print("   - Build integration generation engine (Task 3)")
    print("   - Create Grafana dashboard generation (Task 5)")
    print("   - Add enterprise monitoring system discovery (Task 8)")
    
    print("\n✅ Language Modeling Framework Demo Complete!")


if __name__ == "__main__":
    main()