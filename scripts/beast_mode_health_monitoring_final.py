#!/usr/bin/env python3
"""
Beast Mode Health Monitoring Implementation
Implements comprehensive health monitoring for all modules
"""

import os
import sys
import ast
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from devpost_integration.reflective_module import ModuleHealth, ModuleStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitoringBeastMode:
    """Beast Mode implementation for health monitoring"""
    
    def __init__(self):
        self.devpost_path = Path("src/devpost_integration")
        self.modules_processed = 0
        self.modules_fixed = 0
        self.errors = []
        
    def run(self):
        """Run Beast Mode health monitoring implementation"""
        logger.info("🚀 BEAST MODE: Health Monitoring Implementation")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Find all Python modules
        modules = list(self.devpost_path.glob("*.py"))
        modules = [m for m in modules if m.name != "__init__.py" and m.name != "reflective_module.py"]
        
        logger.info(f"Found {len(modules)} modules to process")
        
        # Process each module
        for module_path in modules:
            try:
                self._process_module(module_path)
                self.modules_processed += 1
            except Exception as e:
                error_msg = f"Error processing {module_path.name}: {e}"
                logger.error(error_msg)
                self.errors.append(error_msg)
        
        # Generate report
        self._generate_report(start_time)
        
        return self.modules_fixed > 0
    
    def _process_module(self, module_path: Path):
        """Process a single module for health monitoring"""
        logger.info(f"Processing {module_path.name}...")
        
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if module already has health monitoring
        if self._has_health_monitoring(content):
            logger.info(f"  ✅ {module_path.name} already has health monitoring")
            return
        
        # Parse AST to find classes
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"  ❌ Syntax error in {module_path.name}: {e}")
            return
        
        # Find ReflectiveModule classes
        classes = self._find_reflective_module_classes(tree)
        
        if not classes:
            logger.info(f"  ⚠️  {module_path.name} has no ReflectiveModule classes")
            return
        
        # Enhance health monitoring for each class
        enhanced_content = self._enhance_health_monitoring(content, classes)
        
        # Write enhanced content
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        logger.info(f"  ✅ Enhanced health monitoring for {module_path.name}")
        self.modules_fixed += 1
    
    def _has_health_monitoring(self, content: str) -> bool:
        """Check if module has comprehensive health monitoring"""
        # Check for health monitoring indicators
        health_indicators = [
            "def check_health(self) -> ModuleHealth:",
            "def get_metrics(self) -> Dict[str, Any]:",
            "ModuleHealth.HEALTHY",
            "ModuleHealth.DEGRADED",
            "ModuleHealth.UNHEALTHY",
            "uptime",
            "error_count",
            "success_rate"
        ]
        
        return all(indicator in content for indicator in health_indicators)
    
    def _find_reflective_module_classes(self, tree: ast.AST) -> List[str]:
        """Find ReflectiveModule classes in AST"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'ReflectiveModule':
                        classes.append(node.name)
                        break
                    elif isinstance(base, ast.Attribute):
                        if base.attr == 'ReflectiveModule':
                            classes.append(node.name)
                            break
        
        return classes
    
    def _enhance_health_monitoring(self, content: str, classes: List[str]) -> str:
        """Enhance health monitoring for classes"""
        enhanced_content = content
        
        for class_name in classes:
            # Enhance check_health method
            enhanced_content = self._enhance_check_health(enhanced_content, class_name)
            
            # Enhance get_metrics method
            enhanced_content = self._enhance_get_metrics(enhanced_content, class_name)
        
        return enhanced_content
    
    def _enhance_check_health(self, content: str, class_name: str) -> str:
        """Enhance check_health method for a class"""
        # Find the class definition
        lines = content.split('\n')
        in_class = False
        class_indent = 0
        method_start = -1
        method_end = -1
        
        for i, line in enumerate(lines):
            if f"class {class_name}" in line:
                in_class = True
                class_indent = len(line) - len(line.lstrip())
            elif in_class and line.strip() and not line.startswith(' ' * (class_indent + 1)):
                in_class = False
            elif in_class and "def check_health(self) -> ModuleHealth:" in line:
                method_start = i
                method_indent = len(line) - len(line.lstrip())
                
                # Find method end
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ' * (method_indent + 1)):
                        method_end = j
                        break
                
                if method_end == -1:
                    method_end = len(lines)
                
                break
        
        if method_start == -1:
            return content
        
        # Replace the method with enhanced version
        enhanced_method = f"""    def check_health(self) -> ModuleHealth:
        \"\"\"Check module health with comprehensive monitoring\"\"\"
        try:
            # Basic health checks
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            
            # Check uptime
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            
            # Check error rate
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            
            # Determine health status
            if error_rate > 0.5:  # >50% error rate
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:  # >10% error rate
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
                
        except Exception as e:
            logger.error(f"Health check failed for {class_name}: {e}")
            return ModuleHealth.UNHEALTHY"""
        
        # Replace the method
        new_lines = lines[:method_start] + [enhanced_method] + lines[method_end:]
        return '\n'.join(new_lines)
    
    def _enhance_get_metrics(self, content: str, class_name: str) -> str:
        """Enhance get_metrics method for a class"""
        # Find the class definition
        lines = content.split('\n')
        in_class = False
        class_indent = 0
        method_start = -1
        method_end = -1
        
        for i, line in enumerate(lines):
            if f"class {class_name}" in line:
                in_class = True
                class_indent = len(line) - len(line.lstrip())
            elif in_class and line.strip() and not line.startswith(' ' * (class_indent + 1)):
                in_class = False
            elif in_class and "def get_metrics(self) -> Dict[str, Any]:" in line:
                method_start = i
                method_indent = len(line) - len(line.lstrip())
                
                # Find method end
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ' * (method_indent + 1)):
                        method_end = j
                        break
                
                if method_end == -1:
                    method_end = len(lines)
                
                break
        
        if method_start == -1:
            return content
        
        # Replace the method with enhanced version
        enhanced_method = f"""    def get_metrics(self) -> Dict[str, Any]:
        \"\"\"Get comprehensive module metrics\"\"\"
        try:
            # Basic metrics
            uptime = (datetime.now() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 0)
            success_count = total_operations - error_count
            
            # Calculate rates
            success_rate = (success_count / total_operations) if total_operations > 0 else 1.0
            error_rate = (error_count / total_operations) if total_operations > 0 else 0.0
            
            # Health status
            health_status = self.check_health()
            
            return {{
                'uptime_seconds': uptime,
                'total_operations': total_operations,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'health_status': health_status.value,
                'module_id': getattr(self, 'module_id', 'unknown'),
                'version': getattr(self, 'version', 'unknown'),
                'last_updated': datetime.now().isoformat()
            }}
        except Exception as e:
            logger.error(f"Metrics collection failed for {class_name}: {e}")
            return {{
                'error': str(e),
                'health_status': 'UNHEALTHY',
                'last_updated': datetime.now().isoformat()
            }}"""
        
        # Replace the method
        new_lines = lines[:method_start] + [enhanced_method] + lines[method_end:]
        return '\n'.join(new_lines)
    
    def _generate_report(self, start_time: datetime):
        """Generate Beast Mode report"""
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("")
        logger.info("🎯 BEAST MODE HEALTH MONITORING COMPLETION REPORT")
        logger.info("=" * 60)
        logger.info(f"⏱️  Duration: {duration:.1f} seconds")
        logger.info(f"📊 Modules Processed: {self.modules_processed}")
        logger.info(f"✅ Modules Enhanced: {self.modules_fixed}")
        logger.info(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            logger.info("\n🚨 ERRORS:")
            for error in self.errors:
                logger.info(f"  - {error}")
        
        logger.info(f"\n🎉 SUCCESS RATE: {(self.modules_fixed/self.modules_processed*100):.1f}%")
        logger.info("=" * 60)

def main():
    """Main execution function"""
    beast_mode = HealthMonitoringBeastMode()
    success = beast_mode.run()
    
    if success:
        logger.info("🚀 Beast Mode Health Monitoring completed successfully!")
        return 0
    else:
        logger.error("❌ Beast Mode Health Monitoring failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
