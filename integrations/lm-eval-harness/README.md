Current working-tree native extensions require the next implementation checkpoint:
`ExactSpec.strip_outer_whitespace`, `MathSpec.profile`, and native harness routing.
The existing dependency-pin.patch records the earlier API checkpoint and must be
updated to the actual new commit before distributing this expanded patch. Local
validation currently uses the campaign working tree; no remote availability is claimed.

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
`91c55a49599fcdead3475f009e62da4e30ca4f27`, including `math_answer_text`.
Apply `dependency-pin.patch` to declare that exact implementation in the source
project metadata. This commit remains local and unpublished: the remote Git URL
in the dependency patch is a publication target, not an available installation.
Evalchemy's lockfile must be regenerated when that dependency becomes fetchable.
For current validation in an environment with the pinned project's existing
dependencies installed, use the local Git commit and install the patched source
without resolving the unpublished remote dependency:

```bash
uv pip install --python /path/to/environment/bin/python 'verifyit @ git+file:///path/to/verifyit@91c55a49599fcdead3475f009e62da4e30ca4f27'
uv pip install --python /path/to/environment/bin/python --no-deps /path/to/patched-project
```

An isolated core-only installation from this exact local Git revision was
validated: completed reasoning-only boxes are accepted, truncated reasoning is
rejected, and extracted MCQ choices produce the expected scalar score. No remote
publication or live model endpoint was used.
