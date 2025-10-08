#!/usr/bin/env python3
"""
Short-Term Planning Memory
==========================

System for preserving planning context across sessions for First Contact scenarios.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import hashlib
import os


@dataclass
class PlanningDimension:
    """Represents a planning dimension with its analysis"""

    name: str
    risk_level: str
    unknown_factors: List[str]
    constraints: List[str]
    mitigation_strategies: List[str]
    status: str  # identified, analyzed, mitigated, resolved
    last_updated: datetime
    confidence: float


@dataclass
class PlanningContext:
    """Complete planning context for a session"""

    session_id: str
    project_name: str
    planning_dimensions: List[PlanningDimension]
    total_dimensions: int
    total_risks: int
    total_unknowns: int
    total_constraints: int
    total_mitigations: int
    planning_depth: int
    planning_exhaustion_level: float
    created_at: datetime
    last_updated: datetime
    context_hash: str


@dataclass
class PlanningInsight:
    """Key insights from planning analysis"""

    insight_type: str  # risk, constraint, unknown, mitigation, architecture
    title: str
    description: str
    importance: str  # critical, high, medium, low
    related_dimensions: List[str]
    action_required: bool
    created_at: datetime


@dataclass
class FirstContactScenario:
    """Scenario for First Contact with preserved planning context"""

    scenario_name: str
    context: PlanningContext
    key_insights: List[PlanningInsight]
    decision_framework: Dict[str, Any]
    success_criteria: List[str]
    created_at: datetime


class PlanningMemoryManager:
    """Manages short-term planning memory for First Contact scenarios"""

    def __init__(self, memory_dir: str = ".planning_memory"):
        self.memory_dir = memory_dir
        self.current_context: Optional[PlanningContext] = None
        self.insights: List[PlanningInsight] = []
        self.scenarios: List[FirstContactScenario] = []

        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)

    def start_planning_session(self, project_name: str) -> str:
        """Start a new planning session"""
        session_id = f"planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_context = PlanningContext(
            session_id=session_id,
            project_name=project_name,
            planning_dimensions=[],
            total_dimensions=0,
            total_risks=0,
            total_unknowns=0,
            total_constraints=0,
            total_mitigations=0,
            planning_depth=0,
            planning_exhaustion_level=0.0,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            context_hash="",
        )

        print(f"🧠 Started planning session: {session_id}")
        return session_id

    def add_planning_dimension(self, dimension: PlanningDimension):
        """Add a planning dimension to current context"""
        if not self.current_context:
            raise ValueError("No active planning session")

        self.current_context.planning_dimensions.append(dimension)
        self.current_context.total_dimensions += 1
        self.current_context.total_risks += 1
        self.current_context.total_unknowns += len(dimension.unknown_factors)
        self.current_context.total_constraints += len(dimension.constraints)
        self.current_context.total_mitigations += len(dimension.mitigation_strategies)
        self.current_context.last_updated = datetime.now()

        # Update context hash
        self._update_context_hash()

        print(f"📊 Added planning dimension: {dimension.name}")

    def add_planning_insight(self, insight: PlanningInsight):
        """Add a planning insight"""
        self.insights.append(insight)
        print(f"💡 Added planning insight: {insight.title}")

    def update_planning_depth(self, depth: int):
        """Update planning depth"""
        if self.current_context:
            self.current_context.planning_depth = max(
                self.current_context.planning_depth, depth
            )
            self.current_context.last_updated = datetime.now()

    def update_planning_exhaustion(self, exhaustion_level: float):
        """Update planning exhaustion level (0.0 = just started, 1.0 = fully exhausted)"""
        if self.current_context:
            self.current_context.planning_exhaustion_level = exhaustion_level
            self.current_context.last_updated = datetime.now()

    def create_first_contact_scenario(self, scenario_name: str) -> FirstContactScenario:
        """Create a First Contact scenario with current planning context"""
        if not self.current_context:
            raise ValueError("No active planning session")

        # Get key insights
        key_insights = [
            insight
            for insight in self.insights
            if insight.importance in ["critical", "high"]
        ]

        # Create decision framework
        decision_framework = self._create_decision_framework()

        # Define success criteria
        success_criteria = [
            "All critical risks identified and mitigated",
            "All critical unknowns acknowledged and categorized",
            "All critical constraints identified and analyzed",
            "Planning depth adequate for project complexity",
            "First Contact scenarios prepared",
            "Decision frameworks established",
        ]

        scenario = FirstContactScenario(
            scenario_name=scenario_name,
            context=self.current_context,
            key_insights=key_insights,
            decision_framework=decision_framework,
            success_criteria=success_criteria,
            created_at=datetime.now(),
        )

        self.scenarios.append(scenario)
        print(f"🎯 Created First Contact scenario: {scenario_name}")

        return scenario

    def save_planning_memory(self, filename: Optional[str] = None) -> str:
        """Save planning memory to file"""
        if not self.current_context:
            raise ValueError("No active planning session")

        if not filename:
            filename = f"planning_memory_{self.current_context.session_id}.json"

        filepath = os.path.join(self.memory_dir, filename)

        # Prepare data for serialization
        memory_data = {
            "current_context": asdict(self.current_context),
            "insights": [asdict(insight) for insight in self.insights],
            "scenarios": [asdict(scenario) for scenario in self.scenarios],
            "saved_at": datetime.now().isoformat(),
        }

        # Convert datetime objects to strings
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        # Recursively convert datetime objects
        def convert_recursive(data):
            if isinstance(data, dict):
                return {k: convert_recursive(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_recursive(item) for item in data]
            else:
                return convert_datetime(data)

        memory_data = convert_recursive(memory_data)

        # Save to file
        with open(filepath, "w") as f:
            json.dump(memory_data, f, indent=2)

        print(f"💾 Saved planning memory to: {filepath}")
        return filepath

    def load_planning_memory(self, filepath: str):
        """Load planning memory from file"""
        with open(filepath, "r") as f:
            memory_data = json.load(f)

        # Restore current context
        context_data = memory_data["current_context"]
        self.current_context = PlanningContext(
            session_id=context_data["session_id"],
            project_name=context_data["project_name"],
            planning_dimensions=[
                PlanningDimension(**dim) for dim in context_data["planning_dimensions"]
            ],
            total_dimensions=context_data["total_dimensions"],
            total_risks=context_data["total_risks"],
            total_unknowns=context_data["total_unknowns"],
            total_constraints=context_data["total_constraints"],
            total_mitigations=context_data["total_mitigations"],
            planning_depth=context_data["planning_depth"],
            planning_exhaustion_level=context_data["planning_exhaustion_level"],
            created_at=datetime.fromisoformat(context_data["created_at"]),
            last_updated=datetime.fromisoformat(context_data["last_updated"]),
            context_hash=context_data["context_hash"],
        )

        # Restore insights
        self.insights = [
            PlanningInsight(**insight) for insight in memory_data["insights"]
        ]

        # Restore scenarios
        self.scenarios = [
            FirstContactScenario(**scenario) for scenario in memory_data["scenarios"]
        ]

        print(f"📂 Loaded planning memory from: {filepath}")

    def get_planning_summary(self) -> Dict[str, Any]:
        """Get summary of current planning state"""
        if not self.current_context:
            return {"error": "No active planning session"}

        return {
            "session_id": self.current_context.session_id,
            "project_name": self.current_context.project_name,
            "total_dimensions": self.current_context.total_dimensions,
            "total_risks": self.current_context.total_risks,
            "total_unknowns": self.current_context.total_unknowns,
            "total_constraints": self.current_context.total_constraints,
            "total_mitigations": self.current_context.total_mitigations,
            "planning_depth": self.current_context.planning_depth,
            "planning_exhaustion_level": self.current_context.planning_exhaustion_level,
            "insights_count": len(self.insights),
            "scenarios_count": len(self.scenarios),
            "last_updated": self.current_context.last_updated.isoformat(),
        }

    def _update_context_hash(self):
        """Update context hash for integrity checking"""
        if self.current_context:
            context_str = json.dumps(
                asdict(self.current_context), sort_keys=True, default=str
            )
            self.current_context.context_hash = hashlib.md5(
                context_str.encode()
            ).hexdigest()

    def _create_decision_framework(self) -> Dict[str, Any]:
        """Create decision framework based on planning analysis"""
        return {
            "risk_assessment": {
                "critical_risks": [
                    dim.name
                    for dim in self.current_context.planning_dimensions
                    if dim.risk_level == "critical"
                ],
                "high_risks": [
                    dim.name
                    for dim in self.current_context.planning_dimensions
                    if dim.risk_level == "high"
                ],
                "mitigation_status": "ongoing",
            },
            "constraint_analysis": {
                "critical_constraints": [
                    dim.name
                    for dim in self.current_context.planning_dimensions
                    if "critical" in dim.constraints
                ],
                "constraint_count": self.current_context.total_constraints,
            },
            "unknown_factors": {
                "critical_unknowns": [
                    dim.name
                    for dim in self.current_context.planning_dimensions
                    if "critical" in dim.unknown_factors
                ],
                "unknown_count": self.current_context.total_unknowns,
            },
            "planning_completeness": {
                "exhaustion_level": self.current_context.planning_exhaustion_level,
                "depth": self.current_context.planning_depth,
                "dimensions_analyzed": self.current_context.total_dimensions,
            },
        }


def create_planning_dimension(
    name: str,
    risk_level: str,
    unknown_factors: List[str],
    constraints: List[str],
    mitigation_strategies: List[str],
) -> PlanningDimension:
    """Helper function to create planning dimensions"""
    return PlanningDimension(
        name=name,
        risk_level=risk_level,
        unknown_factors=unknown_factors,
        constraints=constraints,
        mitigation_strategies=mitigation_strategies,
        status="identified",
        last_updated=datetime.now(),
        confidence=0.8,
    )


def create_planning_insight(
    insight_type: str,
    title: str,
    description: str,
    importance: str,
    related_dimensions: List[str],
) -> PlanningInsight:
    """Helper function to create planning insights"""
    return PlanningInsight(
        insight_type=insight_type,
        title=title,
        description=description,
        importance=importance,
        related_dimensions=related_dimensions,
        action_required=True,
        created_at=datetime.now(),
    )
