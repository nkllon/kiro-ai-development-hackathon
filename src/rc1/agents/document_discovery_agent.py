"""
Document Discovery Agent - Discover and catalog all documents
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from .base_agent import BaseAgent, AgentResult


class DocumentDiscoveryAgent(BaseAgent):
    """Independent agent for document discovery and cataloging"""
    
    def __init__(self):
        super().__init__("DocumentDiscoveryAgent")
        self.document_extensions = [
            '*.md', '*.txt', '*.rst', '*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.h',
            '*.yaml', '*.yml', '*.json', '*.xml', '*.html', '*.css', '*.scss', '*.less',
            '*.sh', '*.bash', '*.zsh', '*.fish', '*.ps1', '*.bat',
            '*.sql', '*.r', '*.go', '*.rs', '*.php', '*.rb', '*.pl', '*.lua',
            '*.dockerfile', '*.Dockerfile', '*.makefile', '*.Makefile',
            '*.pdf', '*.doc', '*.docx', '*.ppt', '*.pptx'
        ]
    
    def execute(self) -> AgentResult:
        """Independent execution of document discovery"""
        self._start_execution()
        
        try:
            # Scan repository for all document types
            self._add_metric("scan_start_time", self.start_time.isoformat())
            
            # Discover all documents
            documents = self._discover_all_documents()
            self._set_data("total_documents", len(documents))
            self._add_metric("documents_found", len(documents))
            
            # Extract metadata for each document
            document_registry = self._extract_document_metadata(documents)
            self._set_data("document_registry", document_registry)
            
            # Analyze document purpose and category
            categorized_documents = self._categorize_documents(document_registry)
            self._set_data("categorized_documents", categorized_documents)
            
            # Detect document dependencies and relationships
            dependencies = self._detect_document_dependencies(document_registry)
            self._set_data("document_dependencies", dependencies)
            
            # Generate document registry JSON
            registry_json = self._generate_document_registry_json(document_registry, categorized_documents, dependencies)
            self._set_data("registry_json", registry_json)
            
            # Self-validate completeness and accuracy
            validation_result = self._validate_discovery_completeness(document_registry)
            self._set_data("validation_result", validation_result)
            
            # Report success/failure with metrics
            self._add_metric("discovery_success", validation_result.get("is_complete", False))
            self._add_metric("validation_score", validation_result.get("score", 0.0))
            
            return self._end_execution(success=True)
            
        except Exception as e:
            self._add_error(f"Critical error in document discovery: {e}")
            return self._end_execution(success=False)
    
    def _discover_all_documents(self) -> List[str]:
        """Scan repository for all document types"""
        documents = []
        
        # Start from current directory
        root_dir = "."
        
        try:
            for extension in self.document_extensions:
                pattern = f"**/{extension}"
                for file_path in Path(root_dir).glob(pattern):
                    if file_path.is_file():
                        # Skip certain directories
                        if self._should_skip_directory(file_path):
                            continue
                        documents.append(str(file_path))
            
            self._add_metric("extensions_scanned", len(self.document_extensions))
            
        except Exception as e:
            self._add_error(f"Error during document discovery: {e}")
        
        return documents
    
    def _should_skip_directory(self, file_path: Path) -> bool:
        """Check if directory should be skipped"""
        skip_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', 'env', '.env', 'build', 'dist', 
            'target', '.idea', '.vscode', '.DS_Store'
        }
        
        for part in file_path.parts:
            if part in skip_dirs or part.startswith('.'):
                return True
        return False
    
    def _extract_document_metadata(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Extract metadata for each document"""
        registry = []
        
        for doc_path in documents:
            try:
                file_stats = self.get_file_stats(doc_path)
                
                # Get content preview
                content_preview = self._get_content_preview(doc_path)
                
                # Determine document type
                doc_type = self._determine_document_type(doc_path)
                
                metadata = {
                    "path": doc_path,
                    "name": Path(doc_path).name,
                    "extension": Path(doc_path).suffix,
                    "type": doc_type,
                    "size_bytes": file_stats.get("size_bytes", 0),
                    "modified_time": file_stats.get("modified_time", ""),
                    "created_time": file_stats.get("created_time", ""),
                    "content_preview": content_preview,
                    "line_count": self._count_lines(doc_path),
                    "directory": str(Path(doc_path).parent),
                    "relative_depth": len(Path(doc_path).parts) - 1
                }
                
                registry.append(metadata)
                
            except Exception as e:
                self._add_error(f"Error extracting metadata for {doc_path}: {e}")
        
        self._add_metric("metadata_extraction_success", len(registry))
        return registry
    
    def _get_content_preview(self, file_path: str) -> str:
        """Get content preview (first 200 characters)"""
        try:
            content = self.read_file_safely(file_path)
            if content:
                # Clean up content for preview
                preview = content.replace('\n', ' ').replace('\r', ' ').strip()
                return preview[:200] + "..." if len(preview) > 200 else preview
        except Exception:
            pass
        return ""
    
    def _determine_document_type(self, file_path: str) -> str:
        """Determine document type based on extension and content"""
        ext = Path(file_path).suffix.lower()
        
        type_mapping = {
            '.md': 'markdown',
            '.txt': 'text',
            '.rst': 'restructured_text',
            '.py': 'python_code',
            '.js': 'javascript_code',
            '.ts': 'typescript_code',
            '.java': 'java_code',
            '.cpp': 'cpp_code',
            '.c': 'c_code',
            '.h': 'header_file',
            '.yaml': 'yaml_config',
            '.yml': 'yaml_config',
            '.json': 'json_data',
            '.xml': 'xml_data',
            '.html': 'html_document',
            '.css': 'css_stylesheet',
            '.sh': 'shell_script',
            '.sql': 'sql_script',
            '.dockerfile': 'docker_file',
            '.makefile': 'makefile',
            '.pdf': 'pdf_document',
            '.doc': 'word_document',
            '.docx': 'word_document'
        }
        
        return type_mapping.get(ext, 'unknown')
    
    def _count_lines(self, file_path: str) -> int:
        """Count lines in file"""
        try:
            content = self.read_file_safely(file_path)
            if content:
                return len(content.splitlines())
        except Exception:
            pass
        return 0
    
    def _categorize_documents(self, document_registry: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze document purpose and category"""
        categories = {
            "documentation": [],
            "source_code": [],
            "configuration": [],
            "scripts": [],
            "tests": [],
            "assets": [],
            "build_files": [],
            "other": []
        }
        
        for doc in document_registry:
            doc_type = doc.get("type", "unknown")
            path = doc.get("path", "").lower()
            
            # Categorize based on type and path
            if doc_type in ["markdown", "text", "restructured_text"]:
                categories["documentation"].append(doc)
            elif doc_type.endswith("_code"):
                categories["source_code"].append(doc)
            elif doc_type in ["yaml_config", "json_data"]:
                categories["configuration"].append(doc)
            elif doc_type == "shell_script":
                categories["scripts"].append(doc)
            elif "test" in path or "spec" in path:
                categories["tests"].append(doc)
            elif doc_type in ["html_document", "css_stylesheet", "pdf_document"]:
                categories["assets"].append(doc)
            elif doc_type in ["docker_file", "makefile"]:
                categories["build_files"].append(doc)
            else:
                categories["other"].append(doc)
        
        # Add category counts to metrics
        for category, docs in categories.items():
            self._add_metric(f"category_{category}_count", len(docs))
        
        return categories
    
    def _detect_document_dependencies(self, document_registry: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Detect document dependencies and relationships"""
        dependencies = {}
        
        for doc in document_registry:
            doc_path = doc.get("path", "")
            doc_deps = []
            
            try:
                content = self.read_file_safely(doc_path)
                if content:
                    # Look for common dependency patterns
                    doc_deps.extend(self._find_file_references(content, document_registry))
                    doc_deps.extend(self._find_import_statements(content, document_registry))
                    doc_deps.extend(self._find_include_statements(content, document_registry))
                
                dependencies[doc_path] = list(set(doc_deps))  # Remove duplicates
                
            except Exception as e:
                self._add_warning(f"Could not analyze dependencies for {doc_path}: {e}")
        
        # Calculate dependency statistics
        total_deps = sum(len(deps) for deps in dependencies.values())
        self._add_metric("total_dependencies", total_deps)
        self._add_metric("average_dependencies_per_doc", total_deps / len(document_registry) if document_registry else 0)
        
        return dependencies
    
    def _find_file_references(self, content: str, document_registry: List[Dict[str, Any]]) -> List[str]:
        """Find file references in content"""
        references = []
        
        # Common file reference patterns
        import re
        
        # Markdown links: [text](file.md)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for _, link in markdown_links:
            if link.endswith(('.md', '.txt', '.py', '.js', '.yaml', '.json')):
                references.append(link)
        
        # Relative file paths
        file_paths = re.findall(r'["\']([^"\']*\.(?:md|txt|py|js|yaml|json|yml|html|css))["\']', content)
        references.extend(file_paths)
        
        return references
    
    def _find_import_statements(self, content: str, document_registry: List[Dict[str, Any]]) -> List[str]:
        """Find import statements"""
        imports = []
        
        import re
        
        # Python imports
        python_imports = re.findall(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content)
        imports.extend(python_imports)
        
        # JavaScript imports
        js_imports = re.findall(r'(?:import|require)\s*\(\s*["\']([^"\']+)["\']', content)
        imports.extend(js_imports)
        
        return imports
    
    def _find_include_statements(self, content: str, document_registry: List[Dict[str, Any]]) -> List[str]:
        """Find include statements"""
        includes = []
        
        import re
        
        # C/C++ includes
        c_includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
        includes.extend(c_includes)
        
        # YAML/JSON references
        yaml_refs = re.findall(r'\$ref:\s*["\']([^"\']+)["\']', content)
        includes.extend(yaml_refs)
        
        return includes
    
    def _generate_document_registry_json(self, document_registry: List[Dict[str, Any]], 
                                       categorized_documents: Dict[str, List[Dict[str, Any]]], 
                                       dependencies: Dict[str, List[str]]) -> Dict[str, Any]:
        """Generate document registry JSON"""
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_documents": len(document_registry),
                "agent_name": self.name,
                "version": "1.0.0"
            },
            "summary": {
                "by_category": {category: len(docs) for category, docs in categorized_documents.items()},
                "total_dependencies": sum(len(deps) for deps in dependencies.values()),
                "average_dependencies": sum(len(deps) for deps in dependencies.values()) / len(document_registry) if document_registry else 0
            },
            "documents": document_registry,
            "categories": categorized_documents,
            "dependencies": dependencies
        }
    
    def _validate_discovery_completeness(self, document_registry: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Self-validate completeness and accuracy"""
        validation = {
            "is_complete": True,
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        total_docs = len(document_registry)
        
        # Check for common document types
        doc_types = [doc.get("type", "unknown") for doc in document_registry]
        type_counts = {}
        for doc_type in doc_types:
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        # Validate that we found expected document types
        expected_types = ["markdown", "python_code", "yaml_config"]
        found_expected = sum(1 for t in expected_types if t in type_counts)
        
        if found_expected < len(expected_types):
            validation["issues"].append(f"Missing expected document types. Found {found_expected}/{len(expected_types)}")
            validation["is_complete"] = False
        
        # Check for minimum document count
        if total_docs < 10:
            validation["issues"].append(f"Low document count: {total_docs}")
            validation["recommendations"].append("Consider expanding search patterns")
        
        # Calculate validation score
        score = 0.0
        score += min(1.0, total_docs / 100) * 0.3  # Document count (30%)
        score += (found_expected / len(expected_types)) * 0.4  # Expected types (40%)
        score += 0.3 if validation["is_complete"] else 0.0  # Completeness (30%)
        
        validation["score"] = round(score, 3)
        
        return validation
