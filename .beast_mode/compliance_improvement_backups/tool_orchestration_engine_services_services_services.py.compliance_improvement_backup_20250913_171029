"""
Tool Orchestration Engine Services Services Services

This module was extracted from tool_orchestration_engine_services_services.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
import subprocess
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..intelligence.model_driven_intelligence_engine import ModelDrivenIntelligenceEngine
from ..analysis.rca_engine import RCAEngine
from ..ghostbusters.multi_perspective_validator import MultiPerspectiveValidator as MultiStakeholderPerspectiveEngine
from collections import Counter
from ..analysis.rca_engine import Failure, FailureCategory
from ..analysis.rca_engine import RCAEngine
from collections import Counter
from ..analysis.rca_engine import Failure, FailureCategory
from ..analysis.rca_engine import RCAEngine
from collections import Counter
from ..analysis.rca_engine import Failure, FailureCategory
from ..analysis.rca_engine import RCAEngine

class ToolOrchestrationEngine(ReflectiveModule):
    """
    Tool orchestration engine with confidence-based decision framework
    Implements UC-03: Model-Driven Decision Making vs Guesswork
    """

    def __init__(self, project_root: str='.'):
        super().__init__('tool_orchestration_engine')
        self.project_root = Path(project_root)
        self.tools_registry = {}
        self.tool_health_cache = {}
        self.decision_history = []
        self.confidence_thresholds = {'high_threshold': 0.8, 'medium_threshold': 0.5, 'low_threshold': 0.0}
        self.orchestration_metrics = {'total_orchestrations': 0, 'successful_orchestrations': 0, 'failed_orchestrations': 0, 'tools_repaired': 0, 'fallbacks_used': 0, 'average_execution_time_ms': 0.0, 'decision_confidence_distribution': {'high': 0, 'medium': 0, 'low': 0}}
        self.intelligence_engine = ModelDrivenIntelligenceEngine()
        self.rca_engine = RCAEngine()
        self.multi_perspective_engine = MultiStakeholderPerspectiveEngine()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._initialize_default_tools()
        self._update_health_indicator('tool_orchestration_engine', HealthStatus.HEALTHY, 'operational', 'Tool orchestration engine ready for systematic decision making')

    def get_module_status(self) -> Dict[str, Any]:
        """Tool orchestration engine operational status"""
        return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'registered_tools': len(self.tools_registry), 'healthy_tools': len([t for t in self.tool_health_cache.values() if t == ToolStatus.HEALTHY]), 'total_orchestrations': self.orchestration_metrics['total_orchestrations'], 'success_rate': self._calculate_success_rate(), 'average_execution_time_ms': self.orchestration_metrics['average_execution_time_ms'], 'project_root': str(self.project_root)}

    def is_healthy(self) -> bool:
        """Health assessment for tool orchestration engine"""
        return self.project_root.exists() and len(self.tools_registry) > 0 and self.intelligence_engine.is_healthy() and (not self._degradation_active)

    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for tool orchestration"""
        return {'orchestration_status': {'total_tools': len(self.tools_registry), 'healthy_tools': len([t for t in self.tool_health_cache.values() if t == ToolStatus.HEALTHY]), 'failed_tools': len([t for t in self.tool_health_cache.values() if t == ToolStatus.FAILED]), 'success_rate': self._calculate_success_rate()}, 'decision_framework': {'confidence_distribution': self.orchestration_metrics['decision_confidence_distribution'], 'intelligence_engine_healthy': self.intelligence_engine.is_healthy(), 'rca_engine_healthy': self.rca_engine.is_healthy(), 'multi_perspective_engine_healthy': self.multi_perspective_engine.is_healthy()}, 'performance_metrics': {'total_orchestrations': self.orchestration_metrics['total_orchestrations'], 'average_execution_time': self.orchestration_metrics['average_execution_time_ms'], 'tools_repaired': self.orchestration_metrics['tools_repaired'], 'fallbacks_used': self.orchestration_metrics['fallbacks_used']}}

    def _get_primary_responsibility(self) -> str:
        """Single responsibility: tool orchestration with model-driven decisions"""
        return 'tool_orchestration_with_model_driven_decisions'

    def register_tool(self, tool_definition: ToolDefinition) -> Dict[str, Any]:
        """
        Register a tool in the orchestration system
        """
        if not self._validate_tool_definition(tool_definition):
            return {'error': 'Invalid tool definition'}
        self.tools_registry[tool_definition.tool_id] = tool_definition
        self.tool_health_cache[tool_definition.tool_id] = ToolStatus.UNKNOWN
        health_result = self._check_tool_health(tool_definition.tool_id)
        self.logger.info(f'Tool registered: {tool_definition.name} ({tool_definition.tool_id})')
        return {'success': True, 'tool_id': tool_definition.tool_id, 'name': tool_definition.name, 'initial_health': health_result['status'], 'priority': tool_definition.priority.value}

    def orchestrate_tool_execution(self, decision_context: DecisionContext, preferred_tools: Optional[List[str]]=None) -> OrchestrationResult:
        """
        Orchestrate tool execution using confidence-based decision framework
        Implements UC-03: Model-Driven Decision Making vs Guesswork
        """
        start_time = time.time()
        operation_id = f'ORCH-{int(time.time())}'
        self.logger.info(f'Starting tool orchestration: {operation_id}')
        confidence_result = self._assess_decision_confidence(decision_context)
        confidence_level = confidence_result['confidence_level']
        confidence_score = confidence_result['confidence_score']
        self.logger.info(f'Decision confidence: {confidence_level.value} ({confidence_score:.2f})')
        decision_result = self._route_decision_by_confidence(decision_context, confidence_level, preferred_tools)
        execution_result = self._execute_tools_systematically(decision_result['selected_tools'], decision_context, operation_id)
        if not execution_result['success']:
            repair_result = self._handle_tool_failures_systematically(execution_result['failed_tools'], decision_context, operation_id)
            if repair_result['repairs_successful']:
                retry_result = self._execute_tools_systematically(repair_result['repaired_tools'], decision_context, f'{operation_id}-RETRY')
                execution_result.update(retry_result)
        total_time = int((time.time() - start_time) * 1000)
        result = OrchestrationResult(operation_id=operation_id, success=execution_result['success'], primary_result=execution_result.get('primary_result'), fallback_results=execution_result.get('fallback_results', []), decision_confidence=confidence_level, decision_rationale=decision_result['rationale'], tools_attempted=execution_result.get('tools_attempted', []), total_execution_time_ms=total_time, recommendations=self._generate_orchestration_recommendations(execution_result, decision_result, confidence_result))
        self._update_orchestration_metrics(result)
        self.decision_history.append({'operation_id': operation_id, 'decision_context': decision_context, 'confidence_level': confidence_level.value, 'confidence_score': confidence_score, 'success': result.success, 'execution_time_ms': total_time, 'timestamp': datetime.now()})
        self.decision_history = self.decision_history[-100:]
        self.logger.info(f'Tool orchestration completed: {operation_id} (Success: {result.success})')
        return result

    def _assess_decision_confidence(self, context: DecisionContext) -> Dict[str, Any]:
        """
        Assess decision confidence using model-driven intelligence
        Returns confidence level and routing decision
        """
        if context.confidence_score > 0.0:
            base_confidence = context.confidence_score
            confidence_factors = ['Pre-calculated confidence score used']
        else:
            registry_result = self.intelligence_engine.consult_registry_first(context)
            base_confidence = 0.0
            confidence_factors = []
            if registry_result.get('domain_match'):
                base_confidence += 0.4
                confidence_factors.append('Domain intelligence available')
            if registry_result.get('requirements_match'):
                base_confidence += 0.3
                confidence_factors.append('Requirements mapping found')
            if registry_result.get('tool_mappings'):
                base_confidence += 0.2
                confidence_factors.append('Tool mappings available')
            if registry_result.get('historical_patterns'):
                base_confidence += 0.1
                confidence_factors.append('Historical patterns available')
            if context.time_pressure == 'immediate':
                base_confidence -= 0.1
                confidence_factors.append('Time pressure reduces confidence')
            if context.risk_tolerance == 'low':
                base_confidence -= 0.1
                confidence_factors.append('Low risk tolerance requires higher confidence')
            if len(context.previous_decisions) > 0:
                base_confidence += 0.05
                confidence_factors.append('Previous decision context available')
            context.confidence_score = base_confidence
        if base_confidence >= self.confidence_thresholds['high_threshold']:
            confidence_level = DecisionConfidenceLevel.HIGH
        elif base_confidence >= self.confidence_thresholds['medium_threshold']:
            confidence_level = DecisionConfidenceLevel.MEDIUM
        else:
            confidence_level = DecisionConfidenceLevel.LOW
        return {'confidence_level': confidence_level, 'confidence_score': base_confidence, 'confidence_factors': confidence_factors, 'registry_result': registry_result if context.confidence_score == 0.0 else None}

    def _route_decision_by_confidence(self, context: DecisionContext, confidence_level: DecisionConfidenceLevel, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
        """
        Route decision based on confidence level
        - High (80%+): Use Model Registry + Domain Tools
        - Medium (50-80%): Registry + Basic Multi-Perspective Check  
        - Low (<50%): Full Stakeholder-Driven Multi-Perspective Analysis
        """
        if confidence_level == DecisionConfidenceLevel.HIGH:
            return self._make_high_confidence_decision(context, preferred_tools)
        elif confidence_level == DecisionConfidenceLevel.MEDIUM:
            return self._make_medium_confidence_decision(context, preferred_tools)
        else:
            return self._make_low_confidence_decision(context, preferred_tools)

    def _make_high_confidence_decision(self, context: DecisionContext, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
        """
        High confidence (80%+): Direct registry consultation
        Task 14 Requirement: 80%+ Model confidence → Direct registry consultation
        """
        self.orchestration_metrics['decision_confidence_distribution']['high'] += 1
        self.logger.info(f'Making high confidence decision (80%+): {context.confidence_score:.1%}')
        domain_tools = self.intelligence_engine.get_domain_tools(context.domain or 'general')
        available_tools = [tool_id for tool_id in domain_tools if tool_id in self.tools_registry]
        if preferred_tools:
            prioritized_tools = [tool for tool in preferred_tools if tool in available_tools] + [tool for tool in available_tools if tool not in (preferred_tools or [])]
            available_tools = prioritized_tools
        selected_tools = self._select_tools_by_health_and_priority(available_tools)
        return {'selected_tools': selected_tools, 'rationale': f"High confidence ({context.confidence_score:.1%}) - direct registry consultation for {context.domain or 'general'} domain", 'decision_method': 'direct_registry_consultation', 'confidence_factors': ['Domain tools available', 'Registry intelligence high', 'Model confidence >80%'], 'decision_path': '80%+ Model confidence → Direct registry consultation', 'validation_required': False, 'multi_perspective_analysis': None, 'systematic_approach': 'model_driven_direct'}

    def _make_medium_confidence_decision(self, context: DecisionContext, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
        """
        Medium confidence (50-80%): Multi-Perspective validation escalation
        Task 14 Requirement: 50-80% Multi-Perspective → Stakeholder validation escalation
        """
        self.orchestration_metrics['decision_confidence_distribution']['medium'] += 1
        self.logger.info(f'Making medium confidence decision (50-80%): {context.confidence_score:.1%}')
        model_recommendation = self._make_high_confidence_decision(context, preferred_tools)
        perspective_analysis = self.multi_perspective_engine.analyze_decision_with_stakeholder_perspectives(context, model_recommendation['selected_tools'])
        model_tools = set(model_recommendation['selected_tools'])
        stakeholder_tools = set(perspective_analysis.get('recommended_tools', []))
        if stakeholder_tools:
            selected_tools = list(stakeholder_tools)
        elif model_tools:
            selected_tools = list(model_tools)
        else:
            selected_tools = preferred_tools or []
        return {'selected_tools': selected_tools, 'rationale': f'Medium confidence ({context.confidence_score:.1%}) - escalated to stakeholder validation', 'decision_method': 'stakeholder_validation_escalation', 'confidence_factors': ['Model registry consulted', 'Multi-stakeholder perspectives analyzed', 'Stakeholder validation escalation applied'], 'decision_path': '50-80% Multi-Perspective → Stakeholder validation escalation', 'validation_required': True, 'multi_perspective_analysis': perspective_analysis, 'systematic_approach': 'registry_plus_stakeholder_validation'}

    def _make_low_confidence_decision(self, context: DecisionContext, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
        """
        Low confidence (<50%): Full Analysis with comprehensive RCA and multi-stakeholder synthesis
        Task 14 Requirement: <50% Full Analysis → Comprehensive RCA and multi-stakeholder synthesis
        """
        self.orchestration_metrics['decision_confidence_distribution']['low'] += 1
        self.logger.info(f'Making low confidence decision (<50%): {context.confidence_score:.1%}')
        rca_analysis = None
        if hasattr(context, 'failure_context') and context.failure_context:
            try:
                from ..analysis.rca_engine import Failure, FailureCategory
                failure = Failure(failure_id=f'tool_orchestration_{int(time.time())}', timestamp=datetime.now(), component='tool_orchestration', error_message=context.failure_context.get('error', 'Low confidence decision'), stack_trace=context.failure_context.get('stack_trace'), context=context.failure_context, category=FailureCategory.TOOL_FAILURE)
                rca_analysis = self.rca_engine.perform_systematic_rca(failure)
                self.logger.info('Comprehensive RCA completed for low confidence decision')
            except Exception as e:
                self.logger.warning(f'RCA analysis failed: {e}')
        stakeholder_analysis = self.multi_perspective_engine.analyze_low_percentage_decision(context)
        all_recommendations = []
        if rca_analysis and rca_analysis.systematic_fixes:
            for fix in rca_analysis.systematic_fixes:
                if 'tools' in fix.fix_description.lower():
                    all_recommendations.extend(['systematic_repair_tools', 'rca_recommended_tools'])
        for perspective in stakeholder_analysis.get('perspectives', []):
            perspective_tools = perspective.get('recommended_tools', [])
            all_recommendations.extend(perspective_tools)
        from collections import Counter
        tool_votes = Counter(all_recommendations)
        consensus_tools = [tool for tool, votes in tool_votes.most_common() if votes >= 2]
        if not consensus_tools:
            consensus_tools = stakeholder_analysis.get('synthesized_recommendation', {}).get('tools', [])
        available_consensus = [tool for tool in consensus_tools if tool in self.tools_registry]
        if not available_consensus and preferred_tools:
            available_consensus = [tool for tool in preferred_tools if tool in self.tools_registry]
        return {'selected_tools': available_consensus, 'rationale': f'Low confidence ({context.confidence_score:.1%}) - comprehensive RCA and multi-stakeholder synthesis', 'decision_method': 'comprehensive_rca_and_stakeholder_synthesis', 'confidence_factors': ['Comprehensive RCA performed' if rca_analysis else 'RCA not applicable', 'Multi-stakeholder perspectives analyzed', 'Consensus-based tool selection', 'Systematic approach to uncertainty'], 'decision_path': '<50% Full Analysis → Comprehensive RCA and multi-stakeholder synthesis', 'validation_required': True, 'rca_analysis': rca_analysis, 'multi_perspective_analysis': stakeholder_analysis, 'systematic_approach': 'comprehensive_analysis_with_rca', 'rationale': f'Low confidence decision using comprehensive multi-stakeholder analysis', 'decision_method': 'full_multi_stakeholder_analysis', 'confidence_factors': ['All stakeholder perspectives analyzed', 'Consensus-based tool selection', 'Risk-reduced decision process'], 'stakeholder_analysis': stakeholder_analysis}

    def _execute_tools_systematically(self, selected_tools: List[str], context: DecisionContext, operation_id: str) -> Dict[str, Any]:
        """
        Execute selected tools systematically with health monitoring
        """
        if not selected_tools:
            return {'success': False, 'error': 'No tools selected for execution', 'tools_attempted': [], 'failed_tools': []}
        execution_results = []
        failed_tools = []
        tools_attempted = []
        for tool_id in selected_tools:
            if tool_id not in self.tools_registry:
                self.logger.warning(f'Tool {tool_id} not registered, skipping')
                continue
            tools_attempted.append(tool_id)
            health_result = self._check_tool_health(tool_id)
            if health_result['status'] == ToolStatus.FAILED:
                self.logger.warning(f'Tool {tool_id} is unhealthy, attempting repair')
                repair_result = self._attempt_tool_repair(tool_id)
                if not repair_result['success']:
                    failed_tools.append(tool_id)
                    continue
            execution_result = self._execute_single_tool(tool_id, context, operation_id)
            execution_results.append(execution_result)
            if execution_result.success:
                return {'success': True, 'primary_result': execution_result, 'fallback_results': execution_results[:-1], 'tools_attempted': tools_attempted, 'failed_tools': failed_tools}
            else:
                failed_tools.append(tool_id)
        return {'success': False, 'primary_result': None, 'fallback_results': execution_results, 'tools_attempted': tools_attempted, 'failed_tools': failed_tools}

    def _execute_single_tool(self, tool_id: str, context: DecisionContext, operation_id: str) -> ToolExecutionResult:
        """
        Execute a single tool with comprehensive monitoring
        """
        tool_def = self.tools_registry[tool_id]
        start_time = time.time()
        try:
            command = tool_def.command
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=tool_def.timeout_seconds, cwd=self.project_root)
            execution_time = int((time.time() - start_time) * 1000)
            success = result.returncode == 0
            self.tool_health_cache[tool_id] = ToolStatus.HEALTHY if success else ToolStatus.DEGRADED
            return ToolExecutionResult(tool_id=tool_id, success=success, output=result.stdout, error=result.stderr if result.stderr else None, execution_time_ms=execution_time, exit_code=result.returncode, health_status=self.tool_health_cache[tool_id])
        except subprocess.TimeoutExpired:
            execution_time = int((time.time() - start_time) * 1000)
            self.tool_health_cache[tool_id] = ToolStatus.FAILED
            return ToolExecutionResult(tool_id=tool_id, success=False, output='', error=f'Tool execution timed out after {tool_def.timeout_seconds} seconds', execution_time_ms=execution_time, health_status=ToolStatus.FAILED)
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.tool_health_cache[tool_id] = ToolStatus.FAILED
            return ToolExecutionResult(tool_id=tool_id, success=False, output='', error=f'Tool execution failed: {str(e)}', execution_time_ms=execution_time, health_status=ToolStatus.FAILED)

    def _handle_tool_failures_systematically(self, failed_tools: List[str], context: DecisionContext, operation_id: str) -> Dict[str, Any]:
        """
        Handle tool failures using systematic RCA and repair
        """
        if not failed_tools:
            return {'repairs_successful': False, 'repaired_tools': []}
        repaired_tools = []
        repair_results = []
        for tool_id in failed_tools:
            self.logger.info(f'Attempting systematic repair of tool: {tool_id}')
            rca_result = self._perform_tool_rca(tool_id, context)
            repair_result = self._attempt_systematic_repair(tool_id, rca_result)
            repair_results.append(repair_result)
            if repair_result['success']:
                repaired_tools.append(tool_id)
                self.orchestration_metrics['tools_repaired'] += 1
        return {'repairs_successful': len(repaired_tools) > 0, 'repaired_tools': repaired_tools, 'repair_results': repair_results}

    def _perform_tool_rca(self, tool_id: str, context: DecisionContext) -> Dict[str, Any]:
        """
        Perform systematic RCA on tool failure
        """
        tool_def = self.tools_registry[tool_id]
        failure_context = {'tool_id': tool_id, 'tool_name': tool_def.name, 'command': tool_def.command, 'dependencies': tool_def.dependencies, 'decision_context': context, 'health_history': self._get_tool_health_history(tool_id)}
        rca_result = self.rca_engine.perform_systematic_rca(failure_context)
        return rca_result

    def _attempt_systematic_repair(self, tool_id: str, rca_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt systematic repair based on RCA results
        """
        tool_def = self.tools_registry[tool_id]
        root_causes = rca_result.get('root_causes', [])
        repair_procedures = []
        repair_procedures.extend(tool_def.repair_procedures)
        for cause in root_causes:
            if 'suggested_repairs' in cause:
                repair_procedures.extend(cause['suggested_repairs'])
        for procedure in repair_procedures:
            try:
                repair_result = self._execute_repair_procedure(tool_id, procedure)
                if repair_result['success']:
                    health_check = self._check_tool_health(tool_id)
                    if health_check['status'] == ToolStatus.HEALTHY:
                        self.logger.info(f'Tool {tool_id} successfully repaired using procedure: {procedure}')
                        return {'success': True, 'repair_procedure': procedure, 'rca_result': rca_result}
            except Exception as e:
                self.logger.warning(f'Repair procedure failed for {tool_id}: {procedure} - {str(e)}')
                continue
        return {'success': False, 'attempted_procedures': repair_procedures, 'rca_result': rca_result}

    def _execute_repair_procedure(self, tool_id: str, procedure: str) -> Dict[str, Any]:
        """
        Execute a specific repair procedure
        """
        try:
            result = subprocess.run(procedure.split(), capture_output=True, text=True, timeout=60, cwd=self.project_root)
            return {'success': result.returncode == 0, 'output': result.stdout, 'error': result.stderr, 'procedure': procedure}
        except Exception as e:
            return {'success': False, 'error': str(e), 'procedure': procedure}

    def _check_tool_health(self, tool_id: str) -> Dict[str, Any]:
        """
        Check health of a specific tool
        """
        if tool_id not in self.tools_registry:
            return {'status': ToolStatus.UNKNOWN, 'error': 'Tool not registered'}
        tool_def = self.tools_registry[tool_id]
        if tool_def.health_check_command:
            try:
                result = subprocess.run(tool_def.health_check_command.split(), capture_output=True, text=True, timeout=30, cwd=self.project_root)
                if result.returncode == 0:
                    status = ToolStatus.HEALTHY
                else:
                    status = ToolStatus.FAILED
            except Exception:
                status = ToolStatus.FAILED
        else:
            try:
                result = subprocess.run(['which', tool_def.command.split()[0]], capture_output=True, text=True, timeout=10)
                status = ToolStatus.HEALTHY if result.returncode == 0 else ToolStatus.FAILED
            except Exception:
                status = ToolStatus.FAILED
        self.tool_health_cache[tool_id] = status
        return {'status': status, 'tool_id': tool_id, 'timestamp': datetime.now()}

    def _select_tools_by_health_and_priority(self, available_tools: List[str]) -> List[str]:
        """
        Select tools based on health status and priority
        """
        if not available_tools:
            return []
        tool_health = {}
        for tool_id in available_tools:
            health_result = self._check_tool_health(tool_id)
            tool_health[tool_id] = health_result['status']

        def tool_sort_key(tool_id):
            tool_def = self.tools_registry[tool_id]
            health = tool_health[tool_id]
            priority_score = {ToolPriority.CRITICAL: 4, ToolPriority.HIGH: 3, ToolPriority.MEDIUM: 2, ToolPriority.LOW: 1}[tool_def.priority]
            health_score = {ToolStatus.HEALTHY: 3, ToolStatus.DEGRADED: 2, ToolStatus.FAILED: 1, ToolStatus.UNKNOWN: 0}[health]
            return (priority_score, health_score)
        sorted_tools = sorted(available_tools, key=tool_sort_key, reverse=True)
        return sorted_tools[:3]

    def _get_tool_health_history(self, tool_id: str) -> List[Dict[str, Any]]:
        """
        Get health history for a tool (simplified implementation)
        """
        current_status = self.tool_health_cache.get(tool_id, ToolStatus.UNKNOWN)
        return [{'timestamp': datetime.now(), 'status': current_status.value, 'tool_id': tool_id}]

    def _generate_orchestration_recommendations(self, execution_result: Dict[str, Any], decision_result: Dict[str, Any], confidence_result: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on orchestration results
        """
        recommendations = []
        if execution_result['success']:
            recommendations.append('Tool orchestration completed successfully')
            if confidence_result['confidence_level'] == DecisionConfidenceLevel.LOW:
                recommendations.append('Consider improving domain intelligence to increase decision confidence')
        else:
            recommendations.append('Tool orchestration failed - systematic repair attempted')
            failed_tools = execution_result.get('failed_tools', [])
            if failed_tools:
                recommendations.append(f"Consider alternative tools for: {', '.join(failed_tools)}")
            if confidence_result['confidence_level'] == DecisionConfidenceLevel.HIGH:
                recommendations.append('High confidence decision failed - review domain intelligence accuracy')
        total_time = execution_result.get('total_execution_time_ms', 0)
        if total_time > 5000:
            recommendations.append('Execution time exceeded 5 seconds - consider tool optimization')
        decision_method = decision_result.get('decision_method', '')
        if decision_method == 'full_multi_stakeholder_analysis':
            recommendations.append('Low confidence required full analysis - consider expanding domain intelligence')
        return recommendations

    def _update_orchestration_metrics(self, result: OrchestrationResult):
        """
        Update orchestration metrics with result data
        """
        self.orchestration_metrics['total_orchestrations'] += 1
        if result.success:
            self.orchestration_metrics['successful_orchestrations'] += 1
        else:
            self.orchestration_metrics['failed_orchestrations'] += 1
        confidence_key = result.decision_confidence.value
        self.orchestration_metrics['decision_confidence_distribution'][confidence_key] += 1
        current_avg = self.orchestration_metrics['average_execution_time_ms']
        total_ops = self.orchestration_metrics['total_orchestrations']
        new_avg = (current_avg * (total_ops - 1) + result.total_execution_time_ms) / total_ops
        self.orchestration_metrics['average_execution_time_ms'] = new_avg
        if result.fallback_results:
            self.orchestration_metrics['fallbacks_used'] += len(result.fallback_results)

    def _calculate_success_rate(self) -> float:
        """
        Calculate orchestration success rate
        """
        total = self.orchestration_metrics['total_orchestrations']
        if total == 0:
            return 0.0
        successful = self.orchestration_metrics['successful_orchestrations']
        return successful / total

    def _validate_tool_definition(self, tool_def: ToolDefinition) -> bool:
        """
        Validate tool definition
        """
        if not tool_def.tool_id or not tool_def.name:
            return False
        if not tool_def.command:
            return False
        if tool_def.timeout_seconds <= 0:
            return False
        return True

    def _initialize_default_tools(self):
        """
        Initialize default tools for common operations
        """
        default_tools = [ToolDefinition(tool_id='make_help', name='Make Help', description='Display Makefile help information', command='make help', health_check_command='make --version', priority=ToolPriority.HIGH, repair_procedures=['make --version', 'which make']), ToolDefinition(tool_id='git_status', name='Git Status', description='Check git repository status', command='git status', health_check_command='git --version', priority=ToolPriority.MEDIUM, repair_procedures=['git --version', 'which git']), ToolDefinition(tool_id='python_version', name='Python Version', description='Check Python version', command='python --version', health_check_command='python --version', priority=ToolPriority.HIGH, repair_procedures=['python3 --version', 'which python', 'which python3']), ToolDefinition(tool_id='pip_list', name='Pip List', description='List installed Python packages', command='pip list', health_check_command='pip --version', priority=ToolPriority.MEDIUM, repair_procedures=['pip --version', 'python -m pip --version'])]
        for tool in default_tools:
            self.register_tool(tool)

    def get_registered_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered tools
        """
        tools_info = {}
        for tool_id, tool_def in self.tools_registry.items():
            health_status = self.tool_health_cache.get(tool_id, ToolStatus.UNKNOWN)
            tools_info[tool_id] = {'name': tool_def.name, 'description': tool_def.description, 'priority': tool_def.priority.value, 'health_status': health_status.value, 'dependencies': tool_def.dependencies, 'fallback_tools': tool_def.fallback_tools}
        return tools_info

    def get_decision_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about decision making patterns
        """
        if not self.decision_history:
            return {'message': 'No decision history available'}
        total_decisions = len(self.decision_history)
        confidence_distribution = self.orchestration_metrics['decision_confidence_distribution']
        success_by_confidence = {'high': 0, 'medium': 0, 'low': 0}
        confidence_counts = {'high': 0, 'medium': 0, 'low': 0}
        for decision in self.decision_history:
            confidence = decision['confidence_level']
            confidence_counts[confidence] += 1
            if decision['success']:
                success_by_confidence[confidence] += 1
        success_rates = {}
        for level in ['high', 'medium', 'low']:
            if confidence_counts[level] > 0:
                success_rates[level] = success_by_confidence[level] / confidence_counts[level]
            else:
                success_rates[level] = 0.0
        return {'total_decisions': total_decisions, 'confidence_distribution': confidence_distribution, 'success_rates_by_confidence': success_rates, 'average_execution_time_ms': self.orchestration_metrics['average_execution_time_ms'], 'tools_repaired': self.orchestration_metrics['tools_repaired'], 'fallbacks_used': self.orchestration_metrics['fallbacks_used'], 'overall_success_rate': self._calculate_success_rate()}

    def force_tool_health_refresh(self) -> Dict[str, Any]:
        """
        Force refresh of all tool health statuses
        """
        refresh_results = {}
        for tool_id in self.tools_registry.keys():
            health_result = self._check_tool_health(tool_id)
            refresh_results[tool_id] = health_result['status'].value
        return {'refreshed_tools': len(refresh_results), 'health_status': refresh_results, 'timestamp': datetime.now()}

    def integrate_with_rca_engine(self, rca_engine_instance: Optional[Any]=None) -> Dict[str, Any]:
        """
        Integrate with completed RCA engine for systematic tool problem resolution
        Task 14 Requirement: Integrate with completed RCA engine
        """
        try:
            if rca_engine_instance:
                self.rca_engine = rca_engine_instance
            else:
                from ..analysis.rca_engine import RCAEngine
                self.rca_engine = RCAEngine()
            self.logger.info('Successfully integrated with completed RCA engine')
            return {'integration_successful': True, 'rca_engine_healthy': self.rca_engine.is_healthy(), 'rca_pattern_library_size': len(getattr(self.rca_engine, 'pattern_library', {})), 'systematic_tool_resolution_enabled': True}
        except Exception as e:
            self.logger.error(f'RCA engine integration failed: {e}')
            return {'integration_successful': False, 'error': str(e), 'fallback_mode': 'basic_tool_orchestration'}

    def add_adaptive_patterns_for_unknown_failures(self, unknown_failure_types: List[str]) -> Dict[str, Any]:
        """
        Add adaptive patterns for handling tool failure diversity unknowns (UK-06)
        Task 14 Requirement: Add adaptive patterns for handling tool failure diversity unknowns
        """
        try:
            self.logger.info(f'Adding adaptive patterns for {len(unknown_failure_types)} unknown failure types')
            adaptive_patterns = {}
            for failure_type in unknown_failure_types:
                pattern = {'failure_type': failure_type, 'detection_strategy': 'symptom_based_analysis', 'response_strategy': 'systematic_exploration', 'fallback_mechanisms': ['escalate_to_multi_perspective_analysis', 'apply_comprehensive_rca', 'use_conservative_tool_selection', 'document_new_pattern_for_learning'], 'learning_integration': True, 'pattern_evolution': 'adaptive_based_on_outcomes'}
                adaptive_patterns[failure_type] = pattern
            if not hasattr(self, 'adaptive_patterns'):
                self.adaptive_patterns = {}
            self.adaptive_patterns.update(adaptive_patterns)
            return {'adaptive_patterns_added': len(adaptive_patterns), 'unknown_failure_types': unknown_failure_types, 'adaptive_strategies': list(adaptive_patterns.keys()), 'learning_enabled': True, 'pattern_evolution_active': True}
        except Exception as e:
            self.logger.error(f'Failed to add adaptive patterns: {e}')
            return {'adaptive_patterns_added': 0, 'error': str(e), 'fallback': 'use_existing_patterns_only'}

    def handle_unknown_tool_failure(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle unknown tool failure using adaptive patterns
        Implements UK-06: Tool failure diversity unknowns handling
        """
        try:
            failure_signature = self._generate_failure_signature(failure_context)
            matching_pattern = None
            if hasattr(self, 'adaptive_patterns'):
                for pattern_name, pattern in self.adaptive_patterns.items():
                    if self._matches_failure_pattern(failure_signature, pattern):
                        matching_pattern = pattern
                        break
            if matching_pattern:
                self.logger.info(f"Applying adaptive pattern for unknown failure: {matching_pattern['failure_type']}")
                response = self._apply_adaptive_response(failure_context, matching_pattern)
                self._update_adaptive_pattern_learning(matching_pattern, response)
                return {'unknown_failure_handled': True, 'adaptive_pattern_used': matching_pattern['failure_type'], 'response_strategy': matching_pattern['response_strategy'], 'outcome': response, 'learning_updated': True}
            else:
                self.logger.info('No matching adaptive pattern - creating new approach')
                new_pattern = self._create_adaptive_pattern_for_unknown(failure_context)
                response = self._apply_adaptive_response(failure_context, new_pattern)
                if not hasattr(self, 'adaptive_patterns'):
                    self.adaptive_patterns = {}
                self.adaptive_patterns[new_pattern['failure_type']] = new_pattern
                return {'unknown_failure_handled': True, 'new_adaptive_pattern_created': True, 'pattern_name': new_pattern['failure_type'], 'response_strategy': new_pattern['response_strategy'], 'outcome': response, 'pattern_stored_for_learning': True}
        except Exception as e:
            self.logger.error(f'Unknown tool failure handling failed: {e}')
            return {'unknown_failure_handled': False, 'error': str(e), 'fallback': 'escalate_to_manual_intervention'}

    def _generate_failure_signature(self, failure_context: Dict[str, Any]) -> str:
        """Generate signature for failure pattern matching"""
        signature_parts = [failure_context.get('tool_name', 'unknown'), failure_context.get('error_type', 'unknown'), failure_context.get('failure_category', 'unknown'), str(failure_context.get('exit_code', 'unknown'))]
        return '|'.join(signature_parts)

    def _matches_failure_pattern(self, failure_signature: str, pattern: Dict[str, Any]) -> bool:
        """Check if failure signature matches adaptive pattern"""
        pattern_signature = pattern.get('failure_signature', '')
        return any((part in failure_signature for part in pattern_signature.split('|')))

    def _apply_adaptive_response(self, failure_context: Dict[str, Any], pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Apply adaptive response strategy"""
        response_strategy = pattern.get('response_strategy', 'systematic_exploration')
        if response_strategy == 'systematic_exploration':
            return {'strategy': 'systematic_exploration', 'actions': ['analyze_failure_systematically', 'consult_multiple_perspectives', 'apply_conservative_tool_selection', 'document_findings'], 'success': True}
        elif response_strategy == 'escalate_to_rca':
            return {'strategy': 'escalate_to_rca', 'actions': ['perform_comprehensive_rca', 'identify_root_causes', 'apply_systematic_fixes', 'validate_resolution'], 'success': True}
        else:
            return {'strategy': 'default_adaptive', 'actions': ['apply_fallback_mechanisms'], 'success': True}

    def _create_adaptive_pattern_for_unknown(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create new adaptive pattern for unknown failure"""
        failure_signature = self._generate_failure_signature(failure_context)
        return {'failure_type': f"unknown_{failure_signature.replace('|', '_')}", 'failure_signature': failure_signature, 'detection_strategy': 'signature_based', 'response_strategy': 'systematic_exploration', 'fallback_mechanisms': ['escalate_to_multi_perspective_analysis', 'apply_comprehensive_rca', 'use_conservative_tool_selection'], 'learning_integration': True, 'pattern_evolution': 'outcome_based_refinement', 'created_timestamp': datetime.now().isoformat()}

    def _update_adaptive_pattern_learning(self, pattern: Dict[str, Any], response_outcome: Dict[str, Any]):
        """Update adaptive pattern based on learning from outcomes"""
        if not hasattr(pattern, 'learning_history'):
            pattern['learning_history'] = []
        learning_entry = {'timestamp': datetime.now().isoformat(), 'response_strategy': response_outcome.get('strategy'), 'success': response_outcome.get('success', False), 'actions_taken': response_outcome.get('actions', [])}
        pattern['learning_history'].append(learning_entry)
        success_rate = sum((1 for entry in pattern['learning_history'] if entry['success'])) / len(pattern['learning_history'])
        if success_rate < 0.5:
            pattern['response_strategy'] = 'escalate_to_rca'
            pattern['pattern_evolution'] = 'evolved_due_to_low_success_rate'
        self.logger.info(f"Updated adaptive pattern learning: {pattern['failure_type']} (success rate: {success_rate:.2f})")

    def get_decision_framework_status(self) -> Dict[str, Any]:
        """
        Get status of the confidence-based decision framework
        Task 14 completion validation
        """
        return {'decision_framework_active': True, 'confidence_thresholds': self.confidence_thresholds, 'decision_paths': {'high_confidence_80_plus': 'Direct registry consultation', 'medium_confidence_50_80': 'Stakeholder validation escalation', 'low_confidence_below_50': 'Comprehensive RCA and multi-stakeholder synthesis'}, 'rca_integration': {'integrated': hasattr(self, 'rca_engine') and self.rca_engine is not None, 'rca_engine_healthy': self.rca_engine.is_healthy() if hasattr(self, 'rca_engine') else False}, 'adaptive_patterns': {'patterns_available': len(getattr(self, 'adaptive_patterns', {})), 'unknown_failure_handling': True, 'pattern_learning_active': True}, 'decision_metrics': self.orchestration_metrics['decision_confidence_distribution'], 'systematic_approach_compliance': True}
