
def _create_instances(self, plan: DistributionPlan) -> List[KiroInstance]:
    """Create Kiro instances based on distribution plan."""
    instances = []
    for instance_id, task_ids in plan.instance_assignments.items():
        if not task_ids:
            continue
        from .models import PeacockTheme
        from pathlib import Path
from src.rm_ddd.core.health import ModuleHealth

        theme = PeacockTheme(color_name=f'color-{len(instances) + 1}', primary_color=f"#{''.join([hex(hash(instance_id))[i] for i in range(2, 8)])}", accent_color=f"#{''.join([hex(hash(instance_id + 'accent'))[i] for i in range(2, 8)])}")
        instance = KiroInstance(instance_id=instance_id, branch_name=f'feature/{instance_id}', workspace_path=Path(f'/tmp/kiro-workspaces/{instance_id}'), source_repository='.', task_assignments=task_ids, communication_endpoint=f'tcp://localhost:{5000 + len(instances)}', peacock_theme=theme, visual_identifier=theme.color_name)
        instances.append(instance)
    return instances
