## DevPost Integration – Requirements Inventory (Canonicalized)

Sources:
- `.kiro/specs/devpost-hackathon-integration/requirements.md`
- `.kiro/specs/devpost-hackathon-integration/requirements_fixed.md`
- `.kiro/specs/devpost-hackathon-integration/requirements_backpropagated.md`

Canonicalization rules (no code changes):
- Canonical ID: `UNIFIED-REQ-###`
- Keep source headings/structure; preserve semantics from fixed/back-propagated docs
- Derived/technical details remain within acceptance criteria or back-propagated notes; full RDI/RCA to follow in matrix

### Canonical Requirement Set
| Canonical ID | Type | Short Name | Source Section | Acceptance Criteria (refs) | Notes |
| --- | --- | --- | --- | --- | --- |
| UNIFIED-REQ-001 | Business | Local Project Management | requirements_fixed.md §Req1 | requirements_fixed.md §AC1.1–AC1.4 | Replace API notions with local config (fixed) |
| UNIFIED-REQ-002 | Business | Local File Mgmt & Validation | requirements_fixed.md §Req2 | requirements_fixed.md §AC2.1–AC2.5 | Detect/validate files; prep submission package |
| UNIFIED-REQ-003 | Business | Metadata Mgmt & Validation | requirements_fixed.md §Req3 | requirements_fixed.md §AC3.1–AC3.5 | Title/tagline/description/tags/team locally |
| UNIFIED-REQ-004 | Business | Deadline Tracking & Notifications | requirements_fixed.md §Req4 | requirements_fixed.md §AC4.1–AC4.5 | Store deadlines; reminders; readiness |
| UNIFIED-REQ-005 | Business | Preview Generation & Validation | requirements_fixed.md §Req5 | requirements_fixed.md §AC5.1–AC5.5 | Local DevPost-like preview; highlight gaps |
| UNIFIED-REQ-006 | Business | Multi-Project Management | requirements_fixed.md §Req6 | requirements_fixed.md §AC6.1–AC6.5 | Isolation and switching |
| UNIFIED-REQ-007 | Derived | CLI Interface (UX) | requirements_backpropagated.md §Req7 | requirements_backpropagated.md §AC7.1–AC7.5 | CLI structure/output/help/error handling |
| UNIFIED-REQ-008 | Derived | Browser Automation & Data Extraction | requirements_backpropagated.md §Req8 | requirements_backpropagated.md §AC8.1–AC8.5 | Playwright-first; a11y; scraping fallback |
| UNIFIED-REQ-009 | Derived | Logging & Profiling Infrastructure | requirements_backpropagated.md §Req9 | requirements_backpropagated.md §AC9.1–AC9.4 | Structured logs; profiling; diagnostics |
| UNIFIED-REQ-010 | Derived | System Architecture & Compliance (RM-DDD) | requirements_backpropagated.md §Req10 | requirements_backpropagated.md §AC10.1–AC10.4 | ReflectiveModule, registry, health |

### Non-Functional / Technical Requirement Groups
| Canonical ID | Group | Source | Notes |
| --- | --- | --- | --- |
| UNIFIED-TR-001..014 | Technical Requirements | requirements_fixed/backpropagated: TR1..TR14 | Config schema; file watching; previews; export; CDP/a11y/scraping; logging; profiling; debugging |
| UNIFIED-NFR-001..004 | Non-Functional Requirements | requirements_fixed/backpropagated: NFR1..NFR4 | Performance, reliability, usability, maintainability |

### Back-Propagated Requirement Notes (kept under canonical IDs)
- UNIFIED-REQ-001: R1.5–R1.7 (ReflectiveModule, registry, health) from implementation
- UNIFIED-REQ-002: R2.6–R2.7 (git integration, change events)
- UNIFIED-REQ-003: R3.6–R3.7 (config mgmt, connections)
- UNIFIED-REQ-004: R4.6 (notification integration)
- UNIFIED-REQ-005: R5.6 (template engine integration)
- UNIFIED-REQ-006: R6.6 (context isolation)
- UNIFIED-REQ-007: R7.1–R7.3 (CLI structure/ops/reporting)
- UNIFIED-REQ-008: R8.1–R8.4 (Playwright/a11y/scraping hierarchy)
- UNIFIED-REQ-010: RM-DDD conformance specifics

### Open Questions / Gaps to Clarify (Requirements-Only)
- Evidence requirements as first-class (screenshots, text dumps, SHA256, UTC timeline) – incorporate under UNIFIED-TR (logging/proofs) or as new UNIFIED-REQ-011?
- Minimum selector stability requirements for browser automation (acceptance thresholds)
- Explicit idempotency requirement for submit operations (re-runnable without side effects)

### Next (still requirements-only)
- Assign precise AC references (by document+number) per canonical ID
- Prepare RDI matrix skeleton (Req → Design placeholders → Implementation placeholders)

---

## RDI Traceability Matrix (Skeleton)
| Requirement (Canonical) | Design Element(s) (Placeholder) | Implementation (files/selectors) (Placeholder) | Artifact(s) (Placeholder) |
| --- | --- | --- | --- |
| UNIFIED-REQ-001 | .kiro/specs/devpost-hackathon-integration/design_fixed.md §Project Config | Config loader; CLI init; JSON schema paths | n/a |
| UNIFIED-REQ-002 | design_fixed.md §File Validation | File monitors; validation engine; media checks | EV-.. file validation logs (TBD) |
| UNIFIED-REQ-003 | design_fixed.md §Metadata Editor | Fields: `#participants_manage_project_overview_title`, `#participants_manage_project_overview_tagline`, `#software_description`, `#software_tag_list`, `#software_urls_attributes_0_url`, `#software_video_url`; Scripts: `ultra_paranoid_automation.py` (fill_form_field), terminal Playwright one-shot | Screenshots of filled fields; body dumps |
| UNIFIED-REQ-004 | design_fixed.md §Deadline Tracker | Deadline calc; reminders scheduling | n/a |
| UNIFIED-REQ-005 | design_fixed.md §Preview Generator | HTML template engine; live refresh | Preview HTML snapshot; hash |
| UNIFIED-REQ-006 | design_fixed.md §Multi-Project Context | Context switching logic; isolation rules | n/a |
| UNIFIED-REQ-007 | design_fixed.md §CLI | CLI command tree; help output | CLI help/output captures |
| UNIFIED-REQ-008 | design_fixed.md §Automation & Extraction | Playwright over CDP to existing Chrome; key selectors: terms checkbox `#participants_manage_finalization_accepts_terms`, submit button `button:has-text('Submit project')` (fallback `text=Submit project`); Files: `ultra_paranoid_automation.py`, terminal one-shot scripts | final_submit_before_*, final_submit_after_*, my_projects_status_*, body dumps, incognito_public_* |
| UNIFIED-REQ-009 | design_fixed.md §Logging & Profiling | Structured logger; timers; diagnostics | Log excerpts; profiling snapshot |
| UNIFIED-REQ-010 | design_fixed.md §RM-DDD Compliance | ReflectiveModule/registry/health components | Module info/health outputs |


