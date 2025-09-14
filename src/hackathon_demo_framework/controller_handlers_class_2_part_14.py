from src.rm_ddd.core.registry import register_module

    def _generate_demo_script(self) -> DemoScript:
        """Generate structured demo script optimized for hackathon judging."""
        return DemoScript(opening_hook='Compelling problem statement that resonates with judges', problem_statement='Clear articulation of the problem being solved', solution_overview='High-level solution approach and key innovations', technical_demonstration='Live demonstration of core functionality', systematic_excellence='Showcase of systematic development approach', business_impact='Clear value proposition and market potential', closing_call_to_action='Memorable closing with clear next steps', total_duration=0, backup_plans=['Recorded demo fallback', 'Screenshot walkthrough', 'Architecture diagram explanation'])
