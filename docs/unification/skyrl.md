# MarinSkyRL verifier mappings

The inventory in [skyrl.json](skyrl.json) pins revision
`91c7a60e85e31b6933ab0ee732125b3338e82b89`. It records 14 registered environments
(13 individual entries and the Nemotron router), 26 Nemotron agent routes, and
9 dormant verifier routes/library scorers. The IFEval registry has 26 checker
names. Each entry names its dispatch, source file/hash, score contract, primitive,
and required adapter. No new verifier category is proposed.

These are adapter mappings, not claims of identical behavior. Executable task
scorers use `script`, `pytest`, or `stdio` for SQL, Lean, grids, calendar constraints,
function calls, and custom numeric comparators. A script that calls retained source
code remains an adapter. The source's XML/CSV OpenAPI validation is stronger than
`xml-elements`/`csv-columns`. Fractional LCB and cohort GenRM require explicit
aggregation adapters. Source extraction must remain at the boundary: first boxed
MCQ, final GSM8K line, and last answer-tag Reasoning Gym have different policies.

`integrations/MarinSkyRL/mcq-verifyit.patch` replaces the simplest native comparison
with `grade_mcq_candidate` while retaining first-box extraction and all 26 option
letters. It applies cleanly to the pinned source. `dependency-pin.patch` adds verifyit to both the root distribution and standalone
gym at implementation commit `91c55a49599fcdead3475f009e62da4e30ca4f27` and raises
standalone gym Python support to >=3.11. Valid prepared tasks retain 0/1 scores. An invalid expected
letter becomes a task error rather than silently producing zero. The patch includes first-versus-last box, lowercase, missing/malformed boxes, and Z
regressions; all 18 source MCQ tests pass in a disposable patched source copy.

AIME's verified correctness is ±1 and its optimization reward also depends on
length/stop evidence. A verifyit 0/1 score must be projected explicitly as `2*r-1`
in the harness, before applying the existing policy. Preserve evaluation budgets,
raw scores, optimization scores, diagnostics, and skipped/unavailable/error states.
Harbor training additionally needs stable per-test IDs, exact stdout evidence, and
completeness for identity-aware shaping; scalar scores alone do not supply this.

## Recent patch coverage

| Source patch | Edge case | verifyit counterpart evidence or remaining requirement |
|---|---|---|
| `00fcf63` | stdin byte reads | Added `test_stdio_binary_stdin_program_scores_correct_output`; real subprocess passes. |
| LCB/coder1 runtime handling | correct stdout before crash | Added parameterized `test_stdio_correct_output_before_candidate_crash_scores_zero`; both normal and special-judge paths failed before fix, pass after. |
| `22e5bc0` | exact rational AIME value | Existing `test_math_scalar_answers_are_compared_symbolically` covers .5 versus 1/2; the exact rational boundary adapter also covers large-decimal policy, avoiding symbolic broadening. |
| `aa86ee3` | ASDiv integer ratios | Source rational ratio normalization must occur before primitive call; `test_aime_normalized_answer_exact_rational_equivalence` covers equivalent/reversed ratios, zero denominators, huge decimals, and rejected candidate syntax; 17 arithmetic adapter cases pass. |
| `5a7ede7` | standalone final GSM8K line | Numeric last-number extraction is different; `test_gsm8k_requires_exact_value_on_standalone_final_line` covers prose-tail, malformed comma, multiple markers, and exact huge decimals. |
| `0cdccc9` | first boxed MCQ and options >4 | `test_mcq_fifth_option_is_gradable_when_declared` and candidate helper tests cover core range; patched source tests cover first-box extraction and options through Z; all 18 pass. |
| `400f598` | JSON grid and unfenced transforms | Source parser/execution retained; canonical grid exact adapter now implemented.41 actual source parity cases include JSON/digit grids and boolean/float/ragged rejection. Unfenced transform extraction remains source client code, not a new mode. |
| `cdc6600` | truncated math judge retry with larger budget | Source two-call retry policy must remain explicit; real HTTP regressions now reject length/content-filtered SCORE replies as infra_error and remove stale rewards; existing once-only malformed-score retry retained. Source doubled-token retry remains a distinct adapter policy. |
| `fc65842` | binary code short circuit | stdio stops at first failure and existing first_failure/passed tests cover counterpart; functional adapter and fractional mode still need tests. |
| `196143f` | Snowball reasoning stripping, bounded chat output | Provider/harness evidence extraction remains outside string primitive; add boundary tests. |
| `a5df364` | Ultra configuration versus candidate failures | Core verdict statuses cover distinction; each Ultra script must map schema/registry failures to unscored states. |
| `24d567f` | verifier child memory/total timeout | stdio timeout coverage exists; memory/output bounds and functional child parity remain adapter work. |
| `5beb28c` | jailbreak judge examples/verdict format | Custom YAML prompt/parser adapter coverage required. |
| `d8b6e8c` | skip grading while preserving tools/Lean refinement | Harness state contract; no deterministic score should replace skipped/unavailable. |
| `91c7a60` | prepared GSM8K/preference extras | Boundary row normalization required; preference remains external reward model. |

Candidate nonzero exits now score zero in stdio, even with correct stdout. The
19 stdio tests pass. Existing task-supplied special judge crashes/timeouts still
reject candidates, and unavailable command paths still score zero by current
contract; infrastructure classification for those boundaries needs a separate
review before changing it.

`arithmetic-verifyit.patch` routes source-normalized AIME answers and GSM8K final-line
answers through the exact rational adapter. Strict-box extraction and AIME reward
shaping remain in the harness; raw boxed contents now use strict exact options. The utility
also delegates strict-first-marker GSM8K equality while retaining multi-turn source control.
All106 source AIME/GSM8K/Search/MCQ tests pass on a disposable patched copy; arithmetic,
MCQ and client-boundaries patches apply together cleanly to the pinned revision.

The implementation commit is local and has not been published. After publication,
regenerate both source lockfiles before frozen installation. The Git dependency
install and updated lockfiles remain unverified. The machine-readable installation
record in `skyrl.json` supplies the dependency and patch order.

The Ultra `mcqa.py` Markdown answer regex rejects alphanumeric continuation with
`(?![a-zA-Z0-9])`. Core MCQ now applies the same boundary: `Answer: Banana`, `BC`,
and `B2` score zero; valid B punctuation, wrappers, and explanations remain valid.
All three negative regressions failed before the change; 35 MCQ and 9 completion
adapter cases pass afterward.

[Reusable adapter contracts](skyrl-adapter-specs.md) specify request fields, scoring,
failure distinctions, dependencies, and regression fixtures for the remaining gaps.
These are unimplemented specs, not claims of direct primitive equivalence.

An isolated uv installation from the local Git repository at the exact pinned
implementation SHA succeeded and graded real rational/MCQ candidates. This proves
that commit packages the required helpers; it does not prove remote availability
or resolve either complete SkyRL environment.

## Client-first reassessment

The48 entries comprise46 scoring routes across17 contract families and two external
objectives. Calendar joins the client/task-harness group, bringing it to 24 routes.
The other 22 retain existing-class profile or comparator-parity requirements; three
dormant math variants are audits, not proven missing APIs. The current register
separates 30 implemented routes, one partially wired client/harness route still pending and
15 concrete existing-class behavior gaps. Three dormant math routes now have source integrations and fixture evidence. Source
orchestration and metrics stay in clients. No new mode category is proposed; a generic source callback
behind script is only a runtime bridge. The disjoint plan is recorded per entry in
`skyrl.json` and detailed in [the composition contracts](skyrl-adapter-specs.md).

The original nine routes have source patches: AIME (normal and strict), GSM8K, GSM8K multi-turn,
Search, SearchCode, MCQ, rounded chemistry, and inductive/transductive ARC. 52 client
boundary tests pass, and41 cases compare directly against unmodified source scorer
files with checked hashes. Execute the reproducible source parity runner with:

```sh
uv run --with requests --with omegaconf --with func-timeout --with pandas \
  python tools/unification/skyrl_client_parity.py /path/to/pinned/MarinSkyRL
```

Client grid validation matches source candidate parsing, including rejecting boolean
and float cells. Invalid reference grids are now invalid tasks; this intentionally
closes native Python bool/int equality on malformed references. Chemistry preserves
Python banker rounding but rejects nonfinite candidates with zero and invalid
nonfinite references as invalid tasks. Any required verifier failure suppresses
source format/partial/optimization reward. Central Reward validation additionally
rejects invalid scalars/status/details and clears stale verdict/reward artifacts.

The dependency pin includes these APIs. These patches are source-validated. The real-trace replay below validates the locally installed integration; remote publication and full training deployment remain separate.

GSM8K strict task references now must parse as finite decimals. Native ground truth `.`
could previously match `#### .` and earn1; the adapter rejects that malformed task
as invalid_task before applying format reward. For valid references, a source-formatted
wrong marker still retains its declared per-turn format reward.


## Real framework replay

The authoritative artifact census recursively discovers 5,460 verified SkyRL execution
links, including retries. Of these, 3,695 belong to the implemented cutover routes
and contain real task inputs, verifier events, and recorded candidate responses.
Known handwritten smoke tasks are excluded by provenance. There are 22 eligible
benchmark/route groups across AIME, GSM8K, MCQ, chemistry, and both ARC routes.
GSM8K multi-turn, Search, and SearchCode have no eligible recorded execution here.
The remaining 24 observed routes retain the explicit composition/extension contracts
in the inventory; they have no current source cutover and are not counted as replayed.

A fresh seeded selection took three execution links from each complete group before
replay (seed 202609300740; selection SHA256
`40448efd0826308eeeca3a1920b0565028e9d746d00b5e6d5b7fde41a2272e6e`).
All 66 selected cases ran the registered framework environment's actual `step`, then
its verification-contract helper, with installed verifyit from commit
`739d765d89ec1d36df0e16111c28e85d1f0f2a92`. All 66 called verifyit and matched the
unmodified pinned framework's verification score and shaped reward; none raised a
runtime error. ARC used the real local sandbox service. 65 matched the archive.

The remaining AIME case predicts 45 for reference 045. Its archived producer
`0cdccc9229f47c8eadff90aa2033a5b4604266aa` compares normalized strings literally;
the pinned source adds rational equality and therefore accepts it. Its over-budget
flag is diagnostic in both source versions, not the cause of rejection. The pilot
also found an older producer rejecting `\dfrac{14}{3}` against `\frac{14}{3}`;
both source fixes have explicit client regression cases. The earlier parent-index
selection was underinclusive and is retained only as pilot evidence.

Reproducible selection, frozen input hashes, raw outputs, actual module/call records,
source baseline results, and independent manager reruns are stored under the campaign's
`evidence/e2e/skyrl`. Use `replay.py --selection selection-full.json --output NEW_DIR
--mode patched --case TRACE_ID` with the framework worktree's `.venv-replay` and
`PYTHONPATH=skyrl-gym:skyrl-train`. `comparison-full.json` contains final comparisons;
`uncovered-routes.json` records the full-population assessment. Archive labels and
current pinned-source labels are reported separately.


## Later opt-in source cutovers

Twenty-six source routes now have integration patches. Nine later cutovers use
`verifyit_enabled` for Reasoning Gym, Nemotron MCQA and typed tool comparison,
explicit QA entrypoints, and the calendar constraint harness. The source-pinned
register separates these implementations from the remaining 20 routes.

The calendar patch applies after `reasoning-mcq-verifyit.patch`. It retains source
JSON extraction and executes trusted duration, window, ordering and overlap checks
through `ScriptSpec.verdict_file`; it does not call the retained native calendar
scorer. Twelve source tests pass, including five regressions that failed before
hardening. Three randomly selected real executions from 214 eligible links match
both native and archived scores, with independent manager replay retained.

Calendar validation intentionally rejects boolean, negative and nonfinite durations,
invalid clock ranges, reversed windows and malformed reference constraints. Unknown
constraints are checked before candidate window short circuits. Zero-duration intervals
remain valid because the source permits them; touching intervals remain nonconflicting.
Evidence, raw actual framework calls and the frozen selection are under the campaign's
`evidence/e2e/wiring/skyrl-calendar`.

The SQL patch wires both SQL source environments through a trusted ScriptSpec
SQLite runtime and strict exact result comparison. Nine source fixture tests pass;
three selected real `text_to_sql` traces match pinned-native and recorded results.
Legacy `text2sql` has no eligible real trace and remains fixture-validated only.
Read-only candidate execution and malformed/nonfinite reference rejection intentionally
tighten legacy behavior; infrastructure errors never earn signed format rewards.
Evidence is under `evidence/e2e/wiring/skyrl-sql`, including the independent manager replay.

The opt-in Lean patch executes the retained compiler runtime inside ScriptSpec.
Source proof assembly, refinement turns and feedback remain source-owned. Six
HTTP protocol boundary tests pass; three frozen real traces match pinned-native
and recorded results, with actual verifyit calls on each proof attempt. Sandbox
completion is explicit `process_status`; its protocol omits exit codes. The pilot
adapter incorrectly required that absent field; corrected unchanged-selection
replays and the rejected pilot are retained under `evidence/e2e/wiring/skyrl-lean`.

LCB and Nemotron code generation now use a trusted ScriptSpec checker with
isolated stateful IPython candidate execution and strict exact comparisons.
References and verdict artifacts remain outside the candidate sandbox. The six
unchanged random real traces reject missing code through verifyit; two explicitly
supplemental recorded-positive traces execute the sandbox and match native/archive
results. Twenty-four regression cases have focused passing evidence. Immutable
hard memory caps, typed/nonfinite rejection and host session cleanup intentionally
strengthen source behavior. Explicit timeout, wrong-answer and exception sentinels
retain their meanings; lost sessions are infrastructure zero and discard partial
credit. Evidence: `evidence/e2e/wiring/skyrl-code`; independent manager replays are
in sibling `manager-code-positive` and `manager-code-random` directories.

## Dormant math cutovers

`dormant-math-verifyit.patch` wires ToRL and DAPO through `GeneralReactTask.evaluate_result` when the trusted instance sets `verifyit_enabled = true`; PRIME exposes the same explicit opt-in on its exported scorer. Source extraction and pure string normalization remain client owned. Existing exact, numeric and math primitives handle literal answers, percentage alternatives, ordered collections, interval endpoints and matrices. ToRL retains its signed reward and format shaping, while verifier failures receive its minimum -1.

The source boundary suite has 76 tests. Forty-eight benign source/native comparisons record actual primitive module paths, specs and returns; eight intentional source-defect corrections are explained in [the integration notes](../../integrations/MarinSkyRL/dormant-math.md). Candidate-derived eval is removed. These dormant routes have no eligible saved trace in the complete census, so fixtures do not count as archived-trace replay.

Both structured-output agents now use client-only OpenAPI dialect framing with
the existing JSON-schema candidate API. Source XML/CSV coercion, raw date typing,
and tool extraction are retained. The frozen complete population has 21 eligible
links across five benchmark groups; three per group give 15 pinned-native and
archive matches. Four candidates reach schema grading, while eleven reject in
source-owned parsing. A separately labeled controlled actual-v3 Env valid/invalid
pair proves primitive dispatch for that branch. Nineteen source tests cover formats,
dialects, local-only references, tool payloads, and conservative nonfinite rejection.
No core schema extension was required. Evidence is under
`evidence/e2e/wiring/skyrl-structured-output/`.

Citation/freeform formatting now registers two source-owned parameterized IFEval
constraint extensions. This is existing-class extension coverage, not built-in
comparator logic. IFEval owns predicate execution and aggregation inside a trusted
ScriptSpec child with a regex deadline. Native per-line counts and marker feedback
are retained. Twenty-nine source tests and twelve frozen real links pass against
native/archive; manager before/after witnesses prove empty-policy rejection and
bounded catastrophic-regex failure. Evidence is in
`evidence/e2e/wiring/skyrl-format/`.
