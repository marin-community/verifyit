The patch targets marin-community/evalchemy
`e3f4a3d601896c437f37b0bd0a30e51651cce6d0`.
Install verifyit in the evaluation environment and apply `verifyit.patch` from
the Evalchemy checkout. Apply the separately pinned harness patch to its installed
harness dependency for native tasks.

GPQA Diamond and MMLU-Pro retain their answer extraction and aggregation. Their
extracted option letters now call verifyit's `grade_mcq_candidate`; GPQA declares
four options and MMLU-Pro ten. Category and repeat counts, standard errors and
sample records remain Evalchemy-owned.

The shared extraction boundary calls verifyit's completion adapter. Final content
takes precedence over reasoning; completed reasoning-only math answers require a
box, while truncated reasoning-only output supplies no answer. Inline reasoning
end markers are handled before benchmark box extraction. The patch retains the
benchmark's own box parser and stop-sequence handling.

The patch also routes AIW normalization through strict exact, GSM8KPerturbed
through zero-tolerance numeric, and the shared AIME/MATH500 boxed comparison
through math. Missing-parse Minerva fallback and judge prompts remain source-owned.
Further normalization/fallback contracts are described in
[the mapping](../../docs/unification/evalchemy_mapping.md).


The integration requires verifyit implementation commit
`87e4a72428695a7eedfa97c22868ea3aa2d1c651`, including JEEBench primitive composition and `math_answer_text`.
Apply `dependency-pin.patch` to declare that exact implementation in the source
project metadata. This commit remains local and unpublished: the remote Git URL
in the dependency patch is a publication target, not an available installation.
Evalchemy's lockfile must be regenerated when that dependency becomes fetchable.
For current validation in an environment with the pinned project's existing
dependencies installed, use the local Git commit and install the patched source
without resolving the unpublished remote dependency:

```bash
uv pip install --python /path/to/environment/bin/python 'verifyit[answer] @ git+file:///path/to/verifyit@87e4a72428695a7eedfa97c22868ea3aa2d1c651'
uv pip install --python /path/to/environment/bin/python --no-deps /path/to/patched-project
```

An isolated core-only installation from this exact local Git revision was
validated through the actual patched JEEBench extraction and evaluation pipeline:
five fixtures over three repetitions match source scores and aggregates, with 88
verifyit calls. Four malformed-reference batches abort without an aggregate.
Installed-package provenance and results are retained in campaign
`evidence/e2e/wiring/evalchemy-jee/installed-metadata.json` and `installed-replay/`.
No remote publication or live model endpoint was used.

The GSM8K override retains its version 3.3 extraction/Minerva contract. Its rational
shortcut uses strict verifyit exact on canonical Fraction values; non-rational
answers retain Minerva symbolic scoring. This client hybrid was exposed by real
recorded traces, so it is separate from upstream harness native-config eligibility.
Run the source parity regressions with the patched Evalchemy environment:

```bash
PYTHONPATH=/path/to/verifyit/src:/path/to/patched-evalchemy:/path/to/harness \
  /path/to/evalchemy/.venv/bin/python integrations/evalchemy/check_gsm_override.py \
  /path/to/original-evalchemy /path/to/patched-evalchemy
```


## JEEBench native client

Apply `jee-verifyit.patch` to the pinned Evalchemy checkout. The opt-in benchmark
constructor `JEEBenchBenchmark(verifyit_enabled=True)` and the existing public
`TaskManager(task_list=["JEEBench"], verifyit_enabled=True)` benchmark-kwargs
route (`from eval.task import TaskManager`) activate the client. No new CLI flag is claimed. The default source scorer
is unchanged, and the verifyit import is lazy. The dependency pin records the actual JEE API implementation checkpoint; it
remains local and unpublished.

The real `extract_answer` and `evaluate_responses` pipeline dispatches source
uppercase A–D option sets to strict exact matching, retains `.25` subset credit
for multiple-answer questions, and uses `NumericSpec` with absolute tolerance
`.01` and zero relative tolerance for integer/numeric questions. Three-repetition
score vectors, means, standard errors and sample metrics remain benchmark-owned.
Malformed/empty choice references and nonfinite/boolean numeric references return
`invalid_task` and abort the evaluation rather than being averaged into positive
scores. Unsupported uppercase candidate labels are scored zero; this tightens
the source's permissive letter filtering (e.g. `AE` formerly matched `A`).

Five actual benchmark fixture cases over three repetitions match every score and
aggregate, with 88 observed verifyit calls. Four malformed-reference batches abort
without returning an aggregate. No JEEBench model-run links were found in the
campaign tracker or local JSON/JSONL artifacts; this is source fixture validation,
not archived-trace replay. Reproducible evidence is in campaign
`evidence/e2e/wiring/evalchemy-jee/source_roundtrip.py` (supports `--output`).


The English TruthfulQA MC2 override uses the harness probability-mass integration
from this same dependency checkpoint. Apply the harness
`truthfulqa-mc2-verifyit.patch` after its base/corpus patches; no override scorer
file change is required. The pinned callback body is verified, then raw likelihoods
and binary labels are graded inside verifyit. Native/source evaluator fixtures and
an isolated installed-package replay match. Three saved run links are frozen in
campaign `evidence/e2e/wiring/harness-mc2/truthfulqa-selection.json`; S3 access is
currently unavailable, so no archived TruthfulQA replay is claimed.

AMC23 literal normalization
---------------------------
Apply `amc23-verifyit.patch` to the pinned Evalchemy source. Enable the public
constructor with `AMC23Benchmark(..., verifyit_enabled=True)`, or use
`from eval.task import TaskManager` and
`TaskManager(task_list=["AMC23"], verifyit_enabled=True)`. The manager forwards
accepted benchmark kwargs; this is not a new CLI flag. Source extraction and
ten repetition aggregates remain. Known normalization errors fail closed
instead of using the original raw-equality fallback. Evidence is under
`evidence/e2e/wiring/evalchemy-amc-math`; AMC23 validation uses source fixtures,
with no matching archived AMC23 inputs found.

## NUPA component metrics

Apply `nupa-exact-verifyit.patch` after the existing Evalchemy patches. Opt in
through the public benchmark constructor:

```python
from importlib import import_module

Benchmark = import_module("eval.chat_benchmarks.NUPA5K-Loose.eval_instruct").NUPA5KLooseBenchmark
benchmark = Benchmark(verifyit_enabled=True)
```

Use `NUPA-Loose` and `NUPALooseBenchmark` for the other variant. Default source
execution remains available. The adapter calls strict exact grading for the full
digit-component tuple and each source-aligned digit comparison. It retains
`exact_match`, `digit_match`, `dlength`, `format_valid_rate` and `no_answer_rate`,
including all task, length-bucket and combined group denominators. This is not
numeric tolerance: `1.00` and `1.0` are different component representations.
Source preparation removes signs, including scientific exponent signs; the
source-defined component metric consequently treats `1.23e-5` and `1.23e5`
alike. That limitation is retained explicitly rather than described as numerical
equivalence.

References must match the complete declared format and contain valid nonempty
digit components. A malformed reference such as `abc123` formerly scored one
against output `123`; the opt-in evaluator now aborts the entire mixed batch.
Unexpected extraction failures propagate, so no partial aggregate is returned.

Three seeded NUPA5K tracker links replay all 15,000 saved responses. Every sample
matches the archive across all five metrics, and all aggregate/bucket metrics
match precisely. The untouched source additionally matches the first complete
run. NUPA-Loose shares this scorer but has source evaluator fixtures only.
Evidence and independent rerun commands are under
`evidence/e2e/wiring/evalchemy-nupa`. Downloads comprise only active sample and
configuration/result shards (86,065,656 bytes), with archive checksums verified;
no model regeneration or dataset download is needed for replay.

## Uncheatable rolling-likelihood overrides

After the existing harness patch sequence, apply
`uncheatable-runtime-verifyit.patch` to the harness checkout. Install the audited
Evalchemy task definitions under that checkout's trusted task directory:

```sh
python integrations/evalchemy/install_uncheatable.py \
  --evalchemy-root /path/to/evalchemy --harness-root /path/to/lm-eval-harness
```

Use Evalchemy's existing `--include_path` argument with
`/path/to/lm-eval-harness/lm_eval/tasks/evalchemy_uncheatable`. That include path
is appended after Evalchemy's default definitions, so the installed entries take
precedence. The installed metadata opts the fifteen category tasks into the
public task factory's corpus-runtime route; the group remains orchestration.

The source category selection, token/byte denominators, word/byte perplexity and
bits per byte execute through verifyit's ScriptSpec boundary. This is retained
source runtime, not native primitive reimplementation. Only single-rank
execution is supported. Pinned configuration, helper, filter, scorer and
aggregation drift is rejected; malformed likelihoods or aggregate overflow abort
the batch without returning partial metrics.

All fifteen category factory/evaluator fixtures match the source metrics and
retain two selected documents while excluding one other category. Six early
configuration failures, four evaluator failure cases and four installer checks
pass. No matching tracker links or local JSON/JSONL artifacts were found;
archived replay is not claimed. Reproducible evidence is under
`evidence/e2e/wiring/evalchemy-uncheatable`.

## DROP multi-span scores

After the harness and Uncheatable patches, apply `drop-runtime-verifyit.patch`
to the harness checkout. Pass task metadata `verifyit_drop_runtime: true` through
TaskManager overrides. Both the harness DROP definition and Evalchemy's DROP
override use this route; Evalchemy's short-answer extraction remains in its
source filter.

Each filtered response executes the pinned source DROP scorer through
`ScriptSpec`, returning EM and F1 to the evaluator. Numeric gating, optimal
multi-span alignment and alternative-reference maxima retain source behavior.
References that normalize to empty spans are invalid tasks and abort the batch,
including when earlier samples scored successfully. Seven evaluator fixtures per
source match per-sample and aggregate metrics. No DROP tracker links were found;
archived replay is not claimed. Evidence is in `evidence/e2e/wiring/harness-drop`.

## HumanEval pass@1

Apply `humaneval-function-verifyit.patch` after the DROP patch. Pull the worker
image `python@sha256:e41613d42d4891e4930f79523f93f81bbc7632584ec65e36ab055f41a800b41e`
and pass task metadata `verifyit_humaneval_runtime: true` through TaskManager.
Docker must be available to the evaluator process. The harness and Evalchemy
HumanEval definitions are supported with one completion and `k: [1]`; other
repeat counts and pass@k configurations are rejected.

The source completion-building filter remains. `ScriptSpec` runs the source
assertions in a supervisor, which calls a persistent candidate function in a
separate container using bounded typed JSON. Candidate stdout is separate from
the function transport. The worker receives the candidate and function inputs;
source assertions remain in the supervisor. The pinned worker has no network,
a read-only filesystem and explicit resource limits.

Three frozen source tasks produce identical source and cutover scores for
canonical, incorrect and correct-with-print completions on both framework
routes. These are source fixtures, not archived model traces. The tracker has
HumanEvalPlus runs, which use a different evaluation contract. Evidence and
installation hashes are under `evidence/e2e/wiring/harness-humaneval`.

## Custom HumanEval and MBPP

These custom benchmarks are separate from the harness HumanEval override above.
Apply `function-rpc-values-verifyit.patch` to the harness after the existing
HumanEval patch, then apply `custom-code-verifyit.patch` to Evalchemy. Instantiate
`HumanEvalBenchmark(verifyit_enabled=True)` or
`MBPPBenchmark(verifyit_enabled=True)`; the source default remains unchanged.
HumanEval retains both Python and shell. Both benchmarks retain the source
pass@k estimator, including multiple completions; MBPP retains per-task sample
annotations.

The dispatcher uses `ScriptSpec` and a separate candidate container. Trusted
Python assertions and shell tests stay in the supervisor. Typed JSON carries
ordinary values, including sets, Counter values and complex numbers. Correct
candidate stdout does not interfere with the protocol. A malformed trusted
reference or verifier failure aborts the batch without returning partial metrics;
an incorrect candidate or candidate timeout scores zero.

The tested image has ID
`sha256:c65c33e0fdd600e418f020d233aca4178c79c3a3208657f51a31dfc77c2c22f3`.
It was built from `code.Dockerfile`, using the existing pinned Python base and
NumPy 2.3.5. The exact image archive is retained in campaign evidence at
`evidence/e2e/wiring/evalchemy-code-family/candidate-image.tar`; load it with
`docker load -i` before replay. This is a local image ID, not a published registry
digest. A fresh build may have a different image ID and requires a new pin and
validation before deployment.

Three frozen source fixtures per language/benchmark exercise canonical and
incorrect completions, plus ten mixed completions per task for pass@1/pass@10.
These are fixtures, not archived model traces. Supplemental tests cover trusted
helper functions, Counter/set/complex transport, candidate functions named
`check`, stdout, wrong return types, timeouts and batch failure after a valid
sample. MBPP367 has an undefined trusted `root` and produces an invalid task.
MBPP180 and MBPP493 have platform-sensitive exact floating-point assertions: unchanged
canonical code fails on macOS and passes on the pinned Linux image. Linux parity
uses the untouched source scorer in that same runtime, through the original
benchmark API; expected values and tolerances are unchanged. Source hashes and
export dependencies are in `custom-code-source.json`.

## HumanEvalPlus and MBPPPlus

After the custom code patches, apply `function-rpc-plus-verifyit.patch` to the
harness and `custom-plus-verifyit.patch` to Evalchemy. Enable
`verifyit_enabled=True` on either Plus benchmark. They reuse the pinned custom
code image and retain source assertion programs, pass@k, scored_count, artifact
validation and per-task annotations. Three frozen source fixtures per benchmark
match complete source evaluator results for canonical, incorrect and ten mixed
completions. Archived replay is not claimed; the three selected tracker links
per family remain frozen in campaign evidence.

Plus function transport supports large integers as tagged hexadecimal values
and nonfinite floating-point values as explicit data tokens. These values are
candidate inputs/results; verifier rewards remain finite. Plus permits a bounded
16 MiB RPC frame; earlier code routes retain 1 MiB. Complete canonical censuses
measured maxima from 3.6 MB to 12.4 MB for the four affected source tasks. Those
four actual evaluator regressions use the same explicit 30-second budget in
both source and cutover, separately from the default three-second frozen fixtures.
The candidate container retains its 256 MiB memory limit; this does not limit
total supervisor memory.

MBPPPlus tasks 737, 787 and 794 computed `exact_match` without asserting it. Their
exact-hash-pinned trusted checker now asserts the result. The source observes
only boolean values and whether other results are None; a pinned projection
preserves that contract without reconstructing candidate regex objects in the
supervisor. All three canonical solutions still pass, while wrong None-returning
solutions change from source score one to zero. A changed checker profile aborts
the batch. These corrections are reported separately from parity evidence.

Source hashes, frame limits and patch dependencies are recorded in
`custom-plus-source.json`. Evidence is under `evidence/e2e/wiring/evalchemy-plus`.

## MixEval

Apply `mixeval-verifyit.patch` and enable `verifyit_enabled=True` for `mixeval`
or `mixeval_hard`. All four model/rule parser combinations run fresh scoring
through ScriptSpec, preserving source prompts, ordered concurrency, split
rounding and weighted category aggregation. Exact and Numeric grade the rule
contracts; model free-form fractional scores retain the source parser.

Eight profiles have 48 evaluator fixtures and 24 matching HTTP requests. The
source rule-MC scorer omits count metadata and its complete aggregate fails;
the correction is checked against untouched per-split scoring and an independent
weighted-aggregate oracle. Missing interpretations, blank candidates and stale
positive caches cannot award credit. Malformed judge transport aborts the batch
after SDK retries, bypassing the source outer 99 retries and random fallback.

Evidence is fixture-only. Use `PYTHONHASHSEED=0` to reproduce source ordering
in parser observations. The internal base-model extraction flag is not exposed
by the benchmark constructor and remains unsupported. Scoring uses temporary
files; existing source caches are neither trusted nor replaced. The batch
deadline is 1900 seconds. Source hashes and boundaries are in
`mixeval-source.json`.

## Partial Zeroeval integration

Apply `zeroeval-verifyit.patch` and enable `verifyit_enabled=True` only for
explicit task selections among `numersense-v2`, `math-l5`, `crux`, `gsm` and
`mmlu-redux`. The original evaluator dispatches the first two to its numeric
parser and the other three to literal comparison; the cutover preserves this
behavior. Append the zeroeval source directory to module lookup for the original
`src.global_configs` import. Existing harness function-RPC exports and their
pinned Python image are required for candidate fraction normalization.

Twenty fixtures cover these five task names through the actual evaluator.
ScriptSpec retains source metrics while candidate expressions run separately
from trusted references. Missing task files and invalid references abort the
whole batch. All missing-answer batches receive zero accuracy, 100 percent
missing answers and zero reasoning length; the source divides by zero.

This does not complete the Zeroeval benchmark. Its default Zebra route needs
the gated `allenai/ZebraLogicBench-private` solutions. All 20,000 cells in the
public dataset are `___` placeholders and cannot substitute for references.
The loader also advertises `alpaca_eval`, whose original evaluator branch is
broken; that branch remains unsupported. No whole-benchmark tested count or
archive replay is claimed. Hashes and scope are in `zeroeval-source.json`.

## MTBench single-mode judges

Apply `mtbench-verifyit.patch` and enable `verifyit_enabled=True` in single mode.
Use the bundled, source-equivalent fastchat package. ScriptSpec retains all four
source profiles (default/math and first/multi-turn), OpenAI chat-completions and
legacy Anthropic completions requests, rating parsing and pandas per-turn/global
means. Source scores range from 1 to 10; verifyit rewards are `(score - 1) / 9`.

Eight local HTTP evaluator judgments match full source records and requests on
both providers. Timestamps remain in emitted records and raw verdicts but are
excluded from deterministic parity comparisons. Missing or out-of-range ratings,
refusals and incomplete responses abort the batch. SDK retries remain, while the
source outer 16 retries are bypassed under a 900-second judge deadline. Each
question requires both turn matches. Empty turns receive minimum score 1, and
stale judgment files are removed before scoring. Only complete successful
batches publish fresh judgment files.

Both source pairwise modes remain unsupported. Pairwise-baseline writes winner
fields but the evaluator reads single-mode score columns, raising KeyError.
Pairwise-all selects only one model even when multiple answer files exist,
creates no matches and fails loading judgments. Evidence is fixture-only; no
matching archive traces were found. Source and installed-module hashes are
recorded in `mtbench-source.json` and its linked provenance.

## AlpacaEval

Apply `instructions-verifyit.patch` first for the shared RNG-state validator, then
`alpaca-verifyit.patch`. Set `verifyit_enabled=True` on `AlpacaBenchmark`; the
disabled path retains its original imports and constructor argument positions.
The source Alpaca package, dependencies, reference datasets and GLM assets remain
required. `alpaca-source.json` pins the client and source implementation.

ScriptSpec supervises the original preference parser and corpus-level statistical
scorer. All eight AE1/AE2 selector profiles preserve 160 fresh local HTTP requests
and source metrics. AE1-auto uses the explicitly fresh baseline, not its earlier
cached witness. Final weighted/ranking replays preserve preadvanced Python and
NumPy RNG states. These are evaluator fixtures, not archived validated scores.

Incomplete/refused/malformed judge output aborts the whole batch. The weighted
one-token classifier may validly finish at its length limit with complete token
and logprob observations. Blank candidates receive loss preferences before source
aggregation; all-blank ordinary, discrete and length-controlled win rates are zero.
The source regularized LC prediction remains diagnostic, while uncertainty fields
retain source values. Fresh scoring bypasses annotation caches. Only the
inapplicable AE1 cached LC NaN is represented as null; computed nonfinite metrics
fail. No new verifier class is introduced.

## BigCodeBench

Apply `bigcodebench-verifyit.patch`, build the dependency image using the included
`eval/graders/bigcodebench_runtime/README.md`, and enable `verifyit_enabled=True`.
The default image is `verifyit-evalchemy-bigcodebench:source-v1`;
`VERIFYIT_BIGCODEBENCH_IMAGE` selects an equivalent validated runtime. The tested
lock targets Linux arm64. The build pins its Python base and 252 resolved Python
package versions; native system libraries and NLTK assets remain runtime inputs.

All four prompt populations retain the original Python unittest scorer, timeout,
`safe_mode`, completion IDs and pass@k denominator behavior. Three tasks per
population were frozen before scoring. Source/cutover parity covers 240 mixed
completions across both safe modes, plus 24 on a fresh documented build. Canonical
task 736 keeps its original scipy-related failure and receives zero. These are
source-task fixtures, not archived validated model traces.

Missing or empty trusted suites invalidate the task; missing trusted dependencies
abort the entire batch. Current responses replace stale generated files, and a
failed later population cannot return earlier positive metrics. Parent cleanup
removes named containers after grading, including timeout paths. Docker networking
remains at its default, preserving the absence of a source network ban.

Candidate code and trusted assertions share the source runtime; isolation remains
unverified. The tested boundary is `evaluate_responses`. The original
`run_benchmark` references missing `self.languages` and remains unchanged. Only
Python execution is implemented by the source executor. No new verifier class
is introduced.


## LiveBench

Apply `instructions-verifyit.patch` and `livebench-verifyit.patch`, build the
included `eval/graders/livebench_runtime/Dockerfile`, and enable
`verifyit_enabled=True`. The runtime README records the pinned Python image,
package lock and required top-level `livebench` import path. The existing
Evalchemy optional dependencies remain required; missing readers or runtimes
abort grading. `VERIFYIT_LIVEBENCH_IMAGE` can select an equivalent validated
image. Host verifyit was tested at `a2ebf259a9ad95871ad0d5655d6878999b353c67`;
the callback container contains source runtime dependencies, not verifyit.

All 49 category/task/subtask/release cells run through both JSONL and Hugging Face
loaders with three frozen source-question fixtures per cell. Full metrics,
ordered judgments and RNG state match the source. Twenty-four separately frozen
public model-answer/judgment joins also match recorded scores and a fresh source
replay; ten are positive. Archive source scorer revisions are not identified.
Supplemental fixtures exercise the source house-traversal branch, absent from
the downloaded question population, and full/partial/zero instruction scores.

CTA uses ExactSpec; registered trusted instruction predicates use IfevalSpec.
Other scorers retain their original callbacks under ScriptSpec, including
source task/category/date aggregation. The documented image runs coding and
AMPS callbacks. Source coding's six-second test and thirty-second task deadlines
remain, under a 120-second outer deadline including startup. No additional
network or memory restriction is imposed. Coding candidate code and trusted
tests share the grader runtime; scoring parity does not establish isolation.

Malformed trusted references, incomplete batches and missing dependencies abort
without partial metrics, and failed batches remove judgment artifacts. Empty
eligible HF tasks cannot reuse stale judgments. Candidate parse errors score
zero; undetectable language no longer receives the source success fallback,
and language detection is explicitly seeded. Nineteen regressions cover these
cases. See `livebench-source.json` for exact hashes and
`evidence/e2e/wiring/evalchemy-livebench/` for frozen selections and raw evidence.
No new verifier class is introduced.


## MultiPLE

Apply `multiple-verifyit.patch`, build the two images documented in
`eval/graders/multiple_runtime/README.md`, and set `verifyit_enabled=True` on
`MultipleBenchmark`. The existing Script mode supervises source scoring and
pass@k aggregation. No new verifier class is required.

All 24 selectors with bundled data have positive and wrong evaluator fixtures,
plus 72 frozen source-task responses. Six existing data/callback aliases are
repaired. Seven of the 31 advertised selectors lack bundled populations:
python, dfy, fs, lean, luau, matlab and v. They remain unsupported, and missing
source generation settings are not claimed repaired. This is fixture evidence,
not archived-score replay or a claim that all 31 advertised routes work.

Go now discovers its Test functions. A callback must report both OK and exit
zero; this corrects source false positives in C#, Clojure and other status-aware
runtimes. Five durable tests include real bundled Go/C#/Clojure correct and wrong
responses, stale-file replacement, mixed pass@1/pass@10, and whole-batch failure
cleanup. Native ARM64 Mono/Racket replace runtimes that abort under AMD64
emulation on the validation host; source comparisons use the same runtime.
Candidate code still shares the source grader with trusted assertions, so this
bridge does not establish candidate/assertion isolation. See
`multiple-source.json` for exact sources, images, scope and evidence.

### Consolidated Judge client checkpoint

`shared-judges-verifyit.patch` requires the core `grade_judge_candidate` API and
`JudgeConnection`. Its existing `verifyit_enabled=True` clients now pass actual
candidate text directly to Judge mode; the per-answer Script subprocess and
client-owned judge transport/parser are removed. Apply it before the separate
FinanceBench client patch. Default source paths remain available.

SimpleQA, SimpleQAMini, FinanceBench, OlympiadBench and OlympiadBenchFull have
fresh local-HTTP framework evidence: seven result scenarios and 45 malformed
batch failures. Blank candidates receive zero without a judge request. The shared
transport uses `max_completion_tokens`, retries incomplete output from 128 to
2048 tokens, and requires an unambiguous complete final label. These are explicit
near-parity policies; archived validation is still pending. See
[checkpoint provenance](shared-judges-source.json). This frozen patch excludes
later Math-family consolidation work.
