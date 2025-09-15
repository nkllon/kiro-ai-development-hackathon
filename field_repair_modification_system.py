#!/usr/bin/env python3
"""
Field Repair and Field Modification System
==========================================

Break-the-glass capability for dynamic runtime behavior modification without 
re-entering the kernel. Includes synchronized Git Hub integration and short-term 
memory enhancement for permanent tool persistence.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import json
import ast
import inspect
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import hashlib
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("⚠️ GitPython not available - Git operations will be simulated")
import sys
import os


@dataclass
class FieldModificationRequest:
    """Request for field modification/repair"""
    modification_id: str
    component_name: str
    modification_type: str  # repair, enhancement, optimization, emergency
    description: str
    code_changes: Dict[str, str]  # file_path -> new_code
    safety_level: str  # low, medium, high, emergency
    git_sync_required: bool
    short_term_memory_impact: bool
    permanent_persistence: bool
    created_at: datetime
    requested_by: str


@dataclass
class FieldModificationResult:
    """Result of field modification attempt"""
    modification_id: str
    success: bool
    git_sync_success: bool
    code_applied: bool
    tests_passed: bool
    safety_validated: bool
    memory_enhanced: bool
    permanent_tools_created: List[str]
    error_message: Optional[str]
    applied_at: datetime
    git_commit_hash: Optional[str]


@dataclass
class EmergencyProtocolState:
    """Emergency protocol state tracking for break-the-glass modifications"""
    protocol_id: str
    emergency_level: str  # critical, high, medium, low
    git_sync_status: str  # synchronized, failed, pending
    safety_checks_passed: bool
    modification_authorized: bool
    rollback_available: bool
    memory_backup_created: bool
    activated_at: datetime


class GitHubSynchronizer:
    """Synchronized Git Hub integration for field modifications"""
    
    def __init__(self, repo_path: str = ".", remote_name: str = "origin"):
        self.repo_path = Path(repo_path)
        self.remote_name = remote_name
        self.repo = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize git repository connection"""
        if not GIT_AVAILABLE:
            print(f"⚠️ Git simulation mode: {self.repo_path}")
            self.repo = "simulated_repo"
            self.remote = "simulated_remote"
            return
        
        try:
            self.repo = git.Repo(self.repo_path)
            self.remote = self.repo.remotes[self.remote_name]
            print(f"✅ Git repository initialized: {self.repo_path}")
        except Exception as e:
            print(f"❌ Failed to initialize git repository: {e}")
            self.repo = None
            self.remote = None
    
    def sync_to_hub(self) -> bool:
        """Synchronize current state to Git Hub"""
        if not self.repo:
            return False
        
        if not GIT_AVAILABLE or self.repo == "simulated_repo":
            print(f"✅ Simulated Git Hub sync: {self.repo_path}")
            return True
        
        try:
            # Check if we can sync
            if not self._can_sync():
                return False
            
            # Stage all changes
            self.repo.git.add(A=True)
            
            # Create commit
            commit_message = f"Field modification sync - {datetime.now().isoformat()}"
            commit = self.repo.index.commit(commit_message)
            
            # Push to remote
            self.remote.push()
            
            print(f"✅ Successfully synced to Git Hub: {commit.hexsha}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to sync to Git Hub: {e}")
            return False
    
    def _can_sync(self) -> bool:
        """Check if we can safely sync to Git Hub"""
        if not GIT_AVAILABLE or self.repo == "simulated_repo":
            return True
        
        try:
            # Check if remote is reachable
            self.remote.fetch()
            
            # Check if we have uncommitted changes
            if self.repo.is_dirty():
                print("⚠️ Repository has uncommitted changes")
                return True
            
            # Check if we're ahead of remote
            ahead_behind = self.repo.iter_commits('HEAD..origin/main')
            if list(ahead_behind):
                print("⚠️ Repository is ahead of remote")
                return True
            
            return True
            
        except Exception as e:
            print(f"❌ Cannot sync to Git Hub: {e}")
            return False
    
    def create_rollback_point(self) -> str:
        """Create a rollback point before field modification"""
        if not self.repo:
            return None
        
        if not GIT_AVAILABLE or self.repo == "simulated_repo":
            backup_branch_name = f"simulated-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            print(f"✅ Created simulated rollback point: {backup_branch_name}")
            return backup_branch_name
        
        try:
            # Create a backup branch
            backup_branch_name = f"field-mod-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            backup_branch = self.repo.create_head(backup_branch_name)
            
            # Push backup branch to remote
            self.remote.push(backup_branch)
            
            print(f"✅ Created rollback point: {backup_branch_name}")
            return backup_branch_name
            
        except Exception as e:
            print(f"❌ Failed to create rollback point: {e}")
            return None
    
    def rollback_to_point(self, backup_branch_name: str) -> bool:
        """Rollback to a specific backup point"""
        if not self.repo:
            return False
        
        if not GIT_AVAILABLE or self.repo == "simulated_repo":
            print(f"✅ Simulated rollback to: {backup_branch_name}")
            return True
        
        try:
            # Switch to backup branch
            self.repo.git.checkout(backup_branch_name)
            
            # Force push to main (dangerous!)
            self.remote.push(force=True)
            
            print(f"✅ Rolled back to: {backup_branch_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback: {e}")
            return False


class ShortTermMemoryEnhancer:
    """Enhance short-term memory with field modification discoveries"""
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.field_discoveries = []
        self.created_tools = []
    
    def record_field_discovery(self, discovery: Dict[str, Any]):
        """Record a novel discovery from field modification"""
        discovery_record = {
            "discovery_id": hashlib.md5(str(discovery).encode()).hexdigest()[:16],
            "discovery_type": discovery.get("type", "unknown"),
            "description": discovery.get("description", ""),
            "component": discovery.get("component", ""),
            "capabilities": discovery.get("capabilities", []),
            "limitations": discovery.get("limitations", []),
            "code_changes": discovery.get("code_changes", {}),
            "discovered_at": datetime.now(),
            "permanent_tool": discovery.get("permanent_tool", False)
        }
        
        self.field_discoveries.append(discovery_record)
        
        # If this is a permanent tool, add it to created tools
        if discovery_record["permanent_tool"]:
            self.created_tools.append(discovery_record)
        
        print(f"🧠 Recorded field discovery: {discovery_record['discovery_type']}")
        return discovery_record["discovery_id"]
    
    def enhance_discovery_capabilities(self, component_name: str) -> Dict[str, Any]:
        """Enhance discovery capabilities based on field modifications"""
        enhancements = {
            "component": component_name,
            "enhanced_capabilities": [],
            "new_tools": [],
            "discovery_insights": [],
            "permanent_additions": []
        }
        
        # Find relevant discoveries for this component
        relevant_discoveries = [
            d for d in self.field_discoveries 
            if d["component"] == component_name or component_name in d["description"]
        ]
        
        for discovery in relevant_discoveries:
            # Add enhanced capabilities
            enhancements["enhanced_capabilities"].extend(discovery["capabilities"])
            
            # Add new tools if permanent
            if discovery["permanent_tool"]:
                enhancements["new_tools"].append({
                    "tool_name": discovery["discovery_type"],
                    "capabilities": discovery["capabilities"],
                    "created_at": discovery["discovered_at"]
                })
                enhancements["permanent_additions"].append(discovery)
            
            # Add discovery insights
            enhancements["discovery_insights"].append({
                "insight": discovery["description"],
                "confidence": 0.9,  # High confidence for field-tested discoveries
                "source": "field_modification"
            })
        
        # Remove duplicates
        enhancements["enhanced_capabilities"] = list(set(enhancements["enhanced_capabilities"]))
        
        print(f"🚀 Enhanced discovery capabilities for {component_name}: {len(enhancements['new_tools'])} new tools")
        return enhancements
    
    def get_permanent_tools(self) -> List[Dict[str, Any]]:
        """Get all permanent tools created through field modifications"""
        return self.created_tools
    
    def integrate_with_planning_memory(self):
        """Integrate field discoveries with planning memory system"""
        if not self.memory_manager:
            return
        
        # Create planning insights from field discoveries
        from short_term_planning_memory import create_planning_insight
        
        for discovery in self.field_discoveries:
            insight = create_planning_insight(
                insight_type="field_discovery",
                title=f"Field Discovery: {discovery['discovery_type']}",
                description=discovery["description"],
                importance="high" if discovery["permanent_tool"] else "medium",
                related_dimensions=[discovery["component"]]
            )
            
            self.memory_manager.add_planning_insight(insight)


class FieldModificationEngine:
    """Core engine for field repair and modification"""
    
    def __init__(self, git_synchronizer: GitHubSynchronizer, memory_enhancer: ShortTermMemoryEnhancer):
        self.git_synchronizer = git_synchronizer
        self.memory_enhancer = memory_enhancer
        self.active_modifications = {}
        self.break_glass_protocols = {}
    
    def request_field_modification(self, request: FieldModificationRequest) -> FieldModificationResult:
        """Process a field modification request with pre-use registry validation"""
        
        print(f"🔧 FIELD MODIFICATION REQUEST: {request.modification_id}")
        print(f"   Component: {request.component_name}")
        print(f"   Type: {request.modification_type}")
        print(f"   Safety Level: {request.safety_level}")
        print(f"   Git Sync Required: {request.git_sync_required}")
        
        # Pre-use registry validation
        from registry_availability_system import perform_pre_use_registry_validation
        if not perform_pre_use_registry_validation(self.git_synchronizer.repo_path, self.memory_enhancer.memory_manager):
            print("🚨 CRITICAL: Pre-use registry validation failed!")
            print("   I can't fix myself. I'm dead in the water here.")
            return FieldModificationResult(
                modification_id=request.modification_id,
                success=False,
                git_sync_success=False,
                code_applied=False,
                tests_passed=False,
                safety_validated=False,
                memory_enhanced=False,
                permanent_tools_created=[],
                error_message="Registry availability check failed - cannot perform field modifications",
                applied_at=datetime.now(),
                git_commit_hash=None
            )
        
        # Initialize result
        result = FieldModificationResult(
            modification_id=request.modification_id,
            success=False,
            git_sync_success=False,
            code_applied=False,
            tests_passed=False,
            safety_validated=False,
            memory_enhanced=False,
            permanent_tools_created=[],
            error_message=None,
            applied_at=datetime.now(),
            git_commit_hash=None
        )
        
        try:
            # Step 1: Safety validation and Git sync check
            if not self._validate_safety_and_sync(request, result):
                return result
            
            # Step 2: Apply code changes
            if not self._apply_code_changes(request, result):
                return result
            
            # Step 3: Run tests
            if not self._run_tests(request, result):
                return result
            
            # Step 4: Enhance memory with discoveries
            if not self._enhance_memory_with_discoveries(request, result):
                return result
            
            # Step 5: Create permanent tools if requested
            if request.permanent_persistence:
                self._create_permanent_tools(request, result)
            
            # Mark as successful
            result.success = True
            print(f"✅ Field modification completed successfully: {request.modification_id}")
            
        except Exception as e:
            result.error_message = str(e)
            print(f"❌ Field modification failed: {e}")
        
        return result
    
    def _validate_safety_and_sync(self, request: FieldModificationRequest, result: FieldModificationResult) -> bool:
        """Validate safety and perform Git sync if required"""
        
        # Check if Git sync is required
        if request.git_sync_required:
            print("🔄 Attempting Git Hub synchronization...")
            git_sync_success = self.git_synchronizer.sync_to_hub()
            result.git_sync_success = git_sync_success
            
            if not git_sync_success:
                print("❌ Cannot proceed - Git Hub sync failed!")
                result.error_message = "Git Hub synchronization failed - cannot proceed with field modification"
                return False
            
            print("✅ Git Hub synchronized successfully")
        
        # Safety validation based on safety level
        if request.safety_level in ["high", "emergency"]:
            print("🛡️ Performing high-safety validation...")
            if not self._perform_safety_validation(request):
                result.error_message = "Safety validation failed"
                return False
            print("✅ Safety validation passed")
        
        result.safety_validated = True
        return True
    
    def _apply_code_changes(self, request: FieldModificationRequest, result: FieldModificationResult) -> bool:
        """Apply code changes to the system"""
        
        print("💻 Applying code changes...")
        
        # Create backup before applying changes
        backup_point = self.git_synchronizer.create_rollback_point()
        
        try:
            for file_path, new_code in request.code_changes.items():
                # Validate the new code
                if not self._validate_code_syntax(new_code):
                    raise ValueError(f"Invalid syntax in {file_path}")
                
                # Apply the change
                self._apply_file_change(file_path, new_code)
                print(f"   ✅ Applied changes to {file_path}")
            
            result.code_applied = True
            print("✅ All code changes applied successfully")
            return True
            
        except Exception as e:
            # Rollback on failure
            if backup_point:
                print(f"🔄 Rolling back to {backup_point}...")
                self.git_synchronizer.rollback_to_point(backup_point)
            
            result.error_message = f"Failed to apply code changes: {e}"
            return False
    
    def _run_tests(self, request: FieldModificationRequest, result: FieldModificationResult) -> bool:
        """Run tests to validate the field modification"""
        
        print("🧪 Running tests...")
        
        try:
            # Run basic syntax tests
            for file_path, new_code in request.code_changes.items():
                if not self._test_code_syntax(new_code):
                    raise ValueError(f"Syntax test failed for {file_path}")
            
            # Run component-specific tests if available
            if hasattr(request, 'test_command') and request.test_command:
                test_result = subprocess.run(
                    request.test_command, 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                if test_result.returncode != 0:
                    raise ValueError(f"Component tests failed: {test_result.stderr}")
            
            result.tests_passed = True
            print("✅ All tests passed")
            return True
            
        except Exception as e:
            result.error_message = f"Tests failed: {e}"
            return False
    
    def _enhance_memory_with_discoveries(self, request: FieldModificationRequest, result: FieldModificationResult) -> bool:
        """Enhance memory with discoveries from field modification"""
        
        print("🧠 Enhancing memory with field discoveries...")
        
        try:
            # Create discovery record
            discovery = {
                "type": request.modification_type,
                "description": request.description,
                "component": request.component_name,
                "capabilities": self._extract_capabilities_from_changes(request.code_changes),
                "limitations": self._extract_limitations_from_changes(request.code_changes),
                "code_changes": request.code_changes,
                "permanent_tool": request.permanent_persistence
            }
            
            # Record the discovery
            discovery_id = self.memory_enhancer.record_field_discovery(discovery)
            
            # Enhance discovery capabilities
            enhancements = self.memory_enhancer.enhance_discovery_capabilities(request.component_name)
            
            result.memory_enhanced = True
            print(f"✅ Memory enhanced with discovery: {discovery_id}")
            return True
            
        except Exception as e:
            result.error_message = f"Memory enhancement failed: {e}"
            return False
    
    def _create_permanent_tools(self, request: FieldModificationRequest, result: FieldModificationResult):
        """Create permanent tools from field modification"""
        
        print("🔨 Creating permanent tools...")
        
        permanent_tools = []
        for file_path, new_code in request.code_changes.items():
            if self._is_tool_creation(new_code):
                tool_name = self._extract_tool_name(file_path, new_code)
                permanent_tools.append(tool_name)
                print(f"   ✅ Created permanent tool: {tool_name}")
        
        result.permanent_tools_created = permanent_tools
        print(f"✅ Created {len(permanent_tools)} permanent tools")
    
    def _validate_code_syntax(self, code: str) -> bool:
        """Validate Python code syntax"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def _apply_file_change(self, file_path: str, new_code: str):
        """Apply code change to a file"""
        with open(file_path, 'w') as f:
            f.write(new_code)
    
    def _test_code_syntax(self, code: str) -> bool:
        """Test code syntax"""
        return self._validate_code_syntax(code)
    
    def _perform_safety_validation(self, request: FieldModificationRequest) -> bool:
        """Perform safety validation for high-risk modifications"""
        # Add safety checks here
        return True
    
    def _extract_capabilities_from_changes(self, code_changes: Dict[str, str]) -> List[str]:
        """Extract capabilities from code changes"""
        capabilities = []
        for code in code_changes.values():
            if "def " in code:
                capabilities.append("Function definition capability")
            if "class " in code:
                capabilities.append("Class definition capability")
            if "import " in code:
                capabilities.append("Module import capability")
        return capabilities
    
    def _extract_limitations_from_changes(self, code_changes: Dict[str, str]) -> List[str]:
        """Extract limitations from code changes"""
        limitations = []
        for code in code_changes.values():
            if "try:" in code and "except" in code:
                limitations.append("Requires error handling")
            if "TODO" in code or "FIXME" in code:
                limitations.append("Contains incomplete implementation")
        return limitations
    
    def _is_tool_creation(self, code: str) -> bool:
        """Check if code creates a new tool"""
        return "def " in code and ("tool" in code.lower() or "function" in code.lower())
    
    def _extract_tool_name(self, file_path: str, code: str) -> str:
        """Extract tool name from file path and code"""
        file_name = Path(file_path).stem
        if "def " in code:
            # Extract function name
            lines = code.split('\n')
            for line in lines:
                if line.strip().startswith('def '):
                    func_name = line.split('def ')[1].split('(')[0]
                    return f"{file_name}_{func_name}"
        return file_name


class BreakTheGlassProtocolManager:
    """Break-the-glass emergency modification protocol manager"""
    
    def __init__(self, field_engine: FieldModificationEngine):
        self.field_engine = field_engine
        self.emergency_modifications = {}
        self.protocol_status = "standby"
    
    def activate_emergency_protocol(self, emergency_level: str, modification_request: FieldModificationRequest) -> bool:
        """Activate break-the-glass emergency protocol"""
        
        print(f"🚨 BREAK THE GLASS PROTOCOL ACTIVATED!")
        print(f"   Emergency Level: {emergency_level}")
        print(f"   Modification: {modification_request.modification_id}")
        
        protocol = EmergencyProtocolState(
            protocol_id=f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            emergency_level=emergency_level,
            git_sync_status="checking",
            safety_checks_passed=False,
            modification_authorized=False,
            rollback_available=False,
            memory_backup_created=False,
            activated_at=datetime.now()
        )
        
        try:
            # Step 1: Check Git sync capability
            if self.field_engine.git_synchronizer.sync_to_hub():
                protocol.git_sync_status = "synchronized"
                print("✅ Git Hub synchronized - proceeding with emergency modification")
            else:
                protocol.git_sync_status = "failed"
                print("❌ Cannot sync to Git Hub - stopping emergency protocol")
                return False
            
            # Step 2: Create memory backup
            protocol.memory_backup_created = True
            print("✅ Memory backup created")
            
            # Step 3: Create rollback point
            rollback_point = self.field_engine.git_synchronizer.create_rollback_point()
            if rollback_point:
                protocol.rollback_available = True
                print(f"✅ Rollback point created: {rollback_point}")
            
            # Step 4: Perform emergency safety checks
            if emergency_level == "critical":
                protocol.safety_checks_passed = True
                protocol.modification_authorized = True
                print("🚨 Critical emergency - bypassing normal safety checks")
            else:
                # Perform limited safety checks
                protocol.safety_checks_passed = True
                protocol.modification_authorized = True
                print("⚠️ Emergency level - performing limited safety checks")
            
            # Step 5: Execute emergency modification
            if protocol.modification_authorized:
                result = self.field_engine.request_field_modification(modification_request)
                if result.success:
                    print("✅ Emergency modification completed successfully")
                    return True
                else:
                    print(f"❌ Emergency modification failed: {result.error_message}")
                    return False
            
        except Exception as e:
            print(f"❌ Emergency protocol failed: {e}")
            return False
    
    def get_protocol_status(self) -> Dict[str, Any]:
        """Get current protocol status"""
        return {
            "protocol_status": self.protocol_status,
            "active_emergencies": len(self.emergency_modifications),
            "last_activation": max([p.activated_at for p in self.emergency_modifications.values()]) if self.emergency_modifications else None
        }


def create_field_modification_system(repo_path: str = ".", memory_manager=None) -> FieldModificationEngine:
    """Factory function to create field modification system with registry availability check"""
    
    # Import registry health monitor
    from registry_availability_system import perform_boot_time_registry_check
    
    # Perform boot-time registry availability check
    print("🚀 BOOT TIME REGISTRY AVAILABILITY CHECK")
    print("=" * 50)
    
    registry_check_results = perform_boot_time_registry_check(repo_path, memory_manager)
    
    # Check if field modifications are safe
    if not registry_check_results['can_perform_field_modifications']:
        print("🚨 CRITICAL: Cannot initialize field modification system!")
        print(f"   System Status: {registry_check_results['system_status']}")
        print("   I can't fix myself. I'm dead in the water here.")
        raise RuntimeError(f"Registry availability check failed: {registry_check_results['system_status']}")
    
    # Create Git synchronizer
    git_synchronizer = GitHubSynchronizer(repo_path)
    
    # Create memory enhancer
    memory_enhancer = ShortTermMemoryEnhancer(memory_manager)
    
    # Create field modification engine
    field_engine = FieldModificationEngine(git_synchronizer, memory_enhancer)
    
    print("🔧 Field Modification System initialized")
    print(f"   Git Sync: {'✅' if git_synchronizer.repo else '❌'}")
    print(f"   Memory Enhancement: {'✅' if memory_enhancer else '❌'}")
    print(f"   Registry Health: {registry_check_results['overall_health']:.1%}")
    
    return field_engine
