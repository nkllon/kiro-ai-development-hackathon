#!/usr/bin/env python3
"""
Code Generation Templates - Proper Structure Templates
=====================================================

This module provides validated templates for code generation to prevent
indentation issues and ensure proper class structure.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Safe code generation templates
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeTemplate:
    """A validated code generation template."""

    name: str
    description: str
    template: str
    validation_rules: List[str]


class CodeGenerationTemplates:
    """Collection of validated code generation templates."""

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, CodeTemplate]:
        """Initialize all validated templates."""
        templates = {}

        # ReflectiveModule Template
        templates["reflective_module"] = CodeTemplate(
            name="ReflectiveModule",
            description="Standard ReflectiveModule implementation",
            template=self._get_reflective_module_template(),
            validation_rules=[
                "Class must inherit from ReflectiveModule",
                "Must have __init__ method with module_name parameter",
                "Must implement all abstract methods",
                "All methods must have proper docstrings",
            ],
        )

        # Tool Health Manager Template
        templates["tool_health_manager"] = CodeTemplate(
            name="ToolHealthManager",
            description="Tool Health Manager implementation",
            template=self._get_tool_health_manager_template(),
            validation_rules=[
                "Class must inherit from ReflectiveModule",
                "Must implement health checking methods",
                "Must have proper service lifecycle methods",
                "All methods must be properly indented within class",
            ],
        )

        # Documentation Manager Template
        templates["documentation_manager"] = CodeTemplate(
            name="DocumentationManager",
            description="Documentation Manager implementation",
            template=self._get_documentation_manager_template(),
            validation_rules=[
                "Class must inherit from ReflectiveModule",
                "Must implement document management methods",
                "Must have proper RDI compliance methods",
                "All methods must be properly indented within class",
            ],
        )

        # Generic Module Template
        templates["generic_module"] = CodeTemplate(
            name="GenericModule",
            description="Generic ReflectiveModule implementation",
            template=self._get_generic_module_template(),
            validation_rules=[
                "Class must inherit from ReflectiveModule",
                "Must have proper constructor",
                "Must implement required abstract methods",
                "All methods must be properly indented within class",
            ],
        )

        return templates

    def _get_reflective_module_template(self) -> str:
        """Get ReflectiveModule template."""
        return '''from src.rm_ddd.core.base_reflective_module import ReflectiveModule
from typing import Dict, Any, List
from datetime import datetime

class {class_name}(ReflectiveModule):
    """{class_name} - ReflectiveModule implementation."""
    
    def __init__(self):
        super().__init__(module_name="{class_name}")
        self.module_id = "{class_name}"
    
    def perform_core_operation(self):
        """Perform core operation for RDI compliance."""
        return {{"status": "success", "operation": "{operation_type}"}}
    
    def check_health(self):
        """Check health status of the module."""
        class HealthStatus:
            def __init__(self, status, timestamp, module_id):
                self.status = status
                self.timestamp = timestamp
                self.module_id = module_id
        
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            module_id=self.module_id
        )
    
    def get_capabilities(self):
        """Get module capabilities."""
        return {capabilities}
    
    def get_dependencies(self):
        """Get module dependencies."""
        return []
    
    def get_module_info(self):
        """Get module information."""
        return {{
            "module_id": self.module_id,
            "version": "1.0.0",
            "description": "{description}"
        }}
    
    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {{
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }}
'''

    def _get_tool_health_manager_template(self) -> str:
        """Get Tool Health Manager template."""
        return '''from src.rm_ddd.core.base_reflective_module import ReflectiveModule
from typing import Dict, Any, List
from datetime import datetime
import subprocess

class {class_name}(ReflectiveModule):
    """{class_name} - Tool Health Manager implementation."""
    
    def __init__(self):
        super().__init__(module_name="{class_name}")
        self.module_id = "{class_name}"
    
    def perform_core_operation(self):
        """Perform core operation for RDI compliance."""
        return {{"status": "success", "operation": "tool_health_management"}}
    
    def check_health(self):
        """Check health status of the module."""
        class HealthStatus:
            def __init__(self, status, timestamp, module_id):
                self.status = status
                self.timestamp = timestamp
                self.module_id = module_id
        
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            module_id=self.module_id
        )
    
    def get_capabilities(self):
        """Get module capabilities."""
        return ["tool_health_management", "service_monitoring", "diagnostic_repair"]
    
    def get_dependencies(self):
        """Get module dependencies."""
        return []
    
    def get_module_info(self):
        """Get module information."""
        return {{
            "module_id": self.module_id,
            "version": "1.0.0",
            "description": "{description}"
        }}
    
    def start(self):
        """Start the service."""
        return True
    
    def stop(self):
        """Stop the service."""
        return True
    
    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {{
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }}
'''

    def _get_documentation_manager_template(self) -> str:
        """Get Documentation Manager template."""
        return '''from src.rm_ddd.core.base_reflective_module import ReflectiveModule
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

@dataclass
class RDIDocument:
    """RDI Document structure."""
    title: str
    content: str
    requirements: List[str]
    traceability_id: str

class {class_name}(ReflectiveModule):
    """{class_name} - Documentation Manager implementation."""
    
    def __init__(self, docs_root: Optional[Path] = None):
        super().__init__(module_name="{class_name}")
        self.module_id = "{class_name}"
        self.docs_root = docs_root or Path("docs")
    
    def perform_core_operation(self):
        """Perform core operation for RDI compliance."""
        return {{"status": "success", "operation": "document_management"}}
    
    def check_health(self):
        """Check health status of the module."""
        class HealthStatus:
            def __init__(self, status, timestamp, module_id):
                self.status = status
                self.timestamp = timestamp
                self.module_id = module_id
        
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            module_id=self.module_id
        )
    
    def get_capabilities(self):
        """Get module capabilities."""
        return ["document_management", "rdi_compliance", "traceability"]
    
    def get_dependencies(self):
        """Get module dependencies."""
        return []
    
    def get_module_info(self):
        """Get module information."""
        return {{
            "module_id": self.module_id,
            "version": "1.0.0",
            "description": "{description}"
        }}
    
    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {{
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }}
'''

    def _get_generic_module_template(self) -> str:
        """Get generic module template."""
        return '''from src.rm_ddd.core.base_reflective_module import ReflectiveModule
from typing import Dict, Any, List
from datetime import datetime

class {class_name}(ReflectiveModule):
    """{class_name} - Generic ReflectiveModule implementation."""
    
    def __init__(self):
        super().__init__(module_name="{class_name}")
        self.module_id = "{class_name}"
    
    def perform_core_operation(self):
        """Perform core operation for RDI compliance."""
        return {{"status": "success", "operation": "{operation_type}"}}
    
    def check_health(self):
        """Check health status of the module."""
        class HealthStatus:
            def __init__(self, status, timestamp, module_id):
                self.status = status
                self.timestamp = timestamp
                self.module_id = module_id
        
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            module_id=self.module_id
        )
    
    def get_capabilities(self):
        """Get module capabilities."""
        return {capabilities}
    
    def get_dependencies(self):
        """Get module dependencies."""
        return []
    
    def get_module_info(self):
        """Get module information."""
        return {{
            "module_id": self.module_id,
            "version": "1.0.0",
            "description": "{description}"
        }}
    
    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {{
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }}
'''

    def get_template(self, template_name: str) -> CodeTemplate:
        """Get a specific template by name."""
        if template_name not in self.templates:
            raise ValueError(
                f"Template '{template_name}' not found. Available: {list(self.templates.keys())}"
            )
        return self.templates[template_name]

    def generate_code(self, template_name: str, **kwargs) -> str:
        """Generate code using a template."""
        template = self.get_template(template_name)

        # Set default values
        defaults = {
            "class_name": "GeneratedModule",
            "description": "Generated module description",
            "operation_type": "generic_operation",
            "capabilities": '["generic_capability"]',
        }
        defaults.update(kwargs)

        return template.template.format(**defaults)

    def list_templates(self) -> List[str]:
        """List all available templates."""
        return list(self.templates.keys())

    def validate_template_usage(
        self, template_name: str, generated_code: str
    ) -> List[str]:
        """Validate that generated code follows template rules."""
        template = self.get_template(template_name)
        errors = []

        # Basic syntax check
        try:
            import ast

            ast.parse(generated_code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e.msg} at line {e.lineno}")

        # Check for module-level functions with 'self'
        lines = generated_code.split("\n")
        for i, line in enumerate(lines):
            if (
                line.strip().startswith("def ")
                and "self" in line
                and not line.startswith("    ")
            ):
                errors.append(
                    f"Line {i+1}: Module-level function with 'self' parameter"
                )

        return errors


def main():
    """Main function for template management."""
    import argparse

    parser = argparse.ArgumentParser(description="Code generation template management")
    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--generate", help="Generate code from template")
    parser.add_argument("--template", help="Template name to use")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--class-name", help="Class name for generated code")
    parser.add_argument("--description", help="Description for generated code")

    args = parser.parse_args()

    templates = CodeGenerationTemplates()

    if args.list:
        print("Available templates:")
        for name in templates.list_templates():
            template = templates.get_template(name)
            print(f"  • {name}: {template.description}")

    elif args.generate and args.template:
        kwargs = {}
        if args.class_name:
            kwargs["class_name"] = args.class_name
        if args.description:
            kwargs["description"] = args.description

        try:
            code = templates.generate_code(args.template, **kwargs)
            print(code)

            if args.output:
                with open(args.output, "w") as f:
                    f.write(code)
                print(f"Code generated and saved to {args.output}")

        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
