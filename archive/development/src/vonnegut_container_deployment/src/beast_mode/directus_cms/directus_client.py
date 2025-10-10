"""
DirectusClient - BeastlyModule implementation for Directus CMS integration

This is the missing DirectusClient that all the existing Beast Mode Directus components expect.
Provides enhanced observability through BeastlyModule Layer 3 capabilities.
"""

import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import os

from src.beast_mode.core.beastly_module import BeastlyModule
from src.rm_ddd.core.unified_reflective_module import ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult


class DirectusClient(BeastlyModule):
    """BeastlyModule-compliant Directus client with enhanced observability"""
    
    def __init__(self, base_url: str = "http://localhost:8055", token: Optional[str] = None):
        super().__init__()
        
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        
        # Set up authentication if token provided
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })
        
        # Connection status
        self._connected = False
        self._last_health_check = None
        
        # Metrics
        self._requests_made = 0
        self._requests_failed = 0
        self._collections_accessed = set()
        
        self.emit_observation(
            "DirectusClient initialized",
            "info", 
            context={"base_url": self.base_url, "authenticated": bool(self.token)},
            emoji="🔗"
        )
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with Directus and get access token"""
        with self.trace_operation("directus_authenticate", email=email) as trace:
            try:
                auth_data = {
                    "email": email,
                    "password": password
                }
                
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json=auth_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get('data', {}).get('access_token')
                    
                    if self.token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.token}',
                            'Content-Type': 'application/json'
                        })
                        self._connected = True
                        trace.output_result = {"authenticated": True}
                        
                        self.emit_observation(
                            "Successfully authenticated with Directus",
                            "info",
                            context={"email": email},
                            emoji="✅"
                        )
                        return True
                
                trace.output_result = {"authenticated": False, "status": response.status_code}
                self.emit_observation(
                    "Directus authentication failed",
                    "error",
                    context={"email": email, "status": response.status_code},
                    emoji="❌"
                )
                return False
                
            except Exception as e:
                trace.error_info = {"error": str(e)}
                self.emit_observation(
                    f"Directus authentication error: {str(e)}",
                    "error",
                    context={"email": email},
                    emoji="💥"
                )
                return False
    
    def health_check(self) -> bool:
        """Check if Directus is healthy and accessible"""
        with self.trace_operation("directus_health_check") as trace:
            try:
                response = self.session.get(
                    f"{self.base_url}/server/health",
                    timeout=5
                )
                
                self._requests_made += 1
                
                if response.status_code == 200:
                    health_data = response.json()
                    is_healthy = health_data.get('status') == 'ok'
                    self._last_health_check = datetime.now()
                    self._connected = is_healthy
                    
                    trace.output_result = {"healthy": is_healthy, "status": health_data.get('status')}
                    return is_healthy
                else:
                    self._requests_failed += 1
                    self._connected = False
                    trace.output_result = {"healthy": False, "status_code": response.status_code}
                    return False
                    
            except Exception as e:
                self._requests_failed += 1
                self._connected = False
                trace.error_info = {"error": str(e)}
                return False
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """Get all collections from Directus"""
        with self.trace_operation("directus_get_collections") as trace:
            try:
                response = self.session.get(
                    f"{self.base_url}/collections",
                    timeout=10
                )
                
                self._requests_made += 1
                
                if response.status_code == 200:
                    data = response.json()
                    collections = data.get('data', [])
                    
                    # Track collections accessed
                    for collection in collections:
                        self._collections_accessed.add(collection.get('collection', 'unknown'))
                    
                    trace.output_result = {"collections_count": len(collections)}
                    return collections
                else:
                    self._requests_failed += 1
                    trace.output_result = {"error": f"HTTP {response.status_code}"}
                    return []
                    
            except Exception as e:
                self._requests_failed += 1
                trace.error_info = {"error": str(e)}
                return []
    
    def create_item(self, collection: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an item in a Directus collection"""
        with self.trace_operation("directus_create_item", collection=collection) as trace:
            try:
                response = self.session.post(
                    f"{self.base_url}/items/{collection}",
                    json=data,
                    timeout=10
                )
                
                self._requests_made += 1
                self._collections_accessed.add(collection)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    item_data = result.get('data', {})
                    
                    trace.output_result = {"created": True, "item_id": item_data.get('id')}
                    
                    self.emit_observation(
                        f"Created item in {collection}",
                        "info",
                        context={"collection": collection, "item_id": item_data.get('id')},
                        emoji="➕"
                    )
                    return item_data
                else:
                    self._requests_failed += 1
                    trace.output_result = {"created": False, "status_code": response.status_code}
                    return None
                    
            except Exception as e:
                self._requests_failed += 1
                trace.error_info = {"error": str(e)}
                return None
    
    def get_items(self, collection: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get items from a Directus collection"""
        with self.trace_operation("directus_get_items", collection=collection) as trace:
            try:
                response = self.session.get(
                    f"{self.base_url}/items/{collection}",
                    params=params or {},
                    timeout=10
                )
                
                self._requests_made += 1
                self._collections_accessed.add(collection)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('data', [])
                    
                    trace.output_result = {"items_count": len(items)}
                    return items
                else:
                    self._requests_failed += 1
                    trace.output_result = {"error": f"HTTP {response.status_code}"}
                    return []
                    
            except Exception as e:
                self._requests_failed += 1
                trace.error_info = {"error": str(e)}
                return []
    
    def update_item(self, collection: str, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an item in a Directus collection"""
        with self.trace_operation("directus_update_item", collection=collection, item_id=item_id) as trace:
            try:
                response = self.session.patch(
                    f"{self.base_url}/items/{collection}/{item_id}",
                    json=data,
                    timeout=10
                )
                
                self._requests_made += 1
                self._collections_accessed.add(collection)
                
                if response.status_code == 200:
                    result = response.json()
                    item_data = result.get('data', {})
                    
                    trace.output_result = {"updated": True, "item_id": item_id}
                    
                    self.emit_observation(
                        f"Updated item in {collection}",
                        "info",
                        context={"collection": collection, "item_id": item_id},
                        emoji="✏️"
                    )
                    return item_data
                else:
                    self._requests_failed += 1
                    trace.output_result = {"updated": False, "status_code": response.status_code}
                    return None
                    
            except Exception as e:
                self._requests_failed += 1
                trace.error_info = {"error": str(e)}
                return None
    
    def delete_item(self, collection: str, item_id: str) -> bool:
        """Delete an item from a Directus collection"""
        with self.trace_operation("directus_delete_item", collection=collection, item_id=item_id) as trace:
            try:
                response = self.session.delete(
                    f"{self.base_url}/items/{collection}/{item_id}",
                    timeout=10
                )
                
                self._requests_made += 1
                self._collections_accessed.add(collection)
                
                if response.status_code == 204:
                    trace.output_result = {"deleted": True}
                    
                    self.emit_observation(
                        f"Deleted item from {collection}",
                        "info",
                        context={"collection": collection, "item_id": item_id},
                        emoji="🗑️"
                    )
                    return True
                else:
                    self._requests_failed += 1
                    trace.output_result = {"deleted": False, "status_code": response.status_code}
                    return False
                    
            except Exception as e:
                self._requests_failed += 1
                trace.error_info = {"error": str(e)}
                return False
    
    # Required BeastlyModule methods
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": "beast_mode_directus_client",
            "module_name": "DirectusClient", 
            "version": "1.0.0",
            "description": "BeastlyModule-compliant Directus CMS client with enhanced observability",
            "base_url": self.base_url,
            "connected": self._connected,
            "requests_made": self._requests_made,
            "collections_accessed": len(self._collections_accessed)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        # Perform health check
        is_healthy = self.health_check()
        
        if is_healthy:
            status = ModuleStatus.HEALTHY
            health_score = 0.95
            issues = []
        elif self._requests_failed > self._requests_made * 0.5:
            status = ModuleStatus.ERROR
            health_score = 0.3
            issues = [f"High failure rate: {self._requests_failed}/{self._requests_made} requests failed"]
        else:
            status = ModuleStatus.WARNING
            health_score = 0.7
            issues = ["Directus not accessible or unhealthy"]
            
        return ModuleHealth(
            module_id="beast_mode_directus_client",
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._requests_failed,
            warning_count=0
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # Test connection
            if self.health_check():
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[],
                    remaining_capabilities=[
                        ModuleCapability.CORE_FUNCTIONALITY,
                        ModuleCapability.API_INTEGRATION,
                        ModuleCapability.DATA_PROCESSING,
                        ModuleCapability.MONITORING
                    ]
                )
            else:
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[
                        ModuleCapability.API_INTEGRATION,
                        ModuleCapability.DATA_PROCESSING
                    ],
                    remaining_capabilities=[
                        ModuleCapability.CORE_FUNCTIONALITY,
                        ModuleCapability.MONITORING
                    ],
                    error_message="Directus not accessible, operating in offline mode"
                )
                
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[
                    ModuleCapability.API_INTEGRATION,
                    ModuleCapability.DATA_PROCESSING
                ],
                remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                error_message=str(e)
            )