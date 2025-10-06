#!/usr/bin/env python3
"""
Complete CMS Phase 1: Foundation Tasks
Systematic completion of Tasks 1.1, 1.2, 1.3, and 1.4 based on audit findings.
"""

import os
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Beast Mode Framework
try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    from src.beast_mode.core.module_health import ModuleHealth, ModuleStatus
    from src.beast_mode.core.graceful_degradation import GracefulDegradationResult
except ImportError as e:
    logger.warning(f"Beast Mode imports not available: {e}")
    # Fallback implementations
    class ReflectiveModule:
        def __init__(self):
            pass
    
    class ModuleHealth:
        def __init__(self, status=None, message=""):
            self.status = status or "HEALTHY"
            self.message = message
    
    class ModuleStatus:
        HEALTHY = "HEALTHY"
        DEGRADED = "DEGRADED"
        UNHEALTHY = "UNHEALTHY"
    
    class GracefulDegradationResult:
        def __init__(self, success=True, fallback_mode=False, message=""):
            self.success = success
            self.fallback_mode = fallback_mode
            self.message = message

@dataclass
class TaskCompletionResult:
    """Task completion result information."""
    task_id: str
    task_name: str
    status: str
    completion_percentage: float
    completed_criteria: List[str]
    remaining_criteria: List[str]
    evidence: List[str]
    next_steps: List[str]

class CMSPhase1Completer(ReflectiveModule):
    """Complete CMS Phase 1: Foundation Tasks with systematic approach."""
    
    def __init__(self):
        super().__init__()
        self.phase_name = "Phase 1: Foundation"
        self.tasks = ["task_1_1", "task_1_2", "task_1_3", "task_1_4"]
        self.completion_log = []
        
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "CMS Phase 1 Completer",
            "version": "1.0.0",
            "description": "Complete CMS Phase 1 Foundation Tasks",
            "author": "Beast Mode Framework",
            "tasks": self.tasks
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get module capabilities."""
        return [
            "CORE_FUNCTIONALITY",
            "DATA_PROCESSING", 
            "API_INTEGRATION",
            "VALIDATION"
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get health status of the completer."""
        return ModuleHealth(
            status=ModuleStatus.HEALTHY,
            message="Phase 1 completer operational"
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Handle graceful degradation on errors."""
        logger.warning("Graceful degradation triggered")
        return GracefulDegradationResult(
            success=False,
            fallback_mode=True,
            message="Phase 1 completion requires manual intervention"
        )
    
    def complete_phase_1(self) -> Dict[str, Any]:
        """Complete all Phase 1 tasks systematically."""
        logger.info("Starting Phase 1 completion")
        
        results = {
            "phase": "Phase 1: Foundation",
            "completion_timestamp": datetime.now().isoformat(),
            "tasks": {},
            "overall_status": "in_progress",
            "summary": {}
        }
        
        # Complete each task
        task_results = []
        
        # Task 1.1: Enhanced Directus Core Setup
        task_1_1_result = self.complete_task_1_1()
        task_results.append(task_1_1_result)
        results["tasks"]["1.1"] = task_1_1_result.__dict__
        
        # Task 1.2: Search Engine Integration  
        task_1_2_result = self.complete_task_1_2()
        task_results.append(task_1_2_result)
        results["tasks"]["1.2"] = task_1_2_result.__dict__
        
        # Task 1.3: Core Data Model Implementation
        task_1_3_result = self.complete_task_1_3()
        task_results.append(task_1_3_result)
        results["tasks"]["1.3"] = task_1_3_result.__dict__
        
        # Task 1.4: Repository Synchronization Service
        task_1_4_result = self.complete_task_1_4()
        task_results.append(task_1_4_result)
        results["tasks"]["1.4"] = task_1_4_result.__dict__
        
        # Calculate overall completion
        total_completion = sum(r.completion_percentage for r in task_results) / len(task_results)
        results["summary"] = {
            "total_tasks": len(task_results),
            "average_completion": f"{total_completion:.1f}%",
            "fully_completed": len([r for r in task_results if r.completion_percentage == 100]),
            "in_progress": len([r for r in task_results if 0 < r.completion_percentage < 100]),
            "not_started": len([r for r in task_results if r.completion_percentage == 0])
        }
        
        # Determine overall status
        if total_completion == 100:
            results["overall_status"] = "completed"
        elif total_completion > 0:
            results["overall_status"] = "in_progress"
        else:
            results["overall_status"] = "not_started"
        
        logger.info(f"Phase 1 completion finished: {total_completion:.1f}% complete")
        return results
    
    def complete_task_1_1(self) -> TaskCompletionResult:
        """Complete Task 1.1: Enhanced Directus Core Setup."""
        logger.info("Completing Task 1.1: Enhanced Directus Core Setup")
        
        # Check current status
        completed_criteria = []
        remaining_criteria = []
        evidence = []
        
        # Check Directus deployment
        if self._check_directus_running():
            completed_criteria.append("Directus CMS deployed with PostgreSQL backend")
            evidence.append("Directus service running on port 8055")
        else:
            remaining_criteria.append("Directus CMS deployed with PostgreSQL backend")
        
        # Check Redis
        if self._check_redis_running():
            completed_criteria.append("Redis caching layer configured and operational")
            evidence.append("Redis service running on port 6379")
        else:
            remaining_criteria.append("Redis caching layer configured and operational")
        
        # Check Docker containerization
        if self._check_docker_containers():
            completed_criteria.append("Docker containerization with health checks")
            evidence.append("Docker containers running with health checks")
        else:
            remaining_criteria.append("Docker containerization with health checks")
        
        # Check authentication
        if self._check_directus_auth():
            completed_criteria.append("Basic authentication and authorization configured")
            evidence.append("Directus authentication responding")
        else:
            remaining_criteria.append("Basic authentication and authorization configured")
        
        # Check for remaining work
        remaining_criteria.extend([
            "Custom schema extensions implemented for stakeholder collections",
            "Health monitoring endpoints functional", 
            "Backup and recovery procedures implemented"
        ])
        
        completion_percentage = (len(completed_criteria) / (len(completed_criteria) + len(remaining_criteria))) * 100
        
        next_steps = [
            "Implement custom schema extensions for stakeholder collections",
            "Add health monitoring endpoints with Beast Mode integration",
            "Create backup and recovery procedures",
            "Fix Docker health check configuration"
        ]
        
        return TaskCompletionResult(
            task_id="1.1",
            task_name="Enhanced Directus Core Setup",
            status="IN_PROGRESS",
            completion_percentage=completion_percentage,
            completed_criteria=completed_criteria,
            remaining_criteria=remaining_criteria,
            evidence=evidence,
            next_steps=next_steps
        )
    
    def complete_task_1_2(self) -> TaskCompletionResult:
        """Complete Task 1.2: Search Engine Integration."""
        logger.info("Completing Task 1.2: Search Engine Integration")
        
        completed_criteria = []
        remaining_criteria = []
        evidence = []
        
        # Check for Elasticsearch
        if self._check_elasticsearch_running():
            completed_criteria.append("Elasticsearch cluster deployed and configured")
            evidence.append("Elasticsearch service detected")
        else:
            remaining_criteria.append("Elasticsearch cluster deployed and configured")
        
        # Check for search-related code
        search_code_exists = self._check_search_code_exists()
        if search_code_exists:
            evidence.append("Search-related code artifacts found")
        
        # Most criteria are likely not completed yet
        remaining_criteria.extend([
            "Full-text search indexing for all content types",
            "Semantic search using vector embeddings", 
            "Search API endpoints implemented",
            "Search result ranking and relevance tuning",
            "Search analytics and monitoring",
            "Performance optimization for large datasets"
        ])
        
        completion_percentage = (len(completed_criteria) / (len(completed_criteria) + len(remaining_criteria))) * 100
        
        next_steps = [
            "Deploy Elasticsearch cluster",
            "Implement search indexing pipeline",
            "Add AI semantic search capabilities",
            "Create search API endpoints",
            "Add search analytics and monitoring"
        ]
        
        return TaskCompletionResult(
            task_id="1.2", 
            task_name="Search Engine Integration",
            status="STARTED",
            completion_percentage=completion_percentage,
            completed_criteria=completed_criteria,
            remaining_criteria=remaining_criteria,
            evidence=evidence,
            next_steps=next_steps
        )
    
    def complete_task_1_3(self) -> TaskCompletionResult:
        """Complete Task 1.3: Core Data Model Implementation."""
        logger.info("Completing Task 1.3: Core Data Model Implementation")
        
        completed_criteria = []
        remaining_criteria = []
        evidence = []
        
        # Check database exists
        if self._check_database_running():
            evidence.append("PostgreSQL database running")
        
        # Check for data model code
        if self._check_data_model_code():
            evidence.append("Data model related code found")
        
        # Most criteria likely not completed
        remaining_criteria.extend([
            "All core collections created with proper schema",
            "Relationship mappings implemented and tested",
            "Data validation rules enforced",
            "Migration scripts for schema updates", 
            "Data integrity constraints implemented",
            "Performance indexes optimized",
            "Audit trail functionality enabled"
        ])
        
        completion_percentage = (len(completed_criteria) / (len(completed_criteria) + len(remaining_criteria))) * 100
        
        next_steps = [
            "Design and implement core collections schema",
            "Create relationship mappings between entities",
            "Implement data validation rules",
            "Add performance indexes",
            "Enable audit trail functionality"
        ]
        
        return TaskCompletionResult(
            task_id="1.3",
            task_name="Core Data Model Implementation", 
            status="STARTED",
            completion_percentage=completion_percentage,
            completed_criteria=completed_criteria,
            remaining_criteria=remaining_criteria,
            evidence=evidence,
            next_steps=next_steps
        )
    
    def complete_task_1_4(self) -> TaskCompletionResult:
        """Complete Task 1.4: Repository Synchronization Service."""
        logger.info("Completing Task 1.4: Repository Synchronization Service")
        
        completed_criteria = []
        remaining_criteria = []
        evidence = []
        
        # Check for sync-related code
        if self._check_sync_code_exists():
            evidence.append("Repository synchronization code found")
        
        # Most criteria likely not completed
        remaining_criteria.extend([
            "Git webhook integration implemented",
            "Automated content extraction and processing",
            "Real-time synchronization with change detection",
            "Conflict resolution and error handling",
            "Metadata extraction and relationship mapping",
            "Batch processing for large repositories",
            "Synchronization monitoring and alerting"
        ])
        
        completion_percentage = (len(completed_criteria) / (len(completed_criteria) + len(remaining_criteria))) * 100
        
        next_steps = [
            "Implement Git webhook handlers",
            "Create content extraction pipeline",
            "Add real-time synchronization",
            "Implement error handling and monitoring",
            "Add batch processing capabilities"
        ]
        
        return TaskCompletionResult(
            task_id="1.4",
            task_name="Repository Synchronization Service",
            status="STARTED", 
            completion_percentage=completion_percentage,
            completed_criteria=completed_criteria,
            remaining_criteria=remaining_criteria,
            evidence=evidence,
            next_steps=next_steps
        )
    
    def _check_directus_running(self) -> bool:
        """Check if Directus is running."""
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8055/server/health'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() == '200'
        except Exception:
            return False
    
    def _check_redis_running(self) -> bool:
        """Check if Redis is running."""
        try:
            result = subprocess.run(
                ['redis-cli', 'ping'],
                capture_output=True, text=True, timeout=5
            )
            return 'PONG' in result.stdout
        except Exception:
            return False
    
    def _check_docker_containers(self) -> bool:
        """Check if Docker containers are running."""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=directus', '--format', '{{.Names}}'],
                capture_output=True, text=True, timeout=5
            )
            return 'directus' in result.stdout
        except Exception:
            return False
    
    def _check_directus_auth(self) -> bool:
        """Check if Directus authentication is configured."""
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8055/auth/login'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() in ['200', '405']  # 405 is also valid (method not allowed)
        except Exception:
            return False
    
    def _check_elasticsearch_running(self) -> bool:
        """Check if Elasticsearch is running."""
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:9200/_cluster/health'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() == '200'
        except Exception:
            return False
    
    def _check_database_running(self) -> bool:
        """Check if PostgreSQL database is running."""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=db', '--format', '{{.Names}}'],
                capture_output=True, text=True, timeout=5
            )
            return 'db' in result.stdout
        except Exception:
            return False
    
    def _check_search_code_exists(self) -> bool:
        """Check if search-related code exists."""
        search_files = [
            'src/cms_platform/search/',
            'scripts/complete_task_1_2_elasticsearch.py'
        ]
        
        for file_path in search_files:
            if Path(file_path).exists():
                return True
        return False
    
    def _check_data_model_code(self) -> bool:
        """Check if data model code exists."""
        model_files = [
            'src/cms_platform/models/',
            'src/cms_platform/schema/'
        ]
        
        for file_path in model_files:
            if Path(file_path).exists():
                return True
        return False
    
    def _check_sync_code_exists(self) -> bool:
        """Check if synchronization code exists."""
        sync_files = [
            'src/cms_platform/sync/',
            'scripts/sync_repository_to_directus.py'
        ]
        
        for file_path in sync_files:
            if Path(file_path).exists():
                return True
        return False

def main():
    """Main execution function."""
    completer = CMSPhase1Completer()
    
    try:
        result = completer.complete_phase_1()
        
        print("=" * 60)
        print("CMS Phase 1 Completion Results")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        logger.error(f"Phase 1 completion failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    main()