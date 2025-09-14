from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def export_validation_report(self, file_path: str):
        """Export validation report to file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'validation_summary': self.get_validation_summary(),
            'validation_history': [
                {
                    'component_name': report.component_name,
                    'timestamp': report.timestamp.isoformat(),
                    'overall_score': report.overall_score,
                    'results': report.results
                }
                for report in self.validation_history
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        register_module(self.__class__.__name__, self)
# Global instance for easy access
enhanced_validator = EnhancedValidationFramework()
