#!/usr/bin/env python3
"""
Test Planning Memory System
===========================

Test the short-term planning memory system for First Contact scenarios.
"""

from short_term_planning_memory import (
    PlanningMemoryManager, 
    create_planning_dimension, 
    create_planning_insight
)


def test_planning_memory_system():
    """Test the planning memory system"""
    
    print("🧠 TESTING PLANNING MEMORY SYSTEM")
    print("=" * 50)
    
    # Create planning memory manager
    memory_manager = PlanningMemoryManager()
    
    # Start planning session
    session_id = memory_manager.start_planning_session("DevPost Integration RMDDD Refactoring")
    print(f"✅ Started planning session: {session_id}")
    
    # Add planning dimensions
    dimensions = [
        create_planning_dimension(
            name="Verification Module RMDDD Violation",
            risk_level="high",
            unknown_factors=["What is optimal verification component size?", "How to maintain RMDDD compliance in verification?"],
            constraints=["Must maintain RMDDD compliance", "Must separate concerns", "Must create independent testable components"],
            mitigation_strategies=["Break verification into focused modules", "Separate execution/analysis/reporting", "Create verification orchestration"]
        ),
        create_planning_dimension(
            name="Short-Term Planning Memory",
            risk_level="critical",
            unknown_factors=["What information needs preservation?", "How to maintain planning context across sessions?"],
            constraints=["Must maintain planning continuity", "Must preserve critical insights", "Must enable First Contact scenarios"],
            mitigation_strategies=["Create planning memory persistence", "Implement context transfer", "Design information retrieval systems"]
        ),
        create_planning_dimension(
            name="Planning Exhaustion Analysis",
            risk_level="medium",
            unknown_factors=["What are signs of true planning exhaustion?", "How to measure planning completeness?"],
            constraints=["Must continue until genuinely out of ideas", "Must achieve adequate planning depth"],
            mitigation_strategies=["Create planning exhaustion criteria", "Implement planning continuation triggers", "Use planning depth analysis"]
        ),
        create_planning_dimension(
            name="Planning Recursion Management",
            risk_level="high",
            unknown_factors=["How to manage planning recursion?", "When does planning recursion become infinite?"],
            constraints=["Must manage planning recursion", "Must prevent infinite loops"],
            mitigation_strategies=["Create planning recursion management", "Implement recursion controls", "Use recursion validation"]
        )
    ]
    
    for dimension in dimensions:
        memory_manager.add_planning_dimension(dimension)
    
    # Add planning insights
    insights = [
        create_planning_insight(
            insight_type="architecture",
            title="Verification System RMDDD Violation",
            description="The verification module itself is getting too big and violates RMDDD principles",
            importance="critical",
            related_dimensions=["Verification Module RMDDD Violation"]
        ),
        create_planning_insight(
            insight_type="risk",
            title="Planning Context Loss",
            description="Without planning memory, each new contact starts from scratch",
            importance="critical",
            related_dimensions=["Short-Term Planning Memory"]
        ),
        create_planning_insight(
            insight_type="constraint",
            title="Planning Exhaustion Criteria",
            description="Need clear criteria for when planning is truly exhausted vs just stopping early",
            importance="high",
            related_dimensions=["Planning Exhaustion Analysis"]
        ),
        create_planning_insight(
            insight_type="unknown",
            title="Planning Recursion Depth",
            description="Planning is a fractal process where each level reveals new dimensions",
            importance="high",
            related_dimensions=["Planning Recursion Management"]
        )
    ]
    
    for insight in insights:
        memory_manager.add_planning_insight(insight)
    
    # Update planning metrics
    memory_manager.update_planning_depth(40)  # 40 dimensions identified
    memory_manager.update_planning_exhaustion(0.7)  # 70% exhausted
    
    # Create First Contact scenario
    scenario = memory_manager.create_first_contact_scenario("DevPost RMDDD Refactoring First Contact")
    print(f"✅ Created First Contact scenario: {scenario.scenario_name}")
    
    # Get planning summary
    summary = memory_manager.get_planning_summary()
    print(f"\n📊 PLANNING SUMMARY")
    print("=" * 30)
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Save planning memory
    filepath = memory_manager.save_planning_memory()
    print(f"✅ Saved planning memory to: {filepath}")
    
    # Test loading planning memory
    new_memory_manager = PlanningMemoryManager()
    new_memory_manager.load_planning_memory(filepath)
    
    # Verify loaded data
    loaded_summary = new_memory_manager.get_planning_summary()
    print(f"\n📂 LOADED PLANNING SUMMARY")
    print("=" * 30)
    for key, value in loaded_summary.items():
        print(f"{key}: {value}")
    
    # Verify data integrity
    assert summary["session_id"] == loaded_summary["session_id"]
    assert summary["total_dimensions"] == loaded_summary["total_dimensions"]
    assert summary["total_risks"] == loaded_summary["total_risks"]
    assert summary["total_unknowns"] == loaded_summary["total_unknowns"]
    assert summary["total_constraints"] == loaded_summary["total_constraints"]
    assert summary["total_mitigations"] == loaded_summary["total_mitigations"]
    assert summary["planning_depth"] == loaded_summary["planning_depth"]
    assert summary["planning_exhaustion_level"] == loaded_summary["planning_exhaustion_level"]
    assert summary["insights_count"] == loaded_summary["insights_count"]
    assert summary["scenarios_count"] == loaded_summary["scenarios_count"]
    
    print("✅ All data integrity checks passed!")
    
    # Display First Contact scenario details
    print(f"\n🎯 FIRST CONTACT SCENARIO")
    print("=" * 30)
    print(f"Scenario: {scenario.scenario_name}")
    print(f"Created: {scenario.created_at}")
    print(f"Key Insights: {len(scenario.key_insights)}")
    print(f"Success Criteria: {len(scenario.success_criteria)}")
    
    print(f"\n💡 KEY INSIGHTS:")
    for insight in scenario.key_insights:
        print(f"   • {insight.title} ({insight.importance})")
    
    print(f"\n🎯 SUCCESS CRITERIA:")
    for criterion in scenario.success_criteria:
        print(f"   • {criterion}")
    
    print(f"\n🔧 DECISION FRAMEWORK:")
    df = scenario.decision_framework
    print(f"   Critical Risks: {len(df['risk_assessment']['critical_risks'])}")
    print(f"   Critical Constraints: {len(df['constraint_analysis']['critical_constraints'])}")
    print(f"   Critical Unknowns: {len(df['unknown_factors']['critical_unknowns'])}")
    print(f"   Planning Exhaustion: {df['planning_completeness']['exhaustion_level']:.1%}")
    print(f"   Planning Depth: {df['planning_completeness']['depth']}")
    
    print(f"\n🎉 PLANNING MEMORY SYSTEM TEST COMPLETED SUCCESSFULLY!")
    return True


if __name__ == "__main__":
    test_planning_memory_system()
