# Analyze Staging Prompts for Completion

## Mission
Analyze all prompts in `./prompts/staging/` to determine which are completed and should be moved to `./prompts/complete/`. Move completed prompts and provide a summary report.

## Context
The staging directory contains numerous prompts related to constellation elaboration, CMS architecture, and various phases of development. We need to identify which prompts represent completed work versus ongoing or future work.

## Task
1. **Scan all files in `./prompts/staging/`** - Read each file to understand its purpose and completion status
2. **Analyze completion indicators** - Look for:
   - Files marked as "COMPLETE" or "FINISHED" 
   - Summary documents that indicate work is done
   - Files that reference completed deliverables
   - Analysis documents that conclude with findings
   - Files with "OPTIMIZATION-COMPLETE" or similar indicators
3. **Categorize by completion status**:
   - **Completed**: Ready to move to `./prompts/complete/`
   - **In Progress**: Should remain in staging
   - **Template/Reference**: May need different handling
4. **Move completed prompts** to `./prompts/complete/` directory
5. **Generate completion report** showing what was moved and why

## Completion Criteria Indicators
Look for these patterns that suggest completion:
- Files with "COMPLETE", "FINISHED", "DONE" in title or content
- Summary documents that provide final analysis
- Files that reference delivered artifacts or completed phases
- Analysis documents with conclusions and recommendations
- Files that indicate "optimization complete" or "execution complete"

## Expected Deliverables
1. **Moved files**: All completed prompts relocated to `./prompts/complete/`
2. **Completion report**: Summary of what was moved and rationale
3. **Remaining staging inventory**: List of what stays in staging and why

## Success Criteria
- All genuinely completed prompts are moved to complete directory
- No in-progress or template files are incorrectly moved
- Clear documentation of completion rationale for each moved file
- Staging directory contains only active/future work

## References
- Current staging directory: `./prompts/staging/` (90+ files)
- Target directory: `./prompts/complete/` (currently empty)
- Look for completion patterns in file names and content

---

**Execute this analysis systematically, reading each staging file to determine completion status before making any moves.**