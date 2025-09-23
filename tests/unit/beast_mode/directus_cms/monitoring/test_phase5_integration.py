"""
Heuristic Tests for Phase 5: Beast Mode Integration Components

Tests health monitoring, structured logging, PDCA orchestration, and backup/recovery.
Focuses on integration patterns and Beast Mode compliance.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.beast_mode.directus_cms.monitoring.health_monitor import DirectusHealthMonitor
from src.beast_mode.directus_cms.monitoring.structured_logger import StructuredLogger, correlation_context
from src.beast_mode.directus_cms.monitoring.pdca_orchestrator import PDCAOrchestrator, PDCAPhase
from src.beast_mode.directus_cms.monitoring.backup_recovery import BackupRecoverySystem
from src.beast_mode.directus_cms.orchestrator import DirectusCMSOrchestrator

from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestPhase5Integration(unittest.TestCase):
    """Test Phase 5 Beast Mode integration components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.database_url = "postgresql://test:test@localhost:5432/test_db"
        
        # Initialize components
        self.health_monitor = DirectusHealthMonitor(self.database_url)
        self.structured_logger = StructuredLogger("test_logger")
        self.pdca_orchestrator = PDCAOrchestrator(self.structured_logger)
        self.backup_recovery = BackupRecoverySystem(
            self.database_url, 
            backup_directory=self.temp_dir,
            logger=self.structured_logger
        )
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_health_monitor_beast_mode_compliance(self):
        """Test health monitor Beast Mode compliance"""
        # Test ReflectiveModule implementation
        module_info = self.health_monitor.get_module_info()
        self.assertEqual(module_info["module_id"], "directus_health_monitor")
        self.assertEqual(module_info["beast_mode_compliance"], "full")
        
        # Test capabilities
        capabilities = self.health_monitor.get_capabilities()
        self.assertIn(ModuleCapability.MONITORING, capabilities)
        
        # Test health endpoints
        health_response = self.health_monitor.health_endpoint()
        self.assertIn("status", health_response)
        self.assertIn("timestamp", health_response)
        self.assertIn("checks", health_response)
        
        ready_response = self.health_monitor.ready_endpoint()
        self.assertIn("status", ready_response)
        
        metrics_response = self.health_monitor.metrics_endpoint()
        self.assertIn("timestamp", metrics_response)
    
    def test_structured_logger_correlation_tracking(self):
        """Test structured logger correlation ID tracking"""
        # Test correlation context management
        with self.structured_logger.correlation_context_manager() as correlation_id:
            self.assertIsNotNone(correlation_id)
            self.assertEqual(correlation_context.get_correlation_id(), correlation_id)
            
            # Test structured logging
            self.structured_logger.info("Test message", test_data="value")
            
            # Test operation tracking
            op_id = self.structured_logger.operation_start("test_operation", param="value")
            self.assertEqual(op_id, correlation_id)
            
            self.structured_logger.operation_checkpoint("test_operation", "checkpoint1")
            self.structured_logger.operation_end("test_operation", True)
        
        # Correlation ID should be cleared
        self.assertIsNone(correlation_context.get_correlation_id())
        
        # Test log aggregation
        logs = self.structured_logger.get_log_aggregation(correlation_id=correlation_id)
        self.assertGreater(len(logs), 0)
        
        # All logs should have the same correlation ID
        for log in logs:
            self.assertEqual(log.get("correlation_id"), correlation_id)
    
    def test_pdca_orchestrator_systematic_execution(self):
        """Test PDCA orchestrator systematic execution"""
        # Define mock PDCA functions
        def plan_func():
            return {"plan_data": "test_plan", "steps": ["step1", "step2"]}
        
        def do_func(plan_data):
            return {"do_data": "executed", "plan": plan_data}
        
        def check_func(do_data):
            return {"check_data": "validated", "do": do_data}
        
        def act_func(check_data):
            return {"improvements": ["improvement1", "improvement2"], "check": check_data}
        
        # Execute PDCA cycle
        cycle = self.pdca_orchestrator.execute_pdca_cycle(
            "test_operation",
            plan_func,
            do_func,
            check_func,
            act_func
        )
        
        # Validate cycle execution
        self.assertEqual(cycle.operation, "test_operation")
        self.assertTrue(cycle.overall_success)
        self.assertEqual(len(cycle.phases), 4)
        
        # Validate each phase
        for phase in PDCAPhase:
            self.assertIn(phase, cycle.phases)
            self.assertTrue(cycle.phases[phase].success)
        
        # Validate improvement actions
        self.assertEqual(cycle.improvement_actions, ["improvement1", "improvement2"])
        
        # Test operation analysis
        analysis = self.pdca_orchestrator.get_operation_analysis("test_operation")
        self.assertEqual(analysis["operation"], "test_operation")
        self.assertEqual(analysis["total_cycles"], 1)
        self.assertEqual(analysis["success_rate_percent"], 100.0)
    
    def test_backup_recovery_system_functionality(self):
        """Test backup and recovery system functionality"""
        # Test full backup creation
        backup_result = self.backup_recovery.create_full_backup()
        self.assertTrue(backup_result["success"])
        self.assertIn("backup_id", backup_result)
        
        backup_id = backup_result["backup_id"]
        
        # Verify backup files exist
        backup_path = Path(self.temp_dir) / backup_id
        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / "database.sql").exists())
        self.assertTrue((backup_path / "configuration").exists())
        
        # Test backup history
        history = self.backup_recovery.get_backup_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["backup_id"], backup_id)
        
        # Test restore functionality
        restore_result = self.backup_recovery.restore_from_backup(backup_id)
        self.assertTrue(restore_result["success"])
        self.assertEqual(restore_result["backup_id"], backup_id)
        
        # Test cleanup
        cleanup_result = self.backup_recovery.cleanup_old_backups(retention_days=0)
        self.assertTrue(cleanup_result["success"])
        self.assertEqual(cleanup_result["cleaned_count"], 1)
    
    def test_orchestrator_phase5_integration(self):
        """Test main orchestrator Phase 5 integration"""
        orchestrator = DirectusCMSOrchestrator(
            database_url=self.database_url,
            repository_root=self.temp_dir
        )
        
        # Test component initialization
        self.assertIsNotNone(orchestrator.health_monitor)
        self.assertIsNotNone(orchestrator.structured_logger)
        self.assertIsNotNone(orchestrator.pdca_orchestrator)
        self.assertIsNotNone(orchestrator.backup_recovery)
        
        # Test module info includes all components
        module_info = orchestrator.get_module_info()
        components = module_info["components"]
        
        phase5_components = [
            "health_monitor", 
            "structured_logger", 
            "pdca_orchestrator", 
            "backup_recovery"
        ]
        
        for component in phase5_components:
            self.assertIn(component, components)
        
        # Test health aggregation
        health_status = orchestrator.get_health_status()
        self.assertIsNotNone(health_status)
        self.assertIn(health_status.status, [ModuleStatus.HEALTHY, ModuleStatus.WARNING])
        
        # Test PDCA integration
        pdca_result = orchestrator.execute_pdca_cycle("full_setup")
        self.assertIn("operation", pdca_result)
        self.assertIn("success", pdca_result)
    
    def test_cross_component_integration(self):
        """Test integration between Phase 5 components"""
        # Test PDCA with structured logging
        with self.structured_logger.correlation_context_manager() as correlation_id:
            
            def plan_func():
                self.structured_logger.info("Planning phase", phase="plan")
                return {"plan": "test"}
            
            def do_func(plan_data):
                self.structured_logger.info("Execution phase", phase="do")
                return {"result": "executed"}
            
            def check_func(do_data):
                self.structured_logger.info("Check phase", phase="check")
                return {"validation": "passed"}
            
            def act_func(check_data):
                self.structured_logger.info("Act phase", phase="act")
                return {"improvements": ["optimize"]}
            
            # Execute PDCA with logging
            cycle = self.pdca_orchestrator.execute_pdca_cycle(
                "integrated_operation",
                plan_func,
                do_func,
                check_func,
                act_func
            )
            
            self.assertTrue(cycle.overall_success)
            
            # Verify logs were created with correlation
            logs = self.structured_logger.get_log_aggregation(
                correlation_id=correlation_id,
                operation="integrated_operation"
            )
            
            # Should have logs from PDCA phases
            phase_logs = [log for log in logs if "phase" in log]
            self.assertGreaterEqual(len(phase_logs), 4)  # At least one per phase
    
    def test_error_handling_and_degradation(self):
        """Test error handling and graceful degradation"""
        # Test health monitor with simulated failures
        with patch.object(self.health_monitor, '_check_database_health') as mock_db_check:
            mock_db_check.side_effect = Exception("Database connection failed")
            
            health_response = self.health_monitor.health_endpoint()
            self.assertEqual(health_response["status"], "error")
            self.assertIn("error", health_response)
        
        # Test PDCA with failing phases
        def failing_plan():
            raise ValueError("Plan failed")
        
        def success_do(plan_data):
            return {"result": "ok"}
        
        def success_check(do_data):
            return {"validation": "ok"}
        
        def success_act(check_data):
            return {"improvements": []}
        
        cycle = self.pdca_orchestrator.execute_pdca_cycle(
            "failing_operation",
            failing_plan,
            success_do,
            success_check,
            success_act
        )
        
        self.assertFalse(cycle.overall_success)
        self.assertFalse(cycle.phases[PDCAPhase.PLAN].success)
        self.assertIn("Plan failed", cycle.phases[PDCAPhase.PLAN].error)
        
        # Test backup recovery with invalid backup
        restore_result = self.backup_recovery.restore_from_backup("nonexistent_backup")
        self.assertFalse(restore_result["success"])
        self.assertIn("not found", restore_result["error"])
    
    def test_performance_and_metrics(self):
        """Test performance monitoring and metrics collection"""
        # Test health monitor metrics caching
        start_time = datetime.now()
        
        # First call should collect metrics
        metrics1 = self.health_monitor.metrics_endpoint()
        
        # Second call within 30 seconds should use cache
        metrics2 = self.health_monitor.metrics_endpoint()
        
        # Should be the same (cached)
        self.assertEqual(metrics1["timestamp"], metrics2["timestamp"])
        
        # Test structured logger performance analysis
        operation_name = "performance_test"
        
        # Create multiple operation instances
        for i in range(3):
            with self.structured_logger.correlation_context_manager():
                self.structured_logger.operation_start(operation_name)
                self.structured_logger.operation_end(operation_name, True)
        
        # Analyze performance
        analysis = self.structured_logger.analyze_operation_performance(operation_name)
        self.assertEqual(analysis["operation"], operation_name)
        self.assertEqual(analysis["total_instances"], 3)
        self.assertEqual(analysis["successful_instances"], 3)
        
        # Test PDCA continuous improvement reporting
        improvement_report = self.pdca_orchestrator.get_continuous_improvement_report()
        self.assertIn("report_timestamp", improvement_report)
        self.assertIn("overall_statistics", improvement_report)
        self.assertIn("pdca_effectiveness", improvement_report)


class TestPhase5HeuristicValidation(unittest.TestCase):
    """Heuristic validation tests for Phase 5 patterns"""
    
    def test_beast_mode_pattern_compliance(self):
        """Test Beast Mode pattern compliance across Phase 5 components"""
        components = [
            DirectusHealthMonitor(),
            StructuredLogger("test"),
            PDCAOrchestrator(),
            BackupRecoverySystem()
        ]
        
        for component in components:
            # Test ReflectiveModule inheritance
            self.assertTrue(hasattr(component, 'get_module_info'))
            self.assertTrue(hasattr(component, 'get_health_status'))
            self.assertTrue(hasattr(component, 'get_capabilities'))
            
            # Test module info structure
            module_info = component.get_module_info()
            self.assertIn("module_id", module_info)
            self.assertIn("module_name", module_info)
            self.assertIn("version", module_info)
            
            # Test capabilities
            capabilities = component.get_capabilities()
            self.assertIsInstance(capabilities, list)
            self.assertGreater(len(capabilities), 0)
    
    def test_file_size_compliance(self):
        """Test file size compliance for Phase 5 components"""
        import inspect
        
        components = [
            DirectusHealthMonitor,
            StructuredLogger,
            PDCAOrchestrator,
            BackupRecoverySystem
        ]
        
        for component_class in components:
            # Get source file
            source_file = inspect.getfile(component_class)
            
            # Count lines
            with open(source_file, 'r') as f:
                lines = f.readlines()
            
            # Filter out empty lines and comments
            code_lines = [
                line for line in lines 
                if line.strip() and not line.strip().startswith('#')
            ]
            
            # Should be under 300 lines (allowing some buffer for Phase 5 complexity)
            self.assertLess(
                len(code_lines), 
                300, 
                f"{component_class.__name__} has {len(code_lines)} code lines, exceeds 300 line limit"
            )
    
    def test_systematic_error_handling(self):
        """Test systematic error handling patterns"""
        logger = StructuredLogger("error_test")
        
        # Test error logging with correlation
        with logger.correlation_context_manager() as correlation_id:
            try:
                raise ValueError("Test error")
            except ValueError as e:
                logger.error("Operation failed", error=str(e), operation="test_op")
        
        # Verify error was logged with correlation
        error_logs = logger.get_log_aggregation(
            correlation_id=correlation_id,
            level="ERROR"
        )
        
        self.assertGreater(len(error_logs), 0)
        self.assertEqual(error_logs[0]["correlation_id"], correlation_id)
        self.assertIn("error", error_logs[0])
    
    def test_integration_consistency(self):
        """Test consistency across Phase 5 integrations"""
        # All components should use consistent patterns
        orchestrator = DirectusCMSOrchestrator()
        
        phase5_components = [
            orchestrator.health_monitor,
            orchestrator.structured_logger,
            orchestrator.pdca_orchestrator,
            orchestrator.backup_recovery
        ]
        
        # Test consistent module_id patterns
        for component in phase5_components:
            module_info = component.get_module_info()
            module_id = module_info["module_id"]
            
            # Should follow naming convention
            self.assertTrue(
                module_id.replace("_", "").isalnum(),
                f"Module ID {module_id} doesn't follow naming convention"
            )
            
            # Should have beast_mode_compliance
            self.assertIn("beast_mode_compliance", module_info)


if __name__ == '__main__':
    unittest.main()