---
name: review-pr
description: Review an explicitly identified verifyit pull request for introduced correctness and maintainability defects.
---

# Review a pull request

Read the shared core referenced by AGENTS.md. Inspect PR metadata, current head, issue comments, inline comments, and submitted
reviews with `gh`. Read AGENTS.md and the instructions that scope changed
paths; read TESTING.md when tests change. Review the complete merge-base diff
and relevant surrounding code at the PR's current head. If a requested head
has changed, report the stale review and post nothing until the target is resolved.

## Standard

Report actionable defects introduced by the PR. Verify each finding against
the diff, call sites, and repository contracts. Check:

- spec parsing/rendering and public API/CLI behavior;
- reward, status, verdict files, and candidate/task/infrastructure error distinctions;
- protected-test restoration, subprocess termination, and timeout cleanup;
- lightweight core installation and mode-specific optional imports and extras;
- Python 3.11 compatibility and consistency across changed callers;
- behavioral test value, independent numerical references, and I/O-boundary fakes;
- documentation and PR text against writing-style/pull-requests.md.

Flag maintainability only for a concrete structural obstacle or hidden coupling.
Omit style preferences, speculative failures, and pre-existing problems. Tests
and CI support a review; passing checks do not prove all contracts are preserved.

## Findings and publication

For each defect, give the changed file/line, concrete impact, evidence, and
smallest useful fix. Distinguish code defects from PR-title/body problems.
If there are no defects, report that directly.

The review is read-only unless the user or invoking workflow authorizes posting.
Before posting, recheck that the PR head is still the reviewed commit. Inspect
existing comments to avoid repeating findings. Prefix comments with `🤖` and
use GitHub's review API or an available inline-comment tool for code findings.
Do not submit approval or request-changes reviews unless authorized.
