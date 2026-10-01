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
reference construction at grading fails closed. `keywords:exclude_word_harder`
uses an explicit keyword deterministically; when omitted, its hidden word must be
resolved before candidate generation. The preparation patch below handles new
references, while legacy hidden state cannot be recovered. Meaningful
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

Apply `math-judge-verifyit.patch` after `instructions-verifyit.patch` and the
dependency patch last. This adds opt-in partial terminal scoring for math-with-judge
and NS-tools with existing MathSpec, JudgeSpec and a total ScriptSpec deadline.
The bounded trusted reference domain and two missing external judge transcripts
remain explicit gaps; neither source route is promoted to complete integration.
See [the contract and evidence](math-judge.md).


Apply `judge-profiles-verifyit.patch` after `math-judge-verifyit.patch`, with the
dependency patch last. `verifyit_enabled = true` wires abstention, MultiChallenge
and all four jailbreak policy routes through existing ExactSpec and JudgeSpec
primitives under a total ScriptSpec deadline. Source clients retain answer
extraction, prompt wording, rubric averaging, policy composition and feedback.
Abstention's normalized `[IDK]` receives 0.5 without a model request; other answers
use complete-line A/B/C labels. MultiChallenge and jailbreak retain bracketed
labels. Judge failures discard the entire composite reward.

Nineteen source parity and failure tests pass, including literal braces in
conversation context and partial-credit failure handling. Thirty-six frozen
archived traces across six routes match pinned-native and installed verifyit
scores and rewards. Archived external judge text is served by exact source
message keys over local HTTP, without fresh model generation; every cutover
trace records actual child primitive verdicts. Evidence and rerun commands are
in `evidence/e2e/wiring/skyrl-judge-family/`. The dependency pin includes
complete-line label parsing and rejection of malformed direct ExactSpec
reference containers.


Apply `dormant-judges-verifyit.patch` after the judge-profile patch to enable
`verifyit_enabled=True` on the exported BrowseComp, RULER and STEM judge APIs.
BrowseComp and RULER preserve source requests and response schemas, then grade
raw external JSON through JSONSchemaSpec and ExactSpec. Duplicate fields,
nonfinite numbers, truncated responses and malformed schemas abort grading.
STEM preserves its request and exact-match branch, but requires a complete final
decision line and rejects contradictory decisions. Its existing error boundary
returns zero. These are core-primitive integrations with 17 source tests and six
HTTP roundtrips; no eligible archived trace exists in the local census.

Apply `genrm-cohort-verifyit.patch` next, with the dependency patch last. The
Nemotron runner forwards `verifyit_enabled` into GenRM configuration. Both
GenRM routes execute the source cohort scorer inside a trusted ScriptSpec child;
this is a retained-runtime integration, not independent per-response judging.
The child preserves circular pairing, comparisons, tie breaking and length
shaping, and returns the complete finite reward vector plus cohort metrics.
ScriptSpec's scalar zero is an execution envelope; training consumes the vector,
whose values may exceed one. Invalid comparisons, incomplete transport, malformed
vectors and total-deadline failures discard the whole cohort.

Thirteen GenRM source tests and six cohort HTTP roundtrips cover both transport
formats and tie/length policies. The evidence exercises the actual group scorer,
not training-loop initialization or model generation. No archived comparison
cohort is available. Exact installed-package proofs and source-patch manifests
are under `evidence/e2e/wiring/skyrl-dormant-judges/` and
`evidence/e2e/wiring/skyrl-genrm/`.


Apply `instruction-preparation-verifyit.patch` after the cohort patch. The three
Nemotron source builders accept `instruction_reference_seed=<integer>` to resolve
registry defaults in an isolated process before candidate generation. Prepared
records contain the resolved kwargs, seed and pinned registry revision. The
resolver rebuilds each checker and requires identical state with no additional
random sampling. The later runtime patch transfers trusted source RNG state for prospective legacy grading; missing historical state still cannot reproduce old random choices.

The source client corrects three reference-construction defects: a supplied zero
span index was treated as missing, the paragraph sampler could select an index
past the last paragraph, and two generated keyword defaults were lists instead
of strings. Sixty-eight source tests and twelve actual environment roundtrips
pass; all 54 default constructors resolve and pass admission with required text
inputs. This preparation audit does not recover historical hidden references. The later
runtime patch integrates source registry construction at the grading boundary. Reproduction
scripts and the complete constructor audit are in
`evidence/e2e/wiring/skyrl-instruction-preparation/`.

Apply `math-reference-contract-verifyit.patch` after the instruction preparation
patch and before the dependency pin. Each public Nemotron source builder accepts
`math_reference_kind="semantic"` or `"symbolic"`; the trusted choice is serialized
before candidate generation. Semantic references use validated nonempty text and
the original symmetric judge prompts. Symbolic references require successful math
parsing. Existing explicit row metadata is preserved; conflicting contracts fail
preparation. The later hybrid-reference patch extends the pinned source policy to untagged
legacy text contracts. Sixteen prepared framework roundtrips match source scores
and HTTP requests, including the exact installed package. The corrected frozen 18-archive replay matches all recorded scores; the two
previously reported missing transcripts were nested in multi-turn diagnostics. See [the contract](math-judge.md).

Apply `coder1-protocols-verifyit.patch` after the math reference contract patch and
before the dependency pin. It adds bytes value transport and common numeric
protocols, including in-place mutation, without moving trusted assertions into
candidate execution. Sixty-nine source tests pass and twelve actual GeneralReact
witnesses agree across native, cutover and exact-installed execution. Coder1 remains
partial for arbitrary Python interoperability; see [the contract](coder1-partial.md).

All 45 wired scoring routes now have actual source-boundary cutover witnesses:
30 have real trace replay and 15 have source fixtures. The last five fixture gaps
were GSM8K multi-turn, search, searchcode, legacy text2sql and SWE-pivot tool
comparison. Each now has three registered Env terminal-grading cases matching
pinned native and independent manager execution, with raw verifyit calls. This
covers terminal grading, not retrieval, tool execution or SWE Harbor preparation.
Evidence is in `evidence/e2e/wiring/skyrl-route-witnesses/`. Coder1 remains partial and outside the complete tested-route count.

Apply `math-hybrid-reference-verifyit.patch` after the coder protocol patch and
before the dependency pin. Legacy text references retain the original symmetric
judge contract; unexpected parser failures remain unscored zero. Forty-seven
source regressions, twelve actual Env fixtures and all eighteen frozen archived
roundtrips pass, including independent manager and exact installed-package runs.
See [the math contract](math-judge.md) for the transcript correction and evidence.

Apply `instruction-runtime-verifyit.patch` after the hybrid math patch and before
the dependency pin. ScriptSpec executes the pinned instruction registry through
actual IFEval predicates. The client captures Python RNG state at the source
grading boundary and accepts the child state only after validating the complete
scored feedback. Failure returns minimum reward without committing partial state.
All constructor randomness uses Python random; language detection has a separate
fixed detector seed on both native and cutover paths. That seed is an explicit
source reproducibility correction, not unchanged historical detector behavior.

Seventy-six regressions, twenty actual Env fixtures and fifteen frozen archive
roundtrips pass, including independent manager and exact installed-package runs.
The fixtures cover omitted/None/empty defaults, signed nonempty copy spans and
language detection, with identical source/cutover rewards and final RNG state.
The 403-case audit spans all 54 registry entries: 302 constructors accept inputs,
279 preserve admitted checker/RNG state and 23 malformed or vacuous contracts
remain rejected. Constructor acceptance alone is not a positive scoring proof.
Each admission difference includes actual source predicate outcomes. Historical
records without their RNG/detector state remain unreproducible; they are not
classified as missing verifier dispatch. Evidence and the 25-patch manifest are
under `evidence/e2e/wiring/skyrl-instruction-runtime/`.


### Empty abstention correction (#891)

Apply `empty-abstention-verifyit.patch` after the existing judge-profile client
patches, and install verifyit at `cd00ed59e9c3fe99fd3460ae7c7df9e5ee60a811`
or later. The existing published SkyRL dependency pin is unchanged by this
export. Present empty final answers explicitly use `empty_output = "grade"`
and reach the original judge; its C label yields 0.5. Missing artifacts,
malformed provider replies and null actions remain failures at zero. Unfinished
reasoning is rejected at zero before extraction can turn it into an abstention.
There is no unconditional reward for empty output.

Six actual `NemotronUltraEnv.step` roundtrips include exact source HTTP and
feedback parity for empty, whitespace and completed-reasoning answers, plus
incomplete-reasoning, empty-provider and null-action failure cases. The manager
independently replayed all six; 29 client regressions pass. These new cases are
local HTTP fixtures, alongside the existing archived judge-family evidence.
See `empty-abstention-provenance.json` for source and patch hashes and
`evidence/issues/skyrl-891/env-manager/roundtrip.json` for raw verdicts.
This restores tested exported coverage, not deployment on current SkyRL main.


### Stateful indirect prompt injection (#890)

Apply `indirect-prompt-injection-verifyit.patch` after the complete existing
client patch stack, including `empty-abstention-verifyit.patch`. The new route
uses the existing structured rollout evidence, pinned NeMo Gym tool handlers
(7a19900a114f8c349c9fac031b016575e39cfa36), and verifyit's exact comparator.
Enable `verifyit_enabled` to compose safety with required-tool utility. The
source handlers retain Apache-2.0 notices. This export does not update the
published SkyRL dependency pin or deploy the route to SkyRL main.

The original SkyRL registry accepted IPI rows but had no implementation.
Validation therefore compares the pinned NeMo pure scoring helper and its
safety-times-utility formula against verifyit, then runs actual registered
SkyRL episodes. The 2,000 MOPD rows cover seven domains and 37 verification
types; all pass reference preflight and 4,000 matcher comparisons. Twelve
completed fixture episodes use three frozen source rows. Three selected saved
model prefixes remain unavailable at their recorded boundary; added terminal
turns are fixtures, not completed archived-score parity. Full NeMo HTTP server
execution and all nine domains in the separate public dataset are not claimed.

Malformed tool arguments, refusal envelopes and unfinished five-turn episodes
return zero. Tool reads alone cannot earn a terminal reward; later steps cannot
revive a terminal failure. Five independent manager scenarios confirm positive,
missing-read, length, refusal and exhausted-turn outcomes; 14 durable tests
cover structured rollout, termination and task-reference behavior. The unfinished-turn and
refusal checks deliberately tighten the source completion contract. See
`indirect-prompt-injection-provenance.json` for exact patch, source and evidence
hashes; raw traces remain in the campaign evidence directory.
