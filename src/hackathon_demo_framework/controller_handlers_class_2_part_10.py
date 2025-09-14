from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class CustomizehackathonconfigClass:
    """Auto-generated class for functions."""

    def customize_hackathon_config(self, template_name: str, customizations: Dict[str, Any]) -> HackathonConfig:
    """
    Customize hackathon configuration from template.

    Args:
    template_name: Name of template to use
    customizations: Dictionary of customizations to apply

    Returns:
    Customized hackathon configuration
    """
    templates = self.get_hackathon_templates()
    if template_name not in templates:
    raise ValueError(f'Unknown template: {template_name}')
    template = templates[template_name]
    config_dict = {'hackathon_name': customizations.get('hackathon_name', template.hackathon_name), 'hackathon_id': customizations.get('hackathon_id', template.hackathon_id), 'submission_deadline': customizations.get('submission_deadline', template.submission_deadline), 'demo_time_limit': customizations.get('demo_time_limit', template.demo_time_limit), 'judging_criteria': customizations.get('judging_criteria', template.judging_criteria), 'required_elements': customizations.get('required_elements', template.required_elements), 'theme_requirements': customizations.get('theme_requirements', template.theme_requirements), 'technical_requirements': customizations.get('technical_requirements', template.technical_requirements), 'platform_requirements': customizations.get('platform_requirements', template.platform_requirements)}
    return HackathonConfig(**config_dict)
