"""
Productivity Triage Orchestrator
===============================

🚨 THIS IS IT! THE MOMENT WE SHOULD HAVE TRAINED FOR! 🚨

Main coordination component for the Ghostbusters Productivity Triage system.
Manages the entire triage process for supernatural productivity explosions.

Author: Beast Mode Framework + Ghostbusters
Date: 2025-09-24
Purpose: Coordinate the coordinators themselves!
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# CRITICAL: Use the unified ReflectiveModule to avoid circular dependency hell
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability
)

from .interfaces import (
    IProductivityTriageOrchestrator,
    ProductivityTriageError,
    CriticalTriageError,
)
from .models import (
    TriageConfig,
    TriageReport,
    ExplosionAssessment,
    IntegrationPlan,
    IntegrationResult,
    WorkArtifact,
    ComplexityLevel,
    TriageStrategy,
    DomainType,
    CompletionStatus,
    ReadinessStatus,
)


class ProductivityTriageOrchestrator(ReflectiveModule, IProductivityTriageOrchestrator):
    """
    Main orchestrator for Ghostbusters Productivity Triage operations.
    
    This is the central coordination system that manages supernatural productivity 
    explosions where Beast Mode has generated so much valuable work that 
    coordination becomes the bottleneck.
    """
    
    def __init__(self, config: Optional[TriageConfig] = None):
        """Initialize the productivity triage orchestrator"""
        super().__init__()
        
        self.module_id = "ghostbusters_productivity_triage_orchestrator"
        self.config = config or TriageConfig()
        self.current_operation: Optional[str] = None
        self.triage_history: List[TriageReport] = []
        
        # Component instances (will be initialized lazily)
        self._content_discovery = None
        self._work_classification = None
        self._conflict_detection = None
        self._integration_planning = None
        self._quality_validator = None
        self._emergency_manager = None
        
        self._logger.info(f"🚨 Ghostbusters Productivity Triage Orchestrator initialized!")
        self._logger.info(f"   Ready to coordinate supernatural productivity explosions")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule compliance"""
        return {
            "module_id": self.module_id,
            "module_name": "ProductivityTriageOrchestrator",
            "version": "1.0.0",
            "description": "Coordinates supernatural productivity explosions",
            "author": "Beast Mode Framework + Ghostbusters",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "current_operation": self.current_operation,
            "triage_operations_completed": len(self.triage_history),
            "emergency_protocols_enabled": self.config.enable_emergency_protocols,
            "initialized_at": self._start_time.isoformat(),
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule compliance"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING,
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - ReflectiveModule compliance"""
        issues = []
        
        # Check configuration health
        if not self.config.scan_paths:
            issues.append("No scan paths configured")
        
        # Check component health (when initialized)
        if self._content_discovery and hasattr(self._content_discovery, 'get_health_status'):
            component_health = self._content_discovery.get_health_status()
            if component_health.status != ModuleStatus.HEALTHY:
                issues.append(f"Content discovery unhealthy: {component_health.status}")
        
        # Determine overall status
        if len(issues) == 0:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        elif len(issues) <= 2:
            status = ModuleStatus.WARNING
            health_score = 0.7
        else:
            status = ModuleStatus.ERROR
            health_score = 0.3
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count,
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation - ReflectiveModule compliance"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        try:
            # In degraded mode, we can still do basic assessment but not full integration
            degraded_capabilities = [ModuleCapability.DATA_PROCESSING]
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.VALIDATION,
                ModuleCapability.MONITORING,
            ]
            
            self._logger.warning("🚨 Productivity Triage entering degraded mode")
            self._logger.warning("   Full integration disabled, assessment-only mode active")
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities,
            )
            
        except Exception as e:
            self._logger.error(f"Failed to enter graceful degradation: {e}")
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e),
            )
    
    def run_triage(self, config: Optional[TriageConfig] = None) -> TriageReport:
        """
        Run complete productivity triage operation.
        
        This is the main entry point for coordinating supernatural productivity explosions!
        """
        operation_config = config or self.config
        
        with self.trace_operation("run_triage", config=operation_config.__dict__) as trace:
            try:
                self.current_operation = "full_triage"
                self._logger.info("🚨 STARTING GHOSTBUSTERS PRODUCTIVITY TRIAGE!")
                self._logger.info("   This is it! The moment we should have trained for!")
                
                start_time = datetime.now()
                
                # Step 1: Assess the productivity explosion
                self._logger.info("📊 Step 1: Assessing productivity explosion...")
                assessment = self.assess_productivity_explosion(operation_config)
                
                # Step 2: Create integration plan
                self._logger.info("📋 Step 2: Creating integration plan...")
                integration_plan = self.create_integration_plan(assessment)
                
                # Step 3: Execute integration (if strategy allows)
                execution_results = []
                if assessment.recommended_strategy in [TriageStrategy.SYSTEMATIC_INTEGRATION, TriageStrategy.SELECTIVE_INTEGRATION]:
                    self._logger.info("⚡ Step 3: Executing integration plan...")
                    execution_results = self.execute_integration(integration_plan)
                else:
                    self._logger.warning(f"⚠️ Integration skipped due to strategy: {assessment.recommended_strategy}")
                
                # Step 4: Generate comprehensive report
                self._logger.info("📄 Step 4: Generating triage report...")
                report = self._generate_triage_report(
                    assessment, integration_plan, execution_results, start_time
                )
                
                # Store in history
                self.triage_history.append(report)
                
                self._logger.info("✅ GHOSTBUSTERS PRODUCTIVITY TRIAGE COMPLETE!")
                self._logger.info(f"   Artifacts processed: {assessment.total_artifacts}")
                self._logger.info(f"   Domains affected: {len(assessment.domains_affected)}")
                self._logger.info(f"   Strategy used: {assessment.recommended_strategy.value}")
                
                trace.output_result = {
                    "success": True,
                    "report_id": report.report_id,
                    "artifacts_processed": assessment.total_artifacts,
                    "strategy": assessment.recommended_strategy.value,
                }
                
                return report
                
            except CriticalTriageError as e:
                self._logger.error(f"💥 CRITICAL TRIAGE ERROR: {e}")
                self._activate_emergency_protocols(str(e))
                raise
            except Exception as e:
                self._logger.error(f"❌ Triage operation failed: {e}")
                self._increment_error_count()
                raise ProductivityTriageError(f"Triage operation failed: {e}") from e
            finally:
                self.current_operation = None
    
    def assess_productivity_explosion(self, config: TriageConfig) -> ExplosionAssessment:
        """
        Assess the current productivity explosion situation.
        
        Analyzes the workspace to understand what we're dealing with.
        """
        with self.trace_operation("assess_productivity_explosion") as trace:
            try:
                self._logger.info("🔍 Analyzing productivity explosion...")
                
                # Initialize content discovery if needed
                if not self._content_discovery:
                    self._initialize_content_discovery()
                
                # Discover all work artifacts
                artifacts = self._content_discovery.scan_workspace(config)
                
                # Analyze the explosion
                domains_affected = list(set(artifact.domain for artifact in artifacts))
                
                completion_distribution = {}
                readiness_distribution = {}
                
                for status in CompletionStatus:
                    completion_distribution[status] = sum(
                        1 for artifact in artifacts if artifact.completion_status == status
                    )
                
                for status in ReadinessStatus:
                    readiness_distribution[status] = sum(
                        1 for artifact in artifacts if artifact.integration_readiness == status
                    )
                
                # Assess complexity and recommend strategy
                complexity = self._assess_integration_complexity(artifacts)
                strategy = self._recommend_triage_strategy(artifacts, complexity)
                
                # Identify critical issues and opportunities
                critical_issues = self._identify_critical_issues(artifacts)
                opportunities = self._identify_opportunities(artifacts)
                
                assessment = ExplosionAssessment(
                    total_artifacts=len(artifacts),
                    domains_affected=domains_affected,
                    completion_distribution=completion_distribution,
                    readiness_distribution=readiness_distribution,
                    conflict_count=0,  # Will be updated by conflict detection
                    integration_complexity=complexity,
                    recommended_strategy=strategy,
                    critical_issues=critical_issues,
                    opportunities=opportunities,
                )
                
                self._logger.info(f"📊 Explosion assessment complete:")
                self._logger.info(f"   Total artifacts: {assessment.total_artifacts}")
                self._logger.info(f"   Domains affected: {len(assessment.domains_affected)}")
                self._logger.info(f"   Complexity: {assessment.integration_complexity.value}")
                self._logger.info(f"   Recommended strategy: {assessment.recommended_strategy.value}")
                
                trace.output_result = assessment
                return assessment
                
            except Exception as e:
                self._logger.error(f"Failed to assess productivity explosion: {e}")
                self._increment_error_count()
                raise ProductivityTriageError(f"Assessment failed: {e}") from e
    
    def create_integration_plan(self, assessment: ExplosionAssessment) -> IntegrationPlan:
        """Create systematic integration plan based on assessment"""
        with self.trace_operation("create_integration_plan", assessment=assessment.__dict__) as trace:
            try:
                self._logger.info("📋 Creating integration plan...")
                
                # For now, create a basic plan structure
                # This will be expanded when we implement the planning system
                plan = IntegrationPlan(
                    plan_id=f"plan_{int(time.time())}",
                    commit_groups=[],
                    execution_order=[],
                    quality_checkpoints=[],
                    rollback_points=[],
                    estimated_duration=timedelta(hours=1),
                )
                
                self._logger.info(f"📋 Integration plan created: {plan.plan_id}")
                
                trace.output_result = plan
                return plan
                
            except Exception as e:
                self._logger.error(f"Failed to create integration plan: {e}")
                self._increment_error_count()
                raise ProductivityTriageError(f"Integration planning failed: {e}") from e
    
    def execute_integration(self, plan: IntegrationPlan) -> List[IntegrationResult]:
        """Execute the integration plan"""
        with self.trace_operation("execute_integration", plan_id=plan.plan_id) as trace:
            try:
                self._logger.info(f"⚡ Executing integration plan: {plan.plan_id}")
                
                # For now, return empty results
                # This will be expanded when we implement the execution system
                results = []
                
                self._logger.info("⚡ Integration execution complete")
                
                trace.output_result = results
                return results
                
            except Exception as e:
                self._logger.error(f"Failed to execute integration: {e}")
                self._increment_error_count()
                raise ProductivityTriageError(f"Integration execution failed: {e}") from e
    
    def _initialize_content_discovery(self):
        """Initialize content discovery engine lazily"""
        try:
            from .content_discovery import ContentDiscoveryEngine
            
            self._content_discovery = ContentDiscoveryEngine()
            self._logger.info("📡 Content discovery engine initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize content discovery: {e}")
            raise ProductivityTriageError(f"Content discovery initialization failed: {e}") from e
    
    def _assess_integration_complexity(self, artifacts: List[WorkArtifact]) -> ComplexityLevel:
        """Assess the complexity of integrating discovered artifacts"""
        if len(artifacts) == 0:
            return ComplexityLevel.LOW
        elif len(artifacts) < 10:
            return ComplexityLevel.LOW
        elif len(artifacts) < 50:
            return ComplexityLevel.MEDIUM
        elif len(artifacts) < 100:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.CRITICAL
    
    def _recommend_triage_strategy(self, artifacts: List[WorkArtifact], complexity: ComplexityLevel) -> TriageStrategy:
        """Recommend triage strategy based on artifacts and complexity"""
        if complexity == ComplexityLevel.CRITICAL:
            return TriageStrategy.EMERGENCY_PRESERVATION
        elif complexity == ComplexityLevel.HIGH:
            return TriageStrategy.SELECTIVE_INTEGRATION
        else:
            return TriageStrategy.SYSTEMATIC_INTEGRATION
    
    def _identify_critical_issues(self, artifacts: List[WorkArtifact]) -> List[str]:
        """Identify critical issues that need attention"""
        issues = []
        
        broken_count = sum(1 for a in artifacts if a.completion_status == CompletionStatus.BROKEN)
        if broken_count > 0:
            issues.append(f"{broken_count} broken artifacts detected")
        
        conflict_count = sum(1 for a in artifacts if a.integration_readiness == ReadinessStatus.HAS_CONFLICTS)
        if conflict_count > 0:
            issues.append(f"{conflict_count} artifacts have conflicts")
        
        return issues
    
    def _identify_opportunities(self, artifacts: List[WorkArtifact]) -> List[str]:
        """Identify opportunities for improvement"""
        opportunities = []
        
        ready_count = sum(1 for a in artifacts if a.integration_readiness == ReadinessStatus.READY)
        if ready_count > 0:
            opportunities.append(f"{ready_count} artifacts ready for immediate integration")
        
        complete_count = sum(1 for a in artifacts if a.completion_status == CompletionStatus.COMPLETE)
        if complete_count > 0:
            opportunities.append(f"{complete_count} complete implementations available")
        
        return opportunities
    
    def _generate_triage_report(
        self, 
        assessment: ExplosionAssessment, 
        plan: IntegrationPlan, 
        results: List[IntegrationResult],
        start_time: datetime
    ) -> TriageReport:
        """Generate comprehensive triage report"""
        
        total_duration = datetime.now() - start_time
        
        report = TriageReport(
            report_id=f"triage_report_{int(time.time())}",
            assessment=assessment,
            integration_plan=plan,
            execution_results=results,
            artifacts_integrated=len([r for r in results if r.success]),
            artifacts_deferred=assessment.total_artifacts - len([r for r in results if r.success]),
            conflicts_resolved=0,  # Will be calculated by conflict resolution
            recommendations=self._generate_recommendations(assessment),
            total_duration=total_duration,
            emergency_protocols_activated=False,
        )
        
        return report
    
    def _generate_recommendations(self, assessment: ExplosionAssessment) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []
        
        if assessment.integration_complexity == ComplexityLevel.CRITICAL:
            recommendations.append("Consider breaking work into smaller, manageable chunks")
            recommendations.append("Activate emergency protocols to preserve all work")
        
        if assessment.recommended_strategy == TriageStrategy.SELECTIVE_INTEGRATION:
            recommendations.append("Focus on integrating complete, ready artifacts first")
            recommendations.append("Defer experimental work until core functionality is stable")
        
        recommendations.append("Run full test suite before any integration")
        recommendations.append("Create backup branches for all major workstreams")
        
        return recommendations
    
    def _activate_emergency_protocols(self, reason: str):
        """Activate emergency protocols for critical situations"""
        try:
            self._logger.error(f"🚨 ACTIVATING EMERGENCY PROTOCOLS: {reason}")
            
            # Initialize emergency manager if needed
            if not self._emergency_manager:
                # Mock emergency manager for now
                class MockEmergencyManager:
                    def activate_emergency_protocols(self, reason: str):
                        return {"status": "activated", "reason": reason}
                
                self._emergency_manager = MockEmergencyManager()
            
            # Activate protocols
            result = self._emergency_manager.activate_emergency_protocols(reason)
            self._logger.info(f"🚨 Emergency protocols activated: {result}")
            
        except Exception as e:
            self._logger.error(f"💥 FAILED TO ACTIVATE EMERGENCY PROTOCOLS: {e}")
            # This is really bad - we can't even activate emergency protocols
            raise CriticalTriageError(f"Emergency protocol activation failed: {e}") from e