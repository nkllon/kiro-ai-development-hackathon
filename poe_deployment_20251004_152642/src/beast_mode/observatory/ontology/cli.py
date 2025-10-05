#!/usr/bin/env python3
"""
WebSocket Ontology Analysis CLI

Command-line interface for querying and analyzing the WebSocket infrastructure ontology.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from .websocket_analyzer import WebSocketOntologyAnalyzer, ProblemAnalysis, SolutionRecommendation

def analyze_symptoms_command(analyzer: WebSocketOntologyAnalyzer, symptoms: List[str]) -> None:
    """Analyze symptoms and display results"""
    print(f"🔍 Analyzing symptoms: {', '.join(symptoms)}")
    print("=" * 60)
    
    problems = analyzer.analyze_symptoms(symptoms)
    
    if not problems:
        print("❌ No problems found matching the provided symptoms")
        return
    
    for i, problem in enumerate(problems, 1):
        print(f"\n📋 Problem {i}: {problem.problem_type}")
        print(f"   URI: {problem.problem_uri}")
        print(f"   Confidence: {problem.confidence:.2f}")
        
        if problem.symptoms:
            print(f"   Symptoms: {', '.join(problem.symptoms)}")
        
        if problem.root_causes:
            print(f"   Root Causes: {', '.join(problem.root_causes)}")
        
        if problem.cascade_effects:
            print(f"   Cascade Effects: {', '.join(problem.cascade_effects)}")
        
        if problem.affected_components:
            print(f"   Affected Components: {', '.join(problem.affected_components)}")

def get_solutions_command(analyzer: WebSocketOntologyAnalyzer, problem_uris: List[str]) -> None:
    """Get solution recommendations for problems"""
    print(f"🔧 Finding solutions for {len(problem_uris)} problems")
    print("=" * 60)
    
    solutions = analyzer.get_solution_recommendations(problem_uris)
    
    if not solutions:
        print("❌ No solutions found for the provided problems")
        return
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n🛠️  Solution {i}: {solution.solution_type}")
        print(f"   URI: {solution.solution_uri}")
        print(f"   Confidence: {solution.confidence:.2f}")
        
        if solution.implementation_time:
            print(f"   Implementation Time: {solution.implementation_time}")
        
        if solution.problems_solved:
            print(f"   Solves Problems: {len(solution.problems_solved)} problems")
        
        if solution.required_components:
            print(f"   Required Components: {', '.join(solution.required_components)}")
        
        if solution.risks_introduced:
            print(f"   ⚠️  Risks Introduced: {len(solution.risks_introduced)} risks")
        
        if solution.risks_mitigated:
            print(f"   ✅ Risks Mitigated: {len(solution.risks_mitigated)} risks")
        
        if solution.constraints:
            print(f"   🚧 Constraints: {len(solution.constraints)} constraints")

def immediate_fixes_command(analyzer: WebSocketOntologyAnalyzer) -> None:
    """Get immediate fix solutions (< 2 hours)"""
    print("⚡ Finding immediate fixes (< 2 hours implementation)")
    print("=" * 60)
    
    solutions = analyzer.get_immediate_fixes()
    
    if not solutions:
        print("❌ No immediate fixes available")
        return
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n🚀 Immediate Fix {i}: {solution.solution_type}")
        print(f"   URI: {solution.solution_uri}")
        print(f"   Implementation Time: {solution.implementation_time}")
        print(f"   Confidence: {solution.confidence:.2f}")
        
        if solution.problems_solved:
            print(f"   Solves: {', '.join(solution.problems_solved)}")
        
        if solution.required_components:
            print(f"   Requires: {', '.join(solution.required_components)}")

def cascade_analysis_command(analyzer: WebSocketOntologyAnalyzer, initial_problem: str) -> None:
    """Analyze potential cascade failures"""
    print(f"🌊 Analyzing cascade failures from: {initial_problem}")
    print("=" * 60)
    
    cascade_problems = analyzer.query_cascade_failures(initial_problem)
    
    if not cascade_problems:
        print("✅ No cascade failures identified")
        return
    
    print(f"⚠️  Found {len(cascade_problems)} potential cascade failures:")
    for i, problem in enumerate(cascade_problems, 1):
        print(f"   {i}. {problem}")

def traffic_analysis_command(analyzer: WebSocketOntologyAnalyzer, traffic_file: Path) -> None:
    """Analyze traffic data correlation"""
    print(f"📊 Analyzing traffic data from: {traffic_file}")
    print("=" * 60)
    
    try:
        with open(traffic_file, 'r') as f:
            traffic_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading traffic data: {e}")
        return
    
    analysis = analyzer.analyze_traffic_correlation(traffic_data)
    
    print(f"Analysis timestamp: {analysis['timestamp']}")
    
    if analysis['traffic_patterns']:
        print(f"\n📈 Traffic Patterns ({len(analysis['traffic_patterns'])}):")
        for pattern in analysis['traffic_patterns']:
            print(f"   • {pattern['pattern']}: {pattern['value']} (severity: {pattern['severity']})")
    
    if analysis['problem_correlations']:
        print(f"\n🔗 Problem Correlations ({len(analysis['problem_correlations'])}):")
        for correlation in analysis['problem_correlations']:
            print(f"   • {correlation['correlation']} → {correlation['problem']}")
            if 'solution' in correlation:
                print(f"     Solution: {correlation['solution']}")

def health_check_command(analyzer: WebSocketOntologyAnalyzer) -> None:
    """Check ontology analyzer health"""
    print("🏥 Ontology Analyzer Health Check")
    print("=" * 60)
    
    health = analyzer.health_check()
    
    status_emoji = "✅" if health['status'] == 'healthy' else "❌"
    print(f"{status_emoji} Status: {health['status']}")
    print(f"📚 Ontology Loaded: {health['ontology_loaded']}")
    print(f"🔢 Triple Count: {health['triple_count']:,}")
    print(f"🏷️  Namespaces: {health['namespaces']}")
    print(f"📦 RDFLib Available: {health['rdflib_available']}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WebSocket Ontology Analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze symptoms
  python -m src.beast_mode.observatory.ontology.cli analyze-symptoms "connection drops" "high latency"
  
  # Get immediate fixes
  python -m src.beast_mode.observatory.ontology.cli immediate-fixes
  
  # Analyze cascade failures
  python -m src.beast_mode.observatory.ontology.cli cascade-analysis "ws:TunnelFailure"
  
  # Health check
  python -m src.beast_mode.observatory.ontology.cli health-check
        """
    )
    
    parser.add_argument(
        "--ontology", 
        type=Path, 
        default=Path("docs/ontology/websocket_ontology.ttl"),
        help="Path to ontology file"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze symptoms command
    symptoms_parser = subparsers.add_parser('analyze-symptoms', help='Analyze observed symptoms')
    symptoms_parser.add_argument('symptoms', nargs='+', help='List of observed symptoms')
    
    # Get solutions command
    solutions_parser = subparsers.add_parser('get-solutions', help='Get solution recommendations')
    solutions_parser.add_argument('problem_uris', nargs='+', help='List of problem URIs')
    
    # Immediate fixes command
    subparsers.add_parser('immediate-fixes', help='Get immediate fix solutions')
    
    # Cascade analysis command
    cascade_parser = subparsers.add_parser('cascade-analysis', help='Analyze cascade failures')
    cascade_parser.add_argument('initial_problem', help='Initial problem URI')
    
    # Traffic analysis command
    traffic_parser = subparsers.add_parser('traffic-analysis', help='Analyze traffic correlation')
    traffic_parser.add_argument('traffic_file', type=Path, help='Path to traffic data JSON file')
    
    # Health check command
    subparsers.add_parser('health-check', help='Check analyzer health')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize analyzer
        print(f"🔄 Loading ontology from: {args.ontology}")
        analyzer = WebSocketOntologyAnalyzer(args.ontology)
        print(f"✅ Loaded {analyzer.health_check()['triple_count']:,} triples\n")
        
        # Execute command
        if args.command == 'analyze-symptoms':
            analyze_symptoms_command(analyzer, args.symptoms)
        elif args.command == 'get-solutions':
            get_solutions_command(analyzer, args.problem_uris)
        elif args.command == 'immediate-fixes':
            immediate_fixes_command(analyzer)
        elif args.command == 'cascade-analysis':
            cascade_analysis_command(analyzer, args.initial_problem)
        elif args.command == 'traffic-analysis':
            traffic_analysis_command(analyzer, args.traffic_file)
        elif args.command == 'health-check':
            health_check_command(analyzer)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()