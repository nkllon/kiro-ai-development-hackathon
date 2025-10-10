#!/usr/bin/env python3
"""
Phase 4 Application Task Breakdown Executor
Generates tasks.md files for Application Layer specifications
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

@dataclass
class TaskBreakdownResult:
    """Result of task breakdown generation."""
    spec_name: str
    success: bool
    tasks_generated: int
    error: Optional[str] = None
    duration_seconds: float = 0.0

class Phase4ApplicationExecutor(ReflectiveModule):
    """Phase 4 Application Layer task breakdown executor."""
    
    def __init__(self):
        super().__init__()
        self.layer_name = "Application"
        self.specs_processed = 0
        self.total_tasks_generated = 0
        self.results: List[TaskBreakdownResult] = []
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Return executor capabilities."""
        return {
            "layer": self.layer_name,
            "phase": 4,
            "operation": "task_breakdown",
            "batch_processing": True,
            "parallel_safe": True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy",
            "specs_processed": self.specs_processed,
            "total_tasks_generated": self.total_tasks_generated,
            "success_rate": len([r for r in self.results if r.success]) / max(len(self.results), 1)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            "name": "Phase4ApplicationExecutor",
            "version": "1.0.0",
            "description": "Generates task breakdown for Application Layer specifications",
            "layer": self.layer_name,
            "phase": 4
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "manual_task_creation",
            "message": "Task breakdown failed, manual task creation required"
        }
    
    def identify_application_specs(self) -> List[str]:
        """Identify Application Layer specifications that need tasks.md."""
        specs_dir = Path(".kiro/specs")
        application_specs = []
        
        # Get all specs that have requirements and design but no tasks
        for spec_dir in specs_dir.iterdir():
            if spec_dir.is_dir():
                spec_name = spec_dir.name
                req_file = spec_dir / "requirements.md"
                design_file = spec_dir / "design.md"
                tasks_file = spec_dir / "tasks.md"
                
                # Skip Bootstrap, Foundation, and Intelligence layers (handled by other executors)
                bootstrap_patterns = ["redis-dag-registry", "runtime-state-registry", "unified-dag-registry", 
                                    "dag-orchestration", "atomic-spec-execution", "prepare-spec-for-execution",
                                    "release-the-hounds", "spec-creation-dag", "spec-framework", "spec-mode"]
                
                foundation_patterns = ["reflective-module", "beast-mode", "artifact-driven", "async-task",
                                     "claude-code-redis", "subprocess-safety", "mcp-development", "mcp-server",
                                     "discord-bot", "google-calendar", "websocket-implementation"]
                
                intelligence_patterns = ["llm-powered", "multi-dimensional-vocabulary", "information-exhaust",
                                       "capture-beastmaster", "documentation-index", "prompt-file-processor",
                                       "spec-theater", "repository-constellation", "repository-synchronization",
                                       "practical-repository"]
                
                # Skip if it matches other layer patterns
                if any(pattern in spec_name for pattern in bootstrap_patterns + foundation_patterns + intelligence_patterns):
                    continue
                
                # Include if it has requirements and design but needs tasks
                if req_file.exists() and design_file.exists() and not tasks_file.exists():
                    application_specs.append(spec_name)
        
        return sorted(application_specs)
    
    def generate_task_breakdown_template(self, spec_name: str) -> str:
        """Generate task breakdown template for a specification."""
        return f"""# Implementation Plan: {spec_name}

## Overview
This implementation plan breaks down the {spec_name} specification into discrete, manageable coding tasks that build incrementally toward the complete application solution.

## Task Breakdown

### Phase 1: Application Foundation
- [ ] 1.1 Create application structure and configuration
  - Set up application directory structure
  - Implement configuration management system
  - Create application lifecycle management
  - _Requirements: Application foundation_

- [ ] 1.2 Implement user interface components
  - Create UI framework and component library
  - Implement responsive design and layouts
  - Add accessibility and usability features
  - _Requirements: User interface_

- [ ]* 1.3 Write UI component tests
  - Test component rendering and behavior
  - Verify responsive design and accessibility
  - Test user interactions and workflows
  - _Requirements: UI validation_

### Phase 2: Business Logic Implementation
- [ ] 2.1 Implement core business logic
  - Create business domain models and services
  - Implement business rules and validation
  - Add workflow and process management
  - _Requirements: Business logic_

- [ ] 2.2 Add data management capabilities
  - Implement data access and persistence
  - Create data validation and transformation
  - Add caching and performance optimization
  - _Requirements: Data management_

- [ ]* 2.3 Create business logic tests
  - Test business rules and validation
  - Verify data access and persistence
  - Test workflow and process management
  - _Requirements: Business logic validation_

### Phase 3: Integration and APIs
- [ ] 3.1 Implement API endpoints and services
  - Create REST API endpoints and documentation
  - Implement API authentication and authorization
  - Add API rate limiting and monitoring
  - _Requirements: API implementation_

- [ ] 3.2 Add external system integrations
  - Implement third-party service integrations
  - Create data synchronization and messaging
  - Add error handling and retry mechanisms
  - _Requirements: External integrations_

- [ ]* 3.3 Create integration tests
  - Test API endpoints and authentication
  - Verify external system integrations
  - Test data synchronization and messaging
  - _Requirements: Integration validation_

### Phase 4: User Experience Features
- [ ] 4.1 Implement advanced user features
  - Create user personalization and preferences
  - Implement search and filtering capabilities
  - Add notification and messaging systems
  - _Requirements: User experience_

- [ ] 4.2 Add collaboration and sharing
  - Implement user collaboration features
  - Create sharing and permission management
  - Add real-time updates and synchronization
  - _Requirements: Collaboration features_

- [ ]* 4.3 Create user experience tests
  - Test user personalization and preferences
  - Verify search and filtering functionality
  - Test collaboration and sharing features
  - _Requirements: User experience validation_

### Phase 5: Production and Operations
- [ ] 5.1 Implement monitoring and analytics
  - Create application performance monitoring
  - Implement user analytics and reporting
  - Add error tracking and alerting
  - _Requirements: Monitoring and analytics_

- [ ] 5.2 Add deployment and scaling
  - Implement containerization and orchestration
  - Create auto-scaling and load balancing
  - Add backup and disaster recovery
  - _Requirements: Production deployment_

- [ ] 5.3 Documentation and support
  - Create user documentation and help system
  - Add administrative tools and interfaces
  - Create troubleshooting and support guides
  - _Requirements: Documentation and support_

## Success Criteria
- All application features implemented and tested
- User interface responsive and accessible
- Business logic validated and performant
- API endpoints secure and documented
- Production deployment ready and monitored

## Dependencies
- UI framework and component libraries
- Database and data storage systems
- Authentication and authorization services
- Third-party APIs and integrations
- Monitoring and analytics platforms

## Estimated Timeline
- Phase 1: 3-4 days
- Phase 2: 4-5 days
- Phase 3: 3-4 days
- Phase 4: 3-4 days
- Phase 5: 2-3 days
- **Total: 15-20 days**

## Notes
- Tasks marked with * are optional testing tasks
- Each phase builds incrementally on previous phases
- All implementations follow responsive design principles
- User experience and accessibility are prioritized throughout
"""
    
    def generate_tasks_for_spec(self, spec_name: str) -> TaskBreakdownResult:
        """Generate tasks.md file for a specific specification."""
        start_time = time.time()
        
        try:
            spec_dir = Path(f".kiro/specs/{spec_name}")
            tasks_file = spec_dir / "tasks.md"
            
            # Check if tasks already exist
            if tasks_file.exists():
                return TaskBreakdownResult(
                    spec_name=spec_name,
                    success=True,
                    tasks_generated=0,
                    error="Tasks already exist",
                    duration_seconds=time.time() - start_time
                )
            
            # Generate task breakdown
            task_content = self.generate_task_breakdown_template(spec_name)
            
            # Write tasks file
            with open(tasks_file, 'w', encoding='utf-8') as f:
                f.write(task_content)
            
            # Count tasks generated (approximate)
            task_count = task_content.count('- [ ]')
            
            return TaskBreakdownResult(
                spec_name=spec_name,
                success=True,
                tasks_generated=task_count,
                duration_seconds=time.time() - start_time
            )
            
        except Exception as e:
            return TaskBreakdownResult(
                spec_name=spec_name,
                success=False,
                tasks_generated=0,
                error=str(e),
                duration_seconds=time.time() - start_time
            )
    
    def execute_phase_4_application(self) -> Dict[str, Any]:
        """Execute Phase 4 Application Layer task breakdown."""
        print("🐺 PHASE 4 APPLICATION TASK BREAKDOWN")
        print("=" * 60)
        
        # Identify Application specs
        application_specs = self.identify_application_specs()
        print(f"📊 Application specs identified: {len(application_specs)}")
        
        if not application_specs:
            print("✅ No Application specs need task breakdown")
            return {"status": "complete", "specs_processed": 0}
        
        # Process specs in batches
        batch_size = 12
        batches = [application_specs[i:i + batch_size] for i in range(0, len(application_specs), batch_size)]
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"\n📱 Processing batch {batch_num}/{len(batches)}")
            
            for spec_name in batch:
                print(f"  📱 Generating tasks: {spec_name}")
                result = self.generate_tasks_for_spec(spec_name)
                self.results.append(result)
                
                if result.success:
                    if result.tasks_generated > 0:
                        print(f"    ✅ Generated {result.tasks_generated} tasks for {spec_name}")
                        self.total_tasks_generated += result.tasks_generated
                    else:
                        print(f"    ✅ Tasks already complete for {spec_name}")
                else:
                    print(f"    ❌ Failed to generate tasks for {spec_name}: {result.error}")
                
                self.specs_processed += 1
        
        # Summary
        successful = len([r for r in self.results if r.success])
        print(f"\n✅ Phase 4 Application Task Breakdown Complete")
        print(f"📊 Processed: {self.specs_processed} specs")
        print(f"✅ Successful: {successful}")
        print(f"📝 Total tasks generated: {self.total_tasks_generated}")
        
        return {
            "status": "complete",
            "specs_processed": self.specs_processed,
            "successful": successful,
            "total_tasks_generated": self.total_tasks_generated,
            "results": [
                {
                    "spec_name": r.spec_name,
                    "success": r.success,
                    "tasks_generated": r.tasks_generated,
                    "error": r.error
                }
                for r in self.results
            ]
        }

def main():
    """Main execution function."""
    executor = Phase4ApplicationExecutor()
    result = executor.execute_phase_4_application()
    
    # Save results
    results_file = Path(".kiro/reports/phase4-application-results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📊 Results saved to {results_file}")
    
    return 0 if result["status"] == "complete" else 1

if __name__ == "__main__":
    sys.exit(main())