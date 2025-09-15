def execute(context):
    """
    Systematic security vulnerability scanning

    Args:
        context: Dictionary containing scan configuration

    Returns:
        Dictionary with scan results
    """
    scan_targets = context.get("targets", [])
    vulnerabilities = []

    for target in scan_targets:
        # Simulate security scanning
        if target.get("type") == "instance":
            # Check for common vulnerabilities
            issues = []

            if not target.get("firewall_enabled", False):
                issues.append(
                    {
                        "severity": "high",
                        "type": "firewall_disabled",
                        "description": "Instance firewall is disabled",
                    }
                )

            if target.get("ssh_keys_count", 0) > 10:
                issues.append(
                    {
                        "severity": "medium",
                        "type": "excessive_ssh_keys",
                        "description": "Too many SSH keys configured",
                    }
                )

            if issues:
                vulnerabilities.extend(issues)

    return {
        "status": "success",
        "scan_completed": True,
        "vulnerabilities_found": len(vulnerabilities),
        "vulnerabilities": vulnerabilities,
        "recommendations": [
            "Enable firewall on all instances",
            "Regularly audit SSH key access",
            "Implement least privilege access",
        ],
    }


class SecurityScannerSpore:
    """Systematic security scanning methodology"""

    def __init__(self):
        self.name = "security_scanner"
        self.version = "1.2.0"
        self.capabilities = ["security_scanning", "vulnerability_assessment"]

    def configure_scan(self, targets):
        """Configure security scan parameters"""
        return {"scan_configured": True, "target_count": len(targets)}

    def generate_security_report(self, results):
        """Generate security assessment report"""
        return {
            "report_type": "security_assessment",
            "format": "json",
            "timestamp": datetime.now().isoformat(),
        }
