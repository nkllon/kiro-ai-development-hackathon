# BLACK FORMATTING FAILED - SYNTAX ERROR
# Error: Cannot parse: 1:12: Here is the revised code based on your feedback:

Here is the revised code based on your feedback:

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

    async def review(self, code):
        with self.urm.trace("review"):
             # Review the generated code...
             pass
             
             # Record operation metrics
             self.urm.record_metric("total_operations", 1)
             self.urm.record_metric("avg_review_time_ms", len(code))

    def select_model(self, task):
        # Select the model based on task requirements...
        return self.models[0]

class KiroSpecParser:
    def __init__(self):
        self.task_pattern = re.compile(r"^-    \[([ x])\](\*?)\s*(\d+(?:\.\d+)?)\s+(.+)$")

    def parse_tasks_file(self, tasks_path):
        with open(tasks_path, "r") as f:
            content = f.read()

class GitIntegration:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)

    async def create_feature_branch(self, task_id):
        branch_name = f"hybrid-gen/{task_id}"
        
class TaskStatusIntegration:
    def __init__(self, spec_path):
        self.spec_path = Path(specpec_path)
        self.tasks_file = self.spec_path / "tasks.md"

    async def update_task_status(self, task_id, status):