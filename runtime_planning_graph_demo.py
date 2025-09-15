#!/usr/bin/env python3
"""
Runtime Planning Graph Demo
==========================

Demonstrates how to load and use the planning graph at runtime
for dynamic analysis, cross-referencing, and intelligent decision-making.
"""

import json
from typing import Dict, Any, List, Optional
from planning_graph_serializer import PlanningGraphLoader


class RuntimePlanningAnalyzer:
    """Runtime analyzer for planning graphs"""
    
    def __init__(self, graph_file: str):
        self.loader = PlanningGraphLoader(graph_file)
        self.graph = self.loader.graph
        self.nodes = self.loader.nodes
        self.edges = self.loader.edges
    
    def analyze_risk_landscape(self) -> Dict[str, Any]:
        """Analyze the overall risk landscape"""
        risk_analysis = {
            "total_risks": 0,
            "risk_distribution": {},
            "critical_paths": [],
            "mitigation_coverage": {},
            "unmitigated_risks": []
        }
        
        # Analyze risk distribution
        dimensions = self.loader.find_nodes_by_type("dimension")
        for dimension in dimensions:
            risk_level = dimension.get('risk_level')
            if risk_level:
                risk_analysis["risk_distribution"][risk_level] = \
                    risk_analysis["risk_distribution"].get(risk_level, 0) + 1
                risk_analysis["total_risks"] += 1
        
        # Check mitigation coverage
        for dimension in dimensions:
            dim_id = dimension['id']
            mitigations = self.loader.get_related_nodes(dim_id, "has_mitigation")
            risk_level = dimension.get('risk_level', 'unknown')
            
            if risk_level not in risk_analysis["mitigation_coverage"]:
                risk_analysis["mitigation_coverage"][risk_level] = {
                    "total_dimensions": 0,
                    "mitigated_dimensions": 0,
                    "mitigation_count": 0
                }
            
            risk_analysis["mitigation_coverage"][risk_level]["total_dimensions"] += 1
            
            if mitigations:
                risk_analysis["mitigation_coverage"][risk_level]["mitigated_dimensions"] += 1
                risk_analysis["mitigation_coverage"][risk_level]["mitigation_count"] += len(mitigations)
            else:
                risk_analysis["unmitigated_risks"].append({
                    "dimension": dimension['title'],
                    "risk_level": risk_level
                })
        
        return risk_analysis
    
    def find_planning_gaps(self) -> List[Dict[str, Any]]:
        """Find gaps in planning coverage"""
        gaps = []
        
        # Check for dimensions with no mitigations
        dimensions = self.loader.find_nodes_by_type("dimension")
        for dimension in dimensions:
            dim_id = dimension['id']
            mitigations = self.loader.get_related_nodes(dim_id, "has_mitigation")
            
            if not mitigations:
                gaps.append({
                    "type": "unmitigated_risk",
                    "dimension": dimension['title'],
                    "risk_level": dimension.get('risk_level'),
                    "description": "Dimension has no mitigation strategies"
                })
        
        # Check for unknown factors without exploration
        unknown_factors = self.loader.find_nodes_by_type("unknown_factor")
        for unknown in unknown_factors:
            # Check if there are related exploration or analysis nodes
            related = self.loader.get_related_nodes(unknown['id'])
            if not related:
                gaps.append({
                    "type": "unexplored_unknown",
                    "unknown": unknown['title'],
                    "description": "Unknown factor has no exploration or analysis"
                })
        
        return gaps
    
    def suggest_next_actions(self) -> List[Dict[str, Any]]:
        """Suggest next actions based on planning analysis"""
        actions = []
        
        # Get critical risks
        critical_risks = self.loader.find_nodes_by_risk_level("critical")
        for risk in critical_risks:
            actions.append({
                "priority": "critical",
                "action": "Address Critical Risk",
                "target": risk['title'],
                "description": f"Immediate attention required for: {risk['title']}",
                "estimated_effort": "high"
            })
        
        # Get high risks without mitigations
        high_risks = self.loader.find_nodes_by_risk_level("high")
        for risk in high_risks:
            mitigations = self.loader.get_related_nodes(risk['id'], "has_mitigation")
            if not mitigations:
                actions.append({
                    "priority": "high",
                    "action": "Develop Mitigation Strategy",
                    "target": risk['title'],
                    "description": f"High-risk dimension needs mitigation strategies",
                    "estimated_effort": "medium"
                })
        
        # Get unexplored unknowns
        unknown_factors = self.loader.find_nodes_by_type("unknown_factor")
        for unknown in unknown_factors[:3]:  # Top 3 unknowns
            actions.append({
                "priority": "medium",
                "action": "Explore Unknown Factor",
                "target": unknown['title'],
                "description": f"Investigate and analyze: {unknown['title']}",
                "estimated_effort": "low"
            })
        
        return actions
    
    def get_planning_context(self, node_id: str) -> Dict[str, Any]:
        """Get comprehensive context for a specific node"""
        if node_id not in self.nodes:
            return {"error": "Node not found"}
        
        node = self.nodes[node_id]
        context = {
            "node": node,
            "related_nodes": self.loader.get_related_nodes(node_id),
            "neighbors": self.graph.neighbors(node_id),
            "context_analysis": {}
        }
        
        # Analyze relationships
        relationship_types = {}
        for related in context["related_nodes"]:
            rel_type = related['relationship']
            if rel_type not in relationship_types:
                relationship_types[rel_type] = []
            relationship_types[rel_type].append(related['node']['title'])
        
        context["context_analysis"]["relationship_types"] = relationship_types
        
        # Get risk context
        if node.get('risk_level'):
            context["context_analysis"]["risk_context"] = {
                "risk_level": node['risk_level'],
                "confidence": node.get('confidence'),
                "status": node.get('status')
            }
        
        return context
    
    def generate_planning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive planning report"""
        report = {
            "summary": self.loader.get_planning_summary(),
            "risk_analysis": self.analyze_risk_landscape(),
            "planning_gaps": self.find_planning_gaps(),
            "suggested_actions": self.suggest_next_actions(),
            "planning_health": self.assess_planning_health()
        }
        
        return report
    
    def assess_planning_health(self) -> Dict[str, Any]:
        """Assess the overall health of the planning"""
        dimensions = self.loader.find_nodes_by_type("dimension")
        total_dimensions = len(dimensions)
        
        # Count dimensions with mitigations
        mitigated_dimensions = 0
        for dimension in dimensions:
            mitigations = self.loader.get_related_nodes(dimension['id'], "has_mitigation")
            if mitigations:
                mitigated_dimensions += 1
        
        # Count unknown factors
        unknown_factors = self.loader.find_nodes_by_type("unknown_factor")
        
        # Count constraints
        constraints = self.loader.find_nodes_by_type("constraint")
        
        health_score = 0.0
        if total_dimensions > 0:
            health_score += (mitigated_dimensions / total_dimensions) * 40  # 40% for mitigation coverage
            health_score += min(len(unknown_factors) / (total_dimensions * 2), 1.0) * 30  # 30% for unknown exploration
            health_score += min(len(constraints) / (total_dimensions * 2), 1.0) * 30  # 30% for constraint identification
        
        return {
            "overall_score": health_score,
            "mitigation_coverage": mitigated_dimensions / total_dimensions if total_dimensions > 0 else 0,
            "unknown_exploration": len(unknown_factors),
            "constraint_identification": len(constraints),
            "total_dimensions": total_dimensions,
            "health_level": "excellent" if health_score > 0.8 else "good" if health_score > 0.6 else "needs_improvement"
        }


def main():
    """Main function to demonstrate runtime planning graph analysis"""
    print("🧠 RUNTIME PLANNING GRAPH ANALYSIS")
    print("=" * 60)
    
    # Load the planning graph
    analyzer = RuntimePlanningAnalyzer("planning_graph.json")
    
    # Generate comprehensive report
    print("📊 Generating comprehensive planning report...")
    report = analyzer.generate_planning_report()
    
    # Display summary
    print(f"\n📋 PLANNING SUMMARY:")
    summary = report['summary']
    print(f"   Total Nodes: {summary['total_nodes']}")
    print(f"   Total Edges: {summary['total_edges']}")
    print(f"   Node Types: {summary['node_types']}")
    print(f"   Risk Levels: {summary['risk_levels']}")
    
    # Display risk analysis
    print(f"\n🎯 RISK ANALYSIS:")
    risk_analysis = report['risk_analysis']
    print(f"   Total Risks: {risk_analysis['total_risks']}")
    print(f"   Risk Distribution: {risk_analysis['risk_distribution']}")
    
    print(f"\n🛡️ MITIGATION COVERAGE:")
    for risk_level, coverage in risk_analysis['mitigation_coverage'].items():
        coverage_pct = (coverage['mitigated_dimensions'] / coverage['total_dimensions'] * 100) if coverage['total_dimensions'] > 0 else 0
        print(f"   {risk_level.upper()}: {coverage['mitigated_dimensions']}/{coverage['total_dimensions']} dimensions ({coverage_pct:.1f}%)")
    
    # Display planning health
    print(f"\n🏥 PLANNING HEALTH:")
    health = report['planning_health']
    print(f"   Overall Score: {health['overall_score']:.2f}")
    print(f"   Health Level: {health['health_level']}")
    print(f"   Mitigation Coverage: {health['mitigation_coverage']:.2f}")
    print(f"   Unknown Factors: {health['unknown_exploration']}")
    print(f"   Constraints: {health['constraint_identification']}")
    
    # Display planning gaps
    print(f"\n🔍 PLANNING GAPS:")
    gaps = report['planning_gaps']
    if gaps:
        for gap in gaps[:5]:  # Show first 5 gaps
            print(f"   • {gap['type']}: {gap.get('dimension', gap.get('unknown', 'Unknown'))}")
    else:
        print("   ✅ No significant planning gaps identified")
    
    # Display suggested actions
    print(f"\n🎯 SUGGESTED NEXT ACTIONS:")
    actions = report['suggested_actions']
    for action in actions[:5]:  # Show first 5 actions
        print(f"   [{action['priority'].upper()}] {action['action']}")
        print(f"      Target: {action['target']}")
        print(f"      Effort: {action['estimated_effort']}")
        print()
    
    # Example: Get context for a specific dimension
    print(f"\n🔍 EXAMPLE: CONTEXT ANALYSIS")
    dimensions = analyzer.loader.find_nodes_by_type("dimension")
    if dimensions:
        first_dimension = dimensions[0]
        context = analyzer.get_planning_context(first_dimension['id'])
        print(f"   Dimension: {first_dimension['title']}")
        print(f"   Risk Level: {first_dimension.get('risk_level', 'N/A')}")
        print(f"   Related Nodes: {len(context['related_nodes'])}")
        print(f"   Neighbors: {len(context['neighbors'])}")
        
        if context['context_analysis'].get('relationship_types'):
            print(f"   Relationship Types:")
            for rel_type, nodes in context['context_analysis']['relationship_types'].items():
                print(f"     • {rel_type}: {len(nodes)} nodes")
    
    print(f"\n✅ Runtime planning graph analysis complete!")
    print(f"   The planning graph is loaded and ready for dynamic analysis!")


if __name__ == "__main__":
    main()


