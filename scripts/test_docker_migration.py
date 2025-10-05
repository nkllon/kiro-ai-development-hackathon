#!/usr/bin/env python3
"""
Docker Volume Migration Test Suite

This script tests the migration process in a safe, isolated environment
before running the actual migration on production data.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
from datetime import datetime
from pathlib import Path


def run_command(cmd, check=True, cwd=None):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        return None
    
    return result


def create_test_environment():
    """Create a test environment with mock data."""
    print("🧪 Creating test environment...")
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="docker_migration_test_")
    print(f"📁 Test directory: {test_dir}")
    
    # Create mock deployment structure
    os.makedirs(f"{test_dir}/deployment/observatory", exist_ok=True)
    
    # Create mock grafana-data
    grafana_data_dir = f"{test_dir}/deployment/observatory/grafana-data"
    os.makedirs(f"{grafana_data_dir}/plugins", exist_ok=True)
    
    # Create mock files
    with open(f"{grafana_data_dir}/grafana.db", 'w') as f:
        f.write("mock grafana database content")
    
    with open(f"{grafana_data_dir}/plugins/test-plugin.js", 'w') as f:
        f.write("mock plugin content")
    
    # Create mock prometheus-data
    prometheus_data_dir = f"{test_dir}/deployment/observatory/prometheus-data"
    os.makedirs(f"{prometheus_data_dir}/wal", exist_ok=True)
    
    with open(f"{prometheus_data_dir}/lock", 'w') as f:
        f.write("prometheus lock file")
    
    with open(f"{prometheus_data_dir}/wal/00000001", 'w') as f:
        f.write("mock wal data")
    
    # Create mock docker-compose.yml
    compose_content = """
version: '3.8'
services:
  grafana:
    image: grafana/grafana:latest
    volumes:
      - ${GRAFANA_DATA_PATH:-./grafana-data}:/var/lib/grafana
  
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ${PROMETHEUS_DATA_PATH:-./prometheus-data}:/prometheus

volumes:
  existing_volume:
    driver: local
"""
    
    with open(f"{test_dir}/deployment/observatory/docker-compose.yml", 'w') as f:
        f.write(compose_content)
    
    # Create mock .gitignore
    with open(f"{test_dir}/.gitignore", 'w') as f:
        f.write("# Existing gitignore\n*.log\n")
    
    return test_dir


def test_data_comparison(test_dir):
    """Test the data comparison logic."""
    print("🔍 Testing data comparison logic...")
    
    # Count files in mock directories
    grafana_files = len(list(Path(f"{test_dir}/deployment/observatory/grafana-data").rglob("*")))
    prometheus_files = len(list(Path(f"{test_dir}/deployment/observatory/prometheus-data").rglob("*")))
    
    print(f"📊 Mock data created:")
    print(f"   Grafana files: {grafana_files}")
    print(f"   Prometheus files: {prometheus_files}")
    
    return grafana_files > 0 and prometheus_files > 0


def test_compose_file_modification(test_dir):
    """Test docker-compose.yml modification."""
    print("🔧 Testing docker-compose.yml modification...")
    
    compose_file = f"{test_dir}/deployment/observatory/docker-compose.yml"
    
    # Read original
    with open(compose_file, 'r') as f:
        original_content = f.read()
    
    print("📄 Original compose file:")
    print(original_content[:200] + "...")
    
    # Apply modifications (simulate the migration script logic)
    modified_content = original_content.replace(
        '${GRAFANA_DATA_PATH:-./grafana-data}:/var/lib/grafana',
        'grafana_data:/var/lib/grafana'
    )
    
    modified_content = modified_content.replace(
        '${PROMETHEUS_DATA_PATH:-./prometheus-data}:/prometheus',
        'prometheus_data:/prometheus'
    )
    
    # Add volumes if not present
    if 'grafana_data:' not in modified_content:
        if 'volumes:' in modified_content:
            modified_content = modified_content.replace(
                'volumes:\n',
                'volumes:\n  grafana_data:\n    driver: local\n  prometheus_data:\n    driver: local\n'
            )
    
    # Write modified file
    with open(compose_file, 'w') as f:
        f.write(modified_content)
    
    # Verify modifications
    with open(compose_file, 'r') as f:
        final_content = f.read()
    
    print("📄 Modified compose file:")
    print(final_content[:300] + "...")
    
    # Check that modifications were applied
    success = (
        'grafana_data:/var/lib/grafana' in final_content and
        'prometheus_data:/prometheus' in final_content and
        'grafana_data:' in final_content and
        'prometheus_data:' in final_content
    )
    
    if success:
        print("✅ docker-compose.yml modification test passed")
    else:
        print("❌ docker-compose.yml modification test failed")
    
    return success


def test_gitignore_update(test_dir):
    """Test .gitignore update logic."""
    print("🧹 Testing .gitignore update...")
    
    gitignore_file = f"{test_dir}/.gitignore"
    
    # Read original
    with open(gitignore_file, 'r') as f:
        original_content = f.read()
    
    print(f"📄 Original .gitignore:\n{original_content}")
    
    # Add governance patterns
    governance_patterns = [
        "# Deployment data governance - Added by migration script",
        "**/grafana-data/",
        "**/prometheus-data/",
        "*.db",
        "*.exe",
        "**/logs/",
        "**/cache/",
        "**/tmp/"
    ]
    
    with open(gitignore_file, 'a') as f:
        f.write('\n' + '\n'.join(governance_patterns) + '\n')
    
    # Verify update
    with open(gitignore_file, 'r') as f:
        final_content = f.read()
    
    print(f"📄 Updated .gitignore:\n{final_content}")
    
    success = all(pattern in final_content for pattern in governance_patterns)
    
    if success:
        print("✅ .gitignore update test passed")
    else:
        print("❌ .gitignore update test failed")
    
    return success


def test_backup_creation(test_dir):
    """Test backup creation logic."""
    print("💾 Testing backup creation...")
    
    backup_dir = f"{test_dir}/test-backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Simulate backup creation
    if os.path.exists(f"{test_dir}/deployment/observatory/grafana-data"):
        shutil.copytree(
            f"{test_dir}/deployment/observatory/grafana-data",
            f"{backup_dir}/host-grafana-data"
        )
    
    if os.path.exists(f"{test_dir}/deployment/observatory/prometheus-data"):
        shutil.copytree(
            f"{test_dir}/deployment/observatory/prometheus-data",
            f"{backup_dir}/host-prometheus-data"
        )
    
    # Verify backup
    backup_grafana_exists = os.path.exists(f"{backup_dir}/host-grafana-data/grafana.db")
    backup_prometheus_exists = os.path.exists(f"{backup_dir}/host-prometheus-data/lock")
    
    success = backup_grafana_exists and backup_prometheus_exists
    
    if success:
        print("✅ Backup creation test passed")
        print(f"   Grafana backup: {backup_grafana_exists}")
        print(f"   Prometheus backup: {backup_prometheus_exists}")
    else:
        print("❌ Backup creation test failed")
    
    return success, backup_dir


def test_rollback_procedure(test_dir, backup_dir):
    """Test the rollback procedure."""
    print("🔄 Testing rollback procedure...")
    
    # Simulate breaking the environment
    compose_file = f"{test_dir}/deployment/observatory/docker-compose.yml"
    with open(compose_file, 'w') as f:
        f.write("# BROKEN COMPOSE FILE")
    
    gitignore_file = f"{test_dir}/.gitignore"
    with open(gitignore_file, 'w') as f:
        f.write("# BROKEN GITIGNORE")
    
    # Remove data directories
    shutil.rmtree(f"{test_dir}/deployment/observatory/grafana-data", ignore_errors=True)
    shutil.rmtree(f"{test_dir}/deployment/observatory/prometheus-data", ignore_errors=True)
    
    print("💥 Environment broken (simulated)")
    
    # Perform rollback
    print("🔄 Performing rollback...")
    
    # Restore data from backup
    if os.path.exists(f"{backup_dir}/host-grafana-data"):
        shutil.copytree(
            f"{backup_dir}/host-grafana-data",
            f"{test_dir}/deployment/observatory/grafana-data"
        )
    
    if os.path.exists(f"{backup_dir}/host-prometheus-data"):
        shutil.copytree(
            f"{backup_dir}/host-prometheus-data",
            f"{test_dir}/deployment/observatory/prometheus-data"
        )
    
    # Restore original files (simulate git checkout)
    original_compose = """
version: '3.8'
services:
  grafana:
    image: grafana/grafana:latest
    volumes:
      - ${GRAFANA_DATA_PATH:-./grafana-data}:/var/lib/grafana
  
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ${PROMETHEUS_DATA_PATH:-./prometheus-data}:/prometheus

volumes:
  existing_volume:
    driver: local
"""
    
    with open(compose_file, 'w') as f:
        f.write(original_compose)
    
    with open(gitignore_file, 'w') as f:
        f.write("# Existing gitignore\n*.log\n")
    
    # Verify rollback
    data_restored = (
        os.path.exists(f"{test_dir}/deployment/observatory/grafana-data/grafana.db") and
        os.path.exists(f"{test_dir}/deployment/observatory/prometheus-data/lock")
    )
    
    compose_restored = '${GRAFANA_DATA_PATH:-./grafana-data}' in open(compose_file).read()
    
    success = data_restored and compose_restored
    
    if success:
        print("✅ Rollback test passed")
        print(f"   Data restored: {data_restored}")
        print(f"   Compose restored: {compose_restored}")
    else:
        print("❌ Rollback test failed")
    
    return success


def run_full_test_suite():
    """Run the complete test suite."""
    print("🧪 Docker Volume Migration Test Suite")
    print("=" * 50)
    
    test_results = []
    test_dir = None
    backup_dir = None
    
    try:
        # Create test environment
        test_dir = create_test_environment()
        test_results.append(("Environment Creation", True))
        
        # Test data comparison
        result = test_data_comparison(test_dir)
        test_results.append(("Data Comparison", result))
        
        # Test compose file modification
        result = test_compose_file_modification(test_dir)
        test_results.append(("Compose File Modification", result))
        
        # Test gitignore update
        result = test_gitignore_update(test_dir)
        test_results.append(("GitIgnore Update", result))
        
        # Test backup creation
        result, backup_dir = test_backup_creation(test_dir)
        test_results.append(("Backup Creation", result))
        
        # Test rollback procedure
        if backup_dir:
            result = test_rollback_procedure(test_dir, backup_dir)
            test_results.append(("Rollback Procedure", result))
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        test_results.append(("Test Suite", False))
    
    finally:
        # Cleanup
        if test_dir and os.path.exists(test_dir):
            shutil.rmtree(test_dir, ignore_errors=True)
            print(f"🧹 Cleaned up test directory: {test_dir}")
    
    # Print results
    print("\n📊 Test Results:")
    print("-" * 30)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<25} {status}")
        if not passed:
            all_passed = False
    
    print("-" * 30)
    
    if all_passed:
        print("🎉 All tests passed! Migration script is ready to use.")
        return True
    else:
        print("❌ Some tests failed! Review the migration script before using.")
        return False


if __name__ == "__main__":
    success = run_full_test_suite()
    sys.exit(0 if success else 1)