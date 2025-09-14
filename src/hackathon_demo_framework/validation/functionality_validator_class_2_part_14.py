from src.rm_ddd.core.registry import register_module

    def _check_documentation_completeness(self) -> List[str]:
        """Check for missing documentation."""
        doc_issues = []
        readme_files = list(self.project_path.glob('README*'))
        if not readme_files:
            doc_issues.append('Missing README file')
        else:
            try:
                with open(readme_files[0], 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                if len(readme_content.strip()) < 100:
                    doc_issues.append('README file too short - needs more content')
                required_sections = ['installation', 'usage', 'setup']
                missing_sections = []
                for section in required_sections:
                    if section.lower() not in readme_content.lower():
                        missing_sections.append(section)
                if missing_sections:
                    doc_issues.append(f"README missing sections: {', '.join(missing_sections)}")
            except Exception as e:
                doc_issues.append(f'Could not analyze README: {e}')
        source_files = list(self.project_path.rglob('src/**/*.py'))
        undocumented_files = []
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if '"""' not in content and "'''" not in content:
                    undocumented_files.append(source_file.name)
            except Exception:
                pass
        if undocumented_files:
            doc_issues.append(f"Files missing docstrings: {', '.join(undocumented_files[:5])}")
        return doc_issues
