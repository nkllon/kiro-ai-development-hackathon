## ADR-003: Idempotent Submit and Evidence Hashing

Context: Repeated submits must be safe; audits must be verifiable.

Decision: Treat DevPost submit as idempotent; always verify success markers and project status. Capture before/after screenshots and body dumps; compute SHA256 hashes and record UTC timestamps.

Consequences:
- Pros: Safe re-runs; audit-grade evidence.
- Cons: Extra storage; process overhead.

Evidence of Record:
- `final_submit_before_*.png`, `final_submit_after_*.png`, `my_projects_status_*.png`, `finalization_body_*.txt`, `my_projects_body_*.txt`, `incognito_public_*.png`

Related Requirements: UNIFIED-REQ-005, UNIFIED-REQ-008, UNIFIED-TR (logging/proofs), UNIFIED-NFR.

