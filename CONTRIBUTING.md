# Contributing to verifyit

Use Python 3.11 or newer and [uv](https://docs.astral.sh/uv/). From the repository root:

```bash
uv sync --locked --all-extras --group test
uv run pytest tests
uv run ruff check .
uv run black --check .
uv run pyrefly check
uv build
```

CI runs these checks on Python 3.11, 3.12, and 3.13 and installs Go for the Go grader integration test.
The local Go test skips if the toolchain is absent. Judge tests use a local HTTP fixture;
they do not require API credentials or a remote model service.

During development, run a focused test such as `uv run pytest tests/test_exact.py`.
Format changed Python files with `uv run ruff check --fix <paths>` and
`uv run black <paths>`, then rerun the checks above when the change affects code.
Read [TESTING.md](TESTING.md) before adding or reviewing tests.

## Package boundaries

The core package depends only on `tomlkit`. Keep optional dependencies in their
mode extras (`answer`, `schema`, `judge`, and `reasoning-gym`); execution modes
use the task image's toolchain. A new optional import must not prevent a
core-only installation from importing the package or running unrelated modes.

[`src/verifyit/spec.py`](src/verifyit/spec.py) defines spec parsing and rendering.
[`src/verifyit/grade.py`](src/verifyit/grade.py) owns dispatch, the Python API,
CLI, and verdict files. Graders and shared execution helpers live in
[`src/verifyit/modes`](src/verifyit/modes).

Preserve the distinction between a candidate scoring zero, an invalid task,
and an infrastructure error. The CLI's verdict and reward files are consumed
by task runners. Changes to those contracts need behavioral coverage and
updated usage documentation.

For pytest, JUnit, and Go execution modes, the spec's `restore` entries name
files or directories copied from the task's tests directory back into the
workspace before setup and execution. This restores task-supplied tests after
candidate edits. The `must_not_break` test IDs protect previously passing tests
when calculating the reward. See the [spec dataclasses](src/verifyit/spec.py)
and [shared restoration helper](src/verifyit/modes/run.py).

## Pull requests and agent workflows

GitHub publication uses the `gh` CLI, authenticated for this repository
(`gh auth status`). Pushing needs repository write access; creating labels
needs label-management permission. If publication access is missing, keep the
validated local commit and report the failed action. Use a fork only when
direct access is unavailable or the user requests it. If label creation fails,
report that limitation and publish without the label when otherwise authorized.

Use a `codex/` prefix for agent branches. Keep a pull request focused on one
change, explain its behavior and motivation, and link an existing issue when
applicable. PR descriptions become squash-merge commit messages; keep
validation results in a PR comment when they are useful to reviewers.

[AGENTS.md](AGENTS.md) defines the shared development rules.
[Repository skills](.agents/skills) cover commits, reviews, debugging, tests,
issues, documentation, and prose cleanup. The `.claude/skills` symlink exposes
the same skills to Claude; `CLAUDE.md` points to the same root instructions.

These guidelines are adapted from
[Marin's contributor and agent workflows](https://github.com/marin-community/marin/tree/c09061f04535aecef3ba8aed33cc6746060b22a0/.agents/skills).
