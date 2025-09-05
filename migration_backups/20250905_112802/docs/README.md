# RDI Documentation Structure

## Consolidated Architecture

This project has been migrated to use consolidated specifications that eliminate
fragmentation and provide unified interfaces. The following consolidations have been implemented:

### Unified Beast Mode System
- **Consolidates**: beast-mode-framework, integrated-beast-mode-system, openflow-backlog-management
- **Interface**: `BeastModeSystemInterface`
- **Purpose**: Domain-intelligent systematic development with PDCA cycles, tool health management, and backlog optimization

### Unified Testing and RCA Framework  
- **Consolidates**: test-rca-integration, test-rca-issues-resolution, test-infrastructure-repair
- **Interface**: `TestingRCAFrameworkInterface`
- **Purpose**: Comprehensive root cause analysis, automated issue resolution, and integrated testing infrastructure

### Unified RDI/RM Analysis System
- **Consolidates**: rdi-rm-compliance-check, rm-rdi-analysis-system, rdi-rm-validation-system
- **Interface**: `RDIRMAnalysisSystemInterface`
- **Purpose**: Requirements-Design-Implementation analysis, compliance validation, and quality assurance

### Migration Information
- **Migration Date**: 2025-09-05
- **Backward Compatibility**: Available through compatibility layers in `src/compatibility/`
- **Documentation**: Updated to reflect consolidated architecture

For detailed migration information, see the migration report in the project root.


This directory follows the RDI (Requirements->Design->Implementation) documentation structure enforced by the Beast Mode Framework DocumentManagementRM.

## Structure

```
docs/
├── requirements/     # Requirements documents
├── design/          # Design documents  
├── implementation/  # Implementation documents
├── rms/            # RM-specific documentation
│   └── {rm_name}/  # Each RM maintains its docs here
├── api/            # API documentation
└── guides/         # User guides and tutorials
```

## RM Documentation Constraint

**Each Reflective Module (RM) MUST maintain its documentation via DocumentManagementRM**

### Required Documents per RM:
1. **Requirements** - What the RM must accomplish
2. **Design** - How the RM is architected  
3. **Implementation** - How the RM is implemented

### Cross-Reference Requirements:
- All documents must reference related requirements, design, and implementation docs
- Cross-references must be validated and maintained
- Circular references are not allowed

## Compliance

All documentation is automatically validated for:
- RDI structure compliance
- Cross-reference integrity
- Version consistency
- RM ownership
- Approval workflow

---
*Maintained by DocumentManagementRM - Beast Mode Framework*
