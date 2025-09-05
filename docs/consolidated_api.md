# Consolidated API Documentation

Generated: 2025-09-05 11:28:02

This document describes the consolidated APIs that replace the fragmented specifications.


## BeastModeSystemInterface

**Consolidates**: beast-mode-framework, integrated-beast-mode-system
**Module**: `src.spec_reconciliation.beast_mode_system`

### Usage

```python
from src.spec_reconciliation.beast_mode_system import BeastModeSystemInterface

# Initialize the interface
interface = BeastModeSystemInterface()

# Use consolidated methods
result = interface.get_module_status()
```

### Migration Notes

This interface replaces the following original interfaces:
- Beast_Mode_FrameworkInterface
- Integrated_Beast_Mode_SystemInterface

### Backward Compatibility

Backward compatibility is available through:
```python
from src.compatibility.unified_beast_mode_system_compatibility import *
```


## TestingRCAFrameworkInterface

**Consolidates**: test-rca-integration, test-rca-issues-resolution
**Module**: `src.spec_reconciliation.testing_rca_framework`

### Usage

```python
from src.spec_reconciliation.testing_rca_framework import TestingRCAFrameworkInterface

# Initialize the interface
interface = TestingRCAFrameworkInterface()

# Use consolidated methods
result = interface.get_module_status()
```

### Migration Notes

This interface replaces the following original interfaces:
- Test_Rca_IntegrationInterface
- Test_Rca_Issues_ResolutionInterface

### Backward Compatibility

Backward compatibility is available through:
```python
from src.compatibility.unified_testing_rca_framework_compatibility import *
```


## RDIRMAnalysisSystemInterface

**Consolidates**: rdi-rm-compliance-check, rm-rdi-analysis-system
**Module**: `src.spec_reconciliation.rdi_rm_analysis_system`

### Usage

```python
from src.spec_reconciliation.rdi_rm_analysis_system import RDIRMAnalysisSystemInterface

# Initialize the interface
interface = RDIRMAnalysisSystemInterface()

# Use consolidated methods
result = interface.get_module_status()
```

### Migration Notes

This interface replaces the following original interfaces:
- Rdi_Rm_Compliance_CheckInterface
- Rm_Rdi_Analysis_SystemInterface

### Backward Compatibility

Backward compatibility is available through:
```python
from src.compatibility.unified_rdi_rm_analysis_system_compatibility import *
```

