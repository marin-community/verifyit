---
name: commit
description: Validate, commit, push, publish, and monitor a verifyit change when it is ready for review.
---

# Commit and PR

Read root AGENTS.md, CONTRIBUTING.md, and the writing-style skill's
pull-requests.md and ai-writing-donts.md before authoring commit or PR text.

## Prepare and validate

Review the complete branch diff against the merge base with origin/main,
including staged, unstaged, and untracked work. Remove unrelated edits, dead
code, weak tests, and stale prose. Read TESTING.md when tests change.

Use the repository's existing checks:

```bash
uv sync --locked --all-extras --group test
uv run ruff check .
uv run black --check .
uv run pyrefly check
```

For behavior changes, run focused tests, `uv run pytest tests`, and `uv build`.
For documentation-only work, validate links and every new command; do not add
tests that merely match documentation wording. Use Ruff's `--fix` and Black
on affected Python files when formatting is needed, then rerun their checks.

Stage only the task's files. Inspect `git diff --cached --check`, the staged
diff, and the exact commit message. After committing, inspect
`git show -s --format='%s%n%n%b' HEAD` for unintended attribution or trailers.
Fix hook failures in a new commit; do not amend without user authorization.

## Advisory review before publication

After the initial commit and before opening a PR, have an independent read-only
agent review the committed branch against AGENTS.md, TESTING.md, and the
writing-style guides. Give it the branch diff and relevant surrounding code.
Use a subagent when available or an authenticated headless CLI in read-only
mode. The reviewer reports findings; it must not edit files, mutate Git, or
post on GitHub.

Address every actionable finding in a follow-up commit. Do not recursively
rerun advisory review after small targeted fixes. Rerun it when the
implementation approach or scope materially changes, or when the user asks.
If no independent reviewer can run, report that limitation and proceed with
mechanical checks and self-review. Do not claim an agentic lint pass.

## Publish

Push when requested or when the task is being carried through publication.
Use `git push -u origin HEAD`. Stop on rejection; do not force-push without
explicit authorization.

The PR description becomes the squash-merge commit message. Write the exact
body to a uniquely named temporary file, inspect it, and use `--body-file`.
Keep behavior, motivation, constraints, and issue links; omit validation logs,
file inventories, and attribution. Add `agent-generated` to agent-created PRs.
If the label is absent in a new repository, attempt to create it before publishing; if permission is denied, report the limitation
and continue publication when otherwise authorized.

After creating or editing the PR, fetch its exact title and body with
`gh pr view --json title,body` and correct inserted or stale text. Report
validation and any review limitation in a concise PR comment when useful;
comments begin with `🤖`.

## Monitor

Monitor until the PR merges or closes, the user requests a stop, or 12 hours
have elapsed from monitor creation. Green CI is not a terminal state.
Use a thread heartbeat where available. Save the repository, PR URL, branch,
12-hour deadline, authorization to fix in-scope failures and feedback, and the
instruction to stay quiet when state is unchanged. Do not create a competing
polling loop or require Marin's wait scripts.

Read current CI, issue comments, inline comments, and submitted reviews before
starting the heartbeat. On later runs, address new actionable feedback and
failures, validate changes, and push ordinary follow-up commits. Reproduce a
failure independently on main before treating an untouched-file failure as
unrelated. Resolve review threads after fixing or answering them. Do not merge
without explicit user authorization.

Notify on actionable failures or feedback, a user decision, completion of CI
and review feedback, terminal PR state, or the deadline. Disable the heartbeat
at a terminal state or deadline. If heartbeats are unavailable, report the last
verified state and the monitoring limitation instead of claiming ongoing monitoring.
