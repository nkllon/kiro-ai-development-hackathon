from src.rm_ddd.core.registry import register_module

    def generate_judge_package(self, demo_package: DemoPackage) -> Dict[str, Any]:
        """
        Generate complete package for judge evaluation.
        
        Args:
            demo_package: Prepared demo package
            
        Returns:
            Judge evaluation package with all materials
        """
        return {'executive_summary': demo_package.judge_materials.executive_summary, 'quick_start_guide': demo_package.judge_materials.quick_start_guide, 'demo_script': demo_package.demo_script, 'technical_highlights': {'score': demo_package.technical_assessment.overall_technical_score, 'test_coverage': demo_package.technical_assessment.test_coverage_percentage, 'key_features': demo_package.systematic_evidence.beast_mode_highlights}, 'systematic_excellence': {'evidence': demo_package.systematic_evidence.spec_driven_evidence, 'advantages': demo_package.systematic_evidence.competitive_advantages, 'maturity_indicators': demo_package.systematic_evidence.development_maturity_indicators}, 'compliance_status': {'score': demo_package.compliance_assessment.overall_compliance_score, 'requirements_met': demo_package.compliance_assessment.mandatory_requirements, 'issues': demo_package.compliance_assessment.blocking_issues}, 'demo_reliability': {'score': demo_package.demo_environment.reliability_score, 'backup_plans': demo_package.backup_plans, 'troubleshooting': demo_package.judge_materials.troubleshooting_guide}}
