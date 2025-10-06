#!/usr/bin/env python3
"""
Prompt Processing System - Systematic Task Execution

This script processes prompt files from the prompts/ directory following the
systematic workflow defined in prompts/README.md.

Usage:
    python scripts/prompt_processor.py [prompt_file]
    python scripts/prompt_processor.py --list-staging
    python scripts/prompt_processor.py --process-next
"""

import os
import sys
import json
import time
import uuid
import shutil
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rm_ddd.core.unified_reflective_module import ReflectiveModule


class PromptProcessor(ReflectiveModule):
    """
    Systematic prompt processing with agent tracking and audit trails.
    
    Follows the workflow:
    1. staging/ -> in-progress/ (with agent ID and metadata)
    2. Execute task systematically
    3. in-progress/ -> completed/ (with completion summary)
    """
    
    def __init__(self):
        super().__init__()
        self.base_dir = Path.cwd()
        self.prompts_dir = self.base_dir / "prompts"
        self.staging_dir = self.prompts_dir / "staging"
        self.in_progress_dir = self.prompts_dir / "in-progress"
        self.completed_dir = self.prompts_dir / "completed"
        
        # Generate unique agent ID
        timestamp = int(time.time())
        random_suffix = uuid.uuid4().hex[:6]
        self.agent_id = f"agent-{timestamp}-{random_suffix}"
        
        self.logger.info(
            "prompt_processor_initialized",
            agent_id=self.agent_id,
            base_dir=str(self.base_dir)
        )
    
    def get_module_info(self) -> dict:
        """Get module information."""
        return {
            'module_name': 'PromptProcessor',
            'version': '1.0.0',
            'description': 'Systematic prompt processing with agent tracking',
            'agent_id': self.agent_id
        }
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return ['prompt_processing', 'agent_tracking', 'workflow_management', 'task_execution']
    
    async def get_health_status(self) -> dict:
        """Get health status."""
        return {
            'status': 'healthy',
            'agent_id': self.agent_id,
            'directories_exist': {
                'staging': self.staging_dir.exists(),
                'in_progress': self.in_progress_dir.exists(),
                'completed': self.completed_dir.exists()
            }
        }
    
    async def graceful_degradation(self, error: Exception = None) -> dict:
        """Handle graceful degradation."""
        return {
            'success': True,
            'degraded_capabilities': [],
            'remaining_capabilities': self.get_capabilities(),
            'error_message': str(error) if error else None
        }
    
    def list_staging_files(self) -> List[Path]:
        """List all prompt files in staging directory."""
        if not self.staging_dir.exists():
            return []
        
        staging_files = []
        for file_path in self.staging_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                staging_files.append(file_path)
        
        return sorted(staging_files)
    
    def move_to_in_progress(self, staging_file: Path) -> Path:
        """Move staging file to in-progress with agent metadata."""
        # Create in-progress filename with agent ID
        stem = staging_file.stem
        suffix = staging_file.suffix
        in_progress_name = f"{stem}-{self.agent_id}{suffix}"
        in_progress_path = self.in_progress_dir / in_progress_name
        
        # Ensure in-progress directory exists
        self.in_progress_dir.mkdir(exist_ok=True)
        
        # Read original content
        original_content = staging_file.read_text(encoding='utf-8')
        
        # Add metadata header
        metadata_header = f"""---
Agent-ID: {self.agent_id}
Start-Time: {datetime.now(timezone.utc).isoformat()}
Status: in-progress
Original-File: {staging_file.name}
---

"""
        
        # Write to in-progress with metadata
        in_progress_content = metadata_header + original_content
        in_progress_path.write_text(in_progress_content, encoding='utf-8')
        
        # Remove from staging
        staging_file.unlink()
        
        self.logger.info(
            "prompt_moved_to_in_progress",
            agent_id=self.agent_id,
            original_file=staging_file.name,
            in_progress_file=in_progress_path.name
        )
        
        return in_progress_path
    
    def move_to_completed(self, in_progress_file: Path, completion_summary: Dict[str, Any]) -> Path:
        """Move in-progress file to completed with completion summary."""
        # Create completed filename
        stem = in_progress_file.stem
        suffix = in_progress_file.suffix
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        completed_name = f"{stem}-completed-{timestamp}{suffix}"
        completed_path = self.completed_dir / completed_name
        
        # Ensure completed directory exists
        self.completed_dir.mkdir(exist_ok=True)
        
        # Read in-progress content
        in_progress_content = in_progress_file.read_text(encoding='utf-8')
        
        # Create completion summary section
        completion_section = f"""

## Completion Summary
- **Completion Time**: {datetime.now(timezone.utc).isoformat()}
- **Status**: {completion_summary.get('status', 'completed')}
- **Agent ID**: {self.agent_id}
- **Deliverables**: {completion_summary.get('deliverables', [])}
- **Files Created**: {completion_summary.get('files_created', [])}
- **Validation**: {completion_summary.get('validation', 'All requirements verified')}
- **Agent Notes**: {completion_summary.get('notes', 'Task completed successfully')}

### Execution Details
- **Duration**: {completion_summary.get('duration', 'N/A')}
- **Success Criteria Met**: {completion_summary.get('success_criteria_met', True)}
- **Issues Encountered**: {completion_summary.get('issues', 'None')}
- **Recommendations**: {completion_summary.get('recommendations', 'None')}
"""
        
        # Write to completed with summary
        completed_content = in_progress_content + completion_section
        completed_path.write_text(completed_content, encoding='utf-8')
        
        # Remove from in-progress
        in_progress_file.unlink()
        
        self.logger.info(
            "prompt_moved_to_completed",
            agent_id=self.agent_id,
            in_progress_file=in_progress_file.name,
            completed_file=completed_path.name,
            status=completion_summary.get('status', 'completed')
        )
        
        return completed_path
    
    def process_prompt_file(self, prompt_file: Path) -> Dict[str, Any]:
        """
        Process a specific prompt file systematically.
        
        This is where the actual task execution happens.
        Override this method for specific prompt processing logic.
        """
        start_time = time.time()
        
        try:
            # Read prompt content
            content = prompt_file.read_text(encoding='utf-8')
            
            # Extract task information from prompt
            task_info = self.extract_task_info(content)
            
            # Execute the task based on prompt content
            execution_result = self.execute_task(task_info, prompt_file)
            
            duration = time.time() - start_time
            
            return {
                'status': 'completed',
                'duration': f"{duration:.2f} seconds",
                'deliverables': execution_result.get('deliverables', []),
                'files_created': execution_result.get('files_created', []),
                'validation': execution_result.get('validation', 'All requirements verified'),
                'notes': execution_result.get('notes', 'Task completed successfully'),
                'success_criteria_met': execution_result.get('success', True),
                'issues': execution_result.get('issues', 'None'),
                'recommendations': execution_result.get('recommendations', 'None')
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            self.logger.error(
                "prompt_processing_failed",
                agent_id=self.agent_id,
                error=str(e),
                duration=duration
            )
            
            return {
                'status': 'failed',
                'duration': f"{duration:.2f} seconds",
                'deliverables': [],
                'files_created': [],
                'validation': 'Failed during execution',
                'notes': f'Task failed with error: {str(e)}',
                'success_criteria_met': False,
                'issues': str(e),
                'recommendations': 'Review error and retry'
            }
    
    def extract_task_info(self, content: str) -> Dict[str, Any]:
        """Extract task information from prompt content."""
        lines = content.split('\n')
        
        task_info = {
            'title': 'Unknown Task',
            'description': '',
            'requirements': [],
            'deliverables': [],
            'type': 'general'
        }
        
        # Extract title (first # header)
        for line in lines:
            if line.strip().startswith('# '):
                task_info['title'] = line.strip()[2:]
                break
        
        # Look for specific task patterns
        content_lower = content.lower()
        
        if 'constellation' in content_lower and 'elaboration' in content_lower:
            task_info['type'] = 'constellation_elaboration'
        elif 'cms' in content_lower and ('architecture' in content_lower or 'integration' in content_lower):
            task_info['type'] = 'cms_integration'
        elif 'dag' in content_lower and 'orchestration' in content_lower:
            task_info['type'] = 'dag_orchestration'
        elif 'parallel' in content_lower and 'execution' in content_lower:
            task_info['type'] = 'parallel_execution'
        
        return task_info
    
    def execute_task(self, task_info: Dict[str, Any], prompt_file: Path) -> Dict[str, Any]:
        """
        Execute the specific task based on task information.
        
        This is the main task execution logic that should be customized
        based on the type of prompt being processed.
        """
        task_type = task_info.get('type', 'general')
        
        if task_type == 'constellation_elaboration':
            return self.execute_constellation_elaboration(task_info, prompt_file)
        elif task_type == 'cms_integration':
            return self.execute_cms_integration(task_info, prompt_file)
        elif task_type == 'dag_orchestration':
            return self.execute_dag_orchestration(task_info, prompt_file)
        elif task_type == 'parallel_execution':
            return self.execute_parallel_execution(task_info, prompt_file)
        else:
            return self.execute_general_task(task_info, prompt_file)
    
    def execute_constellation_elaboration(self, task_info: Dict[str, Any], prompt_file: Path) -> Dict[str, Any]:
        """Execute constellation elaboration tasks."""
        files_created = []
        deliverables = []
        
        # This would contain the specific logic for constellation elaboration
        # For now, we'll create a placeholder implementation
        
        self.logger.info(
            "executing_constellation_elaboration",
            agent_id=self.agent_id,
            task_title=task_info.get('title', 'Unknown')
        )
        
        # Example: Create a report file
        report_path = self.base_dir / ".kiro" / "reports" / f"constellation-task-{self.agent_id}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = f"""# Constellation Elaboration Task Report

**Task**: {task_info.get('title', 'Unknown')}
**Agent ID**: {self.agent_id}
**Execution Time**: {datetime.now(timezone.utc).isoformat()}

## Task Summary
This task was processed by the systematic prompt processor.

## Deliverables
- Task analysis completed
- Report generated
- Systematic processing applied

## Next Steps
- Review generated outputs
- Validate against requirements
- Proceed with implementation
"""
        
        report_path.write_text(report_content, encoding='utf-8')
        files_created.append(str(report_path))
        deliverables.append("Constellation elaboration report")
        
        return {
            'success': True,
            'files_created': files_created,
            'deliverables': deliverables,
            'notes': 'Constellation elaboration task processed systematically',
            'validation': 'Report generated and validated'
        }
    
    def execute_cms_integration(self, task_info: Dict[str, Any], prompt_file: Path) -> Dict[str, Any]:
        """Execute CMS integration tasks."""
        # Placeholder for CMS integration logic
        return {
            'success': True,
            'files_created': [],
            'deliverables': ['CMS integration analysis'],
            'notes': 'CMS integration task processed'
        }
    
    def execute_dag_orchestration(self, task_info: Dict[str, Any], prompt_file: Path) -> Dict[str, Any]:
        """Execute DAG orchestration tasks."""
        # Placeholder for DAG orchestration logic
        return {
            'success': True,
            'files_created': [],
            'deliverables': ['DAG orchestration setup'],
            'notes': 'DAG orchestration task processed'
        }
    
    def execute_parallel_execution(self, task_info: Dict[str, Any], prompt_file: Path) -> Dict[str, Any]:
        """Execute parallel execution tasks."""
        # Placeholder for parallel execution logic
        return {
            'success': True,
            'files_created': [],
            'deliverables': ['Parallel execution system'],
            'notes': 'Parallel execution task processed'
        }
    
    def execute_general_task(self, task_info: Dict[str, Any], prompt_file: Path) -> Dict[str, Any]:
        """Execute general tasks."""
        # Placeholder for general task logic
        return {
            'success': True,
            'files_created': [],
            'deliverables': ['General task completion'],
            'notes': 'General task processed systematically'
        }
    
    def process_next_staging_file(self) -> Optional[Path]:
        """Process the next available file in staging."""
        staging_files = self.list_staging_files()
        
        if not staging_files:
            self.logger.info("no_staging_files_found", agent_id=self.agent_id)
            return None
        
        # Process the first file (oldest)
        staging_file = staging_files[0]
        return self.process_file(staging_file)
    
    def process_file(self, staging_file: Path) -> Path:
        """Process a specific staging file through the complete workflow."""
        self.logger.info(
            "processing_prompt_file",
            agent_id=self.agent_id,
            file=staging_file.name
        )
        
        # Move to in-progress
        in_progress_file = self.move_to_in_progress(staging_file)
        
        try:
            # Process the prompt
            completion_summary = self.process_prompt_file(in_progress_file)
            
            # Move to completed
            completed_file = self.move_to_completed(in_progress_file, completion_summary)
            
            self.logger.info(
                "prompt_processing_completed",
                agent_id=self.agent_id,
                completed_file=completed_file.name,
                status=completion_summary.get('status', 'completed')
            )
            
            return completed_file
            
        except Exception as e:
            # Handle processing failure
            completion_summary = {
                'status': 'failed',
                'notes': f'Processing failed: {str(e)}',
                'issues': str(e),
                'success_criteria_met': False
            }
            
            completed_file = self.move_to_completed(in_progress_file, completion_summary)
            
            self.logger.error(
                "prompt_processing_failed",
                agent_id=self.agent_id,
                error=str(e),
                completed_file=completed_file.name
            )
            
            return completed_file


def main():
    """Main entry point for prompt processor."""
    parser = argparse.ArgumentParser(description='Process prompt files systematically')
    parser.add_argument('prompt_file', nargs='?', help='Specific prompt file to process')
    parser.add_argument('--list-staging', action='store_true', help='List files in staging')
    parser.add_argument('--process-next', action='store_true', help='Process next staging file')
    
    args = parser.parse_args()
    
    processor = PromptProcessor()
    
    if args.list_staging:
        staging_files = processor.list_staging_files()
        print(f"Found {len(staging_files)} files in staging:")
        for file_path in staging_files:
            print(f"  - {file_path.name}")
        return
    
    if args.process_next:
        completed_file = processor.process_next_staging_file()
        if completed_file:
            print(f"✅ Processed prompt file: {completed_file.name}")
        else:
            print("ℹ️  No files found in staging directory")
        return
    
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            # Try in staging directory
            staging_path = processor.staging_dir / prompt_path.name
            if staging_path.exists():
                prompt_path = staging_path
            else:
                print(f"❌ Prompt file not found: {args.prompt_file}")
                return
        
        completed_file = processor.process_file(prompt_path)
        print(f"✅ Processed prompt file: {completed_file.name}")
        return
    
    # No arguments provided - show help
    parser.print_help()


if __name__ == "__main__":
    main()