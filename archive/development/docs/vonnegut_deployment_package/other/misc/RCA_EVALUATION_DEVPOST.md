## RCA Evaluation – DevPost Integration Artifacts

Policy: Each artifact must have a root cause (why it exists) tied to requirements/design.

### Ledger (Initial)
| Artifact | Root Cause | Linked Requirement(s) | Evidence/Notes | Decision |
| --- | --- | --- | --- | --- |
| final_submit_before_20250915_023925.png | Evidence of pre-submit state | UNIFIED-REQ-008, UNIFIED-REQ-005 | SCA proof (before) | Keep |
| final_submit_after_20250915_023925.png | Evidence of post-submit and redirect | UNIFIED-REQ-008 | SCA proof (after) | Keep |
| my_projects_status_20250915_023925.png | Status badge verification | UNIFIED-REQ-008 | Confirms Submitted | Keep |
| finalization_body_20250915_023229.txt | Content-based verification | UNIFIED-REQ-008 | SPA content check | Keep |
| my_projects_body_20250915_023413.txt | Content verification for list | UNIFIED-REQ-008 | Shows draft/submitted words | Keep |
| incognito_public_20250915_031727.png | Public visibility verification | UNIFIED-REQ-005, UNIFIED-REQ-008 | Incognito/public page load | Keep |

### SHA256 Hashes
- final_submit_before_20250915_023925.png: `44ed9fdeaa67d595fdedbba8b9be64d98aa91d5f262c9df7688aee458f90b1d1`
- final_submit_after_20250915_023925.png: `5c42bc5c55256e665b69220d48f2aef32484a18151d22aee9b64677c319848d6`
- my_projects_status_20250915_023925.png: `783c4f731aa3576c34246f2cec28b60e3a79b9124b3172ccf4e6f1a5bd95c568`
- finalization_body_20250915_023229.txt: `981c02f3366c0d7a9a9dc098c87e718b9ac6286b03c506af9d0547f470aed22c`
- my_projects_body_20250915_023413.txt: `25063edf5d2f77ef6475a352de6eda6c164a76da2ae25bac98956ca625bf4053`
- incognito_public_20250915_031727.png: [compute if needed]

Open: Add UTC timeline entries for each artifact creation event.


