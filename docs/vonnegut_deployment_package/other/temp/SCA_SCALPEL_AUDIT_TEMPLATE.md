## SCA (Scalpel Cut Audit) – Six-Phase Template

Purpose: A generalizable, evidence-first audit framework that mirrors the SCALPEL six-phase tactic and adapts validation criteria per use case.

Use this as a fill-in template. Duplicate this file per audit and complete each section.

### 0) Metadata
- Audit name:
- Use case / target domain:
- Time window (UTC):
- Operator:
- Environment snapshot:
  - OS:
  - Chrome (or browser):
  - Playwright / tooling versions:
  - CDP/debug port and profile path (if applicable):

### Global Compliance Policy
- Every artifact MUST map to at least one requirement (RDI traceability). If not, it is noncompliant and must be either (a) mapped via an explicit requirement chain or (b) removed/quarantined.
- Every artifact SHOULD have a documented root cause (RCA) explaining why it exists now, with evidence.

### 1) Phase: SCALPEL RDI (Scope & Target Definition)
- Objective: Define the precise surgical scope of this audit.
- Inputs: Systems/pages/scripts/components in-scope.
- Actions: What segments were examined/touched.
- Evidence: Links, file paths, screenshots.
- Validation criteria (customize per use case):
  - [example] Scope enumerates all steps that can change state.
  - [example] All critical URLs/selectors identified.
  - RDI: Each in-scope artifact has Requirement → Design → Implementation linkage.
- Pass/Fail:

### 2) Phase: SCALPEL Health (Environment & Readiness)
- Objective: Capture environment health and readiness to reproduce.
- Inputs: Versions, sessions, toggles.
- Actions: Snapshot versions; confirm session continuity and required toggles.
- Evidence: Version outputs, screenshots of settings, notes.
- Validation criteria (customize per use case):
  - Tooling versions recorded.
  - Session continuity plan documented (no unintended logouts).
- Pass/Fail:

### 3) Phase: SCALPEL Registry (Runbook & Artifact Index)
- Objective: Create a minimal runbook and artifact registry to replay the work.
- Inputs: Commands, selectors, URLs.
- Actions: Record exact steps and locators; index artifacts.
- Evidence: Command snippets, selector table, artifact list.
- Validation criteria (customize per use case):
  - Runbook replays steps deterministically.
  - Selector inventory present and unambiguous.
  - RDI completeness: Registry entries link to requirement IDs.
- Pass/Fail:

### 4) Phase: SCALPEL Size Fix (Signal, Not Noise)
- Objective: Ensure artifacts are necessary and sufficient; trim noise.
- Inputs: All captured screenshots/dumps/logs.
- Actions: Keep only essential artifacts; compute hashes.
- Evidence: SHA256 for each artifact; rationale for inclusion.
- Validation criteria (customize per use case):
  - Each artifact justifies a verification purpose.
  - All artifacts have hashes.
  - Noncompliant orphan artifacts (no requirement mapping) are removed or quarantined with RCA note.
- Pass/Fail:

### 5) Phase: SCALPEL Test Creation (Verification Procedures)
- Objective: Define and execute verification tests.
- Inputs: Public URLs, status views, content markers.
- Actions: Perform checks (e.g., Incognito visibility, status badges, content markers).
- Evidence: Before/after screenshots, text dumps, logs.
- Validation criteria (customize per use case):
  - [example] Public URL loads unauthenticated.
  - [example] Status badge shows expected state.
  - RCA executed for unexpected artifacts or deviations; decisions logged.
- Pass/Fail:

### 6) Phase: SCALPEL Final Validation (Conclusion & Replay)
- Objective: Conclude with a reproducible command and a timed event log.
- Inputs: Final command(s), timeline.
- Actions: Present one-shot replay; record UTC timestamps of key events.
- Evidence: Command block; timeline; final screenshots.
- Validation criteria (customize per use case):
  - Replay command completes without modification.
  - Timeline entries correlate with artifact timestamps.
- Pass/Fail:

### Selector Inventory (Minimal)
| Purpose | Selector/Pattern | Notes |
| --- | --- | --- |
|  |  |  |

### Artifact Register
| Artifact | Purpose | SHA256 |
| --- | --- | --- |
|  |  |  |

### RDI Traceability Matrix
| Requirement ID | Requirement Text | Design Element(s) | Implementation (files/paths) | Artifact(s) |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### RCA Ledger
| Artifact | Root Cause (why it exists) | Evidence/Notes | Decision (keep/map/remove) |
| --- | --- | --- | --- |
|  |  |  |  |

### Timeline (UTC)
| Time | Event |
| --- | --- |
|  |  |

### Risks & Mitigations (Tailor per use case)
- Risk:
- Mitigation:

### Replay Block (One-shot)
```bash
# Insert a minimal, deterministic command (e.g., Playwright CDP snippet)
```

### Outcome
- Result:
- Next actions:


