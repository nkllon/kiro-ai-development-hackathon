# Branch Workflow Overview

This repository currently uses the `rc1-patch` branch as the primary integration branch for release candidate maintenance work. The historic `master` branch does not include the latest fixes and should only be referenced for archival purposes.

## Working on `rc1-patch`

- Start all new patches from `rc1-patch`.
- Keep commits focused and small so they can be cherry-picked into future release branches if needed.
- Run the standard validation scripts (see `Makefile`) before opening a pull request.

## Opening Pull Requests

When creating a pull request:

1. Target the `rc1-patch` branch unless explicitly coordinating a different destination.
2. Include a short summary of the change and any validation steps performed.
3. Use the existing pull request template in `PULL_REQUEST_TEMPLATE.md` to highlight testing and impact.

Keeping these conventions ensures that the release candidate remains stable while we continue preparing the repository for publication.
