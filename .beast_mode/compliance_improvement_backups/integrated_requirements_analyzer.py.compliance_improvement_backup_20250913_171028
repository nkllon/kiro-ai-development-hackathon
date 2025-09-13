#!/usr/bin/env python3
"""
Integrated Requirements Analyzer

This tool integrates the enhanced registry with requirements analysis to provide
a comprehensive view of interface requirements and their consistency.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import our enhanced registry
try:
    from enhanced_interface_registry import EnhancedInterfaceRegistry, AmbiguityIssue
    from requirements_analyzer import RequirementsAnalyzer, RequirementsAnalysisResult
except ImportError:
    try:
        from .enhanced_interface_registry import EnhancedInterfaceRegistry, AmbiguityIssue
        from .requirements_analyzer import RequirementsAnalyzer, RequirementsAnalysisResult
    except ImportError as e:
        print(f"Warning: Could not import enhanced registry components: {e}")
        print("Please run from the src/rm_ddd/core/ directory or ensure modules are in Python path")
        sys.exit(1)

@dataclass
class IntegratedAnalysisResult:
    """Results of integrated requirements and interface analysis"""
    enhanced_registry_results: Dict[str, Any]
    requirements_analysis: RequirementsAnalysisResult
    integration_insights: List[str]
    priority_actions: List[str]
    analysis_timestamp: str

class IntegratedRequirementsAnalyzer:
    """Integrated analyzer combining enhanced registry and requirements analysis"""
    
    def __init__(self, codebase_path: str = "src"):
        self.codebase_path = codebase_path
        self.enhanced_registry = EnhancedInterfaceRegistry()
        self.requirements_analyzer = RequirementsAnalyzer(codebase_path)
        
        # Adjust codebase path if running from core directory
        if Path.cwd().name == "core" and not Path(codebase_path).exists():
            # We're in core directory, go up to find src
            self.codebase_path = str(Path.cwd().parent.parent)
            self.requirements_analyzer = RequirementsAnalyzer(self.codebase_path)
        
    def run_integrated_analysis(self) -> IntegratedAnalysisResult:
        """Run integrated analysis combining registry and requirements"""
        print("🔍 Integrated Requirements and Interface Analysis")
        print("=" * 60)
        
        # Step 1: Run enhanced registry analysis
        print("📋 Step 1: Running enhanced registry analysis...")
        enhanced_results = self._run_enhanced_registry_analysis()
        
        # Step 2: Extract ambiguous interfaces
        print("\n🎯 Step 2: Extracting ambiguous interfaces...")
        ambiguous_interfaces = self._extract_ambiguous_interfaces(enhanced_results)
        
        # Step 3: Run requirements analysis
        print(f"\n📊 Step 3: Analyzing requirements for {len(ambiguous_interfaces)} ambiguous interfaces...")
        requirements_analysis = self.requirements_analyzer.analyze_requirements(ambiguous_interfaces)
        
        # Step 4: Generate integration insights
        print("\n🔗 Step 4: Generating integration insights...")
        integration_insights = self._generate_integration_insights(enhanced_results, requirements_analysis)
        
        # Step 5: Generate priority actions
        print("\n⚡ Step 5: Generating priority actions...")
        priority_actions = self._generate_priority_actions(enhanced_results, requirements_analysis)
        
        return IntegratedAnalysisResult(
            enhanced_registry_results=enhanced_results,
            requirements_analysis=requirements_analysis,
            integration_insights=integration_insights,
            priority_actions=priority_actions,
            analysis_timestamp=enhanced_results.get('analysis_timestamp', 'unknown')
        )
    
    def _run_enhanced_registry_analysis(self) -> Dict[str, Any]:
        """Run the enhanced registry analysis"""
        # Discover implementations
        implementations = self.enhanced_registry.discover_implementations(self.codebase_path)
        
        # Detect ambiguities
        ambiguities = self.enhanced_registry.detect_ambiguities(self.codebase_path)
        
        # Get unified status
        unified_status = self.enhanced_registry.get_unified_registry_status()
        
        # Test ubiquitous language search
        search_results = self.enhanced_registry.search_by_ubiquitous_language(['interface', 'registry'])
        
        from datetime import datetime
        return {
            'implementations': implementations,
            'ambiguities': ambiguities,
            'unified_status': unified_status,
            'search_results': search_results,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _extract_ambiguous_interfaces(self, enhanced_results: Dict[str, Any]) -> List[str]:
        """Extract ambiguous interfaces from enhanced registry results"""
        ambiguous_interfaces = set()
        
        # Extract from ambiguities
        for ambiguity in enhanced_results.get('ambiguities', []):
            if hasattr(ambiguity, 'interface_name'):
                ambiguous_interfaces.add(ambiguity.interface_name)
            elif isinstance(ambiguity, dict) and 'interface_name' in ambiguity:
                ambiguous_interfaces.add(ambiguity['interface_name'])
        
        # Extract from implementations with conflicts
        for impl in enhanced_results.get('implementations', []):
            if hasattr(impl, 'conflicts') and impl.conflicts:
                if hasattr(impl, 'interface_name'):
                    ambiguous_interfaces.add(impl.interface_name)
            elif isinstance(impl, dict) and impl.get('conflicts'):
                ambiguous_interfaces.add(impl.get('interface_name', ''))
        
        return list(ambiguous_interfaces)
    
    def _generate_integration_insights(self, enhanced_results: Dict[str, Any], 
                                     requirements_analysis: RequirementsAnalysisResult) -> List[str]:
        """Generate insights from integrating registry and requirements analysis"""
        insights = []
        
        # Registry insights
        total_implementations = len(enhanced_results.get('implementations', []))
        total_ambiguities = len(enhanced_results.get('ambiguities', []))
        
        insights.append(f"📊 Registry Discovery: {total_implementations} implementations, {total_ambiguities} ambiguities")
        
        # Requirements insights
        analyzed_interfaces = requirements_analysis.analyzed_interfaces
        ambiguous_interfaces = requirements_analysis.ambiguous_interfaces
        avg_consistency = sum(req.consistency_score for req in requirements_analysis.interface_requirements) / max(1, len(requirements_analysis.interface_requirements))
        
        insights.append(f"📋 Requirements Analysis: {analyzed_interfaces} interfaces analyzed, {ambiguous_interfaces} ambiguous")
        insights.append(f"📈 Average consistency score: {avg_consistency:.2f}")
        
        # Integration patterns
        if total_ambiguities > 0 and ambiguous_interfaces > 0:
            insights.append("🔗 Integration Pattern: Registry ambiguities correlate with requirements inconsistencies")
            insights.append("💡 Insight: Interface ambiguity often stems from conflicting requirements")
        
        # Quality indicators
        if avg_consistency < 0.5:
            insights.append("⚠️  Quality Alert: Low consistency scores indicate significant requirements conflicts")
        elif avg_consistency > 0.8:
            insights.append("✅ Quality Indicator: High consistency scores indicate well-defined requirements")
        
        return insights
    
    def _generate_priority_actions(self, enhanced_results: Dict[str, Any], 
                                 requirements_analysis: RequirementsAnalysisResult) -> List[str]:
        """Generate priority actions based on integrated analysis"""
        actions = []
        
        # High priority: Critical ambiguities
        critical_ambiguities = [
            req for req in requirements_analysis.interface_requirements
            if req.consistency_score < 0.3 and req.ambiguity_type != 'none'
        ]
        
        if critical_ambiguities:
            actions.append("🚨 HIGH PRIORITY: Resolve critical interface ambiguities")
            for req in critical_ambiguities[:3]:  # Top 3
                actions.append(f"   - {req.interface_name} (consistency: {req.consistency_score:.2f})")
        
        # Medium priority: Requirements consolidation
        interface_spec_conflicts = [
            req for req in requirements_analysis.interface_requirements
            if req.ambiguity_type == 'interface_specification_mismatch'
        ]
        
        if interface_spec_conflicts:
            actions.append("🔧 MEDIUM PRIORITY: Consolidate interface specifications")
            actions.append(f"   - {len(interface_spec_conflicts)} interfaces need specification alignment")
        
        # Low priority: Documentation and testing
        test_impl_conflicts = [
            req for req in requirements_analysis.interface_requirements
            if req.ambiguity_type == 'test_implementation_mismatch'
        ]
        
        if test_impl_conflicts:
            actions.append("📝 LOW PRIORITY: Align test cases with implementations")
            actions.append(f"   - {len(test_impl_conflicts)} interfaces need test alignment")
        
        # General actions
        actions.append("📋 GENERAL: Create single source of truth for each interface")
        actions.append("🔍 GENERAL: Establish clear interface ownership and governance")
        
        return actions

def main():
    """Main CLI function"""
    print("🔍 Integrated Requirements and Interface Analysis")
    print("=" * 60)
    
    # Create integrated analyzer
    analyzer = IntegratedRequirementsAnalyzer()
    
    # Run integrated analysis
    result = analyzer.run_integrated_analysis()
    
    # Display results
    print("\n📊 Integrated Analysis Results:")
    print("=" * 40)
    
    # Enhanced registry results
    print("\n🔍 Enhanced Registry Results:")
    print(f"  📋 Implementations: {len(result.enhanced_registry_results.get('implementations', []))}")
    print(f"  ⚠️  Ambiguities: {len(result.enhanced_registry_results.get('ambiguities', []))}")
    print(f"  🔍 Search matches: {len(result.enhanced_registry_results.get('search_results', []))}")
    
    # Requirements analysis results
    print("\n📋 Requirements Analysis Results:")
    print(f"  ✅ Interfaces analyzed: {result.requirements_analysis.analyzed_interfaces}")
    print(f"  ⚠️  Ambiguous interfaces: {result.requirements_analysis.ambiguous_interfaces}")
    print(f"  🔧 Inconsistent requirements: {result.requirements_analysis.inconsistent_requirements}")
    
    # Integration insights
    print("\n🔗 Integration Insights:")
    for insight in result.integration_insights:
        print(f"  {insight}")
    
    # Priority actions
    print("\n⚡ Priority Actions:")
    for action in result.priority_actions:
        print(f"  {action}")
    
    # Detailed interface analysis
    print("\n🔍 Detailed Interface Analysis:")
    print("-" * 40)
    
    for req in result.requirements_analysis.interface_requirements:
        print(f"\n📋 Interface: {req.interface_name}")
        print(f"   📊 Consistency: {req.consistency_score:.2f}")
        print(f"   🔍 Ambiguity: {req.ambiguity_type}")
        print(f"   📝 Sources: {len(req.requirement_sources)}")
        
        if req.conflicting_requirements:
            print(f"   ⚠️  Conflicts: {len(req.conflicting_requirements)}")
            for conflict in req.conflicting_requirements:
                print(f"      - {conflict.requirement_type} in {conflict.file_path}:{conflict.line_number}")
        
        if req.resolution_suggestions:
            print(f"   💡 Suggestions:")
            for suggestion in req.resolution_suggestions:
                print(f"      {suggestion}")
    
    print(f"\n⏰ Analysis completed at: {result.analysis_timestamp}")
    print("✅ Integrated analysis complete!")
    
    # Save results to file
    results_file = "integrated_analysis_results.json"
    with open(results_file, 'w') as f:
        # Convert dataclasses to dict for JSON serialization
        result_dict = {
            'enhanced_registry_results': result.enhanced_registry_results,
            'requirements_analysis': asdict(result.requirements_analysis),
            'integration_insights': result.integration_insights,
            'priority_actions': result.priority_actions,
            'analysis_timestamp': result.analysis_timestamp
        }
        json.dump(result_dict, f, indent=2, default=str)
    
    print(f"💾 Results saved to: {results_file}")

if __name__ == "__main__":
    main()
