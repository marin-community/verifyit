# Evalchemy mapping

## Implemented reassessment

The 42 custom benchmarks now have five clean primitive integrations: GPQA and
MMLU-Pro use MCQ; AIW retains its source normalization and uses strict exact;
GSM8KPerturbed retains extraction/sanitization and uses numeric with zero tolerance.
JEEBench opt-in source extraction/type dispatch composes strict exact option-set
comparison and partial credit with absolute `.01` numeric tolerance; its source
three-repetition metrics remain unchanged. Source fixtures pass, with no matching
archived traces. Malformed references abort the batch; unsupported uppercase
candidate labels are deliberately penalized instead of filtered into a success.
Three benchmarks (AIME24, AIME25, MATH500) share a hybrid integration: native boxed
math parsing/comparison, with source Minerva retained only when parsing extracts
nothing. Parsed non-equivalence never invokes fallback. Parser/verification errors
and timeouts propagate with `raise_on_error=True`, preventing successful fallback
on infrastructure failure. This is a deliberate conservative change from the
source parser's exception-to-empty behavior.

The remaining 34 custom benchmarks can be reframed around existing math, judge,
IFEval, stdio or script modes; implementation/parity remains outstanding. These
are integration/profile gaps, not evidence that 34 new verifier categories are
needed. In particular source-specific judge prompts and instruction registries
need client profiles, while execution/structured metrics need an execution bridge.
Generic delegation remains compatibility-only.

`MathSpec.profile="boxed"` is optional; anchored parsing remains the default.
Boxed missing extraction scores zero with `reason="missing_parse"`, letting the
client explicitly decide its fallback. Anchored invalid references still raise
InvalidTask. `grade_math_candidate` accepts extracted content without imposing
answer-file/last-line extraction. `ExactSpec.strip_outer_whitespace=false` enables
literal source equality without changing existing defaults or sequence semantics.

Five AIW and five numeric source cases passed parity, alongside all 26 real
upstream AIME/MATH500/MMLU extraction regressions. Evidence resides in
`evidence/harness_native/evalchemy_exact_parity.{py,json}` and the patched
validation tree. Both integration patches apply to their pinned checkouts.


Source: marin-community/evalchemy
`e3f4a3d601896c437f37b0bd0a30e51651cce6d0`.
[The generated inventory](evalchemy_inventory.json) covers all 42 custom benchmark
classes discovered by the repository's `*/eval_instruct.py` dispatch convention,
22 local harness YAML overrides and 72 scoring entry points. Discovery indexes
all 4,261 Python definitions under `eval/` in transient evidence, including
normalization helpers whose names do not contain `grade` or `score`. Each record carries source path/hash, inheritance, declared metrics,
scoring calls where defined, primitive candidate, and explicit parity caveats.
Unknown custom benchmark additions fail regeneration rather than silently mapping
to `script`. Static imports and function references are evidence for follow-up;
dynamic dispatch still requires runtime verification.

| Benchmarks | Primitive candidate | Score contract / remaining work |
| --- | --- | --- |
| GPQADiamond, MMLUPro | `mcq` after source extraction | Implemented patch calls `grade_mcq_candidate`; preserve source option shuffle, categories, repeat vectors and standard errors |
| AIME24, AIME25, AMC23, HMMT, MATH500 | `math` | Box extraction and anchors/fallback equivalence need parity |
| OlympiadBench, OlympiadBenchFull, OlympiadBenchDeterministic | `math`, with source judge policy | Preserve deterministic versus judge-fallback distinctions and units; do not add a judge to deterministic variant |
| JEEBench | `exact` + `numeric` | Opt-in source constructor/extraction/evaluator preserves subset credit and three repetitions; malformed references abort, source fixture parity passes |
| GSM8KPerturbed, AIW | `numeric`, `exact` with source normalization | Implemented zero-tolerance numeric and literal exact; five source parity cases each |
| IFEval | `ifeval` | Preserve strict/loose prompt and instruction aggregates; instruction registry parity unresolved |
| IFBench | `script` with original registry | Expanded instruction catalog should remain data/plugin orchestration until shared checker equivalence is shown |
| CodeForces, CodeElo | `stdio` candidate | Preserve case aggregation, tolerances, compilation outcomes, timeouts and contest orchestration |
| HumanEval, HumanEvalPlus, MBPP, MBPPPlus, BigCodeBench | `script` hosting source tests; `pytest` candidate where representable | Preserve sanitization, indentation fixes, execution outcomes and pass@k; avoid collapsing infrastructure failures into wrong answers |
| LiveCodeBench, LiveCodeBenchv5, LiveCodeBenchv5_official | `script` / `stdio` candidate | Shared bounded grader has function-call and stdin contracts; preserve per-case result labels and timeout cleanup |
| MultiPLE, SWEbench | `script` hosting task toolchain | Language execution or repository harness belongs with task; retain tests and container setup |
| CruxEval | `script` | Preserve directional input/output checks and sample records |
| SimpleQA, SimpleQAMini, FinanceBench, HLE | `judge` candidate | Exact prompt/label/retry behavior, not-attempted labels and judge errors need parity; SimpleQA conditional accuracy/F1 cannot be discarded |
| MTBench, WildBench, alpaca_eval, MixEval | `judge` candidate | Multi-turn/pairwise ranking, reference selection and score scales remain benchmark-owned |
| MRCR | `script` | Preserve reference-prefix matching, response comparison score and trial records |
| NUPA-Loose, NUPA5K-Loose | `script` | Exact-match, digit-match and format-validity metrics have distinct denominators; numeric tolerance is not equivalent |
| RepoBench, LiveBench, zeroeval | `script` with source metric bridge | Multiple scorer families and task routing require per-family parity; callable index links their scoring functions |

The [Evalchemy integration patch](../../integrations/evalchemy/README.md) replaces
GPQA/MMLU letter equality with verifyit candidate scoring while retaining source
extraction and all aggregates. Source method execution before/after the patch
produced identical outputs for correct, wrong and missing choices, categories and
repeat metrics. Both integration patches apply cleanly to pinned checkouts, and
patched Python parses. The actual upstream AIME24/AIME25, MATH500 and MMLU-Pro
regression suites pass against the patched validation tree: 26 tests, including
provider completion fields and persisted sample records. The metric bridge for native tasks preserves the source
scorer; this does not establish primitive equivalence for unresolved rows.

Recent patches reviewed and regression consequences:

- `bafdd55` (#186): MMLU-Pro final content overrides tentative reasoning and
  lower-case extracted choices normalize to upper-case. Completion adapter tests
  exercise final precedence and inline reasoning end markers through MCQ scoring.
- `7920acf` (#185): completed reasoning-only math may supply a boxed answer;
  length-truncated reasoning may not. Completion adapter tests cover both and
  final-content precedence. The fork patch retains the source box parser/stops.
- `e80fc88` (#170) and `5becb4e` (#174): mathematical representation equivalence
  and final-answer extraction. Verifyit anchors with `$...$`, whereas Evalchemy
  boxes parsing and falls back to Minerva string normalization; parity remains
  unresolved and is not claimed by the completion tests.
- `9447eed` (#148): indented Plus code and generation limits are task extraction /
  orchestration concerns. Source-hosted test execution must retain dedentation.
- `791d41c` (#150): common bounded LiveCodeBench grader preserves code test case
  outcomes and timeout cleanup. Future `stdio` migration must cover function-call
  cases before replacing the original script.
- `b102201` (#145), `08bcaae` (#144): judge/execution failures remain separate
  trial records; metric projection never turns these records into candidate zero.

No additional verifier category is proposed. The implemented reusable gaps are a
provider completion boundary and a metric-preserving bridge, both independent of
benchmark dependencies. The following contract specifications cover the remaining non-clean mappings.
They extend existing modes; implementation is separate from the current API.


## EXACT-HARNESS: exact normalization and alternative references

Extend `exact` with an explicit `profile="harness"`; retain existing defaults for
other tasks. Inputs are already-filtered candidate strings and one or more
reference strings. Reference cardinality is explicit: `alternatives` means any
reference can match, whereas the existing mode's multiple entries represent a
sequence. Preserve empty strings and every whitespace character at this boundary;
missing candidate artifacts still score zero.

The profile performs `regexes_to_ignore` substitutions in order on both sides,
then optional Unicode `lower`, ASCII punctuation removal, and ASCII digit removal,
in that order. Compare the resulting strings by equality. No implicit stripping,
casefolding, boxing or list splitting is permitted. The existing `ignore_case`
flag selects lowercasing only within this profile. Compile supplied regexes before
scoring; malformed patterns/references are `invalid_task`. Candidate nonmatch is
`scored` zero. Return the source `exact_match` metric and the chosen filter name;
multiple filter chains remain separate outputs.

Evidence: harness `lm_eval/api/metrics.py:exact_match_hf_evaluate` and
`ConfigurableTask.process_results` implement these rules. GSM8K's `strict-match`
uses the first `####` match, while `flexible-extract` uses the last regex match;
retain those extraction chains before calling the shared exact candidate API.

Acceptance cases: `" x "` versus `"x"` must differ; `"Straße"` versus `"STRASSE"`
must differ under lowercasing; empty versus empty must match; the four GSM8K regex
substitutions must run in their source order; any-reference matching must retain
references as alternatives rather than split them into a list answer. Compare
all transformed candidates against the actual pinned source metric function.

## MATH-PROFILES: symbolic and normalization comparators

Extend `math` with a named comparison profile; retain today's symbolic profile
and its invalid-reference behavior. Inputs are an extracted answer string and an
ordered tuple of accepted references. Extraction remains explicit: first or last
box, final-content selection, provider completion status, and stop sequences are
separate from equivalence.

The `boxed-equivalence` profile ports
`eval/graders/answer_equivalence.py:math_answers_equivalent`: normalize the candidate
with the pinned Minerva substitutions; parse candidate/reference inside
`\boxed{...}` using the pinned math-verify engine; when both parses are nonempty,
use its `verify(gold=reference,target=candidate)` result even when false. Only when
one parse is empty may the normalized Minerva comparator run. Any accepted
reference matching produces one. Non-symbolic references remain valid in this
profile; they must not inherit the default mode's `invalid_task` rejection.

Two other reusable profiles cover harness scorers: `hendrycks-normalized` preserves
its ordered string rewrite chain and raw-equality fallback on normalization
exceptions; `minerva-normalized` preserves appendix-D normalization, rational
comparison shortcuts, tuple rejection, symbolic subtraction/simplification and
source timeout behavior. They are distinct named profiles within `math`, not
additional modes. Parser/runtime versions and normalization code hashes are
recorded in the task integration manifest. Missing optional engines are
`infra_error`; task profile/configuration errors are `invalid_task`; valid
unparseable candidates and comparison timeouts follow the selected source profile
and remain scored outcomes. Engine programming errors are not blanket-caught.

Acceptance cases include every upstream MATH500 representation regression:
formatted grouped integers, 0.09 versus 9/100, text answers such as ellipse,
ordered comma-separated answers, matrices, exponent formatting and reordered
algebraic sums. Also test distinct tuple/grouping commas, malformed references,
first-versus-last boxes and parsed-but-unequal pairs that must not use fallback.
Run AIME/MATH500 patched suites and compare candidate/reference cross-products to
the source profile, including a timeout case. Any judge fallback in OlympiadBench
is a separate classifier contract; deterministic variants never invoke it.

## IFEVAL-REGISTRY: official checker profile and result vectors

Extend `ifeval` with a versioned registry profile. The current TaskTrove profile
keeps its existing paragraph/token/language semantics. The official profile takes
`instruction_id_list`, aligned kwargs, prompt, response and an immutable registry
revision. Instantiate each official checker, build its description using source
kwargs filtering, and apply prompt-dependent description updates exactly once as
in the source. Freeze random defaults from the source description phase in the
converted task; missing material arguments without recorded source state are
`invalid_task`, never invented random defaults.

Return four metrics: strict/loose prompt pass and strict/loose ordered instruction
vectors. Strict checks require nonblank response and every registered predicate.
Loose checks OR each predicate across the source's eight response variants:
original, asterisks removed, first/last/both lines removed, and those three line
variants with asterisks removed. Dataset prompt rate averages prompt booleans;
instruction rate pools all instruction booleans rather than averaging per-prompt
rates. A scalar reward key is explicit. Checker registry, tokenization assets and
language detection live in optional extras. Unknown instruction/invalid kwargs
are `invalid_task`; missing dependencies/assets are `infra_error`; a failed
candidate predicate is `scored` zero with its vector retained.

Evidence: Evalchemy IFEval registry/evaluation files and harness
`lm_eval/tasks/ifeval/{instructions,instructions_registry,utils}.py`. Official
paragraphs split on `***`, while current verifyit paragraphs split blank lines;
`combination:repeat_prompt` is absent from the current registry. These differences
require the profile rather than silently changing legacy scoring. The shared
`two_responses` defect is fixed independently: exactly two distinct answers with
no interior empty section, matching the source predicate.

Acceptance cases: run official source tests for every registry class, test `***`
versus blank-line paragraphs, repeat-prompt checks, duplicates/three responses,
strict failure that passes one loose transform, prompt-dependent kwargs, and two
prompts containing different numbers of instructions to verify pooled weighting.
No language-detection or tokenizer approximation may claim official parity.

## JUDGE-CLASSIFIER: explicit prompt and label protocol

Extend `judge` with a classifier rubric configured by a task-owned prompt template,
label parser and label-to-reward table. Inputs are question, references, candidate,
template hash, exact allowed labels, model/endpoint and retry/token budget policy.
Preserve the template bytes, messages, temperature and response parser. Disable
reference/checklist exact gates unless the source explicitly uses them; empty
candidate handling is declared as judge-or-zero rather than inherited implicitly.

For SimpleQA, the template in `eval/graders/simpleqa.py` requests exactly A/B/C;
its parser strips and uppercases the response and rejects other text. Retain raw
response and semantic labels `correct`, `incorrect`, `not_attempted`. A maps to
reward one, B/C to zero, but C remains distinct in metrics. Dataset accuracy,
accuracy given attempted and F1 use source formulas and attempted denominators.
This is not equivalent to today's reference rubric's 0/0.5/1 prompt.

Invalid template/label table is `invalid_task`. Authentication, transport,
exhausted empty completions and invalid judge labels are `infra_error` for the
trial; they remain separate records when other trials succeed. A source judge's
valid negative label is `scored` zero. Optional `openai` dependencies remain in the
judge extra. FinanceBench, HLE and semantic answer equivalence supply their own
pinned templates/parsers through the same profile; MTBench/pairwise evaluations
retain turns/reference orchestration and source aggregators in the metric bridge.

Acceptance cases use the existing local HTTP fixture: A/B/C, lowercase/whitespace,
unknown labels, transient failure, all retries empty, configured model and exact
request prompt. Verify C versus B attempted counts, partial trial failure records,
and source aggregate denominators. No live model is needed or accepted as parity
proof for deterministic transport/parser behavior.

## EXECUTION-CONTRACT: preserve source cases and metric outputs

Executable/custom evaluations use existing `script`, `stdio` or `pytest`
primitives with a declared task adapter. Inputs name the task's trusted scorer,
reference files, candidate artifact, case protocol and resource limits. A scorer
entry point is identified by source revision and function/class path; its
execution environment and optional dependencies belong in the task image.
A candidate source file is installed/restored separately from protected tests.

For stdin cases, map each source input/expected pair to `StdioCase`; retain source
exact/token/float comparison, per-case status and explicit weighting. For callable
cases, serialize positional/keyword arguments and expected return value with a
versioned codec, choose the source import or solution-class entry point, and apply
the source output-comparison protocol. This is an extension to `stdio`'s case
protocol, not a new code-verification mode. If cases require arbitrary source
harness state or toolchains, use `script` with the original trusted grader rather
than infer Python tests from benchmark names.

Every adapter retains code extraction, dedentation, compilation outcomes,
per-case timeouts, process cleanup, numerical tolerance and source test order.
Store all named/vector metrics through the
[metric contract](lm_eval_mapping.md#metric-contract-response-and-aggregation-artifacts).
Pass@k stays dataset aggregation over independently recorded trial successes.
Unknown language, missing tests or incompatible task metadata are `invalid_task`;
missing compiler/runtime, failed worker or task setup is `infra_error`; candidate
compile/runtime errors, failed assertions and case timeouts follow source scored
labels. A task timeout must not hide an infrastructure timeout under candidate zero.

Acceptance cases cover an indented Plus solution (#148), stdin and callable
LiveCodeBench modes (#150), a passing/failed case mixture, compilation error,
process-group cleanup, sample-trial order, protected-test restoration and source
pass@k. MultiPLE language dispatch and SWEbench image/setup retain their existing
orchestration. Source checkers such as MRCR character similarity, NUPA digit/format
metrics and LiveBench scorer families are trusted script functions with their
explicit original aggregation, not approximate numeric/exact comparisons.

## Coverage classification

The source discovery inventory retains its earlier planning labels. The current
[coverage register](coverage-gaps.json) is authoritative for implemented cutovers:
42 custom benchmarks comprise five native clients, three boxed-math hybrids,
and 34 pending integrations/profiles. JEEBench is explicitly opt-in and has
source/evaluator fixture validation, without saved-run replay. Its `invalid_task`
results abort aggregation. Local overrides comprise 21 task configurations
(two native exact routes, one hybrid GSM8K rational-exact route and 18 pending
profiles) plus one orchestration group. Native harness and inline definitions
are separate populations; discovery alone is not semantic validation.

### Recorded-trace replay and GSM8K override cutover

The September 2026 campaign selected three model-run links per capable benchmark before scoring (seed 20260930; selection SHA256 `575523245c2f131685e749edf0d3a546f96cadc4566425eacb4543078405e64a`). All 24 selected runs replayed 63,360 recorded samples through actual Evalchemy `_score_custom_task` or harness `evaluator.evaluate`, reaching 68,913 verifyit primitive calls. Every per-sample score and deterministic point metric matched the archived result; all rounded tracker scores matched. Harness bootstrap stderr was excluded. This validates scoring/filter/aggregation playback, not regenerated inference or the entire 13,982-configuration corpus. Detailed immutable inputs, source hashes, commands, outputs and per-call specs/verdicts are in campaign `evidence/e2e/evals/catalog.json`.

The traces exposed a client mapping omitted from the initial native eligibility assessment: Evalchemy's GSM8K override version 3.3 uses its own final-answer filter and Minerva scorer, rather than upstream harness version 3.0. Its exact rational shortcut now canonicalizes both answers with the pinned source `_rational_value` and compares their Fraction strings through strict verifyit exact. Missing extraction returns verifyit scored zero; non-rational answers retain source symbolic scoring. This is a hybrid client integration, not native symbolic equivalence. All three selected 1,319-sample runs reproduced both strict/flexible metrics and every sample. Eight source-parity regressions cover decimal/integer equality (`28.00` versus `28`), equivalent fractions, mismatches, missing answers, symbolic equality/mismatch and propagation of scorer infrastructure errors. The initial incorrect upstream-route replay and unmodified baseline remain under `evidence/e2e/evals/superseded/upstream-gsm8k`. The current broader harness availability is recorded in [the harness mapping](lm_eval_mapping.md).

AIW, GSM8KPerturbed and AIME25 had no validated tracker trace links; no replay success is claimed for them.
