# Contributing to verifyit

Use Python 3.11 or newer and [uv](https://docs.astral.sh/uv/). From the repository root:

```bash
uv sync --locked --all-extras --group test
uv run pytest tests
infra/pre-commit.py --all-files
uv build
```

CI runs these checks on Python 3.11, 3.12, and 3.13 and installs Go for the Go
grader integration test. The local Go test skips if the toolchain is absent.
Judge tests use a local HTTP fixture and need no remote model credentials.
Run focused tests while editing; read [TESTING.md](TESTING.md) before adding coverage.

## Shared style kit

[marin-style](https://github.com/marin-community/marin-style) supplies the shared
coding/testing standards, portable skills, and lint-review catalog. The exact
Git revision is pinned in pyproject.toml and infra/pre-commit.py. The style
dependency group is selected only on Python >=3.12; the lint shim has an
isolated Python >=3.12 environment and preserves the package's Python 3.11 support.

The required lint entry point runs Ruff, Black, and Pyrefly with this repository's
configuration. Use it for fixes and advisory review:

```bash
infra/pre-commit.py --changed-files --fix
infra/pre-commit.py --review
```

Attempt the advisory review after committing and before publishing the PR.
It uses `claude -p` by default and needs that CLI authenticated, or a configured
headless command supplied with `--agent-command`. Follow the
[unavailable-reviewer fallback](AGENTS.md#repository-workflows) if it cannot run.

The vendored guidance is generated and tracked by
`.agents/marin-style/manifest.json`. Regenerate it from the pinned package:

```bash
uv run --isolated --locked --python 3.12 --group style marin-style sync
uv run --isolated --locked --python 3.12 --group style marin-style sync --check
```

CI runs the check command to detect drift. Keep local rules in AGENTS.md,
TESTING.md, or repository-owned skills; do not edit manifest-owned files.
The `.claude/skills` symlink exposes the same skills to Claude, and CLAUDE.md
points to the root instructions.

## Updating marin-style

The update workflow uses the shared `actions/update-consumer` action. It keeps
the dependency, lint shim, generated guidance, lockfile, and action pin in sync
and opens an update PR. It uses `mode: publish`; it does not merge updates.

Automatic updates are opt-in because this new repository has no updater
credentials configured. Before setting repository variable
`MARIN_STYLE_UPDATES_ENABLED=true`, configure the `external-runtime-updater`
environment to admit only the default branch, provide its
`DEPENDENCY_UPDATER_PRIVATE_KEY` secret, and give the
`marin-external-runtime-updater` App access to this repository. The workflow
can then run nightly or through workflow_dispatch. Do not weaken CI protections.

For a manual update, advance the kit revision in pyproject.toml,
infra/pre-commit.py, and the update workflow; run `uv lock --python 3.12`,
then regenerate and check the vendored files with the commands above.

## Package boundaries

The core depends on `tomlkit` and an immutable `harbor-config` revision for shared
error categories; it does not import the Harbor runtime. Keep grading dependencies in mode extras
(`answer`, `schema`, `judge`, and `reasoning-gym`); execution modes use the task
image's toolchain. An optional import must not prevent a core-only installation
from importing the package or running unrelated modes.

[src/verifyit/spec.py](src/verifyit/spec.py) defines spec parsing and rendering.
[src/verifyit/grade.py](src/verifyit/grade.py) owns dispatch, the API, CLI, and
verdict files. Primitive graders live in [modes](src/verifyit/modes). Shared
command and trusted-call execution lives in [execution](src/verifyit/execution);
[file_ops](src/verifyit/file_ops) owns text, bounded artifact, and restoration
mechanics. Callers retain their decoding and format-validation policies.

For pytest, JUnit, and Go modes, `restore` entries copy files/directories from
the task's tests directory back into the workspace before setup and execution.
The `must_not_break` IDs protect previously passing tests when calculating reward.
See the [spec dataclasses](src/verifyit/spec.py) and
[restoration helper](src/verifyit/file_ops/restore.py).

## Pull requests

Follow [AGENTS.md](AGENTS.md) and the commit skill. GitHub publication uses
`gh` authenticated for this repository; pushing requires write access. Use a
`codex/` prefix for agent branches. PR descriptions become squash-merge commit
messages; keep validation results in a PR comment when useful to reviewers.
