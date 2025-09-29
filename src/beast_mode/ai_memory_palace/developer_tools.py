"""
Developer Experience Tools for AI Memory Palace.

Provides context inspection, editing interface, debugging tools, and 
export/import capabilities for developers working with the context system.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import uuid

from src.beast_mode.core.beastly_module import BeastlyModule
from .models import SessionContext, ContextEvent, ContextEventType
from .context_manager import ContextManager
from .context_registry import ContextRegistry
from .context_validator import ContextValidator


class ContextInspector(BeastlyModule):
    """Context inspection and debugging tools"""
    
    def __init__(self, context_manager: ContextManager):
        super().__init__()
        
        self.context_manager = context_manager
        self.registry = context_manager.registry
        self.validator = context_manager.validator
        
        # Inspector metrics
        self._inspections_performed = 0
        self._exports_created = 0
        self._imports_processed = 0
        self._validations_run = 0
        
        self.logger.info("🔍 ContextInspector initialized")
    
    def inspect_current_context(self) -> Dict[str, Any]:
        """Inspect the current context with detailed analysis"""
        try:
            self._inspections_performed += 1
            
            if not self.context_manager.current_context:
                return {
                    "status": "no_context",
                    "message": "No active context found",
                    "timestamp": datetime.now().isoformat()
                }
            
            context = self.context_manager.current_context
            
            # Basic context information
            inspection = {
                "basic_info": {
                    "project_id": context.project_id,
                    "session_id": context.session_id,
                    "created": context.timestamp.isoformat(),
                    "size_bytes": context.get_context_size(),
                    "size_mb": round(context.get_context_size() / 1024 / 1024, 2)
                },
                
                "content_summary": context.get_summary(),
                
                "conversation_analysis": self._analyze_conversations(context.conversation_history),
                
                "decision_analysis": self._analyze_decisions(context.decisions_made),
                
                "work_analysis": self._analyze_work_items(context.work_completed),
                
                "discovery_analysis": self._analyze_discoveries(context.system_discoveries),
                
                "spec_analysis": self._analyze_specs(context.spec_states),
                
                "health_check": self._health_check_context(context),
                
                "inspection_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"🔍 Context inspection completed for {context.session_id}")
            
            # Emit inspection observation
            self.emit_observation({
                "type": "context_inspected",
                "session_id": context.session_id,
                "inspection_summary": {
                    "size_mb": inspection["basic_info"]["size_mb"],
                    "conversation_events": len(context.conversation_history),
                    "decisions": len(context.decisions_made),
                    "work_items": len(context.work_completed)
                }
            })
            
            return inspection
            
        except Exception as e:
            self.logger.error(f"💥 Context inspection error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_context_integrity(self) -> Dict[str, Any]:
        """Run comprehensive context validation"""
        try:
            self._validations_run += 1
            
            if not self.context_manager.current_context:
                return {"error": "No active context to validate"}
            
            context = self.context_manager.current_context
            
            # Run validation
            validation_result = self.validator.validate_context_integrity(context)
            
            # Format results for developer consumption
            validation_report = {
                "overall_status": "valid" if validation_result.is_valid else "invalid",
                "validation_timestamp": datetime.now().isoformat(),
                
                "errors": [
                    {
                        "severity": error.severity.value,
                        "code": error.code,
                        "message": error.message,
                        "details": error.details,
                        "suggested_fix": error.suggested_fix
                    }
                    for error in validation_result.errors
                ],
                
                "warnings": [
                    {
                        "severity": warning.severity.value,
                        "code": warning.code,
                        "message": warning.message,
                        "details": warning.details,
                        "suggested_fix": warning.suggested_fix
                    }
                    for warning in validation_result.warnings
                ],
                
                "info": [
                    {
                        "severity": info.severity.value,
                        "code": info.code,
                        "message": info.message,
                        "details": info.details
                    }
                    for info in validation_result.info
                ],
                
                "summary": {
                    "total_issues": len(validation_result.errors) + len(validation_result.warnings),
                    "critical_issues": len(validation_result.errors),
                    "warnings": len(validation_result.warnings),
                    "info_items": len(validation_result.info)
                }
            }
            
            self.logger.info(f"✅ Context validation completed: {validation_report['summary']}")
            
            return validation_report
            
        except Exception as e:
            self.logger.error(f"💥 Context validation error: {e}")
            return {"error": str(e)}
    
    def export_context(self, export_path: Optional[str] = None, 
                      include_sensitive: bool = False) -> Dict[str, Any]:
        """Export context to file for backup or sharing"""
        try:
            self._exports_created += 1
            
            if not self.context_manager.current_context:
                return {"error": "No active context to export"}
            
            context = self.context_manager.current_context
            
            # Generate export filename if not provided
            if not export_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = f".kiro/context/exports/context_{context.project_id}_{timestamp}.json"
            
            # Prepare export data
            export_data = {
                "export_metadata": {
                    "export_timestamp": datetime.now().isoformat(),
                    "context_version": "1.0",
                    "exported_by": "context_inspector",
                    "include_sensitive": include_sensitive
                },
                "context_data": context.to_dict()
            }
            
            # Filter sensitive data if requested
            if not include_sensitive:
                export_data["context_data"] = self._filter_sensitive_export_data(export_data["context_data"])
            
            # Ensure export directory exists
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write export file
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            export_result = {
                "success": True,
                "export_path": str(export_path),
                "export_size_bytes": export_file.stat().st_size,
                "export_timestamp": datetime.now().isoformat(),
                "context_summary": context.get_summary()
            }
            
            self.logger.info(f"📤 Context exported to {export_path}")
            
            # Emit export observation
            self.emit_observation({
                "type": "context_exported",
                "export_path": export_path,
                "export_size_bytes": export_result["export_size_bytes"],
                "session_id": context.session_id
            })
            
            return export_result
            
        except Exception as e:
            self.logger.error(f"💥 Context export error: {e}")
            return {"error": str(e)}
    
    def import_context(self, import_path: str, replace_current: bool = False) -> Dict[str, Any]:
        """Import context from file"""
        try:
            self._imports_processed += 1
            
            import_file = Path(import_path)
            if not import_file.exists():
                return {"error": f"Import file not found: {import_path}"}
            
            # Read import file
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate import format
            if "context_data" not in import_data:
                return {"error": "Invalid import file format"}
            
            # Create context from imported data
            imported_context = SessionContext.from_dict(import_data["context_data"])
            
            # Validate imported context
            validation_result = self.validator.validate_context_integrity(imported_context)
            
            if not validation_result.is_valid:
                return {
                    "error": "Imported context failed validation",
                    "validation_errors": [error.message for error in validation_result.errors]
                }
            
            # Store imported context
            if replace_current:
                # Replace current context
                self.context_manager.current_context = imported_context
                self.registry.store_context(imported_context)
            else:
                # Store as new context with new session ID
                imported_context.session_id = str(uuid.uuid4())
                self.registry.store_context(imported_context)
            
            import_result = {
                "success": True,
                "import_path": import_path,
                "imported_session_id": imported_context.session_id,
                "replaced_current": replace_current,
                "import_timestamp": datetime.now().isoformat(),
                "context_summary": imported_context.get_summary()
            }
            
            self.logger.info(f"📥 Context imported from {import_path}")
            
            # Emit import observation
            self.emit_observation({
                "type": "context_imported",
                "import_path": import_path,
                "session_id": imported_context.session_id,
                "replaced_current": replace_current
            })
            
            return import_result
            
        except Exception as e:
            self.logger.error(f"💥 Context import error: {e}")
            return {"error": str(e)}
    
    def clear_context_with_confirmation(self, confirmation_code: str) -> Dict[str, Any]:
        """Clear current context with confirmation"""
        try:
            expected_code = "CLEAR_CONTEXT_CONFIRMED"
            
            if confirmation_code != expected_code:
                return {
                    "error": f"Invalid confirmation code. Expected: {expected_code}",
                    "provided": confirmation_code
                }
            
            if not self.context_manager.current_context:
                return {"message": "No active context to clear"}
            
            old_session_id = self.context_manager.current_context.session_id
            
            # Clear the context
            success = self.context_manager.clear_context("CONFIRM_CLEAR_CONTEXT")
            
            if success:
                result = {
                    "success": True,
                    "cleared_session_id": old_session_id,
                    "new_session_id": self.context_manager.current_session_id,
                    "clear_timestamp": datetime.now().isoformat()
                }
                
                self.logger.info(f"🧹 Context cleared: {old_session_id}")
                
                # Emit clear observation
                self.emit_observation({
                    "type": "context_cleared",
                    "old_session_id": old_session_id,
                    "new_session_id": self.context_manager.current_session_id
                })
                
                return result
            else:
                return {"error": "Failed to clear context"}
                
        except Exception as e:
            self.logger.error(f"💥 Context clear error: {e}")
            return {"error": str(e)}
    
    def get_context_history(self, project_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get context history for project"""
        try:
            if not project_id:
                project_id = self.context_manager.current_project_id
            
            sessions = self.registry.list_project_sessions(project_id)
            
            # Limit results
            sessions = sessions[:limit]
            
            history = {
                "project_id": project_id,
                "total_sessions": len(sessions),
                "sessions": sessions,
                "query_timestamp": datetime.now().isoformat()
            }
            
            return history
            
        except Exception as e:
            self.logger.error(f"💥 Context history error: {e}")
            return {"error": str(e)}
    
    def _analyze_conversations(self, conversations: List) -> Dict[str, Any]:
        """Analyze conversation history"""
        if not conversations:
            return {"total": 0, "analysis": "No conversations found"}
        
        # Event type distribution
        event_types = {}
        for conv in conversations:
            event_type = conv.event_type
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Time analysis
        first_event = min(conversations, key=lambda x: x.timestamp)
        last_event = max(conversations, key=lambda x: x.timestamp)
        duration = last_event.timestamp - first_event.timestamp
        
        return {
            "total": len(conversations),
            "event_types": event_types,
            "duration_minutes": duration.total_seconds() / 60,
            "first_event": first_event.timestamp.isoformat(),
            "last_event": last_event.timestamp.isoformat(),
            "average_events_per_hour": len(conversations) / max(1, duration.total_seconds() / 3600)
        }
    
    def _analyze_decisions(self, decisions: List) -> Dict[str, Any]:
        """Analyze decisions made"""
        if not decisions:
            return {"total": 0, "analysis": "No decisions found"}
        
        # Decision analysis
        with_rationale = sum(1 for d in decisions if d.rationale)
        with_alternatives = sum(1 for d in decisions if d.alternatives_considered)
        with_outcomes = sum(1 for d in decisions if d.outcome)
        
        return {
            "total": len(decisions),
            "with_rationale": with_rationale,
            "with_alternatives": with_alternatives,
            "with_outcomes": with_outcomes,
            "completeness_score": (with_rationale + with_alternatives + with_outcomes) / (len(decisions) * 3)
        }
    
    def _analyze_work_items(self, work_items: List) -> Dict[str, Any]:
        """Analyze work completed"""
        if not work_items:
            return {"total": 0, "analysis": "No work items found"}
        
        # Work type distribution
        work_types = {}
        total_files = 0
        
        for work in work_items:
            work_type = work.work_type
            work_types[work_type] = work_types.get(work_type, 0) + 1
            total_files += len(work.files_created) + len(work.files_modified)
        
        return {
            "total": len(work_items),
            "work_types": work_types,
            "total_files_affected": total_files,
            "average_files_per_work_item": total_files / len(work_items)
        }
    
    def _analyze_discoveries(self, discoveries: List) -> Dict[str, Any]:
        """Analyze system discoveries"""
        if not discoveries:
            return {"total": 0, "analysis": "No discoveries found"}
        
        # Discovery type distribution
        discovery_types = {}
        total_components = 0
        
        for discovery in discoveries:
            discovery_type = discovery.discovery_type
            discovery_types[discovery_type] = discovery_types.get(discovery_type, 0) + 1
            total_components += len(discovery.components_found)
        
        return {
            "total": len(discoveries),
            "discovery_types": discovery_types,
            "total_components_found": total_components,
            "average_components_per_discovery": total_components / len(discoveries)
        }
    
    def _analyze_specs(self, spec_states: Dict) -> Dict[str, Any]:
        """Analyze specification states"""
        if not spec_states:
            return {"total": 0, "analysis": "No specs found"}
        
        total_completion = sum(spec.completion_percentage for spec in spec_states.values())
        average_completion = total_completion / len(spec_states)
        
        return {
            "total": len(spec_states),
            "average_completion": average_completion,
            "completed_specs": sum(1 for spec in spec_states.values() if spec.completion_percentage >= 100),
            "in_progress_specs": sum(1 for spec in spec_states.values() if 0 < spec.completion_percentage < 100)
        }
    
    def _health_check_context(self, context: SessionContext) -> Dict[str, Any]:
        """Perform health check on context"""
        health = {
            "status": "healthy",
            "issues": []
        }
        
        # Size check
        size_mb = context.get_context_size() / 1024 / 1024
        if size_mb > 100:
            health["issues"].append(f"Large context size: {size_mb:.1f}MB")
        
        # Age check
        age_days = (datetime.now() - context.timestamp).days
        if age_days > 30:
            health["issues"].append(f"Old context: {age_days} days old")
        
        # Content checks
        if len(context.conversation_history) > 1000:
            health["issues"].append(f"Many conversation events: {len(context.conversation_history)}")
        
        if health["issues"]:
            health["status"] = "warning"
        
        return health
    
    def _filter_sensitive_export_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive data from export"""
        # This would integrate with the security module
        # For now, just return the data as-is
        return data
    
    def get_inspector_stats(self) -> Dict[str, Any]:
        """Get inspector statistics"""
        return {
            "inspections_performed": self._inspections_performed,
            "exports_created": self._exports_created,
            "imports_processed": self._imports_processed,
            "validations_run": self._validations_run
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ContextInspector"""
        return {
            "status": "healthy",
            "inspector_stats": self.get_inspector_stats(),
            "context_manager_available": self.context_manager is not None
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        return {
            "context_inspector_inspections_total": self._inspections_performed,
            "context_inspector_exports_total": self._exports_created,
            "context_inspector_imports_total": self._imports_processed,
            "context_inspector_validations_total": self._validations_run
        }


class ContextDebugger(BeastlyModule):
    """Advanced debugging tools for context system"""
    
    def __init__(self, context_manager: ContextManager):
        super().__init__()
        
        self.context_manager = context_manager
        self._debug_sessions = {}
        
        self.logger.info("🐛 ContextDebugger initialized")
    
    def start_debug_session(self, session_name: str) -> str:
        """Start a debugging session"""
        debug_id = str(uuid.uuid4())
        
        self._debug_sessions[debug_id] = {
            "name": session_name,
            "start_time": datetime.now(),
            "events": [],
            "snapshots": []
        }
        
        self.logger.info(f"🐛 Debug session started: {session_name}")
        return debug_id
    
    def capture_context_snapshot(self, debug_id: str, label: str) -> bool:
        """Capture context snapshot for debugging"""
        try:
            if debug_id not in self._debug_sessions:
                return False
            
            if self.context_manager.current_context:
                snapshot = {
                    "label": label,
                    "timestamp": datetime.now(),
                    "context_summary": self.context_manager.current_context.get_summary(),
                    "context_size": self.context_manager.current_context.get_context_size()
                }
                
                self._debug_sessions[debug_id]["snapshots"].append(snapshot)
                self.logger.debug(f"📸 Context snapshot captured: {label}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"💥 Snapshot capture error: {e}")
            return False
    
    def get_debug_report(self, debug_id: str) -> Dict[str, Any]:
        """Get debugging report"""
        if debug_id not in self._debug_sessions:
            return {"error": "Debug session not found"}
        
        session = self._debug_sessions[debug_id]
        
        return {
            "session_name": session["name"],
            "start_time": session["start_time"].isoformat(),
            "duration_minutes": (datetime.now() - session["start_time"]).total_seconds() / 60,
            "snapshots": session["snapshots"],
            "events": session["events"]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ContextDebugger"""
        return {
            "status": "healthy",
            "active_debug_sessions": len(self._debug_sessions)
        }