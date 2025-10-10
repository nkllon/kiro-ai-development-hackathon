# ADR Review Requirements for Design Documents

## Mandatory ADR Review Process

All design documents MUST include a review of existing Architectural Decision Records (ADRs) to ensure conformance with established standards and constraints.

## ADR Review Checklist

### 1. Existing ADR Inventory
Before creating any design, review all existing ADRs in `/ADRS/` directory:

**Current ADRs (as of 2025-01-27):**
- ADR-001: No Public DevPost API – Web Integration Only
- ADR-002: Playwright over CDP with Accessibility Fallback  
- ADR-003: Idempotent Submit and Evidence Hashing
- ADR-004: DAG Orchestration with Celery + Redis
- ADR-005: ReflectiveModule Pattern for Universal Observability
- ADR-006: Existing DAG Registry Over External Graph Libraries
- ADR-007: Integration-First Design Strategy
- ADR-008: Failure Isolation Over Cascade Prevention
- ADR-009: Resource-Aware Dynamic Concurrency Over Fixed Thread Pools
- ADR-010: CMS-Based Configuration Management

### 2. Conformance Assessment

For each relevant ADR, assess:

#### **Infrastructure Decisions**
- Does the design align with existing Redis infrastructure decisions (ADR-004)?
- Does it follow ReflectiveModule patterns for observability (ADR-005)?
- Does it integrate with existing CMS for configuration (ADR-010)?

#### **Integration Patterns**
- Does it follow integration-first design strategy (ADR-007)?
- Does it leverage existing DAG Registry infrastructure (ADR-006)?
- Does it maintain consistency with Beast Mode framework patterns?

#### **Operational Patterns**
- Does it implement failure isolation strategies (ADR-008)?
- Does it use resource-aware dynamic approaches (ADR-009)?
- Does it provide idempotent operations where applicable (ADR-003)?

#### **Technology Choices**
- Does it avoid creating new public APIs where existing patterns exist (ADR-001)?
- Does it use established automation patterns (ADR-002)?
- Does it follow evidence-based validation approaches (ADR-003)?

### 3. Conflict Resolution

If design conflicts with existing ADRs:

#### **Option 1: Modify Design**
- Adjust design to conform with existing ADR
- Document why conformance is beneficial
- Maintain architectural consistency

#### **Option 2: Update ADR**
- Create new ADR that supersedes existing decision
- Document why change is necessary
- Update related documentation and systems

#### **Option 3: Create Exception**
- Document specific exception with clear rationale
- Define scope and limitations of exception
- Plan for future alignment if possible

### 4. New ADR Creation

Create new ADRs for:
- **Novel architectural decisions** not covered by existing ADRs
- **Technology choices** that establish new patterns
- **Integration strategies** that affect multiple components
- **Operational patterns** that impact system behavior

### 5. Documentation Requirements

#### **In Design Documents**
Include section: "ADR Conformance Review"
- List relevant ADRs reviewed
- Document conformance assessment
- Explain any conflicts and resolutions
- Reference new ADRs created

#### **In Implementation Plans**
- Ensure tasks align with ADR decisions
- Include ADR validation checkpoints
- Plan for ADR updates if needed

## ADR Review Template

```markdown
## ADR Conformance Review

### Relevant ADRs Reviewed
- ADR-XXX: [Title] - [Conformance Status: ✅ Compliant / ⚠️ Partial / ❌ Conflict]
- ADR-YYY: [Title] - [Conformance Status]

### Conformance Assessment
- **Infrastructure**: [Assessment of infrastructure alignment]
- **Integration**: [Assessment of integration pattern alignment]  
- **Operations**: [Assessment of operational pattern alignment]
- **Technology**: [Assessment of technology choice alignment]

### Conflicts and Resolutions
- **Conflict**: [Description of any conflicts found]
- **Resolution**: [How conflicts were resolved]
- **New ADRs**: [Any new ADRs created]

### Architectural Consistency
[Overall assessment of how design maintains architectural consistency]
```

## Enforcement

- **Design Reviews**: All design documents must include ADR conformance section
- **Implementation Reviews**: Code reviews should verify ADR compliance
- **Architecture Reviews**: Periodic reviews to ensure ADR alignment across systems

## Benefits

- **Consistency**: Maintains architectural consistency across components
- **Knowledge Transfer**: Ensures design decisions are informed by previous experience
- **Risk Reduction**: Prevents architectural drift and conflicting patterns
- **Quality Assurance**: Systematic approach to design validation

---

*This steering rule ensures all designs build upon established architectural foundations rather than creating conflicting patterns.*