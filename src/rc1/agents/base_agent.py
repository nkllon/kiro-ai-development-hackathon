"""
Base Agent - Common functionality for all agents
"""

import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class AgentResult:
    """Result of agent execution"""
    agent_name: str
    success: bool
    execution_time_ms: float
    start_time: datetime
    end_time: datetime
    data: Dict[str, Any]
    metrics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class BaseAgent(ABC):
    """Base class for all agents with common functionality"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.data: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    @abstractmethod
    def execute(self) -> AgentResult:
        """Execute the agent's main functionality"""
        pass
    
    async def execute_async(self) -> AgentResult:
        """Execute the agent asynchronously"""
        return self.execute()
    
    def _start_execution(self) -> None:
        """Start execution timing"""
        self.start_time = datetime.now()
        self.data = {}
        self.metrics = {}
        self.errors = []
        self.warnings = []
    
    def _end_execution(self, success: bool = True) -> AgentResult:
        """End execution and create result"""
        self.end_time = datetime.now()
        
        execution_time = 0.0
        if self.start_time:
            execution_time = (self.end_time - self.start_time).total_seconds() * 1000
        
        return AgentResult(
            agent_name=self.name,
            success=success,
            execution_time_ms=execution_time,
            start_time=self.start_time or datetime.now(),
            end_time=self.end_time,
            data=self.data,
            metrics=self.metrics,
            errors=self.errors,
            warnings=self.warnings
        )
    
    def _add_error(self, error: str) -> None:
        """Add an error message"""
        self.errors.append(f"{datetime.now().isoformat()}: {error}")
    
    def _add_warning(self, warning: str) -> None:
        """Add a warning message"""
        self.warnings.append(f"{datetime.now().isoformat()}: {warning}")
    
    def _add_metric(self, key: str, value: Any) -> None:
        """Add a metric"""
        self.metrics[key] = value
    
    def _set_data(self, key: str, value: Any) -> None:
        """Set data value"""
        self.data[key] = value
    
    def discover_files(self, directory: str, patterns: List[str]) -> List[str]:
        """Discover files matching patterns in directory"""
        files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            self._add_error(f"Directory not found: {directory}")
            return files
        
        try:
            for pattern in patterns:
                for file_path in directory_path.rglob(pattern):
                    if file_path.is_file():
                        files.append(str(file_path))
        except Exception as e:
            self._add_error(f"Error discovering files: {e}")
        
        return files
    
    def read_file_safely(self, file_path: str) -> Optional[str]:
        """Safely read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self._add_error(f"Error reading file {file_path}: {e}")
            return None
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get file statistics"""
        try:
            path = Path(file_path)
            stat = path.stat()
            return {
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "extension": path.suffix,
                "is_executable": path.stat().st_mode & 0o111 != 0
            }
        except Exception as e:
            self._add_error(f"Error getting stats for {file_path}: {e}")
            return {}
