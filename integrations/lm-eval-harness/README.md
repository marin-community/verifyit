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
`7e3aa30d5f9fd8f90dfe1c5a23162d5ec5a8c296`, including the AfroBench and corpus runtime APIs.
Apply `dependency-pin.patch` to declare that exact implementation in the source
project metadata. This commit remains local and unpublished: the remote Git URL
in the dependency patch is a publication target, not an available installation.
Evalchemy's lockfile must be regenerated when that dependency becomes fetchable.
For current validation in an environment with the pinned project's existing
dependencies installed, use the local Git commit and install the patched source
without resolving the unpublished remote dependency:

```bash
uv pip install --python /path/to/environment/bin/python 'verifyit @ git+file:///path/to/verifyit@7e3aa30d5f9fd8f90dfe1c5a23162d5ec5a8c296'
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
