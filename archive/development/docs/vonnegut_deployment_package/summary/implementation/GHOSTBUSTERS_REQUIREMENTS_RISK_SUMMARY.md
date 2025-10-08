## Ghostbusters Risk Summary – Requirements & Design (DevPost Integration)

### Top Risks
1) Naming Convention Drift
   - Symptom: Multiple ID patterns (REQ-###, UNIFIED-REQ-###, NEW-REQ-###)
   - Risk: Traceability confusion
   - Mitigation: Canonicalize on UNIFIED-REQ-###; map legacy IDs in RDI

2) SPA State Verification
   - Symptom: URL not sufficient to verify page state
   - Risk: False positives in automation
   - Mitigation: Always include content checks + screenshots; keep body dumps

3) Session Continuity
   - Symptom: Chrome restart loses session; AppleScript JS toggle off
   - Risk: Login loops; lost context
   - Mitigation: CDP to existing Chrome; checklist for AppleScript toggle

4) Idempotent Submit
   - Symptom: Repeatable submit must be safe
   - Risk: Side effects if not idempotent
   - Mitigation: Verify success markers and project status on each run

5) Evidence Integrity
   - Symptom: Screenshots/dumps lack hashes/timestamps
   - Risk: Weak auditability
   - Mitigation: SHA256 + UTC timeline in audit

### Immediate Actions
- Add hashes/timestamps to evidence set.
- Formalize selectors table and stability criteria.
- Add ADRs for key choices (no API, CDP, a11y fallback, submit idempotency).


