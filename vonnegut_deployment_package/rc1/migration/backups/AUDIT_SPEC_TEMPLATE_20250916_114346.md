## Unified Audit Specification Template (SCA + RMDDD)

Purpose: Define audit requirements upfront, combining Scalpel Cut Audit (SCA) rigor with RMDDD lifecycle compliance. Fill this before work begins; update during execution; finalize at close.

### 0) Metadata
- Audit Name:
- Use Case / Domain:
- Time Window (UTC):
- Operator(s):
- Environment Snapshot: OS / Browser / Tooling versions / CDP port & profile

### 1) SCA Phases (Evidence-First, Replayable)
1. RDI Scope (Requirements → Design → Implementation)
   - Scope statement:
   - In-scope artifacts (files/URLs/selectors):
   - Requirement IDs linked:
2. Health (Environment Readiness)
   - Versions:
   - Session continuity plan:
   - Toggles/features required:
3. Registry (Runbook & Artifact Index)
   - Exact commands/steps:
   - Selectors/locators:
   - Artifact list:
4. Size Fix (Signal vs Noise)
   - Keep rationale per artifact:
   - SHA256 per artifact:
5. Test Creation (Verification Procedures)
   - Checks (public visibility, status badges, content markers, etc.):
   - Expected vs Actual:
6. Final Validation (Replay & Timeline)
   - One-shot replay block:
   - UTC timeline of key events:

### 2) RMDDD Compliance (Lifecycle & Architecture)
- Requirements Model
  - Requirement set + IDs:
  - Ubiquitous Language terms:
  - Invariants/constraints:
- Design Model
  - Bounded contexts / responsibilities:
  - Interfaces/contracts:
  - ADRs (decision records):
- Implementation
  - Files/modules implementing requirements:
  - Event/flow mapping (if applicable):
- Tests
  - Spec-to-test linkage:
  - Coverage of invariants:
- Governance Gates
  - Definition of Done:
  - Security/Privacy checks:
  - Observability/logging requirements:

### 3) 22-Dimension Validation Matrix (customize)
| Dimension | Criteria | Evidence | Pass/Fail |
| --- | --- | --- | --- |
| Traceability (RDI) | Every artifact maps to requirement chain |  |  |
| RCA | Every artifact has root cause justification |  |  |
| Replayability | One-shot command succeeds as-is |  |  |
| Idempotency | Re-running causes no harm |  |  |
| Session Integrity | No unintended login loss |  |  |
| Selector Stability | Locators resilient across reloads |  |  |
| SPA State Validity | Content verified, not just URL |  |  |
| Timestamping | UTC events recorded |  |  |
| Integrity Hashing | SHA256 for artifacts |  |  |
| Public Visibility | Incognito access verified |  |  |
| Governance | DoD/security/privacy met |  |  |
| Observability | Logs/screens/artifacts adequate |  |  |
| Version Pinning | Tooling versions recorded |  |  |
| Rollback | Clear recovery path |  |  |
| Risk Register | Risks & mitigations logged |  |  |
| Performance | Reasonable runtime/latency |  |  |
| Accessibility | Basic a11y passes (as needed) |  |  |
| Internationalization | Not applicable/applicable |  |  |
| Data Hygiene | No secrets in artifacts |  |  |
| Compliance | Legal/ToS adhered |  |  |
| Ownership | Responsible parties identified |  |  |
| Change Control | Git history clean & tagged |  |  |

### 4) RDI Traceability Matrix
| Requirement ID | Requirement Text | Design Element(s) | Implementation (files/paths) | Artifact(s) |
| --- | --- | --- | --- | --- |

### 5) RCA Ledger
| Artifact | Root Cause (why it exists) | Evidence/Notes | Decision (keep/map/remove) |
| --- | --- | --- | --- |

### 6) Evidence Register (with SHA256)
| Artifact | Purpose | SHA256 |
| --- | --- | --- |

### 7) Replay Block (One-Shot)
```bash
# Insert minimal deterministic command(s) to replay the key action
```

### 8) Outcome & Next Actions
- Outcome:
- Residual risks:
- Next steps:


