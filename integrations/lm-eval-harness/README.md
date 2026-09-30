The patch targets EleutherAI/lm-evaluation-harness v0.4.12,
`6d642546f4688648fced259eb3302efd36ece5af`, which Evalchemy pins.
Install the campaign verifyit package in the evaluation environment and apply
`verifyit.patch` with `git apply` from the harness checkout.

The evaluator calls `verifyit.adapters.lm_eval.score_task` after harness filters.
It consumes `.metrics`, retaining every original metric value and the original
harness aggregators. This is compatibility integration: the source scorer still
owns benchmark semantics. No scalar reward is implicitly selected. No model or
dataset download is needed to apply the patch.

For external consumers, `score_task(task, doc, filtered_responses, reward_metric)`
returns source metrics plus an optional verifyit `Reward`. `aggregate_task` calls
source aggregators with original per-sample values, including tuples used for
weighted perplexity. Selecting an absent, structured, unbounded or nonfinite
metric returns `invalid_task` while retaining metrics. Scorer/aggregator exceptions
propagate to the integration's infrastructure boundary. A wrong candidate's valid
zero metric produces `scored`, never an infrastructure failure.


The initial bridge implementation is local verifyit commit
`545ae96c553b171b09d4ee108df7c3d06879497d` on `codex/verifier-unification`.
It has not been pushed and is not installable from a GitHub revision URL.
Use a local checkout or built wheel for validation. The current Evalchemy patch
also requires the subsequent `math_answer_text` API refinement; its final
implementation revision must be recorded after that checkpoint is committed.
Do not pin only the initial commit for the latest patch.
