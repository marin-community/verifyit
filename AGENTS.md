# Agent Guidelines for verifyit

Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, commands, and package boundaries.
Read [TESTING.md](TESTING.md) before writing or reviewing tests.

## Workflow playbooks

Skills live in `.agents/skills/`, also exposed through `.claude/skills/`.
Before non-trivial work, check for a matching skill and read its `SKILL.md`.

- `debug`: reproduce and diagnose a stated failure.
- `write-tests`: add or review behavior-focused coverage.
- `update-docs`: keep usage and contributor instructions current.
- `commit`: validate, commit, review, publish, and monitor a PR.
- `review-pr`: review a requested PR at its current head.
- `file-issue` and `fix-issue`: handle explicitly requested GitHub issue work.
- `noslop`: simplify a requested diff or remove low-value tests and prose.
- `writing-style`: apply the shared prose rules and the guide for the medium.

Use `rg` for the current checkout and Git history or GitHub for prior work.
These workflows run from this repository; they do not require a Marin checkout.

## Development

Use Python >=3.11 and `uv run` for Python entry points. The commands in
CONTRIBUTING.md match CI. Keep core installation lightweight and optional
mode dependencies isolated. Do not add a dependency on Marin or its services.

Preserve the verdict statuses, reward-file behavior, CLI exit behavior, and
spec parsing/rendering contracts described in README.md. Test candidate errors,
malformed tasks, and infrastructure failures at their observable boundaries.
Execution modes run task-provided programs; maintain process-group cleanup on
timeout and protected-test restoration.

Search the existing source and `pyproject.toml` before adding a helper or
dependency. Reuse the shared parsers and execution helpers when they fit.

## Communication and commits

- Never credit the agent in commit messages or PR/issue bodies. Do not add
  `Co-Authored-By`, generation notices, or session trailers.
- Use `codex/` for agent branches. Never amend or force-push without user authorization.
- Add `agent-generated` to agent-created PRs and issues.
- Agent PR/issue comments begin with `🤖` unless the exact text was approved by the user.
- Follow `writing-style` for commits, PRs, issues, comments, and documentation.
- Use `gh ... --json <fields>` or narrow flags when inspecting GitHub objects.
- Publishing a PR does not authorize merging it. Require explicit user authorization to merge.
- Use heartbeats for PR monitoring where available. Stay quiet when state is unchanged;
  notify on actionable failures or feedback, decisions, completion, or timeout.

## Code Style

- All imports at the top of the file. No local imports except to break circular dependencies or guard optional deps. No `TYPE_CHECKING` guards — fix cycles structurally via protocols.
- Prefer top-level functions over classes when code does not mutate shared state. Reduce deep inheritance hierarchies.
- Use early returns to reduce nesting.
- Document public APIs with concise Google-style docstrings. Skip docstrings on trivial functions with clear names.
- Prefer `dataclasses.replace` over mutating config arguments in-place.
- Prefer logging over `print` (except in scripts and debugging).
- Resolve environment-dependent defaults once and fail fast on unknown inputs.
- No ad-hoc compatibility hacks (`hasattr(m, "old_attr")`); update code consistently.
- Prefer small concrete helpers over abstraction that adds indirection without reuse. Start simple; abstract only under real pressure.
- Delete dead code: unused parameters, stale options, old experiments.
- Top-level constants for magic strings/numbers.
- Separate computation from I/O (split compute from upload/write).
- Use context managers for resource lifecycle.

## Naming

- No `*_utils.py` — use descriptive names like `text_cleaning.py`.
- Function names should reflect return types (`probe_task` → `task_status`).
- No `_s` suffix for seconds (assumed in this codebase). No abbreviations like `exe` — use `exec` or full words.

## Types & Data Structures

- Dataclass/namedtuple over raw dicts. `StrEnum` over string keys.
- Use `Protocol` for decoupling; avoid hard-coupling to concrete types.
- Avoid `X | str` unions that require `isinstance` checks — pick one input type.
- Replace compound booleans encoding state with an enum.

## Configuration

- No `default_*` wrappers that obscure underlying mechanisms.
- Force explicit specification of critical parameters (no silent defaults).
- Centralize defaults in one canonical location.
- Prefer explicit constructor/config parameters over env vars.
- Composition over inheritance: embed sub-configs, don't subclass.

## API Design

- Accept only what's necessary. Replace boolean flags with meaningful parameters (e.g., `num_workers: int` instead of `parallel: bool`).
- Express distinct behavior variants through explicit types or modes.
- Normalize inputs to a standard format once at the boundary, not throughout.

## Error Handling

- Let exceptions propagate by default.
- Only catch to add meaningful context and re-raise, or to intentionally alter control flow.
- NEVER swallow exceptions unless specifically requested.
- Assert liberally; prefer `raise ValueError` over silent fallbacks.

## Documentation and planning

Keep README.md and contributor instructions synchronized with behavior.
Write documentation that stands alone. Record investigation and implementation
progress in the existing task, issue, or PR; do not add one-off planning or
session log files to the repository.

For a non-trivial change, resolve repository context and explain the concrete
plan before editing. Ask only when a missing decision would materially change
the implementation. Continue authorized work through validation and publication.

## Compatibility and comments

Update affected call sites instead of adding compatibility shims unless the
user explicitly requests one. Account for consumers such as Marin when changing
public specs, imports, CLI arguments, environment variables, or verdict files.

Comments explain subtle behavior or constraints. Delete stale comments and
avoid narrating the code. Keep public docstrings concise; omit docstrings on
trivial functions with clear names.

## Testing

TESTING.md owns test quality, numerical tolerances, mocks, timing, and commands.
Fix tests you break. Do not weaken tolerances or expectations to make a failure
pass. Keep scratch probes outside checked-in tests.
