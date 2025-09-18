"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.511848
"""




import pytest
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock

from beast_mode.deployment.config_manager import ConfigManager
from beast_mode.deployment.deployment_manager import (
    DeploymentManager, DeploymentType, ServiceDefinition, DeploymentStatus
)


class TestDeploymentManager(ReflectiveModule):
    """Test deployment manager functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
        self.deployment_manager = DeploymentManager(self.config_manager)

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Stop any running deployments
        self.deployment_manager.stop_all_deployments()

    @patch('subprocess.Popen')
    def test_create_single_machine_deployment(self, mock_popen):
        """Test creating single machine deployment"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        deployment_id = self.deployment_manager.create_single_machine_deployment("development")

        assert deployment_id.startswith("single_development_")
        assert deployment_id in self.deployment_manager.deployments

        deployment = self.deployment_manager.deployments[deployment_id]
        assert deployment.type == DeploymentType.SINGLE_MACHINE
        assert deployment.environment == "development"
        assert "redis" in deployment.services
        assert "mailbox_logger" in deployment.services
        assert "agent" in deployment.services

    def test_create_distributed_deployment(self):
        """Test creating distributed deployment"""
        nodes = ["node1", "node2", "node3"]
        deployment_id = self.deployment_manager.create_distributed_deployment("distributed", nodes)

        assert deployment_id.startswith("distributed_distributed_")
        assert deployment_id in self.deployment_manager.deployments

        deployment = self.deployment_manager.deployments[deployment_id]
        assert deployment.type == DeploymentType.DISTRIBUTED
        assert deployment.environment == "distributed"

        # Check that manifest file was created
        import os
        manifest_file = f"deployment_{deployment_id}.json"
        assert os.path.exists(manifest_file)

        # Load and verify manifest
        import json
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)

        assert manifest["deployment_id"] == deployment_id
        assert manifest["environment"] == "distributed"
        assert manifest["nodes"] == nodes
        assert "services" in manifest

        # Cleanup
        os.remove(manifest_file)

    def test_create_docker_deployment(self):
        """Test creating Docker deployment"""
        deployment_id = self.deployment_manager.create_docker_deployment("docker")

        assert deployment_id.startswith("docker_docker_")
        assert deployment_id in self.deployment_manager.deployments

        deployment = self.deployment_manager.deployments[deployment_id]
        assert deployment.type == DeploymentType.DOCKER
        assert deployment.environment == "docker"

        # Check that Docker Compose file was created
        import os
        compose_file = f"docker-compose-{deployment_id}.yml"
        env_file = f".env-{deployment_id}"

        assert os.path.exists(compose_file)
        assert os.path.exists(env_file)

        # Verify compose file content
        with open(compose_file, 'r') as f:
            import yaml
            compose_content = yaml.safe_load(f)

        assert "services" in compose_content
        assert "redis" in compose_content["services"]
        assert "mailbox_logger" in compose_content["services"]
        assert "agent" in compose_content["services"]

        # Cleanup
        os.remove(compose_file)
        os.remove(env_file)

    @patch('subprocess.Popen')
    def test_stop_deployment(self, mock_popen):
        """Test stopping deployment"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process

        # Create deployment
        deployment_id = self.deployment_manager.create_single_machine_deployment("development")

        # Stop deployment
        self.deployment_manager.stop_deployment(deployment_id)

        deployment = self.deployment_manager.deployments[deployment_id]
        assert deployment.status == "stopped"

        # Verify terminate was called
        mock_process.terminate.assert_called()

    def test_stop_nonexistent_deployment(self):
        """Test stopping non-existent deployment"""
        with pytest.raises(ValueError, match="Deployment not found"):
            self.deployment_manager.stop_deployment("nonexistent")

    @patch('subprocess.Popen')
    def test_get_deployment_status(self, mock_popen):
        """Test getting deployment status"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process

        # Create deployment
        deployment_id = self.deployment_manager.create_single_machine_deployment("development")

        # Get status
        status = self.deployment_manager.get_deployment_status(deployment_id)

        assert status.deployment_id == deployment_id
        assert status.type == DeploymentType.SINGLE_MACHINE
        assert status.environment == "development"
        assert len(status.services) > 0

    def test_get_status_nonexistent_deployment(self):
        """Test getting status of non-existent deployment"""
        with pytest.raises(ValueError, match="Deployment not found"):
            self.deployment_manager.get_deployment_status("nonexistent")

    def test_list_deployments(self):
        """Test listing deployments"""
        # Initially empty
        deployments = self.deployment_manager.list_deployments()
        assert len(deployments) == 0

        # Create some deployments
        with patch('subprocess.Popen'):
            deployment_id1 = self.deployment_manager.create_single_machine_deployment("development")
            deployment_id2 = self.deployment_manager.create_docker_deployment("docker")

        deployments = self.deployment_manager.list_deployments()
        assert len(deployments) == 2

        deployment_ids = [d.deployment_id for d in deployments]
        assert deployment_id1 in deployment_ids
        assert deployment_id2 in deployment_ids

    @patch('psutil.Process')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_health_check_deployment(self, mock_disk, mock_memory, mock_cpu, mock_process):
        """Test deployment health check"""
        # Mock system resources
        mock_cpu.return_value = 25.0
        mock_memory.return_value = Mock(percent=60.0)
        mock_disk.return_value = Mock(percent=45.0)

        # Mock process
        mock_proc = Mock()
        mock_proc.is_running.return_value = True
        mock_proc.cpu_percent.return_value = 15.0
        mock_proc.memory_percent.return_value = 20.0
        mock_process.return_value = mock_proc

        with patch('subprocess.Popen') as mock_popen:
            mock_popen.return_value = Mock(pid=12345)

            # Create deployment
            deployment_id = self.deployment_manager.create_single_machine_deployment("development")

            # Perform health check
            health = self.deployment_manager.health_check_deployment(deployment_id)

            assert health["deployment_id"] == deployment_id
            assert "overall_status" in health
            assert "services" in health
            assert "system_resources" in health

            # Check system resources
            assert health["system_resources"]["cpu_percent"] == 25.0
            assert health["system_resources"]["memory_percent"] == 60.0
            assert health["system_resources"]["disk_percent"] == 45.0


class TestServiceDefinition(ReflectiveModule):
    """Test service definition data model"""

    def test_service_definition_creation(self):
        """Test creating service definition"""
        service = ServiceDefinition(
            name="test_service",
            command=["python", "-m", "test"],
            working_directory="/app",
            environment={"TEST": "value"}
        )

        assert service.name == "test_service"
        assert service.command == ["python", "-m", "test"]
        assert service.working_directory == "/app"
        assert service.environment == {"TEST": "value"}
        assert service.dependencies == []  # Default
        assert service.health_check_url is None  # Default
        assert service.restart_policy == "always"  # Default

    def test_service_definition_with_dependencies(self):
        """Test service definition with dependencies"""
        service = ServiceDefinition(
            name="dependent_service",
            command=["python", "-m", "dependent"],
            working_directory="/app",
            environment={},
            dependencies=["redis", "database"]
        )

        assert service.dependencies == ["redis", "database"]


class TestDeploymentStatus(ReflectiveModule):
    """Test deployment status data model"""

    def test_deployment_status_creation(self):
        """Test creating deployment status"""
        services = {
            "redis": {"status": "running", "pid": 123},
            "agent": {"status": "starting", "pid": None}
        }

        status = DeploymentStatus(
            deployment_id="test_deployment",
            type=DeploymentType.SINGLE_MACHINE,
            environment="test",
            services=services,
            started_at="2023-01-01 12:00:00",
            status="running"
        )

        assert status.deployment_id == "test_deployment"
        assert status.type == DeploymentType.SINGLE_MACHINE
        assert status.environment == "test"
        assert status.services == services
        assert status.started_at == "2023-01-01 12:00:00"
        assert status.status == "running"


class TestDeploymentManagerIntegration(ReflectiveModule):
    """Integration tests for deployment manager"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
        self.deployment_manager = DeploymentManager(self.config_manager)

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
# from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.deployment_manager.stop_all_deployments()

    @patch('subprocess.Popen')
    def test_deployment_lifecycle(self, mock_popen):
        """Test complete deployment lifecycle"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        # Create deployment
        deployment_id = self.deployment_manager.create_single_machine_deployment("development")

        # Check initial status
        status = self.deployment_manager.get_deployment_status(deployment_id)
        assert status.status in ["starting", "running"]

        # List deployments
        deployments = self.deployment_manager.list_deployments()
        assert len(deployments) == 1
        assert deployments[0].deployment_id == deployment_id

        # Health check
        with patch('psutil.Process'), patch('psutil.cpu_percent'), \
             patch('psutil.virtual_memory'), patch('psutil.disk_usage'):
            health = self.deployment_manager.health_check_deployment(deployment_id)
            assert health["deployment_id"] == deployment_id

        # Stop deployment
        self.deployment_manager.stop_deployment(deployment_id)

        # Check final status
        status = self.deployment_manager.get_deployment_status(deployment_id)

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())

    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }

    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert status.status == "stopped"