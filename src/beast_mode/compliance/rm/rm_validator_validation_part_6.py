from src.rm_ddd.core.health import ModuleHealth

def _validate_class_methods(self, class_node: ast.ClassDef, module_path: str) -> tuple[List[str], List[str]]:
    """Validate methods in a ReflectiveModule class."""
    missing_methods = []
    invalid_methods = []
    class_methods = set()
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef):
            class_methods.add(node.name)
    for method_name in self.REQUIRED_RM_METHODS:
        if method_name not in class_methods:
            missing_methods.append(method_name)
    return (missing_methods, invalid_methods)
