#!/usr/bin/env python3
"""
Dynamic Session Classifier
=========================

Advanced session classification and hypothesis testing based on multi-dimensional analysis.
"Sniff the air, look where I'm at, do a multi-dimensional analysis and say, based on the vector, I think I'm here."
"""

import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import os
from planning_graph_serializer import PlanningGraphLoader


@dataclass
class SessionVector:
    """Multi-dimensional session vector for classification"""
    session_id: str
    timestamp: datetime
    dimensions: Dict[str, float]  # dimension_name -> confidence/strength
    context_signals: Dict[str, Any]  # raw context data
    classification_hypothesis: Optional[str] = None
    confidence_score: Optional[float] = None
    vector_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class SessionClass:
    """Represents a class of similar sessions"""
    class_id: str
    class_name: str
    description: str
    dimensional_signature: Dict[str, float]  # typical dimension values
    context_patterns: List[Dict[str, Any]]  # typical context patterns
    success_patterns: List[Dict[str, Any]]  # patterns that led to success
    failure_patterns: List[Dict[str, Any]]  # patterns that led to failure
    recovery_patterns: List[Dict[str, Any]]  # patterns for recovery
    instance_count: int = 0
    success_rate: float = 0.0
    created_at: datetime = None
    last_updated: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        return data


@dataclass
class SessionInstance:
    """Represents a specific session instance"""
    instance_id: str
    session_class: str
    session_vector: SessionVector
    execution_log: List[Dict[str, Any]]  # step-by-step execution
    outcome: str  # success, failure, partial_success, abandoned
    failure_points: List[Dict[str, Any]]  # where things went wrong
    recovery_attempts: List[Dict[str, Any]]  # recovery actions taken
    final_state: Dict[str, Any]  # final session state
    lessons_learned: List[str]  # key insights
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


class MultiDimensionalSessionAnalyzer:
    """Analyzes sessions across multiple dimensions"""
    
    def __init__(self):
        self.dimension_weights = {
            "technical_complexity": 0.2,
            "risk_level": 0.25,
            "uncertainty_level": 0.15,
            "resource_constraints": 0.1,
            "time_pressure": 0.1,
            "user_expertise": 0.1,
            "system_stability": 0.1
        }
    
    def analyze_session_context(self, context: Dict[str, Any]) -> SessionVector:
        """Analyze session context and create multi-dimensional vector"""
        dimensions = {}
        
        # Technical complexity analysis
        dimensions["technical_complexity"] = self._analyze_technical_complexity(context)
        
        # Risk level analysis
        dimensions["risk_level"] = self._analyze_risk_level(context)
        
        # Uncertainty level analysis
        dimensions["uncertainty_level"] = self._analyze_uncertainty_level(context)
        
        # Resource constraints analysis
        dimensions["resource_constraints"] = self._analyze_resource_constraints(context)
        
        # Time pressure analysis
        dimensions["time_pressure"] = self._analyze_time_pressure(context)
        
        # User expertise analysis
        dimensions["user_expertise"] = self._analyze_user_expertise(context)
        
        # System stability analysis
        dimensions["system_stability"] = self._analyze_system_stability(context)
        
        # Create session vector
        session_vector = SessionVector(
            session_id=context.get("session_id", f"session_{datetime.now().isoformat()}"),
            timestamp=datetime.now(),
            dimensions=dimensions,
            context_signals=context
        )
        
        # Generate vector hash for uniqueness
        vector_str = json.dumps(dimensions, sort_keys=True)
        session_vector.vector_hash = hashlib.md5(vector_str.encode()).hexdigest()[:16]
        
        return session_vector
    
    def _analyze_technical_complexity(self, context: Dict[str, Any]) -> float:
        """Analyze technical complexity dimension"""
        complexity_indicators = 0
        total_indicators = 0
        
        # Check for complex technologies
        tech_stack = context.get("tech_stack", [])
        if "langgraph" in str(tech_stack).lower():
            complexity_indicators += 2
            total_indicators += 2
        if "playwright" in str(tech_stack).lower():
            complexity_indicators += 1
            total_indicators += 1
        if "browser_automation" in str(context).lower():
            complexity_indicators += 2
            total_indicators += 2
        
        # Check for integration complexity
        if context.get("integration_points", 0) > 3:
            complexity_indicators += 1
            total_indicators += 1
        
        # Check for debugging complexity
        if context.get("debugging_required", False):
            complexity_indicators += 1
            total_indicators += 1
        
        return complexity_indicators / max(total_indicators, 1)
    
    def _analyze_risk_level(self, context: Dict[str, Any]) -> float:
        """Analyze risk level dimension"""
        risk_score = 0.0
        
        # Check for critical components
        if context.get("critical_components", 0) > 0:
            risk_score += 0.3
        
        # Check for data loss risk
        if context.get("data_loss_risk", False):
            risk_score += 0.2
        
        # Check for system downtime risk
        if context.get("downtime_risk", False):
            risk_score += 0.2
        
        # Check for user impact
        if context.get("user_impact", "low") in ["high", "critical"]:
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def _analyze_uncertainty_level(self, context: Dict[str, Any]) -> float:
        """Analyze uncertainty level dimension"""
        uncertainty_score = 0.0
        
        # Check for unknown factors
        unknown_factors = context.get("unknown_factors", [])
        uncertainty_score += min(len(unknown_factors) * 0.2, 0.6)
        
        # Check for ambiguous requirements
        if context.get("ambiguous_requirements", False):
            uncertainty_score += 0.2
        
        # Check for changing requirements
        if context.get("changing_requirements", False):
            uncertainty_score += 0.2
        
        return min(uncertainty_score, 1.0)
    
    def _analyze_resource_constraints(self, context: Dict[str, Any]) -> float:
        """Analyze resource constraints dimension"""
        constraint_score = 0.0
        
        # Check for memory constraints
        if context.get("memory_limited", False):
            constraint_score += 0.3
        
        # Check for CPU constraints
        if context.get("cpu_limited", False):
            constraint_score += 0.2
        
        # Check for time constraints
        if context.get("time_limited", False):
            constraint_score += 0.3
        
        # Check for dependency constraints
        if context.get("dependency_constraints", False):
            constraint_score += 0.2
        
        return min(constraint_score, 1.0)
    
    def _analyze_time_pressure(self, context: Dict[str, Any]) -> float:
        """Analyze time pressure dimension"""
        time_pressure = 0.0
        
        # Check for deadlines
        if context.get("deadline_pressure", False):
            time_pressure += 0.4
        
        # Check for urgency
        if context.get("urgent", False):
            time_pressure += 0.3
        
        # Check for blocking dependencies
        if context.get("blocking_others", False):
            time_pressure += 0.3
        
        return min(time_pressure, 1.0)
    
    def _analyze_user_expertise(self, context: Dict[str, Any]) -> float:
        """Analyze user expertise dimension"""
        expertise_score = 0.0
        
        # Check for domain expertise
        if context.get("domain_expertise", "low") in ["medium", "high"]:
            expertise_score += 0.4
        
        # Check for technical expertise
        if context.get("technical_expertise", "low") in ["medium", "high"]:
            expertise_score += 0.3
        
        # Check for system knowledge
        if context.get("system_knowledge", "low") in ["medium", "high"]:
            expertise_score += 0.3
        
        return min(expertise_score, 1.0)
    
    def _analyze_system_stability(self, context: Dict[str, Any]) -> float:
        """Analyze system stability dimension"""
        stability_score = 1.0  # Start with perfect stability
        
        # Check for known issues
        if context.get("known_issues", 0) > 0:
            stability_score -= 0.2
        
        # Check for recent changes
        if context.get("recent_changes", False):
            stability_score -= 0.2
        
        # Check for error rates
        error_rate = context.get("error_rate", 0.0)
        stability_score -= error_rate * 0.6
        
        return max(stability_score, 0.0)


class SessionClassifier:
    """Classifies sessions and tests hypotheses"""
    
    def __init__(self, planning_graph_loader: PlanningGraphLoader):
        self.planning_graph = planning_graph_loader
        self.analyzer = MultiDimensionalSessionAnalyzer()
        self.session_classes: Dict[str, SessionClass] = {}
        self.session_instances: List[SessionInstance] = []
        self.classification_history: List[Dict[str, Any]] = []
    
    def sniff_the_air(self, context: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        """Main classification method - 'sniff the air, look where I'm at'"""
        print("🌬️ SNIFFING THE AIR - Multi-dimensional session analysis...")
        
        # Create session vector
        session_vector = self.analyzer.analyze_session_context(context)
        print(f"📊 Session Vector Created: {session_vector.vector_hash}")
        print(f"   Dimensions: {session_vector.dimensions}")
        
        # Classify session
        classification_result = self.classify_session(session_vector)
        hypothesis = classification_result["hypothesis"]
        confidence = classification_result["confidence"]
        analysis_details = classification_result["analysis_details"]
        
        print(f"🎯 HYPOTHESIS: {hypothesis}")
        print(f"📈 CONFIDENCE: {confidence:.2f}")
        
        # Test the hypothesis
        test_result = self.test_hypothesis(session_vector, hypothesis)
        print(f"🧪 HYPOTHESIS TEST: {test_result['test_passed']}")
        print(f"   Reasoning: {test_result['reasoning']}")
        
        return hypothesis, confidence, {
            "session_vector": session_vector.to_dict(),
            "classification_result": classification_result,
            "test_result": test_result,
            "analysis_details": analysis_details
        }
    
    def classify_session(self, session_vector: SessionVector) -> Dict[str, Any]:
        """Classify session based on multi-dimensional analysis"""
        if not self.session_classes:
            # No existing classes - create first classification
            return self._create_initial_classification(session_vector)
        
        # Find best matching class
        best_match = None
        best_similarity = 0.0
        
        for class_id, session_class in self.session_classes.items():
            similarity = self._calculate_class_similarity(session_vector, session_class)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = session_class
        
        if best_similarity > 0.7:  # High confidence threshold
            hypothesis = f"Session class: {best_match.class_name}"
            confidence = best_similarity
        elif best_similarity > 0.4:  # Medium confidence threshold
            hypothesis = f"Possible session class: {best_match.class_name} (similarity: {best_similarity:.2f})"
            confidence = best_similarity
        else:
            # Low similarity - might be new class
            hypothesis = "New session type - insufficient similarity to existing classes"
            confidence = 1.0 - best_similarity
        
        return {
            "hypothesis": hypothesis,
            "confidence": confidence,
            "best_match": best_match.class_name if best_match else "None",
            "similarity_score": best_similarity,
            "analysis_details": {
                "session_vector": session_vector.dimensions,
                "best_match_signature": best_match.dimensional_signature if best_match else {},
                "similarity_breakdown": self._get_similarity_breakdown(session_vector, best_match) if best_match else {}
            }
        }
    
    def _create_initial_classification(self, session_vector: SessionVector) -> Dict[str, Any]:
        """Create initial classification when no classes exist"""
        # Analyze the vector to suggest a class
        dominant_dimensions = self._get_dominant_dimensions(session_vector)
        class_suggestion = self._suggest_class_from_dimensions(dominant_dimensions)
        
        return {
            "hypothesis": f"Initial classification: {class_suggestion}",
            "confidence": 0.5,  # Medium confidence for initial classification
            "best_match": "None",
            "similarity_score": 0.0,
            "analysis_details": {
                "session_vector": session_vector.dimensions,
                "dominant_dimensions": dominant_dimensions,
                "class_suggestion": class_suggestion,
                "reasoning": "No existing classes - creating initial classification"
            }
        }
    
    def _calculate_class_similarity(self, session_vector: SessionVector, session_class: SessionClass) -> float:
        """Calculate similarity between session vector and session class"""
        similarities = []
        
        for dimension, session_value in session_vector.dimensions.items():
            if dimension in session_class.dimensional_signature:
                class_value = session_class.dimensional_signature[dimension]
                # Calculate similarity (1 - absolute difference)
                similarity = 1.0 - abs(session_value - class_value)
                similarities.append(similarity)
        
        # Weighted average similarity
        if similarities:
            weights = [self.analyzer.dimension_weights.get(dim, 1.0) for dim in session_vector.dimensions.keys()]
            weighted_similarity = sum(s * w for s, w in zip(similarities, weights)) / sum(weights)
            return weighted_similarity
        
        return 0.0
    
    def _get_dominant_dimensions(self, session_vector: SessionVector) -> List[Tuple[str, float]]:
        """Get dimensions with highest values"""
        sorted_dimensions = sorted(
            session_vector.dimensions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_dimensions[:3]  # Top 3 dimensions
    
    def _suggest_class_from_dimensions(self, dominant_dimensions: List[Tuple[str, float]]) -> str:
        """Suggest session class based on dominant dimensions"""
        if not dominant_dimensions:
            return "Unknown Session Type"
        
        top_dimension, top_value = dominant_dimensions[0]
        
        # Class suggestion logic based on dominant dimensions
        if top_dimension == "technical_complexity" and top_value > 0.7:
            return "Complex Technical Integration Session"
        elif top_dimension == "risk_level" and top_value > 0.7:
            return "High-Risk Critical System Session"
        elif top_dimension == "uncertainty_level" and top_value > 0.7:
            return "Exploratory Discovery Session"
        elif top_dimension == "time_pressure" and top_value > 0.7:
            return "Urgent Time-Critical Session"
        elif top_dimension == "resource_constraints" and top_value > 0.7:
            return "Resource-Constrained Session"
        else:
            return "Standard Development Session"
    
    def test_hypothesis(self, session_vector: SessionVector, hypothesis: str) -> Dict[str, Any]:
        """Test the classification hypothesis"""
        print(f"🧪 TESTING HYPOTHESIS: {hypothesis}")
        
        # Test 1: Dimensional consistency check
        dimensional_test = self._test_dimensional_consistency(session_vector)
        
        # Test 2: Context pattern matching
        pattern_test = self._test_context_patterns(session_vector)
        
        # Test 3: Historical success prediction
        prediction_test = self._test_success_prediction(session_vector)
        
        # Overall test result
        tests_passed = sum([dimensional_test["passed"], pattern_test["passed"], prediction_test["passed"]])
        overall_passed = tests_passed >= 2  # At least 2 out of 3 tests must pass
        
        reasoning = f"Tests passed: {tests_passed}/3. "
        if dimensional_test["passed"]:
            reasoning += "Dimensional consistency ✓. "
        if pattern_test["passed"]:
            reasoning += "Context patterns ✓. "
        if prediction_test["passed"]:
            reasoning += "Success prediction ✓. "
        
        return {
            "test_passed": overall_passed,
            "tests_passed": tests_passed,
            "total_tests": 3,
            "reasoning": reasoning,
            "test_details": {
                "dimensional_test": dimensional_test,
                "pattern_test": pattern_test,
                "prediction_test": prediction_test
            }
        }
    
    def _test_dimensional_consistency(self, session_vector: SessionVector) -> Dict[str, Any]:
        """Test if dimensions are internally consistent"""
        dimensions = session_vector.dimensions
        
        # Check for logical consistency
        inconsistencies = []
        
        # High technical complexity should correlate with higher risk
        if dimensions.get("technical_complexity", 0) > 0.7 and dimensions.get("risk_level", 0) < 0.3:
            inconsistencies.append("High technical complexity with low risk seems inconsistent")
        
        # High uncertainty should correlate with higher risk
        if dimensions.get("uncertainty_level", 0) > 0.7 and dimensions.get("risk_level", 0) < 0.3:
            inconsistencies.append("High uncertainty with low risk seems inconsistent")
        
        # High time pressure with low user expertise is risky
        if dimensions.get("time_pressure", 0) > 0.7 and dimensions.get("user_expertise", 0) < 0.3:
            inconsistencies.append("High time pressure with low user expertise is risky")
        
        passed = len(inconsistencies) == 0
        
        return {
            "passed": passed,
            "inconsistencies": inconsistencies,
            "reasoning": "Dimensional consistency check"
        }
    
    def _test_context_patterns(self, session_vector: SessionVector) -> Dict[str, Any]:
        """Test if context patterns match expected patterns for the classification"""
        context = session_vector.context_signals
        
        # Look for expected patterns based on dimensions
        patterns_found = []
        patterns_missing = []
        
        # Technical complexity patterns
        if session_vector.dimensions.get("technical_complexity", 0) > 0.5:
            if "langgraph" in str(context).lower() or "playwright" in str(context).lower():
                patterns_found.append("Complex technology stack detected")
            else:
                patterns_missing.append("Expected complex technology indicators")
        
        # Risk level patterns
        if session_vector.dimensions.get("risk_level", 0) > 0.5:
            if context.get("critical_components", 0) > 0 or context.get("data_loss_risk", False):
                patterns_found.append("High-risk indicators present")
            else:
                patterns_missing.append("Expected high-risk indicators")
        
        # Uncertainty patterns
        if session_vector.dimensions.get("uncertainty_level", 0) > 0.5:
            if len(context.get("unknown_factors", [])) > 0:
                patterns_found.append("Uncertainty indicators present")
            else:
                patterns_missing.append("Expected uncertainty indicators")
        
        passed = len(patterns_found) > 0 and len(patterns_missing) == 0
        
        return {
            "passed": passed,
            "patterns_found": patterns_found,
            "patterns_missing": patterns_missing,
            "reasoning": "Context pattern matching"
        }
    
    def _test_success_prediction(self, session_vector: SessionVector) -> Dict[str, Any]:
        """Test if we can predict success based on historical data"""
        # For now, use dimensional analysis to predict success
        dimensions = session_vector.dimensions
        
        # Success factors (positive indicators)
        success_score = 0.0
        
        # High user expertise increases success probability
        if dimensions.get("user_expertise", 0) > 0.7:
            success_score += 0.3
        
        # High system stability increases success probability
        if dimensions.get("system_stability", 0) > 0.8:
            success_score += 0.3
        
        # Low uncertainty increases success probability
        if dimensions.get("uncertainty_level", 0) < 0.3:
            success_score += 0.2
        
        # Risk factors (negative indicators)
        risk_score = 0.0
        
        # High risk level decreases success probability
        if dimensions.get("risk_level", 0) > 0.7:
            risk_score += 0.3
        
        # High time pressure decreases success probability
        if dimensions.get("time_pressure", 0) > 0.7:
            risk_score += 0.2
        
        # High resource constraints decrease success probability
        if dimensions.get("resource_constraints", 0) > 0.7:
            risk_score += 0.2
        
        # Calculate overall success prediction
        prediction_score = success_score - risk_score
        predicted_success = prediction_score > 0.2
        
        return {
            "passed": predicted_success,
            "success_score": success_score,
            "risk_score": risk_score,
            "prediction_score": prediction_score,
            "reasoning": f"Success prediction based on dimensional analysis (score: {prediction_score:.2f})"
        }
    
    def _get_similarity_breakdown(self, session_vector: SessionVector, session_class: SessionClass) -> Dict[str, float]:
        """Get detailed similarity breakdown"""
        breakdown = {}
        
        for dimension, session_value in session_vector.dimensions.items():
            if dimension in session_class.dimensional_signature:
                class_value = session_class.dimensional_signature[dimension]
                similarity = 1.0 - abs(session_value - class_value)
                breakdown[dimension] = {
                    "session_value": session_value,
                    "class_value": class_value,
                    "similarity": similarity
                }
        
        return breakdown
    
    def create_session_class(self, class_name: str, description: str, 
                           session_vectors: List[SessionVector]) -> SessionClass:
        """Create a new session class from multiple session vectors"""
        # Calculate average dimensional signature
        all_dimensions = set()
        for vector in session_vectors:
            all_dimensions.update(vector.dimensions.keys())
        
        dimensional_signature = {}
        for dimension in all_dimensions:
            values = [v.dimensions.get(dimension, 0.0) for v in session_vectors]
            dimensional_signature[dimension] = sum(values) / len(values)
        
        # Create session class
        session_class = SessionClass(
            class_id=f"class_{class_name.lower().replace(' ', '_')}",
            class_name=class_name,
            description=description,
            dimensional_signature=dimensional_signature,
            context_patterns=[],
            success_patterns=[],
            failure_patterns=[],
            recovery_patterns=[],
            instance_count=len(session_vectors),
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.session_classes[session_class.class_id] = session_class
        return session_class
    
    def record_session_instance(self, session_vector: SessionVector, 
                              session_class: str, outcome: str,
                              execution_log: List[Dict[str, Any]] = None) -> SessionInstance:
        """Record a session instance for learning"""
        instance = SessionInstance(
            instance_id=f"instance_{datetime.now().isoformat()}",
            session_class=session_class,
            session_vector=session_vector,
            execution_log=execution_log or [],
            outcome=outcome,
            failure_points=[],
            recovery_attempts=[],
            final_state={},
            lessons_learned=[],
            created_at=datetime.now()
        )
        
        self.session_instances.append(instance)
        
        # Update session class statistics
        if session_class in self.session_classes:
            self.session_classes[session_class].instance_count += 1
            self.session_classes[session_class].last_updated = datetime.now()
        
        return instance
    
    def export_classification_data(self, output_file: str):
        """Export classification data for persistence"""
        data = {
            "session_classes": {cid: sc.to_dict() for cid, sc in self.session_classes.items()},
            "session_instances": [si.to_dict() for si in self.session_instances],
            "classification_history": self.classification_history,
            "exported_at": datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Classification data exported to {output_file}")


def main():
    """Main function to demonstrate dynamic session classification"""
    print("🌬️ DYNAMIC SESSION CLASSIFIER")
    print("=" * 60)
    
    # Load planning graph
    try:
        planning_loader = PlanningGraphLoader("planning_graph.json")
        print("✅ Planning graph loaded")
    except FileNotFoundError:
        print("❌ Planning graph not found - creating mock loader")
        planning_loader = None
    
    # Initialize classifier
    classifier = SessionClassifier(planning_loader)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Complex DevPost Integration Session",
            "context": {
                "session_id": "devpost_integration_001",
                "tech_stack": ["langgraph", "playwright", "browser_automation"],
                "integration_points": 5,
                "debugging_required": True,
                "critical_components": 2,
                "data_loss_risk": True,
                "user_impact": "high",
                "unknown_factors": ["form_validation", "session_management"],
                "ambiguous_requirements": True,
                "memory_limited": False,
                "cpu_limited": False,
                "deadline_pressure": True,
                "urgent": True,
                "domain_expertise": "medium",
                "technical_expertise": "high",
                "known_issues": 1,
                "error_rate": 0.1
            }
        },
        {
            "name": "Simple Bug Fix Session",
            "context": {
                "session_id": "bug_fix_001",
                "tech_stack": ["python", "logging"],
                "integration_points": 1,
                "debugging_required": False,
                "critical_components": 0,
                "data_loss_risk": False,
                "user_impact": "low",
                "unknown_factors": [],
                "ambiguous_requirements": False,
                "memory_limited": False,
                "cpu_limited": False,
                "deadline_pressure": False,
                "urgent": False,
                "domain_expertise": "high",
                "technical_expertise": "high",
                "known_issues": 0,
                "error_rate": 0.0
            }
        },
        {
            "name": "Exploratory Discovery Session",
            "context": {
                "session_id": "exploration_001",
                "tech_stack": ["unknown"],
                "integration_points": 0,
                "debugging_required": True,
                "critical_components": 0,
                "data_loss_risk": False,
                "user_impact": "low",
                "unknown_factors": ["system_behavior", "api_endpoints", "data_flow"],
                "ambiguous_requirements": True,
                "memory_limited": False,
                "cpu_limited": False,
                "deadline_pressure": False,
                "urgent": False,
                "domain_expertise": "low",
                "technical_expertise": "medium",
                "known_issues": 0,
                "error_rate": 0.3
            }
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎭 TESTING SCENARIO {i}: {scenario['name']}")
        print("-" * 50)
        
        hypothesis, confidence, analysis = classifier.sniff_the_air(scenario['context'])
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   Hypothesis: {hypothesis}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Test Passed: {analysis['test_result']['test_passed']}")
        print(f"   Reasoning: {analysis['test_result']['reasoning']}")
        
        # Record the session instance
        session_vector = SessionVector(**analysis['session_vector'])
        instance = classifier.record_session_instance(
            session_vector, 
            analysis['classification_result']['best_match'],
            "success" if analysis['test_result']['test_passed'] else "needs_review"
        )
        print(f"   Instance Recorded: {instance.instance_id}")
    
    # Create session classes based on the instances
    print(f"\n🏗️ CREATING SESSION CLASSES...")
    
    # Group instances by similarity and create classes
    if classifier.session_instances:
        # For demo, create classes based on the test scenarios
        complex_class = classifier.create_session_class(
            "Complex Technical Integration",
            "Sessions involving complex technical integrations with multiple components",
            [classifier.session_instances[0].session_vector]
        )
        
        simple_class = classifier.create_session_class(
            "Simple Development Tasks",
            "Simple development tasks with low complexity and risk",
            [classifier.session_instances[1].session_vector]
        )
        
        exploratory_class = classifier.create_session_class(
            "Exploratory Discovery",
            "Sessions focused on exploration and discovery of unknown systems",
            [classifier.session_instances[2].session_vector]
        )
        
        print(f"✅ Created {len(classifier.session_classes)} session classes")
    
    # Export classification data
    classifier.export_classification_data("session_classification_data.json")
    
    print(f"\n🎉 Dynamic session classification demo complete!")
    print(f"   Session Classes: {len(classifier.session_classes)}")
    print(f"   Session Instances: {len(classifier.session_instances)}")
    print(f"   Classification Data: session_classification_data.json")


if __name__ == "__main__":
    main()

