# RDI Documentation Structure

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
