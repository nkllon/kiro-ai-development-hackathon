from src.rm_ddd.core.registry import register_module

    def get_hackathon_templates(self) -> Dict[str, HackathonConfig]:
        """Get available hackathon configuration templates."""
        return {'devpost': DEVPOST_HACKATHON_TEMPLATE, 'mlh': MLH_HACKATHON_TEMPLATE}
