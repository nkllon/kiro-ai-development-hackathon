## ADR-001: No Public DevPost API – Web Integration Only

Context: DevPost provides no supported public API for hackathon project management.

Decision: Integrate via web UI only using browser automation (Playwright via CDP), accessibility APIs as needed, and web scraping as last-resort fallback.

Consequences:
- Pros: Works with live site; preserves session via CDP; verifiable.
- Cons: Fragile selectors; SPA state issues; requires robust verification.

Related Requirements: UNIFIED-REQ-008, UNIFIED-TR (automation), UNIFIED-NFR (reliability).

