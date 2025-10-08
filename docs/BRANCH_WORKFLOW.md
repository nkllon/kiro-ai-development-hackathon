# Branch Workflow Overview

This repository currently uses the `rc1-patch` branch as the primary integration branch for release candidate maintenance work. The historic `master` branch does not include the latest fixes and should only be referenced for archival purposes. Until we promote the release candidate, **do not merge directly into `master`**.

## Working on `rc1-patch`

- Start all new patches from `rc1-patch` (for example: `git checkout rc1-patch && git pull`).
- Keep commits focused and small so they can be cherry-picked into future release branches if needed.
- Run the standard validation scripts (see `Makefile`) before opening a pull request.
- Coordinate any work that genuinely targets `master` with the release manager so we can schedule the promotion together.

## Opening Pull Requests

When creating a pull request:

1. Target the `rc1-patch` branch unless explicitly coordinating a different destination.
2. Call out any dependency on infrastructure changes (Docker, networking, etc.) in the pull request description so reviewers can prep the environment.
3. Include a short summary of the change and any validation steps performed.
4. Use the existing pull-request template in `.github/PULL_REQUEST_TEMPLATE.md` to highlight testing and impact.

Keeping these conventions ensures that the release candidate remains stable while we continue preparing the repository for publication and avoids accidental regressions on `master`.
