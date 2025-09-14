from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _validate_integrations(self) -> Dict[str, Any]:
        """Validate integration points and end-to-end workflows."""
        integration_results = {'working_integrations': [], 'broken_integrations': [], 'integration_score': 0.0, 'errors': []}
        try:
            import_issues = self._check_import_health()
            if not import_issues:
                integration_results['working_integrations'].append('All imports working')
                integration_results['integration_score'] = 100.0
            else:
                integration_results['broken_integrations'] = import_issues
                integration_results['integration_score'] = max(0, 100 - len(import_issues) * 20)
            config_files = [self.project_path / 'requirements.txt', self.project_path / 'pyproject.toml', self.project_path / 'setup.py']
            valid_configs = 0
            for config_file in config_files:
                if config_file.exists():
                    try:
                        if config_file.name == 'requirements.txt':
                            with open(config_file, 'r') as f:
                                lines = f.readlines()
                                if lines:
                                    valid_configs += 1
                        elif config_file.name in ['pyproject.toml', 'setup.py']:
                            valid_configs += 1
                    except Exception as e:
                        integration_results['errors'].append(f'Config file error {config_file}: {e}')
            if valid_configs > 0:
                integration_results['working_integrations'].append(f'Valid configuration files: {valid_configs}')
            else:
                integration_results['broken_integrations'].append('No valid configuration files found')
        except Exception as e:
            integration_results['errors'].append(f'Integration validation failed: {e}')
        return integration_results
