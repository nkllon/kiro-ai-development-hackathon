from src.rm_ddd.core.health import ModuleHealth

def assess_code_quality(self) -> CodeQualityReport:
    """
        Perform comprehensive code quality assessment.
        
        Returns:
            Detailed code quality report with scores and recommendations
        """
    self.logger.info('Starting comprehensive code quality assessment')
    try:
        source_files = self._discover_source_files()
        if not source_files:
            return self._create_empty_report('No Python source files found')
        self.logger.info(f'Analyzing {len(source_files)} source files')
        all_issues = []
        total_lines = 0
        complexity_scores = []
        maintainability_scores = []
        documentation_scores = []
        style_scores = []
        security_scores = []
        performance_scores = []
        for source_file in source_files:
            try:
                file_analysis = self._analyze_file(source_file)
                all_issues.extend(file_analysis['issues'])
                total_lines += file_analysis['lines_of_code']
                complexity_scores.append(file_analysis['complexity_score'])
                maintainability_scores.append(file_analysis['maintainability_score'])
                documentation_scores.append(file_analysis['documentation_score'])
                style_scores.append(file_analysis['style_score'])
                security_scores.append(file_analysis['security_score'])
                performance_scores.append(file_analysis['performance_score'])
            except Exception as e:
                self.logger.warning(f'Failed to analyze {source_file}: {e}')
                all_issues.append(CodeQualityIssue(file_path=str(source_file), line_number=1, issue_type=CodeQualityMetric.MAINTAINABILITY, severity='major', message=f'Analysis failed: {e}', suggestion='Fix syntax errors or file encoding issues'))
        complexity_score = self._calculate_average_score(complexity_scores)
        maintainability_score = self._calculate_average_score(maintainability_scores)
        documentation_score = self._calculate_average_score(documentation_scores)
        style_score = self._calculate_average_score(style_scores)
        security_score = self._calculate_average_score(security_scores)
        performance_score = self._calculate_average_score(performance_scores)
        overall_score = complexity_score * 0.25 + maintainability_score * 0.2 + documentation_score * 0.2 + style_score * 0.15 + security_score * 0.1 + performance_score * 0.1
        critical_issues = [i for i in all_issues if i.severity == 'critical']
        major_issues = [i for i in all_issues if i.severity == 'major']
        minor_issues = [i for i in all_issues if i.severity == 'minor']
        recommendations = self._generate_recommendations(all_issues, {'complexity': complexity_score, 'maintainability': maintainability_score, 'documentation': documentation_score, 'style': style_score, 'security': security_score, 'performance': performance_score})
        report = CodeQualityReport(overall_score=overall_score, complexity_score=complexity_score, maintainability_score=maintainability_score, documentation_score=documentation_score, style_score=style_score, security_score=security_score, performance_score=performance_score, total_issues=len(all_issues), critical_issues=len(critical_issues), major_issues=len(major_issues), minor_issues=len(minor_issues), issues=all_issues, recommendations=recommendations, files_analyzed=len(source_files), lines_of_code=total_lines)
        self.logger.info(f'Code quality assessment complete. Overall score: {overall_score:.1f}')
        return report
    except Exception as e:
        self.logger.error(f'Code quality assessment failed: {e}')
        return self._create_empty_report(f'Assessment failed: {e}')

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

