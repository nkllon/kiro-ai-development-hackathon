#!/usr/bin/env python3
"""
Phase 4 Intelligence Task Breakdown Executor
Generates tasks.md files for Intelligence Layer specifications
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

class Phase4IntelligenceExecutor(ReflectiveModule):
    """Phase 4 Intelligence Layer task breakdown executor."""
    
    def __init__(self):
        super().__init__()
        self.layer_name = "Intelligence"
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
            "name": "Phase4IntelligenceExecutor",
            "version": "1.0.0",
            "description": "Generates task breakdown for Intelligence Layer specifications",
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
    
    def identify_intelligence_specs(self) -> List[str]:
        """Identify Intelligence Layer specifications."""
        specs_dir = Path(".kiro/specs")
        intelligence_specs = []
        
        # Intelligence layer specs - AI/ML and smart processing
        intelligence_patterns = [
            "llm-powered-engagement-engines",
            "multi-dimensional-vocabulary-projector",
            "information-exhaust-preservation",
            "capture-beastmaster-outputs",
            "documentation-index-generator",
            "prompt-file-processor-hook",
            "spec-theater-remediation",
            "repository-constellation",
            "repository-synchronization-cleanup",
            "practical-repository-cleanup"
        ]
        
        for spec_dir in specs_dir.iterdir():
            if spec_dir.is_dir():
                spec_name = spec_dir.name
                # Check if it matches intelligence patterns
                if any(pattern in spec_name for pattern in intelligence_patterns):
                    # Verify it has requirements and design but needs tasks
                    req_file = spec_dir / "requirements.md"
                    design_file = spec_dir / "design.md"
                    tasks_file = spec_dir / "tasks.md"
                    
                    if req_file.exists() and design_file.exists() and not tasks_file.exists():
                        intelligence_specs.append(spec_name)
        
        return sorted(intelligence_specs)
    
    def generate_task_breakdown_template(self, spec_name: str) -> str:
        """Generate task breakdown template for a specification."""
        return f"""# Implementation Plan: {spec_name}

## Overview
This implementation plan breaks down the {spec_name} specification into discrete, manageable coding tasks that build incrementally toward the complete AI/ML solution.

## Task Breakdown

### Phase 1: AI/ML Foundation
- [ ] 1.1 Create AI/ML infrastructure components
  - Set up machine learning pipeline infrastructure
  - Implement model management and versioning
  - Create data processing and feature engineering
  - _Requirements: AI/ML foundation_

- [ ] 1.2 Implement data ingestion and preprocessing
  - Create data collection and validation systems
  - Implement data cleaning and transformation
  - Add data quality monitoring and alerting
  - _Requirements: Data processing_

- [ ]* 1.3 Write data pipeline tests
  - Test data ingestion and validation
  - Verify data transformation and quality
  - Test pipeline performance and reliability
  - _Requirements: Data pipeline validation_

### Phase 2: Intelligence Processing
- [ ] 2.1 Implement core AI/ML algorithms
  - Create machine learning models and training
  - Implement inference and prediction systems
  - Add model evaluation and validation
  - _Requirements: AI/ML algorithms_

- [ ] 2.2 Add intelligent processing capabilities
  - Implement natural language processing
  - Create pattern recognition and analysis
  - Add intelligent decision making systems
  - _Requirements: Intelligent processing_

- [ ]* 2.3 Create AI/ML model tests
  - Test model training and inference
  - Verify model accuracy and performance
  - Test model deployment and scaling
  - _Requirements: AI/ML validation_

### Phase 3: Knowledge Management
- [ ] 3.1 Implement knowledge extraction
  - Create information extraction systems
  - Implement knowledge graph construction
  - Add semantic analysis and understanding
  - _Requirements: Knowledge extraction_

- [ ] 3.2 Add knowledge storage and retrieval
  - Implement knowledge base management
  - Create intelligent search and retrieval
  - Add knowledge recommendation systems
  - _Requirements: Knowledge management_

- [ ]* 3.3 Create knowledge system tests
  - Test knowledge extraction and storage
  - Verify search and retrieval accuracy
  - Test recommendation system performance
  - _Requirements: Knowledge system validation_

### Phase 4: Intelligent Automation
- [ ] 4.1 Implement automated decision making
  - Create rule-based decision systems
  - Implement machine learning-based automation
  - Add intelligent workflow orchestration
  - _Requirements: Intelligent automation_

- [ ] 4.2 Add adaptive learning capabilities
  - Implement online learning and adaptation
  - Create feedback loops and improvement
  - Add performance monitoring and optimization
  - _Requirements: Adaptive learning_

- [ ]* 4.3 Create automation tests
  - Test automated decision making
  - Verify adaptive learning capabilities
  - Test system performance and reliability
  - _Requirements: Automation validation_

### Phase 5: Integration and Deployment
- [ ] 5.1 Integrate with existing systems
  - Connect to data sources and APIs
  - Implement system integration patterns
  - Add monitoring and observability
  - _Requirements: System integration_

- [ ] 5.2 Create intelligent interfaces
  - Implement AI-powered user interfaces
  - Create conversational and interactive systems
  - Add intelligent assistance capabilities
  - _Requirements: Intelligent interfaces_

- [ ] 5.3 Documentation and training
  - Create AI/ML system documentation
  - Add model documentation and explanations
  - Create training materials and examples
  - _Requirements: Documentation completeness_

## Success Criteria
- All AI/ML components implemented and trained
- Intelligent processing capabilities operational
- Knowledge management systems functional
- Automated decision making validated
- System integration and deployment complete

## Dependencies
- Machine learning frameworks and libraries
- Data processing and storage infrastructure
- Model training and deployment platforms
- Knowledge graph and semantic technologies
- Monitoring and observability systems

## Estimated Timeline
- Phase 1: 4-5 days
- Phase 2: 5-6 days
- Phase 3: 4-5 days
- Phase 4: 3-4 days
- Phase 5: 3-4 days
- **Total: 19-24 days**

## Notes
- Tasks marked with * are optional testing tasks
- Each phase builds incrementally on previous phases
- All implementations include model validation and testing
- Performance and accuracy metrics are tracked throughout
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
    
    def execute_phase_4_intelligence(self) -> Dict[str, Any]:
        """Execute Phase 4 Intelligence Layer task breakdown."""
        print("🐺 PHASE 4 INTELLIGENCE TASK BREAKDOWN")
        print("=" * 60)
        
        # Identify Intelligence specs
        intelligence_specs = self.identify_intelligence_specs()
        print(f"📊 Intelligence specs identified: {len(intelligence_specs)}")
        
        if not intelligence_specs:
            print("✅ No Intelligence specs need task breakdown")
            return {"status": "complete", "specs_processed": 0}
        
        # Process specs in batches
        batch_size = 12
        batches = [intelligence_specs[i:i + batch_size] for i in range(0, len(intelligence_specs), batch_size)]
        
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
        print(f"\n✅ Phase 4 Intelligence Task Breakdown Complete")
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
    executor = Phase4IntelligenceExecutor()
    result = executor.execute_phase_4_intelligence()
    
    # Save results
    results_file = Path(".kiro/reports/phase4-intelligence-results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📊 Results saved to {results_file}")
    
    return 0 if result["status"] == "complete" else 1

if __name__ == "__main__":
    sys.exit(main())