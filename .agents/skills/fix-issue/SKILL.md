---
name: fix-issue
description: Implement a fix for an explicitly identified marin-community/verifyit GitHub issue.
---

# Fix an issue

Read AGENTS.md and the issue, including recent comments. Search open PRs and
issues for overlapping work before implementing. Reuse an existing fix when it
covers the same problem, or scope a follow-up to the remaining behavior.

Reproduce the reported behavior using the debug skill. Explain the cause and
smallest fix in the current task or issue. Use a `codex/fix-<issue-number>`
branch. Follow write-tests for regression coverage and update-docs when usage
or a public contract changes.

Validate and publish through commit. Reference the issue in the PR body with
`Fixes #<number>` when the fix fully addresses it. A request to fix an issue
authorizes reporting the fix and blockers on that issue; prefix comments with
`🤖`. Follow writing-style and keep comments factual and concise.

Monitor through the commit workflow. Report the merged/closed state or timeout;
do not merge without explicit user authorization.
