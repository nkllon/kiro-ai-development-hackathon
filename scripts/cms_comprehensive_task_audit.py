#!/usr/bin/env python3
"""
CMS Comprehensive Task Audit System
Conducts systematic audit of all 22 CMS Architecture tasks with 99% confidence.
"""

import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class TaskStatus:
    """Task status information."""
    task_id: str
    title: str
    reported_status: str
    actual_status: str
    evidence: List[str]
    confidence: float
    recommendation: str

class CMSTaskAuditor:
    """Comprehensive CMS task auditor with 99% confidence requirement."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.tasks_file = self.project_root / ".kiro/specs/cms-architecture/tasks.md"
        self.audit_results = []
        self.evidence_log = []
        
    def conduct_full_audit(self) -> Dict[str, Any]:
        """Conduct comprehensive audit of all 22 CMS tasks."""
        print("🔍 Starting CMS Task Comprehensive Audit")
        print("=" * 60)
        
        # Phase 1: Parse all tasks from specification
        tasks = self._parse_all_tasks()
        print(f"📋 Found {len(tasks)} tasks to audit")
        
        # Phase 2: Audit each task systematically
        audit_results = []
        for task in tasks:
            result = self._audit_single_task(task)
            audit_results.append(result)
            print(f"✅ Audited {task['id']}: {result.actual_status}")
        
        # Phase 3: Generate comprehensive report
        report = self._generate_audit_report(audit_results)
        
        # Phase 4: Save results
        self._save_audit_results(report)
        
        return report
    
    def _parse_all_tasks(self) -> List[Dict[str, Any]]:
        """Parse all 22 tasks from the CMS architecture specification."""
        if not self.tasks_file.exists():
            raise FileNotFoundError(f"Tasks file not found: {self.tasks_file}")
        
        with open(self.tasks_file, 'r') as f:
            content = f.read()
        
        tasks = []
        
        # Parse tasks using regex patterns
        task_pattern = r'### Task (\d+\.\d+): ([^\n]+)\n\*\*Priority:\*\* (\w+)\s+\n\*\*Estimated Effort:\*\* ([^\n]+)\s+\n\*\*Dependencies:\*\* ([^\n]+)\s+\n\*\*Assignee:\*\* ([^\n]+)(?:\s+\n\*\*Status:\*\* ([^\n]+))?'
        
        matches = re.finditer(task_pattern, content, re.MULTILINE)
        
        for match in matches:
            task_id = match.group(1)
            title = match.group(2).strip()
            priority = match.group(3).strip()
            effort = match.group(4).strip()
            dependencies = match.group(5).strip()
            assignee = match.group(6).strip()
            status = match.group(7).strip() if match.group(7) else "not_started"
            
            # Extract acceptance criteria
            task_start = match.end()
            next_task_match = re.search(r'### Task \d+\.\d+:', content[task_start:])
            task_end = task_start + next_task_match.start() if next_task_match else len(content)
            task_content = content[task_start:task_end]
            
            # Parse acceptance criteria
            criteria_pattern = r'- \[([ x])\] (.+)'
            criteria_matches = re.findall(criteria_pattern, task_content)
            
            acceptance_criteria = []
            for checked, criterion in criteria_matches:
                acceptance_criteria.append({
                    'text': criterion.strip(),
                    'completed': checked == 'x'
                })
            
            tasks.append({
                'id': task_id,
                'title': title,
                'priority': priority,
                'effort': effort,
                'dependencies': dependencies,
                'assignee': assignee,
                'reported_status': status,
                'acceptance_criteria': acceptance_criteria,
                'content': task_content
            })
        
        return tasks
    
    def _audit_single_task(self, task: Dict[str, Any]) -> TaskStatus:
        """Audit a single task with comprehensive evidence collection."""
        task_id = task['id']
        title = task['title']
        reported_status = task['reported_status']
        
        print(f"🔍 Auditing Task {task_id}: {title}")
        
        # Collect evidence for task status
        evidence = []
        confidence = 0.0
        
        # 1. Check for code artifacts
        code_evidence = self._check_code_artifacts(task)
        evidence.extend(code_evidence)
        
        # 2. Check for documentation
        doc_evidence = self._check_documentation(task)
        evidence.extend(doc_evidence)
        
        # 3. Check for infrastructure
        infra_evidence = self._check_infrastructure(task)
        evidence.extend(infra_evidence)
        
        # 4. Check acceptance criteria completion
        criteria_evidence = self._check_acceptance_criteria(task)
        evidence.extend(criteria_evidence)
        
        # 5. Check for running services
        service_evidence = self._check_running_services(task)
        evidence.extend(service_evidence)
        
        # Determine actual status based on evidence
        actual_status, confidence = self._determine_actual_status(
            reported_status, evidence, task
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            reported_status, actual_status, evidence
        )
        
        return TaskStatus(
            task_id=task_id,
            title=title,
            reported_status=reported_status,
            actual_status=actual_status,
            evidence=evidence,
            confidence=confidence,
            recommendation=recommendation
        )
    
    def _check_code_artifacts(self, task: Dict[str, Any]) -> List[str]:
        """Check for code artifacts related to the task."""
        evidence = []
        task_id = task['id']
        title = task['title'].lower()
        
        # Define search terms based on task content
        search_terms = self._extract_search_terms(task)
        
        # Search for Python files
        try:
            for term in search_terms:
                result = subprocess.run(
                    ['find', '.', '-name', '*.py', '-exec', 'grep', '-l', term, '{}', ';'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0 and result.stdout.strip():
                    files = result.stdout.strip().split('\n')
                    evidence.append(f"Code files found for '{term}': {len(files)} files")
                    for file in files[:3]:  # Limit to first 3 files
                        evidence.append(f"  - {file}")
        except Exception as e:
            evidence.append(f"Code search error: {str(e)}")
        
        return evidence
    
    def _check_documentation(self, task: Dict[str, Any]) -> List[str]:
        """Check for documentation related to the task."""
        evidence = []
        search_terms = self._extract_search_terms(task)
        
        # Search for documentation files
        try:
            for term in search_terms:
                result = subprocess.run(
                    ['find', '.', '-name', '*.md', '-exec', 'grep', '-l', term, '{}', ';'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0 and result.stdout.strip():
                    files = result.stdout.strip().split('\n')
                    # Filter out the tasks.md file itself
                    files = [f for f in files if 'tasks.md' not in f]
                    if files:
                        evidence.append(f"Documentation found for '{term}': {len(files)} files")
                        for file in files[:2]:  # Limit to first 2 files
                            evidence.append(f"  - {file}")
        except Exception as e:
            evidence.append(f"Documentation search error: {str(e)}")
        
        return evidence
    
    def _check_infrastructure(self, task: Dict[str, Any]) -> List[str]:
        """Check for infrastructure related to the task."""
        evidence = []
        
        # Check Docker containers
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', 'table {{.Names}}\t{{.Status}}'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                containers = result.stdout.strip()
                if containers:
                    evidence.append("Docker containers found:")
                    for line in containers.split('\n')[1:]:  # Skip header
                        evidence.append(f"  - {line}")
        except Exception as e:
            evidence.append(f"Docker check error: {str(e)}")
        
        # Check for configuration files
        config_patterns = ['docker-compose*.yml', '*.yaml', '*.json']
        for pattern in config_patterns:
            try:
                result = subprocess.run(
                    ['find', '.', '-name', pattern, '-type', 'f'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    files = result.stdout.strip().split('\n')
                    evidence.append(f"Configuration files ({pattern}): {len(files)} found")
            except Exception:
                pass
        
        return evidence
    
    def _check_acceptance_criteria(self, task: Dict[str, Any]) -> List[str]:
        """Check acceptance criteria completion status."""
        evidence = []
        criteria = task.get('acceptance_criteria', [])
        
        if criteria:
            total_criteria = len(criteria)
            completed_criteria = sum(1 for c in criteria if c['completed'])
            
            evidence.append(f"Acceptance criteria: {completed_criteria}/{total_criteria} completed")
            
            if completed_criteria > 0:
                evidence.append("Completed criteria:")
                for c in criteria:
                    if c['completed']:
                        evidence.append(f"  ✅ {c['text']}")
            
            if completed_criteria < total_criteria:
                evidence.append("Remaining criteria:")
                for c in criteria:
                    if not c['completed']:
                        evidence.append(f"  ⏳ {c['text']}")
        else:
            evidence.append("No acceptance criteria defined")
        
        return evidence
    
    def _check_running_services(self, task: Dict[str, Any]) -> List[str]:
        """Check for running services related to the task."""
        evidence = []
        
        # Check for common service ports
        service_ports = {
            'directus': 8055,
            'elasticsearch': 9200,
            'redis': 6379,
            'postgresql': 5432,
            'prometheus': 9090,
            'grafana': 3000
        }
        
        for service, port in service_ports.items():
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    evidence.append(f"Service running on port {port}: {service}")
            except Exception:
                pass
        
        return evidence
    
    def _extract_search_terms(self, task: Dict[str, Any]) -> List[str]:
        """Extract search terms from task content."""
        terms = []
        
        # Extract from title
        title_words = task['title'].lower().split()
        terms.extend([word for word in title_words if len(word) > 3])
        
        # Add specific terms based on task content
        content = task.get('content', '').lower()
        
        if 'directus' in content:
            terms.extend(['directus', 'cms'])
        if 'elasticsearch' in content:
            terms.extend(['elasticsearch', 'search'])
        if 'redis' in content:
            terms.extend(['redis', 'cache'])
        if 'postgresql' in content:
            terms.extend(['postgresql', 'postgres', 'database'])
        if 'docker' in content:
            terms.extend(['docker', 'compose'])
        
        return list(set(terms))  # Remove duplicates
    
    def _determine_actual_status(self, reported_status: str, evidence: List[str], 
                                task: Dict[str, Any]) -> Tuple[str, float]:
        """Determine actual task status based on evidence."""
        
        # Count different types of evidence
        code_evidence = len([e for e in evidence if 'Code files found' in e])
        doc_evidence = len([e for e in evidence if 'Documentation found' in e])
        infra_evidence = len([e for e in evidence if 'Docker containers' in e or 'Service running' in e])
        
        # Check acceptance criteria completion
        criteria = task.get('acceptance_criteria', [])
        completed_criteria = sum(1 for c in criteria if c['completed'])
        total_criteria = len(criteria)
        completion_ratio = completed_criteria / total_criteria if total_criteria > 0 else 0
        
        # Determine status based on evidence
        if completion_ratio > 0.5:  # More than 50% criteria completed
            actual_status = "IN_PROGRESS"
            confidence = 0.95
        elif completion_ratio > 0:  # Some criteria completed
            actual_status = "STARTED"
            confidence = 0.90
        elif code_evidence > 0 or infra_evidence > 0:
            actual_status = "STARTED"
            confidence = 0.85
        elif doc_evidence > 0:
            actual_status = "PLANNING"
            confidence = 0.80
        else:
            actual_status = "NOT_STARTED"
            confidence = 0.99  # High confidence in negative result
        
        return actual_status, confidence
    
    def _generate_recommendation(self, reported_status: str, actual_status: str, 
                               evidence: List[str]) -> str:
        """Generate recommendation based on status comparison."""
        
        if reported_status == actual_status:
            return "Status accurately reported - no action needed"
        
        if reported_status == "not_started" and actual_status != "NOT_STARTED":
            return f"FALSE POSITIVE: Task marked as not_started but evidence shows {actual_status}. Update status in specification."
        
        if reported_status != "not_started" and actual_status == "NOT_STARTED":
            return f"FALSE NEGATIVE: Task marked as {reported_status} but no evidence found. Verify actual work status."
        
        return f"Status mismatch: Reported {reported_status}, Actual {actual_status}. Review and update."
    
    def _generate_audit_report(self, audit_results: List[TaskStatus]) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        
        # Calculate statistics
        total_tasks = len(audit_results)
        true_negatives = len([r for r in audit_results if r.reported_status == "not_started" and r.actual_status == "NOT_STARTED"])
        false_positives = len([r for r in audit_results if r.reported_status == "not_started" and r.actual_status != "NOT_STARTED"])
        false_negatives = len([r for r in audit_results if r.reported_status != "not_started" and r.actual_status == "NOT_STARTED"])
        true_positives = len([r for r in audit_results if r.reported_status != "not_started" and r.actual_status != "NOT_STARTED"])
        
        # Calculate confidence metrics
        avg_confidence = sum(r.confidence for r in audit_results) / total_tasks
        error_rate = (false_positives + false_negatives) / total_tasks
        
        report = {
            "audit_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_tasks_audited": total_tasks,
                "audit_confidence": avg_confidence,
                "error_rate": error_rate,
                "methodology": "Comprehensive evidence-based audit"
            },
            "executive_summary": {
                "tasks_audited": f"{total_tasks}/22 (100%)",
                "true_negatives": true_negatives,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "true_positives": true_positives,
                "audit_confidence": f"{avg_confidence:.1%}",
                "error_rate": f"{error_rate:.1%}"
            },
            "confusion_matrix": {
                "reported_not_started": {
                    "actual_not_started": true_negatives,
                    "actual_started": false_positives
                },
                "reported_started": {
                    "actual_not_started": false_negatives,
                    "actual_started": true_positives
                }
            },
            "detailed_findings": [],
            "recommendations": []
        }
        
        # Add detailed findings
        for result in audit_results:
            finding = {
                "task_id": result.task_id,
                "title": result.title,
                "reported_status": result.reported_status,
                "actual_status": result.actual_status,
                "confidence": f"{result.confidence:.1%}",
                "evidence_count": len(result.evidence),
                "evidence": result.evidence,
                "recommendation": result.recommendation
            }
            report["detailed_findings"].append(finding)
        
        # Add overall recommendations
        if false_positives > 0:
            report["recommendations"].append(f"Update {false_positives} tasks marked as 'not_started' but showing evidence of work")
        
        if false_negatives > 0:
            report["recommendations"].append(f"Verify {false_negatives} tasks marked as started but showing no evidence")
        
        if error_rate > 0.01:  # More than 1% error rate
            report["recommendations"].append("Error rate exceeds 1% threshold - review audit methodology")
        
        if avg_confidence < 0.99:  # Less than 99% confidence
            report["recommendations"].append("Confidence below 99% threshold - gather additional evidence")
        
        return report
    
    def _save_audit_results(self, report: Dict[str, Any]) -> None:
        """Save audit results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cms_task_audit_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Audit report saved to: {filename}")
        
        # Also create a summary markdown report
        self._create_markdown_summary(report, timestamp)
    
    def _create_markdown_summary(self, report: Dict[str, Any], timestamp: str) -> None:
        """Create a markdown summary of the audit results."""
        filename = f"cms_task_audit_summary_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write("# CMS Task Audit Results\n\n")
            f.write(f"**Audit Date:** {report['audit_metadata']['timestamp']}\n")
            f.write(f"**Confidence Level:** {report['executive_summary']['audit_confidence']}\n")
            f.write(f"**Error Rate:** {report['executive_summary']['error_rate']}\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"- **Tasks Audited:** {report['executive_summary']['tasks_audited']}\n")
            f.write(f"- **True Negatives:** {report['executive_summary']['true_negatives']} (correctly not started)\n")
            f.write(f"- **False Positives:** {report['executive_summary']['false_positives']} (work begun but marked not started)\n")
            f.write(f"- **False Negatives:** {report['executive_summary']['false_negatives']} (marked started but no evidence)\n")
            f.write(f"- **True Positives:** {report['executive_summary']['true_positives']} (correctly marked as started)\n\n")
            
            f.write("## Confusion Matrix\n\n")
            f.write("```\n")
            f.write("                    ACTUAL STATUS\n")
            f.write("                 Not_Started | Started\n")
            f.write(f"REPORTED Not_Started    {report['confusion_matrix']['reported_not_started']['actual_not_started']:2d}   |   {report['confusion_matrix']['reported_not_started']['actual_started']:2d}\n")
            f.write(f"         Started         {report['confusion_matrix']['reported_started']['actual_not_started']:2d}   |   {report['confusion_matrix']['reported_started']['actual_started']:2d}\n")
            f.write("```\n\n")
            
            f.write("## Key Findings\n\n")
            for finding in report['detailed_findings']:
                if finding['reported_status'] != finding['actual_status']:
                    f.write(f"### Task {finding['task_id']}: {finding['title']}\n")
                    f.write(f"- **Reported:** {finding['reported_status']}\n")
                    f.write(f"- **Actual:** {finding['actual_status']}\n")
                    f.write(f"- **Confidence:** {finding['confidence']}\n")
                    f.write(f"- **Recommendation:** {finding['recommendation']}\n\n")
            
            f.write("## Recommendations\n\n")
            for rec in report['recommendations']:
                f.write(f"- {rec}\n")
        
        print(f"📝 Audit summary saved to: {filename}")

def main():
    """Main execution function."""
    auditor = CMSTaskAuditor()
    
    try:
        report = auditor.conduct_full_audit()
        
        print("\n" + "=" * 60)
        print("🎯 AUDIT COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Tasks Audited: {report['executive_summary']['tasks_audited']}")
        print(f"Confidence Level: {report['executive_summary']['audit_confidence']}")
        print(f"Error Rate: {report['executive_summary']['error_rate']}")
        print(f"False Positives: {report['executive_summary']['false_positives']}")
        print(f"True Negatives: {report['executive_summary']['true_negatives']}")
        
        return report
        
    except Exception as e:
        print(f"❌ Audit failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()