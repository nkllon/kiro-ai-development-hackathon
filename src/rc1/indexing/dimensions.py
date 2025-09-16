"""
Dimension Classes - 20+ dimensional indexing system
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class DimensionValue:
    """Value within a dimension"""
    key: str
    value: Any
    metadata: Dict[str, Any]
    confidence: float = 1.0


class BaseDimension(ABC):
    """Base class for all dimensions"""
    
    def __init__(self, name: str):
        self.name = name
        self.values: Dict[str, DimensionValue] = {}
    
    @abstractmethod
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze content and extract dimension values"""
        pass
    
    def add_value(self, key: str, value: Any, metadata: Dict[str, Any] = None, confidence: float = 1.0):
        """Add a value to this dimension"""
        self.values[key] = DimensionValue(
            key=key,
            value=value,
            metadata=metadata or {},
            confidence=confidence
        )
    
    def get_values(self) -> List[DimensionValue]:
        """Get all values in this dimension"""
        return list(self.values.values())


class TemporalDimension(BaseDimension):
    """Temporal dimension - time-based analysis"""
    
    def __init__(self):
        super().__init__("temporal")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze temporal aspects"""
        values = []
        
        # Extract timestamps from metadata
        if 'modified_time' in metadata:
            values.append(DimensionValue("modified_time", metadata['modified_time'], metadata))
        
        if 'created_time' in metadata:
            values.append(DimensionValue("created_time", metadata['created_time'], metadata))
        
        # Analyze temporal patterns in content
        import re
        time_patterns = re.findall(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', content)
        for pattern in time_patterns:
            values.append(DimensionValue("content_date", pattern, {"source": "content_regex"}))
        
        return values


class SpatialDimension(BaseDimension):
    """Spatial dimension - location and scope analysis"""
    
    def __init__(self):
        super().__init__("spatial")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze spatial aspects"""
        values = []
        
        # Directory-based spatial analysis
        if 'directory' in metadata:
            path_parts = metadata['directory'].split('/')
            for i, part in enumerate(path_parts):
                values.append(DimensionValue(f"level_{i}", part, {"depth": i}))
        
        # File scope analysis
        if 'relative_depth' in metadata:
            depth = metadata['relative_depth']
            if depth == 0:
                scope = "root"
            elif depth <= 2:
                scope = "shallow"
            elif depth <= 5:
                scope = "medium"
            else:
                scope = "deep"
            values.append(DimensionValue("scope", scope, {"depth": depth}))
        
        return values


class SemanticDimension(BaseDimension):
    """Semantic dimension - meaning and context analysis"""
    
    def __init__(self):
        super().__init__("semantic")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze semantic aspects"""
        values = []
        
        # Content type analysis
        if 'type' in metadata:
            values.append(DimensionValue("document_type", metadata['type'], metadata))
        
        # Topic extraction (simplified)
        topics = self._extract_topics(content)
        for topic in topics:
            values.append(DimensionValue("topic", topic, {"source": "content_analysis"}))
        
        # Language analysis
        language = self._detect_language(content)
        values.append(DimensionValue("language", language, {"confidence": 0.8}))
        
        return values
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        topics = []
        
        # Simple keyword-based topic extraction
        topic_keywords = {
            "documentation": ["readme", "docs", "guide", "manual", "tutorial"],
            "configuration": ["config", "settings", "yaml", "json", "env"],
            "source_code": ["def ", "class ", "function", "import", "export"],
            "testing": ["test", "spec", "unit", "integration", "fixture"],
            "deployment": ["deploy", "docker", "k8s", "kubernetes", "ci/cd"]
        }
        
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _detect_language(self, content: str) -> str:
        """Detect programming language"""
        if 'def ' in content or 'import ' in content:
            return "python"
        elif 'function ' in content or 'const ' in content:
            return "javascript"
        elif 'class ' in content and '{' in content:
            return "java"
        elif '#include' in content:
            return "c/c++"
        else:
            return "text"


class StructuralDimension(BaseDimension):
    """Structural dimension - hierarchy and organization analysis"""
    
    def __init__(self):
        super().__init__("structural")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze structural aspects"""
        values = []
        
        # File structure analysis
        if 'path' in metadata:
            path_parts = metadata['path'].split('/')
            values.append(DimensionValue("depth", len(path_parts) - 1, {"path": metadata['path']}))
        
        # Content structure
        lines = content.split('\n')
        values.append(DimensionValue("line_count", len(lines), {"content_length": len(content)}))
        
        # Header structure (for markdown)
        if '#' in content:
            header_count = content.count('#')
            values.append(DimensionValue("header_count", header_count, {"type": "markdown"}))
        
        # Code structure
        if 'def ' in content:
            function_count = content.count('def ')
            values.append(DimensionValue("function_count", function_count, {"type": "python"}))
        
        return values


class QualityDimension(BaseDimension):
    """Quality dimension - quality metrics analysis"""
    
    def __init__(self):
        super().__init__("quality")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze quality aspects"""
        values = []
        
        # Size-based quality indicators
        if 'size_bytes' in metadata:
            size = metadata['size_bytes']
            if size < 1024:
                quality_level = "small"
            elif size < 10240:
                quality_level = "medium"
            else:
                quality_level = "large"
            values.append(DimensionValue("size_category", quality_level, {"size_bytes": size}))
        
        # Content quality indicators
        if len(content) > 100:
            values.append(DimensionValue("substantial_content", True, {"content_length": len(content)}))
        
        # Documentation quality
        doc_indicators = ['"""', "'''", '#', '//', '/*']
        doc_count = sum(content.count(indicator) for indicator in doc_indicators)
        values.append(DimensionValue("documentation_level", doc_count, {"indicators_found": doc_count}))
        
        return values


class SecurityDimension(BaseDimension):
    """Security dimension - security-related analysis"""
    
    def __init__(self):
        super().__init__("security")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze security aspects"""
        values = []
        
        # Security-sensitive keywords
        security_keywords = ['password', 'secret', 'key', 'token', 'auth', 'permission']
        security_count = sum(1 for keyword in security_keywords if keyword.lower() in content.lower())
        
        if security_count > 0:
            values.append(DimensionValue("security_sensitive", True, {"keyword_count": security_count}))
        
        # File extension security
        if 'extension' in metadata:
            ext = metadata['extension']
            if ext in ['.py', '.js', '.sh']:
                values.append(DimensionValue("executable", True, {"extension": ext}))
        
        return values


class PerformanceDimension(BaseDimension):
    """Performance dimension - performance-related analysis"""
    
    def __init__(self):
        super().__init__("performance")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze performance aspects"""
        values = []
        
        # File size performance impact
        if 'size_bytes' in metadata:
            size = metadata['size_bytes']
            if size > 102400:  # > 100KB
                values.append(DimensionValue("large_file", True, {"size_bytes": size}))
        
        # Performance-related keywords
        perf_keywords = ['performance', 'optimize', 'cache', 'async', 'parallel']
        perf_count = sum(1 for keyword in perf_keywords if keyword.lower() in content.lower())
        
        if perf_count > 0:
            values.append(DimensionValue("performance_related", True, {"keyword_count": perf_count}))
        
        return values


class DependencyDimension(BaseDimension):
    """Dependency dimension - dependency analysis"""
    
    def __init__(self):
        super().__init__("dependency")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze dependency aspects"""
        values = []
        
        # Import/require statements
        import re
        
        # Python imports
        python_imports = re.findall(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content)
        if python_imports:
            values.append(DimensionValue("python_dependencies", len(python_imports), {"imports": python_imports}))
        
        # JavaScript imports
        js_imports = re.findall(r'(?:import|require)\s*\(\s*["\']([^"\']+)["\']', content)
        if js_imports:
            values.append(DimensionValue("javascript_dependencies", len(js_imports), {"imports": js_imports}))
        
        return values


class ArchitectureDimension(BaseDimension):
    """Architecture dimension - architectural patterns analysis"""
    
    def __init__(self):
        super().__init__("architecture")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze architectural aspects"""
        values = []
        
        # Architectural patterns
        patterns = {
            "mvc": ["controller", "model", "view"],
            "microservices": ["service", "api", "endpoint"],
            "event_driven": ["event", "listener", "publish", "subscribe"],
            "layered": ["layer", "tier", "abstraction"]
        }
        
        content_lower = content.lower()
        for pattern, keywords in patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                values.append(DimensionValue("architectural_pattern", pattern, {"confidence": 0.7}))
        
        return values


class TechnologyDimension(BaseDimension):
    """Technology dimension - technology stack analysis"""
    
    def __init__(self):
        super().__init__("technology")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze technology aspects"""
        values = []
        
        # Technology detection based on content and metadata
        if 'extension' in metadata:
            ext = metadata['extension']
            tech_mapping = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.go': 'go',
                '.rs': 'rust',
                '.yaml': 'yaml',
                '.json': 'json'
            }
            
            if ext in tech_mapping:
                values.append(DimensionValue("technology", tech_mapping[ext], {"extension": ext}))
        
        return values


class StakeholderDimension(BaseDimension):
    """Stakeholder dimension - stakeholder analysis"""
    
    def __init__(self):
        super().__init__("stakeholder")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze stakeholder aspects"""
        values = []
        
        # Audience detection
        audience_keywords = {
            "developer": ["api", "code", "function", "class", "import"],
            "user": ["usage", "example", "tutorial", "guide"],
            "admin": ["config", "deploy", "setup", "install"],
            "business": ["requirement", "feature", "specification"]
        }
        
        content_lower = content.lower()
        for audience, keywords in audience_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                values.append(DimensionValue("target_audience", audience, {"confidence": 0.6}))
        
        return values


class ProcessDimension(BaseDimension):
    """Process dimension - process and workflow analysis"""
    
    def __init__(self):
        super().__init__("process")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze process aspects"""
        values = []
        
        # Process-related keywords
        process_keywords = {
            "development": ["develop", "code", "implement", "create"],
            "testing": ["test", "spec", "verify", "validate"],
            "deployment": ["deploy", "release", "publish", "build"],
            "maintenance": ["maintain", "update", "fix", "refactor"]
        }
        
        content_lower = content.lower()
        for process, keywords in process_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                values.append(DimensionValue("process_type", process, {"confidence": 0.6}))
        
        return values


class LifecycleDimension(BaseDimension):
    """Lifecycle dimension - lifecycle stage analysis"""
    
    def __init__(self):
        super().__init__("lifecycle")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze lifecycle aspects"""
        values = []
        
        # Lifecycle stage indicators
        lifecycle_indicators = {
            "planning": ["plan", "design", "specification", "requirement"],
            "development": ["develop", "implement", "create", "build"],
            "testing": ["test", "debug", "verify", "validate"],
            "deployment": ["deploy", "release", "production", "live"],
            "maintenance": ["maintain", "support", "update", "fix"]
        }
        
        content_lower = content.lower()
        for stage, indicators in lifecycle_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                values.append(DimensionValue("lifecycle_stage", stage, {"confidence": 0.6}))
        
        return values


class GovernanceDimension(BaseDimension):
    """Governance dimension - governance and compliance analysis"""
    
    def __init__(self):
        super().__init__("governance")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze governance aspects"""
        values = []
        
        # Governance-related keywords
        governance_keywords = {
            "compliance": ["compliance", "regulation", "standard", "policy"],
            "security": ["security", "audit", "access", "permission"],
            "quality": ["quality", "standard", "best_practice", "guideline"]
        }
        
        content_lower = content.lower()
        for governance_type, keywords in governance_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                values.append(DimensionValue("governance_type", governance_type, {"confidence": 0.6}))
        
        return values


class KnowledgeDimension(BaseDimension):
    """Knowledge dimension - knowledge management analysis"""
    
    def __init__(self):
        super().__init__("knowledge")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze knowledge aspects"""
        values = []
        
        # Knowledge type indicators
        knowledge_types = {
            "documentation": ["documentation", "guide", "manual", "tutorial"],
            "code": ["code", "implementation", "algorithm", "function"],
            "configuration": ["config", "setting", "parameter", "option"],
            "test": ["test", "specification", "validation", "verification"]
        }
        
        content_lower = content.lower()
        for knowledge_type, indicators in knowledge_types.items():
            if any(indicator in content_lower for indicator in indicators):
                values.append(DimensionValue("knowledge_type", knowledge_type, {"confidence": 0.7}))
        
        return values


class MaintenanceDimension(BaseDimension):
    """Maintenance dimension - maintenance requirements analysis"""
    
    def __init__(self):
        super().__init__("maintenance")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze maintenance aspects"""
        values = []
        
        # Maintenance indicators
        maintenance_indicators = {
            "high": ["todo", "fixme", "hack", "temporary", "workaround"],
            "medium": ["review", "optimize", "improve", "enhance"],
            "low": ["stable", "production", "release", "final"]
        }
        
        content_lower = content.lower()
        for maintenance_level, indicators in maintenance_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                values.append(DimensionValue("maintenance_level", maintenance_level, {"confidence": 0.7}))
        
        return values


class DocumentTypeDimension(BaseDimension):
    """Document type dimension - document classification analysis"""
    
    def __init__(self):
        super().__init__("document_type")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze document type aspects"""
        values = []
        
        # Document type classification
        if 'type' in metadata:
            values.append(DimensionValue("primary_type", metadata['type'], metadata))
        
        # Additional type classification
        doc_types = {
            "readme": ["readme", "getting started", "quick start"],
            "api_doc": ["api", "endpoint", "method", "parameter"],
            "tutorial": ["tutorial", "how to", "step by step", "example"],
            "reference": ["reference", "documentation", "specification"]
        }
        
        content_lower = content.lower()
        for doc_type, indicators in doc_types.items():
            if any(indicator in content_lower for indicator in indicators):
                values.append(DimensionValue("document_category", doc_type, {"confidence": 0.6}))
        
        return values


class ComplexityDimension(BaseDimension):
    """Complexity dimension - complexity analysis"""
    
    def __init__(self):
        super().__init__("complexity")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze complexity aspects"""
        values = []
        
        # Size-based complexity
        if 'size_bytes' in metadata:
            size = metadata['size_bytes']
            if size < 1024:
                complexity = "simple"
            elif size < 10240:
                complexity = "moderate"
            else:
                complexity = "complex"
            values.append(DimensionValue("size_complexity", complexity, {"size_bytes": size}))
        
        # Content complexity
        lines = content.split('\n')
        if len(lines) > 100:
            values.append(DimensionValue("content_complexity", "complex", {"line_count": len(lines)}))
        elif len(lines) > 20:
            values.append(DimensionValue("content_complexity", "moderate", {"line_count": len(lines)}))
        else:
            values.append(DimensionValue("content_complexity", "simple", {"line_count": len(lines)}))
        
        return values


class AudienceDimension(BaseDimension):
    """Audience dimension - target audience analysis"""
    
    def __init__(self):
        super().__init__("audience")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze audience aspects"""
        values = []
        
        # Audience detection based on content and path
        audience_indicators = {
            "public": ["public", "open", "community", "general"],
            "developer": ["developer", "api", "code", "technical"],
            "admin": ["admin", "configuration", "deployment", "management"],
            "expert": ["expert", "advanced", "professional", "enterprise"]
        }
        
        content_lower = content.lower()
        path_lower = metadata.get('path', '').lower()
        
        for audience, indicators in audience_indicators.items():
            if any(indicator in content_lower or indicator in path_lower for indicator in indicators):
                values.append(DimensionValue("target_audience", audience, {"confidence": 0.6}))
        
        return values


class UrgencyDimension(BaseDimension):
    """Urgency dimension - urgency and priority analysis"""
    
    def __init__(self):
        super().__init__("urgency")
    
    def analyze(self, content: str, metadata: Dict[str, Any]) -> List[DimensionValue]:
        """Analyze urgency aspects"""
        values = []
        
        # Urgency indicators
        urgency_indicators = {
            "critical": ["critical", "urgent", "emergency", "asap", "immediately"],
            "high": ["important", "priority", "soon", "quickly"],
            "medium": ["normal", "standard", "regular"],
            "low": ["optional", "nice to have", "future", "later"]
        }
        
        content_lower = content.lower()
        for urgency, indicators in urgency_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                values.append(DimensionValue("urgency_level", urgency, {"confidence": 0.7}))
        
        return values
