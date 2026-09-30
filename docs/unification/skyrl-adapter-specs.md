# Reusable SkyRL adapter contracts

All46 scoring routes map to existing verifyit classes; no new mode category is
proposed. The48 inventory entries also include two external-objective placeholders.
The17 scorer-contract families are source behavior groupings, not mode categories.

The route-level reassessment is disjoint:

| Strategy | Routes | Contracts and concrete composition |
|---|---:|---|
| Client extraction and existing primitives | 17 | Arithmetic4, QA3, MCQ2, ReasoningGym2, ARC grids2, rounded chemistry1, typed tool equality3. Extract source evidence; canonicalize each side independently; exact/numeric compares values; source aggregation retains partial scores. |
| Task-owned executable harness | 6 | Code3 compiles callable/stdin cases into pytest/stdio; SQLite2 executes trusted fixture/reference and candidate queries in isolated test harness; Lean1 compiles candidate proof through script. These are task harnesses, not a generic retained scorer callback claimed as primitive equivalence. |
| Existing-class extensions | 23 | Math5, structured schema2, instruction/format/calendar5, rubric/cohort judge11. Extend four existing classes as specified below; keep source extraction, retries, orchestration and metrics in clients. |
| External objective, no correctness verifier | 2 | Preference/prompt-only retain their external reward objectives. |

Nine source routes now have executable integration patches: AIME normal/strict,
GSM8K standalone/multi-turn, Search, SearchCode, MCQ, chemistry, and both ARC routes.
The shared exact option `strip_outer_whitespace=False` removes the strict-literal
gap. Source imports retained only for extraction, execution and metrics are client
code; unchanged source scorer callbacks behind script remain runtime bridges only.

For every composition, a malformed reference is `invalid_task`; unavailable or
broken verifier infrastructure is `infra_error`; neither receives format or partial
credit. All failures carry scalar zero and remove stale rewards. A valid wrong
candidate may receive only its explicitly declared source partial/format score.
Source AIME signed score and length shaping, cohort bonuses, and diagnostic vectors
stay outside the bounded verifyit correctness scalar. Aggregation first checks all
constituent statuses: any failed required verifier makes the whole result unscored
zero before averaging, multiplying, selecting alternatives, or applying shaping.

Per-test evidence retains stable `id`, `passed`, exact `stdout`, `executed`, `total`,
and `complete`; partial execution sets `complete=false`. Clients cannot reconstruct
identity-aware weighting or missing evidence from a scalar reward.

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

## Remaining extensions of existing classes

These are concrete extension specifications, not implemented APIs or new modes.

- **math**: expose a prepared-candidate scorer; retain source extraction and symbolic
  backend selection. Optional equality policy `up_to_constant` compares a derivative
  of the expression difference with zero for declared indefinite integrals. Approximate
  pi substitutions happen independently before grading. Clients compose symmetric
  judge fallbacks and source retry limits; disagreement or failed required call is zero.
- **json-schema**: accept an explicitly declared OpenAPI dialect/validator policy in
  the existing schema mode. Client XML/CSV deserialization uses schema-directed coercion;
  JSON/YAML/TOML remain native formats. Preserve nullable/union and array semantics;
  invalid schema fails before candidate validation. No inference that OpenAPI and
  JSON Schema acceptance sets are interchangeable.
- **ifeval**: expose a prepared-text constraint scorer with a trusted, pinned checker
  registry and explicit aggregation `all`/`mean`. Add line-regex, required/spurious
  marker and structured-calendar constraint checkers. Clients retain JSON extraction,
  kwargs, source registry lookup and calendar evidence; registry/configuration failures
  cannot become satisfied constraints or partial credit. Existing check names keep
  their default semantics.
- **judge**: extend the existing class with task-owned prompt templates, complete
  output-label grammar and a finite label-to-score table; labels must consume the final
  source-defined verdict field, never a numeric prefix. Clients invoke this prepared
  judge once per rubric/pair, retain source prompts and bounded retry policy, then
  compute average/product/first or cohort metrics only from valid scored results.
  No custom prompt uses reference exact-gating implicitly. Missing/malformed/incomplete
  judge output is infra zero. Template/label configuration errors are invalid tasks.

Typed tool equality needs no new class: compare key sets, list shape, type tags and
string leaves with strict exact; numeric leaves with numeric. A source strict
`abs(delta)<epsilon` is represented by inclusive tolerance
`math.nextafter(epsilon, 0.0)` for finite binary floats. Preserve Python bool/int
source policy explicitly instead of flattening values into JSON numbers. QA F1 is
client token matching plus source overlap/precision/recall aggregation; it is not a
new correctness category. These compositions are specified, not yet source-patched.

<a id="arithmetic"></a>Implemented arithmetic profiles use
`grade_aime_candidate` and `grade_gsm8k_final_line` in `verifyit.adapters.skyrl`.
AIME source normalization and ±1 policy remain explicit. Strict-box mode is implemented in the source patch: extract the last box from the source's last100-character tail
and compare its raw content with the expected string using the shared
[EXACT-HARNESS profile](evalchemy_mapping.md#exact-harness-exact-normalization-and-alternative-references).
Use no stripping, lowercasing, punctuation/digit removal or regex substitutions;
the default exact mode's outer stripping is not equivalent. Preserve one literal
expected answer and zero on missing/malformed box. Acceptance fixtures require
boxed `42` versus expected`42` to pass, boxed ` 42`/`42 ` to fail, exact case to
remain significant, and an answer beyond the last100-character tail to fail.

The implemented GSM8K helper covers the standalone final-line route only.
`gsm8k_multi_turn` uses the first strict `####` marker each turn and literal
ground-truth equality after finite-decimal reference validation: correct earns1.0, formatted wrong earns0.2/max_turns,
missing marker earns0.0. It stops at a correct response or max_turns and otherwise
returns source feedback. The implemented source utility patch retains those per-turn results
and harness policy; it must not call the standalone final-line helper. Acceptance
fixtures require first-correct/last-wrong and first-wrong/last-correct marker pairs,
a well-formatted wrong turn receiving0.2/max_turns, absent markers receiving0,
a correct turn terminating immediately, and max-turn exhaustion terminating after
its last scored attempt. The original turn controller is unchanged; the patched strict utility performs comparison through exact.
<a id="mcq"></a>Implemented MCQ uses source first-box extraction followed by
`grade_mcq_candidate`; Ultra MCQA modes require their own source extraction.
<a id="reasoning-gym"></a>Reasoning Gym uses complete pinned task/entry data and
source extraction followed by the existing native scorer primitive.
<a id="no-verifier"></a>Preference and prompt-only routes carry external objective
or skipped/unavailable state, rather than a deterministic correctness verdict.
