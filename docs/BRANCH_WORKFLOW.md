# `rc1-patch` Integration Workflow

The active work for the release candidate happens on `rc1-patch`. Treat the historic `master` branch as read only until the release
is officially promoted. Any change that accidentally merges straight into `master` will diverge from the infrastructure that is
deployed today, so make a habit of double-checking your current branch before committing.

```bash
git checkout rc1-patch
git pull --ff-only
```

If you discover the branch locally under a different name (for example, `work` or another scratch branch), rename it so that
future scripts and documentation remain consistent.

## Starting New Work

1. **Branch off `rc1-patch`.** Use `git checkout -b <feature> rc1-patch` so your change inherits the latest fixes and hot patches.
2. **Keep diffs surgical.** Small, focused commits make it easy to cherry-pick fixes into other deployments or revert if an agent
   introduces a regression.
3. **Run local validation.** The `Makefile` wraps the common checks (`make lint`, `make test`, etc.). Running them before a pull
   request keeps the CI pipeline quiet.
4. **Sync frequently.** Rebase or merge from `rc1-patch` whenever you notice new commits landing so that the next merge is clean.

## Pull Request Expectations

When you open a PR:

- **Target branch:** Always set the base to `rc1-patch` unless you are coordinating a release promotion. Mention any exception in
  bold at the top of the description.
- **Testing notes:** Fill out the testing section in `PULL_REQUEST_TEMPLATE.md` so we can trace how the change was validated.
- **Infra call-outs:** Flag Docker, networking, or credentials requirements. The observatory stack spans multiple machines, so
  reviewers need to know if extra services must be running.
- **Link dependent specs:** If the work came from a Kiro or SPORE spec, add the link to help downstream agents understand the
  context.

These notes make it easier to operate the public-facing lab without pausing for clarification pings.

## Merging While Solo

Branch protection currently enforces a single approving review on `rc1-patch`. When you are the only maintainer online:

1. Use the **Admin override** button in the GitHub UI _or_ run `gh pr merge <number> --admin` to record that the bypass was
   intentional.
2. Leave a short note in the PR summary that no reviewer was available and that the change is limited to release-candidate work.
3. Restore the standard protections immediately if you temporarily relaxed any rules in repository settings.

Documenting the override keeps the audit trail clean so that when additional collaborators join, they can verify that the
release candidate history remained controlled even without formal reviews.

## Promoting to `master`

Once the release candidate is ready for publication, coordinate a scheduled window to fast-forward `master` from `rc1-patch`.
Announce the window to anyone running long-lived branches, tag the release, and update the observatory deployment notes. Until
that coordinated promotion happens, keep all day-to-day development on `rc1-patch`.

