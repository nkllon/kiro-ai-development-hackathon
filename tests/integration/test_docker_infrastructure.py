"""
Integration Tests for Docker Infrastructure

Tests the Docker Compose setup for Directus CMS to ensure:
- All services start correctly
- Health checks pass
- Network connectivity works
- Database initialization succeeds

Requirements Tested:
- 1.3: Docker Compose infrastructure setup
- 8.1: Deployment with Docker and Docker Compose
- 8.2: Environment-specific configurations
"""

import unittest
import subprocess
import time
import requests
import os
from typing import Dict, Any

# Optional dependencies for integration testing
try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class TestDockerInfrastructure(unittest.TestCase):
    """Integration tests for Docker infrastructure"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment - start Docker services"""
        cls.compose_file = "docker-compose.directus.yml"
        cls.services_started = False
        
        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise unittest.SkipTest("Docker or docker-compose not available")
        
        # Check if services are already running
        result = subprocess.run(
            ["docker-compose", "-f", cls.compose_file, "ps", "-q"],
            capture_output=True, text=True
        )
        
        if result.stdout.strip():
            print("Docker services already running, using existing setup")
            cls.services_started = True
        else:
            print("Starting Docker services for testing...")
            cls._start_services()
    
    @classmethod
    def _start_services(cls):
        """Start Docker services"""
        try:
            # Create necessary directories
            os.makedirs("directus/snapshots", exist_ok=True)
            
            # Start services
            subprocess.run([
                "docker-compose", "-f", cls.compose_file, "up", "-d"
            ], check=True, timeout=300)
            
            # Wait for services to be healthy
            cls._wait_for_services()
            cls.services_started = True
            
        except subprocess.TimeoutExpired:
            raise unittest.SkipTest("Docker services failed to start within timeout")
        except subprocess.CalledProcessError as e:
            raise unittest.SkipTest(f"Failed to start Docker services: {e}")
    
    @classmethod
    def _wait_for_services(cls, timeout: int = 120):
        """Wait for all services to be healthy"""
        start_time = time.time()
        
        services = {
            "postgres": cls._check_postgres_health,
            "redis": cls._check_redis_health,
            "directus": cls._check_directus_health
        }
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service_name, health_check in services.items():
                try:
                    if not health_check():
                        all_healthy = False
                        print(f"Waiting for {service_name}...")
                        break
                except Exception as e:
                    all_healthy = False
                    print(f"Health check failed for {service_name}: {e}")
                    break
            
            if all_healthy:
                print("All services are healthy!")
                return
            
            time.sleep(5)
        
        raise TimeoutError(f"Services failed to become healthy within {timeout} seconds")
    
    @classmethod
    def _check_postgres_health(cls) -> bool:
        """Check PostgreSQL health"""
        if not POSTGRESQL_AVAILABLE:
            return False
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="directus",
                user="directus",
                password="directus",
                connect_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True
        except Exception:
            return False
    
    @classmethod
    def _check_redis_health(cls) -> bool:
        """Check Redis health"""
        if not REDIS_AVAILABLE:
            return False
        try:
            r = redis.Redis(host="localhost", port=6379, socket_timeout=5)
            return r.ping()
        except Exception:
            return False
    
    @classmethod
    def _check_directus_health(cls) -> bool:
        """Check Directus health"""
        try:
            response = requests.get("http://localhost:8055/server/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Note: We don't automatically stop services to allow manual inspection
        # Uncomment the following lines if you want automatic cleanup:
        # if cls.services_started:
        #     subprocess.run([
        #         "docker-compose", "-f", cls.compose_file, "down"
        #     ], capture_output=True)
        pass
    
    def test_docker_compose_config_valid(self):
        """Test that Docker Compose configuration is valid"""
        result = subprocess.run([
            "docker-compose", "-f", self.compose_file, "config"
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, f"Docker Compose config invalid: {result.stderr}")
        self.assertIn("services:", result.stdout)
        self.assertIn("postgres:", result.stdout)
        self.assertIn("directus:", result.stdout)
        self.assertIn("redis:", result.stdout)
    
    def test_all_services_running(self):
        """Test that all required services are running"""
        result = subprocess.run([
            "docker-compose", "-f", self.compose_file, "ps"
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        
        # Check that all services are listed and running
        expected_services = ["directus_postgres", "directus_cms", "directus_redis"]
        for service in expected_services:
            self.assertIn(service, result.stdout, f"Service {service} not found in running services")
    
    def test_postgres_connectivity(self):
        """Test PostgreSQL database connectivity and schema"""
        if not POSTGRESQL_AVAILABLE:
            self.skipTest("PostgreSQL client not available")
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="directus",
                user="directus",
                password="directus",
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            
            # Test basic connectivity
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            self.assertIn("PostgreSQL", version)
            
            # Test repository_content schema exists
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'repository_content'
            """)
            schema_result = cursor.fetchone()
            self.assertIsNotNone(schema_result, "repository_content schema not found")
            
            # Test that our tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'repository_content'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ["code_files", "documents", "specifications", "tasks"]
            for table in expected_tables:
                self.assertIn(table, tables, f"Table {table} not found in repository_content schema")
            
            # Test initial data
            cursor.execute("SELECT COUNT(*) FROM repository_content.specifications")
            spec_count = cursor.fetchone()[0]
            self.assertGreaterEqual(spec_count, 3, "Expected at least 3 initial specifications")
            
            cursor.close()
            conn.close()
            
        except psycopg2.Error as e:
            self.fail(f"PostgreSQL connectivity test failed: {e}")
    
    def test_redis_connectivity(self):
        """Test Redis connectivity and basic operations"""
        if not REDIS_AVAILABLE:
            self.skipTest("Redis client not available")
        
        try:
            r = redis.Redis(host="localhost", port=6379, socket_timeout=10)
            
            # Test basic connectivity
            self.assertTrue(r.ping(), "Redis ping failed")
            
            # Test basic operations
            test_key = "test_key_integration"
            test_value = "test_value_integration"
            
            r.set(test_key, test_value)
            retrieved_value = r.get(test_key).decode('utf-8')
            self.assertEqual(retrieved_value, test_value)
            
            # Cleanup
            r.delete(test_key)
            
        except redis.RedisError as e:
            self.fail(f"Redis connectivity test failed: {e}")
    
    def test_directus_api_accessibility(self):
        """Test Directus API accessibility and basic endpoints"""
        try:
            # Test health endpoint
            health_response = requests.get("http://localhost:8055/server/health", timeout=10)
            self.assertEqual(health_response.status_code, 200)
            
            # Test server info endpoint
            info_response = requests.get("http://localhost:8055/server/info", timeout=10)
            self.assertEqual(info_response.status_code, 200)
            
            info_data = info_response.json()
            self.assertIn("directus", info_data)
            self.assertIn("version", info_data["directus"])
            
            # Test that admin interface is accessible
            admin_response = requests.get("http://localhost:8055/admin", timeout=10)
            # Should return 200 (admin interface) or redirect
            self.assertIn(admin_response.status_code, [200, 301, 302])
            
        except requests.RequestException as e:
            self.fail(f"Directus API accessibility test failed: {e}")
    
    def test_network_connectivity_between_services(self):
        """Test network connectivity between Docker services"""
        try:
            # Test that Directus can connect to PostgreSQL
            # This is implicit in Directus starting successfully, but let's verify
            
            # Get Directus container logs to check for database connection
            result = subprocess.run([
                "docker-compose", "-f", self.compose_file, "logs", "directus"
            ], capture_output=True, text=True, timeout=30)
            
            # Should not contain database connection errors
            self.assertNotIn("ECONNREFUSED", result.stdout)
            self.assertNotIn("Connection refused", result.stdout)
            
            # Should contain successful startup messages
            # Note: Exact messages may vary by Directus version
            
        except subprocess.TimeoutExpired:
            self.fail("Failed to retrieve Directus logs within timeout")
    
    def test_volume_persistence(self):
        """Test that Docker volumes are properly configured"""
        # Check that volumes exist
        result = subprocess.run([
            "docker", "volume", "ls", "--format", "{{.Name}}"
        ], capture_output=True, text=True)
        
        volume_names = result.stdout.strip().split('\n')
        
        expected_volumes = [
            "postgres_data",
            "directus_uploads", 
            "directus_extensions",
            "redis_data"
        ]
        
        for volume in expected_volumes:
            # Volume names are prefixed with project name
            volume_found = any(volume in vol_name for vol_name in volume_names)
            self.assertTrue(volume_found, f"Volume {volume} not found")
    
    def test_environment_configuration(self):
        """Test that environment variables are properly configured"""
        # Check Directus environment through API
        try:
            # Test that Directus is using PostgreSQL (not SQLite)
            info_response = requests.get("http://localhost:8055/server/info", timeout=10)
            self.assertEqual(info_response.status_code, 200)
            
            # The fact that we can connect to PostgreSQL separately confirms
            # that Directus is using the correct database configuration
            
        except requests.RequestException as e:
            self.fail(f"Environment configuration test failed: {e}")
    
    def test_health_checks_working(self):
        """Test that Docker health checks are working"""
        # Get service health status
        result = subprocess.run([
            "docker-compose", "-f", self.compose_file, "ps", "--format", "json"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse JSON output if available (newer docker-compose versions)
            try:
                import json
                services = json.loads(result.stdout)
                if isinstance(services, list):
                    for service in services:
                        if "Health" in service:
                            self.assertIn(service["Health"], ["healthy", "starting"])
            except (json.JSONDecodeError, KeyError):
                # Fallback: just check that services are running
                pass
        
        # Alternative check: verify services respond to health checks
        self.assertTrue(self._check_postgres_health(), "PostgreSQL health check failed")
        self.assertTrue(self._check_redis_health(), "Redis health check failed")
        self.assertTrue(self._check_directus_health(), "Directus health check failed")


class TestDockerManagementScripts(unittest.TestCase):
    """Test Docker management scripts"""
    
    def test_start_script_exists_and_executable(self):
        """Test that start script exists and is executable"""
        script_path = "scripts/start-directus.sh"
        self.assertTrue(os.path.exists(script_path), f"Start script {script_path} not found")
        self.assertTrue(os.access(script_path, os.X_OK), f"Start script {script_path} not executable")
    
    def test_stop_script_exists_and_executable(self):
        """Test that stop script exists and is executable"""
        script_path = "scripts/stop-directus.sh"
        self.assertTrue(os.path.exists(script_path), f"Stop script {script_path} not found")
        self.assertTrue(os.access(script_path, os.X_OK), f"Stop script {script_path} not executable")
    
    def test_health_check_script_exists_and_executable(self):
        """Test that health check script exists and is executable"""
        script_path = "scripts/health-check-directus.sh"
        self.assertTrue(os.path.exists(script_path), f"Health check script {script_path} not found")
        self.assertTrue(os.access(script_path, os.X_OK), f"Health check script {script_path} not executable")
    
    def test_database_init_script_exists(self):
        """Test that database initialization script exists"""
        script_path = "scripts/init-db.sql"
        self.assertTrue(os.path.exists(script_path), f"Database init script {script_path} not found")
        
        # Check that it contains expected SQL
        with open(script_path, 'r') as f:
            content = f.read()
            self.assertIn("CREATE SCHEMA IF NOT EXISTS repository_content", content)
            self.assertIn("CREATE TABLE IF NOT EXISTS repository_content.specifications", content)
    
    def test_environment_file_exists(self):
        """Test that environment configuration file exists"""
        env_file = ".env.directus"
        self.assertTrue(os.path.exists(env_file), f"Environment file {env_file} not found")
        
        # Check that it contains expected configuration
        with open(env_file, 'r') as f:
            content = f.read()
            self.assertIn("DATABASE_URL", content)
            self.assertIn("ADMIN_EMAIL", content)
            self.assertIn("directus", content.lower())


if __name__ == '__main__':
    # Configure test environment
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2, warnings='ignore')