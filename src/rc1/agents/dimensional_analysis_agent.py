"""
Dimensional Analysis Agent - Analyze dimensional hierarchies
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentResult


class DimensionalAnalysisAgent(BaseAgent):
    """Independent agent for dimensional hierarchy analysis"""
    
    def __init__(self):
        super().__init__("DimensionalAnalysisAgent")
        self.dimensions = [
            'temporal', 'spatial', 'semantic', 'structural', 'quality', 'security',
            'performance', 'dependency', 'architecture', 'technology', 'stakeholder',
            'process', 'lifecycle', 'governance', 'knowledge', 'maintenance',
            'document_type', 'complexity', 'audience', 'urgency'
        ]
    
    def execute(self) -> AgentResult:
        """Independent execution of dimensional analysis"""
        self._start_execution()
        
        try:
            # Analyze all dimensional hierarchies
            dimensional_hierarchies = self._analyze_dimensional_hierarchies()
            self._set_data("dimensional_hierarchies", dimensional_hierarchies)
            
            # Map dimensional relationships
            relationships = self._map_dimensional_relationships(dimensional_hierarchies)
            self._set_data("dimensional_relationships", relationships)
            
            # Generate dimensional registry
            registry = self._generate_dimensional_registry(dimensional_hierarchies, relationships)
            self._set_data("dimensional_registry", registry)
            
            # Self-validate analysis completeness
            validation = self._validate_analysis_completeness(dimensional_hierarchies)
            self._set_data("validation_result", validation)
            
            self._add_metric("dimensions_analyzed", len(self.dimensions))
            self._add_metric("hierarchies_found", len(dimensional_hierarchies))
            self._add_metric("relationships_mapped", len(relationships))
            
            return self._end_execution(success=True)
            
        except Exception as e:
            self._add_error(f"Critical error in dimensional analysis: {e}")
            return self._end_execution(success=False)
    
    def _analyze_dimensional_hierarchies(self) -> Dict[str, Any]:
        """Analyze dimensional hierarchies"""
        hierarchies = {}
        
        for dimension in self.dimensions:
            hierarchies[dimension] = {
                "name": dimension,
                "levels": self._get_dimension_levels(dimension),
                "attributes": self._get_dimension_attributes(dimension),
                "relationships": []
            }
        
        return hierarchies
    
    def _get_dimension_levels(self, dimension: str) -> List[str]:
        """Get levels for a dimension"""
        level_mappings = {
            'temporal': ['year', 'month', 'day', 'hour', 'minute'],
            'spatial': ['global', 'regional', 'local', 'component'],
            'semantic': ['domain', 'concept', 'entity', 'attribute'],
            'structural': ['system', 'module', 'component', 'class', 'method'],
            'quality': ['excellent', 'good', 'fair', 'poor', 'critical'],
            'security': ['public', 'internal', 'confidential', 'restricted'],
            'performance': ['optimal', 'good', 'acceptable', 'poor', 'critical'],
            'complexity': ['simple', 'moderate', 'complex', 'very_complex'],
            'audience': ['public', 'developer', 'admin', 'expert']
        }
        
        return level_mappings.get(dimension, ['level1', 'level2', 'level3'])
    
    def _get_dimension_attributes(self, dimension: str) -> List[str]:
        """Get attributes for a dimension"""
        attribute_mappings = {
            'temporal': ['timestamp', 'duration', 'frequency'],
            'spatial': ['location', 'scope', 'boundary'],
            'semantic': ['meaning', 'context', 'relation'],
            'structural': ['hierarchy', 'composition', 'inheritance'],
            'quality': ['metrics', 'standards', 'thresholds']
        }
        
        return attribute_mappings.get(dimension, ['attribute1', 'attribute2'])
    
    def _map_dimensional_relationships(self, hierarchies: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map relationships between dimensions"""
        relationships = []
        
        # Define common relationships
        relationship_patterns = [
            {"from": "temporal", "to": "quality", "type": "temporal_quality_correlation"},
            {"from": "structural", "to": "complexity", "type": "structure_complexity_relation"},
            {"from": "semantic", "to": "audience", "type": "semantic_audience_mapping"},
            {"from": "performance", "to": "quality", "type": "performance_quality_impact"}
        ]
        
        for pattern in relationship_patterns:
            if pattern["from"] in hierarchies and pattern["to"] in hierarchies:
                relationships.append({
                    "source_dimension": pattern["from"],
                    "target_dimension": pattern["to"],
                    "relationship_type": pattern["type"],
                    "strength": self._calculate_relationship_strength(pattern["from"], pattern["to"])
                })
        
        return relationships
    
    def _calculate_relationship_strength(self, from_dim: str, to_dim: str) -> float:
        """Calculate relationship strength between dimensions"""
        # Simplified strength calculation
        strength_mapping = {
            ("temporal", "quality"): 0.8,
            ("structural", "complexity"): 0.9,
            ("semantic", "audience"): 0.7,
            ("performance", "quality"): 0.85
        }
        
        return strength_mapping.get((from_dim, to_dim), 0.5)
    
    def _generate_dimensional_registry(self, hierarchies: Dict[str, Any], relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate dimensional registry"""
        return {
            "metadata": {
                "generated_at": self.start_time.isoformat() if self.start_time else "",
                "agent_name": self.name,
                "total_dimensions": len(self.dimensions)
            },
            "dimensions": hierarchies,
            "relationships": relationships,
            "summary": {
                "total_dimensions": len(self.dimensions),
                "total_relationships": len(relationships),
                "average_relationship_strength": sum(r.get("strength", 0) for r in relationships) / len(relationships) if relationships else 0
            }
        }
    
    def _validate_analysis_completeness(self, hierarchies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis completeness"""
        validation = {
            "is_complete": True,
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Check if all dimensions were analyzed
        analyzed_dims = len(hierarchies)
        expected_dims = len(self.dimensions)
        
        if analyzed_dims < expected_dims:
            validation["issues"].append(f"Only {analyzed_dims}/{expected_dims} dimensions analyzed")
            validation["is_complete"] = False
        
        # Check if dimensions have required attributes
        for dim_name, dim_data in hierarchies.items():
            if not dim_data.get("levels") or not dim_data.get("attributes"):
                validation["issues"].append(f"Dimension {dim_name} missing required attributes")
        
        # Calculate validation score
        score = (analyzed_dims / expected_dims) * 0.7
        score += 0.3 if validation["is_complete"] else 0.0
        
        validation["score"] = round(score, 3)
        
        return validation
