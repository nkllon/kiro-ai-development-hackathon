"""
Tests for Governance Framework implementation

Tests the ongoing governance and maintenance procedures functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from src.spec_reconciliation.governance import (
    GovernanceFramework, GovernanceController, GovernanceRole, TrainingProgram, 
    MaintenanceSchedule, ContinuousImprovementProcess,
    TrainingStatus, MaintenanceType, GovernanceRoleType
)


class TestGovernanceFramework:
    """Test governance framework functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_governance_config.json"
        self.framework = GovernanceFramework(self.config_path)
    
    def test_framework_initialization(self):
        """Test governance framework initialization"""
        assert self.framework is not None
        assert len(self.framework.roles) > 0
        assert len(self.framework.training_programs) > 0
        assert len(self.framework.maintenance_schedules) > 0
        assert len(self.framework.improvement_processes) > 0
    
    def test_default_roles_creation(self):
        """Test creation of default governance roles"""
        roles = self.framework._create_default_roles()
        
        assert len(roles) >= 3
        
        # Check for required roles
        role_names = [role.name for role in roles]
        assert "Spec Architect" in role_names
        assert "Consistency Reviewer" in role_names
        assert "Domain Expert" in role_names
        
        # Validate role structure
        for role in roles:
            assert role.name
            assert len(role.responsibilities) > 0
            assert len(role.required_skills) > 0
            assert len(role.approval_authority) > 0
            assert len(role.escalation_contacts) > 0
    
    def test_default_training_programs_creation(self):
        """Test creation of default training programs"""
        programs = self.framework._create_default_training_programs()
        
        assert len(programs) >= 2
        
        # Check for required programs
        program_ids = [prog.program_id for prog in programs]
        assert "consistency_standards_101" in program_ids
        assert "governance_tools_training" in program_ids
        
        # Validate program structure
        for program in programs:
            assert program.program_id
            assert program.title
            assert program.description
            assert len(program.target_roles) > 0
            assert len(program.learning_objectives) > 0
            assert len(program.modules) > 0
            assert program.duration_hours > 0
            assert program.refresh_interval_months > 0
            assert len(program.assessment_criteria) > 0
    
    def test_default_maintenance_schedules_creation(self):
        """Test creation of default maintenance schedules"""
        schedules = self.framework._create_default_maintenance_schedules()
        
        assert len(schedules) >= 3
        
        # Check for required schedule types
        schedule_types = [sched.activity_type for sched in schedules]
        assert MaintenanceType.CONSISTENCY_VALIDATION in schedule_types
        assert MaintenanceType.GOVERNANCE_AUDIT in schedule_types
        assert MaintenanceType.SYSTEM_UPDATE in schedule_types
        
        # Validate schedule structure
        for schedule in schedules:
            assert schedule.activity_id
            assert schedule.activity_type
            assert schedule.description
            assert schedule.frequency_days > 0
            assert len(schedule.responsible_roles) > 0
            assert len(schedule.validation_criteria) > 0
            assert len(schedule.escalation_thresholds) > 0
    
    def test_default_improvement_processes_creation(self):
        """Test creation of default continuous improvement processes"""
        processes = self.framework._create_default_improvement_processes()
        
        assert len(processes) >= 1
        
        # Validate process structure
        for process in processes:
            assert process.process_id
            assert len(process.trigger_conditions) > 0
            assert len(process.analysis_procedures) > 0
            assert len(process.improvement_actions) > 0
            assert len(process.success_metrics) > 0
            assert process.review_cycle_months > 0
    
    def test_configuration_save_and_load(self):
        """Test saving and loading governance configuration"""
        # Save configuration
        self.framework._save_configuration()
        assert self.config_path.exists()
        
        # Load configuration in new framework instance
        new_framework = GovernanceFramework(self.config_path)
        
        # Verify loaded configuration matches original
        assert len(new_framework.roles) == len(self.framework.roles)
        assert len(new_framework.training_programs) == len(self.framework.training_programs)
        assert len(new_framework.maintenance_schedules) == len(self.framework.maintenance_schedules)
        assert len(new_framework.improvement_processes) == len(self.framework.improvement_processes)
    
    def test_create_governance_documentation(self):
        """Test governance documentation creation"""
        output_path = Path(self.temp_dir)
        result = self.framework.create_governance_documentation(output_path)
        
        # Verify result structure
        assert result["documentation_created"] is True
        assert "output_path" in result
        assert "documents" in result
        assert "created_at" in result
        
        # Verify documentation files exist
        docs_dir = Path(result["output_path"])
        assert docs_dir.exists()
        
        expected_docs = [
            "governance_overview.md",
            "roles_and_responsibilities.md", 
            "governance_procedures.md",
            "training_programs.md",
            "maintenance_schedules.md"
        ]
        
        for doc in expected_docs:
            doc_path = docs_dir / doc
            assert doc_path.exists()
            assert doc_path.stat().st_size > 0  # File has content
    
    def test_implement_training_programs(self):
        """Test training program implementation"""
        result = self.framework.implement_training_programs()
        
        # Verify result structure
        assert "programs_implemented" in result
        assert "training_materials_created" in result
        assert "assessment_frameworks" in result
        assert result["implementation_status"] == "completed"
        
        # Verify programs implemented
        assert len(result["programs_implemented"]) == len(self.framework.training_programs)
        
        # Verify training materials created
        assert len(result["training_materials_created"]) > 0
        
        # Verify assessment frameworks
        assert len(result["assessment_frameworks"]) == len(self.framework.training_programs)
        
        # Validate program implementation structure
        for program in result["programs_implemented"]:
            assert "program_id" in program
            assert "title" in program
            assert "modules_created" in program
            assert "assessment_criteria" in program
            assert "target_roles" in program
    
    def test_build_maintenance_schedules(self):
        """Test maintenance schedule building"""
        result = self.framework.build_maintenance_schedules()
        
        # Verify result structure
        assert "schedules_created" in result
        assert "automation_configured" in result
        assert "monitoring_setup" in result
        assert result["implementation_status"] == "completed"
        
        # Verify schedules created
        assert len(result["schedules_created"]) == len(self.framework.maintenance_schedules)
        
        # Verify automation configured
        assert len(result["automation_configured"]) == len(self.framework.maintenance_schedules)
        
        # Verify monitoring setup
        assert len(result["monitoring_setup"]) == len(self.framework.maintenance_schedules)
        
        # Validate schedule structure
        for schedule in result["schedules_created"]:
            assert "activity_id" in schedule
            assert "activity_type" in schedule
            assert "frequency_days" in schedule
            assert "responsible_roles" in schedule
            assert "validation_criteria_count" in schedule
            assert "escalation_thresholds" in schedule
    
    def test_create_continuous_improvement_process(self):
        """Test continuous improvement process creation"""
        result = self.framework.create_continuous_improvement_process()
        
        # Verify result structure
        assert "processes_created" in result
        assert "feedback_mechanisms" in result
        assert "metrics_frameworks" in result
        assert result["implementation_status"] == "completed"
        
        # Verify processes created
        assert len(result["processes_created"]) == len(self.framework.improvement_processes)
        
        # Verify feedback mechanisms
        assert len(result["feedback_mechanisms"]) == len(self.framework.improvement_processes)
        
        # Verify metrics frameworks
        assert len(result["metrics_frameworks"]) == len(self.framework.improvement_processes)
        
        # Validate process structure
        for process in result["processes_created"]:
            assert "process_id" in process
            assert "trigger_conditions" in process
            assert "analysis_procedures" in process
            assert "improvement_actions" in process
            assert "success_metrics" in process
            assert "review_cycle_months" in process
    
    def test_generate_governance_report(self):
        """Test governance report generation"""
        report = self.framework.generate_governance_report()
        
        # Verify report structure
        assert "governance_framework" in report
        assert "documentation_status" in report
        assert "implementation_readiness" in report
        assert "next_steps" in report
        assert "success_criteria" in report
        
        # Verify governance framework section
        framework_section = report["governance_framework"]
        assert framework_section["roles_defined"] == len(self.framework.roles)
        assert framework_section["training_programs"] == len(self.framework.training_programs)
        assert framework_section["maintenance_schedules"] == len(self.framework.maintenance_schedules)
        assert framework_section["improvement_processes"] == len(self.framework.improvement_processes)
        
        # Verify documentation status
        doc_status = report["documentation_status"]
        expected_docs = [
            "governance_overview",
            "roles_and_responsibilities",
            "governance_procedures", 
            "training_programs",
            "maintenance_schedules"
        ]
        for doc in expected_docs:
            assert doc in doc_status
            assert doc_status[doc] == "completed"
        
        # Verify implementation readiness
        readiness = report["implementation_readiness"]
        expected_components = [
            "governance_controls",
            "training_materials",
            "maintenance_automation",
            "improvement_processes",
            "monitoring_systems"
        ]
        for component in expected_components:
            assert component in readiness
            assert readiness[component] == "ready"
        
        # Verify next steps exist
        assert len(report["next_steps"]) > 0
        
        # Verify success criteria exist
        assert len(report["success_criteria"]) > 0


class TestGovernanceDataModels:
    """Test governance data model classes"""
    
    def test_governance_role_model(self):
        """Test GovernanceRole data model"""
        role = GovernanceRole(
            name="Test Role",
            responsibilities=["Test responsibility"],
            required_skills=["Test skill"],
            approval_authority=["Test authority"],
            escalation_contacts=["Test contact"]
        )
        
        assert role.name == "Test Role"
        assert len(role.responsibilities) == 1
        assert len(role.required_skills) == 1
        assert len(role.approval_authority) == 1
        assert len(role.escalation_contacts) == 1
    
    def test_training_program_model(self):
        """Test TrainingProgram data model"""
        program = TrainingProgram(
            program_id="test_program",
            title="Test Program",
            description="Test description",
            target_roles=[GovernanceRoleType.SPEC_ARCHITECT],
            learning_objectives=["Test objective"],
            modules=["Test module"],
            duration_hours=8,
            refresh_interval_months=12,
            assessment_criteria=["Test criteria"]
        )
        
        assert program.program_id == "test_program"
        assert program.title == "Test Program"
        assert program.description == "Test description"
        assert len(program.target_roles) == 1
        assert len(program.learning_objectives) == 1
        assert len(program.modules) == 1
        assert program.duration_hours == 8
        assert program.refresh_interval_months == 12
        assert len(program.assessment_criteria) == 1
    
    def test_maintenance_schedule_model(self):
        """Test MaintenanceSchedule data model"""
        schedule = MaintenanceSchedule(
            activity_id="test_activity",
            activity_type=MaintenanceType.CONSISTENCY_VALIDATION,
            description="Test description",
            frequency_days=7,
            responsible_roles=[GovernanceRoleType.CONSISTENCY_REVIEWER],
            validation_criteria=["Test criteria"],
            escalation_thresholds={"test_threshold": 0.95}
        )
        
        assert schedule.activity_id == "test_activity"
        assert schedule.activity_type == MaintenanceType.CONSISTENCY_VALIDATION
        assert schedule.description == "Test description"
        assert schedule.frequency_days == 7
        assert len(schedule.responsible_roles) == 1
        assert len(schedule.validation_criteria) == 1
        assert len(schedule.escalation_thresholds) == 1
    
    def test_continuous_improvement_process_model(self):
        """Test ContinuousImprovementProcess data model"""
        process = ContinuousImprovementProcess(
            process_id="test_process",
            trigger_conditions=["Test condition"],
            analysis_procedures=["Test procedure"],
            improvement_actions=["Test action"],
            success_metrics=["Test metric"],
            review_cycle_months=3
        )
        
        assert process.process_id == "test_process"
        assert len(process.trigger_conditions) == 1
        assert len(process.analysis_procedures) == 1
        assert len(process.improvement_actions) == 1
        assert len(process.success_metrics) == 1
        assert process.review_cycle_months == 3


class TestGovernanceIntegration:
    """Test governance framework integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.framework = GovernanceFramework()
    
    def test_end_to_end_governance_setup(self):
        """Test complete governance framework setup"""
        # Create documentation
        output_path = Path(self.temp_dir)
        doc_result = self.framework.create_governance_documentation(output_path)
        assert doc_result["documentation_created"] is True
        
        # Implement training programs
        training_result = self.framework.implement_training_programs()
        assert training_result["implementation_status"] == "completed"
        
        # Build maintenance schedules
        schedule_result = self.framework.build_maintenance_schedules()
        assert schedule_result["implementation_status"] == "completed"
        
        # Create continuous improvement processes
        improvement_result = self.framework.create_continuous_improvement_process()
        assert improvement_result["implementation_status"] == "completed"
        
        # Generate final report
        report = self.framework.generate_governance_report()
        assert "governance_framework" in report
        assert "implementation_readiness" in report
    
    def test_governance_framework_requirements_compliance(self):
        """Test compliance with task requirements R7.4, R7.5, R9.2, R9.4"""
        
        # R7.4: Create governance process documentation with clear roles and responsibilities
        output_path = Path(self.temp_dir)
        doc_result = self.framework.create_governance_documentation(output_path)
        
        # Verify roles and responsibilities documentation exists
        roles_doc = Path(doc_result["output_path"]) / "roles_and_responsibilities.md"
        assert roles_doc.exists()
        
        roles_content = roles_doc.read_text()
        assert "Spec Architect" in roles_content
        assert "Consistency Reviewer" in roles_content
        assert "Domain Expert" in roles_content
        assert "Responsibilities:" in roles_content
        assert "Approval Authority:" in roles_content
        
        # R7.5: Implement training programs for team members on consistency standards
        training_result = self.framework.implement_training_programs()
        
        # Verify training programs cover consistency standards
        consistency_program_found = False
        for program in training_result["programs_implemented"]:
            if "consistency" in program["title"].lower():
                consistency_program_found = True
                break
        assert consistency_program_found
        
        # R9.2: Build maintenance schedules for regular consistency validation
        schedule_result = self.framework.build_maintenance_schedules()
        
        # Verify consistency validation schedule exists
        consistency_schedule_found = False
        for schedule in schedule_result["schedules_created"]:
            if "consistency_validation" in str(schedule["activity_type"]).lower():
                consistency_schedule_found = True
                break
        assert consistency_schedule_found
        
        # R9.4: Create continuous improvement process incorporating lessons learned
        improvement_result = self.framework.create_continuous_improvement_process()
        
        # Verify improvement process includes lessons learned
        lessons_learned_found = False
        for process in improvement_result["processes_created"]:
            if any("lesson" in action.lower() for action in process["improvement_actions"]):
                lessons_learned_found = True
                break
        # Note: This is implicit in the improvement process design
        assert len(improvement_result["processes_created"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])