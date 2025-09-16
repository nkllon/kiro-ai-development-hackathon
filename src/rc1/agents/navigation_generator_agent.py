"""
Navigation Generator Agent - Generate navigation structure
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentResult


class NavigationGeneratorAgent(BaseAgent):
    """Independent agent for navigation structure generation"""
    
    def __init__(self):
        super().__init__("NavigationGeneratorAgent")
    
    def execute(self) -> AgentResult:
        """Independent execution of navigation generation"""
        self._start_execution()
        
        try:
            # Generate hierarchical navigation structure
            navigation_structure = self._generate_hierarchical_navigation()
            self._set_data("navigation_structure", navigation_structure)
            
            # Create cross-references and indexes
            cross_references = self._create_cross_references(navigation_structure)
            self._set_data("cross_references", cross_references)
            
            # Build navigation maps
            navigation_maps = self._build_navigation_maps(navigation_structure, cross_references)
            self._set_data("navigation_maps", navigation_maps)
            
            # Self-validate navigation completeness
            validation = self._validate_navigation_completeness(navigation_structure)
            self._set_data("validation_result", validation)
            
            self._add_metric("navigation_levels", len(navigation_structure.get("levels", [])))
            self._add_metric("cross_references_created", len(cross_references))
            self._add_metric("navigation_maps_generated", len(navigation_maps))
            
            return self._end_execution(success=True)
            
        except Exception as e:
            self._add_error(f"Critical error in navigation generation: {e}")
            return self._end_execution(success=False)
    
    def _generate_hierarchical_navigation(self) -> Dict[str, Any]:
        """Generate hierarchical navigation structure"""
        # Discover document structure
        documents = self.discover_files(".", ["*.md", "*.txt", "*.py"])
        
        navigation = {
            "root": ".",
            "levels": [],
            "hierarchy": {},
            "breadcrumbs": {}
        }
        
        # Build hierarchy based on directory structure
        hierarchy = {}
        for doc_path in documents:
            path_parts = doc_path.split('/')
            current_level = hierarchy
            
            for i, part in enumerate(path_parts[:-1]):  # Exclude filename
                if part not in current_level:
                    current_level[part] = {"type": "directory", "children": {}, "files": []}
                current_level = current_level[part]["children"]
            
            # Add file to appropriate level
            filename = path_parts[-1]
            if path_parts[:-1]:  # Has directory path
                current_level[filename] = {"type": "file", "path": doc_path}
            else:
                hierarchy[filename] = {"type": "file", "path": doc_path}
        
        navigation["hierarchy"] = hierarchy
        
        # Generate navigation levels
        navigation["levels"] = self._extract_navigation_levels(hierarchy)
        
        return navigation
    
    def _extract_navigation_levels(self, hierarchy: Dict[str, Any], current_level: int = 0) -> List[Dict[str, Any]]:
        """Extract navigation levels from hierarchy"""
        levels = []
        
        if current_level == 0:
            levels.append({
                "level": 0,
                "name": "root",
                "items": list(hierarchy.keys()),
                "type": "root"
            })
        
        for key, value in hierarchy.items():
            if isinstance(value, dict) and value.get("type") == "directory":
                levels.append({
                    "level": current_level + 1,
                    "name": key,
                    "items": list(value["children"].keys()) + value.get("files", []),
                    "type": "directory",
                    "path": key
                })
                
                # Recursively extract child levels
                child_levels = self._extract_navigation_levels(value["children"], current_level + 1)
                levels.extend(child_levels)
        
        return levels
    
    def _create_cross_references(self, navigation_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create cross-references and indexes"""
        cross_references = []
        
        # Create type-based cross-references
        type_refs = self._create_type_cross_references()
        cross_references.extend(type_refs)
        
        # Create topic-based cross-references
        topic_refs = self._create_topic_cross_references()
        cross_references.extend(topic_refs)
        
        # Create dependency cross-references
        dependency_refs = self._create_dependency_cross_references()
        cross_references.extend(dependency_refs)
        
        return cross_references
    
    def _create_type_cross_references(self) -> List[Dict[str, Any]]:
        """Create cross-references by document type"""
        documents = self.discover_files(".", ["*.md", "*.py", "*.yaml", "*.json"])
        
        type_references = {}
        for doc in documents:
            doc_type = doc.split('.')[-1]
            if doc_type not in type_references:
                type_references[doc_type] = []
            type_references[doc_type].append(doc)
        
        cross_refs = []
        for doc_type, files in type_references.items():
            cross_refs.append({
                "type": "document_type",
                "category": doc_type,
                "references": files,
                "count": len(files)
            })
        
        return cross_refs
    
    def _create_topic_cross_references(self) -> List[Dict[str, Any]]:
        """Create cross-references by topic"""
        # Simplified topic detection based on common keywords
        topics = {
            "documentation": ["README", "docs", "guide", "manual"],
            "configuration": ["config", "settings", "yaml", "json"],
            "source_code": ["src", "lib", "main", "core"],
            "testing": ["test", "spec", "unit", "integration"],
            "deployment": ["deploy", "docker", "k8s", "kubernetes"]
        }
        
        cross_refs = []
        for topic, keywords in topics.items():
            matching_files = []
            documents = self.discover_files(".", ["*"])
            
            for doc in documents:
                if any(keyword.lower() in doc.lower() for keyword in keywords):
                    matching_files.append(doc)
            
            if matching_files:
                cross_refs.append({
                    "type": "topic",
                    "category": topic,
                    "references": matching_files,
                    "count": len(matching_files)
                })
        
        return cross_refs
    
    def _create_dependency_cross_references(self) -> List[Dict[str, Any]]:
        """Create cross-references based on dependencies"""
        # Simplified dependency detection
        cross_refs = []
        
        # Find files that reference each other
        documents = self.discover_files(".", ["*.md", "*.py", "*.yaml"])
        
        for doc in documents[:10]:  # Limit for performance
            try:
                content = self.read_file_safely(doc)
                if content:
                    references = self._extract_file_references(content, documents)
                    if references:
                        cross_refs.append({
                            "type": "dependency",
                            "source": doc,
                            "references": references,
                            "count": len(references)
                        })
            except Exception:
                continue
        
        return cross_refs
    
    def _extract_file_references(self, content: str, all_files: List[str]) -> List[str]:
        """Extract file references from content"""
        references = []
        
        # Simple reference detection
        import re
        
        # Look for common reference patterns
        patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown links
            r'["\']([^"\']*\.(?:md|py|yaml|json))["\']',  # File paths
            r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',  # Python imports
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                ref = match[1] if isinstance(match, tuple) else match
                if ref in all_files:
                    references.append(ref)
        
        return list(set(references))  # Remove duplicates
    
    def _build_navigation_maps(self, navigation_structure: Dict[str, Any], cross_references: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build navigation maps"""
        return {
            "hierarchical_map": navigation_structure,
            "cross_reference_map": cross_references,
            "quick_access_map": self._build_quick_access_map(navigation_structure),
            "search_index": self._build_search_index(navigation_structure)
        }
    
    def _build_quick_access_map(self, navigation_structure: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build quick access map"""
        quick_access = {
            "recent": [],
            "frequently_accessed": [],
            "important": []
        }
        
        # Find important files (README, main files, etc.)
        important_patterns = ["README", "main", "index", "setup", "requirements"]
        documents = self.discover_files(".", ["*"])
        
        for pattern in important_patterns:
            for doc in documents:
                if pattern.lower() in doc.lower():
                    quick_access["important"].append(doc)
        
        return quick_access
    
    def _build_search_index(self, navigation_structure: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build search index"""
        search_index = {}
        
        documents = self.discover_files(".", ["*.md", "*.txt", "*.py"])
        
        for doc in documents[:20]:  # Limit for performance
            try:
                content = self.read_file_safely(doc)
                if content:
                    # Extract keywords (simple approach)
                    words = content.lower().split()
                    keywords = [word for word in words if len(word) > 3 and word.isalpha()]
                    
                    for keyword in keywords:
                        if keyword not in search_index:
                            search_index[keyword] = []
                        if doc not in search_index[keyword]:
                            search_index[keyword].append(doc)
            except Exception:
                continue
        
        return search_index
    
    def _validate_navigation_completeness(self, navigation_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Validate navigation completeness"""
        validation = {
            "is_complete": True,
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Check if hierarchy was built
        hierarchy = navigation_structure.get("hierarchy", {})
        if not hierarchy:
            validation["issues"].append("No hierarchy structure generated")
            validation["is_complete"] = False
        
        # Check if navigation levels exist
        levels = navigation_structure.get("levels", [])
        if not levels:
            validation["issues"].append("No navigation levels generated")
            validation["is_complete"] = False
        
        # Check for minimum required files
        documents = self.discover_files(".", ["*"])
        if len(documents) < 5:
            validation["issues"].append("Very few documents found for navigation")
            validation["recommendations"].append("Consider expanding search patterns")
        
        # Calculate validation score
        score = 0.0
        score += 0.4 if hierarchy else 0.0
        score += 0.3 if levels else 0.0
        score += 0.2 if len(documents) >= 5 else 0.0
        score += 0.1 if validation["is_complete"] else 0.0
        
        validation["score"] = round(score, 3)
        
        return validation
