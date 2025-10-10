# BLACK FORMATTING FAILED - SYNTAX ERROR
# Error: Cannot parse: 1:13: Here is your corrected code:

Here is your corrected code:

```python
import re
from pathlib import Path
import git
import unified_reflective_module as urm

class HybridCodeGenerator:
    def __init__(self, model1, model2):
        self.models = [model1, model2]
        self.urm = urm.UnifiedReflectiveModule()

    async def generate(self, task_id, context):
        with self.urm.trace("generate", {"task_id": task_id}) as trace:
            try:
                if "deepseek" in context["requirements"]:
                    model = self.models[0]
                else:
                    model = self.models[1]

                code = await model.generate(task_id, context)
                trace.set("code", code)
            except Exception as e:
                trace.fail(e)

        return code

    async def review(self, task_id, generated_code):
        with self.urm.trace("review", {"task_id": task_id}) as trace:
            try:
                pass   # Manual review process here...

                trace.set("result", "approved")
            except Exception as e:
                trace.fail(e)

        return "approved"

    async def integrate_with_git(self, task_id, files):
        git = GitIntegration("/path/to/your/repo")

        try:
            branch_name = await git.create_feature_branch(task_id)

            await git.commit_generated_code(files, task_description)

            return branch_name
        except Exception as e:
            self.urm.log("git_integration", {"error": str(e)})

        return None

    async def update_task_status(self, task_id, status):
        try:
            tasks = KiroSpecParser().parse_tasks_file("/path/to/your/spec.md")

            for task in tasks:
                if task.id == task_id:
                    task.metadata["status"] = status

                    with open("/path/to/your/spec.md", "w") as f:
                        f.write(
                            "\n".join(
                                f'- [{t.metadata["completed"]}]{t.id} {t.description}'
                                for t in tasks
                            )
                        )

            return status
        except Exception as e:
            self.urm.log("task_status", {"error": str(e)})

        return None

    async def load_context_files(self, spec_dir):
        try:
            parser = KiroSpecParser()

            tasks = parser.parse_tasks_file("/path/to/your/spec.md")
            context = parser.load_context_files(spec_dir)

            return (tasks, context)
        except Exception as e:
            self.urm.log("load_context", {"error": str(e)})

        return None

    async def run(self, task_id):
        with self.urm.trace("run", {"task_id": task_id}) as trace:
            try:
                tasks, context = await self.load_context_files("/path/to/your/spec.dir")

                if not tasks or task_id not in [t.id for t in tasks]:
                    raise Exception(f"Task {task_id} not found.")

                generated_code = await self.generate(task_id, context)

                if await self.review(task_id, generated_code) == "approved":
                    branch_name = await self.integrate_with_git(
                        task_id, ["generated_file.py"]
                       )

                    await self.update_task_status(task_id, "completed")

                    trace.set("branch", branch_name)
                else:
                    trace.set("result", "rejected")
            except Exception as e:
                trace.fail(e)

        return None