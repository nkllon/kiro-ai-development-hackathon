#!/usr/bin/env python3
"""
HackathonDemoController - Main Controller for Demo Orchestration

This controller coordinates between models and views, implementing
proper MVC separation with update and create functions following Beast Mode principles.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..models import (
    SpecToCodeModel,
    SystematicSuperiorityModel,
    MultiAgentCollaborationModel,
    ProductionInfrastructureModel,
    Task,
    HumanInput,
    GKEConfig,
)
from ..views import HackathonDemoView, DemoPhase, DemoContent


@dataclass
class DemoSession:
    """Represents a demo session for a judge"""

    session_id: str
    judge_id: str
    start_time: datetime
    current_phase: DemoPhase
    progress: float
    interactions: List[Dict[str, Any]]
    systematic_score: float
    learning_patterns: List[Dict[str, Any]]


@dataclass
class TransformationResult:
    """Result of spec-to-code transformation"""

    transformation_id: str
    spec: str
    generated_code: str
    systematic_score: float
    quality_metrics: Dict[str, Any]
    learning_patterns: List[Dict[str, Any]]
    created_at: datetime


@dataclass
class CollaborationResult:
    """Result of multi-agent collaboration"""

    collaboration_id: str
    task_description: str
    participating_agents: List[str]
    coordination_events: List[Dict[str, Any]]
    conflicts_resolved: List[Dict[str, Any]]
    human_amplification: Dict[str, Any]
    final_output: Dict[str, Any]
    created_at: datetime


class HackathonDemoController:
    """
    Main controller for hackathon demo orchestration.

    Coordinates between models and views, implementing proper MVC separation
    with update and create functions following Beast Mode principles.
    """

    def __init__(self):
        # Initialize models
        self.spec_model = SpecToCodeModel()
        self.superiority_model = SystematicSuperiorityModel()
        self.agent_model = MultiAgentCollaborationModel()
        self.infra_model = ProductionInfrastructureModel()

        # Initialize view
        self.demo_view = HackathonDemoView()

        # Controller state
        self.active_sessions: Dict[str, DemoSession] = {}
        self.transformation_history: List[TransformationResult] = []
        self.collaboration_history: List[CollaborationResult] = []

        # Beast Mode tracking
        self.systematic_scores: List[float] = []
        self.learning_patterns: List[Dict[str, Any]] = []

    # CREATE FUNCTIONS

    def create_demo_session(self, judge_id: str) -> DemoSession:
        """Create a new demo session for a judge"""
        session_id = f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        session = DemoSession(
            session_id=session_id,
            judge_id=judge_id,
            start_time=datetime.now(),
            current_phase=DemoPhase.HOOK,
            progress=0.0,
            interactions=[],
            systematic_score=0.908,  # Default high score
            learning_patterns=[],
        )

        # Store active session
        self.active_sessions[session_id] = session

        # Log session creation
        self._log_interaction(
            session_id,
            "session_created",
            {
                "judge_id": judge_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

        return session

    def create_spec_transformation(
        self, session_id: str, spec: str
    ) -> TransformationResult:
        """Create a new spec-to-code transformation"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        # Use spec model to transform
        model_result = self.spec_model.transform_spec_to_code(spec)

        # Create transformation result
        transformation = TransformationResult(
            transformation_id=f"TRANS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            spec=spec,
            generated_code=model_result.generated_code,
            systematic_score=model_result.systematic_score,
            quality_metrics={
                "quality_level": model_result.quality_level.value,
                "test_coverage": model_result.test_coverage,
                "security_validation": model_result.security_validation,
                "performance_metrics": model_result.performance_metrics,
            },
            learning_patterns=[
                {
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "confidence_score": pattern.confidence_score,
                    "improvement_factor": pattern.improvement_factor,
                }
                for pattern in model_result.learning_patterns
            ],
            created_at=datetime.now(),
        )

        # Store in history
        self.transformation_history.append(transformation)

        # Update session
        self._update_session_progress(
            session_id, 0.1
        )  # 10% progress for transformation

        # Log transformation
        self._log_interaction(
            session_id,
            "transformation_created",
            {
                "transformation_id": transformation.transformation_id,
                "spec": spec,
                "systematic_score": model_result.systematic_score,
            },
        )

        return transformation

    def create_agent_collaboration(
        self, session_id: str, task_description: str, human_input: Optional[str] = None
    ) -> CollaborationResult:
        """Create a new multi-agent collaboration"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        # Create task
        task = Task(
            task_id=f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            description=task_description,
            complexity=0.8,  # High complexity for demo
            required_agents=[agent.agent_type for agent in self.agent_model.agents],
            human_input=human_input,
            created_at=datetime.now(),
        )

        # Use agent model to coordinate
        model_result = self.agent_model.coordinate_agents(task)

        # Create collaboration result
        collaboration = CollaborationResult(
            collaboration_id=model_result.collaboration_id,
            task_description=task_description,
            participating_agents=[
                agent.agent_id for agent in model_result.participating_agents
            ],
            coordination_events=model_result.coordination_events,
            conflicts_resolved=model_result.conflicts_resolved,
            human_amplification=model_result.human_amplification,
            final_output=model_result.final_output,
            created_at=datetime.now(),
        )

        # Store in history
        self.collaboration_history.append(collaboration)

        # Update session
        self._update_session_progress(
            session_id, 0.15
        )  # 15% progress for collaboration

        # Log collaboration
        self._log_interaction(
            session_id,
            "collaboration_created",
            {
                "collaboration_id": collaboration.collaboration_id,
                "task_description": task_description,
                "participating_agents": collaboration.participating_agents,
            },
        )

        return collaboration

    def create_infrastructure_deployment(self, session_id: str) -> Dict[str, Any]:
        """Create a new infrastructure deployment"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        # Create GKE config
        config = GKEConfig(
            cluster_name=f"demo-cluster-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            node_count=3,
            machine_type="e2-medium",
            region="us-central1",
            auto_scaling=True,
            security_policies=["network-policy", "pod-security-policy"],
            monitoring_enabled=True,
            cost_optimization=model_result.cost_optimization,
        )

        # Use infra model to deploy
        model_result = self.infra_model.deploy_gke_cluster(config)

        # Update session
        self._update_session_progress(session_id, 0.2)  # 20% progress for deployment

        # Log deployment
        self._log_interaction(
            session_id,
            "deployment_created",
            {
                "deployment_id": model_result.deployment_id,
                "cluster_name": config.cluster_name,
                "status": model_result.status.value,
            },
        )

        return {
            "deployment_id": model_result.deployment_id,
            "status": model_result.status.value,
            "health_metrics": model_result.health_metrics,
            "cost_metrics": model_result.cost_metrics,
            "security_metrics": model_result.security_metrics,
            "performance_metrics": model_result.performance_metrics,
        }

    # UPDATE FUNCTIONS

    def update_demo_progress(self, session_id: str, progress: float) -> None:
        """Update demo progress for a session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session.progress = min(progress, 1.0)  # Cap at 100%

        # Log progress update
        self._log_interaction(
            session_id,
            "progress_updated",
            {"progress": progress, "timestamp": datetime.now().isoformat()},
        )

    def update_systematic_score(self, session_id: str, new_score: float) -> None:
        """Update systematic score for a session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session.systematic_score = new_score

        # Track systematic scores
        self.systematic_scores.append(new_score)

        # Log score update
        self._log_interaction(
            session_id,
            "systematic_score_updated",
            {
                "old_score": session.systematic_score,
                "new_score": new_score,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def update_learning_patterns(
        self, session_id: str, patterns: List[Dict[str, Any]]
    ) -> None:
        """Update learning patterns for a session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session.learning_patterns.extend(patterns)

        # Track learning patterns
        self.learning_patterns.extend(patterns)

        # Log pattern update
        self._log_interaction(
            session_id,
            "learning_patterns_updated",
            {
                "pattern_count": len(patterns),
                "total_patterns": len(session.learning_patterns),
                "timestamp": datetime.now().isoformat(),
            },
        )

    def update_demo_phase(self, session_id: str, phase: DemoPhase) -> None:
        """Update current demo phase for a session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        old_phase = session.current_phase
        session.current_phase = phase

        # Update view current phase
        self.demo_view.current_phase = phase

        # Log phase update
        self._log_interaction(
            session_id,
            "phase_updated",
            {
                "old_phase": old_phase.value,
                "new_phase": phase.value,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def update_session_interaction(
        self, session_id: str, interaction_type: str, details: Dict[str, Any]
    ) -> None:
        """Update session with new interaction"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        # Log interaction
        self._log_interaction(session_id, interaction_type, details)

        # Update view interaction log
        self.demo_view.log_interaction(interaction_type, details)

    # PRIVATE HELPER METHODS

    def _log_interaction(
        self, session_id: str, interaction_type: str, details: Dict[str, Any]
    ) -> None:
        """Log interaction for a session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "interaction_type": interaction_type,
                "details": details,
            }
            session.interactions.append(interaction)

    def _update_session_progress(
        self, session_id: str, progress_increment: float
    ) -> None:
        """Update session progress by increment"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.progress = min(session.progress + progress_increment, 1.0)

    # DEMO ORCHESTRATION METHODS

    def run_complete_demo(self, judge_id: str) -> Dict[str, Any]:
        """Run complete 3-minute demo for a judge"""
        # Create demo session
        session = self.create_demo_session(judge_id)

        # Run demo phases
        demo_result = self.demo_view.render_complete_demo()

        # Update session with demo results
        self.update_demo_progress(session.session_id, 1.0)
        self.update_demo_phase(session.session_id, DemoPhase.NEXT_STEPS)

        # Add demo analytics
        demo_analytics = self.demo_view.get_demo_analytics()

        # Combine results
        complete_result = {
            "session": {
                "session_id": session.session_id,
                "judge_id": judge_id,
                "start_time": session.start_time.isoformat(),
                "progress": session.progress,
                "systematic_score": session.systematic_score,
                "interactions": len(session.interactions),
            },
            "demo_content": demo_result,
            "analytics": demo_analytics,
            "model_health": {
                "spec_model": self.spec_model.check_health().health_score,
                "superiority_model": self.superiority_model.check_health().health_score,
                "agent_model": self.agent_model.check_health().health_score,
                "infra_model": self.infra_model.check_health().health_score,
            },
            "beast_mode_metrics": {
                "systematic_scores": self.systematic_scores,
                "learning_patterns": len(self.learning_patterns),
                "transformations_completed": len(self.transformation_history),
                "collaborations_completed": len(self.collaboration_history),
            },
        }

        return complete_result

    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "judge_id": session.judge_id,
            "duration_minutes": (datetime.now() - session.start_time).total_seconds()
            / 60,
            "progress": session.progress,
            "current_phase": session.current_phase.value,
            "interactions": len(session.interactions),
            "systematic_score": session.systematic_score,
            "learning_patterns": len(session.learning_patterns),
            "interaction_breakdown": {
                interaction["interaction_type"]: len(
                    [
                        i
                        for i in session.interactions
                        if i["interaction_type"] == interaction["interaction_type"]
                    ]
                )
                for interaction in session.interactions
            },
        }

    def get_controller_health(self) -> Dict[str, Any]:
        """Get overall controller health"""
        return {
            "active_sessions": len(self.active_sessions),
            "total_transformations": len(self.transformation_history),
            "total_collaborations": len(self.collaboration_history),
            "systematic_scores": {
                "count": len(self.systematic_scores),
                "average": (
                    sum(self.systematic_scores) / len(self.systematic_scores)
                    if self.systematic_scores
                    else 0
                ),
                "latest": self.systematic_scores[-1] if self.systematic_scores else 0,
            },
            "learning_patterns": {
                "count": len(self.learning_patterns),
                "unique_types": len(
                    set(
                        pattern.get("pattern_type", "unknown")
                        for pattern in self.learning_patterns
                    )
                ),
            },
            "model_health": {
                "spec_model": self.spec_model.check_health().health_score,
                "superiority_model": self.superiority_model.check_health().health_score,
                "agent_model": self.agent_model.check_health().health_score,
                "infra_model": self.infra_model.check_health().health_score,
            },
        }
