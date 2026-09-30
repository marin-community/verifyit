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
`a4b0602a2f03b7864f7d7da35d374b7007b348f1`, including the AfroBench and corpus runtime APIs.
Apply `dependency-pin.patch` to declare that exact implementation in the source
project metadata. This commit remains local and unpublished: the remote Git URL
in the dependency patch is a publication target, not an available installation.
Evalchemy's lockfile must be regenerated when that dependency becomes fetchable.
For current validation in an environment with the pinned project's existing
dependencies installed, use the local Git commit and install the patched source
without resolving the unpublished remote dependency:

```bash
uv pip install --python /path/to/environment/bin/python 'verifyit @ git+file:///path/to/verifyit@a4b0602a2f03b7864f7d7da35d374b7007b348f1'
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
single-rank batch route for 868 translation and 40 default rolling-likelihood
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
