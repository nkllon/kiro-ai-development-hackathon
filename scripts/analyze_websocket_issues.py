#!/usr/bin/env python3
"""
Practical WebSocket Issue Analysis using the Ontology

This script demonstrates how to use the ontology to analyze the specific
WebSocket issues documented in your system.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from beast_mode.observatory.ontology.websocket_analyzer import WebSocketOntologyAnalyzer
    
    def analyze_observatory_issues():
        """Analyze the specific Observatory WebSocket issues"""
        print("🔍 Observatory WebSocket Issue Analysis")
        print("=" * 60)
        
        # Initialize analyzer with logging
        print("🔄 Initializing WebSocket Ontology Analyzer...")
        analyzer = WebSocketOntologyAnalyzer()
        print(f"✅ Analyzer initialized with {analyzer.health_check()['triple_count']:,} triples")
        
        # Symptoms observed in your system
        observed_symptoms = [
            "websocket connection drops",
            "http polling fallback",
            "high request volume",
            "cloudflare tunnel failure",
            "protocol downgrade",
            "bot protection triggered"
        ]
        
        print(f"📋 Analyzing {len(observed_symptoms)} observed symptoms:")
        for symptom in observed_symptoms:
            print(f"   • {symptom}")
        
        # Analyze symptoms
        print(f"\n🔬 Running symptom analysis...")
        problems = analyzer.analyze_symptoms(observed_symptoms)
        print(f"📊 Symptom analysis complete")
        
        print(f"\n🎯 Identified {len(problems)} potential problems:")
        problem_uris = []
        
        for i, problem in enumerate(problems, 1):
            print(f"\n   {i}. {problem.problem_type}")
            print(f"      Confidence: {problem.confidence:.2f}")
            print(f"      URI: {problem.problem_uri}")
            problem_uris.append(problem.problem_uri)
            
            if problem.cascade_effects:
                print(f"      ⚠️  Cascade Effects: {len(problem.cascade_effects)}")
        
        # Get solution recommendations
        if problem_uris:
            print(f"\n🔧 Finding solutions for identified problems...")
            solutions = analyzer.get_solution_recommendations(problem_uris)
            
            print(f"✅ Found {len(solutions)} solution recommendations:")
            
            for i, solution in enumerate(solutions, 1):
                print(f"\n   {i}. {solution.solution_type}")
                print(f"      Implementation Time: {solution.implementation_time or 'Not specified'}")
                print(f"      Confidence: {solution.confidence:.2f}")
                print(f"      Problems Solved: {len(solution.problems_solved)}")
                
                if solution.risks_introduced:
                    print(f"      ⚠️  Risks Introduced: {len(solution.risks_introduced)}")
                if solution.risks_mitigated:
                    print(f"      ✅ Risks Mitigated: {len(solution.risks_mitigated)}")
        
        # Get immediate fixes
        print(f"\n⚡ Immediate fixes (< 2 hours):")
        immediate_fixes = analyzer.get_immediate_fixes()
        
        if immediate_fixes:
            for i, fix in enumerate(immediate_fixes, 1):
                print(f"   {i}. {fix.solution_type}")
                print(f"      Time: {fix.implementation_time}")
                print(f"      Confidence: {fix.confidence:.2f}")
        else:
            print("   No immediate fixes available in ontology")
        
        return problems, solutions, immediate_fixes
    
    def analyze_traffic_correlation():
        """Analyze traffic correlation with known patterns"""
        print(f"\n📊 Traffic Pattern Analysis")
        print("=" * 60)
        
        # Simulate the traffic data you mentioned (11k requests)
        traffic_data = {
            "request_count": 11000,
            "timestamp": "2025-09-26T00:00:00Z",
            "source": "cloudflare_analytics",
            "pattern": "midnight_spike"
        }
        
        analyzer = WebSocketOntologyAnalyzer()
        analysis = analyzer.analyze_traffic_correlation(traffic_data)
        
        print(f"Analysis timestamp: {analysis['timestamp']}")
        
        if analysis['traffic_patterns']:
            print(f"\n📈 Detected Traffic Patterns:")
            for pattern in analysis['traffic_patterns']:
                severity_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(pattern['severity'], "⚪")
                print(f"   {severity_emoji} {pattern['pattern']}: {pattern['value']:,}")
                print(f"      Threshold: {pattern['threshold']:,}")
                print(f"      Severity: {pattern['severity']}")
        
        if analysis['problem_correlations']:
            print(f"\n🔗 Problem Correlations:")
            for correlation in analysis['problem_correlations']:
                print(f"   • {correlation['correlation']} → {correlation['problem']}")
                if 'solution' in correlation:
                    print(f"     💡 Solution: {correlation['solution']}")
        
        return analysis
    
    def generate_action_plan(problems, solutions, immediate_fixes):
        """Generate actionable implementation plan"""
        print(f"\n📋 Recommended Action Plan")
        print("=" * 60)
        
        print("🚀 Phase 1: Immediate Actions (0-2 hours)")
        if immediate_fixes:
            for i, fix in enumerate(immediate_fixes, 1):
                print(f"   {i}. Implement {fix.solution_type}")
                print(f"      Expected time: {fix.implementation_time}")
                if fix.required_components:
                    print(f"      Components needed: {', '.join(fix.required_components)}")
        else:
            print("   • Review Cloudflare WebSocket settings")
            print("   • Check tunnel configuration")
            print("   • Verify SSL/TLS mode (Full Strict)")
            print("   • Implement heartbeat mechanism")
        
        print(f"\n🔧 Phase 2: Progressive Solutions (2-4 weeks)")
        progressive_solutions = [s for s in solutions if "Progressive" in s.solution_type]
        if progressive_solutions:
            for i, solution in enumerate(progressive_solutions, 1):
                print(f"   {i}. {solution.solution_type}")
                print(f"      Problems addressed: {len(solution.problems_solved)}")
        else:
            print("   • Implement hybrid architecture")
            print("   • Set up multi-region failover")
            print("   • Enhance monitoring and alerting")
        
        print(f"\n🏗️  Phase 3: Alternative Architecture (1-3 months)")
        alternative_solutions = [s for s in solutions if "Alternative" in s.solution_type]
        if alternative_solutions:
            for i, solution in enumerate(alternative_solutions, 1):
                print(f"   {i}. {solution.solution_type}")
        else:
            print("   • Evaluate direct WebSocket architecture")
            print("   • Consider multi-CDN strategy")
            print("   • Implement comprehensive observability")
        
        print(f"\n📊 Success Metrics")
        print("   • WebSocket connection success rate > 99%")
        print("   • Connection stability < 1% unexpected drops")
        print("   • Latency impact < 50ms additional through CDN")
        print("   • Heartbeat efficiency < 1KB/minute overhead")
    
    def main():
        """Main analysis workflow"""
        print("🎯 WebSocket Infrastructure Analysis")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        try:
            # Step 1: Analyze current issues
            problems, solutions, immediate_fixes = analyze_observatory_issues()
            
            # Step 2: Analyze traffic patterns
            traffic_analysis = analyze_traffic_correlation()
            
            # Step 3: Generate action plan
            generate_action_plan(problems, solutions, immediate_fixes)
            
            print(f"\n✅ Analysis complete!")
            print(f"📄 Results summary:")
            print(f"   • Problems identified: {len(problems)}")
            print(f"   • Solutions available: {len(solutions)}")
            print(f"   • Immediate fixes: {len(immediate_fixes)}")
            print(f"   • Traffic patterns: {len(traffic_analysis.get('traffic_patterns', []))}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Install dependencies with: pip install -r requirements-ontology.txt")
    sys.exit(1)