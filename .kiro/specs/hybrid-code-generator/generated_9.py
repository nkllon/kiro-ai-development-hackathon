# BLACK FORMATTING FAILED - SYNTAX ERROR
# Error: Cannot parse: 21:65: Failed to parse: UnterminatedString

import re
from pathlib import Path
import git
import unified_reflective_module as urm
from typing import List
from kiro_spec_parser import KiroSpecParser   # Added missing imports
from git_integration import GitIntegration   # Added missing imports
from task_status_integration import TaskStatusIntegration   # Added missing imports
from kiro_task import KiroTask   # Added missing imports

class HybridCodeGenerator:
    def __init__(self, spec_path: str, repo_path: str):
        self.spec_path = Path(spec_path)
        self.repo_path = Path(repo_path)

        # Initialize integrations
        self.urm = urm.UnifiedReflectiveModule()
        self.kiro_parser = KiroSpecParser()
        self.git_integration = GitIntegration(repo_path)
        self.task_status_integration = TaskStatusIntegration(spec_path)
        self.tasks = self.kiro_parser.parse_tasks_file(self.spec.md")
        self.context = self.kiro_parser.load_context_files(self.spec_path)

    async def generate_code(self, task_id: str):
        # Start operation trace
        with self.urm.trace("generate_code", {"task_id": task_id}) as span:
            try:
                generated_code = await self._generate_from_task(task_id)

                # End operation trace with success
                span.set_success()
            except Exception as e:
                # End operation trace with failure and exception
                span.set_failure("Code generation failed", {"error": str(e)})

        return generated_code

    async def _generate_from_task(self, task_id: str):
        # Load and parse task
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Generate code
        generated_code, files = await self._generate_from_specs(task.description)

        # Commit to Git and update status
        branch_name = await self.git_integration.create_feature_branch(task_id)
        await self.git_integration.commit_generated_code(files, task.description)
        await self.task_status_integration.update_task_status(task_id, "completed")

        return generated_code

    async def _generate_from_specs(self, description: str):
        # Start operation trace
        with self.urm.trace("generate_from_specs", {"description": description[:50]}) as span:
            try:
                # Load and parse requirements
                requirements = [r for r in self.context["requirements"].split("\n") if r.startswith(f"{task.id}.")]

                # Generate code based on task and requirements
                generated_code, files = await self._generate_from_specs(description, requirements)

                # End operation trace with success
                span.set_success()
            except Exception as e:
                # End operation trace with failure and exception
                span.set_failure("Code generation from specs failed", {"error": str(e)})

        return generated_code, files  # Ensuring the function returns both `generated_code` and `files`