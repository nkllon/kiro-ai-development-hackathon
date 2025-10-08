#!/usr/bin/env python3
"""
Validation Checklist System - Phase 5 Task 5.3

Creates validation checklists for manual verification, automated tests,
accuracy confidence scoring, and change notification systems.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ChecklistItemType(Enum):
    """Types of checklist items."""
    AUTOMATED = "automated"
    MANUAL = "manual"
    HYBRID = "hybrid"


class ChecklistStatus(Enum):
    """Status of checklist items."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChecklistItem:
    """Individual checklist item."""
    item_id: str
    title: str
    description: str
    item_type: ChecklistItemType
    component: str
    priority: int = 1  # 1=high, 2=medium, 3=low
    estimated_time_minutes: int = 5
    automated_test_command: Optional[str] = None
    manual_instructions: Optional[str] = None
    validation_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Status tracking
    status: ChecklistStatus = ChecklistStatus.PENDING
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    confidence_score: float = 0.0


@dataclass
class ValidationChecklist:
    """Complete validation checklist for a component or system."""
    checklist_id: str
    name: str
    description: str
    component: str
    version: str
    created_at: datetime
    items: List[ChecklistItem] = field(default_factory=list)
    
    # Progress tracking
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    overall_confidence: float = 0.0
    estimated_duration_minutes: int = 0
    actual_duration_minutes: Optional[int] = None


@dataclass
class ConfidenceMetric:
    """Confidence scoring metric."""
    metric_id: str
    name: str
    weight: float
    current_value: float
    max_value: float
    description: str
    last_updated: datetime


class ValidationChecklistSystem(ReflectiveModule):
    """
    Validation checklist system that manages automated and manual validation
    procedures with confidence scoring and change notifications.
    """
    
    def __init__(self):
        super().__init__()
        self.checklists: Dict[str, ValidationChecklist] = {}
        self.checklist_templates: Dict[str, Dict[str, Any]] = {}
        self.confidence_metrics: Dict[str, ConfidenceMetric] = {}
        self.stakeholders: Dict[str, Dict[str, Any]] = {}
        self.notification_queue: List[Dict[str, Any]] = []
        
        # Initialize metrics
        self.metrics.update({
            'total_checklists': 0,
            'active_checklists': 0,
            'completed_checklists': 0,
            'overall_system_confidence': 0.0,
            'automated_tests_passed': 0,
            'manual_validations_completed': 0,
            'notifications_sent': 0,
            'average_completion_time_minutes': 0
        })
        
        self.logger.info("ValidationChecklistSystem initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the validation checklist system."""
        correlation_id = self.generate_correlation_id()
        
        try:
            # Load checklist templates
            await self._load_checklist_templates()
            
            # Initialize confidence metrics
            await self._initialize_confidence_metrics()
            
            # Load stakeholder configuration
            await self._load_stakeholder_configuration()
            
            # Start background tasks
            asyncio.create_task(self._confidence_monitoring_loop())
            asyncio.create_task(self._notification_processing_loop())
            
            self.logger.info("ValidationChecklistSystem initialized successfully",
                           extra={"correlation_id": correlation_id})
            
            return {
                "status": "initialized",
                "templates_loaded": len(self.checklist_templates),
                "confidence_metrics": len(self.confidence_metrics),
                "stakeholders": len(self.stakeholders),
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ValidationChecklistSystem: {e}",
                            extra={"correlation_id": correlation_id})
            return {
                "status": "failed",
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _load_checklist_templates(self):
        """Load predefined checklist templates."""
        # Observatory System Validation Template
        observatory_template = {
            "name": "Observatory System Validation",
            "description": "Complete validation checklist for Observatory system components",
            "component": "observatory",
            "items": [
                {
                    "item_id": "obs_websocket_endpoints",
                    "title": "WebSocket Endpoints Validation",
                    "description": "Validate all Observatory WebSocket endpoints are accessible and functional",
                    "item_type": ChecklistItemType.AUTOMATED,
                    "priority": 1,
                    "estimated_time_minutes": 5,
                    "automated_test_command": "python -m pytest tests/test_websocket_endpoints.py -v",
                    "validation_criteria": [
                        "/ws/observatory endpoint accepts connections",
                        "/ws/emoji-rain endpoint accepts connections", 
                        "/ws/anomalies endpoint accepts connections",
                        "/ws/doctor-status endpoint accepts connections",
                        "WebSocket upgrade negotiation successful",
                        "Ping/pong heartbeat functional"
                    ],
                    "tags": ["websocket", "connectivity", "critical"]
                },
                {
                    "item_id": "obs_health_endpoints",
                    "title": "Health Endpoints Validation", 
                    "description": "Validate all health monitoring endpoints return correct status",
                    "item_type": ChecklistItemType.AUTOMATED,
                    "priority": 1,
                    "estimated_time_minutes": 3,
                    "automated_test_command": "curl -s http://localhost:8888/health | jq '.status'",
                    "validation_criteria": [
                        "Observatory /health returns 200 OK",
                        "Health response includes status: healthy",
                        "Response time < 1000ms",
                        "All component health checks pass"
                    ],
                    "tags": ["health", "monitoring", "critical"]
                },
                {
                    "item_id": "obs_emoji_rain_workflow",
                    "title": "Emoji Rain Workflow Validation",
                    "description": "Manually validate emoji rain celebration workflow end-to-end",
                    "item_type": ChecklistItemType.MANUAL,
                    "priority": 2,
                    "estimated_time_minutes": 10,
                    "manual_instructions": """
                    1. Trigger a test achievement in the system
                    2. Verify WebSocket broadcast is sent to /ws/emoji-rain
                    3. Confirm frontend receives and renders celebration
                    4. Check celebration animation completes successfully
                    5. Verify metrics are updated correctly
                    """,
                    "validation_criteria": [
                        "Achievement detection triggers celebration",
                        "WebSocket message broadcast successful",
                        "Frontend animation renders correctly",
                        "Celebration metrics updated",
                        "No errors in browser console"
                    ],
                    "tags": ["emoji-rain", "workflow", "user-experience"]
                },
                {
                    "item_id": "obs_anomaly_detection",
                    "title": "Anomaly Detection Flow Validation",
                    "description": "Validate anomaly detection from Prometheus to WebSocket alerts",
                    "item_type": ChecklistItemType.HYBRID,
                    "priority": 1,
                    "estimated_time_minutes": 15,
                    "automated_test_command": "python scripts/test_anomaly_detection.py",
                    "manual_instructions": """
                    1. Create test anomaly condition in Prometheus metrics
                    2. Verify detection engine identifies anomaly
                    3. Confirm WebSocket alert sent to /ws/anomalies
                    4. Check alert appears in monitoring dashboard
                    """,
                    "validation_criteria": [
                        "Prometheus metrics ingestion working",
                        "Anomaly detection algorithm functional",
                        "WebSocket alert broadcast successful",
                        "Alert correlation ID tracking works",
                        "Dashboard displays alert correctly"
                    ],
                    "tags": ["anomaly-detection", "monitoring", "alerts"]
                }
            ]
        }
        
        # Infrastructure Validation Template
        infrastructure_template = {
            "name": "Infrastructure Validation",
            "description": "Validation checklist for core infrastructure components",
            "component": "infrastructure",
            "items": [
                {
                    "item_id": "infra_redis_coordination",
                    "title": "Redis Coordination Validation",
                    "description": "Validate Redis coordination with failover capability",
                    "item_type": ChecklistItemType.AUTOMATED,
                    "priority": 1,
                    "estimated_time_minutes": 5,
                    "automated_test_command": "python scripts/test_redis_coordination.py",
                    "validation_criteria": [
                        "Primary Redis (192.168.1.119:6379) accessible",
                        "Fallback Redis (localhost:6380) accessible", 
                        "Automatic failover functional",
                        "Data synchronization working",
                        "Connection pooling optimal"
                    ],
                    "tags": ["redis", "coordination", "failover", "critical"]
                },
                {
                    "item_id": "infra_cloudflare_tunnel",
                    "title": "Cloudflare Tunnel Validation",
                    "description": "Validate Cloudflare tunnel connectivity and routing",
                    "item_type": ChecklistItemType.MANUAL,
                    "priority": 1,
                    "estimated_time_minutes": 10,
                    "manual_instructions": """
                    1. Check tunnel status: cloudflared tunnel info
                    2. Verify DNS routing for all subdomains
                    3. Test WebSocket proxy configuration
                    4. Validate SSL/TLS certificate status
                    5. Check tunnel performance metrics
                    """,
                    "validation_criteria": [
                        "Tunnel status shows connected",
                        "All DNS routes functional",
                        "WebSocket upgrade through tunnel works",
                        "SSL certificates valid and current",
                        "Latency within acceptable limits"
                    ],
                    "tags": ["cloudflare", "tunnel", "networking", "ssl"]
                }
            ]
        }
        
        # Documentation Validation Template
        documentation_template = {
            "name": "Documentation Validation",
            "description": "Validation checklist for generated documentation accuracy",
            "component": "documentation",
            "items": [
                {
                    "item_id": "doc_accuracy_check",
                    "title": "Documentation Accuracy Validation",
                    "description": "Validate generated documentation matches actual system behavior",
                    "item_type": ChecklistItemType.HYBRID,
                    "priority": 1,
                    "estimated_time_minutes": 20,
                    "automated_test_command": "python scripts/validate_documentation_accuracy.py",
                    "manual_instructions": """
                    1. Review generated operational workflows
                    2. Compare with actual system behavior
                    3. Verify all endpoints documented correctly
                    4. Check troubleshooting guides accuracy
                    5. Validate security documentation completeness
                    """,
                    "validation_criteria": [
                        "Operational workflows match implementation",
                        "All endpoints documented and accessible",
                        "Troubleshooting guides resolve actual issues",
                        "Security procedures are current and complete",
                        "Documentation freshness < 24 hours"
                    ],
                    "tags": ["documentation", "accuracy", "completeness"]
                }
            ]
        }
        
        self.checklist_templates = {
            "observatory": observatory_template,
            "infrastructure": infrastructure_template,
            "documentation": documentation_template
        }
        
        self.logger.info(f"Loaded {len(self.checklist_templates)} checklist templates")
    
    async def _initialize_confidence_metrics(self):
        """Initialize confidence scoring metrics."""
        confidence_metrics = [
            ConfidenceMetric(
                metric_id="automated_test_coverage",
                name="Automated Test Coverage",
                weight=0.3,
                current_value=0.0,
                max_value=100.0,
                description="Percentage of functionality covered by automated tests",
                last_updated=datetime.utcnow()
            ),
            ConfidenceMetric(
                metric_id="manual_validation_completeness",
                name="Manual Validation Completeness",
                weight=0.2,
                current_value=0.0,
                max_value=100.0,
                description="Percentage of manual validation items completed",
                last_updated=datetime.utcnow()
            ),
            ConfidenceMetric(
                metric_id="documentation_freshness",
                name="Documentation Freshness",
                weight=0.15,
                current_value=0.0,
                max_value=100.0,
                description="How recent the documentation is (100% = updated within 1 hour)",
                last_updated=datetime.utcnow()
            ),
            ConfidenceMetric(
                metric_id="system_health_score",
                name="System Health Score",
                weight=0.2,
                current_value=0.0,
                max_value=100.0,
                description="Overall system health based on monitoring metrics",
                last_updated=datetime.utcnow()
            ),
            ConfidenceMetric(
                metric_id="validation_consistency",
                name="Validation Consistency",
                weight=0.15,
                current_value=0.0,
                max_value=100.0,
                description="Consistency of validation results over time",
                last_updated=datetime.utcnow()
            )
        ]
        
        for metric in confidence_metrics:
            self.confidence_metrics[metric.metric_id] = metric
        
        self.logger.info(f"Initialized {len(self.confidence_metrics)} confidence metrics")
    
    async def _load_stakeholder_configuration(self):
        """Load stakeholder notification configuration."""
        # Default stakeholder configuration
        self.stakeholders = {
            "development_team": {
                "name": "Development Team",
                "notification_methods": ["email", "slack"],
                "interests": ["automated_test_failures", "system_health_alerts", "documentation_updates"],
                "escalation_threshold": 0.8  # Notify if confidence drops below 80%
            },
            "operations_team": {
                "name": "Operations Team", 
                "notification_methods": ["slack", "pagerduty"],
                "interests": ["infrastructure_issues", "performance_alerts", "security_incidents"],
                "escalation_threshold": 0.9  # Notify if confidence drops below 90%
            },
            "quality_assurance": {
                "name": "Quality Assurance",
                "notification_methods": ["email"],
                "interests": ["validation_failures", "accuracy_issues", "manual_validation_required"],
                "escalation_threshold": 0.85  # Notify if confidence drops below 85%
            }
        }
        
        self.logger.info(f"Loaded {len(self.stakeholders)} stakeholder configurations")
    
    async def create_checklist_from_template(self, template_name: str, 
                                           component: str = None) -> str:
        """Create a new checklist from a template."""
        if template_name not in self.checklist_templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.checklist_templates[template_name]
        checklist_id = f"{template_name}_{component or template['component']}_{int(datetime.utcnow().timestamp())}"
        
        # Create checklist items from template
        items = []
        total_time = 0
        
        for item_data in template["items"]:
            item = ChecklistItem(
                item_id=item_data["item_id"],
                title=item_data["title"],
                description=item_data["description"],
                item_type=ChecklistItemType(item_data["item_type"]),
                component=component or template["component"],
                priority=item_data.get("priority", 1),
                estimated_time_minutes=item_data.get("estimated_time_minutes", 5),
                automated_test_command=item_data.get("automated_test_command"),
                manual_instructions=item_data.get("manual_instructions"),
                validation_criteria=item_data.get("validation_criteria", []),
                dependencies=item_data.get("dependencies", []),
                tags=item_data.get("tags", [])
            )
            items.append(item)
            total_time += item.estimated_time_minutes
        
        # Create checklist
        checklist = ValidationChecklist(
            checklist_id=checklist_id,
            name=template["name"],
            description=template["description"],
            component=component or template["component"],
            version="1.0",
            created_at=datetime.utcnow(),
            items=items,
            total_items=len(items),
            estimated_duration_minutes=total_time
        )
        
        self.checklists[checklist_id] = checklist
        self.metrics['total_checklists'] += 1
        self.metrics['active_checklists'] += 1
        
        self.logger.info(f"Created checklist from template: {checklist_id}",
                        extra={"template": template_name, "items": len(items)})
        
        return checklist_id
    
    async def execute_checklist_item(self, checklist_id: str, item_id: str, 
                                   assigned_to: str = None) -> Dict[str, Any]:
        """Execute a specific checklist item."""
        if checklist_id not in self.checklists:
            raise ValueError(f"Checklist '{checklist_id}' not found")
        
        checklist = self.checklists[checklist_id]
        item = next((item for item in checklist.items if item.item_id == item_id), None)
        
        if not item:
            raise ValueError(f"Checklist item '{item_id}' not found")
        
        correlation_id = self.generate_correlation_id()
        
        # Update item status
        item.status = ChecklistStatus.IN_PROGRESS
        item.assigned_to = assigned_to
        item.started_at = datetime.utcnow()
        
        try:
            if item.item_type == ChecklistItemType.AUTOMATED:
                result = await self._execute_automated_item(item, correlation_id)
            elif item.item_type == ChecklistItemType.MANUAL:
                result = await self._prepare_manual_item(item, correlation_id)
            else:  # HYBRID
                result = await self._execute_hybrid_item(item, correlation_id)
            
            # Update item with results
            item.status = ChecklistStatus.COMPLETED if result["success"] else ChecklistStatus.FAILED
            item.completed_at = datetime.utcnow()
            item.result = result
            item.confidence_score = result.get("confidence_score", 0.0)
            
            # Update checklist progress
            await self._update_checklist_progress(checklist_id)
            
            # Update metrics
            if result["success"]:
                if item.item_type == ChecklistItemType.AUTOMATED:
                    self.metrics['automated_tests_passed'] += 1
                else:
                    self.metrics['manual_validations_completed'] += 1
            
            self.logger.info(f"Executed checklist item: {item_id}",
                           extra={
                               "correlation_id": correlation_id,
                               "success": result["success"],
                               "confidence": item.confidence_score
                           })
            
            return {
                "status": "completed",
                "item_id": item_id,
                "success": result["success"],
                "confidence_score": item.confidence_score,
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            item.status = ChecklistStatus.FAILED
            item.completed_at = datetime.utcnow()
            item.result = {"success": False, "error": str(e)}
            
            self.logger.error(f"Failed to execute checklist item {item_id}: {e}",
                            extra={"correlation_id": correlation_id})
            
            return {
                "status": "failed",
                "item_id": item_id,
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _execute_automated_item(self, item: ChecklistItem, 
                                    correlation_id: str) -> Dict[str, Any]:
        """Execute an automated checklist item."""
        if not item.automated_test_command:
            raise ValueError("Automated item missing test command")
        
        import subprocess
        
        try:
            # Execute the automated test command
            result = subprocess.run(
                item.automated_test_command.split(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            confidence_score = 1.0 if success else 0.0
            
            return {
                "success": success,
                "confidence_score": confidence_score,
                "output": result.stdout,
                "error": result.stderr if not success else None,
                "execution_time": "automated",
                "correlation_id": correlation_id
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "confidence_score": 0.0,
                "error": "Test execution timed out",
                "correlation_id": correlation_id
            }
        except Exception as e:
            return {
                "success": False,
                "confidence_score": 0.0,
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _prepare_manual_item(self, item: ChecklistItem, 
                                 correlation_id: str) -> Dict[str, Any]:
        """Prepare a manual checklist item for execution."""
        # For manual items, we prepare the instructions and return pending status
        # The actual execution will be marked complete by human operator
        
        return {
            "success": True,  # Preparation successful
            "confidence_score": 0.5,  # Partial confidence until manual completion
            "instructions": item.manual_instructions,
            "validation_criteria": item.validation_criteria,
            "status": "awaiting_manual_completion",
            "correlation_id": correlation_id
        }
    
    async def _execute_hybrid_item(self, item: ChecklistItem, 
                                 correlation_id: str) -> Dict[str, Any]:
        """Execute a hybrid checklist item (automated + manual)."""
        # First run automated portion
        automated_result = await self._execute_automated_item(item, correlation_id)
        
        # Then prepare manual portion
        manual_result = await self._prepare_manual_item(item, correlation_id)
        
        # Combine results
        combined_confidence = (automated_result["confidence_score"] + 
                             manual_result["confidence_score"]) / 2
        
        return {
            "success": automated_result["success"],
            "confidence_score": combined_confidence,
            "automated_result": automated_result,
            "manual_instructions": manual_result["instructions"],
            "validation_criteria": manual_result["validation_criteria"],
            "correlation_id": correlation_id
        }
    
    async def _update_checklist_progress(self, checklist_id: str):
        """Update checklist progress and confidence scores."""
        checklist = self.checklists[checklist_id]
        
        completed_items = len([item for item in checklist.items 
                             if item.status == ChecklistStatus.COMPLETED])
        failed_items = len([item for item in checklist.items 
                          if item.status == ChecklistStatus.FAILED])
        
        checklist.completed_items = completed_items
        checklist.failed_items = failed_items
        
        # Calculate overall confidence
        if checklist.items:
            total_confidence = sum(item.confidence_score for item in checklist.items)
            checklist.overall_confidence = total_confidence / len(checklist.items)
        
        # Check if checklist is complete
        if completed_items + failed_items == checklist.total_items:
            checklist.actual_duration_minutes = int(
                (datetime.utcnow() - checklist.created_at).total_seconds() / 60
            )
            
            self.metrics['active_checklists'] -= 1
            self.metrics['completed_checklists'] += 1
            
            # Send completion notification
            await self._queue_notification({
                "type": "checklist_completed",
                "checklist_id": checklist_id,
                "confidence": checklist.overall_confidence,
                "completed_items": completed_items,
                "failed_items": failed_items
            })
    
    async def calculate_system_confidence(self) -> float:
        """Calculate overall system confidence score."""
        if not self.confidence_metrics:
            return 0.0
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric in self.confidence_metrics.values():
            normalized_value = metric.current_value / metric.max_value
            weighted_sum += normalized_value * metric.weight
            total_weight += metric.weight
        
        system_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
        self.metrics['overall_system_confidence'] = system_confidence
        
        return system_confidence
    
    async def update_confidence_metric(self, metric_id: str, value: float):
        """Update a specific confidence metric."""
        if metric_id in self.confidence_metrics:
            metric = self.confidence_metrics[metric_id]
            metric.current_value = min(value, metric.max_value)
            metric.last_updated = datetime.utcnow()
            
            # Recalculate system confidence
            system_confidence = await self.calculate_system_confidence()
            
            # Check for confidence threshold alerts
            await self._check_confidence_thresholds(system_confidence)
    
    async def _confidence_monitoring_loop(self):
        """Background loop for monitoring confidence metrics."""
        while True:
            try:
                # Update confidence metrics based on current system state
                await self._update_confidence_metrics()
                
                # Calculate overall system confidence
                system_confidence = await self.calculate_system_confidence()
                
                # Check thresholds and send alerts if needed
                await self._check_confidence_thresholds(system_confidence)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in confidence monitoring loop: {e}")
                await asyncio.sleep(300)
    
    async def _update_confidence_metrics(self):
        """Update confidence metrics based on current system state."""
        # Update automated test coverage
        total_automated = len([item for checklist in self.checklists.values() 
                             for item in checklist.items 
                             if item.item_type == ChecklistItemType.AUTOMATED])
        passed_automated = len([item for checklist in self.checklists.values() 
                              for item in checklist.items 
                              if (item.item_type == ChecklistItemType.AUTOMATED and 
                                  item.status == ChecklistStatus.COMPLETED)])
        
        if total_automated > 0:
            coverage = (passed_automated / total_automated) * 100
            await self.update_confidence_metric("automated_test_coverage", coverage)
        
        # Update manual validation completeness
        total_manual = len([item for checklist in self.checklists.values() 
                          for item in checklist.items 
                          if item.item_type == ChecklistItemType.MANUAL])
        completed_manual = len([item for checklist in self.checklists.values() 
                              for item in checklist.items 
                              if (item.item_type == ChecklistItemType.MANUAL and 
                                  item.status == ChecklistStatus.COMPLETED)])
        
        if total_manual > 0:
            completeness = (completed_manual / total_manual) * 100
            await self.update_confidence_metric("manual_validation_completeness", completeness)
    
    async def _check_confidence_thresholds(self, system_confidence: float):
        """Check confidence thresholds and send alerts to stakeholders."""
        for stakeholder_id, config in self.stakeholders.items():
            threshold = config["escalation_threshold"]
            
            if system_confidence < threshold:
                await self._queue_notification({
                    "type": "confidence_threshold_alert",
                    "stakeholder": stakeholder_id,
                    "current_confidence": system_confidence,
                    "threshold": threshold,
                    "severity": "high" if system_confidence < 0.7 else "medium"
                })
    
    async def _queue_notification(self, notification: Dict[str, Any]):
        """Queue a notification for processing."""
        notification["timestamp"] = datetime.utcnow().isoformat()
        notification["id"] = f"notif_{int(datetime.utcnow().timestamp())}"
        
        self.notification_queue.append(notification)
        
        self.logger.info(f"Queued notification: {notification['type']}",
                        extra={"notification_id": notification["id"]})
    
    async def _notification_processing_loop(self):
        """Background loop for processing notifications."""
        while True:
            try:
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    await self._send_notification(notification)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in notification processing loop: {e}")
                await asyncio.sleep(10)
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send a notification to stakeholders."""
        # This would integrate with actual notification systems
        # For now, we'll log the notification
        
        self.logger.info(f"Sending notification: {notification['type']}",
                        extra={"notification": notification})
        
        self.metrics['notifications_sent'] += 1
    
    async def get_checklist_status(self, checklist_id: str) -> Dict[str, Any]:
        """Get status of a specific checklist."""
        if checklist_id not in self.checklists:
            raise ValueError(f"Checklist '{checklist_id}' not found")
        
        checklist = self.checklists[checklist_id]
        
        return {
            "checklist_id": checklist_id,
            "name": checklist.name,
            "component": checklist.component,
            "total_items": checklist.total_items,
            "completed_items": checklist.completed_items,
            "failed_items": checklist.failed_items,
            "progress_percentage": (checklist.completed_items / checklist.total_items * 100) if checklist.total_items > 0 else 0,
            "overall_confidence": checklist.overall_confidence,
            "estimated_duration_minutes": checklist.estimated_duration_minutes,
            "actual_duration_minutes": checklist.actual_duration_minutes,
            "created_at": checklist.created_at.isoformat(),
            "items": [asdict(item) for item in checklist.items]
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system validation status."""
        system_confidence = await self.calculate_system_confidence()
        
        return {
            "system_confidence": system_confidence,
            "confidence_metrics": {k: asdict(v) for k, v in self.confidence_metrics.items()},
            "active_checklists": self.metrics['active_checklists'],
            "completed_checklists": self.metrics['completed_checklists'],
            "metrics": self.metrics,
            "pending_notifications": len(self.notification_queue),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    async def main():
        system = ValidationChecklistSystem()
        await system.initialize()
        
        # Create a test checklist
        checklist_id = await system.create_checklist_from_template("observatory")
        print(f"Created checklist: {checklist_id}")
        
        # Get status
        status = await system.get_checklist_status(checklist_id)
        print(f"Checklist Status: {json.dumps(status, indent=2, default=str)}")
        
        # Get system status
        system_status = await system.get_system_status()
        print(f"System Status: {json.dumps(system_status, indent=2, default=str)}")
    
    asyncio.run(main())