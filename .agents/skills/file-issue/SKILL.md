---
name: file-issue
description: File a verifyit GitHub issue only when explicitly requested or authorized by the user.
---

# File an issue

Read AGENTS.md and the writing-style skill's issues.md and ai-writing-donts.md.
Search open issues in marin-community/verifyit for the same symptom before
filing. Report an existing match instead of duplicating it.

Use a factual symptom for a bug title or an imperative outcome for a task;
keep it at most 80 characters. A bug body explains the impact, minimal
numbered reproduction, expected behavior, and concise evidence. A task body
explains the desired change and testable completion criteria. Link extended
logs and source evidence rather than pasting investigation history.

Inspect the exact title and body before publication. Write the body to a
uniquely named temporary file and use `gh issue create --body-file`. Add
`agent-generated` and existing kind/priority labels when applicable. If
`agent-generated` is absent, attempt to create it; if permission is denied, report the limitation
and continue publication when otherwise authorized. Do not invent a priority.

An explicit request to file an issue authorizes publication without another
preview. If the issue was discovered during other work, report the finding;
do not create it without user authorization.

After publication, fetch `gh issue view --json title,body` and correct stale
or tool-inserted text. Return the issue link.
