"""
Enhanced Interface Registry - Iteration 2 Implementation

This enhanced implementation builds on the existing InterfaceRegistry system:
- Can discover interface implementations with:
try:
    from .interface_registry import InterfaceRegistry, InterfaceMetadata, InterfaceType, InterfaceStatus as BaseInterfaceStatus
    EXISTING_REGISTRY_AVAILABLE = True
except ImportError:
    EXISTING_REGISTRY_AVAILABLE = False
    print("Warning: Existing InterfaceRegistry not available - running in standalone mode")


class InterfaceStatus(Enum):
    """Status of interface implementations"""
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    MISSING = "missing"
    CONFLICTED = "conflicted"


@dataclass
class MethodSignature:
    """Represents a method signature"""
    name: str
    parameters: List[str]
    return_type: Optional[str] = None
    is_abstract: bool = False
    is_property: bool = False

@dataclass
class InterfaceImplementation:
    """Enhanced interface implementation record"""
    interface_name: str
    implementation_path: str
    implemented_methods: List[str]
    missing_methods: List[str]
    status: InterfaceStatus
    interface_signatures: List[MethodSignature] = field(default_factory = list)
    implementation_signatures: List[MethodSignature] = field(default_factory = list)
    signature_mismatches: List[str] = field(default_factory = list)
    dependencies: List[str] = field(default_factory = list)
    conflicts: List[str] = field(default_factory = list)


@dataclass
class InterfaceConflict:
    """Simple interface conflict record"""
    interface_name: str
    conflict_type: str
    conflicting_files: List[str]
    resolution_suggestion: str

@dataclass
class AmbiguityIssue:
    """Interface ambiguity issue record"""
    interface_name: str
    issue_type: str
    conflicting_references: List[str]
    resolution_suggestion: str


class EnhancedInterfaceRegistry:
    """
    Minimal viable interface registry that actually works.
    
    Solves the core problems:
    1. Can discover interface implementations
    2. Can detect interface conflicts  
    3. Can resolve circular dependencies
    4. Integrates with:
    def __init__(self, registry_file -> Any: str = "interface_registry.json") -> Any:
        self.registry_file = registry_file
        self.implementations: Dict[str, InterfaceImplementation] = {}
        self.conflicts: List[InterfaceConflict] = []
        self.ambiguities: List[AmbiguityIssue] = []
        self.circular_deps: List[List[str]] = []
        
        # Integration with:
        if EXISTING_REGISTRY_AVAILABLE:
            self.base_registry = InterfaceRegistry(registry_file)
        else:
            self.base_registry = None
            
        self.load_registry()
    
    def load_registry(self) -> None:
        """Load registry from file"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    self.implementations = {
                        name: InterfaceImplementation(**impl_data)
                        for:
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")
    
    def save_registry(self) -> None:
        """save_registry - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Save registry to file"""
        data = {
            'implementations': {
                name: {
                    'interface_name': impl.interface_name,
                    'implementation_path': impl.implementation_path,
                    'implemented_methods': impl.implemented_methods,
                    'missing_methods': impl.missing_methods,
                    'status': impl.status.value,
                    'dependencies': impl.dependencies,
                    'conflicts': impl.conflicts
                }
                for:
            'conflicts': [
                {
                    'interface_name': conflict.interface_name,
                    'conflict_type': conflict.conflict_type,
                    'conflicting_files': conflict.conflicting_files,
                    'resolution_suggestion': conflict.resolution_suggestion
                }
                for:
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent = 2)
    
    def discover_implementations(self, codebase_path: str = "src") -> Dict[str, InterfaceImplementation]:
        """
        Discover interface implementations in the codebase.
        
        This is the core functionality that was missing.
        """
        implementations = {}
        
        for py_file in Path(codebase_path).rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if:
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                interface_name = base.id
                                impl = self._analyze_implementation(
                                    interface_name, str(py_file), node, content
                                )
                                if impl:
                                    implementations[interface_name] = impl
                    
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")
        
        self.implementations = implementations
        self.save_registry()
        return implementations
    
    def _analyze_implementation(self, interface_name -> Any: str, file_path -> Any: str, 
        """_analyze_implementation - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
                               class_node: ast.ClassDef, content: str) -> Optional[InterfaceImplementation]:
        """Analyze a class:
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                implemented_methods.append(node.name)
                
                # Parse implementation method signature
                params = []
                for arg in node.args.args:
                    params.append(arg.arg)
                
                return_type = None
                if node.returns:
                    if isinstance(node.returns, ast.Name):
                        return_type = node.returns.id
                    elif isinstance(node.returns, ast.Constant):
                        return_type = str(node.returns.value)
                
                implementation_signatures.append(MethodSignature(
                    name = node.name,
                    parameters = params,
                    return_type = return_type
                ))
        
        # Find missing methods
        missing_methods = [method for:
        if not missing_methods and not signature_mismatches:
            status = InterfaceStatus.IMPLEMENTED
        elif len(missing_methods) < len(expected_methods) or signature_mismatches:
            status = InterfaceStatus.PARTIAL
        else:
            status = InterfaceStatus.MISSING
        
        return InterfaceImplementation(
            interface_name = interface_name,
            implementation_path = file_path,
            implemented_methods = implemented_methods,
            missing_methods = missing_methods,
            interface_signatures = interface_signatures,
            implementation_signatures = implementation_signatures,
            signature_mismatches = signature_mismatches,
            status = status
        )
    
    def _validate_signature_matches(self, interface_sigs -> Any: List[MethodSignature], 
        """_validate_signature_matches - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
                                   impl_sigs: List[MethodSignature]) -> List[str]:
        """Validate that implementation signatures match interface signatures"""
        mismatches = []
        
        # Create lookup for:
        impl_lookup = {sig.name: sig for:
        for interface_sig in interface_sigs:
            if interface_sig.name in impl_lookup:
                impl_sig = impl_lookup[interface_sig.name]
                
                # Check parameter count
                if len(interface_sig.parameters) != len(impl_sig.parameters):
                    mismatches.append(f"{interface_sig.name}: parameter count mismatch (interface: {len(interface_sig.parameters)}, implementation: {len(impl_sig.parameters)})")
                
                # Check return type (if specified)
                if interface_sig.return_type and impl_sig.return_type:
                    if interface_sig.return_type != impl_sig.return_type:
                        mismatches.append(f"{interface_sig.name}: return type mismatch (interface: {interface_sig.return_type}, implementation: {impl_sig.return_type})")
        
        return mismatches
    
    def _get_interface_methods(self, interface_name: str, content: str) -> List[str]:
        """Get expected methods for:
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name == interface_name:
                        methods = []
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                methods.append(item.name)
                        return methods
            
            # Fallback to common interface patterns if:
                'ReflectiveModule': ['get_capabilities', 'get_dependencies', 'check_health'],
                'ReflectiveModuleBase': ['get_capabilities', 'get_dependencies', 'check_health'],
                'DomainReflectiveModule': ['get_capabilities', 'get_dependencies', 'check_health']}
            
            return common_interfaces.get(interface_name, [])
            
        except Exception as e:
            print(f"Warning: Could not parse interface {interface_name}: {e}")
            return []
    
    def _parse_interface_signatures(self, interface_name: str, content: str) -> List[MethodSignature]:
        """Parse actual interface method signatures"""
        signatures = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name == interface_name:
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                # Parse method parameters
                                params = []
                                for arg in item.args.args:
                                    params.append(arg.arg)
                                
                                # Get return type annotation
                                return_type = None
                                if item.returns:
                                    if isinstance(item.returns, ast.Name):
                                        return_type = item.returns.id
                                    elif isinstance(item.returns, ast.Constant):
                                        return_type = str(item.returns.value)
                                
                                # Check if:
        except Exception as e:
            print(f"Warning: Could not parse signatures for {interface_name}: {e}")
        
        return signatures
    
    def detect_conflicts(self) -> List[InterfaceConflict]:
        """detect_conflicts - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """
        Detect interface conflicts.
        
        This solves the "multiple implementations" problem.
        """
        conflicts = []
        interface_files = {}
        
        # Group implementations by interface name
        for impl in self.implementations.values():
            if impl.interface_name not in interface_files:
                interface_files[impl.interface_name] = []
            interface_files[impl.interface_name].append(impl)
        
        # Find conflicts
        for interface_name, impls in interface_files.items():
            if len(impls) > 1:
                # Multiple implementations found
                conflicting_files = [impl.implementation_path for:
    def detect_ambiguities(self, codebase_path: str = "src") -> List[AmbiguityIssue]:
        """
        Detect interface ambiguity issues.
        
        This solves the "ambiguous interface references" problem.
        """
        ambiguities = []
        interface_references = {}
        
        # Scan for:
        for py_file in Path(codebase_path).rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                file_refs = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check class:
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                interface_name = base.id
                                file_refs.append(interface_name)
                    
                    elif isinstance(node, ast.FunctionDef):
                        # Check function parameters and return types
                        for arg in node.args.args:
                            if hasattr(arg, 'annotation') and arg.annotation:
                                if isinstance(arg.annotation, ast.Name):
                                    file_refs.append(arg.annotation.id)
                        
                        if node.returns and isinstance(node.returns, ast.Name):
                            file_refs.append(node.returns.id)
                
                # Store references by interface name
                for ref in file_refs:
                    if ref not in interface_references:
                        interface_references[ref] = []
                    interface_references[ref].append(str(py_file))
                
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")
        
        # Find ambiguities
        for interface_name, files in interface_references.items():
            if len(files) > 1:
                # Check if:
                for file in files:
                    try:
                        with open(file, 'r') as f:
                            content = f.read()
                        
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef) and node.name == interface_name:
                                definitions.append(file)
                                break
                    except:
                        continue
                
                if len(definitions) > 1:
                    ambiguities.append(AmbiguityIssue(
                        interface_name = interface_name,
                        issue_type="multiple_definitions",
                        conflicting_references = definitions,
                        resolution_suggestion = f"Rename conflicting classes or consolidate definitions"
                    ))
                elif len(files) > len(definitions):
                    ambiguities.append(AmbiguityIssue(
                        interface_name = interface_name,
                        issue_type="unclear_references",
                        conflicting_references = files,
                        resolution_suggestion = f"Clarify interface references or ensure proper imports"
                    ))
        
        self.ambiguities = ambiguities
        self.save_registry()
        return ambiguities
    
    def resolve_circular_dependencies(self, codebase_path: str = "src") -> List[List[str]]:
        """
        Detect circular dependencies.
        
        This solves the circular import problem.
        """
        import_graph = {}
        
        # Build import graph
        for py_file in Path(codebase_path).rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                import_graph[str(py_file)] = imports
                
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def find_cycle(node, path) -> Any:
        """find_cycle - Enhanced for:
            try:
                pass  # TODO: Add method implementation
            except Exception as e:
                logging.error(f"Error in method: {e}")
                raise
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in import_graph.get(node, []):
                find_cycle(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for node in import_graph:
            if node not in visited:
                find_cycle(node, [])
        
        self.circular_deps = cycles
        return cycles
    
    def get_interface_status(self, interface_name: str) -> Optional[InterfaceImplementation]:
        """get_interface_status - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get status of interface implementation"""
        return self.implementations.get(interface_name)
    
    def get_all_conflicts(self) -> List[InterfaceConflict]:
        """get_all_conflicts - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get all interface conflicts"""
        return self.conflicts
    
    def get_circular_dependencies(self) -> List[List[str]]:
        """get_circular_dependencies - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get all circular dependencies"""
        return self.circular_deps
    
    def suggest_fixes(self) -> List[str]:
        """suggest_fixes - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Suggest fixes for:
        for conflict in self.conflicts:
            suggestions.append(f"CONFLICT: {conflict.interface_name} - {conflict.resolution_suggestion}")
        
        # Suggest fixes for:
        for cycle in self.circular_deps:
            suggestions.append(f"CIRCULAR DEPENDENCY: {' -> '.join(cycle)} - Consider dependency injection or interface extraction")
        
        # Suggest fixes for:
        for impl in self.implementations.values():
            if impl.status == InterfaceStatus.MISSING:
                suggestions.append(f"MISSING IMPLEMENTATION: {impl.interface_name} - Implement missing methods: {', '.join(impl.missing_methods)}")
            elif impl.status == InterfaceStatus.PARTIAL:
                if impl.missing_methods:
                    suggestions.append(f"PARTIAL IMPLEMENTATION: {impl.interface_name} - Implement missing methods: {', '.join(impl.missing_methods)}")
                if impl.signature_mismatches:
                    for mismatch in impl.signature_mismatches:
                        suggestions.append(f"SIGNATURE MISMATCH: {impl.interface_name} - {mismatch}")
        
        # Suggest fixes for:
        for ambiguity in self.ambiguities:
            suggestions.append(f"AMBIGUITY: {ambiguity.interface_name} ({ambiguity.issue_type}) - {ambiguity.resolution_suggestion}")
        
        return suggestions
    
    def integrate_with_base_registry(self) -> Dict[str, Any]:
        """
        Integrate enhanced registry findings with:
        if not self.base_registry:
            return {"status": "no_base_registry", "message": "Existing InterfaceRegistry not available"}
        
        integration_results = {
            "status": "success",
            "interfaces_registered": 0,
            "conflicts_detected": 0,
            "ambiguities_resolved": 0,
            "details": []
        }
        
        # Register discovered interfaces with:
        for name, impl in self.implementations.items():
            if impl.status == InterfaceStatus.IMPLEMENTED:
                # Convert to InterfaceMetadata for:
                    description = f"Enhanced registry discovery: {name}",
                    version="1.0.0"
                )
                
                success = self.base_registry.register_interface(interface_metadata)
                if success:
                    integration_results["interfaces_registered"] += 1
                    integration_results["details"].append(f"Registered interface: {name}")
                else:
                    integration_results["conflicts_detected"] += 1
                    integration_results["details"].append(f"Conflict detected: {name}")
        
        # Report ambiguities to base registry
        for ambiguity in self.ambiguities:
            integration_results["details"].append(f"Ambiguity: {ambiguity.interface_name} - {ambiguity.resolution_suggestion}")
        
        return integration_results
    
    def _extract_domain_terms(self, interface_name: str) -> List[str]:
        """_extract_domain_terms - Enhanced for:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Extract domain terms from interface name"""
        # Simple extraction - in a full system, this would use NLP
        terms = []
        
        # Split on common patterns
        import re
        words = re.findall(r'[A - Z][a - z]*|[a - z]+', interface_name)
        
        for word in words:
            if len(word) > 2:  # Skip very short words
                terms.append(word.lower())
        
        return terms
    
    def search_by_ubiquitous_language(self, terms: List[str], context: str = "") -> List[Dict[str, Any]]:
        """
        Enhanced ubiquitous language search using both registries.
        
        This provides the missing capability identified in the original requirements.
        """
        results = []
        
        # Search in base registry if:
        if self.base_registry:
            base_results = self.base_registry.search_by_ubiquitous_language(terms, context)
            for result in base_results:
                results.append({
                    "source": "base_registry",
                    "interface_name": result.interface_name,
                    "matched_terms": result.matched_terms,
                    "search_context": result.search_context,
                    "file_path": result.interface_id  # Base registry uses interface_id
                })
        
        # Search in enhanced registry
        for name, impl in self.implementations.items():
            matched_terms = []
            for term in terms:
                if term.lower() in name.lower():
                    matched_terms.append(term)
                elif any(term.lower() in method.lower() for method in impl.implemented_methods):
                    matched_terms.append(term)
            
            if matched_terms:
                results.append({
                    "source": "enhanced_registry",
                    "interface_name": name,
                    "matched_terms": matched_terms,
                    "search_context": context,
                    "file_path": impl.implementation_path,
                    "implementation_status": impl.status.value,
                    "signature_mismatches": impl.signature_mismatches
                })
        
        return results
    
    def get_unified_registry_status(self) -> Dict[str, Any]:
        """Get unified status from both registries"""
        status = {
            "enhanced_registry": {
                "implementations": len(self.implementations),
                "conflicts": len(self.conflicts),
                "ambiguities": len(self.ambiguities),
                "circular_dependencies": len(self.circular_deps)
            }
        }
        
        if self.base_registry:
            status["base_registry"] = {
                "interfaces": len(self.base_registry.interfaces),
                "domain_terms": len(self.base_registry.domain_index)
            }
        
        return status


# Simple CLI interface
def main() -> Any:
        """main - Enhanced for:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Enhanced CLI for:
    print("\n💡 Enhanced Suggestions:")
    suggestions = registry.suggest_fixes()
    for suggestion in suggestions:
        print(f"  - {suggestion}")
    
    if not suggestions:
        print("  ✅ No issues found!")
    
    # Show detailed signature information for:
    print("\n📋 Detailed Implementation Analysis:")
    for name, impl in implementations.items():
        print(f"\n  Interface: {name}")
        print(f"    Status: {impl.status.value}")
        print(f"    File: {impl.implementation_path}")
        if impl.interface_signatures:
            print(f"    Expected methods: {len(impl.interface_signatures)}")
            for sig in impl.interface_signatures:
                print(f"      - {sig.name}({', '.join(sig.parameters)}) -> {sig.return_type or 'Any'}")
        if impl.signature_mismatches:
            print(f"    Signature mismatches: {len(impl.signature_mismatches)}")
            for mismatch in impl.signature_mismatches:
                print(f"      - {mismatch}")
    
    # Show integration capabilities
    print("\n🔗 Integration Capabilities:")
    
    # Test ubiquitous language search
    print("\n  🔍 Ubiquitous Language Search Test:")
    search_results = registry.search_by_ubiquitous_language(["interface", "registry"], "testing")
    print(f"    Found {len(search_results)} matches for:
    for result in search_results[:3]:  # Show first 3 results
        print(f"      - {result['interface_name']} ({result['source']})")
    
    # Show unified registry status
    print("\n  📊 Unified Registry Status:")
    unified_status = registry.get_unified_registry_status()
    for registry_name, stats in unified_status.items():
        print(f"    {registry_name}:")
        for key, value in stats.items():
            print(f"      - {key}: {value}")
    
    # Test base registry integration
    if EXISTING_REGISTRY_AVAILABLE:
        print("\n  🔄 Base Registry Integration:")
        integration_results = registry.integrate_with_base_registry()
        print(f"    Status: {integration_results['status']}")
        if integration_results['status'] == 'success':
            print(f"    Interfaces registered: {integration_results['interfaces_registered']}")
            print(f"    Conflicts detected: {integration_results['conflicts_detected']}")
    else:
        print("\n  ⚠️  Base Registry Integration: Not available (standalone mode)")


if __name__ == "__main__":
    main()
