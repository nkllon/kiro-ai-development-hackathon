#!/usr/bin/env python3
"""
Pattern Discovery Workflow
==========================

System for identifying, validating, and approving new atomic patterns.
Provides structured process for evolving the pattern knowledge base.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.spec_framework.knowledge.atomic_pattern_registry import (
    AtomicPattern, PatternCategory, PatternStatus, AtomicPatternRegistry
)


class DiscoveryStage(Enum):
    """Stages in the pattern discovery workflow."""
    OBSERVATION = "observation"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"
    REVIEW = "review"
    APPROVAL = "approval"
    INTEGRATION = "integration"


@dataclass
class PatternDiscovery:
    """Represents a pattern in the discovery process."""
    discovery_id: str
    stage: DiscoveryStage
    observer: str
    observation_date: str
    pattern_candidate: AtomicPattern
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    review_comments: List[Dict[str, Any]] = field(default_factory=list)
    approval_status: Optional[str] = None
    approver: Optional[str] = None
    approval_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternDiscoveryWorkflow(ReflectiveModule):
    """Manages the pattern discovery and approval workflow."""
    
    def __init__(self, workflow_path: Optional[str] = None):
        super().__init__()
        self.workflow_path = Path(workflow_path or ".kiro/knowledge/pattern_discoveries.json")
        self.registry = AtomicPatternRegistry()
        self.discoveries: Dict[str, PatternDiscovery] = {}
        self._load_discoveries()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'workflow_stages': [stage.value for stage in DiscoveryStage],
            'discovery_management': ['observe', 'document', 'validate', 'review', 'approve'],
            'validation_types': ['functional', 'performance', 'reliability', 'integration'],
            'approval_workflow': True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        stage_counts = {}
        for stage in DiscoveryStage:
            stage_counts[stage.value] = len([d for d in self.discoveries.values() if d.stage == stage])
        
        return {
            'status': 'healthy',
            'total_discoveries': len(self.discoveries),
            'stage_distribution': stage_counts,
            'workflow_path': str(self.workflow_path)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'PatternDiscoveryWorkflow',
            'version': '1.0.0',
            'description': 'Manages pattern discovery and approval workflow',
            'dependencies': ['ReflectiveModule', 'AtomicPatternRegistry'],
            'workflow_control': 'atomic-pattern-discovery'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_discovery_tracking'],
            'recommendation': 'Check workflow file permissions and format'
        }
    
    def observe_pattern(self, observer: str, pattern_name: str, description: str,
                       command_sequence: List[str], category: PatternCategory,
                       context: str = "") -> str:
        """Record observation of a potential new pattern."""
        discovery_id = f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.discoveries)}"
        
        # Create candidate pattern
        pattern_candidate = AtomicPattern(
            pattern_id=f"candidate_{pattern_name.lower().replace(' ', '_')}",
            name=pattern_name,
            description=description,
            category=category,
            status=PatternStatus.DISCOVERED,
            command_sequence=command_sequence,
            expected_outputs=[],  # To be filled during documentation
            success_criteria=[],  # To be filled during documentation
            tags=set()
        )
        
        # Create discovery record
        discovery = PatternDiscovery(
            discovery_id=discovery_id,
            stage=DiscoveryStage.OBSERVATION,
            observer=observer,
            observation_date=datetime.now().isoformat(),
            pattern_candidate=pattern_candidate,
            metadata={'context': context}
        )
        
        self.discoveries[discovery_id] = discovery
        self._save_discoveries()
        
        print(f"📝 Pattern observation recorded: {pattern_name}")
        print(f"   Discovery ID: {discovery_id}")
        print(f"   Next step: Document the pattern with complete details")
        
        return discovery_id
    
    def document_pattern(self, discovery_id: str, expected_outputs: List[str],
                        success_criteria: List[str], failure_modes: List[str] = None,
                        remediation_steps: List[str] = None, dependencies: List[str] = None,
                        examples: List[str] = None, tags: Set[str] = None) -> bool:
        """Complete pattern documentation."""
        discovery = self.discoveries.get(discovery_id)
        if not discovery or discovery.stage != DiscoveryStage.OBSERVATION:
            print(f"❌ Invalid discovery ID or wrong stage: {discovery_id}")
            return False
        
        # Update pattern candidate with complete documentation
        pattern = discovery.pattern_candidate
        pattern.expected_outputs = expected_outputs
        pattern.success_criteria = success_criteria
        pattern.failure_modes = failure_modes or []
        pattern.remediation_steps = remediation_steps or []
        pattern.dependencies = dependencies or []
        pattern.examples = examples or []
        pattern.tags = tags or set()
        
        # Advance to documentation stage
        discovery.stage = DiscoveryStage.DOCUMENTATION
        self._save_discoveries()
        
        print(f"📋 Pattern documentation completed: {pattern.name}")
        print(f"   Next step: Validate the pattern")
        
        return True
    
    def validate_pattern(self, discovery_id: str, validator: str, 
                        validation_type: str, success: bool, 
                        execution_time: float = None, notes: str = "") -> bool:
        """Record pattern validation results."""
        discovery = self.discoveries.get(discovery_id)
        if not discovery:
            print(f"❌ Invalid discovery ID: {discovery_id}")
            return False
        
        validation_result = {
            'validator': validator,
            'validation_type': validation_type,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'execution_time': execution_time,
            'notes': notes
        }
        
        discovery.validation_results.append(validation_result)
        
        # Advance stage if this is the first validation
        if discovery.stage == DiscoveryStage.DOCUMENTATION:
            discovery.stage = DiscoveryStage.VALIDATION
        
        self._save_discoveries()
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} Pattern validation: {discovery.pattern_candidate.name}")
        print(f"   Type: {validation_type}")
        print(f"   Validator: {validator}")
        if execution_time:
            print(f"   Execution time: {execution_time:.2f}s")
        
        return True
    
    def review_pattern(self, discovery_id: str, reviewer: str, 
                      recommendation: str, comments: str = "") -> bool:
        """Add review comments to a pattern."""
        discovery = self.discoveries.get(discovery_id)
        if not discovery:
            print(f"❌ Invalid discovery ID: {discovery_id}")
            return False
        
        review_comment = {
            'reviewer': reviewer,
            'timestamp': datetime.now().isoformat(),
            'recommendation': recommendation,  # 'approve', 'reject', 'needs_work'
            'comments': comments
        }
        
        discovery.review_comments.append(review_comment)
        
        # Advance stage if this is the first review
        if discovery.stage == DiscoveryStage.VALIDATION:
            discovery.stage = DiscoveryStage.REVIEW
        
        self._save_discoveries()
        
        print(f"📝 Review added for pattern: {discovery.pattern_candidate.name}")
        print(f"   Reviewer: {reviewer}")
        print(f"   Recommendation: {recommendation}")
        
        return True
    
    def approve_pattern(self, discovery_id: str, approver: str, 
                       decision: str, notes: str = "") -> bool:
        """Make final approval decision on a pattern."""
        discovery = self.discoveries.get(discovery_id)
        if not discovery or discovery.stage != DiscoveryStage.REVIEW:
            print(f"❌ Invalid discovery ID or wrong stage: {discovery_id}")
            return False
        
        discovery.approval_status = decision  # 'approved', 'rejected'
        discovery.approver = approver
        discovery.approval_date = datetime.now().isoformat()
        discovery.stage = DiscoveryStage.APPROVAL
        
        if notes:
            discovery.metadata['approval_notes'] = notes
        
        self._save_discoveries()
        
        if decision == 'approved':
            print(f"✅ Pattern APPROVED: {discovery.pattern_candidate.name}")
            print(f"   Approver: {approver}")
            print(f"   Next step: Integrate into pattern registry")
        else:
            print(f"❌ Pattern REJECTED: {discovery.pattern_candidate.name}")
            print(f"   Approver: {approver}")
            if notes:
                print(f"   Reason: {notes}")
        
        return True
    
    def integrate_pattern(self, discovery_id: str) -> bool:
        """Integrate approved pattern into the main registry."""
        discovery = self.discoveries.get(discovery_id)
        if not discovery or discovery.stage != DiscoveryStage.APPROVAL:
            print(f"❌ Invalid discovery ID or wrong stage: {discovery_id}")
            return False
        
        if discovery.approval_status != 'approved':
            print(f"❌ Pattern not approved for integration: {discovery.pattern_candidate.name}")
            return False
        
        # Calculate success rate from validations
        successful_validations = [v for v in discovery.validation_results if v['success']]
        total_validations = len(discovery.validation_results)
        success_rate = len(successful_validations) / total_validations if total_validations > 0 else 0.0
        
        # Update pattern status based on validation results
        pattern = discovery.pattern_candidate
        pattern.validation_count = total_validations
        pattern.success_rate = success_rate
        
        if success_rate >= 0.9 and total_validations >= 3:
            pattern.status = PatternStatus.PRODUCTION_READY
        elif success_rate >= 0.7:
            pattern.status = PatternStatus.VALIDATED
        
        # Add validation metadata
        pattern.metadata['discovery_process'] = {
            'discovery_id': discovery_id,
            'observer': discovery.observer,
            'observation_date': discovery.observation_date,
            'validation_results': discovery.validation_results,
            'review_comments': discovery.review_comments,
            'approver': discovery.approver,
            'approval_date': discovery.approval_date
        }
        
        # Register in main registry
        if self.registry.register_pattern(pattern):
            discovery.stage = DiscoveryStage.INTEGRATION
            self._save_discoveries()
            
            print(f"🎉 Pattern integrated successfully: {pattern.name}")
            print(f"   Pattern ID: {pattern.pattern_id}")
            print(f"   Status: {pattern.status.value}")
            print(f"   Success Rate: {pattern.success_rate:.1%}")
            
            return True
        else:
            print(f"❌ Failed to integrate pattern: {pattern.name}")
            return False
    
    def get_discoveries_by_stage(self, stage: DiscoveryStage) -> List[PatternDiscovery]:
        """Get all discoveries at a specific stage."""
        return [d for d in self.discoveries.values() if d.stage == stage]
    
    def get_discovery_status(self, discovery_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a discovery."""
        discovery = self.discoveries.get(discovery_id)
        if not discovery:
            return None
        
        return {
            'discovery_id': discovery_id,
            'pattern_name': discovery.pattern_candidate.name,
            'stage': discovery.stage.value,
            'observer': discovery.observer,
            'observation_date': discovery.observation_date,
            'validation_count': len(discovery.validation_results),
            'successful_validations': len([v for v in discovery.validation_results if v['success']]),
            'review_count': len(discovery.review_comments),
            'approval_status': discovery.approval_status,
            'approver': discovery.approver
        }
    
    def export_discovery_report(self, output_path: Optional[str] = None) -> str:
        """Export discovery workflow report."""
        report_lines = [
            "# Pattern Discovery Workflow Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            f"Total Discoveries: {len(self.discoveries)}",
            ""
        ]
        
        # Summary by stage
        stage_counts = {}
        for stage in DiscoveryStage:
            count = len([d for d in self.discoveries.values() if d.stage == stage])
            stage_counts[stage.value] = count
            if count > 0:
                report_lines.append(f"- {stage.value.title()}: {count}")
        
        report_lines.extend(["", "## Discoveries by Stage", ""])
        
        # Details by stage
        for stage in DiscoveryStage:
            discoveries = self.get_discoveries_by_stage(stage)
            if not discoveries:
                continue
            
            report_lines.extend([
                f"### {stage.value.title()} ({len(discoveries)})",
                ""
            ])
            
            for discovery in discoveries:
                pattern = discovery.pattern_candidate
                report_lines.extend([
                    f"#### {pattern.name}",
                    f"- **Discovery ID**: `{discovery.discovery_id}`",
                    f"- **Observer**: {discovery.observer}",
                    f"- **Category**: {pattern.category.value}",
                    f"- **Observation Date**: {discovery.observation_date}",
                ])
                
                if discovery.validation_results:
                    successful = len([v for v in discovery.validation_results if v['success']])
                    total = len(discovery.validation_results)
                    report_lines.append(f"- **Validations**: {successful}/{total} successful")
                
                if discovery.approval_status:
                    report_lines.append(f"- **Approval**: {discovery.approval_status}")
                
                report_lines.extend(["", "---", ""])
        
        content = "\n".join(report_lines)
        
        if output_path:
            Path(output_path).write_text(content)
        
        return content
    
    def _load_discoveries(self) -> None:
        """Load discoveries from workflow file."""
        if not self.workflow_path.exists():
            self.workflow_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_discoveries()
            return
        
        try:
            data = json.loads(self.workflow_path.read_text())
            for discovery_data in data.get('discoveries', {}).values():
                # Convert string enums back to enum objects
                discovery_data['stage'] = DiscoveryStage(discovery_data['stage'])
                
                pattern_data = discovery_data['pattern_candidate']
                pattern_data['category'] = PatternCategory(pattern_data['category'])
                pattern_data['status'] = PatternStatus(pattern_data['status'])
                pattern_data['tags'] = set(pattern_data.get('tags', []))
                
                discovery_data['pattern_candidate'] = AtomicPattern(**pattern_data)
                discovery = PatternDiscovery(**discovery_data)
                self.discoveries[discovery.discovery_id] = discovery
                
        except Exception as e:
            print(f"⚠️ Error loading discoveries: {e}")
            self.discoveries = {}
    
    def _save_discoveries(self) -> None:
        """Save discoveries to workflow file."""
        try:
            data = {
                'discoveries': {},
                'last_updated': datetime.now().isoformat(),
                'total_discoveries': len(self.discoveries)
            }
            
            for discovery_id, discovery in self.discoveries.items():
                discovery_dict = asdict(discovery)
                
                # Convert enums to strings for JSON serialization
                discovery_dict['stage'] = discovery_dict['stage'].value
                
                pattern_dict = discovery_dict['pattern_candidate']
                pattern_dict['category'] = pattern_dict['category'].value
                pattern_dict['status'] = pattern_dict['status'].value
                pattern_dict['tags'] = list(pattern_dict['tags'])
                
                data['discoveries'][discovery_id] = discovery_dict
            
            self.workflow_path.write_text(json.dumps(data, indent=2, default=str))
            
        except Exception as e:
            print(f"❌ Error saving discoveries: {e}")


# CLI interface for pattern discovery
def main():
    """Command-line interface for pattern discovery workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pattern Discovery Workflow CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Observe command
    observe_parser = subparsers.add_parser('observe', help='Record pattern observation')
    observe_parser.add_argument('--observer', required=True, help='Observer name')
    observe_parser.add_argument('--name', required=True, help='Pattern name')
    observe_parser.add_argument('--description', required=True, help='Pattern description')
    observe_parser.add_argument('--category', required=True, choices=[c.value for c in PatternCategory])
    observe_parser.add_argument('--commands', required=True, nargs='+', help='Command sequence')
    observe_parser.add_argument('--context', help='Additional context')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show workflow status')
    status_parser.add_argument('--discovery-id', help='Specific discovery ID')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate workflow report')
    report_parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    workflow = PatternDiscoveryWorkflow()
    
    if args.command == 'observe':
        discovery_id = workflow.observe_pattern(
            observer=args.observer,
            pattern_name=args.name,
            description=args.description,
            command_sequence=args.commands,
            category=PatternCategory(args.category),
            context=args.context or ""
        )
        print(f"\n📋 Next steps:")
        print(f"1. Document pattern: python {__file__} document {discovery_id}")
        print(f"2. Validate pattern: python {__file__} validate {discovery_id}")
        
    elif args.command == 'status':
        if args.discovery_id:
            status = workflow.get_discovery_status(args.discovery_id)
            if status:
                print(json.dumps(status, indent=2))
            else:
                print(f"❌ Discovery not found: {args.discovery_id}")
        else:
            health = workflow.get_health_status()
            print(json.dumps(health, indent=2))
            
    elif args.command == 'report':
        report = workflow.export_discovery_report(args.output)
        if args.output:
            print(f"📄 Report saved to: {args.output}")
        else:
            print(report)


if __name__ == "__main__":
    main()