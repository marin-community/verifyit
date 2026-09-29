# Testing guidelines

This policy is adapted from Marin's behavior-focused testing guidance.
Read AGENTS.md and CONTRIBUTING.md alongside it.

## Running tests locally

```bash
uv sync --locked --all-extras --group test
uv run pytest tests/test_exact.py  # focus on the behavior being changed
uv run pytest tests               # full local suite
```

The test environment includes every mode extra. Tests use temporary files,
real local subprocesses, and a local HTTP judge fixture. They require no remote
model credentials. The Go integration test runs when `go` is available and
skips otherwise; CI installs Go. Tests have a 120-second default timeout from
pyproject.toml. Give a legitimately longer test an explicit timeout instead of
increasing the global default.

Run focused tests while editing and the full suite for behavior changes before
publishing. Documentation-only changes need link and command checks. A
formatter-only change needs formatting and lint checks.

## Grading contracts

Prefer assertions on public spec parsing/rendering, returned reward and status,
and persisted CLI verdicts. A candidate scoring zero differs from an invalid
task or infrastructure error. Only scored results write reward files; a new
unscored verdict must remove stale reward files. Exercise these consequences
when changing dispatch or error handling.

Use real subprocesses in temp workspaces to verify executable graders,
protected-test restoration, and timeout cleanup. Keep remote judge responses
behind the existing local HTTP fixture. For optional dependencies, confirm a
core-only installation can still run unrelated modes when a change affects
import boundaries or package extras.

## Core Rule

A test must fail when behavior is wrong. It should not fail only because an
implementation detail, wording choice, helper call, or command assembly changed.

Do not add a test for every validation branch. A scalar or configuration guard
such as `count > 0`, enum membership, a required field, or a simple range check
does not justify a checked-in test by itself. Test such a guard only when it
reproduces a reported regression or protects a compatibility-critical public
contract. Otherwise, test the consequential behavior on the valid path or omit
the test.

Prefer integration-style tests that validate externally observable behavior:

- public API return values
- structured output or machine-readable fields
- persisted state
- real side effects in a temp directory or in-memory fake
- grading status and reward-file transitions
- mathematical and numeric scoring against an independent reference

Delete tautological tests and tests that pin implementation details without protecting behavior.

## Good Targets

- A regression for a reported bug.
- A boundary case where user-visible behavior changes: empty input, duplicate
  answers, malformed output, missing references, timeout behavior, failed
  toolchains, or invalid specs.
- A round trip through the public API: parse, render, reload, and grade a spec.
- A stable contract: spec field, CLI JSON output, reward file, or public exception type.
- For numerical grading, compare scores against known mathematical results and tolerance boundaries.

## Slop Tests To Reject

Delete or rewrite tests with negative value:

- Tautologies: constant equals itself, method exists, object constructor assigns
  attributes, `len(list) >= 0`, type exists. This definition should be construed broadly.
- Private state: assertions on private attributes or `_`-prefixed state.
- Incidental strings: assertions on human log text, progress messages, command
  fragments, or copied prose.
- Internal helper dispatch: assertions on `assert_called_once_with`, call count,
  or "helper X was invoked" for in-process helpers.
- Reimplementation: Tests that reimplement the production logic and compare the implementation to
  itself.
- Obvious error-condition behavior: Obvious error-condition tests that only prove a type checker, dataclass
  constructor, or standard library function works. Infrastructure failure modes
  are valid when the failure is externally observable.
- Scalar and configuration guards: standalone tests that only set a count,
  timeout, enum, boolean, or other config value outside an obvious allowed range
  and assert that construction raises. Keep one only for a reported regression
  or a compatibility-critical public contract.
- Tests for Python language semantics.
- Registration tests: Tests that check that specific items are registered in global registries.
- Configuration projections: assertions that a lowered or constructed field equals the same value
  supplied by the test or checked-in config. Test validation, merge conflicts, observable behavior,
  or a real external wire translation instead.
- Permanently skipped tests or empty test files.
- Screenshot-only tests without behavioral assertions.
- "Does not raise" tests without a comment explaining why that is the contract.
- "Does raise" tests if the exception type is not part of the contract or an important regression signal.

Disposable smoke probes are different from checked-in tests. During development,
use scratch scripts, REPL snippets, or temporary local assertions to confirm
imports, object construction, or fixture wiring. Do not leave those as pytest
tests. Before a PR-ready commit, replace them with behavior assertions or delete
them.

String assertions are allowed when the string is the contract: a wire format,
machine-readable output, a downstream-parsed log line, or an exact user-facing
error promised by the API. Assert on structured fields when possible.

Command construction is rarely the contract. Prefer to run through the boundary
and assert the effect. If the command line is the contract, assert the parsed
argv or structured command object, not a substring in rendered shell text.

Exact dependency versions, default scalar values, and serialized configuration
text are not contracts by default. Test the compatibility behavior they enable.
Assert an exact value or representation only when external consumers depend on
it.

## Mocks And Fakes

Default to real behavior. Use mocks only at I/O boundaries:

- toolchain subprocesses
- HTTP or remote APIs
- model endpoints and other external services
- filesystem boundaries that would be slow, expensive, or destructive

Prefer fakes over mocks when practical: in-memory services, temp directories,
local HTTP clients, and fake clocks. Reuse the existing local judge fixture
and temp-directory helpers before adding a new fake.

Do not mock internal functions to prove wiring. If a side effect matters, expose
or observe it through a public API or use a fake that records stable state.
If the effect is hard to observe, reconsider the test or expose the relevant
behavior through the public API.

## Timing

Do not use `time.sleep()` in tests. Inject `now=time.time()`, use a fake clock,
or use existing deadline/backoff helpers.

Reuse existing deadline or fake-clock helpers when they exist. A short sleep
to let a background thread start needs a comment naming the race. A deliberate
sleep in a child program is appropriate when testing grader timeout cleanup.

## Numerical tests

Use an independent reference or known result for mathematical and numeric
scoring. Exercise the tolerance boundary and nonfinite values when those affect
the public grading contract. Do not relax tolerances without human agreement.

## Pytest Style

- Prefer top-level `def test_*` functions with fixtures over test classes.
- Name tests as `test_<subject>_<scenario>_<expected_outcome>`.
- Use parameterization for meaningful behavior variation.
- Extend existing test files before creating new ones.
- Every test must contain an assertion or `pytest.raises`.
- Remove dead helpers, unused fakes, unused imports, and empty stubs.
- Keep normal tests local and deterministic. Do not add live-service or Docker requirements to the default suite.
- For non-trivial public classes with protocols, test the protocol behavior
  rather than concrete private state.

## Review Checklist

When reviewing tests, flag the test if the answer to any question is "yes":

- Would this test pass if the behavior were wrong?
- Would this test fail only because a helper was renamed or a log line changed?
- Is it asserting on private state, call counts, or internal dispatch?
- Does it duplicate the implementation instead of checking an independent
  oracle or observable behavior?
- Does it only mirror a scalar or config guard without a reported regression or
  compatibility-critical public contract?
- Does it pin an exact dependency version, default, or serialized config detail
  instead of the compatibility behavior that matters?
- Is the mock inside the system under test rather than at an external boundary?
- Does it sleep, skip permanently, or lack a real assertion?
- Did the change weaken a numerical tolerance or test expectation without justification?
- Does it ignore AGENTS.md or this policy for fakes, mocks, commands, optional dependencies, or integration boundaries?

Ask for low-value tests to be deleted or rewritten. More tests are not better
when they pin implementation details and miss real regressions.
