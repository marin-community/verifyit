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

| mode | contract | empty or absent candidate contract |
|---|---|---|
| `mcq` | expected option letter | `empty_output`; no option still scores zero |
| `math` | expression equality through math-verify | `empty_output`; an absent expression cannot match |
| `numeric` | numeric equality with explicit tolerances | `empty_output`; no number scores zero; numeric zero is data |
| `exact` | normalized equality or single-reference substring | `empty_output`; explicit `grade` permits an intentionally empty expected string |
| `json-schema` | JSON, YAML, or TOML checked against JSON Schema | `empty_output`; decoded null and empty collections follow the schema |
| `xml-elements` | required elements and attributes | `empty_output`; an empty document is invalid XML |
| `csv-columns` | required header columns | `empty_output`; missing columns fail, a valid header-only table can pass |
| `ifeval` | deterministic constraints | `empty_output`; explicit `grade` evaluates constraints against empty text |
| `reasoning-gym` | named scorer and trusted entry | `empty_output`; explicit `grade` delegates empty text to the scorer |
| `stdio` | program stdout over hidden cases | empty stdout may match an explicit empty expected output; failed execution cannot pass |
| `pytest` | required and protected tests | no collected tests or missing/malformed report cannot earn reward |
| `junit` | JUnit XML report | absent or empty test reports cannot earn reward |
| `gotest` | Go test events | absent tests or incomplete events cannot earn reward |
| `judge` | reference, checklist or final-label rubric | `empty_output`; explicit `grade` sends present empty text to the configured rubric |
| `script` | declared verdict or scalar reward producer | missing/malformed reward is failure; no implicit empty reward |

Every answer-file spec has an explicit typed `empty_output` policy. Parsing an omitted
policy materializes `zero`, and rendering always writes it. `zero` gives a present empty
or whitespace-only file the minimum score. `grade` passes that text, unchanged, to the
mode's validated task contract. It never supplies a fixed abstention reward or judge label.
A missing file stays minimum under either policy; provider failures and incomplete judge
responses remain infrastructure failures. The five execution/report modes use their
artifact contracts in the table instead of an answer-file policy.

This policy concerns submitted text, not trusted references or decoded truthiness. Missing
or malformed required references remain invalid tasks. A JSON document containing `null`,
`[]`, `{}`, `0`, `false`, or `""` is a present document; its schema decides whether it is valid.
Direct text-candidate APIs honor the same policy, while already-decoded JSON values retain
schema semantics. Clients must preserve absent or incomplete transport as failure instead
of converting it into a present empty answer. For example, an abstention task may set
`empty_output = "grade"` and let a completed judge label map to 0.5; a missing response or
unfinished reasoning block is not a valid abstention.

For `judge`, a length-truncated or content-filtered judge response is an infrastructure
error. Only explicit `finish_reason="stop"` completes grading; tool requests and missing or
unknown reasons also fail closed. A completed response with no parseable score is retried once; if the retry
also fails, the verdict is `infra_error`. These failures write no reward files.
The last nonempty response line must be a complete `SCORE: value` label: reference accepts
`0`, `0.5`, or `1`; checklist accepts `0` or `1`. Numeric prefixes and other labels fail closed.
The opt-in `labels` rubric supplies one reference, trusted `system_prompt`/`prompt_template`
strings using only `{question}`, `{reference}` and `{candidate}`, and a nonempty
`label_scores` table of finite rewards in `[0, 1]`. Its final line must exactly name one
configured label; contradictory labels in the answer invalidate the result.
`label_scan = "lines"` recognizes only completed label lines for bare labels such as
`A`/`B`/`C`, leaving letters inside explanatory prose alone; the default `literal`
scan remains unchanged. `label_scan = "whole"` requires the entire answer to be one label;
`label_case = "upper"` uppercases both labels and replies, rejecting colliding configured labels.
The default case policy is `sensitive`. For the labels rubric, `api = "responses"` selects
Responses instead of the default `chat_completions`: `max_completion_tokens` becomes
`max_output_tokens`, `reasoning_effort` becomes `reasoning.effort`, and temperature is omitted.
Only a completed response containing one completed assistant text message is accepted;
reasoning metadata is never graded, and refusals, tool output and ambiguous JSON fail closed. Optional
`strip_reasoning_blocks` removes completed think/thinking blocks before label parsing.
Unfinished reasoning, malformed labels, HTTP errors and non-completed responses are
infrastructure failures with zero reward; label judging does not retry HTTP failures.
`incomplete_retry_tokens` permits one larger budget only after length truncation; it does not retry malformed labels. Successful
label verdict detail retains the complete judge response in `completion`.

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
Pytest `batch_size` splits selected paths into separate invocations (`0` runs one invocation).
The timeout covers restoration, setup and all batches; a later execution error cannot retain
partial credit. Failed or skipped repeated tests cannot be overridden by an earlier pass.
`id_matching = "exact"` is the default. `"unique_prefix"` also accepts uniquely matching
bracket-truncated parameter IDs and Unicode-escaped IDs; ambiguous or overlapping aliases fail.

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

The `reasoning-gym` spec optionally accepts `params`, a JSON object file beside the spec.
It preserves configured dataset scoring; omitting it retains the default scorer.
The optional extra requires reasoning-gym >=0.1.25, whose registered config dataclasses
are validated before the public dataset factory runs. Invalid configuration is an invalid
task; dataset construction failures remain infrastructure errors.

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

Clients holding answer text can call `grade_judge_candidate` from
`verifyit.modes.grade_judge` with the same `JudgeSpec`. Pass a runtime-only
`JudgeConnection(base_url, api_key)` to avoid changing process environment
variables or serializing credentials into task specs. This helper returns a
`Reward`; invalid tasks and provider failures raise, so clients must abort the
batch rather than aggregate partial success. Clients close on success or failure.
The spec's `empty_output` policy applies to direct candidates. File-based grading
still scores missing output artifacts zero, independently of empty-string policy.

For decoded paired judge ratings, install `verifyit[judge,schema]` and call
`grade_paired_ordinal` from `verifyit.modes.grade_judge`:

```python
from verifyit.modes.grade_judge import grade_paired_ordinal

verdicts = grade_paired_ordinal(
    2, [(0, 1)],
    [{"left": 0, "right": 1, "score_left": 5, "score_right": 2, "ranking": 1}],
)
```

The trusted cohort must have at least two responses and directed edges covering
all responses, without self edges or duplicates. Opposite directions are distinct.
Provider records must match those edges in order, exactly once. JSON integer-valued
indices are accepted; booleans are rejected. Default rating bounds are 1–5 and
ranking bounds 1–6. Equal ratings receive opposite adjustments of `3.5 - ranking`;
each response receives the mean of its incident ratings. Rewards are normalized to
[0, 1], while `detail["raw_score"]` and `detail["raw_bounds"]` retain the native
scale (default −1.5–7.5). Invalid trusted contracts raise `InvalidTask`; malformed
provider cohorts raise `RuntimeError`. Abort the entire affected batch at minimum
reward on either failure, before applying any framework reward shaping. This API
does not call a provider or introduce another verifier spec.

`summarize_log_likelihoods(likelihoods, normalization_lengths=...)` from
`verifyit.modes.grade_mcq` reports corpus mean log-likelihood, perplexity and bits
per supplied unit. Supply positive integer word, byte or token counts matching the
task; the helper divides total log-likelihood by total counts in source order.
These are unbounded diagnostics, not Rewards or a new mode. Model log-likelihoods
must be finite and nonpositive. Missing data, invalid counts and unrepresentable
statistics raise `InvalidTask`; callers must abort reporting rather than substitute
a favorable zero.

Clients with already normalized tokens or canonical labels can call
`grade_collection_f1(reference, candidate, multiplicity=..., empty_reference=...,
round_digits=...)` from `verifyit.modes.grade_exact`. Both inputs are sequences or sets
of strings. Choose `multiplicity="set"` to ignore repeats or `"multiset"` to
count occurrences; tokenization and normalization remain the caller's responsibility.
Choose `empty_reference="zero"` for tasks defining empty references as zero, or
`"invalid"` to reject them. Empty or malformed candidates score zero; malformed
references raise `InvalidTask` before candidate scoring. Each input is limited
to 10,000 items and 1,000,000 characters. `round_digits=None` preserves the
unrounded overlap score; integers from 0 through 6 request binary64 scaled,
ties-to-even decimal rounding. The unrounded calculation uses
`2 * overlap / (reference_count + candidate_count)` and can differ by floating-point
roundoff from an equivalent precision/recall calculation. This direct API leaves
Exact specs' equality behavior unchanged.

`grade_collection_precision_interval(reference, candidate, minimum_percent=...,
maximum_percent=..., multiplicity=..., empty_reference=...)` uses the same prepared
collections, multiplicity policies and limits. It scores one when
`overlap / candidate_count * 100` lies within the inclusive finite, ordered bounds.
Bounds accept finite Python integers or floats and may extend outside 0–100 to
express a tolerance around an endpoint; integers are compared without a float cast.
`empty_reference="zero"` gives a valid nonempty candidate zero precision;
`"invalid"` rejects an empty reference. Malformed or empty candidates always score
zero, even when the interval includes zero. A valid disjoint candidate can pass
that interval. Tokenization remains the caller's responsibility.

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

`MathSpec.allow_additive_constant` is an opt-in equivalence policy for finite scalar
expressions. After ordinary equality fails, a simplified difference with no free
symbols and a proven finite value counts as equal. Multiplicative factors, collection
differences and nonfinite constants do not qualify. Existing parsing profiles, exact
comparison and defaults remain unchanged; backend deadlines fail closed.

The opt-in math `raw` profile preserves an unwrapped prediction for expression and
LaTeX extraction, while parsing the reference as boxed LaTeX. A final box still
takes precedence and a malformed final box scores zero. Unlike the default profile,
it does not wrap bare symbolic text to make it parse. A reference that yields only
an unparsed string is an invalid task. Additive fallback in this profile uses
LaTeX extraction only.

Clients can grade prepared text with `grade_ifeval_candidate` from
`verifyit.modes.grade_ifeval`. Its optional `registry` supplies additional trusted
checks without changing global registrations or overriding built-in names.
Direct text grading follows the spec's `empty_output` policy. Keyword existence
and forbidden-word constraints accept `word_boundary = false` in their params
for case-insensitive substring matching; the default keeps whole-word matching.

`canonical_math_members` from `verifyit.modes.grade_math` prepares finite exact
constants as delimiter-safe strings for Exact scalar or multiset comparison.
It rejects symbolic variables, nonfinite values and approximate compound
expressions. Run preparation inside `verifyit.bounded.call_bounded` so parsing
and simplification share a process deadline; it does not implement approximate
numeric equivalence.
