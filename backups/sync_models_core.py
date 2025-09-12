"""
Sync Models Core

This module was extracted from sync_models.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import SyncOperationType, ChangeType
from typing import Dict, List, Any, Optional

class SyncResult(ReflectiveModule):
    """
    Manages synchronization results and outcomes.
    
    This class handles the results of sync operations including
    success status, error details, and performance metrics.
    """

    def __init__(self, result_data: Dict[str, Any]=None):
        """Initialize sync result."""
        super().__init__()
        self.module_id = 'sync_result'
        self.version = '1.0.0'
        self.result_data = result_data or {}
        self.success = True
        self.error_message = None
        self.sync_time = datetime.now()
        self.records_processed = 0
        self.records_failed = 0
        self._operation_count = 0
        self._errors = 0
        register_module(self)

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'success': self.success, 'records_processed': self.records_processed, 'records_failed': self.records_failed}

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.RESULT_TRACKING, ModuleCapability.ERROR_HANDLING, ModuleCapability.METRICS_COLLECTION, ModuleCapability.REPORTING]

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ['reflective_module', 'datetime', 'typing', 'enum_models']

    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} internal errors occurred')
        if not self.success and (not self.error_message):
            issues.append('Failed sync without error message')
        if self.records_failed > self.records_processed:
            issues.append('More failures than processed records')
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        if not self.success:
            score -= 0.3
        if self.records_failed > 0:
            failure_rate = self.records_failed / max(1, self.records_processed)
            score -= failure_rate * 0.4
        return max(0.0, score)

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Internal errors: {self._errors}')
        if not self.success:
            issues.append('Sync operation failed')
        if self.records_failed > 0:
            issues.append(f'Failed records: {self.records_failed}')
        return issues

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'max_retries': 3, 'timeout_seconds': 300, 'batch_size': 100, 'error_threshold': 0.1}

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            return True
        except Exception as e:
            logger.error(f'Failed to update configuration: {e}')
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'success': self.success, 'records_processed': self.records_processed, 'records_failed': self.records_failed, 'sync_time': self.sync_time.isoformat(), 'success_rate': (self.records_processed - self.records_failed) / max(1, self.records_processed)}

    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0
        self.records_processed = 0
        self.records_failed = 0
        self.success = True
        self.error_message = None

    def set_success(self, success: bool, error_message: str=None) -> None:
        """Set sync success status."""
        try:
            self.success = success
            if not success and error_message:
                self.error_message = error_message
            self._operation_count += 1
        except Exception as e:
            logger.error(f'Failed to set success status: {e}')
            self._errors += 1

    def add_processed_record(self) -> None:
        """Increment processed records count."""
        try:
            self.records_processed += 1
            self._operation_count += 1
        except Exception as e:
            logger.error(f'Failed to add processed record: {e}')
            self._errors += 1

    def add_failed_record(self) -> None:
        """Increment failed records count."""
        try:
            self.records_failed += 1
            self._operation_count += 1
        except Exception as e:
            logger.error(f'Failed to add failed record: {e}')
            self._errors += 1

    def get_result_summary(self) -> Dict[str, Any]:
        """Get sync result summary."""
        return {'success': self.success, 'error_message': self.error_message, 'records_processed': self.records_processed, 'records_failed': self.records_failed, 'success_rate': (self.records_processed - self.records_failed) / max(1, self.records_processed), 'sync_time': self.sync_time.isoformat()}

    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f'Sync result: {operation}')

class FileChangeEvent(ReflectiveModule):
    """
    Manages file change events and tracking.
    
    This class handles file change notifications including
    creation, modification, deletion, and movement events.
    """

    def __init__(self, event_data: Dict[str, Any]=None):
        """Initialize file change event."""
        super().__init__()
        self.module_id = 'file_change_event'
        self.version = '1.0.0'
        self.event_data = event_data or {}
        self.file_path = self.event_data.get('file_path', '')
        change_type_value = self.event_data.get('change_type', ChangeType.MODIFIED)
        self.change_type = change_type_value if isinstance(change_type_value, ChangeType) else ChangeType(change_type_value)
        self.timestamp = datetime.now()
        self.file_size = self.event_data.get('file_size', 0)
        self.checksum = self.event_data.get('checksum', '')
        self._operation_count = 0
        self._errors = 0
        register_module(self)

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat()}

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.EVENT_TRACKING, ModuleCapability.CHANGE_DETECTION, ModuleCapability.METADATA_MANAGEMENT]

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ['reflective_module', 'datetime', 'typing', 'enum_models']

    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} internal errors occurred')
        if not self.file_path:
            issues.append('No file path specified')
        if self.file_size < 0:
            issues.append('Invalid file size')
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        if not self.file_path:
            score -= 0.3
        if self.file_size < 0:
            score -= 0.2
        return max(0.0, score)

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Internal errors: {self._errors}')
        if not self.file_path:
            issues.append('Missing file path')
        if self.file_size < 0:
            issues.append(f'Invalid file size: {self.file_size}')
        return issues

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'max_file_size': 100 * 1024 * 1024, 'supported_extensions': ['.py', '.md', '.json', '.yaml'], 'checksum_algorithm': 'sha256'}

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            return True
        except Exception as e:
            logger.error(f'Failed to update configuration: {e}')
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'file_path': self.file_path, 'file_size': self.file_size, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat()}

    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0

    def get_event_details(self) -> Dict[str, Any]:
        """Get detailed event information."""
        return {'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat(), 'file_size': self.file_size, 'checksum': self.checksum}

    def update_file_path(self, new_path: str) -> bool:
        """Update file path."""
        try:
            self.file_path = new_path
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to update file path: {e}')
            self._errors += 1
            return False

    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f'File change event: {operation}')

def __init__(self, result_data: Dict[str, Any]=None):
    """Initialize sync result."""
    super().__init__()
    self.module_id = 'sync_result'
    self.version = '1.0.0'
    self.result_data = result_data or {}
    self.success = True
    self.error_message = None
    self.sync_time = datetime.now()
    self.records_processed = 0
    self.records_failed = 0
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'success': self.success, 'records_processed': self.records_processed, 'records_failed': self.records_failed}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.RESULT_TRACKING, ModuleCapability.ERROR_HANDLING, ModuleCapability.METRICS_COLLECTION, ModuleCapability.REPORTING]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing', 'enum_models']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.success:
        score -= 0.3
    if self.records_failed > 0:
        failure_rate = self.records_failed / max(1, self.records_processed)
        score -= failure_rate * 0.4
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.success:
        issues.append('Sync operation failed')
    if self.records_failed > 0:
        issues.append(f'Failed records: {self.records_failed}')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_retries': 3, 'timeout_seconds': 300, 'batch_size': 100, 'error_threshold': 0.1}

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'success': self.success, 'records_processed': self.records_processed, 'records_failed': self.records_failed, 'sync_time': self.sync_time.isoformat(), 'success_rate': (self.records_processed - self.records_failed) / max(1, self.records_processed)}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0
    self.records_processed = 0
    self.records_failed = 0
    self.success = True
    self.error_message = None

def set_success(self, success: bool, error_message: str=None) -> None:
    """Set sync success status."""
    try:
        self.success = success
        if not success and error_message:
            self.error_message = error_message
        self._operation_count += 1
    except Exception as e:
        logger.error(f'Failed to set success status: {e}')
        self._errors += 1

def add_failed_record(self) -> None:
    """Increment failed records count."""
    try:
        self.records_failed += 1
        self._operation_count += 1
    except Exception as e:
        logger.error(f'Failed to add failed record: {e}')
        self._errors += 1

def get_result_summary(self) -> Dict[str, Any]:
    """Get sync result summary."""
    return {'success': self.success, 'error_message': self.error_message, 'records_processed': self.records_processed, 'records_failed': self.records_failed, 'success_rate': (self.records_processed - self.records_failed) / max(1, self.records_processed), 'sync_time': self.sync_time.isoformat()}

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Sync result: {operation}')

def __init__(self, event_data: Dict[str, Any]=None):
    """Initialize file change event."""
    super().__init__()
    self.module_id = 'file_change_event'
    self.version = '1.0.0'
    self.event_data = event_data or {}
    self.file_path = self.event_data.get('file_path', '')
    change_type_value = self.event_data.get('change_type', ChangeType.MODIFIED)
    self.change_type = change_type_value if isinstance(change_type_value, ChangeType) else ChangeType(change_type_value)
    self.timestamp = datetime.now()
    self.file_size = self.event_data.get('file_size', 0)
    self.checksum = self.event_data.get('checksum', '')
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat()}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.EVENT_TRACKING, ModuleCapability.CHANGE_DETECTION, ModuleCapability.METADATA_MANAGEMENT]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing', 'enum_models']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.file_path:
        score -= 0.3
    if self.file_size < 0:
        score -= 0.2
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.file_path:
        issues.append('Missing file path')
    if self.file_size < 0:
        issues.append(f'Invalid file size: {self.file_size}')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_file_size': 100 * 1024 * 1024, 'supported_extensions': ['.py', '.md', '.json', '.yaml'], 'checksum_algorithm': 'sha256'}

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'file_path': self.file_path, 'file_size': self.file_size, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat()}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0

def get_event_details(self) -> Dict[str, Any]:
    """Get detailed event information."""
    return {'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat(), 'file_size': self.file_size, 'checksum': self.checksum}

def update_file_path(self, new_path: str) -> bool:
    """Update file path."""
    try:
        self.file_path = new_path
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to update file path: {e}')
        self._errors += 1
        return False

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'File change event: {operation}')
