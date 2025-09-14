from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def prepare_hackathon_demo(self, quick_mode: bool=False) -> DemoPackage:
        """
        Orchestrate complete hackathon demo preparation workflow.
        
        Args:
            quick_mode: If True, skip some time-intensive validations
            
        Returns:
            Complete demo package ready for hackathon submission
        """
        self.logger.info('Starting hackathon demo preparation workflow')
        try:
            self.logger.info('Phase 1: Validating technical foundation')
            technical_assessment = self._validate_technical_completeness()
            self.logger.info('Phase 2: Collecting systematic excellence evidence')
            systematic_evidence = self._collect_systematic_evidence()
            self.logger.info('Phase 3: Preparing demo environment')
            demo_environment = self._prepare_demo_environment()
            self.logger.info('Phase 4: Generating presentation content')
            demo_script = self._generate_demo_script()
            judge_materials = self._create_judge_materials(systematic_evidence)
            self.logger.info('Phase 5: Verifying hackathon compliance')
            compliance_assessment = self._verify_compliance()
            demo_package = DemoPackage(demo_script=demo_script, judge_materials=judge_materials, demo_environment=demo_environment, systematic_evidence=systematic_evidence, technical_assessment=technical_assessment, compliance_assessment=compliance_assessment)
            if not quick_mode:
                self.logger.info('Phase 7: Final validation and optimization')
                presentation_metrics = self._measure_presentation_impact(demo_package)
                demo_package.presentation_metrics = presentation_metrics
                demo_package = self._optimize_demo_package(demo_package)
            self.logger.info(f'Demo preparation complete. Readiness score: {demo_package.get_readiness_score():.1f}')
            return demo_package
        except Exception as e:
            self.logger.error(f'Demo preparation failed: {e}')
            raise

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

