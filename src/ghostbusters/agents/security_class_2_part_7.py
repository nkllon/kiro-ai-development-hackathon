from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def validate_confidence(self, result: AnalysisResult) -> bool:
        """Validate confidence score accuracy"""
        if not 0.0 <= result.confidence <= 1.0:
            return False
        if result.confidence > 0.8:
            return 'security_checks_performed' in result.metadata
        if result.confidence < 0.3:
            return any((f.severity == Severity.CRITICAL for f in result.findings))
        return True

    async def _analyze_directory(self, directory: Path) -> List[Finding]:
        """Analyze directory for security issues"""
        findings = []
        for file_path in directory.rglob('*'):
            if file_path.is_file() and self._should_analyze_file(file_path):
                try:
                    findings.extend(await self._analyze_file(file_path))
                except Exception as e:
                    logger.warning(f'Failed to analyze {file_path}: {str(e)}')
        return findings

    async def _analyze_file(self, file_path: Path) -> List[Finding]:
        """Analyze single file for security vulnerabilities"""
        findings = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            findings.extend(self._check_sql_injection(content, file_path))
            findings.extend(self._check_xss_vulnerabilities(content, file_path))
            findings.extend(self._check_command_injection(content, file_path))
            findings.extend(self._check_hardcoded_secrets(content, file_path))
            findings.extend(self._check_crypto_issues(content, file_path))
            findings.extend(self._check_path_traversal(content, file_path))
            findings.extend(self._check_file_permissions(file_path))
            file_extension = file_path.suffix.lower()
            if file_extension == '.py':
                findings.extend(self._check_python_security(content, file_path))
            elif file_extension in ['.js', '.ts']:
                findings.extend(self._check_javascript_security(content, file_path))
            elif file_extension == '.java':
                findings.extend(self._check_java_security(content, file_path))
        except Exception as e:
            findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.MEDIUM, location=CodeLocation(str(file_path), 1), description=f'Could not analyze file for security issues: {str(e)}', confidence=0.8))
        return findings
