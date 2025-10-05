#!/usr/bin/env python3
"""
DAG Orchestration Integration Layer Validation Script
====================================================

Comprehensive validation of all integration layer components:
- ACE Reporter Integration
- AI Memory Palace Integration
- System Integration Framework
- Task List Converter
- Integration Health Monitor

Author: Beast Mode Framework
Date: 2025-01-27
"""

import asyncio
import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationLayerValidator:
    """Comprehensive validator for DAG orchestration integration layer."""
    
    def __init__(self):
        self.validation_results = {}
        self.start_time = datetime.now()
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of all integration components."""
        logger.info("🚀 Starting DAG Orchestration Integration Layer Validation")
        logger.info("=" * 70)
        
        validation_results = {
            "validation_start": self.start_time.isoformat(),
            "component_validations": {},
            "integration_tests": {},
            "health_monitoring_tests": {},
            "overall_status": "UNKNOWN",
            "summary": {}
        }
        
        try:
            # 1. Validate component imports
            logger.info("📦 Validating component imports...")
            import_results = await self._validate_imports()
            validation_results["component_validations"]["imports"] = import_results
            
            if not import_results["success"]:
                validation_results["overall_status"] = "FAILED"
                validation_results["summary"]["error"] = "Import validation failed"
                return validation_results
            
            # 2. Validate ACE Reporter Integration
            logger.info("📡 Validating ACE Reporter Integration...")
            ace_results = await self._validate_ace_reporter_integration()
            validation_results["component_validations"]["ace_reporter"] = ace_results
            
            # 3. Validate AI Memory Palace Integration
            logger.info("🧠 Validating AI Memory Palace Integration...")
            memory_results = await self._validate_ai_memory_palace_integration()
            validation_results["component_validations"]["memory_palace"] = memory_results
            
            # 4. Validate System Integration Framework
            logger.info("🔧 Validating System Integration Framework...")
            framework_results = await self._validate_system_integration_framework()
            validation_results["component_validations"]["system_framework"] = framework_results
            
            # 5. Validate Task List Converter
            logger.info("📋 Validating Task List Converter...")
            converter_results = await self._validate_task_list_converter()
            validation_results["component_validations"]["task_converter"] = converter_results
            
            # 6. Validate Integration Health Monitor
            logger.info("🏥 Validating Integration Health Monitor...")
            health_results = await self._validate_integration_health_monitor()
            validation_results["component_validations"]["health_monitor"] = health_results
            
            # 7. Run integration tests
            logger.info("🔗 Running integration tests...")
            integration_results = await self._run_integration_tests()
            validation_results["integration_tests"] = integration_results
            
            # 8. Run health monitoring tests
            logger.info("📊 Running health monitoring tests...")
            monitoring_results = await self._run_health_monitoring_tests()
            validation_results["health_monitoring_tests"] = monitoring_results
            
            # 9. Calculate overall status
            validation_results["overall_status"] = self._calculate_overall_status(validation_results)
            validation_results["summary"] = self._generate_summary(validation_results)
            
            # 10. Generate final report
            validation_results["validation_end"] = datetime.now().isoformat()
            validation_results["total_duration_seconds"] = (
                datetime.now() - self.start_time
            ).total_seconds()
            
            logger.info("✅ Integration layer validation completed")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Validation failed with error: {e}")
            validation_results["overall_status"] = "ERROR"
            validation_results["summary"] = {"error": str(e)}
            return validation_results
    
    async def _validate_imports(self) -> Dict[str, Any]:
        """Validate that all integration components can be imported."""
        import_results = {
            "success": True,
            "imported_components": [],
            "failed_imports": [],
            "details": {}
        }
        
        components_to_import = [
            ("ace_reporter_integration", "src.dag_orchestration.integration.ace_reporter_integration"),
            ("ai_memory_palace_integration", "src.dag_orchestration.integration.ai_memory_palace_integration"),
            ("system_integration_framework", "src.dag_orchestration.integration.system_integration_framework"),
            ("task_list_converter", "src.dag_orchestration.integration.task_list_converter"),
            ("integration_health_monitor", "src.dag_orchestration.integration.integration_health_monitor")
        ]
        
        for component_name, module_path in components_to_import:
            try:
                module = __import__(module_path, fromlist=[''])
                import_results["imported_components"].append(component_name)
                import_results["details"][component_name] = {
                    "status": "SUCCESS",
                    "module_path": module_path
                }
                logger.info(f"  ✅ {component_name} imported successfully")
                
            except ImportError as e:
                import_results["failed_imports"].append(component_name)
                import_results["details"][component_name] = {
                    "status": "FAILED",
                    "error": str(e)
                }
                import_results["success"] = False
                logger.error(f"  ❌ {component_name} import failed: {e}")
        
        return import_results
    
    async def _validate_ace_reporter_integration(self) -> Dict[str, Any]:
        """Validate ACE Reporter Integration functionality."""
        try:
            from src.dag_orchestration.integration.ace_reporter_integration import (
                create_ace_reporter_integration
            )
            
            ace_reporter = create_ace_reporter_integration()
            
            # Test basic functionality
            health = ace_reporter.get_health_status()
            info = ace_reporter.get_module_info()
            
            # Test broadcasting functionality
            execution_id = "validation_test_001"
            broadcast_start = await ace_reporter.broadcast_execution_start(
                execution_id, 3, {"estimated_duration": 120}
            )
            
            broadcast_task = await ace_reporter.broadcast_task_completion(
                execution_id, "task_1", "completed", 30.0
            )
            
            broadcast_summary = await ace_reporter.broadcast_execution_summary(
                execution_id, {"success_rate": 1.0, "task_count": 3}
            )
            
            # Get statistics
            stats = ace_reporter.get_broadcast_statistics()
            
            return {
                "status": "SUCCESS",
                "health_score": health.health_score,
                "module_info": info,
                "broadcast_tests": {
                    "execution_start": broadcast_start,
                    "task_completion": broadcast_task,
                    "execution_summary": broadcast_summary
                },
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"ACE Reporter validation failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def _validate_ai_memory_palace_integration(self) -> Dict[str, Any]:
        """Validate AI Memory Palace Integration functionality."""
        try:
            from src.dag_orchestration.integration.ai_memory_palace_integration import (
                create_ai_memory_palace_integration
            )
            
            memory_palace = create_ai_memory_palace_integration()
            
            # Test basic functionality
            health = memory_palace.get_health_status()
            info = memory_palace.get_module_info()
            
            # Test pattern storage
            execution_id = "validation_pattern_001"
            pattern_data = {
                "task_count": 5,
                "strategy": "parallel",
                "complexity": "medium"
            }
            performance_metrics = {
                "duration": 180,
                "efficiency": 1.8,
                "resource_usage": 0.6
            }
            
            store_result = await memory_palace.store_execution_pattern(
                execution_id, pattern_data, performance_metrics
            )
            
            # Test pattern retrieval
            similar_patterns = await memory_palace.retrieve_similar_patterns(
                pattern_data, limit=5
            )
            
            # Test learning
            insights = await memory_palace.learn_from_execution(
                execution_id, performance_metrics
            )
            
            # Get statistics
            stats = memory_palace.get_learning_statistics()
            
            return {
                "status": "SUCCESS",
                "health_score": health.health_score,
                "module_info": info,
                "pattern_tests": {
                    "store_pattern": store_result,
                    "retrieve_patterns": len(similar_patterns),
                    "learning_insights": len(insights.get("optimization_suggestions", []))
                },
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"AI Memory Palace validation failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def _validate_system_integration_framework(self) -> Dict[str, Any]:
        """Validate System Integration Framework functionality."""
        try:
            from src.dag_orchestration.integration.system_integration_framework import (
                create_system_integration_framework
            )
            
            framework = create_system_integration_framework()
            
            # Test basic functionality
            health = framework.get_health_status()
            info = framework.get_module_info()
            
            # Test sequential to DAG conversion
            sequential_tasks = [
                {"id": "task_1", "name": "Initialize", "function": "init"},
                {"id": "task_2", "name": "Process", "function": "process"},
                {"id": "task_3", "name": "Finalize", "function": "finalize"}
            ]
            
            dag_tasks = framework.convert_sequential_to_dag(sequential_tasks)
            
            # Test legacy integration
            integration_result = await framework.integrate_with_legacy_executor(dag_tasks)
            
            # Test system compatibility
            compatibility = framework.validate_system_compatibility()
            
            # Test deployment configuration
            deployment_config = framework.create_deployment_configuration()
            
            # Get statistics
            stats = framework.get_integration_statistics()
            
            return {
                "status": "SUCCESS",
                "health_score": health.health_score,
                "module_info": info,
                "conversion_tests": {
                    "dag_tasks_count": len(dag_tasks),
                    "legacy_integration": integration_result.success,
                    "system_compatibility": compatibility["overall_compatibility"]
                },
                "deployment_config": {
                    "components_count": len(deployment_config["components"]),
                    "integration_settings": deployment_config["integration_settings"]
                },
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"System Integration Framework validation failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def _validate_task_list_converter(self) -> Dict[str, Any]:
        """Validate Task List Converter functionality."""
        try:
            from src.dag_orchestration.integration.task_list_converter import (
                create_task_list_converter
            )
            
            converter = create_task_list_converter()
            
            # Create sample spec content
            sample_spec = """
# Implementation Plan

- [x] 1. Set up infrastructure
  - Create base components
  - _Requirements: 1.1, 1.2_

- [ ] 2. Implement core functionality
- [ ] 2.1 Build execution engine
  - Create parallel execution capabilities
  - _Requirements: 2.1, 2.2_

- [ ] 2.2 Add monitoring
  - Implement health monitoring
  - _Requirements: 2.3_

- [ ] 3. Deploy system
  - Deploy to production
  - _Requirements: 3.1_
"""
            
            # Test with temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(sample_spec)
                temp_path = f.name
            
            try:
                # Test conversion
                result = converter.convert_spec_tasks(temp_path)
                
                # Test export
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    export_path = f.name
                
                export_success = False
                if result.success:
                    export_success = converter.export_dag_definition(result, export_path)
                
                return {
                    "status": "SUCCESS" if result.success else "FAILED",
                    "conversion_result": {
                        "success": result.success,
                        "task_count": len(result.task_definitions),
                        "dag_validation": result.dag_validation,
                        "errors": result.errors,
                        "warnings": result.warnings
                    },
                    "export_result": {
                        "success": export_success,
                        "export_path": export_path if export_success else None
                    }
                }
                
            finally:
                Path(temp_path).unlink()
                if 'export_path' in locals():
                    Path(export_path).unlink()
            
        except Exception as e:
            logger.error(f"Task List Converter validation failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def _validate_integration_health_monitor(self) -> Dict[str, Any]:
        """Validate Integration Health Monitor functionality."""
        try:
            from src.dag_orchestration.integration.integration_health_monitor import (
                create_integration_health_monitor
            )
            
            monitor = create_integration_health_monitor()
            
            # Test basic functionality
            health = monitor.get_health_status()
            info = monitor.get_module_info()
            
            # Test component registration (mock component)
            class MockComponent:
                def get_health_status(self):
                    from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
                    return ModuleHealth(
                        module_id="mock_component",
                        status=ModuleStatus.HEALTHY,
                        health_score=0.95,
                        issues=[],
                        last_check=datetime.now(),
                        uptime_seconds=100
                    )
                
                def get_module_info(self):
                    return {
                        "module_id": "mock_component",
                        "name": "Mock Component",
                        "version": "1.0.0"
                    }
            
            mock_component = MockComponent()
            register_result = monitor.register_component("mock_component", mock_component)
            
            # Test health check
            health_report = await monitor.perform_health_check()
            
            # Test health summary
            health_summary = monitor.get_health_summary()
            
            # Test unregistration
            unregister_result = monitor.unregister_component("mock_component")
            
            return {
                "status": "SUCCESS",
                "health_score": health.health_score,
                "module_info": info,
                "monitoring_tests": {
                    "component_registration": register_result,
                    "health_check": {
                        "overall_health_score": health_report.overall_health_score,
                        "system_status": health_report.system_status,
                        "components_checked": len(health_report.component_health)
                    },
                    "component_unregistration": unregister_result
                },
                "health_summary": health_summary
            }
            
        except Exception as e:
            logger.error(f"Integration Health Monitor validation failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests."""
        try:
            # Import all components
            from src.dag_orchestration.integration.ace_reporter_integration import create_ace_reporter_integration
            from src.dag_orchestration.integration.ai_memory_palace_integration import create_ai_memory_palace_integration
            from src.dag_orchestration.integration.system_integration_framework import create_system_integration_framework
            from src.dag_orchestration.integration.task_list_converter import create_task_list_converter
            
            # Create components
            ace_reporter = create_ace_reporter_integration()
            memory_palace = create_ai_memory_palace_integration()
            system_framework = create_system_integration_framework()
            task_converter = create_task_list_converter()
            
            # Test end-to-end workflow
            execution_id = "integration_test_e2e"
            
            # 1. Convert tasks
            sample_tasks = [
                {"id": "task_1", "name": "Initialize", "function": "init"},
                {"id": "task_2", "name": "Process", "function": "process"}
            ]
            dag_tasks = system_framework.convert_sequential_to_dag(sample_tasks)
            
            # 2. Broadcast execution start
            broadcast_start = await ace_reporter.broadcast_execution_start(
                execution_id, len(dag_tasks)
            )
            
            # 3. Store execution pattern
            pattern_stored = await memory_palace.store_execution_pattern(
                execution_id,
                {"task_count": len(dag_tasks), "type": "integration_test"},
                {"duration": 60, "efficiency": 1.5}
            )
            
            # 4. Broadcast completion
            broadcast_summary = await ace_reporter.broadcast_execution_summary(
                execution_id, {"success_rate": 1.0, "task_count": len(dag_tasks)}
            )
            
            return {
                "status": "SUCCESS",
                "workflow_tests": {
                    "task_conversion": len(dag_tasks) > 0,
                    "execution_broadcast": broadcast_start,
                    "pattern_storage": pattern_stored,
                    "summary_broadcast": broadcast_summary
                },
                "component_interaction": "All components interacted successfully"
            }
            
        except Exception as e:
            logger.error(f"Integration tests failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def _run_health_monitoring_tests(self) -> Dict[str, Any]:
        """Run health monitoring tests."""
        try:
            from src.dag_orchestration.integration.integration_health_monitor import (
                setup_integration_monitoring
            )
            
            # Set up comprehensive monitoring
            monitor = await setup_integration_monitoring()
            
            # Perform health check
            health_report = await monitor.perform_health_check()
            
            # Export health report
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                export_path = f.name
            
            export_success = monitor.export_health_report(export_path)
            
            try:
                return {
                    "status": "SUCCESS",
                    "monitoring_setup": {
                        "components_monitored": len(monitor._monitored_components),
                        "overall_health_score": health_report.overall_health_score,
                        "system_status": health_report.system_status
                    },
                    "health_report_export": {
                        "success": export_success,
                        "export_path": export_path if export_success else None
                    }
                }
            finally:
                if export_success:
                    Path(export_path).unlink()
            
        except Exception as e:
            logger.error(f"Health monitoring tests failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    def _calculate_overall_status(self, validation_results: Dict[str, Any]) -> str:
        """Calculate overall validation status."""
        component_validations = validation_results.get("component_validations", {})
        integration_tests = validation_results.get("integration_tests", {})
        health_monitoring_tests = validation_results.get("health_monitoring_tests", {})
        
        # Check component validations (exclude imports from component count)
        failed_components = []
        successful_components = []
        
        for component, result in component_validations.items():
            if component == "imports":  # Skip imports validation in component status
                continue
                
            if isinstance(result, dict):
                if result.get("status") == "FAILED":
                    failed_components.append(component)
                elif result.get("status") == "SUCCESS":
                    successful_components.append(component)
        
        # Check integration tests
        integration_failed = integration_tests.get("status") == "FAILED"
        
        # Check health monitoring tests
        monitoring_failed = health_monitoring_tests.get("status") == "FAILED"
        
        # Check imports separately
        imports_failed = not component_validations.get("imports", {}).get("success", True)
        
        if failed_components or integration_failed or monitoring_failed or imports_failed:
            return "FAILED"
        elif (len(successful_components) > 0 and 
              integration_tests.get("status") == "SUCCESS" and 
              health_monitoring_tests.get("status") == "SUCCESS"):
            return "SUCCESS"
        else:
            return "PARTIAL"
    
    def _generate_summary(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary."""
        component_validations = validation_results.get("component_validations", {})
        
        successful_components = []
        failed_components = []
        
        for component, result in component_validations.items():
            if component == "imports":  # Skip imports in component summary
                continue
                
            if isinstance(result, dict):
                if result.get("status") == "SUCCESS":
                    successful_components.append(component)
                elif result.get("status") == "FAILED":
                    failed_components.append(component)
        
        total_components = len(component_validations) - 1  # Exclude imports from count
        
        return {
            "total_components": total_components,
            "successful_components": len(successful_components),
            "failed_components": len(failed_components),
            "success_rate": len(successful_components) / max(total_components, 1),
            "successful_component_list": successful_components,
            "failed_component_list": failed_components,
            "imports_successful": component_validations.get("imports", {}).get("success", False),
            "integration_tests_passed": validation_results.get("integration_tests", {}).get("status") == "SUCCESS",
            "health_monitoring_tests_passed": validation_results.get("health_monitoring_tests", {}).get("status") == "SUCCESS"
        }


async def main():
    """Main validation function."""
    validator = IntegrationLayerValidator()
    
    try:
        results = await validator.run_comprehensive_validation()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎯 DAG ORCHESTRATION INTEGRATION LAYER VALIDATION SUMMARY")
        print("=" * 70)
        
        print(f"Overall Status: {results['overall_status']}")
        print(f"Validation Duration: {results.get('total_duration_seconds', 0):.2f} seconds")
        
        summary = results.get("summary", {})
        print(f"Components Tested: {summary.get('total_components', 0)}")
        print(f"Successful Components: {summary.get('successful_components', 0)}")
        print(f"Failed Components: {summary.get('failed_components', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        
        if summary.get("successful_component_list"):
            print(f"✅ Successful: {', '.join(summary['successful_component_list'])}")
        
        if summary.get("failed_component_list"):
            print(f"❌ Failed: {', '.join(summary['failed_component_list'])}")
        
        print(f"Integration Tests: {'✅ PASSED' if summary.get('integration_tests_passed') else '❌ FAILED'}")
        print(f"Health Monitoring Tests: {'✅ PASSED' if summary.get('health_monitoring_tests_passed') else '❌ FAILED'}")
        
        # Export detailed results
        output_file = f"dag_orchestration_integration_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results exported to: {output_file}")
        
        # Return appropriate exit code
        if results['overall_status'] == "SUCCESS":
            print("\n🎉 All integration layer components validated successfully!")
            return 0
        else:
            print("\n⚠️  Some validation issues found. Check detailed results.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)