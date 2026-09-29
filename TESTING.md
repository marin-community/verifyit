# Testing guidelines for verifyit

Read the shared [behavior-focused testing policy](.agents/marin-style/TESTING-core.md)
and AGENTS.md before writing or reviewing tests. The local rules below define
commands and grading boundaries for this package.

## Running tests

```bash
uv sync --locked --all-extras --group test
uv run pytest tests/test_exact.py
uv run pytest tests
infra/pre-commit.py --all-files
uv build
```

Tests use temporary files, real local subprocesses, and a local HTTP judge
fixture. They require no remote model credentials. The Go integration test
runs when `go` is available and skips otherwise; CI installs Go. The default
timeout is 120 seconds, configured in pyproject.toml. Give a legitimately
longer test an explicit timeout rather than raising the global default.

Run focused tests while editing and the full suite for behavior changes before
publishing. Documentation-only changes need link and command checks. A
formatter-only change needs the shared lint entry point.

## Grading contracts

Prefer assertions on public spec parsing/rendering, returned reward and status,
and persisted CLI verdicts. A candidate scoring zero differs from an invalid
task or infrastructure error. Only scored results write reward files; a new
unscored verdict must remove stale reward files. Exercise those consequences
when changing dispatch or error handling.

Use real subprocesses in temporary workspaces to verify executable graders,
protected-test restoration, and timeout cleanup. A deliberate sleep in a child
program is appropriate when testing grader timeout cleanup. Use the existing
local HTTP fixture for judge responses; normal tests must not call a live service.

When changing optional imports or extras, verify that a core-only installation
can still run unrelated modes. For mathematical and numeric scoring, use known
results or an independent reference and exercise relevant tolerance boundaries.
Do not weaken tolerances or expectations to make failures pass.
