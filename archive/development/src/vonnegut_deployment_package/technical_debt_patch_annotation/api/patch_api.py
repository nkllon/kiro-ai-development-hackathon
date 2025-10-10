"""
Technical Debt Patch Annotation REST API

This module provides a comprehensive REST API for external integration with the
Technical Debt Patch Annotation System. It implements CRUD operations for patches,
webhook support for external notifications, and comprehensive API documentation.

Requirements Addressed:
- 6.1: Integration with development workflow
- 6.2: Code review and CI/CD integration
- 6.4: Cleanup task validation
- 6.5: Technical debt reporting
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, validator
import uvicorn

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability, ModuleHealth
from src.technical_debt_patch_annotation.core.models import (
    PatchAnnotation, DebtLevel, BypassType, ValidationResult, ExtractionResult,
    AnnotationParser, validate_patch_annotation
)


# Pydantic models for API requests/responses
class PatchCreateRequest(BaseModel):
    """Request model for creating a new patch annotation."""
    reason: str = Field(..., description="Why this patch was needed")
    upstream_issue: str = Field(..., description="Reference to root cause issue")
    cleanup_task: str = Field(..., description="Specific remediation guidance")
    debt_level: str = Field(..., description="Technical debt severity level")
    bypass_type: str = Field(..., description="Type of architectural bypass")
    component: str = Field(..., description="Affected system component")
    file_path: str = Field(..., description="Source file location")
    line_start: int = Field(..., description="Starting line number")
    line_end: int = Field(..., description="Ending line number")
    expected_resolution: Optional[str] = Field(None, description="Expected resolution date (ISO format)")
    validation_criteria: List[str] = Field(default_factory=list, description="How to verify cleanup success")
    created_by: str = Field("", description="Developer who created the patch")
    assigned_to: str = Field("", description="Developer responsible for cleanup")
    tags: List[str] = Field(default_factory=list, description="Additional classification tags")

    @validator('debt_level')
    def validate_debt_level(cls, v):
        try:
            DebtLevel(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid debt level: {v}. Must be one of: {[dl.value for dl in DebtLevel]}")

    @validator('bypass_type')
    def validate_bypass_type(cls, v):
        try:
            BypassType(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid bypass type: {v}. Must be one of: {[bt.value for bt in BypassType]}")


class PatchUpdateRequest(BaseModel):
    """Request model for updating an existing patch annotation."""
    reason: Optional[str] = Field(None, description="Why this patch was needed")
    upstream_issue: Optional[str] = Field(None, description="Reference to root cause issue")
    cleanup_task: Optional[str] = Field(None, description="Specific remediation guidance")
    debt_level: Optional[str] = Field(None, description="Technical debt severity level")
    bypass_type: Optional[str] = Field(None, description="Type of architectural bypass")
    component: Optional[str] = Field(None, description="Affected system component")
    expected_resolution: Optional[str] = Field(None, description="Expected resolution date (ISO format)")
    validation_criteria: Optional[List[str]] = Field(None, description="How to verify cleanup success")
    assigned_to: Optional[str] = Field(None, description="Developer responsible for cleanup")
    tags: Optional[List[str]] = Field(None, description="Additional classification tags")

    @validator('debt_level')
    def validate_debt_level(cls, v):
        if v is not None:
            try:
                DebtLevel(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid debt level: {v}. Must be one of: {[dl.value for dl in DebtLevel]}")
        return v

    @validator('bypass_type')
    def validate_bypass_type(cls, v):
        if v is not None:
            try:
                BypassType(v)
                return v
            except ValueError:
                raise ValueError(f"Invalid bypass type: {v}. Must be one of: {[bt.value for bt in BypassType]}")
        return v


class PatchResponse(BaseModel):
    """Response model for patch annotation data."""
    patch_id: str
    reason: str
    upstream_issue: str
    cleanup_task: str
    debt_level: str
    bypass_type: str
    created_date: str
    expected_resolution: Optional[str]
    component: str
    file_path: str
    line_start: int
    line_end: int
    validation_criteria: List[str]
    created_by: str
    assigned_to: str
    tags: List[str]


class WebhookRequest(BaseModel):
    """Request model for webhook registration."""
    url: str = Field(..., description="Webhook endpoint URL")
    events: List[str] = Field(..., description="List of events to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for webhook signature verification")
    active: bool = Field(True, description="Whether webhook is active")


class WebhookResponse(BaseModel):
    """Response model for webhook data."""
    webhook_id: str
    url: str
    events: List[str]
    active: bool
    created_at: str
    last_triggered: Optional[str]


class PatchScanRequest(BaseModel):
    """Request model for patch scanning operations."""
    file_paths: List[str] = Field(..., description="List of file paths to scan")
    include_patterns: List[str] = Field(default_factory=list, description="File patterns to include")
    exclude_patterns: List[str] = Field(default_factory=list, description="File patterns to exclude")


class PatchReportRequest(BaseModel):
    """Request model for patch reporting."""
    component_filter: Optional[str] = Field(None, description="Filter by component")
    debt_level_filter: Optional[str] = Field(None, description="Filter by debt level")
    date_from: Optional[str] = Field(None, description="Start date for filtering (ISO format)")
    date_to: Optional[str] = Field(None, description="End date for filtering (ISO format)")
    include_resolved: bool = Field(False, description="Include resolved patches")


class TechnicalDebtPatchAPI(ReflectiveModule):
    """
    REST API for Technical Debt Patch Annotation System.
    
    Provides comprehensive API endpoints for patch CRUD operations,
    webhook support, and external system integration.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        super().__init__()
        self.module_id = "technical_debt_patch_api"
        self.host = host
        self.port = port
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Technical Debt Patch Annotation API",
            description="REST API for managing technical debt patches and annotations",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # In-memory storage (replace with persistent storage in production)
        self.patches: Dict[str, PatchAnnotation] = {}
        self.webhooks: Dict[str, Dict[str, Any]] = {}
        
        # Setup routes
        self._setup_routes()
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Technical Debt Patch API",
            "version": "1.0.0",
            "description": "REST API for technical debt patch management",
            "host": self.host,
            "port": self.port,
            "endpoints": len(self.app.routes),
            "patches_count": len(self.patches),
            "webhooks_count": len(self.webhooks)
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        try:
            # Check if API is responsive
            status = ModuleStatus.HEALTHY
            issues = []
            health_score = 1.0
            
            # Check patch storage
            if len(self.patches) > 10000:  # Arbitrary threshold
                issues.append("High number of patches in memory storage")
                health_score -= 0.1
            
            # Check webhook health
            inactive_webhooks = sum(1 for w in self.webhooks.values() if not w.get('active', True))
            if inactive_webhooks > 0:
                issues.append(f"{inactive_webhooks} inactive webhooks")
                health_score -= 0.05 * inactive_webhooks
            
            if health_score < 0.8:
                status = ModuleStatus.WARNING
            elif health_score < 0.5:
                status = ModuleStatus.ERROR
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                health_score=max(0.0, health_score),
                issues=issues,
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
                error_count=self._error_count,
                warning_count=self._warning_count
            )
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.ERROR,
                health_score=0.0,
                issues=[f"Health check failed: {str(e)}"],
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
                error_count=self._error_count + 1,
                warning_count=self._warning_count
            )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        try:
            # In degraded mode, disable webhooks but keep core API functionality
            degraded_capabilities = []
            remaining_capabilities = [
                ModuleCapability.API_INTEGRATION,
                ModuleCapability.DATA_PROCESSING,
                ModuleCapability.VALIDATION
            ]
            
            # Disable webhook functionality in degraded mode
            if len(self.webhooks) > 0:
                degraded_capabilities.append(ModuleCapability.MONITORING)
                self.logger.warning("Webhook functionality disabled in degraded mode")
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e)
            )

    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        # Health and documentation endpoints
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            health = self.get_health_status()
            return {
                "status": health.status.value,
                "health_score": health.health_score,
                "issues": health.issues,
                "timestamp": health.last_check.isoformat(),
                "uptime_seconds": health.uptime_seconds
            }

        @self.app.get("/ready")
        async def readiness_check():
            """Readiness check endpoint."""
            return {
                "ready": True,
                "timestamp": datetime.now().isoformat(),
                "patches_loaded": len(self.patches),
                "webhooks_configured": len(self.webhooks)
            }

        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint."""
            metrics_data = self.get_performance_metrics()
            return {
                "module_metrics": metrics_data,
                "api_metrics": {
                    "total_patches": len(self.patches),
                    "total_webhooks": len(self.webhooks),
                    "active_webhooks": sum(1 for w in self.webhooks.values() if w.get('active', True))
                }
            }

        # Patch CRUD operations
        @self.app.post("/api/v1/patches", response_model=PatchResponse)
        async def create_patch(patch_request: PatchCreateRequest):
            """Create a new patch annotation."""
            try:
                with self.trace_operation("create_patch", **patch_request.dict()) as trace:
                    # Create patch annotation
                    patch_data = patch_request.dict()
                    
                    # Convert string dates to datetime objects
                    if patch_data.get('expected_resolution'):
                        patch_data['expected_resolution'] = datetime.fromisoformat(patch_data['expected_resolution'])
                    
                    # Convert string enums to enum objects
                    patch_data['debt_level'] = DebtLevel(patch_data['debt_level'])
                    patch_data['bypass_type'] = BypassType(patch_data['bypass_type'])
                    
                    patch = PatchAnnotation(**patch_data)
                    
                    # Validate patch
                    validation_result = patch.validate()
                    if not validation_result.is_valid:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "message": "Patch validation failed",
                                "errors": validation_result.errors,
                                "warnings": validation_result.warnings
                            }
                        )
                    
                    # Store patch
                    self.patches[patch.patch_id] = patch
                    
                    # Trigger webhooks
                    await self._trigger_webhooks("patch.created", {"patch": asdict(patch)})
                    
                    # Convert to response format
                    response_data = asdict(patch)
                    response_data['debt_level'] = patch.debt_level.value
                    response_data['bypass_type'] = patch.bypass_type.value
                    response_data['created_date'] = patch.created_date.isoformat()
                    if patch.expected_resolution:
                        response_data['expected_resolution'] = patch.expected_resolution.isoformat()
                    
                    trace.output_result = {"patch_id": patch.patch_id}
                    return PatchResponse(**response_data)
                    
            except HTTPException:
                raise
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to create patch: {str(e)}")

        @self.app.get("/api/v1/patches/{patch_id}", response_model=PatchResponse)
        async def get_patch(patch_id: str):
            """Get a specific patch annotation by ID."""
            try:
                with self.trace_operation("get_patch", patch_id=patch_id) as trace:
                    if patch_id not in self.patches:
                        raise HTTPException(status_code=404, detail=f"Patch {patch_id} not found")
                    
                    patch = self.patches[patch_id]
                    
                    # Convert to response format
                    response_data = asdict(patch)
                    response_data['debt_level'] = patch.debt_level.value
                    response_data['bypass_type'] = patch.bypass_type.value
                    response_data['created_date'] = patch.created_date.isoformat()
                    if patch.expected_resolution:
                        response_data['expected_resolution'] = patch.expected_resolution.isoformat()
                    
                    trace.output_result = {"patch_id": patch_id}
                    return PatchResponse(**response_data)
                    
            except HTTPException:
                raise
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to get patch: {str(e)}")

        @self.app.put("/api/v1/patches/{patch_id}", response_model=PatchResponse)
        async def update_patch(patch_id: str, patch_request: PatchUpdateRequest):
            """Update an existing patch annotation."""
            try:
                with self.trace_operation("update_patch", patch_id=patch_id, **patch_request.dict()) as trace:
                    if patch_id not in self.patches:
                        raise HTTPException(status_code=404, detail=f"Patch {patch_id} not found")
                    
                    patch = self.patches[patch_id]
                    
                    # Update fields that are provided
                    update_data = patch_request.dict(exclude_unset=True)
                    for field, value in update_data.items():
                        if value is not None:
                            if field == 'expected_resolution':
                                value = datetime.fromisoformat(value)
                            elif field == 'debt_level':
                                value = DebtLevel(value)
                            elif field == 'bypass_type':
                                value = BypassType(value)
                            
                            setattr(patch, field, value)
                    
                    # Validate updated patch
                    validation_result = patch.validate()
                    if not validation_result.is_valid:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "message": "Patch validation failed",
                                "errors": validation_result.errors,
                                "warnings": validation_result.warnings
                            }
                        )
                    
                    # Trigger webhooks
                    await self._trigger_webhooks("patch.updated", {"patch": asdict(patch)})
                    
                    # Convert to response format
                    response_data = asdict(patch)
                    response_data['debt_level'] = patch.debt_level.value
                    response_data['bypass_type'] = patch.bypass_type.value
                    response_data['created_date'] = patch.created_date.isoformat()
                    if patch.expected_resolution:
                        response_data['expected_resolution'] = patch.expected_resolution.isoformat()
                    
                    trace.output_result = {"patch_id": patch_id}
                    return PatchResponse(**response_data)
                    
            except HTTPException:
                raise
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to update patch: {str(e)}")

        @self.app.delete("/api/v1/patches/{patch_id}")
        async def delete_patch(patch_id: str):
            """Delete a patch annotation."""
            try:
                with self.trace_operation("delete_patch", patch_id=patch_id) as trace:
                    if patch_id not in self.patches:
                        raise HTTPException(status_code=404, detail=f"Patch {patch_id} not found")
                    
                    patch = self.patches[patch_id]
                    del self.patches[patch_id]
                    
                    # Trigger webhooks
                    await self._trigger_webhooks("patch.deleted", {"patch_id": patch_id, "patch": asdict(patch)})
                    
                    trace.output_result = {"deleted": True}
                    return {"message": f"Patch {patch_id} deleted successfully"}
                    
            except HTTPException:
                raise
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to delete patch: {str(e)}")

        @self.app.get("/api/v1/patches")
        async def list_patches(
            component: Optional[str] = None,
            debt_level: Optional[str] = None,
            bypass_type: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
        ):
            """List patch annotations with optional filtering."""
            try:
                with self.trace_operation("list_patches", component=component, debt_level=debt_level, 
                                        bypass_type=bypass_type, limit=limit, offset=offset) as trace:
                    patches = list(self.patches.values())
                    
                    # Apply filters
                    if component:
                        patches = [p for p in patches if p.component == component]
                    if debt_level:
                        patches = [p for p in patches if p.debt_level.value == debt_level]
                    if bypass_type:
                        patches = [p for p in patches if p.bypass_type.value == bypass_type]
                    
                    # Apply pagination
                    total = len(patches)
                    patches = patches[offset:offset + limit]
                    
                    # Convert to response format
                    response_patches = []
                    for patch in patches:
                        response_data = asdict(patch)
                        response_data['debt_level'] = patch.debt_level.value
                        response_data['bypass_type'] = patch.bypass_type.value
                        response_data['created_date'] = patch.created_date.isoformat()
                        if patch.expected_resolution:
                            response_data['expected_resolution'] = patch.expected_resolution.isoformat()
                        response_patches.append(response_data)
                    
                    result = {
                        "patches": response_patches,
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                        "has_more": offset + limit < total
                    }
                    
                    trace.output_result = {"count": len(response_patches), "total": total}
                    return result
                    
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to list patches: {str(e)}")

        # Patch scanning endpoints
        @self.app.post("/api/v1/patches/scan")
        async def scan_patches(scan_request: PatchScanRequest):
            """Scan files for patch annotations."""
            try:
                with self.trace_operation("scan_patches", **scan_request.dict()) as trace:
                    results = []
                    total_patches = 0
                    total_errors = 0
                    
                    for file_path in scan_request.file_paths:
                        try:
                            if not Path(file_path).exists():
                                results.append({
                                    "file_path": file_path,
                                    "error": "File not found",
                                    "patches": [],
                                    "patch_count": 0
                                })
                                total_errors += 1
                                continue
                            
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            extraction_result = AnnotationParser.extract_annotations(content, file_path)
                            
                            # Store found patches
                            for patch in extraction_result.patches:
                                self.patches[patch.patch_id] = patch
                            
                            results.append({
                                "file_path": file_path,
                                "patches": [asdict(p) for p in extraction_result.patches],
                                "patch_count": len(extraction_result.patches),
                                "errors": extraction_result.errors,
                                "lines_scanned": extraction_result.total_lines_scanned
                            })
                            
                            total_patches += len(extraction_result.patches)
                            total_errors += len(extraction_result.errors)
                            
                        except Exception as e:
                            results.append({
                                "file_path": file_path,
                                "error": str(e),
                                "patches": [],
                                "patch_count": 0
                            })
                            total_errors += 1
                    
                    # Trigger webhooks for discovered patches
                    if total_patches > 0:
                        await self._trigger_webhooks("patches.discovered", {
                            "total_patches": total_patches,
                            "files_scanned": len(scan_request.file_paths)
                        })
                    
                    result = {
                        "scan_results": results,
                        "summary": {
                            "files_scanned": len(scan_request.file_paths),
                            "total_patches_found": total_patches,
                            "total_errors": total_errors
                        }
                    }
                    
                    trace.output_result = {"patches_found": total_patches, "files_scanned": len(scan_request.file_paths)}
                    return result
                    
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to scan patches: {str(e)}")

        # Webhook management endpoints
        @self.app.post("/api/v1/webhooks", response_model=WebhookResponse)
        async def create_webhook(webhook_request: WebhookRequest):
            """Register a new webhook."""
            try:
                with self.trace_operation("create_webhook", **webhook_request.dict()) as trace:
                    import uuid
                    webhook_id = str(uuid.uuid4())
                    
                    webhook_data = {
                        "webhook_id": webhook_id,
                        "url": webhook_request.url,
                        "events": webhook_request.events,
                        "secret": webhook_request.secret,
                        "active": webhook_request.active,
                        "created_at": datetime.now(),
                        "last_triggered": None
                    }
                    
                    self.webhooks[webhook_id] = webhook_data
                    
                    response_data = webhook_data.copy()
                    response_data['created_at'] = webhook_data['created_at'].isoformat()
                    if response_data['last_triggered']:
                        response_data['last_triggered'] = response_data['last_triggered'].isoformat()
                    
                    trace.output_result = {"webhook_id": webhook_id}
                    return WebhookResponse(**response_data)
                    
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to create webhook: {str(e)}")

        @self.app.get("/api/v1/webhooks")
        async def list_webhooks():
            """List all registered webhooks."""
            try:
                with self.trace_operation("list_webhooks") as trace:
                    webhooks = []
                    for webhook_data in self.webhooks.values():
                        response_data = webhook_data.copy()
                        response_data['created_at'] = webhook_data['created_at'].isoformat()
                        if response_data['last_triggered']:
                            response_data['last_triggered'] = response_data['last_triggered'].isoformat()
                        webhooks.append(response_data)
                    
                    trace.output_result = {"count": len(webhooks)}
                    return {"webhooks": webhooks}
                    
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to list webhooks: {str(e)}")

        @self.app.delete("/api/v1/webhooks/{webhook_id}")
        async def delete_webhook(webhook_id: str):
            """Delete a webhook."""
            try:
                with self.trace_operation("delete_webhook", webhook_id=webhook_id) as trace:
                    if webhook_id not in self.webhooks:
                        raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")
                    
                    del self.webhooks[webhook_id]
                    
                    trace.output_result = {"deleted": True}
                    return {"message": f"Webhook {webhook_id} deleted successfully"}
                    
            except HTTPException:
                raise
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to delete webhook: {str(e)}")

        # Reporting endpoints
        @self.app.post("/api/v1/reports/patches")
        async def generate_patch_report(report_request: PatchReportRequest):
            """Generate a comprehensive patch report."""
            try:
                with self.trace_operation("generate_patch_report", **report_request.dict()) as trace:
                    patches = list(self.patches.values())
                    
                    # Apply filters
                    if report_request.component_filter:
                        patches = [p for p in patches if p.component == report_request.component_filter]
                    
                    if report_request.debt_level_filter:
                        patches = [p for p in patches if p.debt_level.value == report_request.debt_level_filter]
                    
                    if report_request.date_from:
                        date_from = datetime.fromisoformat(report_request.date_from)
                        patches = [p for p in patches if p.created_date >= date_from]
                    
                    if report_request.date_to:
                        date_to = datetime.fromisoformat(report_request.date_to)
                        patches = [p for p in patches if p.created_date <= date_to]
                    
                    # Generate report statistics
                    debt_level_counts = {}
                    bypass_type_counts = {}
                    component_counts = {}
                    
                    for patch in patches:
                        # Count by debt level
                        debt_level = patch.debt_level.value
                        debt_level_counts[debt_level] = debt_level_counts.get(debt_level, 0) + 1
                        
                        # Count by bypass type
                        bypass_type = patch.bypass_type.value
                        bypass_type_counts[bypass_type] = bypass_type_counts.get(bypass_type, 0) + 1
                        
                        # Count by component
                        component = patch.component
                        component_counts[component] = component_counts.get(component, 0) + 1
                    
                    # Calculate overdue patches
                    now = datetime.now()
                    overdue_patches = [
                        p for p in patches 
                        if p.expected_resolution and p.expected_resolution < now
                    ]
                    
                    report = {
                        "report_generated_at": now.isoformat(),
                        "filters_applied": report_request.dict(),
                        "summary": {
                            "total_patches": len(patches),
                            "overdue_patches": len(overdue_patches),
                            "debt_level_distribution": debt_level_counts,
                            "bypass_type_distribution": bypass_type_counts,
                            "component_distribution": component_counts
                        },
                        "overdue_patches": [
                            {
                                "patch_id": p.patch_id,
                                "component": p.component,
                                "debt_level": p.debt_level.value,
                                "expected_resolution": p.expected_resolution.isoformat(),
                                "days_overdue": (now - p.expected_resolution).days
                            }
                            for p in overdue_patches
                        ]
                    }
                    
                    trace.output_result = {"total_patches": len(patches), "overdue_patches": len(overdue_patches)}
                    return report
                    
            except Exception as e:
                self._increment_error_count()
                raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

    async def _trigger_webhooks(self, event_type: str, payload: Dict[str, Any]):
        """Trigger registered webhooks for an event."""
        try:
            import aiohttp
            import hashlib
            import hmac
            
            for webhook_id, webhook_data in self.webhooks.items():
                if not webhook_data.get('active', True):
                    continue
                
                if event_type not in webhook_data.get('events', []):
                    continue
                
                try:
                    webhook_payload = {
                        "event": event_type,
                        "timestamp": datetime.now().isoformat(),
                        "webhook_id": webhook_id,
                        "data": payload
                    }
                    
                    headers = {
                        "Content-Type": "application/json",
                        "User-Agent": "TechnicalDebtPatchAPI/1.0"
                    }
                    
                    # Add signature if secret is provided
                    if webhook_data.get('secret'):
                        payload_bytes = json.dumps(webhook_payload).encode('utf-8')
                        signature = hmac.new(
                            webhook_data['secret'].encode('utf-8'),
                            payload_bytes,
                            hashlib.sha256
                        ).hexdigest()
                        headers['X-Webhook-Signature'] = f"sha256={signature}"
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            webhook_data['url'],
                            json=webhook_payload,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            if response.status == 200:
                                webhook_data['last_triggered'] = datetime.now()
                                self.logger.info(f"Webhook {webhook_id} triggered successfully")
                            else:
                                self.logger.warning(f"Webhook {webhook_id} returned status {response.status}")
                
                except Exception as e:
                    self.logger.error(f"Failed to trigger webhook {webhook_id}: {e}")
                    
        except ImportError:
            self.logger.warning("aiohttp not available, webhooks disabled")
        except Exception as e:
            self.logger.error(f"Failed to trigger webhooks: {e}")

    def start_server(self):
        """Start the FastAPI server."""
        try:
            self.logger.info(f"Starting Technical Debt Patch API server on {self.host}:{self.port}")
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise

    def stop_server(self):
        """Stop the FastAPI server."""
        # This would be implemented with proper server lifecycle management
        self.logger.info("Server stop requested")


def create_api_instance(host: str = "0.0.0.0", port: int = 8080) -> TechnicalDebtPatchAPI:
    """
    Factory function to create API instance.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        
    Returns:
        TechnicalDebtPatchAPI instance
    """
    return TechnicalDebtPatchAPI(host=host, port=port)


if __name__ == "__main__":
    # CLI entry point
    import argparse
    
    parser = argparse.ArgumentParser(description="Technical Debt Patch Annotation API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start API
    api = create_api_instance(host=args.host, port=args.port)
    api.start_server()