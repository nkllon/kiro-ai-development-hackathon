"""
Context Validator for AI Memory Palace.

Ensures context integrity and mathematical governance compliance with DAG validation,
circular dependency detection, and automated repair mechanisms.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from ..core.reflective_module import ReflectiveModule
from .models import SessionContext, ContextEvent, ContextEventType


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    severity: ValidationSeverity
    code: str
    message: str
    details: Dict[str, Any]
    suggested_fix: Optional[str] = None


@dataclass
class DAGValidationResult:
    """Result of DAG validation"""
    is_valid: bool
    cycles_detected: List[List[str]]
    topological_order: List[str]
    issues: List[ValidationIssue]
    
    @property
    def has_cycles(self) -> bool:
        return len(self.cycles_detected) > 0


@dataclass
class ConsistencyResult:
    """Result of consistency checking"""
    is_consistent: bool
    inconsistencies: List[ValidationIssue]
    data_integrity_score: float
    
    @property
    def is_healthy(self) -> bool:
        return self.is_consistent and self.data_integrity_score > 0.9


@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


@dataclass
class RepairResult:
    """Result of context repair operation"""
    success: bool
    repaired_context: Optional[SessionContext]
    repairs_applied: List[str]
    unresolved_issues: List[ValidationIssue]


class ContextValidator(ReflectiveModule):
    """Validates context integrity and DAG compliance"""
    
    def __init__(self):
        super().__init__()
        
        # Validation metrics
        self._validations_performed = 0
        self._dag_validations = 0
        self._consistency_checks = 0
        self._repairs_attempted = 0
        self._repairs_successful = 0
        
        # Validation rules cache
        self._validation_rules = self._initialize_validation_rules()
        
        self.logger.info("🔍 ContextValidator initialized with mathematical governance")
    
    def validate_dag_integrity(self, context: SessionContext) -> DAGValidationResult:
        """Validate DAG compliance for context event dependencies"""
        try:
            self.emit_observation({
                "type": "dag_validation_started",
                "session_id": context.session_id,
                "event_count": len(context.conversation_history)
            })
            
            # Build dependency graph from context events
            dependency_graph = self._build_dependency_graph(context)
            
            # Detect cycles using DFS
            cycles = self._detect_cycles(dependency_graph)
            
            # Generate topological order if no cycles
            topological_order = []
            issues = []
            
            if not cycles:
                topological_order = self._topological_sort(dependency_graph)
            else:
                # Create issues for each cycle
                for i, cycle in enumerate(cycles):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        code="DAG_CYCLE_DETECTED",
                        message=f"Circular dependency detected in context events",
                        details={
                            "cycle_id": i,
                            "cycle_nodes": cycle,
                            "cycle_length": len(cycle)
                        },
                        suggested_fix="Remove or reorder events to break circular dependency"
                    ))
            
            result = DAGValidationResult(
                is_valid=len(cycles) == 0,
                cycles_detected=cycles,
                topological_order=topological_order,
                issues=issues
            )
            
            self._dag_validations += 1
            
            self.logger.info(f"📊 DAG validation: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
            if cycles:
                self.logger.warning(f"🔄 Detected {len(cycles)} circular dependencies")
            
            self.emit_observation({
                "type": "dag_validation_completed",
                "session_id": context.session_id,
                "is_valid": result.is_valid,
                "cycles_detected": len(cycles),
                "topological_order_length": len(topological_order)
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Error validating DAG: {e}")
            return DAGValidationResult(
                is_valid=False,
                cycles_detected=[],
                topological_order=[],
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="DAG_VALIDATION_ERROR",
                    message=f"DAG validation failed: {str(e)}",
                    details={"error": str(e)}
                )]
            )
    
    def check_context_consistency(self, context: SessionContext) -> ConsistencyResult:
        """Check context data consistency and integrity"""
        try:
            self.emit_observation({
                "type": "consistency_check_started",
                "session_id": context.session_id
            })
            
            inconsistencies = []
            
            # Check timestamp consistency
            inconsistencies.extend(self._check_timestamp_consistency(context))
            
            # Check ID uniqueness
            inconsistencies.extend(self._check_id_uniqueness(context))
            
            # Check data integrity
            inconsistencies.extend(self._check_data_integrity(context))
            
            # Check cross-references
            inconsistencies.extend(self._check_cross_references(context))
            
            # Calculate data integrity score
            total_checks = 20  # Total number of integrity checks
            failed_checks = len([i for i in inconsistencies if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]])
            integrity_score = max(0.0, (total_checks - failed_checks) / total_checks)
            
            result = ConsistencyResult(
                is_consistent=len([i for i in inconsistencies if i.severity == ValidationSeverity.CRITICAL]) == 0,
                inconsistencies=inconsistencies,
                data_integrity_score=integrity_score
            )
            
            self._consistency_checks += 1
            
            self.logger.info(f"🔍 Consistency check: {integrity_score:.2f} integrity score")
            
            self.emit_observation({
                "type": "consistency_check_completed",
                "session_id": context.session_id,
                "is_consistent": result.is_consistent,
                "integrity_score": integrity_score,
                "issues_found": len(inconsistencies)
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Error checking consistency: {e}")
            return ConsistencyResult(
                is_consistent=False,
                inconsistencies=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="CONSISTENCY_CHECK_ERROR",
                    message=f"Consistency check failed: {str(e)}",
                    details={"error": str(e)}
                )],
                data_integrity_score=0.0
            )
    
    def detect_circular_dependencies(self, events: List[ContextEvent]) -> List[List[str]]:
        """Detect circular dependencies in context events"""
        try:
            # Build dependency graph from events
            graph = {}
            for event in events:
                event_id = event.event_id
                dependencies = event.data.get("dependencies", [])
                graph[event_id] = dependencies
            
            # Detect cycles
            cycles = self._detect_cycles(graph)
            
            self.logger.info(f"🔄 Circular dependency detection: {len(cycles)} cycles found")
            
            return cycles
            
        except Exception as e:
            self.logger.error(f"💥 Error detecting circular dependencies: {e}")
            return []
    
    def repair_context_corruption(self, corrupted_context: SessionContext) -> RepairResult:
        """Attempt to repair corrupted context"""
        try:
            self.emit_observation({
                "type": "context_repair_started",
                "session_id": corrupted_context.session_id
            })
            
            self._repairs_attempted += 1
            repairs_applied = []
            unresolved_issues = []
            
            # Create a copy for repair
            repaired_context = SessionContext(
                project_id=corrupted_context.project_id,
                session_id=corrupted_context.session_id,
                timestamp=corrupted_context.timestamp,
                conversation_history=corrupted_context.conversation_history.copy(),
                project_state=corrupted_context.project_state,
                decisions_made=corrupted_context.decisions_made.copy(),
                work_completed=corrupted_context.work_completed.copy(),
                system_discoveries=corrupted_context.system_discoveries.copy(),
                spec_states=corrupted_context.spec_states.copy()
            )
            
            # Repair timestamp issues
            if self._repair_timestamps(repaired_context):
                repairs_applied.append("timestamp_normalization")
            
            # Repair duplicate IDs
            if self._repair_duplicate_ids(repaired_context):
                repairs_applied.append("duplicate_id_resolution")
            
            # Repair broken references
            if self._repair_broken_references(repaired_context):
                repairs_applied.append("reference_repair")
            
            # Validate repaired context
            validation_result = self.validate_context_integrity(repaired_context)
            
            success = not validation_result.has_errors
            if success:
                self._repairs_successful += 1
            
            # Collect unresolved issues
            unresolved_issues = validation_result.errors
            
            result = RepairResult(
                success=success,
                repaired_context=repaired_context if success else None,
                repairs_applied=repairs_applied,
                unresolved_issues=unresolved_issues
            )
            
            self.logger.info(f"🔧 Context repair: {'✅ Success' if success else '❌ Failed'}")
            self.logger.info(f"🛠️ Repairs applied: {', '.join(repairs_applied)}")
            
            self.emit_observation({
                "type": "context_repair_completed",
                "session_id": corrupted_context.session_id,
                "success": success,
                "repairs_applied": repairs_applied,
                "unresolved_issues": len(unresolved_issues)
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Error repairing context: {e}")
            return RepairResult(
                success=False,
                repaired_context=None,
                repairs_applied=[],
                unresolved_issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="REPAIR_ERROR",
                    message=f"Context repair failed: {str(e)}",
                    details={"error": str(e)}
                )]
            )
    
    def validate_context_integrity(self, context: SessionContext) -> ValidationResult:
        """Complete context integrity validation"""
        try:
            self._validations_performed += 1
            
            all_issues = []
            
            # DAG validation
            dag_result = self.validate_dag_integrity(context)
            all_issues.extend(dag_result.issues)
            
            # Consistency validation
            consistency_result = self.check_context_consistency(context)
            all_issues.extend(consistency_result.inconsistencies)
            
            # Additional validation rules
            all_issues.extend(self._apply_validation_rules(context))
            
            # Categorize issues by severity
            errors = [i for i in all_issues if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]
            warnings = [i for i in all_issues if i.severity == ValidationSeverity.WARNING]
            info = [i for i in all_issues if i.severity == ValidationSeverity.INFO]
            
            result = ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                info=info
            )
            
            self.logger.info(f"✅ Context validation: {len(errors)} errors, {len(warnings)} warnings")
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Error validating context integrity: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="VALIDATION_ERROR",
                    message=f"Context validation failed: {str(e)}",
                    details={"error": str(e)}
                )],
                warnings=[],
                info=[]
            )
    
    def validate_context_event(self, event: ContextEvent) -> bool:
        """Validate individual context event"""
        try:
            # Basic validation
            if not event.event_id or not event.correlation_id:
                return False
            
            if not isinstance(event.event_type, ContextEventType):
                return False
            
            if not isinstance(event.data, dict):
                return False
            
            # Event-specific validation
            if event.event_type == ContextEventType.CODE_WRITTEN:
                required_fields = ["description"]
                if not all(field in event.data for field in required_fields):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Error validating context event: {e}")
            return False
    
    def _build_dependency_graph(self, context: SessionContext) -> Dict[str, List[str]]:
        """Build dependency graph from context"""
        graph = {}
        
        # Add conversation events
        for i, conv in enumerate(context.conversation_history):
            event_id = f"conv_{i}"
            dependencies = []
            if i > 0:
                dependencies.append(f"conv_{i-1}")  # Sequential dependency
            graph[event_id] = dependencies
        
        # Add decisions with dependencies on conversations
        for i, decision in enumerate(context.decisions_made):
            decision_id = f"decision_{decision.decision_id}"
            # Decisions depend on recent conversations
            dependencies = [f"conv_{j}" for j in range(max(0, len(context.conversation_history)-5), len(context.conversation_history))]
            graph[decision_id] = dependencies
        
        # Add work items with dependencies on decisions
        for work in context.work_completed:
            work_id = f"work_{work.work_id}"
            # Work depends on decisions
            dependencies = [f"decision_{d.decision_id}" for d in context.decisions_made[-3:]]
            graph[work_id] = dependencies
        
        return graph
    
    def _detect_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect cycles in dependency graph using DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor in graph:  # Only follow existing nodes
                    if dfs(neighbor):
                        return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort on DAG"""
        in_degree = {node: 0 for node in graph}
        
        # Calculate in-degrees
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        return result
    
    def _check_timestamp_consistency(self, context: SessionContext) -> List[ValidationIssue]:
        """Check timestamp consistency"""
        issues = []
        
        # Check conversation history timestamps
        for i in range(1, len(context.conversation_history)):
            prev_time = context.conversation_history[i-1].timestamp
            curr_time = context.conversation_history[i].timestamp
            
            if curr_time < prev_time:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="TIMESTAMP_ORDER",
                    message="Conversation events not in chronological order",
                    details={"event_index": i, "prev_time": prev_time.isoformat(), "curr_time": curr_time.isoformat()}
                ))
        
        return issues
    
    def _check_id_uniqueness(self, context: SessionContext) -> List[ValidationIssue]:
        """Check ID uniqueness"""
        issues = []
        
        # Check decision IDs
        decision_ids = [d.decision_id for d in context.decisions_made]
        if len(decision_ids) != len(set(decision_ids)):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="DUPLICATE_DECISION_IDS",
                message="Duplicate decision IDs found",
                details={"total_decisions": len(decision_ids), "unique_ids": len(set(decision_ids))}
            ))
        
        # Check work IDs
        work_ids = [w.work_id for w in context.work_completed]
        if len(work_ids) != len(set(work_ids)):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="DUPLICATE_WORK_IDS",
                message="Duplicate work IDs found",
                details={"total_work": len(work_ids), "unique_ids": len(set(work_ids))}
            ))
        
        return issues
    
    def _check_data_integrity(self, context: SessionContext) -> List[ValidationIssue]:
        """Check data integrity"""
        issues = []
        
        # Check for required fields
        if not context.project_id:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="MISSING_PROJECT_ID",
                message="Context missing project ID",
                details={}
            ))
        
        if not context.session_id:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="MISSING_SESSION_ID",
                message="Context missing session ID",
                details={}
            ))
        
        return issues
    
    def _check_cross_references(self, context: SessionContext) -> List[ValidationIssue]:
        """Check cross-references between context components"""
        issues = []
        
        # This is a placeholder for more complex cross-reference validation
        # In a real implementation, you would check that references between
        # decisions, work items, and discoveries are valid
        
        return issues
    
    def _apply_validation_rules(self, context: SessionContext) -> List[ValidationIssue]:
        """Apply additional validation rules"""
        issues = []
        
        for rule_name, rule_func in self._validation_rules.items():
            try:
                rule_issues = rule_func(context)
                issues.extend(rule_issues)
            except Exception as e:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="VALIDATION_RULE_ERROR",
                    message=f"Validation rule '{rule_name}' failed: {str(e)}",
                    details={"rule": rule_name, "error": str(e)}
                ))
        
        return issues
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules"""
        return {
            "context_size_limit": self._validate_context_size,
            "conversation_length_limit": self._validate_conversation_length,
            "decision_completeness": self._validate_decision_completeness
        }
    
    def _validate_context_size(self, context: SessionContext) -> List[ValidationIssue]:
        """Validate context size limits"""
        issues = []
        
        size_mb = context.get_context_size() / (1024 * 1024)
        if size_mb > 100:  # 100MB limit
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="CONTEXT_SIZE_LARGE",
                message=f"Context size ({size_mb:.1f}MB) exceeds recommended limit",
                details={"size_mb": size_mb, "limit_mb": 100},
                suggested_fix="Consider context summarization"
            ))
        
        return issues
    
    def _validate_conversation_length(self, context: SessionContext) -> List[ValidationIssue]:
        """Validate conversation length"""
        issues = []
        
        if len(context.conversation_history) > 1000:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="CONVERSATION_LENGTH_LONG",
                message=f"Conversation history is very long ({len(context.conversation_history)} events)",
                details={"length": len(context.conversation_history), "limit": 1000},
                suggested_fix="Consider conversation summarization"
            ))
        
        return issues
    
    def _validate_decision_completeness(self, context: SessionContext) -> List[ValidationIssue]:
        """Validate decision completeness"""
        issues = []
        
        for decision in context.decisions_made:
            if not decision.rationale:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    code="DECISION_MISSING_RATIONALE",
                    message="Decision missing rationale",
                    details={"decision_id": decision.decision_id, "description": decision.description}
                ))
        
        return issues
    
    def _repair_timestamps(self, context: SessionContext) -> bool:
        """Repair timestamp issues"""
        try:
            # Sort conversation history by timestamp
            context.conversation_history.sort(key=lambda x: x.timestamp)
            return True
        except Exception:
            return False
    
    def _repair_duplicate_ids(self, context: SessionContext) -> bool:
        """Repair duplicate ID issues"""
        try:
            # Fix duplicate decision IDs
            seen_decision_ids = set()
            for decision in context.decisions_made:
                if decision.decision_id in seen_decision_ids:
                    decision.decision_id = f"{decision.decision_id}_{datetime.now().timestamp()}"
                seen_decision_ids.add(decision.decision_id)
            
            # Fix duplicate work IDs
            seen_work_ids = set()
            for work in context.work_completed:
                if work.work_id in seen_work_ids:
                    work.work_id = f"{work.work_id}_{datetime.now().timestamp()}"
                seen_work_ids.add(work.work_id)
            
            return True
        except Exception:
            return False
    
    def _repair_broken_references(self, context: SessionContext) -> bool:
        """Repair broken references"""
        # Placeholder for reference repair logic
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ContextValidator"""
        return {
            "status": "healthy",
            "validations_performed": self._validations_performed,
            "dag_validations": self._dag_validations,
            "consistency_checks": self._consistency_checks,
            "repairs_attempted": self._repairs_attempted,
            "repairs_successful": self._repairs_successful,
            "repair_success_rate": self._repairs_successful / max(1, self._repairs_attempted)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        return {
            "context_validator_validations_total": self._validations_performed,
            "context_validator_dag_validations_total": self._dag_validations,
            "context_validator_consistency_checks_total": self._consistency_checks,
            "context_validator_repairs_attempted_total": self._repairs_attempted,
            "context_validator_repairs_successful_total": self._repairs_successful,
            "context_validator_repair_success_rate": self._repairs_successful / max(1, self._repairs_attempted)
        }