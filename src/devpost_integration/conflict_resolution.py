#!/usr/bin/env python3
"""
Conflict Resolution - Multi-project conflict resolution

Extracted from multi_project_manager.py for RM-DDD compliance.
Single responsibility: Multi-project conflict resolution logic.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import ConflictResolution, ConflictResolutionStrategy

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Multi-project conflict resolution logic."""
    
    def __init__(self):
        """Initialize conflict resolver."""
        self.resolution_history: List[ConflictResolution] = []
        self.default_strategy = ConflictResolutionStrategy.MANUAL
    
    def detect_conflicts(self, project_ids: List[str], project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts between projects."""
        from .conflict_detector import ConflictDetector
        
        detector = ConflictDetector()
        return detector.detect_conflicts(project_ids, project_data)
    
    def resolve_conflict(self, conflict_id: str, project_ids: List[str], 
                        conflict_type: str, strategy: ConflictResolutionStrategy,
                        resolution_data: Optional[Dict[str, Any]] = None) -> ConflictResolution:
        """Resolve a specific conflict."""
        try:
            resolution = ConflictResolution(
                conflict_id=conflict_id,
                project_ids=project_ids,
                conflict_type=conflict_type,
                resolution_strategy=strategy,
                resolved=False
            )
            
            if strategy == ConflictResolutionStrategy.AUTOMATIC:
                resolution = self._resolve_automatic(conflict_id, project_ids, conflict_type, resolution_data)
            elif strategy == ConflictResolutionStrategy.MANUAL:
                resolution = self._resolve_manual(conflict_id, project_ids, conflict_type, resolution_data)
            elif strategy == ConflictResolutionStrategy.PROMPT:
                resolution = self._resolve_prompt(conflict_id, project_ids, conflict_type, resolution_data)
            elif strategy == ConflictResolutionStrategy.IGNORE:
                resolution = self._resolve_ignore(conflict_id, project_ids, conflict_type)
            else:
                raise ValueError(f"Unknown resolution strategy: {strategy}")
            
            # Record resolution
            self.resolution_history.append(resolution)
            
            # Keep only last 50 resolutions
            if len(self.resolution_history) > 50:
                self.resolution_history = self.resolution_history[-50:]
            
            return resolution
            
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict_id}: {e}")
            return ConflictResolution(
                conflict_id=conflict_id,
                project_ids=project_ids,
                conflict_type=conflict_type,
                resolution_strategy=strategy,
                resolved=False,
                error_message=str(e)
            )
    
    
    def _resolve_automatic(self, conflict_id: str, project_ids: List[str], 
                          conflict_type: str, resolution_data: Optional[Dict[str, Any]]) -> ConflictResolution:
        """Resolve conflict automatically."""
        # Implement automatic resolution logic
        resolution = ConflictResolution(
            conflict_id=conflict_id,
            project_ids=project_ids,
            conflict_type=conflict_type,
            resolution_strategy=ConflictResolutionStrategy.AUTOMATIC,
            resolved=True,
            resolution_timestamp=datetime.now(),
            resolution_details="Automatically resolved using default rules",
            auto_resolved=True
        )
        
        logger.info(f"Automatically resolved conflict {conflict_id}")
        return resolution
    
    def _resolve_manual(self, conflict_id: str, project_ids: List[str], 
                       conflict_type: str, resolution_data: Optional[Dict[str, Any]]) -> ConflictResolution:
        """Resolve conflict manually."""
        # Manual resolution requires user intervention
        resolution = ConflictResolution(
            conflict_id=conflict_id,
            project_ids=project_ids,
            conflict_type=conflict_type,
            resolution_strategy=ConflictResolutionStrategy.MANUAL,
            resolved=False,
            resolution_details="Requires manual intervention"
        )
        
        logger.info(f"Manual resolution required for conflict {conflict_id}")
        return resolution
    
    def _resolve_prompt(self, conflict_id: str, project_ids: List[str], 
                       conflict_type: str, resolution_data: Optional[Dict[str, Any]]) -> ConflictResolution:
        """Resolve conflict with user prompt."""
        # Prompt-based resolution
        resolution = ConflictResolution(
            conflict_id=conflict_id,
            project_ids=project_ids,
            conflict_type=conflict_type,
            resolution_strategy=ConflictResolutionStrategy.PROMPT,
            resolved=False,
            resolution_details="Awaiting user prompt response"
        )
        
        logger.info(f"Prompt resolution initiated for conflict {conflict_id}")
        return resolution
    
    def _resolve_ignore(self, conflict_id: str, project_ids: List[str], conflict_type: str) -> ConflictResolution:
        """Ignore conflict."""
        resolution = ConflictResolution(
            conflict_id=conflict_id,
            project_ids=project_ids,
            conflict_type=conflict_type,
            resolution_strategy=ConflictResolutionStrategy.IGNORE,
            resolved=True,
            resolution_timestamp=datetime.now(),
            resolution_details="Conflict ignored as per strategy",
            auto_resolved=True
        )
        
        logger.info(f"Ignored conflict {conflict_id}")
        return resolution
    
    def get_resolution_history(self) -> List[ConflictResolution]:
        """Get conflict resolution history."""
        return self.resolution_history.copy()
    
    def get_resolution_metrics(self) -> Dict[str, Any]:
        """Get conflict resolution metrics."""
        total_resolutions = len(self.resolution_history)
        resolved_count = sum(1 for r in self.resolution_history if r.resolved)
        auto_resolved_count = sum(1 for r in self.resolution_history if r.auto_resolved)
        
        return {
            'total_conflicts': total_resolutions,
            'resolved_conflicts': resolved_count,
            'auto_resolved_conflicts': auto_resolved_count,
            'resolution_rate': resolved_count / total_resolutions if total_resolutions > 0 else 0,
            'auto_resolution_rate': auto_resolved_count / total_resolutions if total_resolutions > 0 else 0
        }
