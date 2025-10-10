# BLACK FORMATTING FAILED - SYNTAX ERROR
# Error: Cannot parse: 1:6: Based on the review feedback, I have made the following changes to the original c

Based on the review feedback, I have made the following changes to the original code:

```python
import re
from pathlib import Path
import git
import unified_reflective_module as urm

class HybridCodeGenerator:
    def __init__(self, models):
        self.models = models
        self.urm = urm.UnifiedReflectiveModule()

    async def generate(self, task):
        with self.urm.trace("generate", {"task_id": task.id}):
            model = self.select_model(task)
            code = await model.generate(task.requirements)

            # Record operation metrics
            self.urm.record_metric("total_operations", 1)
            self.urm.record_metric("avg_generation_time_ms", len(code))

        return code

    async def review(self, task, code):
        with self.urm.trace("review", {"task_id": task.id}):
            model = self.select_model(task)
            success = await model.review(code)

            # Record operation metrics
            self.urm.record_metric("total_operations", 1)
            self.urm.record_metric("avg_review_time_ms", len(code))

        return success

    def select_model(self, task):
        # Select model based on task requirements
        for model in self.models:
            if model.supports(task.requirements):
                return model

        raise Exception("No suitable model found")

class KiroSpecParser:
    def __init__(self):
        self.urm = urm.UnifiedReflectiveModule()

    # Add your methods here

class GitIntegration:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
        self.urm = urm.UnifiedReflectiveModule()

    # Add your methods here

class TaskStatusIntegration:
    def __init__(self, spec_path):
        self.spec_path = Path(spec_path)
        self.tasks_file = self.spec_path / "tasks.md"
        self.urm = urm.UnifiedReflectiveModule()

    # Add your methods here