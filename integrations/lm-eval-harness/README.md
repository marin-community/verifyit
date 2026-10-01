The AfroBench profile patch adds 45 AfriQA exact/F1, 100 MasakhaNER span-F1,
100 MasakhaPOS token-accuracy and five ASK-GEC implicit exact configurations.
The three AfroBench families passed source API and evaluator fixture comparisons;
no matching saved model-run traces were available. Apply
`afrobench-profiles-verifyit.patch` after `verifyit.patch`. The dependency pin records the implementation commit for the profile APIs.

The patch targets EleutherAI/lm-evaluation-harness v0.4.12,
`6d642546f4688648fced259eb3302efd36ece5af`, which Evalchemy pins.
Install the campaign verifyit package in the evaluation environment and apply
`verifyit.patch` with `git apply` from the harness checkout.

The evaluator calls `verifyit.adapters.lm_eval.score_task` after harness filters.
It consumes `.metrics`, retaining every original metric value and the original
harness aggregators. Recognized default exact/likelihood-choice branches use
verifyit primitives; other source scorers remain compatibility-only. Invalid native
samples abort evaluation instead of disappearing from aggregates. No scalar reward is implicitly selected. No model or
dataset download is needed to apply the patch.

For external consumers, `score_task(task, doc, filtered_responses, reward_metric)`
returns source metrics plus an optional verifyit `Reward`. `aggregate_task` calls
source aggregators with original per-sample values, including tuples used for
weighted perplexity. Selecting an absent, structured, unbounded or nonfinite
metric returns `invalid_task` while retaining metrics. Scorer/aggregator exceptions
propagate to the integration's infrastructure boundary. A wrong candidate's valid
zero metric produces `scored`, never an infrastructure failure.


The integration requires verifyit implementation commit
`87e4a72428695a7eedfa97c22868ea3aa2d1c651`, including the AfroBench and corpus runtime APIs.
Apply `dependency-pin.patch` to declare that exact implementation in the source
project metadata. This commit remains local and unpublished: the remote Git URL
in the dependency patch is a publication target, not an available installation.
Evalchemy's lockfile must be regenerated when that dependency becomes fetchable.
For current validation in an environment with the pinned project's existing
dependencies installed, use the local Git commit and install the patched source
without resolving the unpublished remote dependency:

```bash
uv pip install --python /path/to/environment/bin/python 'verifyit @ git+file:///path/to/verifyit@87e4a72428695a7eedfa97c22868ea3aa2d1c651'
uv pip install --python /path/to/environment/bin/python --no-deps /path/to/patched-project
```

A core-package installation from this exact local Git revision was validated
against the existing optional framework dependencies. Actual factory/evaluator
roundtrips preserve BLEU/CHRF/TER and weighted-perplexity observations and point
metrics. The installed module path and Git commit are recorded in campaign
`evidence/e2e/wiring/harness-runtime/installed-metadata.json`; no remote publication
or live model endpoint was used.


## Retained corpus runtime

Apply `corpus-runtime-verifyit.patch` after `verifyit.patch`. It adds an optional
single-rank batch route for 868 translation, 40 default rolling-likelihood and 28 default likelihood
configs. The dependency pin records the actual local implementation checkpoint. It is
unpublished; use a local Git installation for validation and do not assume the
remote Git URL is fetchable.

Select supported tasks and opt in with `--metadata verifyit_corpus_runtime=true`,
or `TaskManager(metadata={"verifyit_corpus_runtime": True})`. The actual task
factory binds its trusted indexed YAML path; unknown grading overrides, inline
configs and custom classes are rejected. `enable_corpus_runtime(task, trusted_yaml)`
is also available for explicit task setup. Multi-rank execution is rejected.

The evaluator passes a complete filtered response/document batch as JSON to
`verifyit.adapters.harness_runtime.score_corpus`. Its `ScriptSpec` subprocess
loads the matching trusted source modules, constructs datasets from those
supplied documents without downloads, and executes actual `process_results` and
registered corpus aggregators. Source module/config SHA256 provenance is retained.
The evaluator consumes the returned point metrics directly; optional bootstrap
statistics use the unchanged raw observations. Corpus reward is explicitly zero
with `retained_runtime` metadata, not a clipped correctness score.

BLEU/CHRF/TER and word/byte perplexity/bits-per-byte before/after evaluator fixtures
match all named point metrics and observations. Empty candidate translations retain
source zero-overlap behavior. Empty references/weighting denominators, nonfinite
samples, producer failures or missing observations abort the entire evaluation
without a positive aggregate. No matching saved tracker runs were available for
these families, so this validation does not claim genuine archived replay.

The default likelihood extension preserves scalar log probabilities, integer greedy
accuracy observations, and source `exp(-mean(logp))` perplexity without clipping.
Ten arithmetic configs, ASDiv and 17 LAMBADA configs pass registered-source guard
roundtrips; actual evaluator fixtures cover all three families. A malformed pair,
nonboolean greedy flag, nonfinite/positive log probability or overflowing
perplexity aborts the entire batch without an aggregate. Acc-only tasks accept
large negative finite log probabilities because no perplexity is computed.
Fixture evidence is in campaign `evidence/e2e/wiring/harness-likelihood/`.
No matching model-run links were found in the tracker. Named local ASDiv artifacts
include SkyRL generation traces; those do not supply harness likelihood response
pairs. This is source fixture validation, not archived model-run replay.
The dependency pin above includes the likelihood extension at its actual API
checkpoint; it remains local and unpublished.

## Source-pinned CodeXGLUE metric

The six code-to-text tasks opt in through the same factory metadata. The guard
requires the original BLEU/utils file hashes, exact source callable configuration
and registered mean aggregation; arbitrary callbacks and modified implementations
remain unsupported. The source metric keeps its 100-point scale and its lowercase,
punctuation and add-one smoothing semantics for nonempty output. Empty or
whitespace-only output deliberately scores zero because source smoothing grants
it positive credit. These zero samples remain in the corpus denominator.
Malformed references abort the complete evaluation without an aggregate.
Actual evaluator and all six registered-source guard fixtures pass, including
source-hash mutation rejection. No named tracker/model artifacts were found for
these tasks; evidence is campaign `evidence/e2e/wiring/harness-code-text/`.
The dependency pin records the actual CodeXGLUE API checkpoint above; it remains
local and unpublished.

## Source-pinned XLSUM ROUGE

The 36 XLSUM tasks (12 languages, three prompts) use the same metadata opt-in.
The client accepts only the pinned passthrough/aggregation functions and the
source default `none`/`take_first` filter; changed filters fail before execution.
An observation stage preserves every ordered gold/prediction pair. At the normal
per-task aggregation position, a complete ScriptSpec batch executes the actual
source ROUGE aggregator. It transfers evaluate's uint32 seed from the current
NumPy state; evaluate's temporary seed restores state, so the parent RNG is never
mutated. Point metrics, subsequent framework stderr and task ordering remain
source-compatible. Multi-task fixtures with nonzero bootstrap settings match
metrics, stderr, observations and final RNG state, including preadvanced state.
Missing references, failures and changed source hashes abort without an aggregate.
All 36 source guard roundtrips pass. No named XLSUM run links were found in the
tracker or local JSON/JSONL artifacts; this is fixture-only validation. Evidence
is campaign `evidence/e2e/wiring/harness-rouge/`, including cached backend and
seed-wrapper hashes. The initial estimate of five prompt families was corrected
before coverage promotion; the pinned source has three. The dependency pin records this extension at its actual API checkpoint. The optional evaluation environment
must already supply evaluate, rouge_score and its cached ROUGE metric module.


## TruthfulQA MC2 probability mass

Apply `truthfulqa-mc2-verifyit.patch` after the base and corpus-runtime patches.
The evaluator validates the recognized task before filters run. After filtering,
it grades raw likelihood pairs and binary correctness labels inside verifyit:
stable softmax weights strict ExactSpec choice-index membership. This preserves
probability mass across all correct alternatives, rather than replacing MC2 with
argmax accuracy. The source mean aggregator still consumes every sample.

The guard accepts 31 pinned Okapi multilingual configs and Evalchemy's English
TruthfulQA MC2 override with its separate pinned scorer hash. Callback bytecode,
source hashes, actual default filter and registered mean identity are checked.
Malformed/nonfinite likelihoods, label vectors without a correct alternative,
and changed grading callbacks or filters abort without an aggregate. All-correct
vectors score exactly one. For Okapi's direct exponentiation underflow, stable
softmax deliberately produces the mathematically defined finite probability ratio.
The English override already uses stable softmax and matches within floating tolerance.

All 31 registered task guards, three seeded evaluator witnesses, two-document
native/cutover evaluator parity for both source contracts, and malformed-batch
failure fixtures pass. Evidence is campaign `evidence/e2e/wiring/harness-mc2/`.
Three of thirteen matching English tracker links were selected before scoring;
S3 credentials are currently unavailable and no matching local JSON/JSONL artifacts
were found, so archived replay is not claimed. The dependency pin above records the actual local MC2 implementation checkpoint.
An isolated core-only Git install passed the English actual evaluator replay with
32 calls and matching metrics; installed provenance and results are in campaign
`evidence/e2e/wiring/harness-mc2/installed-english/`. The commit remains unpublished.

Hendrycks literal math
---------------------
Apply `hendrycks-exact-verifyit.patch` after the base, AfroBench, corpus runtime,
and TruthfulQA patches. Eight pinned task configurations use source boxed
reference extraction and string normalization followed by strict ExactSpec
grading. Profile drift, malformed references, and nonfinite values fail closed.
The patch checks the filter before executing it. Evidence under
`evidence/e2e/wiring/evalchemy-amc-math` includes all eight config guards and
three selected full MATH500 response runs: all 1,500 scores match this fresh
harness source comparator. Archived custom MATH500 scores use a different
comparator and are not claimed to match.

AGIEval multi-answer choice scoring
----------------------------------
Apply `agieval-mcqa-verifyit.patch` after the Hendrycks patch in the sequence above.
The 19 pinned MCQA configs use raw and character-normalized first-maximum
likelihood winners, graded against every accepted gold index through existing
choice/exact primitives. Source `acc` and `acc_norm` mean aggregation remains.
Malformed gold, empty options, nonfinite or positive likelihoods, and malformed
likelihood pairs abort evaluation rather than producing partial aggregates.
Scorer, metric, and filter drift is rejected before filters run.

Reproducible actual evaluator and all-config guard scripts are under
`evidence/e2e/wiring/harness-agieval`. They cover Unicode option lengths, ties,
alternative golds, a mixed valid/invalid batch, and four early contract-drift
negatives. This validation uses source fixtures: the named tracker/local
artifact census found no matching AGIEval saved runs.

CrowS-Pairs preference metrics
-----------------------------
Apply `crows-pairs-verifyit.patch` after the AGIEval patch. All 22 pinned configs
preserve source sentence ordering, subset filters, strict preference ties, and
both named metrics. Reversed MCQ choice implements strict stereo preference;
verifyit also computes unbounded `likelihood_diff` and the original arithmetic
means. These are bias/preference benchmark metrics, not universal correctness
rewards. The framework still computes stderr, which verifyit validates before
export. Malformed samples, missing sentence references, nonfinite means or
stderr abort evaluation without a partial aggregate. Finite-overflow rejection
is an intentional conservative change from source infinity outputs.

Evidence and reproducible scripts are under `evidence/e2e/wiring/harness-crows`:
all 22 config guards, three seeded actual evaluator witnesses, fresh source
metric/stderr parity, and malformed/overflow/drift failures. No named matching
tracker or local saved runs were found; this is source-fixture validation.

Babilong substring scoring
-------------------------
Apply `babilong-substring-verifyit.patch` after CrowS-Pairs. The 20 pinned configs
run the original response preprocessor exactly once, then source target
strip/lower and response lower feed `ExactSpec(substring=True)` with casefold
and whitespace normalization disabled. Internal newlines remain significant.
This is literal substring containment, with no keyword boundary added. The new
exact option defaults to false and requires a single nonempty normalized target.
Empty targets previously scored one in the source; they now abort the whole
mixed batch without a partial aggregate. Reference preprocessing never uses
the response control-character transformation.

All-config guards, three seeded actual evaluator witnesses, source preprocessing
call counts, source-empty-target regression and before/after evidence are under
`evidence/e2e/wiring/harness-babilong`. Scorer/helper/metric/filter drift aborts
before filters execute. The tracker/local artifact census found no named matching
saved runs; validation uses source fixtures rather than archived traces.

### MMMU typed answers

Apply `mmmu-typed-verifyit.patch` after `babilong-substring-verifyit.patch`.
This adds guarded native scoring for all 30 subject configurations. Source image
and prompt construction, answer extraction and two-decimal normalization remain;
verifyit grades choice alternatives with MCQ, prepared numeric values with zero
tolerance NumericSpec, and strings with strict substring ExactSpec. Source padding
for single-character references remains significant.

Missing choice extraction returns zero instead of randomly guessing. Empty or
nonfinite references abort evaluation without a partial aggregate; nonfinite
candidates receive zero. Ordinary multimodal fixtures preserve sample scores,
normal stderr and actual image arguments. All 30 guards, three seeded evaluator
witnesses and five early drift failures pass. The untouched evaluator separately
reproduces positive scores for empty gold, infinite gold and random guessing.
Evidence is under `evidence/e2e/wiring/harness-mmmu`; no eligible saved MMMU
model-run artifacts were found, so this is source-fixture validation.

The exported source patch requires the API revision containing `harness_mmmu`.
An earlier installed Babilong revision must use its earlier source-patch prefix,
or the untouched source checkout for baseline comparisons.

## CaBBQ and EsBBQ

Apply `bbq-mcq-verifyit.patch` after the Evalchemy Uncheatable, DROP and
HumanEval source patches. Set task metadata `verifyit_bbq: true` to enable the
20 pinned CaBBQ/EsBBQ category configurations.

The source's first maximum likelihood choice uses verifyit's existing MCQ
primitive. All nine unknown-answer alternatives map to label 2. Source bias
classification, observation tuples and corpus aggregators remain; their signed
bias values are not correctness rewards. All eleven likelihoods must be finite.
Malformed metadata, missing alternatives, changed scoring configuration and
undefined corpus aggregates abort evaluation without partial results.

Each of the 20 configurations preserves all four sample observations and corpus
metrics in five source evaluator fixtures, including ties and the final unknown
alternative. Regression checks reject a NaN likelihood that the source previously
counted correct and a bias aggregate with a missing comparison population.
Evidence is under `evidence/e2e/wiring/harness-bbq`; no archived replay is claimed.

## LIBRA length-group metrics

Apply `libra-primitives-verifyit.patch` after the BBQ patch and install the
harness `libra` extra. It pins the tested pymorphy3 normalizer and Russian
dictionary; the source extra previously named pymorphy2 despite importing
pymorphy3. Set task metadata `verifyit_libra: true` for the 18 configurations.

Source morphology and length grouping remain. Existing exact substring, token
F1 over characters, and exact comparison of extracted numbers calculate the
three scoring profiles. Empty normalized references and nonstring predictions
abort the whole evaluation before it returns grouped metrics. All 18 evaluator
fixtures match source observations and per-length aggregates; 21 invalid-data
and configuration cases abort without partial results.

The source takes the first positive score while iterating a reference set.
This behavior remains sensitive to Python's hash seed: the same F1 example
scores 0.8 under seeds 0/3 and 0.857142857 under seeds 1/2 in both implementations.
Evidence is in `evidence/e2e/wiring/harness-libra`. These are source fixtures;
archived replay is not claimed.

## MLQA language pairs

Apply `mlqa-primitives-verifyit.patch` after the LIBRA patch and set task
metadata `verifyit_mlqa: true`. The 49 configurations listed in
`mlqa-source.json` retain source language-specific article removal, Unicode
punctuation handling and Chinese segmentation. Normalized answers feed strict
exact comparison and the existing token-F1 primitive; each metric selects the
best reference independently and uses source mean aggregation.

References that normalize to empty text invalidate the task instead of awarding
an empty response an exact match. Malformed predictions and changed scoring,
filter or aggregation contracts abort the whole evaluation before results return.
All 49 configurations match source per-sample and aggregate scores on evaluator
fixtures. Seven language-specific empty-reference regressions and 49 invalid
batches pass. Evidence is in `evidence/e2e/wiring/harness-mlqa`; archived replay
remains unvalidated because the tracker contains no matching MLQA runs.

## LongBench metrics

Apply `longbench-primitives-verifyit.patch` after the MLQA patch, install the
pinned `longbench` extra and set task metadata `verifyit_longbench: true`.
`longbench-source.json` enumerates 34 configurations: 21 compose existing
exact and token-F1 primitives, and 13 run the source ROUGE or fuzzy code-similarity
metric through ScriptSpec. Source normalization, Chinese segmentation, numeric
match fractions, overlapping class handling and mean aggregation are preserved.
The code-similarity route requires the audited difflib backend; installations
using optional python-Levenshtein are rejected.

Empty references and malformed predictions invalidate the whole evaluation.
In particular, empty code references can no longer award blank output full
similarity. Invalid tasks remain distinct from runtime failures, and both abort
without returning partial aggregates. All 34 configurations match source scores
on evaluator fixtures, including partial credit and alternative references.
Evidence is in `evidence/e2e/wiring/harness-longbench`. Matching archived runs
were unavailable in the tracker; this validation does not claim archive replay.
