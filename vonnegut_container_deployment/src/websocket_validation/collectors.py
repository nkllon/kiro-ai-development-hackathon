"""
EvidenceCollector - Systematic collection and storage of all validation evidence.
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import uuid

from .models import Evidence, EvidenceType, TestResult
from .config import ValidationConfig
from .utils import get_logger


class EvidenceCollector:
    """
    Systematic collection and storage of all validation evidence.
    
    Collects timestamped evidence from all tests, stores logs, screenshots,
    and response data, maintains evidence integrity and traceability,
    and provides evidence retrieval and analysis.
    """
    
    def __init__(self, config: ValidationConfig):
        """
        Initialize EvidenceCollector.
        
        Args:
            config: Validation configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.evidence_store: Dict[str, Evidence] = {}
        self.collection_start: Optional[datetime] = None
        self.collection_end: Optional[datetime] = None
        
        # Ensure evidence directory exists
        self.evidence_dir = Path(config.evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different evidence types
        self._create_evidence_subdirectories()
        
        self.logger.info(f"EvidenceCollector initialized with directory: {self.evidence_dir}")
    
    def _create_evidence_subdirectories(self) -> None:
        """Create subdirectories for different types of evidence."""
        subdirs = [
            "logs",
            "network_captures", 
            "screenshots",
            "config_snapshots",
            "test_outputs",
            "http_responses",
            "websocket_traces",
            "code_analysis",
            "performance_metrics"
        ]
        
        for subdir in subdirs:
            (self.evidence_dir / subdir).mkdir(exist_ok=True)
    
    def collect_test_evidence(self, test_result: TestResult) -> Evidence:
        """
        Collect evidence from a test result.
        
        Args:
            test_result: Test result to collect evidence from
            
        Returns:
            Evidence: Created evidence record
        """
        if self.collection_start is None:
            self.collection_start = datetime.utcnow()
        
        # Create evidence from test result
        evidence_data = {
            "test_id": test_result.test_id,
            "test_name": test_result.test_name,
            "test_category": test_result.test_category,
            "status": test_result.status.value,
            "execution_time": test_result.execution_time,
            "metrics": test_result.metrics,
            "error_details": test_result.error_details,
            "assertions_passed": test_result.assertions_passed,
            "assertions_failed": test_result.assertions_failed
        }
        
        evidence = Evidence(
            evidence_type=EvidenceType.TEST_OUTPUT,
            source_test=test_result.test_name,
            data=evidence_data,
            metadata={
                "test_category": test_result.test_category,
                "test_status": test_result.status.value,
                "collection_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Store evidence
        self._store_evidence(evidence)
        
        # Add evidence ID to test result
        test_result.evidence_ids.append(evidence.evidence_id)
        
        self.logger.info(f"Collected test evidence: {evidence.evidence_id} for test {test_result.test_name}")
        
        return evidence
    
    def store_network_capture(self, capture_data: bytes, context: Dict[str, Any]) -> str:
        """
        Store network capture data.
        
        Args:
            capture_data: Raw network capture data
            context: Additional context information
            
        Returns:
            str: Evidence ID
        """
        evidence = Evidence(
            evidence_type=EvidenceType.NETWORK_CAPTURE,
            source_test=context.get("source_test", "unknown"),
            data=capture_data,
            metadata={
                "capture_size": len(capture_data),
                "capture_format": context.get("format", "raw"),
                "endpoint": context.get("endpoint", ""),
                "protocol": context.get("protocol", ""),
                "collection_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        self._store_evidence(evidence)
        
        self.logger.info(f"Stored network capture: {evidence.evidence_id} ({len(capture_data)} bytes)")
        
        return evidence.evidence_id
    
    def take_system_screenshot(self, context: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Take and store a system screenshot.
        
        Args:
            context: Context description for the screenshot
            metadata: Optional additional metadata
            
        Returns:
            str: Evidence ID
        """
        # Note: This is a placeholder implementation
        # In a real implementation, this would capture an actual screenshot
        screenshot_data = f"Screenshot placeholder for context: {context}".encode('utf-8')
        
        evidence = Evidence(
            evidence_type=EvidenceType.SCREENSHOT,
            source_test=metadata.get("source_test", "system") if metadata else "system",
            data=screenshot_data,
            metadata={
                "context": context,
                "screenshot_format": "placeholder",
                "collection_timestamp": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
        
        self._store_evidence(evidence)
        
        self.logger.info(f"Captured screenshot: {evidence.evidence_id} for context: {context}")
        
        return evidence.evidence_id
    
    def snapshot_configuration(self, config_type: str, config_data: Union[str, Dict]) -> str:
        """
        Create a snapshot of configuration data.
        
        Args:
            config_type: Type of configuration (e.g., "cloudflare", "fastapi")
            config_data: Configuration data to snapshot
            
        Returns:
            str: Evidence ID
        """
        evidence = Evidence(
            evidence_type=EvidenceType.CONFIG_SNAPSHOT,
            source_test=f"{config_type}_configuration",
            data=config_data,
            metadata={
                "config_type": config_type,
                "snapshot_timestamp": datetime.utcnow().isoformat(),
                "data_type": type(config_data).__name__
            }
        )
        
        self._store_evidence(evidence)
        
        self.logger.info(f"Created configuration snapshot: {evidence.evidence_id} for {config_type}")
        
        return evidence.evidence_id
    
    def store_http_response(
        self, 
        url: str, 
        method: str, 
        status_code: int,
        headers: Dict[str, str],
        body: str,
        response_time: float,
        source_test: str
    ) -> str:
        """
        Store HTTP response data.
        
        Args:
            url: Request URL
            method: HTTP method
            status_code: Response status code
            headers: Response headers
            body: Response body
            response_time: Response time in seconds
            source_test: Test that generated this response
            
        Returns:
            str: Evidence ID
        """
        response_data = {
            "url": url,
            "method": method,
            "status_code": status_code,
            "headers": headers,
            "body": body,
            "response_time": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        evidence = Evidence(
            evidence_type=EvidenceType.HTTP_RESPONSE,
            source_test=source_test,
            data=response_data,
            metadata={
                "url": url,
                "method": method,
                "status_code": status_code,
                "response_size": len(body),
                "response_time": response_time
            }
        )
        
        self._store_evidence(evidence)
        
        self.logger.info(f"Stored HTTP response: {evidence.evidence_id} for {method} {url}")
        
        return evidence.evidence_id
    
    def store_websocket_trace(
        self,
        endpoint: str,
        messages: List[Dict[str, Any]],
        connection_info: Dict[str, Any],
        source_test: str
    ) -> str:
        """
        Store WebSocket connection trace.
        
        Args:
            endpoint: WebSocket endpoint URL
            messages: List of messages exchanged
            connection_info: Connection metadata
            source_test: Test that generated this trace
            
        Returns:
            str: Evidence ID
        """
        trace_data = {
            "endpoint": endpoint,
            "messages": messages,
            "connection_info": connection_info,
            "message_count": len(messages),
            "trace_timestamp": datetime.utcnow().isoformat()
        }
        
        evidence = Evidence(
            evidence_type=EvidenceType.WEBSOCKET_TRACE,
            source_test=source_test,
            data=trace_data,
            metadata={
                "endpoint": endpoint,
                "message_count": len(messages),
                "connection_duration": connection_info.get("duration", 0),
                "connection_status": connection_info.get("status", "unknown")
            }
        )
        
        self._store_evidence(evidence)
        
        self.logger.info(f"Stored WebSocket trace: {evidence.evidence_id} for {endpoint}")
        
        return evidence.evidence_id
    
    def store_log_file(self, log_content: str, log_type: str, source_test: str) -> str:
        """
        Store log file content.
        
        Args:
            log_content: Log file content
            log_type: Type of log (e.g., "application", "system", "error")
            source_test: Test that generated this log
            
        Returns:
            str: Evidence ID
        """
        evidence = Evidence(
            evidence_type=EvidenceType.LOG_FILE,
            source_test=source_test,
            data=log_content,
            metadata={
                "log_type": log_type,
                "log_size": len(log_content),
                "line_count": log_content.count('\n'),
                "collection_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        self._store_evidence(evidence)
        
        self.logger.info(f"Stored log file: {evidence.evidence_id} ({log_type}) for {source_test}")
        
        return evidence.evidence_id
    
    def _store_evidence(self, evidence: Evidence) -> None:
        """
        Store evidence in memory and optionally persist to disk.
        
        Args:
            evidence: Evidence to store
        """
        # Store in memory
        self.evidence_store[evidence.evidence_id] = evidence
        
        # Persist to disk if encryption is enabled
        if self.config.encrypt_evidence:
            self._persist_evidence_encrypted(evidence)
        else:
            self._persist_evidence_plain(evidence)
    
    def _persist_evidence_plain(self, evidence: Evidence) -> None:
        """
        Persist evidence to disk in plain format.
        
        Args:
            evidence: Evidence to persist
        """
        # Determine subdirectory based on evidence type
        subdir_map = {
            EvidenceType.LOG_FILE: "logs",
            EvidenceType.NETWORK_CAPTURE: "network_captures",
            EvidenceType.SCREENSHOT: "screenshots",
            EvidenceType.CONFIG_SNAPSHOT: "config_snapshots",
            EvidenceType.TEST_OUTPUT: "test_outputs",
            EvidenceType.HTTP_RESPONSE: "http_responses",
            EvidenceType.WEBSOCKET_TRACE: "websocket_traces",
            EvidenceType.CODE_ANALYSIS: "code_analysis",
            EvidenceType.PERFORMANCE_METRICS: "performance_metrics"
        }
        
        subdir = subdir_map.get(evidence.evidence_type, "misc")
        evidence_dir = self.evidence_dir / subdir
        
        # Create filename with timestamp and evidence ID
        timestamp = evidence.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{evidence.evidence_id}.json"
        filepath = evidence_dir / filename
        
        # Prepare data for serialization
        evidence_dict = {
            "evidence_id": evidence.evidence_id,
            "timestamp": evidence.timestamp.isoformat(),
            "evidence_type": evidence.evidence_type.value,
            "source_test": evidence.source_test,
            "metadata": evidence.metadata,
            "integrity_hash": evidence.integrity_hash,
            "data": self._serialize_evidence_data(evidence.data)
        }
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(evidence_dict, f, indent=2, ensure_ascii=False)
            
            evidence.file_path = str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to persist evidence {evidence.evidence_id}: {e}")
    
    def _persist_evidence_encrypted(self, evidence: Evidence) -> None:
        """
        Persist evidence to disk in encrypted format.
        
        Args:
            evidence: Evidence to persist
        """
        # Placeholder for encryption implementation
        # In a real implementation, this would encrypt the evidence data
        self.logger.warning("Evidence encryption not implemented, storing in plain format")
        self._persist_evidence_plain(evidence)
    
    def _serialize_evidence_data(self, data: Union[str, bytes, Dict]) -> Any:
        """
        Serialize evidence data for JSON storage.
        
        Args:
            data: Data to serialize
            
        Returns:
            Serializable data
        """
        if isinstance(data, bytes):
            # Convert bytes to base64 string for JSON serialization
            import base64
            return {
                "_type": "bytes",
                "_data": base64.b64encode(data).decode('ascii')
            }
        elif isinstance(data, dict):
            return data
        elif isinstance(data, str):
            return data
        else:
            return str(data)
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """
        Retrieve evidence by ID.
        
        Args:
            evidence_id: Evidence identifier
            
        Returns:
            Evidence if found, None otherwise
        """
        return self.evidence_store.get(evidence_id)
    
    def get_evidence_by_test(self, test_name: str) -> List[Evidence]:
        """
        Get all evidence for a specific test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            List of evidence for the test
        """
        return [
            evidence for evidence in self.evidence_store.values()
            if evidence.source_test == test_name
        ]
    
    def get_evidence_by_type(self, evidence_type: EvidenceType) -> List[Evidence]:
        """
        Get all evidence of a specific type.
        
        Args:
            evidence_type: Type of evidence
            
        Returns:
            List of evidence of the specified type
        """
        return [
            evidence for evidence in self.evidence_store.values()
            if evidence.evidence_type == evidence_type
        ]
    
    def verify_evidence_integrity(self, evidence_id: str) -> bool:
        """
        Verify the integrity of stored evidence.
        
        Args:
            evidence_id: Evidence identifier
            
        Returns:
            True if integrity is verified, False otherwise
        """
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return False
        
        # Recalculate hash and compare
        if isinstance(evidence.data, str):
            data_bytes = evidence.data.encode('utf-8')
        elif isinstance(evidence.data, dict):
            data_bytes = json.dumps(evidence.data, sort_keys=True).encode('utf-8')
        else:
            data_bytes = evidence.data
        
        calculated_hash = hashlib.sha256(data_bytes).hexdigest()
        
        return calculated_hash == evidence.integrity_hash
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of collected evidence.
        
        Returns:
            Dict containing evidence collection summary
        """
        self.collection_end = datetime.utcnow()
        
        # Count evidence by type
        evidence_by_type = {}
        for evidence in self.evidence_store.values():
            evidence_type = evidence.evidence_type.value
            evidence_by_type[evidence_type] = evidence_by_type.get(evidence_type, 0) + 1
        
        # Count evidence by test
        evidence_by_test = {}
        for evidence in self.evidence_store.values():
            test_name = evidence.source_test
            evidence_by_test[test_name] = evidence_by_test.get(test_name, 0) + 1
        
        # Calculate total size
        total_size = 0
        for evidence in self.evidence_store.values():
            if isinstance(evidence.data, str):
                total_size += len(evidence.data.encode('utf-8'))
            elif isinstance(evidence.data, bytes):
                total_size += len(evidence.data)
            elif isinstance(evidence.data, dict):
                total_size += len(json.dumps(evidence.data).encode('utf-8'))
        
        # Verify integrity of all evidence
        integrity_verified = all(
            self.verify_evidence_integrity(evidence_id)
            for evidence_id in self.evidence_store.keys()
        )
        
        return {
            "total_items": len(self.evidence_store),
            "by_type": evidence_by_type,
            "by_test": evidence_by_test,
            "total_size": total_size,
            "integrity_verified": integrity_verified,
            "collection_start": self.collection_start,
            "collection_end": self.collection_end,
            "collection_duration": (
                (self.collection_end - self.collection_start).total_seconds()
                if self.collection_start and self.collection_end else 0
            )
        }
    
    def cleanup_old_evidence(self, retention_days: Optional[int] = None) -> int:
        """
        Clean up old evidence files based on retention policy.
        
        Args:
            retention_days: Number of days to retain evidence (uses config default if None)
            
        Returns:
            Number of evidence items cleaned up
        """
        retention_days = retention_days or self.config.evidence_retention_days
        cutoff_date = datetime.utcnow().timestamp() - (retention_days * 24 * 60 * 60)
        
        cleaned_count = 0
        evidence_to_remove = []
        
        for evidence_id, evidence in self.evidence_store.items():
            if evidence.timestamp.timestamp() < cutoff_date:
                evidence_to_remove.append(evidence_id)
                
                # Remove file if it exists
                if evidence.file_path and os.path.exists(evidence.file_path):
                    try:
                        os.remove(evidence.file_path)
                        cleaned_count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to remove evidence file {evidence.file_path}: {e}")
        
        # Remove from memory store
        for evidence_id in evidence_to_remove:
            del self.evidence_store[evidence_id]
        
        self.logger.info(f"Cleaned up {cleaned_count} old evidence items")
        
        return cleaned_count