#!/usr/bin/env python3
"""
Demonstration of OpenMetrics Discovery and Modeling System.

This script shows the complete discovery → modeling → generation methodology
using OpenMetrics as a reference implementation.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.openmetrics_discovery import (
    MonitoringDiscoveryEngine,
    OpenMetricsDiscoveryResult
)
from beast_mode.observatory.language_modeling import (
    UbiquitousLanguageEngine,
    DomainLanguageModel
)


async def demonstrate_openmetrics_discovery():
    """Demonstrate the complete OpenMetrics discovery process."""
    print("🔍 OpenMetrics Discovery and Modeling Demonstration")
    print("=" * 60)
    
    # Initialize engines
    print("🚀 Initializing discovery engines...")
    language_engine = UbiquitousLanguageEngine()
    discovery_engine = MonitoringDiscoveryEngine(language_engine)
    
    print("✅ Engines initialized")
    print(f"   📚 Language engine ready")
    print(f"   🔍 Discovery engine loaded OpenMetrics spec v{discovery_engine._openmetrics_spec['version']}")
    
    # Step 1: Discover OpenMetrics specification
    print("\n🔍 Step 1: Discovering OpenMetrics Specification...")
    print("   (Treating OpenMetrics spec as if it were a customer's monitoring system)")
    
    discovery_result = await discovery_engine.discover_openmetrics_specification()
    
    print(f"✅ Discovery complete!")
    print(f"   📊 Metric families discovered: {len(discovery_result.metric_families)}")
    print(f"   📝 Terminology extracted: {len(discovery_result.terminology_extracted)} terms")
    print(f"   🧠 Business concepts identified: {len(discovery_result.business_concepts)}")
    print(f"   📋 Patterns discovered: {len(discovery_result.discovered_patterns)}")
    
    # Show some discovered metric families
    print("\n   📊 Sample Discovered Metric Families:")
    for i, family in enumerate(discovery_result.metric_families[:5]):
        print(f"      {i+1}. {family.name} ({family.metric_type.value})")
        print(f"         📝 {family.help_text}")
        print(f"         🏷️  Labels: {', '.join(family.labels[:3])}{'...' if len(family.labels) > 3 else ''}")
    
    # Show terminology mapping
    print("\n   📝 Sample Terminology Mapping:")
    for i, (tech_term, business_term) in enumerate(list(discovery_result.terminology_extracted.items())[:5]):
        print(f"      '{tech_term}' → '{business_term}'")
    
    # Show discovered patterns
    print("\n   📋 Sample Discovered Patterns:")
    for i, pattern in enumerate(discovery_result.discovered_patterns[:3]):
        print(f"      {i+1}. {pattern}")
    
    # Step 2: Generate language model
    print("\n📝 Step 2: Generating Domain Language Model...")
    
    language_model = await discovery_engine.generate_language_model(discovery_result)
    
    print(f"✅ Language model generated!")
    print(f"   🏷️  Domain: {language_model.domain.value}")
    print(f"   📝 Name: {language_model.name}")
    print(f"   📚 Terminology: {len(language_model.terminology)} terms")
    print(f"   🧠 Concepts: {len(language_model.concepts)} concepts")
    print(f"   ⚙️ Aggregation rules: {len(language_model.aggregation_rules)} rules")
    
    # Show some generated terminology
    print("\n   📝 Generated Terminology (Technical → Business):")
    for i, (tech_name, term) in enumerate(list(language_model.terminology.items())[:5]):
        print(f"      '{tech_name}' → '{term.business_name}'")
        print(f"         📖 {term.description}")
    
    # Show aggregation rules
    print("\n   ⚙️ Generated Aggregation Rules:")
    for rule_name, rule in language_model.aggregation_rules.items():
        print(f"      {rule_name}:")
        print(f"         📊 Function: {rule.aggregation_function.value}")
        print(f"         📈 Sources: {', '.join(rule.source_metrics)}")
        print(f"         🕐 Window: {rule.window_size_seconds}s")
        print(f"         💼 Context: {rule.business_context}")
    
    # Step 3: Validate the model
    print("\n✅ Step 3: Validating Generated Language Model...")
    
    validation_result = language_model.validate()
    
    if validation_result.is_valid:
        print("✅ Language model is valid!")
    else:
        print("❌ Language model has validation errors:")
        for error in validation_result.errors:
            print(f"   - {error}")
    
    if validation_result.warnings:
        print("⚠️ Warnings:")
        for warning in validation_result.warnings:
            print(f"   - {warning}")
    
    if validation_result.suggestions:
        print("💡 Suggestions:")
        for suggestion in validation_result.suggestions:
            print(f"   - {suggestion}")
    
    # Step 4: Generate methodology documentation
    print("\n📚 Step 4: Generating Methodology Documentation...")
    
    methodology = discovery_engine.generate_methodology_documentation()
    
    print("✅ Methodology documentation generated!")
    print(f"   📋 Process: {methodology['methodology']['name']}")
    print(f"   📝 Steps: {len(methodology['process_steps'])} documented steps")
    print(f"   🔍 Audit trail: Complete with {methodology['audit_trail']['confidence']} confidence")
    
    # Show process steps
    print("\n   📋 Documented Process Steps:")
    for step in methodology['process_steps']:
        print(f"      {step['step']}. {step['name']}")
        print(f"         📝 {step['description']}")
        print(f"         📥 Inputs: {', '.join(step['inputs'])}")
        print(f"         📤 Outputs: {', '.join(step['outputs'])}")
    
    # Show replication guide
    print("\n   🔄 Replication Guide for Enterprise Customers:")
    replication = methodology['replication_guide']
    print(f"      📖 {replication['description']}")
    print("      📋 Steps to replicate for any monitoring system:")
    for i, step in enumerate(replication['steps'], 1):
        print(f"         {i}. {step}")
    
    # Step 5: Save the language model
    print("\n💾 Step 5: Saving Language Model...")
    
    model_path = Path("examples/language_models/openmetrics_discovered.yaml")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    success = language_engine.save_model(language_model, model_path)
    
    if success:
        print(f"✅ Language model saved to: {model_path}")
        print("   📁 Model can be loaded and reused for integration generation")
    else:
        print("❌ Failed to save language model")
    
    # Step 6: Demonstrate audit trail
    print("\n📋 Step 6: Audit Trail and Traceability...")
    
    audit_records = discovery_engine.get_discovery_audit_trail()
    
    print(f"✅ Complete audit trail available!")
    print(f"   📊 Records: {len(audit_records)} discovery sessions")
    
    if audit_records:
        latest_record = audit_records[-1]
        print(f"   🔍 Latest discovery:")
        print(f"      📅 Timestamp: {latest_record.timestamp}")
        print(f"      📊 Confidence: {latest_record.confidence_score}")
        print(f"      🎯 Findings: {len(latest_record.findings)} data points")
        print(f"      ✅ Decisions: {len(latest_record.decisions_made)} documented")
        print(f"      📝 Next steps: {len(latest_record.next_steps)} identified")
    
    # Summary
    print("\n🎯 Discovery and Modeling Complete!")
    print("=" * 60)
    print("✅ Demonstrated complete methodology:")
    print("   1. 🔍 Systematic discovery of monitoring system (OpenMetrics)")
    print("   2. 📝 Terminology extraction and business mapping")
    print("   3. 🧠 Concept identification and relationship modeling")
    print("   4. ⚙️ Aggregation rule generation")
    print("   5. ✅ Model validation and consistency checking")
    print("   6. 📚 Methodology documentation generation")
    print("   7. 💾 Model persistence for reuse")
    print("   8. 📋 Complete audit trail for enterprise compliance")
    
    print("\n💡 Enterprise Value Demonstrated:")
    print("   🏢 Walk into any enterprise with existing monitoring")
    print("   🔍 Apply this exact methodology to discover their system")
    print("   📝 Generate language model using their terminology")
    print("   ⚙️ Create integrations that speak their business language")
    print("   📋 Provide complete audit trail for compliance")
    print("   🔄 Replicate process for any monitoring system")
    
    print("\n🚀 Next Steps:")
    print("   - Task 3: Build integration generation engine")
    print("   - Task 4: Implement metric processing with discovered rules")
    print("   - Task 5: Generate Grafana dashboards using business terminology")
    print("   - Task 7: Integrate with existing Observatory infrastructure")
    
    return discovery_result, language_model, methodology


async def main():
    """Main demonstration function."""
    try:
        discovery_result, language_model, methodology = await demonstrate_openmetrics_discovery()
        
        print(f"\n✅ OpenMetrics Discovery Demonstration Complete!")
        print(f"📊 Ready for integration generation and enterprise deployment")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())