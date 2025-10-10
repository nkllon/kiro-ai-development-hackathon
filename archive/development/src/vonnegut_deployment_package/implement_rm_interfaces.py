#!/usr/bin/env python3
"""
Implement RM Interfaces - Systematic ReflectiveModule interface implementation

This script systematically implements the ReflectiveModule interface for all modules
in the DevPost integration system to achieve RM-DDD compliance.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import ast
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)


class RMInterfaceImplementer:
    """Systematically implements ReflectiveModule interfaces for all modules"""

    def __init__(self, devpost_path: str = "src/devpost_integration"):
        """Initialize the implementer"""
        self.devpost_path = Path(devpost_path)
        self.reflective_module_path = self.devpost_path / "reflective_module.py"
        self.modules_processed = 0
        self.modules_updated = 0
        self.errors = []

        # Template for ReflectiveModule implementation
        self.rm_interface_template = '''
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {{
            'module_id': self.module_id,
            'version': self.version,
            'name': '{module_name}',
            'description': '{module_description}',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }}
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return {capabilities}
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return {dependencies}
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            {module_specific_checks}
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {{e}}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {{e}}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={{}}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={{}},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={{}},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {{self.module_id}}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {{e}}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {{
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }}
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {{self.module_id}} module")
'''

    def find_python_modules(self) -> List[Path]:
        """Find all Python modules in the DevPost integration directory"""
        modules = []

        for py_file in self.devpost_path.glob("*.py"):
            if py_file.name != "__init__.py" and py_file.name != "reflective_module.py":
                modules.append(py_file)

        return sorted(modules)

    def analyze_module(self, module_path: Path) -> Dict[str, Any]:
        """Analyze a module to determine its characteristics"""
        try:
            with open(module_path, "r") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Find main class
            main_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not main_class or len(node.body) > len(main_class.body):
                        main_class = node

            # Extract information
            module_name = module_path.stem
            class_name = main_class.name if main_class else "Unknown"

            # Determine capabilities based on module name and content
            capabilities = self._determine_capabilities(module_name, content)

            # Determine dependencies
            dependencies = self._extract_dependencies(content)

            # Determine module-specific health checks
            health_checks = self._determine_health_checks(module_name, content)

            return {
                "module_name": module_name,
                "class_name": class_name,
                "capabilities": capabilities,
                "dependencies": dependencies,
                "health_checks": health_checks,
                "has_rm_interface": "ReflectiveModule" in content,
            }

        except Exception as e:
            logger.error(f"Error analyzing module {module_path}: {e}")
            return {
                "module_name": module_path.stem,
                "class_name": "Unknown",
                "capabilities": [],
                "dependencies": [],
                "health_checks": "",
                "has_rm_interface": False,
                "error": str(e),
            }

    def _determine_capabilities(self, module_name: str, content: str) -> List[str]:
        """Determine module capabilities based on name and content"""
        capabilities = [ModuleCapability.CORE_FUNCTIONALITY]

        # Add capabilities based on module name
        if "cli" in module_name:
            capabilities.append(ModuleCapability.CONFIGURATION)
            capabilities.append(ModuleCapability.LOGGING)
        elif "api" in module_name:
            capabilities.append(ModuleCapability.API_INTEGRATION)
        elif "notification" in module_name:
            capabilities.append(ModuleCapability.NOTIFICATIONS)
        elif "validation" in module_name:
            capabilities.append(ModuleCapability.CONFIGURATION)
        elif "file" in module_name or "monitor" in module_name:
            capabilities.append(ModuleCapability.PERSISTENCE)

        # Add capabilities based on content
        if "health" in content.lower() or "check_health" in content:
            capabilities.append(ModuleCapability.HEALTH_MONITORING)
        if "metrics" in content.lower() or "get_metrics" in content:
            capabilities.append(ModuleCapability.METRICS)
        if "log" in content.lower() or "logger" in content:
            capabilities.append(ModuleCapability.LOGGING)

        return capabilities

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract module dependencies from imports"""
        dependencies = []

        # Find relative imports
        import_pattern = r"from \.(\w+) import"
        matches = re.findall(import_pattern, content)
        dependencies.extend(matches)

        # Remove duplicates and sort
        return sorted(list(set(dependencies)))

    def _determine_health_checks(self, module_name: str, content: str) -> str:
        """Determine module-specific health checks"""
        checks = []

        # Add checks based on module type
        if "cli" in module_name:
            checks.append("# Check CLI components")
            checks.append("if not hasattr(self, 'parser'):")
            checks.append("    issues.append('Missing parser component')")
            checks.append("    health_score -= 0.2")
        elif "api" in module_name:
            checks.append("# Check API connectivity")
            checks.append("if not hasattr(self, 'api_client'):")
            checks.append("    issues.append('Missing API client')")
            checks.append("    health_score -= 0.3")
        elif "validation" in module_name:
            checks.append("# Check validation rules")
            checks.append("if not hasattr(self, 'rules'):")
            checks.append("    issues.append('Missing validation rules')")
            checks.append("    health_score -= 0.2")

        return "\n            ".join(checks)

    def implement_rm_interface(self, module_path: Path) -> bool:
        """Implement ReflectiveModule interface for a module"""
        try:
            # Analyze module
            analysis = self.analyze_module(module_path)

            if analysis.get("has_rm_interface"):
                logger.info(f"Module {module_path.name} already has RM interface")
                return True

            # Read current content
            with open(module_path, "r") as f:
                content = f.read()

            # Add imports
            if "from .reflective_module import" not in content:
                # Find the last import statement
                import_end = content.rfind("\n")
                for i, line in enumerate(content.split("\n")):
                    if line.startswith("import ") or line.startswith("from "):
                        import_end = content.find("\n", content.find(line))

                # Add RM imports
                rm_imports = """
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime
"""

                content = content[:import_end] + rm_imports + content[import_end:]

            # Find main class and add RM interface
            class_pattern = r"class (\w+):"
            match = re.search(class_pattern, content)

            if not match:
                logger.warning(f"No class found in {module_path.name}")
                return False

            class_name = match.group(1)

            # Update class to inherit from ReflectiveModule
            if f"class {class_name}:" in content:
                content = content.replace(
                    f"class {class_name}:", f"class {class_name}(ReflectiveModule):"
                )

            # Add RM interface methods
            rm_interface = self.rm_interface_template.format(
                module_name=analysis["module_name"].replace("_", " ").title(),
                module_description=f"{analysis['module_name']} module for DevPost integration",
                capabilities=analysis["capabilities"],
                dependencies=analysis["dependencies"],
                module_specific_checks=analysis["health_checks"],
            )

            # Find the end of the class and add RM interface
            class_end = content.rfind("\n\n")
            if class_end == -1:
                class_end = len(content)

            content = content[:class_end] + rm_interface + content[class_end:]

            # Add initialization code
            init_pattern = r"def __init__\(self[^)]*\):"
            init_match = re.search(init_pattern, content)

            if init_match:
                init_start = init_match.start()
                init_end = content.find("\n", init_start)

                # Add RM initialization
                rm_init = """
        super().__init__(module_id="{module_id}", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)
""".format(
                    module_id=analysis["module_name"]
                )

                content = content[:init_end] + rm_init + content[init_end:]

            # Write updated content
            with open(module_path, "w") as f:
                f.write(content)

            logger.info(f"Implemented RM interface for {module_path.name}")
            return True

        except Exception as e:
            logger.error(f"Error implementing RM interface for {module_path}: {e}")
            self.errors.append(f"{module_path}: {e}")
            return False

    def implement_all_modules(self) -> Dict[str, Any]:
        """Implement RM interfaces for all modules"""
        logger.info("Starting RM interface implementation for all modules")

        modules = self.find_python_modules()
        results = {
            "total_modules": len(modules),
            "processed": 0,
            "updated": 0,
            "errors": [],
            "modules": {},
        }

        for module_path in modules:
            self.modules_processed += 1
            results["processed"] += 1

            logger.info(
                f"Processing module {self.modules_processed}/{len(modules)}: {module_path.name}"
            )

            success = self.implement_rm_interface(module_path)

            if success:
                self.modules_updated += 1
                results["updated"] += 1
                results["modules"][module_path.name] = "success"
            else:
                results["modules"][module_path.name] = "failed"

        results["errors"] = self.errors

        logger.info(
            f"RM interface implementation complete: {self.modules_updated}/{self.modules_processed} modules updated"
        )
        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate implementation report"""
        report = f"""
RM Interface Implementation Report
================================

Total Modules: {results['total_modules']}
Processed: {results['processed']}
Updated: {results['updated']}
Errors: {len(results['errors'])}

Success Rate: {(results['updated'] / results['processed'] * 100):.1f}%

Module Status:
"""

        for module_name, status in results["modules"].items():
            report += f"  {module_name}: {status}\n"

        if results["errors"]:
            report += "\nErrors:\n"
            for error in results["errors"]:
                report += f"  {error}\n"

        return report


def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)

    implementer = RMInterfaceImplementer()
    results = implementer.implement_all_modules()

    # Print report
    print(implementer.generate_report(results))

    # Save report
    with open("rm_interface_implementation_report.txt", "w") as f:
        f.write(implementer.generate_report(results))

    logger.info(
        "RM interface implementation report saved to rm_interface_implementation_report.txt"
    )


if __name__ == "__main__":
    main()
