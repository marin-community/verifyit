# Verifier unification reference

The campaign maps source verifiers to verifyit's existing primitives, records
explicit adapter specifications where semantics differ, and adds regression
coverage when source failures expose gaps in the counterpart. No new verifier
category is proposed. Source discovery, semantic mapping, implemented adaptation,
and executable parity are separate kinds of evidence.

## Pinned populations and mappings

| Source snapshot | Enumerated population | Mapping and specification evidence |
|---|---|---|
| [MarinSkyRL](skyrl.md), `91c7a60e85e31b6933ab0ee732125b3338e82b89` | 14 registered environments; 26 Nemotron Ultra agent routes; 9 dormant verifier/scorer routes; 48 mapping entries, with 26 IFEval checkers indexed | [Source-pinned inventory](skyrl.json); every entry links to a [reusable adapter contract](skyrl-adapter-specs.md) |
| [Harbor](harbor.md), `6f94f2237224869a49c249a737d701147afc33b6` | 87 adapters; 115 tracked task configurations; 128 executable test entrypoints | [Discovery inventory](harbor_inventory.json); [87 source-reviewed semantic mappings](harbor_semantics.json) |
| [Evalchemy](evalchemy_mapping.md), `e3f4a3d601896c437f37b0bd0a30e51651cce6d0` | 42 custom benchmark classes; 22 local harness overrides; 72 scoring entrypoints | [Inventory](evalchemy_inventory.json); mapping document specifies exact, math, instruction, judge, and execution profiles |
| [lm-eval-harness](lm_eval_mapping.md), `6d642546f4688648fced259eb3302efd36ece5af` (Evalchemy's v0.4.12 pin) | 13,982 configurations: 12,692 tasks, 834 groups, 456 templates; 123 scoring entrypoints | [Resolved configuration inventory](lm_eval_inventory.json); source metric and filter contracts; combined loader parity on 14,004 nonempty harness/override configurations |
| [Task Trove](task_trove.md), `open-athena/task-trove@9065fa568394f286dab0081e43dc76fc87c48984` | 861,848 retained rows; 81 mapping cohorts; 43 sources, 19 converters, 63 templates; 12 existing modes | [Full metadata inventory](task_trove_inventory.json); release grader pin `b76d03131cd88bd9fc711dba206659027edba3a8` |

Counts describe the pinned discoverable source populations. Runtime-expanded task
names, user-registered environments, external custom verifier imports, and remotely
fetched task bodies require their own source evidence. Dormant SkyRL code is
included separately from active dispatch. Group/template configurations describe
orchestration rather than independent correctness scorers.

## Implemented integrations

| Integration | Implemented behavior | Verification evidence |
|---|---|---|
| [SkyRL patches](skyrl.md) | Source first-box MCQ calls verifyit candidate scoring; normalized AIME rational and GSM8K final-line answers use exact arithmetic boundaries. Source strict-box extraction, ±1 reward and length shaping remain explicit. | Patches apply to pinned source; 18 patched MCQ source tests and 40 patched arithmetic source tests pass; 17 verifyit arithmetic regression cases. |
| [Evalchemy patch](../../integrations/evalchemy/README.md) | GPQA/MMLU extracted choices call verifyit; completion boundary preserves final-content precedence and completed reasoning-only math policy. Source box parsers/stops and aggregation remain. | Source scoring before/after parity probes; 26 upstream AIME24/AIME25, MATH500 and MMLU-Pro tests pass against patched validation tree. |
| [Harness patch](../../integrations/lm-eval-harness/README.md) | Filtered native responses call `score_task`; source metrics and aggregators remain intact. Explicit scalar projection is optional. | Structured weighted-perplexity and optional metric bridge tests; pinned loader parity covers configuration includes. This proves compatibility, not replacement by native primitive equivalents. |
| [Harbor patch](../../integrations/harbor/verifyit.patch) | Tasks shipping `tests/verifier.toml` invoke verifyit; unscored verdicts reject stale scalar reward artifacts. Legacy task harnesses remain supported. | Three real-verifier/local-CLI integration regressions and 12 existing verifier tests pass; container execution remains unverified. |
| Task Trove task specs | Existing archive `tests/verifier.toml` specifies primitive routing; installation/invocation must use verifyit while retaining task runtime and hidden/protected tests. | All rows' metadata scanned using bounded HTTP ranges. Historical mode/helper drift and archive namespace migration remain under audit; pipeline installation changes are not yet ready. |

The first implementation checkpoint is local commit
`545ae96c553b171b09d4ee108df7c3d06879497d` on `codex/verifier-unification`.
SkyRL's dependency patch pins this commit and raises its standalone gym Python
floor to >=3.11, as required by verifyit. An isolated local Git installation at
that SHA passed real helper grading. Later completion/judge/MCQ refinements need
their subsequent implementation checkpoint. Nothing here establishes a published
GitHub dependency, updated frozen fork locks, or deployed integration.

## Hardening evidence

[SkyRL's patch coverage matrix](skyrl.md#recent-patch-coverage) ties recent source
changes to existing or added counterpart regressions and identifies adapter-only
gaps. [Evalchemy's review](evalchemy_mapping.md) does the same for completion
fields, mathematical equivalence, code extraction and failure records. Harbor's
mapping documents source runtime failure classification and authoritative reward
file handling.

Concrete regression fixes include correct stdout followed by candidate crash,
MCQ word prefixes mistakenly accepted as option letters, exact large-number and
ratio boundaries, malformed authoritative reward files replaced by stdout,
repeated passing test observations erasing previous failures, and incomplete or
malformed judge replies counted as candidate outcomes. Judge failures now become
`infra_error`; valid judge zero remains a scored candidate. Candidate failure,
invalid task and infrastructure failure remain distinct, and unscored verdicts
remove scalar reward artifacts. Relevant tests exercise real subprocesses, local
HTTP endpoints, or the public verdict-writing boundary.

## Remaining scope and evidence limits

Most custom source semantics require adapters even when the execution primitive
exists. The linked specifications define request fields, comparison/aggregation,
status mapping, resource boundaries and regression fixtures. A `script` route
retaining the original scorer is an adapter mapping, not native equivalence.
Proposed Python profile APIs and mode profiles are not implemented merely because
they are specified.

The user permits a concrete reusable specification when no clean primitive mapping
exists. The linked unimplemented profiles fulfill that mapping/specification role;
they do not promise a completed runtime migration. Retained source scorers and
implemented bridges keep original dependencies and metric contracts. Any missing
source route, vague specification, or source patch with an untested existing
counterpart remains campaign work, rather than optional deployment validation.

Before deploying integrations, validate complete fork environments/lockfiles,
containers, dynamic extensions, source judge/registry/callable-code profiles and
per-test evidence. Those deployment checks are separate from mapping a pinned
source contract or specifying a reusable extension. Task Trove's metadata proves
routing for its retained population; downloading/executing the 2.6 GB embedded
archive is additional runtime validation, not required mapping evidence in the
absence of a discovered archive-contract discrepancy.

These artifacts provide a requirement-to-evidence index. They do not assert that
all migrations are complete or that the campaign goal has been achieved.
