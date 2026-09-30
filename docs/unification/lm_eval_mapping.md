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
Static discovery does not prove a dynamically registered task's scoring parity.
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
