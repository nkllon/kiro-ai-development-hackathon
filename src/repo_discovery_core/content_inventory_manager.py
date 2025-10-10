#!/usr/bin/env python3
"""
Content Inventory Manager - Repository Discovery System
=====================================================

Combines scanning, classification, and metadata extraction into unified inventory
with change tracking and git integration.

Author: Beast Mode Framework
Date: 2025-09-18
Version: 1.0
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
import subprocess
import json

# Import unified ReflectiveModule
from ._reflective import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)

# Import our discovery components
from .content_scanner import ContentScanner, ContentScanResult
from .content_classifier import ContentClassifier, ClassificationBatch
from .content_metadata_extractor import ContentMetadataExtractor, FileMetadata


@dataclass
class ContentItem:
    """Unified content item with all discovery data"""
    file_path: str
    content_type: str
    confidence: float
    metadata: FileMetadata
    discovered_at: datetime
    last_modified: datetime
    content_hash: str


@dataclass
class ContentInventory:
    """Complete repository content inventory"""
    inventory_id: str
    root_path: str
    created_at: datetime
    total_items: int
    items: List[ContentItem]
    content_types: Dict[str, int]
    total_size: int
    scan_duration: float
    classification_duration: float
    metadata_duration: float


@dataclass
class ContentChange:
    """Represents a change in repository content"""
    change_type: str  # "added", "modified", "deleted", "moved"
    file_path: str
    old_path: Optional[str]
    timestamp: datetime
    change_details: Dict[str, Any]


class ContentInventoryManager(ReflectiveModule):
    """
    Content Inventory Manager - RM-DDD Compliant
    
    Combines scanning, classification, and metadata into unified inventory.
    
    Single Responsibility: Manage comprehensive content inventory with change tracking
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "ContentInventoryManager"
        self._config = config or {}
        self._logger = logging.getLogger(f"repository_discovery.core.{self.__class__.__name__}")
        
        # Initialize component dependencies
        self._scanner = ContentScanner()
        self._classifier = ContentClassifier()
        self._metadata_extractor = ContentMetadataExtractor()
        
        # Inventory cache
        self._current_inventory: Optional[ContentInventory] = None
        
        self._logger.info("ContentInventoryManager initialized with scanner, classifier, and metadata extractor")
    
    def build_inventory(
        self,
        root_path: Path,
        exclusion_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None
    ) -> ContentInventory:
        """
        Build comprehensive inventory from scan and classification results.
        
        Args:
            root_path: Root directory to inventory
            exclusion_patterns: Additional patterns to exclude
            max_depth: Maximum directory depth
            
        Returns:
            ContentInventory with unified discovery data
        """
        with self.trace_operation("build_inventory") as trace:
            start_time = datetime.now()
            inventory_id = f"inventory_{int(start_time.timestamp())}"
            
            try:
                self._logger.info(f"Building inventory for {root_path}")
                
                # Step 1: Scan filesystem
                scan_start = datetime.now()
                scan_result = self._scanner.discover_all_content(
                    root_path=root_path,
                    exclusion_patterns=exclusion_patterns,
                    max_depth=max_depth
                )
                scan_duration = (datetime.now() - scan_start).total_seconds()
                
                # Step 2: Classify content types
                classify_start = datetime.now()
                file_paths = [Path(f) for f in scan_result.discovered_files]
                classification_result = self._classifier.classify_content_types(
                    file_paths=file_paths,
                    batch_size=100
                )
                classify_duration = (datetime.now() - classify_start).total_seconds()
                
                # Step 3: Extract metadata
                metadata_start = datetime.now()
                metadata_results = self._metadata_extractor.extract_batch_metadata(file_paths)
                metadata_duration = (datetime.now() - metadata_start).total_seconds()
                
                # Step 4: Combine all data into unified inventory
                items = []
                content_types = {}
                
                # Create lookup dictionaries for efficient combination
                classification_lookup = {
                    result.file_path: result for result in classification_result.results
                }
                metadata_lookup = {}
                for result in metadata_results:
                    if result.success and result.metadata:
                        # Convert absolute path to relative path for matching
                        abs_path = Path(result.metadata.file_path)
                        try:
                            rel_path = str(abs_path.relative_to(Path.cwd()))
                            metadata_lookup[rel_path] = result.metadata
                        except ValueError:
                            # If can't make relative, use absolute path as fallback
                            metadata_lookup[result.metadata.file_path] = result.metadata
                
                for file_path in scan_result.discovered_files:
                    path_obj = Path(file_path)
                    
                    # Get classification data
                    classification = classification_lookup.get(str(path_obj))
                    if not classification:
                        self._logger.debug(f"No classification found for {file_path}")
                        continue
                    
                    # Get metadata
                    metadata = metadata_lookup.get(str(path_obj))
                    if not metadata:
                        self._logger.debug(f"No metadata found for {file_path}")
                        continue
                    
                    # Create unified content item
                    item = ContentItem(
                        file_path=file_path,
                        content_type=classification.primary_type.value,
                        confidence=classification.confidence,
                        metadata=metadata,
                        discovered_at=start_time,
                        last_modified=metadata.modified_at,
                        content_hash=metadata.content_hash
                    )
                    
                    items.append(item)
                    
                    # Track content type counts
                    content_type = classification.primary_type.value
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                
                # Create final inventory
                inventory = ContentInventory(
                    inventory_id=inventory_id,
                    root_path=str(root_path),
                    created_at=start_time,
                    total_items=len(items),
                    items=items,
                    content_types=content_types,
                    total_size=scan_result.total_size,
                    scan_duration=scan_duration,
                    classification_duration=classify_duration,
                    metadata_duration=metadata_duration
                )
                
                # Cache current inventory
                self._current_inventory = inventory
                
                self._logger.info(f"Inventory built: {len(items)} items, {len(content_types)} content types")
                
                trace.output_result = {
                    'inventory_id': inventory_id,
                    'total_items': len(items),
                    'content_types': len(content_types),
                    'total_duration': (datetime.now() - start_time).total_seconds()
                }
                
                return inventory
                
            except Exception as e:
                error_msg = f"Failed to build inventory: {e}"
                self._logger.error(error_msg)
                trace.output_result = {'success': False, 'error': error_msg}
                raise
    
    def detect_changes(self, previous_inventory: ContentInventory) -> List[ContentChange]:
        """
        Detect changes between inventory versions with git integration.
        
        Args:
            previous_inventory: Previous inventory to compare against
            
        Returns:
            List of detected changes
        """
        with self.trace_operation("detect_changes") as trace:
            try:
                if not self._current_inventory:
                    raise ValueError("No current inventory available for comparison")
                
                changes = []
                current_time = datetime.now()
                
                # Create lookup sets for efficient comparison
                previous_files = {item.file_path: item for item in previous_inventory.items}
                current_files = {item.file_path: item for item in self._current_inventory.items}
                
                # Detect added files
                for file_path in current_files:
                    if file_path not in previous_files:
                        changes.append(ContentChange(
                            change_type="added",
                            file_path=file_path,
                            old_path=None,
                            timestamp=current_time,
                            change_details={
                                'content_type': current_files[file_path].content_type,
                                'size': current_files[file_path].metadata.file_size
                            }
                        ))
                
                # Detect deleted files
                for file_path in previous_files:
                    if file_path not in current_files:
                        changes.append(ContentChange(
                            change_type="deleted",
                            file_path=file_path,
                            old_path=None,
                            timestamp=current_time,
                            change_details={
                                'content_type': previous_files[file_path].content_type
                            }
                        ))
                
                # Detect modified files
                for file_path in current_files:
                    if file_path in previous_files:
                        current_item = current_files[file_path]
                        previous_item = previous_files[file_path]
                        
                        if current_item.content_hash != previous_item.content_hash:
                            changes.append(ContentChange(
                                change_type="modified",
                                file_path=file_path,
                                old_path=None,
                                timestamp=current_time,
                                change_details={
                                    'old_hash': previous_item.content_hash,
                                    'new_hash': current_item.content_hash,
                                    'old_size': previous_item.metadata.file_size,
                                    'new_size': current_item.metadata.file_size
                                }
                            ))
                
                # Try to get git changes for additional context
                try:
                    git_changes = self._get_git_changes()
                    # TODO: Correlate git changes with file changes for richer context
                except Exception as e:
                    self._logger.warning(f"Could not get git changes: {e}")
                
                self._logger.info(f"Detected {len(changes)} changes")
                
                trace.output_result = {
                    'changes_detected': len(changes),
                    'added': len([c for c in changes if c.change_type == "added"]),
                    'modified': len([c for c in changes if c.change_type == "modified"]),
                    'deleted': len([c for c in changes if c.change_type == "deleted"])
                }
                
                return changes
                
            except Exception as e:
                error_msg = f"Failed to detect changes: {e}"
                self._logger.error(error_msg)
                trace.output_result = {'success': False, 'error': error_msg}
                raise
    
    def get_current_inventory(self) -> Optional[ContentInventory]:
        """Get the current cached inventory"""
        return self._current_inventory
    
    def save_inventory(self, inventory: ContentInventory, output_path: Path) -> None:
        """Save inventory to JSON file for persistence"""
        with self.trace_operation("save_inventory") as trace:
            try:
                # Convert to serializable format
                inventory_data = asdict(inventory)
                
                # Convert datetime objects to ISO strings
                inventory_data['created_at'] = inventory.created_at.isoformat()
                for item_data in inventory_data['items']:
                    item_data['discovered_at'] = item_data['discovered_at'].isoformat() if isinstance(item_data['discovered_at'], datetime) else item_data['discovered_at']
                    item_data['last_modified'] = item_data['last_modified'].isoformat() if isinstance(item_data['last_modified'], datetime) else item_data['last_modified']
                    
                    # Handle metadata datetime fields
                    metadata = item_data['metadata']
                    for field in ['created_at', 'modified_at', 'accessed_at']:
                        if field in metadata and isinstance(metadata[field], datetime):
                            metadata[field] = metadata[field].isoformat()
                
                # Write to file
                with open(output_path, 'w') as f:
                    json.dump(inventory_data, f, indent=2)
                
                self._logger.info(f"Inventory saved to {output_path}")
                trace.output_result = {'saved': True, 'path': str(output_path)}
                
            except Exception as e:
                error_msg = f"Failed to save inventory: {e}"
                self._logger.error(error_msg)
                trace.output_result = {'success': False, 'error': error_msg}
                raise
    
    def _get_git_changes(self) -> List[str]:
        """Get recent git changes for context"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n') if result.stdout.strip() else []
            else:
                return []
        except Exception:
            return []
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ContentInventoryManager",
            "version": "1.0.0",
            "description": "Manages comprehensive content inventory with change tracking",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "status": "implemented",
            "has_current_inventory": self._current_inventory is not None,
            "dependencies": ["ContentScanner", "ContentClassifier", "ContentMetadataExtractor"]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Check dependency health
            scanner_health = self._scanner.get_health_status()
            classifier_health = self._classifier.get_health_status()
            metadata_health = self._metadata_extractor.get_health_status()
            
            # Aggregate health scores
            health_scores = [
                scanner_health.health_score,
                classifier_health.health_score,
                metadata_health.health_score
            ]
            
            avg_health = sum(health_scores) / len(health_scores)
            
            if avg_health >= 0.8:
                status = ModuleStatus.HEALTHY
            elif avg_health >= 0.5:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.ERROR
            
            issues = []
            if scanner_health.health_score < 0.8:
                issues.extend([f"Scanner: {issue}" for issue in scanner_health.issues])
            if classifier_health.health_score < 0.8:
                issues.extend([f"Classifier: {issue}" for issue in classifier_health.issues])
            if metadata_health.health_score < 0.8:
                issues.extend([f"Metadata: {issue}" for issue in metadata_health.issues])
                
        except Exception as e:
            status = ModuleStatus.ERROR
            avg_health = 0.0
            issues = [f"ContentInventoryManager health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=avg_health,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still build basic inventories
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY
            ]
            
            degraded_capabilities = [
                ModuleCapability.DATA_PROCESSING,
                ModuleCapability.VALIDATION,
                ModuleCapability.MONITORING
            ]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )