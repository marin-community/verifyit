# verifyit

`verifyit` grades task outputs against declarative specifications. It supports answer checks,
structured-output validation, executable tests, and model judges. The task supplies a flat `tests/verifier.toml`; `tests/test.sh` contains this shim:

```sh
exec verifyit /tests/verifier.toml
```

The command writes `/logs/verifier/verdict.json`:

```json
{"reward": 1.0, "status": "scored", "detail": {"extracted": "C"}}
```

Statuses are `scored`, `invalid_task`, and `infra_error`. A scored result also writes
`/logs/verifier/reward.json` and `/logs/verifier/reward.txt` for the
[Harbor task runner](https://github.com/marin-community/harbor). Invalid tasks and infrastructure failures omit those reward files,
so the trial can be masked instead of recorded as a zero. Candidate output never causes a nonzero
process exit after a verdict has been written.

Rewards must be finite numbers in `[0, 1]`; malformed grader rewards or statuses become
`infra_error` with reward zero. Persisting malformed verdict details also replaces any previous
verdict with this failure and removes stale reward files. Source metrics and training reward
shaping belong in the client rather than this bounded correctness scalar.

## Modes

| mode | contract |
|---|---|
| `mcq` | expected option letter |
| `math` | expression equality through math-verify |
| `numeric` | numeric equality with explicit tolerances |
| `exact` | normalized string equality; optional single-reference substring containment |
| `json-schema` | JSON, YAML, or TOML checked against JSON Schema |
| `xml-elements` | required XML elements and attributes |
| `csv-columns` | required CSV header columns |
| `ifeval` | deterministic instruction-following constraints |
| `reasoning-gym` | the named reasoning-gym scorer and entry |
| `stdio` | program stdout over hidden cases |
| `pytest` | pytest JSON report with required and protected tests |
| `junit` | JUnit XML report |
| `gotest` | `go test -json` events |
| `judge` | reference-answer or checklist rubric through a configured model endpoint |
| `script` | legacy `test.sh` fallback with normalized reward files and fail-closed errors |

For `judge`, a length-truncated or content-filtered judge response is an infrastructure
error. Only explicit `finish_reason="stop"` completes grading; tool requests and missing or
unknown reasons also fail closed. A completed response with no parseable score is retried once; if the retry
also fails, the verdict is `infra_error`. These failures write no reward files.
The last nonempty response line must be a complete `SCORE: value` label: reference accepts
`0`, `0.5`, or `1`; checklist accepts `0` or `1`. Numeric prefixes and other labels fail closed.

For `stdio`, a candidate program that exits unsuccessfully scores zero even if its stdout matches.

For `script`, a nonzero producer exit is an infrastructure error even when it writes a positive
reward. Optional `verdict_file = "result.json"` declares an authoritative JSON verdict inside the
private `VERIFYIT_LOGS_DIR`: `status`, finite `reward`, and object `detail`. Status is `scored`,
`invalid_task`, or `infra_error`; unscored reward must be zero. Structured producers must complete
successfully before their timeout. Missing/malformed verdicts never fall back to scalar reward
files or stdout. Native metadata may be placed under `detail.native`; `detail.script` is reserved
for process diagnostics. Scalar-only scripts keep their existing timeout-zero behavior.

JUnit report globs declare output files: matching old files are removed before execution so stale
passing reports cannot satisfy required tests. Report paths must remain inside the workspace.
Interrupted pytest runs, collection errors and incomplete Go test/package event streams cannot
earn positive rewards. Ordinary reported test failures retain required/protected test scoring.
For pytest tasks, `setup_failure_is_infra = true` makes a failed or timed-out `setup` an unscored
infrastructure error with no reward file. Use it for task-owned dependency installation and
environment preparation; the default remains scored zero for candidate-dependent setup commands.

For the `math` and `numeric` grading modes, the last `\boxed{...}` occurrence determines the
candidate when the output contains a box marker. Its braces must be balanced and its content must be
nonempty. Otherwise, the candidate receives reward `0.0`, even when an earlier marker contains the
expected answer. Without a box marker, `math` grades the last nonempty line and `numeric` grades the
last number. Numeric expected values and absolute and relative tolerances must be finite. Tolerances
must also be nonnegative. The effective tolerance,
`max(tolerance_abs, tolerance_rel * abs(expected))`, must be finite.

[`spec.py`](src/verifyit/spec.py) owns the frozen mode dataclasses plus `parse_spec` and
`render_spec`. Spec paths are relative to the directory containing `verifier.toml`. `grade.py`
owns dispatch, output handling, verdict writing, and the CLI. Executable graders live in
`modes/grade_*.py`; shared parsers and process runners remain separate.

## Install and use

```bash
uv tool install --python ">=3.11" \
  "verifyit[answer] @ git+https://github.com/marin-community/verifyit@<sha>"
```

Replace `<sha>` with a commit SHA from this repository to pin the installed verifier.
For library use in a Python project, run:

```bash
uv add "verifyit[answer] @ git+https://github.com/marin-community/verifyit@<sha>"
```

Extras are `answer`, `schema`, `judge`, `reasoning-gym`, and `all`. Execution modes use the task
image's toolchain.

A minimal `tests/verifier.toml` checks a candidate answer:

```toml
mode = "exact"
expected = ["hello"]
```

Write the candidate to `/app/answer.txt`, then run the shim above. To use local directories:

```bash
mkdir -p app
printf 'hello\n' > app/answer.txt
verifyit tests/verifier.toml --workspace app --logs-dir logs/verifier
```

Answer modes read `/app/answer.txt` by default; `--workspace` relocates that default. A spec's
`output` field can select a different candidate file. Execution modes run in the workspace.
The Python API returns a verdict without writing reward files:

```python
from pathlib import Path

from verifyit.grade import grade
from verifyit.spec import parse_spec

tests_dir = Path("/tests")
spec = parse_spec((tests_dir / "verifier.toml").read_text())
reward = grade(spec, tests_dir=tests_dir, workspace=Path("/app"))
```

For development, see [CONTRIBUTING.md](CONTRIBUTING.md),
[AGENTS.md](AGENTS.md), and the [repository skills](.agents/skills).
Run the package checks from the repository root:

```bash
uv sync --locked --all-extras --group test
uv run pytest tests
infra/pre-commit.py --all-files
uv build
```

## Source history

This repository was extracted from [`lib/tasktrove-verify` in Marin](https://github.com/marin-community/marin/tree/9c2d1a0be3cd1b7d71f8af3b22231038acb213e9/lib/tasktrove-verify).
The package's commit history and author attribution are preserved. The standalone package,
Python import, and command are named `verifyit`.

Exact specs default to equality. `substring = true` explicitly grades whether one
nonempty normalized reference occurs in the candidate. Multiple references or
a reference emptied by normalization are invalid tasks, even when no candidate
output exists. This option preserves the existing case/whitespace controls;
clients requiring source `lower()` semantics should lowercase their inputs and
set `ignore_case = false` rather than relying on casefold normalization.
