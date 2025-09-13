# Repository Refactoring Implementation

## 🎯 **Overview**

This document provides the implementation details for the Repository Refactoring capability within the RM-DDD framework. This implementation extends the proven module-level refactoring approach to entire repositories, ensuring comprehensive RM-DDD compliance.

## 🏗️ **Implementation Structure**

### **Core Implementation Files**

```
scripts/
├── repository_refactoring_engine.py      # Analysis and planning engine
├── refactoring_executor.py               # Safe execution engine
├── refactoring_validator.py              # Validation engine
└── repository_refactoring_orchestrator.py # Complete orchestration

docs/
├── requirements/rm_ddd/
│   └── repository_refactoring_requirements.md
├── design/rm_ddd/
│   └── repository_refactoring_design.md
└── implementation/rm_ddd/
    └── repository_refactoring_implementation.md

Makefile                                 # Integration targets
REPOSITORY_REFACTORING_GUIDE.md         # User guide
```

## 🔧 **Implementation Details**

### **1. Repository Refactoring Engine**

#### **File**: `scripts/repository_refactoring_engine.py`

**Purpose**: Analyzes repository structure and generates refactoring plans.

**Key Classes**:
```python
class RepositoryRefactoringEngine:
    """Main engine for repository-wide refactoring analysis"""
    
    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.analysis_results: List[FileAnalysis] = []
        self.refactoring_plans: List[RefactoringPlan] = []
        self.domain_patterns = self._load_domain_patterns()
    
    def analyze_repository(self) -> Dict[str, Any]:
        """Analyze entire repository for refactoring opportunities"""
        # Implementation details...
    
    def generate_refactoring_plans(self) -> List[RefactoringPlan]:
        """Generate refactoring plans for large files"""
        # Implementation details...

@dataclass
class FileAnalysis:
    """Analysis result for a single Python file"""
    file_path: str
    line_count: int
    class_count: int
    function_count: int
    import_count: int
    is_large: bool
    classes: List[str]
    functions: List[str]
    imports: List[str]
    dependencies: List[str]
    domain: Optional[str] = None
    refactoring_priority: int = 0
    suggested_modules: List[str] = None
```

**Key Features**:
- **File Discovery**: Recursively scans repository for Python files
- **Size Analysis**: Identifies files exceeding 300-line limit
- **Domain Classification**: Groups files by functionality patterns
- **Complexity Assessment**: Calculates refactoring priority scores
- **Plan Generation**: Creates detailed refactoring strategies

### **2. Refactoring Executor**

#### **File**: `scripts/refactoring_executor.py`

**Purpose**: Safely executes refactoring plans with backup and rollback support.

**Key Classes**:
```python
class RefactoringExecutor:
    """Executes refactoring operations safely"""
    
    def __init__(self, src_dir: str = "src", backup_dir: str = "backups"):
        self.src_dir = Path(src_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.results: List[RefactoringResult] = []
    
    def execute_refactoring_plan(self, plan: RefactoringPlan, dry_run: bool = False) -> RefactoringResult:
        """Execute a single refactoring plan"""
        # Implementation details...
    
    def execute_all_plans(self, plans_file: str, dry_run: bool = False, max_files: Optional[int] = None) -> List[RefactoringResult]:
        """Execute all refactoring plans"""
        # Implementation details...

@dataclass
class RefactoringResult:
    """Result of a refactoring operation"""
    source_file: str
    target_modules: List[str]
    success: bool
    errors: List[str]
    warnings: List[str]
    lines_moved: int
    classes_moved: int
    functions_moved: int
```

**Key Features**:
- **Backup Creation**: Creates safety backups before modifications
- **Safe Execution**: Splits files while preserving functionality
- **Import Updates**: Updates import statements correctly
- **Rollback Support**: Restores from backups on failure
- **Progress Tracking**: Monitors execution progress

### **3. Refactoring Validator**

#### **File**: `scripts/refactoring_validator.py`

**Purpose**: Validates refactored modules for compliance and functionality.

**Key Classes**:
```python
class RefactoringValidator:
    """Validates refactored modules for compliance and functionality"""
    
    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.validation_results: List[ValidationResult] = []
    
    def validate_module(self, module_path: str) -> ValidationResult:
        """Validate a single module"""
        # Implementation details...
    
    def validate_all_modules(self, module_paths: List[str]) -> List[ValidationResult]:
        """Validate all specified modules"""
        # Implementation details...

@dataclass
class ValidationResult:
    """Result of validation for a single module"""
    module_path: str
    syntax_valid: bool
    imports_resolved: bool
    rm_ddd_compliant: bool
    functionality_preserved: bool
    performance_impact: str  # low, medium, high
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]
```

**Key Features**:
- **Syntax Validation**: Checks Python syntax correctness
- **Import Resolution**: Verifies all imports work correctly
- **RM-DDD Compliance**: Validates ReflectiveModule implementation
- **Functionality Testing**: Ensures behavior preservation
- **Performance Assessment**: Measures refactoring impact

### **4. Repository Refactoring Orchestrator**

#### **File**: `scripts/repository_refactoring_orchestrator.py`

**Purpose**: Orchestrates the complete refactoring process from analysis through validation.

**Key Classes**:
```python
class RepositoryRefactoringOrchestrator:
    """Orchestrates the complete repository refactoring process"""
    
    def __init__(self, src_dir: str = "src", max_files: Optional[int] = None):
        self.src_dir = Path(src_dir)
        self.max_files = max_files
        self.scripts_dir = Path("scripts")
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_complete_refactoring(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run the complete refactoring process"""
        # Implementation details...
    
    def _run_analysis_phase(self) -> Dict[str, Any]:
        """Run repository analysis phase"""
        # Implementation details...
    
    def _run_planning_phase(self) -> Dict[str, Any]:
        """Run refactoring planning phase"""
        # Implementation details...
    
    def _run_execution_phase(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run refactoring execution phase"""
        # Implementation details...
    
    def _run_validation_phase(self) -> Dict[str, Any]:
        """Run validation phase"""
        # Implementation details...
    
    def _run_reporting_phase(self) -> Dict[str, Any]:
        """Run final reporting phase"""
        # Implementation details...
```

**Key Features**:
- **Phase Management**: Coordinates all refactoring phases
- **Error Handling**: Manages errors and recovery
- **Progress Reporting**: Provides real-time feedback
- **Report Generation**: Creates comprehensive reports
- **Integration**: Works with Makefile and CLI

## 🔧 **Configuration and Setup**

### **Environment Setup**

#### **Prerequisites**
```bash
# Python 3.11+ required
python --version

# UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### **Directory Structure**
```
project/
├── src/                           # Source code directory
├── scripts/                       # Refactoring scripts
│   ├── repository_refactoring_engine.py
│   ├── refactoring_executor.py
│   ├── refactoring_validator.py
│   └── repository_refactoring_orchestrator.py
├── docs/                          # Documentation
│   ├── requirements/rm_ddd/
│   ├── design/rm_ddd/
│   └── implementation/rm_ddd/
├── reports/                       # Generated reports
├── backups/                       # Safety backups
├── Makefile                       # Integration targets
└── REPOSITORY_REFACTORING_GUIDE.md
```

### **Configuration Files**

#### **Domain Patterns Configuration**
```python
# In repository_refactoring_engine.py
DOMAIN_PATTERNS = {
    "core": ["base", "core", "foundation", "common", "utils"],
    "models": ["model", "data", "entity", "schema", "dto"],
    "services": ["service", "manager", "handler", "processor", "engine"],
    "api": ["api", "client", "endpoint", "controller", "route"],
    "validation": ["validator", "validation", "checker", "verifier"],
    "testing": ["test", "spec", "mock", "fixture", "stub"],
    "integration": ["integration", "adapter", "bridge", "connector"],
    "monitoring": ["monitor", "metrics", "logging", "health", "status"],
    "configuration": ["config", "settings", "options", "preferences"],
    "storage": ["storage", "repository", "dao", "persistence", "database"]
}
```

#### **Refactoring Rules Configuration**
```python
# In refactoring_executor.py
REFACTORING_RULES = {
    "max_file_size": 300,
    "target_file_size": 200,
    "min_module_size": 50,
    "max_classes_per_module": 10,
    "max_functions_per_module": 25,
    "required_interface": "ReflectiveModule",
    "backup_retention_days": 30
}
```

## 🚀 **Usage Examples**

### **Basic Usage**

#### **1. Analyze Repository**
```bash
# Using Makefile
make refactor-analyze

# Using direct script
uv run python scripts/repository_refactoring_engine.py
```

#### **2. Generate Refactoring Plans**
```bash
# Using Makefile
make refactor-plan

# Using direct script (same as analyze)
uv run python scripts/repository_refactoring_engine.py
```

#### **3. Test Refactoring (Dry Run)**
```bash
# Using Makefile
make refactor-dry-run

# Using direct script
uv run python scripts/refactoring_executor.py --dry-run
```

#### **4. Execute Refactoring**
```bash
# Using Makefile (with safety warnings)
make refactor-execute

# Using direct script
uv run python scripts/refactoring_executor.py
```

#### **5. Validate Results**
```bash
# Using Makefile
make refactor-validate

# Using direct script
uv run python scripts/refactoring_validator.py --execution-report refactoring_execution_report.json
```

#### **6. Complete Orchestration**
```bash
# Using Makefile (dry run)
make refactor-orchestrate

# Using Makefile (execute)
make refactor-orchestrate-execute

# Using direct script
uv run python scripts/repository_refactoring_orchestrator.py --dry-run
```

### **Advanced Usage**

#### **Custom Configuration**
```python
# Custom domain patterns
engine = RepositoryRefactoringEngine(src_dir="custom_src")
engine.domain_patterns = {
    "custom_domain": ["custom_pattern", "special_function"]
}

# Custom refactoring rules
executor = RefactoringExecutor()
executor.refactoring_rules["max_file_size"] = 250
```

#### **Selective Refactoring**
```bash
# Limit to specific number of files
uv run python scripts/refactoring_executor.py --max-files 10

# Refactor specific files only
uv run python scripts/refactoring_validator.py --modules src/specific_file.py
```

#### **Custom Validation**
```python
# Validate specific modules
validator = RefactoringValidator()
results = validator.validate_all_modules([
    "src/module1.py",
    "src/module2.py"
])
```

## 📊 **Generated Reports**

### **Analysis Report** (`repository_analysis_report.json`)
```json
{
  "summary": {
    "total_files": 467,
    "large_files": 233,
    "compliance_rate": 50.1,
    "total_lines": 177383,
    "average_file_size": 379
  },
  "domain_breakdown": {
    "core": {"total": 45, "large": 12, "lines": 15000},
    "models": {"total": 23, "large": 15, "lines": 12000}
  },
  "largest_files": [
    {
      "file_path": "src/devpost_integration/models.py",
      "line_count": 6470,
      "class_count": 39,
      "function_count": 539
    }
  ],
  "priority_files": [
    {
      "file_path": "src/spec_reconciliation/consolidation.py",
      "line_count": 1999,
      "refactoring_priority": 5
    }
  ]
}
```

### **Execution Report** (`refactoring_execution_report.json`)
```json
[
  {
    "source_file": "src/devpost_integration/models.py",
    "target_modules": ["core_models.py", "validation_models.py"],
    "success": true,
    "lines_moved": 1200,
    "classes_moved": 15,
    "functions_moved": 45
  }
]
```

### **Validation Report** (`validation_report.json`)
```json
{
  "summary": {
    "total_modules": 16,
    "syntax_valid": 16,
    "imports_resolved": 16,
    "rm_ddd_compliant": 16,
    "functionality_preserved": 16,
    "success_rate": 100.0
  },
  "detailed_results": [
    {
      "module_path": "src/devpost_integration/core_models.py",
      "syntax_valid": true,
      "imports_resolved": true,
      "rm_ddd_compliant": true,
      "functionality_preserved": true,
      "performance_impact": "low"
    }
  ]
}
```

## 🛡️ **Safety and Error Handling**

### **Backup System**
```python
# Automatic backup creation
def _create_backup(self, file_path: str):
    backup_path = self.backup_dir / Path(file_path).name
    shutil.copy2(file_path, backup_path)
    logger.debug(f"Created backup: {backup_path}")

# Rollback on failure
def _rollback_refactoring(self, source_file: str):
    backup_path = self.backup_dir / Path(source_file).name
    if backup_path.exists():
        shutil.copy2(backup_path, source_file)
        logger.info(f"Rolled back {source_file}")
```

### **Error Handling**
```python
# Graceful error handling
try:
    result = self.execute_refactoring_plan(plan, dry_run)
    if not result.success:
        self._rollback_refactoring(plan.source_file)
except Exception as e:
    logger.error(f"Refactoring failed: {e}")
    self._rollback_refactoring(plan.source_file)
```

### **Validation Pipeline**
```python
# Multi-stage validation
def validate_module(self, module_path: str) -> ValidationResult:
    result = ValidationResult(module_path=module_path)
    
    # Stage 1: Syntax validation
    result.syntax_valid = self._validate_syntax(content, result)
    
    # Stage 2: Import resolution
    result.imports_resolved = self._validate_imports(module_path, result)
    
    # Stage 3: RM-DDD compliance
    result.rm_ddd_compliant = self._validate_rm_ddd_compliance(module_path, content, result)
    
    # Stage 4: Functionality preservation
    result.functionality_preserved = self._validate_functionality(module_path, result)
    
    return result
```

## 🔧 **Integration Points**

### **Makefile Integration**
```makefile
# Repository Refactoring Targets
refactor-analyze: ## Analyze repository for refactoring opportunities
	@uv run python scripts/repository_refactoring_engine.py

refactor-execute: ## Execute refactoring (WARNING: modifies files)
	@echo "⚠️  WARNING: This will modify files in your repository!"
	@sleep 5
	@uv run python scripts/refactoring_executor.py

refactor-validate: ## Validate refactored modules
	@uv run python scripts/refactoring_validator.py --execution-report refactoring_execution_report.json
```

### **CLI Integration**
```bash
# Command-line interface
uv run python scripts/repository_refactoring_orchestrator.py --help
uv run python scripts/repository_refactoring_orchestrator.py --dry-run
uv run python scripts/repository_refactoring_orchestrator.py --max-files 10
```

### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Repository Refactoring
  run: |
    make refactor-analyze
    make refactor-dry-run
    if [ $? -eq 0 ]; then
      make refactor-execute
      make refactor-validate
    fi
```

## 📈 **Performance Considerations**

### **Optimization Strategies**
- **Parallel Processing**: Process multiple files simultaneously
- **Caching**: Cache analysis results to avoid recomputation
- **Incremental Analysis**: Only analyze changed files
- **Memory Management**: Optimize memory usage for large repositories

### **Scalability**
- **Large Repositories**: Handles 1000+ files efficiently
- **Memory Usage**: Optimized for large codebases
- **Processing Time**: Reasonable execution times
- **Resource Management**: Efficient resource utilization

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
def test_file_analysis():
    engine = RepositoryRefactoringEngine()
    result = engine._analyze_file("test_file.py")
    assert result.line_count > 0
    assert result.class_count >= 0

def test_refactoring_execution():
    executor = RefactoringExecutor()
    plan = RefactoringPlan(...)
    result = executor.execute_refactoring_plan(plan, dry_run=True)
    assert result.success
```

### **Integration Tests**
```python
def test_complete_refactoring_process():
    orchestrator = RepositoryRefactoringOrchestrator()
    results = orchestrator.run_complete_refactoring(dry_run=True)
    assert results['overall_success']
```

### **End-to-End Tests**
```python
def test_repository_refactoring():
    # Test with actual repository
    engine = RepositoryRefactoringEngine()
    analysis = engine.analyze_repository()
    assert analysis['summary']['total_files'] > 0
```

## 📚 **Related Implementations**

- **RM-DDD Core Implementation**: `src/devpost_integration/reflective_module.py`
- **Health Monitoring Implementation**: `src/devpost_integration/health_monitoring.py`
- **Module Registry Implementation**: `src/devpost_integration/module_registry.py`
- **CLI Implementation**: `src/devpost_integration/cli.py`

---

**This implementation provides a complete, production-ready system for repository-wide refactoring that ensures RM-DDD compliance while maintaining safety, functionality, and quality.**



