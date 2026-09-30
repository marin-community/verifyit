# Reusable SkyRL adapter contracts

These adapters use existing `script`, `pytest`, `stdio`, `exact`, `math`,
`json-schema`, `ifeval`, `reasoning-gym`, and `judge` primitives. They do not add
verifier categories. The implemented arithmetic and MCQ integrations are described
in [skyrl.md](skyrl.md); this document specifies unimplemented semantic gaps.

Each script adapter receives a task-owned JSON request and candidate evidence file.
The request names a scorer, pinned scorer package/source revision, configuration,
and expected data. Evidence contains final text, structured assistant message,
finish status, and optional workspace artifact path. The Python adapter returns `Reward`: request/reference validation yields
`invalid_task`; missing dependencies, unavailable sandbox/judge/compiler, and
verifier execution faults yield `infra_error`; candidate errors yield `scored`
zero. A task-image script transport cannot currently encode that distinction
through reward files alone, so it must use a surrounding Python adapter to classify
unscored outcomes. The script writes
`reward.json` with a finite bounded `reward` and serializable diagnostics; malformed
request/reference or unavailable execution raises without writing reward. Candidate
parse/type/runtime failures write zero. The harness maps verifier errors to masked
training outcomes and applies source-specific optimization shaping separately.
For binary source scores, preserve verifyit 0/1; project AIME correctness to
`2 * reward - 1` and legacy SQL format failure to -1 only in harness policy.
GenRM remains a vector of source cohort scores, not bounded individual reward.
Per-test evidence contains `id` (stable task identity), `passed`, exact `stdout`,
`executed`, `total`, and `complete`; interrupted or short-circuited runs must mark
`complete=false`. Harbor sibling alignment and identity-aware weighting remain
harness policy and may not be reconstructed from a scalar reward.

A generic source script that merely reports zero on exceptions does not meet this
contract. Runtime dependencies belong in the task image or adapter extra.

| Reusable scorer | Request fields and consequential behavior | Required regression fixtures |
|---|---|---|
| <a id="sqlite"></a>SQLite result equivalence | `schema_sql`, `insert_sql`, `reference_sql`, `order_significant`, `comparison` (`set` legacy SQL or `multiset_6dp` text_to_sql), `perturb_stride`, deadline/result cap. Read-only candidate and reference authorizers; rebuild seed and optional perturbed database; aliases ignored, column count/order retained. Legacy -1 format penalty remains harness projection. | Equivalent query; duplicate rows distinguished in multiset but ignored in set mode; ordered mismatch; hard-coded seeded answer fails perturbation; malformed seed/reference unscored; candidate write, timeout, excess rows scored zero. |
| <a id="typed-equality"></a>Typed structured equality | `expected_action`, selected payload key/name, recursive value/type contract, absolute float threshold with strict `<` comparison. Evidence is the assistant message, not lossy rendered text. Exactly one call when expected; chat expectation requires content and no calls. | Extra/missing key, multiple calls, reordered list, bool versus int source policy, threshold equality rejects, wrong tool name, invalid JSON. |
| <a id="calendar"></a>Calendar constraints | Expected event IDs, duration, min/max time, optional before/after/between/at constraint. Parse first valid object-bearing JSON list; reject think marker; validate expected task first; compare IDs/count, overlaps, windows. | Escaped JSON brackets; duplicate event IDs; touching intervals accepted; overlap rejected; missing fields candidate zero; unknown reference constraint unscored. |
| <a id="schema"></a>Structured OpenAPI payload | `schema_str`, dialect, format JSON/YAML/TOML/XML/CSV, response mode text/tool, tool name/payload key. Pin OpenAPI validator and retain schema-directed XML/CSV scalar/array coercion. Core JSON Schema route allowed only after dialect compatibility check. | Typed XML singleton arrays; CSV nullable union scalar; incorrect tool name/count; malformed candidate zero; invalid schema unscored; valid format whose schema requires unexpected type rejects. |
| <a id="format"></a>Regex and marker constraints | Regex list, minimum matching lines; or expected markers plus patterns identifying spurious markers. Evaluate lines once even if multiple regexes match. | Two patterns on one line count once; absent marker/spurious citation reject; invalid task regex unscored. |
| <a id="rounded-scalar"></a>Rounded scalar equality | Wrapper policy boxed/double-parentheses, property type, expected finite value, last-number extraction inside final wrapper, Python banker rounding. | Half-integer parity boundaries, required wrapper missing, nonfinite values, unsupported task property; numeric tolerance is not an equivalent comparator. |
| <a id="grid"></a>Grid equality / transform execution | Expected rectangular integer-palette grid; text accepts JSON/digit rows and optional box; transform route extracts final fenced code or unfenced `def transform` plus imports and executes on test input with explicit runtime limits. | Ragged/boolean/out-of-palette grids reject; JSON and digit forms equivalent; unfenced import retained; ndarray conversion; candidate exception zero; unavailable sandbox unscored. |
| <a id="code"></a>Code execution | Tests declare stdin/stdout or function name/input/output; candidate code uses final fenced block; explicit source output comparator, binary/fraction scoring, memory/total/per-case limits. Compile functional tests into a task-owned pytest harness. Preserve per-test IDs, results, and completeness. | stdin.buffer; correct output before crash; first-test failure stops binary but fractional evaluates all; function exception; timeout kills child group; memory/output exhaustion; tests malformed unscored. |
| <a id="instruction"></a>Instruction registry | Pinned `verifiable_instructions` or open-instruct registry, ID/kwargs list, binary/fraction aggregation. Validate equal ID/kwargs lengths and task checker availability before execution. Core ifeval mapping requires per-checker equivalence, not just names. | Two constraints with one failure distinguish binary/fraction; missing kwargs/unknown ID unscored; empty response source semantics; language/tokenizer runtime unavailable unscored. |
| <a id="math-judge"></a>Symbolic then symmetric judge | Expected math expression/question, source extraction/normalization, exact/up-to-constant policy, optional approximate-pi values, symbolic backend pin, and optional judge fallback; bounded isolated math-verify; on failure source judge prompt in both answer orders, required last-line verdict; retry only incomplete output with doubled output budget. | Constant-shift antiderivatives versus exact tasks; symbolic timeout; reversed judge disagreement rejects; truncated first call retries; exhausted retries unscored; malformed completed verdict unscored. |
| <a id="rubric"></a>Rubric/policy judge | Explicit prompt templates, accepted labels, label-to-reward mapping, item context, aggregation average/product/first, and optional normalized IDK=.5 branch. | Abstention .5; incorrect 0; correct 1; product differs from average; template label not merely quoted earlier in response; missing endpoint unscored. |
| <a id="cohort"></a>Cohort comparison judge | Full sibling responses and conversation, circular pair generation, source GenRM parser, tiebreaker, bonuses, length penalties, bounded parse retries. This is batch scoring, not an individual grade call. | Pair order/rotation, ties, group size edge, parser retries/exhaustion, reasoning/answer length penalty, missing sibling evidence; maintain separate raw and optimization rewards. |
| <a id="lean"></a>Lean compilation | Task proof prefix/statement, candidate proof, compiler/runtime pin, correction policy owned by harness. Script reports compile result; intermediate failed attempt is unavailable until correction ends. | Valid proof, syntax/type error, timeout, compiler missing, correction round replacement; skip grading still performs Lean refinement. |
| <a id="qa"></a>QA normalized equality/F1 | Target alternatives, source lowercase/punctuation/article/whitespace normalization, last answer-tag extraction, score policy EM/subEM/token F1. Core exact list represents output multiset, so alternatives need explicit iteration. | Article/punctuation equivalence; multiple targets; last tag wins; token multiplicity F1; substring policy separate from EM. |

Preference and prompt-only environments are not verifiers; no fabricated correctness
score replaces their external reward objective. Dormant verifier variants reuse the
contracts above with their own explicitly pinned extraction and comparator policies.
External user-registered environments remain open extension points and cannot be
enumerated from this source snapshot.

Only the implemented MCQ/arithmetic patches and stdio fixes have execution evidence
in this campaign. The table specifies reviewable remaining adapters and their test
requirements; it does not claim those adapters or fixtures are implemented.

## Proposed Python adapter API

The status-preserving transport is an explicit Python function:
`grade_profile(request: Mapping[str, object], evidence: Mapping[str, object], *,
tests_dir: Path, workspace: Path) -> verifyit.grade.Reward`. This API is a proposed
extension, not implemented by the current script primitive. It consumes only
necessary candidate fields; source rollout/tool control stays in the harness.

Validation completes before candidate execution. Unknown profile, absent required
fields, invalid expected data, unrecognized schema/constraint, mismatched test
IDs, and malformed expected queries/proofs yield `invalid_task(message)`.
Dependencies unavailable after valid configuration, process launch failures,
sandbox transport failures, compiler/judge unavailable, malformed judge output,
and incomplete execution evidence yield `infra_error(message)`. A syntactically
bad or incorrect candidate, a candidate subprocess nonzero exit, and an enforced
candidate deadline yield `scored(0, ...)`. A verifier subprocess deadline yields
`infra_error`; classify by which process timed out rather than its exit code.
Successful candidate grading yields `scored(reward, profile=..., diagnostics=...)`.
Source cohort/optimization policies return their separate harness values; they
must not be forced into an individual bounded correctness reward.

The caller receives the returned `Reward` directly, and calls verifyit's existing
`write_reward` only after grading. That function writes `verdict.json`; only
`scored` writes scalar reward artifacts, and an unscored result removes stale
reward files. The adapter does not parse candidate-authored verdict/reward files:
trusted profile code owns evaluation, and subprocess artifacts use a fresh
verifier-owned temporary directory. Candidate stdout is evidence only. Thus a
candidate cannot forge the profile's status by leaving files in its workspace.
Retained legacy reward-file transports remain the current script mode and do not
acquire this proposed API's validation classifications automatically.

<a id="arithmetic"></a>Implemented arithmetic profiles use
`grade_aime_candidate` and `grade_gsm8k_final_line` in `verifyit.adapters.skyrl`.
AIME source normalization and ±1 policy remain explicit. Strict-box mode is a
spec-needed route: extract the last box from the source's last100-character tail
and compare its raw content with the expected string using the shared
[EXACT-HARNESS profile](evalchemy_mapping.md#exact-harness-exact-normalization-and-alternative-references).
Use no stripping, lowercasing, punctuation/digit removal or regex substitutions;
the default exact mode's outer stripping is not equivalent. Preserve one literal
expected answer and zero on missing/malformed box. Acceptance fixtures require
boxed `42` versus expected`42` to pass, boxed ` 42`/`42 ` to fail, exact case to
remain significant, and an answer beyond the last100-character tail to fail.

The implemented GSM8K helper covers the standalone final-line route only.
`gsm8k_multi_turn` uses the first strict `####` marker each turn and literal
ground-truth equality: correct earns1.0, formatted wrong earns0.2/max_turns,
missing marker earns0.0. It stops at a correct response or max_turns and otherwise
returns source feedback. Its proposed adapter must retain those per-turn results
and harness policy; it must not call the standalone final-line helper. Acceptance
fixtures require first-correct/last-wrong and first-wrong/last-correct marker pairs,
a well-formatted wrong turn receiving0.2/max_turns, absent markers receiving0,
a correct turn terminating immediately, and max-turn exhaustion terminating after
its last scored attempt. This route is specified, not implemented.
<a id="mcq"></a>Implemented MCQ uses source first-box extraction followed by
`grade_mcq_candidate`; Ultra MCQA modes require their own source extraction.
<a id="reasoning-gym"></a>Reasoning Gym uses complete pinned task/entry data and
source extraction followed by the existing native scorer primitive.
<a id="no-verifier"></a>Preference and prompt-only routes carry external objective
or skipped/unavailable state, rather than a deterministic correctness verdict.
