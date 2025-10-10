#!/usr/bin/env python3
"""
CMS Integration - Task 5.1 Component
====================================

Implements CMS integration through Directus for configuration management
with fallback to file-based configuration when CMS is unavailable.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import json
import time
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability


@dataclass
class CMSConfig:
    """Configuration for CMS integration."""
    # Directus configuration
    cms_url: str = "http://localhost:8055"
    api_endpoint: str = "/items"
    auth_endpoint: str = "/auth/login"
    
    # Authentication
    username: Optional[str] = None
    password: Optional[str] = None
    access_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Fallback configuration
    fallback_enabled: bool = True
    fallback_directory: Path = Path("config/fallback")
    
    # Connection settings
    connection_timeout: int = 10
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Sync settings
    auto_sync_enabled: bool = True
    sync_interval_seconds: int = 300  # 5 minutes
    
    # Collections to manage
    collections: List[str] = field(default_factory=lambda: [
        "orchestration_config",
        "validation_rules",
        "generation_templates",
        "monitoring_thresholds"
    ])


@dataclass
class ConfigurationItem:
    """Represents a configuration item."""
    collection: str
    item_id: str
    data: Dict[str, Any]
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    source: str = "cms"  # cms, file, default


class CMSIntegration(ReflectiveModule):
    """
    CMS integration through Directus with file-based fallback.
    
    Provides configuration management capabilities with automatic
    synchronization and graceful degradation when CMS is unavailable.
    """
    
    def __init__(self, cms_url: str = "http://localhost:8055", fallback_enabled: bool = True):
        super().__init__()
        self.module_id = "CMSIntegration"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Configuration
        self._config = CMSConfig(
            cms_url=cms_url,
            fallback_enabled=fallback_enabled
        )
        
        # Ensure fallback directory exists
        if self._config.fallback_enabled:
            self._config.fallback_directory.mkdir(parents=True, exist_ok=True)
        
        # State
        self._is_connected = False
        self._last_sync_time: Optional[datetime] = None
        self._configuration_cache: Dict[str, Dict[str, ConfigurationItem]] = {}
        
        # Metrics
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Initialize cache
        self._initialize_configuration_cache()
        
        self._logger.info("CMSIntegration initialized")
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.CONFIGURATION
        ]
    
    def _initialize_configuration_cache(self) -> None:
        """Initialize configuration cache with default values."""
        # Initialize empty cache for each collection
        for collection in self._config.collections:
            self._configuration_cache[collection] = {}
        
        # Load fallback configurations if available
        if self._config.fallback_enabled:
            self._load_fallback_configurations()
        
        # Try to connect to CMS and sync
        self._attempt_cms_connection()
    
    def _load_fallback_configurations(self) -> None:
        """Load configurations from fallback files."""
        self._logger.info("Loading fallback configurations...")
        
        for collection in self._config.collections:
            fallback_file = self._config.fallback_directory / f"{collection}.yaml"
            
            if fallback_file.exists():
                try:
                    with open(fallback_file, 'r') as f:
                        data = yaml.safe_load(f) or {}
                    
                    # Convert to ConfigurationItem objects
                    for item_id, item_data in data.items():
                        config_item = ConfigurationItem(
                            collection=collection,
                            item_id=item_id,
                            data=item_data,
                            source="file"
                        )
                        self._configuration_cache[collection][item_id] = config_item
                    
                    self._logger.info(f"Loaded {len(data)} items from {fallback_file}")
                    
                except Exception as e:
                    self._logger.error(f"Error loading fallback file {fallback_file}: {e}")
            else:
                # Create default fallback file
                self._create_default_fallback_file(collection, fallback_file)
    
    def _create_default_fallback_file(self, collection: str, file_path: Path) -> None:
        """Create default fallback configuration file."""
        default_configs = {
            "orchestration_config": {
                "default": {
                    "scheduled_generation_interval": 3600,
                    "change_detection_interval": 300,
                    "stale_documentation_threshold": 86400,
                    "max_concurrent_generations": 3
                }
            },
            "validation_rules": {
                "accuracy_threshold": {
                    "threshold": 0.95,
                    "enabled": True
                },
                "staleness_check": {
                    "threshold_hours": 24,
                    "enabled": True
                }
            },
            "generation_templates": {
                "component_diagram": {
                    "format": "plantuml",
                    "include_security": True,
                    "include_real_time": True
                }
            },
            "monitoring_thresholds": {
                "response_time": {
                    "warning": 1000,
                    "critical": 5000
                },
                "error_rate": {
                    "warning": 0.05,
                    "critical": 0.10
                }
            }
        }
        
        default_data = default_configs.get(collection, {"default": {}})
        
        try:
            with open(file_path, 'w') as f:
                yaml.dump(default_data, f, default_flow_style=False)
            
            self._logger.info(f"Created default fallback file: {file_path}")
            
        except Exception as e:
            self._logger.error(f"Error creating default fallback file {file_path}: {e}")
    
    def _attempt_cms_connection(self) -> bool:
        """Attempt to connect to CMS."""
        try:
            # Test connection with health check
            response = requests.get(
                f"{self._config.cms_url}/server/ping",
                timeout=self._config.connection_timeout
            )
            
            if response.status_code == 200:
                self._is_connected = True
                self._logger.info("Successfully connected to CMS")
                
                # Sync configurations
                self._sync_from_cms()
                return True
            else:
                self._logger.warning(f"CMS health check failed: {response.status_code}")
                
        except Exception as e:
            self._logger.warning(f"Failed to connect to CMS: {e}")
        
        self._is_connected = False
        return False
    
    def _sync_from_cms(self) -> None:
        """Sync configurations from CMS."""
        if not self._is_connected:
            return
        
        self._logger.info("Syncing configurations from CMS...")
        
        for collection in self._config.collections:
            try:
                items = self._fetch_collection_items(collection)
                
                # Update cache
                for item in items:
                    config_item = ConfigurationItem(
                        collection=collection,
                        item_id=item.get("id", str(time.time())),
                        data=item,
                        source="cms",
                        updated_at=datetime.now()
                    )
                    self._configuration_cache[collection][config_item.item_id] = config_item
                
                self._logger.info(f"Synced {len(items)} items from collection {collection}")
                
            except Exception as e:
                self._logger.error(f"Error syncing collection {collection}: {e}")
        
        self._last_sync_time = datetime.now()
        
        # Save to fallback files
        if self._config.fallback_enabled:
            self._save_to_fallback_files()
    
    def _fetch_collection_items(self, collection: str) -> List[Dict[str, Any]]:
        """Fetch items from a CMS collection."""
        url = f"{self._config.cms_url}{self._config.api_endpoint}/{collection}"
        
        self._total_requests += 1
        
        try:
            response = requests.get(
                url,
                timeout=self._config.request_timeout,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                self._successful_requests += 1
                data = response.json()
                return data.get("data", [])
            else:
                self._failed_requests += 1
                self._logger.error(f"Failed to fetch collection {collection}: {response.status_code}")
                return []
                
        except Exception as e:
            self._failed_requests += 1
            self._logger.error(f"Error fetching collection {collection}: {e}")
            return []
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for CMS requests."""
        headers = {"Content-Type": "application/json"}
        
        if self._config.access_token:
            headers["Authorization"] = f"Bearer {self._config.access_token}"
        
        return headers
    
    def _save_to_fallback_files(self) -> None:
        """Save current cache to fallback files."""
        if not self._config.fallback_enabled:
            return
        
        for collection, items in self._configuration_cache.items():
            fallback_file = self._config.fallback_directory / f"{collection}.yaml"
            
            try:
                # Convert ConfigurationItem objects to dict
                data = {
                    item_id: item.data
                    for item_id, item in items.items()
                }
                
                with open(fallback_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
                
                self._logger.debug(f"Saved {len(data)} items to {fallback_file}")
                
            except Exception as e:
                self._logger.error(f"Error saving fallback file {fallback_file}: {e}")
    
    def get_configuration(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration item."""
        if collection not in self._configuration_cache:
            self._cache_misses += 1
            return None
        
        if item_id not in self._configuration_cache[collection]:
            self._cache_misses += 1
            return None
        
        self._cache_hits += 1
        config_item = self._configuration_cache[collection][item_id]
        return config_item.data
    
    def get_collection_configurations(self, collection: str) -> Dict[str, Dict[str, Any]]:
        """Get all configurations for a collection."""
        if collection not in self._configuration_cache:
            return {}
        
        return {
            item_id: item.data
            for item_id, item in self._configuration_cache[collection].items()
        }
    
    def set_configuration(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Set configuration item."""
        try:
            # Try to update in CMS first
            if self._is_connected:
                success = self._update_cms_item(collection, item_id, data)
                if not success and not self._config.fallback_enabled:
                    return False
            
            # Update cache
            config_item = ConfigurationItem(
                collection=collection,
                item_id=item_id,
                data=data,
                source="cms" if self._is_connected else "file",
                updated_at=datetime.now()
            )
            
            if collection not in self._configuration_cache:
                self._configuration_cache[collection] = {}
            
            self._configuration_cache[collection][item_id] = config_item
            
            # Save to fallback if enabled
            if self._config.fallback_enabled:
                self._save_to_fallback_files()
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error setting configuration {collection}/{item_id}: {e}")
            return False
    
    def _update_cms_item(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Update item in CMS."""
        url = f"{self._config.cms_url}{self._config.api_endpoint}/{collection}/{item_id}"
        
        self._total_requests += 1
        
        try:
            response = requests.patch(
                url,
                json=data,
                timeout=self._config.request_timeout,
                headers=self._get_auth_headers()
            )
            
            if response.status_code in [200, 204]:
                self._successful_requests += 1
                return True
            else:
                self._failed_requests += 1
                self._logger.error(f"Failed to update CMS item {collection}/{item_id}: {response.status_code}")
                return False
                
        except Exception as e:
            self._failed_requests += 1
            self._logger.error(f"Error updating CMS item {collection}/{item_id}: {e}")
            return False
    
    def delete_configuration(self, collection: str, item_id: str) -> bool:
        """Delete configuration item."""
        try:
            # Try to delete from CMS first
            if self._is_connected:
                self._delete_cms_item(collection, item_id)
            
            # Remove from cache
            if (collection in self._configuration_cache and 
                item_id in self._configuration_cache[collection]):
                del self._configuration_cache[collection][item_id]
            
            # Update fallback files
            if self._config.fallback_enabled:
                self._save_to_fallback_files()
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error deleting configuration {collection}/{item_id}: {e}")
            return False
    
    def _delete_cms_item(self, collection: str, item_id: str) -> bool:
        """Delete item from CMS."""
        url = f"{self._config.cms_url}{self._config.api_endpoint}/{collection}/{item_id}"
        
        self._total_requests += 1
        
        try:
            response = requests.delete(
                url,
                timeout=self._config.request_timeout,
                headers=self._get_auth_headers()
            )
            
            if response.status_code in [200, 204]:
                self._successful_requests += 1
                return True
            else:
                self._failed_requests += 1
                self._logger.error(f"Failed to delete CMS item {collection}/{item_id}: {response.status_code}")
                return False
                
        except Exception as e:
            self._failed_requests += 1
            self._logger.error(f"Error deleting CMS item {collection}/{item_id}: {e}")
            return False
    
    def sync_configurations(self) -> bool:
        """Manually trigger configuration sync."""
        if not self._attempt_cms_connection():
            self._logger.warning("CMS not available, using cached/fallback configurations")
            return False
        
        self._sync_from_cms()
        return True
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status."""
        return {
            "is_connected": self._is_connected,
            "last_sync_time": self._last_sync_time.isoformat() if self._last_sync_time else None,
            "cms_url": self._config.cms_url,
            "fallback_enabled": self._config.fallback_enabled,
            "collections": self._config.collections,
            "cached_items": {
                collection: len(items)
                for collection, items in self._configuration_cache.items()
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """ReflectiveModule health status implementation."""
        return {
            "status": "healthy" if (self._is_connected or self._config.fallback_enabled) else "degraded",
            "cms_connection": {
                "connected": self._is_connected,
                "url": self._config.cms_url,
                "last_sync": self._last_sync_time.isoformat() if self._last_sync_time else None
            },
            "fallback": {
                "enabled": self._config.fallback_enabled,
                "directory": str(self._config.fallback_directory)
            },
            "cache": {
                "collections": len(self._configuration_cache),
                "total_items": sum(len(items) for items in self._configuration_cache.values()),
                "hit_rate": (
                    self._cache_hits / max(1, self._cache_hits + self._cache_misses)
                ) * 100
            },
            "requests": {
                "total": self._total_requests,
                "successful": self._successful_requests,
                "failed": self._failed_requests,
                "success_rate": (
                    self._successful_requests / max(1, self._total_requests)
                ) * 100
            }
        }
    
    def get_metrics(self) -> Dict[str, float]:
        """ReflectiveModule metrics implementation."""
        return {
            "cms_integration_connected": 1.0 if self._is_connected else 0.0,
            "cms_integration_requests_total": float(self._total_requests),
            "cms_integration_requests_successful": float(self._successful_requests),
            "cms_integration_requests_failed": float(self._failed_requests),
            "cms_integration_success_rate": (
                self._successful_requests / max(1, self._total_requests)
            ) * 100,
            "cms_integration_cache_hits": float(self._cache_hits),
            "cms_integration_cache_misses": float(self._cache_misses),
            "cms_integration_cache_hit_rate": (
                self._cache_hits / max(1, self._cache_hits + self._cache_misses)
            ) * 100,
            "cms_integration_cached_collections": float(len(self._configuration_cache)),
            "cms_integration_cached_items": float(
                sum(len(items) for items in self._configuration_cache.values())
            )
        }#!/usr/bin/env python3
"""
CMS Integration - Phase 5 Task 5.1 Component

Integrates with Directus CMS for configuration management with
file-based fallback when CMS is unavailable.
"""

import os
import json
import yaml
import aiohttp
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class CMSConfiguration:
    """Represents a configuration item from CMS."""
    id: str
    collection: str
    key: str
    value: Any
    data_type: str  # 'string', 'number', 'boolean', 'json', 'array'
    description: Optional[str] = None
    category: Optional[str] = None
    last_updated: Optional[datetime] = None
    version: int = 1


@dataclass
class CMSConnectionConfig:
    """Configuration for CMS connection."""
    base_url: str = "http://localhost:8055"
    api_token: Optional[str] = None
    timeout: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0
    fallback_enabled: bool = True
    fallback_directory: str = "config/fallback"
    sync_interval_minutes: int = 15


class CMSIntegration(ReflectiveModule):
    """
    Directus CMS integration with file-based fallback.
    
    Provides configuration management through Directus CMS with automatic
    fallback to file-based configuration when CMS is unavailable.
    """
    
    def __init__(self, config: Optional[CMSConnectionConfig] = None):
        super().__init__()
        self.config = config or CMSConnectionConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.cms_available = False
        self.last_sync = None
        self.configuration_cache: Dict[str, CMSConfiguration] = {}
        self.fallback_configs: Dict[str, Any] = {}
        self.sync_task: Optional[asyncio.Task] = None
        
        # Ensure fallback directory exists
        Path(self.config.fallback_directory).mkdir(parents=True, exist_ok=True)
        
        # Register capabilities
        self.register_capability('cms_integration', {
            'description': 'Directus CMS integration with file-based fallback',
            'cms_url': self.config.base_url,
            'fallback_enabled': self.config.fallback_enabled,
            'sync_interval_minutes': self.config.sync_interval_minutes
        })
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize CMS integration."""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test CMS connection
            cms_status = await self._test_cms_connection()
            
            # Load fallback configurations
            await self._load_fallback_configurations()
            
            # If CMS is available, sync configurations
            if cms_status['available']:
                await self._sync_from_cms()
            
            # Start periodic sync if CMS is available
            if cms_status['available'] and self.config.sync_interval_minutes > 0:
                self.sync_task = asyncio.create_task(self._periodic_sync())
            
            self.logger.info(f"CMS integration initialized - CMS available: {cms_status['available']}")
            
            return {
                'status': 'initialized',
                'cms_available': cms_status['available'],
                'fallback_configs_loaded': len(self.fallback_configs),
                'cached_configs': len(self.configuration_cache)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CMS integration: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _test_cms_connection(self) -> Dict[str, Any]:
        """Test connection to Directus CMS."""
        try:
            if not self.session:
                return {'available': False, 'error': 'No session'}
            
            # Test server ping
            async with self.session.get(f"{self.config.base_url}/server/ping") as response:
                if response.status == 200:
                    ping_data = await response.json()
                    self.cms_available = True
                    return {
                        'available': True,
                        'status': response.status,
                        'ping_response': ping_data
                    }
                else:
                    self.cms_available = False
                    return {
                        'available': False,
                        'status': response.status,
                        'error': f'HTTP {response.status}'
                    }
        
        except Exception as e:
            self.cms_available = False
            self.logger.warning(f"CMS connection test failed: {e}")
            return {'available': False, 'error': str(e)}
    
    async def _load_fallback_configurations(self):
        """Load configurations from fallback files."""
        try:
            fallback_path = Path(self.config.fallback_directory)
            
            # Load JSON files
            for json_file in fallback_path.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        self.fallback_configs[json_file.stem] = data
                        self.logger.debug(f"Loaded fallback config: {json_file.name}")
                except Exception as e:
                    self.logger.error(f"Error loading {json_file}: {e}")
            
            # Load YAML files
            for yaml_file in fallback_path.glob("*.yml"):
                try:
                    with open(yaml_file, 'r') as f:
                        data = yaml.safe_load(f)
                        self.fallback_configs[yaml_file.stem] = data
                        self.logger.debug(f"Loaded fallback config: {yaml_file.name}")
                except Exception as e:
                    self.logger.error(f"Error loading {yaml_file}: {e}")
            
            for yaml_file in fallback_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        data = yaml.safe_load(f)
                        self.fallback_configs[yaml_file.stem] = data
                        self.logger.debug(f"Loaded fallback config: {yaml_file.name}")
                except Exception as e:
                    self.logger.error(f"Error loading {yaml_file}: {e}")
            
            self.logger.info(f"Loaded {len(self.fallback_configs)} fallback configurations")
            
        except Exception as e:
            self.logger.error(f"Error loading fallback configurations: {e}")
    
    async def _sync_from_cms(self) -> Dict[str, Any]:
        """Sync configurations from CMS."""
        if not self.cms_available or not self.session:
            return {'status': 'cms_unavailable'}
        
        try:
            synced_configs = 0
            errors = []
            
            # Define collections to sync
            collections_to_sync = [
                'orchestration_config',
                'discovery_config',
                'analysis_config',
                'generation_config',
                'validation_config'
            ]
            
            for collection in collections_to_sync:
                try:
                    configs = await self._fetch_collection_configs(collection)
                    for config in configs:
                        self.configuration_cache[f"{collection}.{config.key}"] = config
                        synced_configs += 1
                    
                    # Save to fallback file
                    await self._save_fallback_config(collection, configs)
                    
                except Exception as e:
                    error_msg = f"Error syncing {collection}: {e}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            self.last_sync = datetime.now()
            
            return {
                'status': 'completed',
                'synced_configs': synced_configs,
                'errors': errors,
                'last_sync': self.last_sync.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error syncing from CMS: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _fetch_collection_configs(self, collection: str) -> List[CMSConfiguration]:
        """Fetch configurations from a specific CMS collection."""
        if not self.session:
            return []
        
        try:
            url = f"{self.config.base_url}/items/{collection}"
            headers = {}
            
            if self.config.api_token:
                headers['Authorization'] = f"Bearer {self.config.api_token}"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    configs = []
                    
                    items = data.get('data', [])
                    if not isinstance(items, list):
                        items = [items] if items else []
                    
                    for item in items:
                        config = CMSConfiguration(
                            id=str(item.get('id', '')),
                            collection=collection,
                            key=item.get('key', ''),
                            value=item.get('value'),
                            data_type=item.get('data_type', 'string'),
                            description=item.get('description'),
                            category=item.get('category'),
                            last_updated=datetime.fromisoformat(item['date_updated'].replace('Z', '+00:00')) if item.get('date_updated') else None,
                            version=item.get('version', 1)
                        )
                        configs.append(config)
                    
                    return configs
                else:
                    self.logger.warning(f"Failed to fetch {collection}: HTTP {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error fetching {collection}: {e}")
            return []
    
    async def _save_fallback_config(self, collection: str, configs: List[CMSConfiguration]):
        """Save configurations to fallback file."""
        try:
            fallback_file = Path(self.config.fallback_directory) / f"{collection}.json"
            
            config_data = {
                'collection': collection,
                'last_updated': datetime.now().isoformat(),
                'configs': [asdict(config) for config in configs]
            }
            
            with open(fallback_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            self.logger.debug(f"Saved fallback config for {collection}")
            
        except Exception as e:
            self.logger.error(f"Error saving fallback config for {collection}: {e}")
    
    async def _periodic_sync(self):
        """Periodic synchronization with CMS."""
        while True:
            try:
                await asyncio.sleep(self.config.sync_interval_minutes * 60)
                
                # Test CMS availability
                cms_status = await self._test_cms_connection()
                
                if cms_status['available']:
                    await self._sync_from_cms()
                else:
                    self.logger.warning("CMS not available for periodic sync")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic sync: {e}")
    
    async def get_config(self, key: str, default: Any = None, collection: Optional[str] = None) -> Any:
        """Get configuration value by key."""
        try:
            # Try cache first
            cache_key = f"{collection}.{key}" if collection else key
            
            if cache_key in self.configuration_cache:
                config = self.configuration_cache[cache_key]
                return self._convert_config_value(config.value, config.data_type)
            
            # Try fallback configurations
            if collection and collection in self.fallback_configs:
                fallback_data = self.fallback_configs[collection]
                if isinstance(fallback_data, dict) and 'configs' in fallback_data:
                    for config_item in fallback_data['configs']:
                        if config_item.get('key') == key:
                            return self._convert_config_value(config_item['value'], config_item.get('data_type', 'string'))
            
            # Try direct fallback lookup
            if key in self.fallback_configs:
                return self.fallback_configs[key]
            
            # Return default
            return default
            
        except Exception as e:
            self.logger.error(f"Error getting config {key}: {e}")
            return default
    
    async def set_config(self, key: str, value: Any, collection: str = 'orchestration_config', 
                        data_type: str = 'string', description: Optional[str] = None) -> Dict[str, Any]:
        """Set configuration value."""
        try:
            if self.cms_available and self.session:
                # Try to update in CMS
                result = await self._update_cms_config(collection, key, value, data_type, description)
                if result['success']:
                    # Update cache
                    config = CMSConfiguration(
                        id=result.get('id', ''),
                        collection=collection,
                        key=key,
                        value=value,
                        data_type=data_type,
                        description=description,
                        last_updated=datetime.now()
                    )
                    self.configuration_cache[f"{collection}.{key}"] = config
                    return {'status': 'updated_cms', 'result': result}
            
            # Fallback to file-based storage
            await self._update_fallback_config(collection, key, value, data_type, description)
            return {'status': 'updated_fallback'}
            
        except Exception as e:
            self.logger.error(f"Error setting config {key}: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _update_cms_config(self, collection: str, key: str, value: Any, 
                               data_type: str, description: Optional[str]) -> Dict[str, Any]:
        """Update configuration in CMS."""
        if not self.session:
            return {'success': False, 'error': 'No session'}
        
        try:
            url = f"{self.config.base_url}/items/{collection}"
            headers = {'Content-Type': 'application/json'}
            
            if self.config.api_token:
                headers['Authorization'] = f"Bearer {self.config.api_token}"
            
            data = {
                'key': key,
                'value': value,
                'data_type': data_type,
                'description': description
            }
            
            # Try to find existing item first
            existing_item = await self._find_cms_config_item(collection, key)
            
            if existing_item:
                # Update existing item
                item_url = f"{url}/{existing_item['id']}"
                async with self.session.patch(item_url, json=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {'success': True, 'id': existing_item['id'], 'action': 'updated', 'data': result}
                    else:
                        return {'success': False, 'error': f'HTTP {response.status}'}
            else:
                # Create new item
                async with self.session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {'success': True, 'id': result.get('data', {}).get('id'), 'action': 'created', 'data': result}
                    else:
                        return {'success': False, 'error': f'HTTP {response.status}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _find_cms_config_item(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Find existing configuration item in CMS."""
        if not self.session:
            return None
        
        try:
            url = f"{self.config.base_url}/items/{collection}"
            params = {'filter[key][_eq]': key}
            headers = {}
            
            if self.config.api_token:
                headers['Authorization'] = f"Bearer {self.config.api_token}"
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('data', [])
                    return items[0] if items else None
                else:
                    return None
        
        except Exception as e:
            self.logger.error(f"Error finding CMS config item: {e}")
            return None
    
    async def _update_fallback_config(self, collection: str, key: str, value: Any, 
                                    data_type: str, description: Optional[str]):
        """Update configuration in fallback file."""
        try:
            fallback_file = Path(self.config.fallback_directory) / f"{collection}.json"
            
            # Load existing data
            config_data = {'collection': collection, 'configs': []}
            if fallback_file.exists():
                with open(fallback_file, 'r') as f:
                    config_data = json.load(f)
            
            # Update or add configuration
            configs = config_data.get('configs', [])
            updated = False
            
            for config_item in configs:
                if config_item.get('key') == key:
                    config_item['value'] = value
                    config_item['data_type'] = data_type
                    config_item['description'] = description
                    config_item['last_updated'] = datetime.now().isoformat()
                    updated = True
                    break
            
            if not updated:
                configs.append({
                    'key': key,
                    'value': value,
                    'data_type': data_type,
                    'description': description,
                    'last_updated': datetime.now().isoformat()
                })
            
            config_data['configs'] = configs
            config_data['last_updated'] = datetime.now().isoformat()
            
            # Save to file
            with open(fallback_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            # Update fallback cache
            self.fallback_configs[collection] = config_data
            
        except Exception as e:
            self.logger.error(f"Error updating fallback config: {e}")
    
    def _convert_config_value(self, value: Any, data_type: str) -> Any:
        """Convert configuration value to appropriate type."""
        try:
            if data_type == 'number':
                return float(value) if '.' in str(value) else int(value)
            elif data_type == 'boolean':
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes', 'on')
            elif data_type == 'json':
                if isinstance(value, (dict, list)):
                    return value
                return json.loads(value) if isinstance(value, str) else value
            elif data_type == 'array':
                if isinstance(value, list):
                    return value
                return json.loads(value) if isinstance(value, str) else [value]
            else:  # string
                return str(value)
        except Exception as e:
            self.logger.warning(f"Error converting config value {value} to {data_type}: {e}")
            return value
    
    async def get_all_configs(self, collection: Optional[str] = None) -> Dict[str, Any]:
        """Get all configurations, optionally filtered by collection."""
        configs = {}
        
        # From cache
        for cache_key, config in self.configuration_cache.items():
            if collection is None or config.collection == collection:
                configs[config.key] = self._convert_config_value(config.value, config.data_type)
        
        # From fallback
        if collection:
            if collection in self.fallback_configs:
                fallback_data = self.fallback_configs[collection]
                if isinstance(fallback_data, dict) and 'configs' in fallback_data:
                    for config_item in fallback_data['configs']:
                        key = config_item.get('key')
                        if key and key not in configs:
                            configs[key] = self._convert_config_value(
                                config_item['value'], 
                                config_item.get('data_type', 'string')
                            )
        else:
            # All fallback configs
            for fb_key, fb_value in self.fallback_configs.items():
                if fb_key not in configs:
                    configs[fb_key] = fb_value
        
        return configs
    
    async def force_sync(self) -> Dict[str, Any]:
        """Force synchronization with CMS."""
        if not self.cms_available:
            cms_status = await self._test_cms_connection()
            if not cms_status['available']:
                return {'status': 'cms_unavailable', 'error': cms_status.get('error')}
        
        return await self._sync_from_cms()
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status."""
        return {
            'cms_available': self.cms_available,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'cached_configs': len(self.configuration_cache),
            'fallback_configs': len(self.fallback_configs),
            'sync_interval_minutes': self.config.sync_interval_minutes,
            'periodic_sync_active': self.sync_task is not None and not self.sync_task.done()
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            # Cancel periodic sync
            if self.sync_task:
                self.sync_task.cancel()
                try:
                    await self.sync_task
                except asyncio.CancelledError:
                    pass
            
            # Close HTTP session
            if self.session:
                await self.session.close()
                self.session = None
            
            self.logger.info("CMS integration cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'cms_available': self.cms_available,
            'session_active': self.session is not None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'cached_configs': len(self.configuration_cache),
            'fallback_configs': len(self.fallback_configs)
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,  # Always ready due to fallback
            'cms_available': self.cms_available,
            'fallback_enabled': self.config.fallback_enabled,
            'configs_available': len(self.configuration_cache) > 0 or len(self.fallback_configs) > 0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get CMS integration metrics."""
        return {
            'cms_integration_available': 1 if self.cms_available else 0,
            'cms_integration_cached_configs': len(self.configuration_cache),
            'cms_integration_fallback_configs': len(self.fallback_configs),
            'cms_integration_sync_active': 1 if (self.sync_task and not self.sync_task.done()) else 0
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create CMS integration
        config = CMSConnectionConfig(
            base_url="http://localhost:8055",
            sync_interval_minutes=5
        )
        
        cms = CMSIntegration(config)
        
        # Initialize
        result = await cms.initialize()
        print(f"Initialization: {result}")
        
        # Set a configuration
        await cms.set_config('test_key', 'test_value', 'orchestration_config', 'string', 'Test configuration')
        
        # Get configuration
        value = await cms.get_config('test_key', collection='orchestration_config')
        print(f"Retrieved value: {value}")
        
        # Get all configs
        all_configs = await cms.get_all_configs('orchestration_config')
        print(f"All configs: {all_configs}")
        
        # Get sync status
        sync_status = await cms.get_sync_status()
        print(f"Sync status: {sync_status}")
        
        # Cleanup
        await cms.cleanup()
    
    asyncio.run(main())