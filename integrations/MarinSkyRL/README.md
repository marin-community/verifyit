# MarinSkyRL integration

Source pin: `91c7a60e85e31b6933ab0ee732125b3338e82b89`. Apply the MCQ,
arithmetic and client-boundaries patches, then `reasoning-mcq-verifyit.patch`,
`tool-comparison-verifyit.patch` and `qa-verifyit.patch`. Apply the dependency pin
patch last. The latter pins the local
verifyit implementation checkpoint and raises the standalone gym Python floor
to >=3.11 and includes the `answer`, `schema`, `reasoning-gym` and `pytest` extras. The source SHA must exist on the remote before external
installation. Do not silently replace a pinned Git dependency with a floating
branch. Regenerate fork locks in the fork's supported environment before use.

The MCQ patch retains source strict first-box extraction and binary reward,
and calls verifyit only for candidate correctness. Arithmetic patches retain
source AIME rational and strict-box equality, signed reward/length shaping, GSM8K final-line
and strict-first-marker equality. The original multi-turn controller retains format reward,
termination, and feedback. Client boundaries also route Search QA EM, rounded chemistry,
and both ARC grid comparisons through exact after source extraction/execution.
Malformed candidate grid cells retain rejection; invalid reference grids and nonfinite
chemistry references now fail closed rather than exploiting Python equality or raising during rounding.
The dependency pin includes the Exact/Math options, expanded client adapters and
fail-closed boundaries used by these patches.
Patched source regressions and verifyit API regression
counts are recorded in [the mapping](../../docs/unification/skyrl.md).

Real registered-environment replay validated 66 randomly selected execution links
from the complete eligible local artifact population: all matched pinned native
results and invoked installed verifyit. The [mapping](../../docs/unification/skyrl.md)
records population scope, one archive producer mismatch, and missing route traces.
GSM8K strict/final-line rejection now calls the client before source reward projection,
so missing markers remain zero while still producing a verifyit verdict.

The [coverage report](../../docs/unification/coverage-gaps.md) tracks eight later
opt-in cutovers. Reasoning Gym and Nemotron MCQA matched nine selected real
traces; the two tool-comparison routes with saved SkyRL Gym traces matched six.
The SWE pivot tool route and two exported QA APIs have no eligible real trace.
The tool comparator uses exact, numeric and JSON-schema primitives for typed
arguments and message actions. It rejects a boolean candidate for an integer
reference, which the source comparator accepts through Python's bool/int equality.
The campaign evidence is under `evidence/e2e/wiring/skyrl-reasoning-mcq/`,
`evidence/e2e/wiring/skyrl-tools/` and `evidence/e2e/wiring/skyrl-qa/`.


Apply `calendar-verifyit.patch` after `reasoning-mcq-verifyit.patch` to enable the
calendar task harness with `verifyit_enabled = true` in Nemotron environment config.
Its trusted ScriptSpec checker preserves valid source schedule semantics and rejects
malformed candidates/tasks with zero. Twelve source tests and three selected real
framework replays pass; evidence is under `evidence/e2e/wiring/skyrl-calendar`.

Apply `sqlite-verifyit.patch` to enable both SQL environments with
`verifyit_enabled = true`. A trusted ScriptSpec checker executes candidate and
reference queries in SQLite, then uses strict exact comparison of independently
canonicalized results. Seeded SQL retains duplicate rows, optional ordering,
six-decimal normalization and the perturbed-database check. Legacy SQL retains
set equality and the source's signed formatting reward. Verifier failures produce
zero before formatting rewards; malformed references are unscored. Both routes
execute candidate queries read-only, an intentional tightening of the legacy
rollback behavior. The checker launches the framework's Python interpreter.

Nine source fixture tests pass. Three randomly selected real `text_to_sql` traces
match recorded and pinned-native results through the registered environment and
verifyit. The complete census contains no eligible legacy `text2sql` trace, so that
route has fixture coverage but no real-trace validation. Inputs, hashes, commands
and results are in `evidence/e2e/wiring/skyrl-sql`.

Apply `lean-verifyit.patch` after the reasoning/MCQ and calendar patches. The
Nemotron opt-in flag routes each proof attempt through ScriptSpec, which executes
the retained sandbox compiler runtime and emits a structured verdict. Source
proof construction, correction prompts and refinement termination are retained.
Compiler errors, sorry and timeouts score zero; incomplete, unknown or truncated
compiler results are infrastructure errors. Six HTTP boundary tests and three
selected real refinement traces pass against pinned-native and recorded results.
Evidence is under `evidence/e2e/wiring/skyrl-lean`.

Apply `code-verifyit.patch` after the reasoning/MCQ, calendar and Lean patches.
The LCB and Nemotron code-generation opt-in routes use ScriptSpec to own execution
and exact comparison. Candidate Python runs in a disposable stateful IPython
sandbox session; reference tests and verifier artifacts remain in the trusted
checker. Configure `sandbox.host` and `sandbox.port` in the source environment.
Trusted runtime imports finish before memory limits; candidate code then runs
under lowered soft and hard limits. The host deletes the session even if the
checker exceeds its total deadline. This intentionally strengthens the source's
mutable soft limit and local reliability guard.

Source last-fence extraction, compiled state across tests, binary/fractional
aggregation and stop-on-failure remain. Wrong answers and runtime exceptions
retain source sentinels; an explicit protocol timeout retains its timeout sentinel.
Lost sessions and incomplete execution produce infrastructure zero, discarding
prior partial credit. Boolean/numeric conflation, nonfinite outputs and unsupported
output types reject conservatively. Source top-level tuple-to-list handling remains.

The unchanged random sample is six real traces whose source extraction rejects
missing code, now through verifyit. Two separately labeled supplemental positive
traces exercise actual sandbox execution and match recorded/pinned-native results.
Twenty-four boundary regression cases have focused passing evidence, including
reference/verdict tampering, state, memory limits, cleanup and protocol errors.
Artifacts are under `evidence/e2e/wiring/skyrl-code`; independent manager replays
are in sibling `manager-code-positive` and `manager-code-random` directories.

Apply `dormant-math-verifyit.patch` for opt-in ToRL, DAPO and PRIME source scoring.
The [math integration notes](dormant-math.md) describe retained extraction/reward
contracts, source-defect corrections, actual source comparison commands and
the absence of eligible archived traces. The pin includes the core math timeout
fix and provides an optional `skyrl-agent[verifyit]` install for these dormant APIs.

Apply `structured-output-verifyit.patch` after the other Nemotron dispatch patches.
Both structured-output agents retain native JSON/YAML/TOML/XML/CSV decoding and
tool extraction, then call the existing JSON-schema candidate API. A private
client dialect selects the pinned OpenAPI 0.9 OAS32 policy and local-only reference
registry; standard validator registrations remain unchanged. Unknown dialects and
nonfinite candidates reject conservatively. Native parse/shape categories remain;
schema violation messages come from verifyit. Configuration and infrastructure
failures produce framework error status and zero reward.

The frozen full population contains 21 real links in five source_id groups;
three selected per group give 15 native/archive matches. Four positive responses
reach schema grading; eleven are rejected by source-owned parsing. An additional
controlled actual-v3 Env valid/invalid pair proves that branch reaches the schema
grader and is not counted as archived evidence. Nineteen source parity/edge tests
pass. Evidence and rerun scripts are in
`evidence/e2e/wiring/skyrl-structured-output`.

Apply `format-verifyit.patch` after `structured-output-verifyit.patch` to wire
citation and freeform formatting. These are source-owned parameterized IFEval
constraint extensions, not built-in comparator coverage. They count matching
lines across regex alternatives or enforce required/allowed marker policies.
Existing IFEval executes and aggregates the constraint; a trusted ScriptSpec child
bounds Python regex evaluation with process-group cleanup. Candidate text is data,
never executable. The client retains exact native matching/missing/spurious feedback.
Invalid or vacuous policies produce configuration error and zero; deadline or
infrastructure failure produces verifier error and zero. Meaningful negative-marker
policies remain supported.

Twenty-nine source parity/edge tests pass. The complete format population has 18
verified links across four groups; three selected per group give 12 native/archive
matches, with an actual child IFEval verdict for every item. The manager independently
replayed both sides and verified before/after vacuous-policy and catastrophic-regex
failures. Evidence is in `evidence/e2e/wiring/skyrl-format/`.

Apply `instructions-verifyit.patch` after `format-verifyit.patch`. The standalone
IFEval route and Nemotron instruction agent register named source-owned predicates
in existing IFEval. ScriptSpec bounds the entire construction/checking operation,
including resource initialization; source clients compose the fraction or binary
reward and retain per-constraint feedback. This is a client registry extension,
not built-in comparator coverage or delegation to a precomputed source score.

The standalone registry has 26 predicates. NVIDIA's 54-class registry is pinned
to `f46a5ac87b1400a4f8973039844b6be9b56e3faf`, with retained NLTK and language
detection dependencies. Predicate results must be actual booleans. Checker,
detector, dependency and deadline failures invalidate the full result rather than
retain partial credit. Malformed, empty, vacuous positive-minimum and randomized
reference construction fails closed. In particular, `keywords:exclude_word_harder`
randomizes its hidden forbidden word even with explicit kwargs and is rejected;
this integration does not claim faithful replay of stochastic references. Meaningful
exact-zero prohibitions remain supported. JSON-format constraints use existing
JSON-schema candidate grading and reject nonfinite JSON.

Sixty source tests cover normalization, predicate parity, binary/fraction rewards
and failure boundaries. The full eligible population contains 29 links in five
benchmark groups; three frozen random links per group yield 15 actual Env replays.
All match recorded and pinned-native scores/rewards (nine ones, five zeros and
one half). Manager replays independently confirm both lanes and actual child
IFEval grading. The final worker replay includes the conservative guards above;
full-registry golden replay is not claimed. Evidence and rerun driver are in
`evidence/e2e/wiring/skyrl-instructions/`.
