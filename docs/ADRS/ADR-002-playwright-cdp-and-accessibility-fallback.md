## ADR-002: Playwright over CDP with Accessibility Fallback

Context: Need robust, session-preserving automation against DevPost web UI.

Decision: Primary automation via Playwright connected to existing Chrome over CDP port 9222; fallback to OS accessibility APIs; final fallback to web scraping.

Consequences:
- Pros: Preserves cookies/session; resilient interactions; OS-level control available.
- Cons: Requires Chrome debug port; accessibility toggles; selector maintenance.

Selectors of Record:
- Terms checkbox: `#participants_manage_finalization_accepts_terms`
- Submit button: `button:has-text('Submit project')` (fallback `text=Submit project`)
- Metadata fields: `#participants_manage_project_overview_title`, `#participants_manage_project_overview_tagline`, `#software_description`, `#software_tag_list`, `#software_urls_attributes_0_url`, `#software_video_url`

Related Requirements: UNIFIED-REQ-003, UNIFIED-REQ-008, UNIFIED-TR (automation), UNIFIED-NFR.

