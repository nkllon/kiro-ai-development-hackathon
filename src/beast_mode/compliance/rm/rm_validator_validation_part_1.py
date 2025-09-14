
def validate_rm_interface_implementation(self, module_path: str) -> RMInterfaceResult:
    """
        Validate that a module properly implements the RM interface.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            RMInterfaceResult with validation details
        """
    issues = []
    missing_methods = []
    invalid_methods = []
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        tree = ast.parse(source_code)
        rm_classes = self._find_rm_classes(tree, source_code)
        if not rm_classes:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description='No ReflectiveModule classes found in module', affected_files=[module_path], remediation_steps=['Create a class that inherits from ReflectiveModule', 'Implement all required RM interface methods'], blocking_merge=True))
            return RMInterfaceResult(module_path=module_path, implements_rm_interface=False, missing_methods=list(self.REQUIRED_RM_METHODS.keys()), invalid_methods=[], interface_compliance_score=0.0, issues=issues)
        for class_node in rm_classes:
            class_missing, class_invalid = self._validate_class_methods(class_node, module_path)
            missing_methods.extend(class_missing)
            invalid_methods.extend(class_invalid)
        for method_name in missing_methods:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.CRITICAL, description=f'Missing required RM method: {method_name}', affected_files=[module_path], remediation_steps=[f'Implement the {method_name} method', f"Method should: {self.REQUIRED_RM_METHODS.get(method_name, 'Follow RM interface specification')}"], blocking_merge=True))
        for method_name in invalid_methods:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Invalid RM method implementation: {method_name}', affected_files=[module_path], remediation_steps=[f'Fix the {method_name} method implementation', f'Ensure method signature and behavior match RM specification'], blocking_merge=False))
        total_required = len(self.REQUIRED_RM_METHODS)
        implemented_required = total_required - len(missing_methods)
        interface_compliance_score = implemented_required / total_required if total_required > 0 else 0.0
        implements_rm_interface = len(missing_methods) == 0 and len(rm_classes) > 0
        return RMInterfaceResult(module_path=module_path, implements_rm_interface=implements_rm_interface, missing_methods=missing_methods, invalid_methods=invalid_methods, interface_compliance_score=interface_compliance_score, issues=issues)
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Failed to validate RM interface: {str(e)}', affected_files=[module_path], remediation_steps=['Fix syntax errors in the module', 'Ensure module is valid Python code'], blocking_merge=True))
        return RMInterfaceResult(module_path=module_path, implements_rm_interface=False, missing_methods=list(self.REQUIRED_RM_METHODS.keys()), invalid_methods=[], interface_compliance_score=0.0, issues=issues)
