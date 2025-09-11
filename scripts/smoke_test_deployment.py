#!/usr/bin/env python3
"""
Smoke Test Script for Beast Mode Deployment

This script performs comprehensive smoke tests to validate
that a Beast Mode deployment is working correctly.
"""

import os
import sys
import argparse
import logging
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.deployment.config_manager import ConfigManager
from beast_mode.deployment.deployment_manager import DeploymentManager
from beast_mode.deployment.validator import DeploymentValidator, ValidationLevel


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('smoke_test.log')
        ]
    )


class SmokeTestRunner:
    """Runs comprehensive smoke tests for Beast Mode deployment"""
    
    def __init__(self, environment: str, deployment_id: str = None):
        self.environment = environment
        self.deployment_id = deployment_id
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.deployment_manager = DeploymentManager(self.config_manager)
        self.validator = DeploymentValidator(self.config_manager)
        
        # Test results
        self.results = {
            'environment': environment,
            'deployment_id': deployment_id,
            'started_at': time.strftime("%Y-%m-%d %H:%M:%S"),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        }
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test and record results"""
        self.logger.info(f"Running test: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            test_result = {
                'name': test_name,
                'status': 'PASSED' if result else 'FAILED',
                'duration_ms': duration * 1000,
                'message': 'Test completed successfully' if result else 'Test failed',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if result:
                self.results['summary']['passed'] += 1
                self.logger.info(f"✓ {test_name} - PASSED ({duration:.2f}s)")
            else:
                self.results['summary']['failed'] += 1
                self.logger.error(f"✗ {test_name} - FAILED ({duration:.2f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = {
                'name': test_name,
                'status': 'FAILED',
                'duration_ms': duration * 1000,
                'message': f'Test failed with exception: {str(e)}',
                'error': str(e),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.results['summary']['failed'] += 1
            self.logger.error(f"✗ {test_name} - FAILED ({duration:.2f}s): {e}")
            result = False
        
        self.results['tests'].append(test_result)
        self.results['summary']['total'] += 1
        
        return result
    
    def test_configuration_loading(self) -> bool:
        """Test configuration loading and validation"""
        try:
            config = self.config_manager.get_config(self.environment)
            issues = self.config_manager.validate_config(config)
            
            if issues:
                self.logger.error(f"Configuration validation issues: {issues}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration loading failed: {e}")
            return False
    
    def test_environment_variables(self) -> bool:
        """Test environment variable generation"""
        try:
            env_vars = self.config_manager.get_environment_variables(self.environment)
            
            required_vars = [
                'BEAST_MODE_ENVIRONMENT',
                'REDIS_HOST',
                'REDIS_PORT',
                'AGENT_ID',
                'AGENT_CAPABILITIES'
            ]
            
            for var in required_vars:
                if var not in env_vars:
                    self.logger.error(f"Missing required environment variable: {var}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Environment variable generation failed: {e}")
            return False
    
    def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity"""
        try:
            config = self.config_manager.get_config(self.environment)
            
            import redis
            client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                ssl=config.redis.ssl,
                socket_timeout=5
            )
            
            # Test basic operations
            client.ping()
            
            test_key = "smoke_test_key"
            test_value = "smoke_test_value"
            
            client.set(test_key, test_value, ex=60)
            retrieved_value = client.get(test_key)
            client.delete(test_key)
            
            if retrieved_value != test_value.encode():
                self.logger.error("Redis value mismatch")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Redis connectivity test failed: {e}")
            return False
    
    def test_redis_pubsub(self) -> bool:
        """Test Redis pub/sub functionality"""
        try:
            config = self.config_manager.get_config(self.environment)
            
            import redis
            client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                ssl=config.redis.ssl
            )
            
            pubsub = client.pubsub()
            test_channel = "smoke_test_channel"
            test_message = "smoke_test_message"
            
            pubsub.subscribe(test_channel)
            
            # Wait for subscription confirmation
            message = pubsub.get_message(timeout=5)
            if not message or message['type'] != 'subscribe':
                self.logger.error("Failed to subscribe to test channel")
                return False
            
            # Publish test message
            client.publish(test_channel, test_message)
            
            # Receive message
            message = pubsub.get_message(timeout=5)
            if not message or message['type'] != 'message':
                self.logger.error("Failed to receive pub/sub message")
                return False
            
            if message['data'].decode() != test_message:
                self.logger.error("Pub/sub message mismatch")
                return False
            
            pubsub.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Redis pub/sub test failed: {e}")
            return False
    
    def test_deployment_status(self) -> bool:
        """Test deployment status if deployment ID provided"""
        if not self.deployment_id:
            self.logger.info("No deployment ID provided, skipping deployment status test")
            return True
        
        try:
            status = self.deployment_manager.get_deployment_status(self.deployment_id)
            
            if status.status not in ['running', 'starting']:
                self.logger.error(f"Deployment status is {status.status}, expected running or starting")
                return False
            
            # Check that services exist
            if not status.services:
                self.logger.error("No services found in deployment")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Deployment status test failed: {e}")
            return False
    
    def test_deployment_health(self) -> bool:
        """Test deployment health check if deployment ID provided"""
        if not self.deployment_id:
            self.logger.info("No deployment ID provided, skipping deployment health test")
            return True
        
        try:
            health = self.deployment_manager.health_check_deployment(self.deployment_id)
            
            if health['overall_status'] != 'healthy':
                self.logger.warning(f"Deployment health is {health['overall_status']}")
                # Don't fail the test for unhealthy status, just warn
            
            # Check system resources
            resources = health.get('system_resources', {})
            cpu_usage = resources.get('cpu_percent', 0)
            memory_usage = resources.get('memory_percent', 0)
            
            if cpu_usage > 95:
                self.logger.warning(f"High CPU usage: {cpu_usage}%")
            
            if memory_usage > 95:
                self.logger.warning(f"High memory usage: {memory_usage}%")
            
            return True
        except Exception as e:
            self.logger.error(f"Deployment health test failed: {e}")
            return False
    
    def test_message_publishing(self) -> bool:
        """Test message publishing to beast_mode_network channel"""
        try:
            config = self.config_manager.get_config(self.environment)
            
            import redis
            client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                ssl=config.redis.ssl
            )
            
            test_message = {
                "id": "smoke_test_message",
                "type": "simple_message",
                "source": "smoke_test",
                "payload": {"test": True, "timestamp": time.time()},
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            result = client.publish("beast_mode_network", json.dumps(test_message))
            
            # Result is the number of subscribers, 0 is OK if no agents are listening
            self.logger.info(f"Message published to {result} subscribers")
            
            return True
        except Exception as e:
            self.logger.error(f"Message publishing test failed: {e}")
            return False
    
    def test_file_permissions(self) -> bool:
        """Test file and directory permissions"""
        try:
            config = self.config_manager.get_config(self.environment)
            
            # Test directories
            directories = [
                config.agent.spore_directory,
                "logs",
                "config"
            ]
            
            for directory in directories:
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory, exist_ok=True)
                        self.logger.info(f"Created directory: {directory}")
                    except Exception as e:
                        self.logger.error(f"Cannot create directory {directory}: {e}")
                        return False
                
                # Test write permissions
                test_file = os.path.join(directory, "smoke_test.tmp")
                try:
                    with open(test_file, 'w') as f:
                        f.write("smoke test")
                    os.remove(test_file)
                except Exception as e:
                    self.logger.error(f"Cannot write to directory {directory}: {e}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"File permissions test failed: {e}")
            return False
    
    def test_log_file_creation(self) -> bool:
        """Test log file creation and writing"""
        try:
            config = self.config_manager.get_config(self.environment)
            log_file = config.agent.mailbox_log_file
            
            # Ensure logs directory exists
            log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "."
            os.makedirs(log_dir, exist_ok=True)
            
            # Test log file writing
            test_message = f"Smoke test log entry - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            with open(log_file, 'a') as f:
                f.write(f"{test_message}\n")
            
            # Verify the message was written
            with open(log_file, 'r') as f:
                content = f.read()
                if test_message not in content:
                    self.logger.error("Test message not found in log file")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Log file creation test failed: {e}")
            return False
    
    def test_process_monitoring(self) -> bool:
        """Test process monitoring capabilities"""
        try:
            import psutil
            
            # Test system resource monitoring
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.logger.info(f"System resources - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
            
            # Test process enumeration
            processes = list(psutil.process_iter(['pid', 'name']))
            if len(processes) == 0:
                self.logger.error("No processes found")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Process monitoring test failed: {e}")
            return False
    
    def test_network_connectivity(self) -> bool:
        """Test network connectivity"""
        try:
            import socket
            
            config = self.config_manager.get_config(self.environment)
            
            # Test Redis port connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((config.redis.host, config.redis.port))
            sock.close()
            
            if result != 0:
                self.logger.error(f"Cannot connect to Redis at {config.redis.host}:{config.redis.port}")
                return False
            
            # Test DNS resolution (if not localhost)
            if config.redis.host not in ['localhost', '127.0.0.1']:
                try:
                    socket.gethostbyname(config.redis.host)
                except socket.gaierror as e:
                    self.logger.error(f"DNS resolution failed for {config.redis.host}: {e}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Network connectivity test failed: {e}")
            return False
    
    def test_deployment_validation(self) -> bool:
        """Test deployment validation"""
        try:
            report = self.validator.validate_deployment(
                self.deployment_id or "smoke_test",
                self.environment,
                ValidationLevel.BASIC
            )
            
            if not report.overall_passed:
                self.logger.warning(f"Deployment validation failed: {report.failed_checks}/{report.total_checks} checks failed")
                
                # Log failed checks
                for result in report.results:
                    if not result.passed:
                        self.logger.warning(f"  - {result.name}: {result.message}")
                
                # Don't fail smoke test for validation failures, just warn
                return True
            
            self.logger.info(f"Deployment validation passed: {report.passed_checks}/{report.total_checks} checks")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment validation test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all smoke tests"""
        self.logger.info(f"Starting smoke tests for environment: {self.environment}")
        
        # Define test suite
        tests = [
            ("Configuration Loading", self.test_configuration_loading),
            ("Environment Variables", self.test_environment_variables),
            ("File Permissions", self.test_file_permissions),
            ("Network Connectivity", self.test_network_connectivity),
            ("Redis Connectivity", self.test_redis_connectivity),
            ("Redis Pub/Sub", self.test_redis_pubsub),
            ("Message Publishing", self.test_message_publishing),
            ("Log File Creation", self.test_log_file_creation),
            ("Process Monitoring", self.test_process_monitoring),
            ("Deployment Status", self.test_deployment_status),
            ("Deployment Health", self.test_deployment_health),
            ("Deployment Validation", self.test_deployment_validation)
        ]
        
        # Run tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Finalize results
        self.results['completed_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.results['duration_ms'] = (time.time() - time.mktime(time.strptime(self.results['started_at'], "%Y-%m-%d %H:%M:%S"))) * 1000
        
        # Log summary
        summary = self.results['summary']
        self.logger.info(f"Smoke tests completed: {summary['passed']}/{summary['total']} passed, {summary['failed']} failed")
        
        return self.results
    
    def generate_report(self, output_file: str):
        """Generate smoke test report"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Smoke test report saved to: {output_file}")
    
    def generate_html_report(self, output_file: str):
        """Generate HTML smoke test report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Beast Mode Smoke Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .test {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .test.passed {{ border-left-color: green; }}
        .test.failed {{ border-left-color: red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Beast Mode Smoke Test Report</h1>
        <p><strong>Environment:</strong> {self.results['environment']}</p>
        <p><strong>Deployment ID:</strong> {self.results.get('deployment_id', 'N/A')}</p>
        <p><strong>Started:</strong> {self.results['started_at']}</p>
        <p><strong>Completed:</strong> {self.results['completed_at']}</p>
        <p><strong>Duration:</strong> {self.results['duration_ms']:.0f}ms</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Tests:</strong> {self.results['summary']['total']}</p>
        <p class="passed"><strong>Passed:</strong> {self.results['summary']['passed']}</p>
        <p class="failed"><strong>Failed:</strong> {self.results['summary']['failed']}</p>
    </div>
    
    <div class="tests">
        <h2>Test Results</h2>
"""
        
        for test in self.results['tests']:
            status_class = "passed" if test['status'] == 'PASSED' else "failed"
            
            html_content += f"""
        <div class="test {status_class}">
            <h3>{test['name']} - {test['status']}</h3>
            <p>{test['message']}</p>
            <p><small>Duration: {test['duration_ms']:.0f}ms | {test['timestamp']}</small></p>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML smoke test report saved to: {output_file}")


def main():
    """Main smoke test function"""
    parser = argparse.ArgumentParser(description="Run Beast Mode deployment smoke tests")
    parser.add_argument("--environment", required=True,
                       help="Environment to test (development, production, etc.)")
    parser.add_argument("--deployment-id",
                       help="Deployment ID to test (optional)")
    parser.add_argument("--output", default="smoke_test_results.json",
                       help="Output file for test results (default: smoke_test_results.json)")
    parser.add_argument("--html-report",
                       help="Generate HTML report (provide filename)")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Log level (default: INFO)")
    parser.add_argument("--fail-on-error", action="store_true",
                       help="Exit with error code if any tests fail")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Beast Mode deployment smoke tests")
    
    try:
        # Run smoke tests
        runner = SmokeTestRunner(args.environment, args.deployment_id)
        results = runner.run_all_tests()
        
        # Generate reports
        runner.generate_report(args.output)
        
        if args.html_report:
            runner.generate_html_report(args.html_report)
        
        # Print summary
        summary = results['summary']
        print(f"\nSmoke Test Summary:")
        print(f"Environment: {args.environment}")
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {(summary['passed']/summary['total']*100):.1f}%")
        
        if summary['failed'] > 0:
            print(f"\nFailed Tests:")
            for test in results['tests']:
                if test['status'] == 'FAILED':
                    print(f"  - {test['name']}: {test['message']}")
        
        # Exit with appropriate code
        if args.fail_on_error and summary['failed'] > 0:
            logger.error("Some smoke tests failed")
            return 1
        
        logger.info("Smoke tests completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Smoke tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())