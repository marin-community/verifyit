# lm-eval-harness mapping

Evalchemy pins EleutherAI/lm-evaluation-harness v0.4.12 at
`6d642546f4688648fced259eb3302efd36ece5af`.
[The generated inventory](lm_eval_inventory.json) resolves every discovered YAML
include and records original file hashes, task/group names, output types,
metrics, filter chains, custom scorer symbols and candidate primitives.

Discovery covers 13,982 configurations: 12,692 task configurations, 834 groups,
and 456 templates. These are configuration counts, not unique runtime-expanded
evaluation names. Discovery indexes all 2,839 task functions in the transient evidence directory;
the tracked manifest retains 123 scoring entry points and their call references.
Runtime discovery uses the actual pinned TaskManager, with its installed manager,
index, factory and loader files byte-equal to the source checkout. It enumerates
12,662 YAML tasks and 30 Python-class tasks: 12,692 unique task names, matching the
configuration inventory. It also finds 834 groups and 696 derived tags. The source
contains no separate `register_task` decorators outside this YAML/Python-class
index. Group source expansion adds 64 inline task definitions; every definition
receives an existing-mode/spec mapping and parent source evidence. Four consist
only of a name absent from the registry and are explicitly invalid configurations. Seven T0 group
members lack both task/group keys and are explicitly invalid task configurations,
not omitted verifier names. Tags select indexed tasks and add no scorer family.
The resolved configuration corpus matches the pinned loader for all 14,004
nonempty harness and override configurations; one empty commented template is
excluded. Shared reason, metric and filter contracts use IDs, and each source
record occupies one line. Omitted empty fields represent absent configuration.

| Source contract | Existing primitive / integration | Required preservation |
| --- | --- | --- |
| `multiple_choice` | Metric bridge; bounded `acc` can become reward | Conditional likelihood tuples, greedy flags, character/byte normalization, optional unconditional likelihoods for mutual information, all configured metrics |
| `loglikelihood` | Metric bridge | Log likelihood and greedy correctness; perplexity is an aggregate, not a bounded reward |
| `loglikelihood_rolling` | Metric bridge | `(loglikelihood, word/byte count)` values and weighted aggregates; preserve bits per byte |
| Generation `exact_match` | `exact` candidate; normalization adapter unresolved | Raw whitespace, lower versus casefold, punctuation/number/regex removal, filter chains, multiple targets |
| Hendrycks/Minerva/HRM math | `math` candidate; parity unresolved | Benchmark-specific box selection, string fallback equivalence, source parser anchors and answer cardinality |
| IFEval | `ifeval` candidate; registry and aggregate parity unresolved | Strict/loose instruction and prompt metrics, original transform chain and instruction parameters |
| Custom Python scorer / task class | Source metric bridge; primitive candidates recorded where known | Every source metric value and aggregator; benchmark semantics remain source-owned |
| Task group | Harness orchestration | Group expansion, metric weights, bootstrap errors and higher-is-better declarations |

The source of default scoring is `lm_eval.api.task.ConfigurableTask.process_results`.
The bridge's [integration patch](../../integrations/lm-eval-harness/README.md)
changes its evaluator call site to use verifyit while returning the same source
metrics. This is an implemented compatibility bridge, not evidence that a source
scorer has been replaced by an equivalent verifyit primitive.

The reusable bridge contract is implemented without a new mode or core dependency:
`score_task` processes already filtered responses, `aggregate_task` calls source
aggregators on original values, and `project_metrics` selects a named bounded
numeric reward only on explicit request. Invalid projection retains source
metrics and returns `invalid_task`; runtime scorer failures propagate. Perplexity,
counts, correlations, vectors and error records remain available without forcing
them into a `[0,1]` reward.

Regenerate both inventories with:

```bash
uv run --with pyyaml python tools/unification/eval_inventory.py --sources /path/to/campaign/sources
```

The discovery manifest deliberately labels unresolved primitive parity. Completion
requires resolving those cases through source parity tests or a concrete retained
source integration. Generation filters operate before the bridge; bypassing those
filters is not a supported migration.

## METRIC-CONTRACT: response and aggregation artifacts

This is the reusable specification for likelihood evaluations and custom metric
scorers whose complete outputs cannot be expressed as one existing scalar
verdict. It extends the integration API, with `script` as the task-image execution
primitive when a subprocess boundary is required. It adds no verifier category.

The task contract records immutable source revision, task/configuration hash,
scorer entry point, response output type, ordered filter definitions, complete
metric declarations, aggregators and higher-is-better flags. Inputs contain
candidate responses in their native shapes: strings for generation; ordered
`(conditional_loglikelihood, is_greedy)` pairs for choice scoring; unconditional
pairs when mutual information is declared; or one rolling log-likelihood value.
Trusted task entry points run in the task environment. Model inference and dataset
loading remain separate from verification. No inference is rerun by the bridge.

Per-sample output contains every emitted source metric, filter name and explicit
source failure record. Aggregation receives original typed values in order:
weighted perplexity consumes `(loglikelihood, count)` tuples, F1/MCC consume
`(gold,predicted)` pairs, Brier/likelihood metrics preserve probability or
likelihood vectors, and IFEval pools instruction vectors. A versioned artifact
codec explicitly distinguishes tuples, arrays and special numeric values if the
boundary is persisted; lossy implicit `str` conversion is forbidden. Until that
codec is implemented, the in-process `TaskResult` retains native objects and the
subprocess integration must use task-owned aggregate JSON metrics.

Selecting a reward is optional and explicit. A named finite numeric metric in
`[0,1]` maps to `scored`; source boolean accuracy fields may be converted to 0/1
only by a declared projection policy, since the current bridge rejects bool.
Structured/unbounded/nonfinite metrics remain metrics and an attempted invalid
projection is `invalid_task`. Do not rescale perplexity or invert lower-is-better
metrics implicitly. Preserve source defaults, denominators, skipped items and
bootstrap/group aggregation separately from scalar reward.

Task/config/hash or response-shape mismatches are `invalid_task`. Missing
execution engines/dependencies and unexpected scorer failures are `infra_error`.
Ordinary source candidate failures keep their original label and valid zero score.
The runner must clean up the process group on timeout, preserve failure records,
and remove stale scalar reward files on an unscored outcome. Partial worker or
judge failures stay attached to their trials; the source's aggregation policy
defines whether a dataset aggregate is reportable.

The current `score_task` / `aggregate_task` API implements the in-process metric
preservation/projection portion. The evaluator patch calls this API with actual
filtered responses. Declarative source identity validation, persisted typed
artifacts and task-specific failure schemas remain specified work. This distinction
is recorded per inventory row as `spec-needed`, rather than claiming the bridge
has replaced each benchmark scorer.

Acceptance tests compare actual pinned `ConfigurableTask.process_results` for
raw, character-normalized, byte-normalized and mutual-information choices,
negative log-likelihoods, greedy flags, multiple targets and invalid gold indices.
Compare weighted perplexity, F1/MCC and Brier aggregates without scalar projection;
round-trip typed persisted artifacts; exercise one optional metric emitted for
only some samples; assert zero versus malformed task versus failed infrastructure;
and retain partial trial failure records. The actual harness rolling scorer and
weighted-perplexity aggregator have already passed a focused in-process parity
probe using two documents with different word counts.

## Existing primitive profiles

Generation exact, math, official IFEval and label judges map to the proposed
[exact profile](evalchemy_mapping.md#exact-harness-exact-normalization-and-alternative-references),
[math profiles](evalchemy_mapping.md#math-profiles-symbolic-and-normalization-comparators),
[official registry profile](evalchemy_mapping.md#ifeval-registry-official-checker-profile-and-result-vectors)
and [classifier profile](evalchemy_mapping.md#judge-classifier-explicit-prompt-and-label-protocol).
These specifications state inputs, normalization, metrics, failures and acceptance
cases. Each relevant generated record names its required specification anchor.


Runtime population validation can be regenerated in the installed pinned harness
environment without loading datasets or models:

```bash
python tools/unification/eval_runtime_index.py --source /path/to/sources/lm-eval-harness --output /path/to/evidence/lm_eval_runtime_index.json
uv run --with pyyaml python tools/unification/eval_inventory.py --sources /path/to/sources --runtime-index /path/to/evidence/lm_eval_runtime_index.json
```

The runtime manifest records group overrides and inline definitions rather than
instantiating all group combinations. Those configurations use the same verified
source factory/scorer contracts. Some inline definitions retain `include` keys
that the pinned factory does not resolve; their declared include file hashes are
recorded separately. This is a source task-assembly defect, not evidence that
missing dataset metadata can be ignored by a verifier. The metric contract requires
explicit invalid-task configuration outcomes until the task adapter resolves and
validates that metadata.
