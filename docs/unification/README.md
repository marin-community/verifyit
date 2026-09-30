# Verifier unification reference

The campaign maps source verifiers to verifyit's existing primitives, records
explicit adapter specifications where semantics differ, and adds regression
coverage when source failures expose gaps in the counterpart. No new verifier
category is proposed. Source discovery, semantic mapping, implemented adaptation,
and executable parity are separate kinds of evidence.

The [coverage report](coverage-gaps.md) lists the remaining source routes and why
they are not native integrations. Its [entity register](coverage-gaps.json)
preserves the pinned source evidence and required change for each route. It
distinguishes missing client integration, missing profiles within existing modes,
implemented source fallbacks, and validation gaps. These counts apply only to the
source revisions below.

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
| [SkyRL patches](skyrl.md) | Twenty-six source routes now call existing primitives or their client APIs. The nine recent routes cover Reasoning Gym, Nemotron MCQA, three typed tool comparisons two dormant QA APIs and the task-owned calendar harness; both SQL routes use a trusted execution harness, and Lean executes its retained compiler under ScriptSpec; LCB/code generation isolate candidate execution in a sandbox. Three dormant math routes now use exact/numeric/math primitives with retained extraction and safe client normalization. | The earlier 66 selected replays remain recorded. The new Reasoning Gym/MCQA and tool cutovers match 18 selected real traces including three calendar cases; three additional SQL and three Lean traces match native and recorded results. Six random code traces reject missing code through verifyit; two separately selected genuine positives match native/archive results with real sandbox execution. Legacy SQL has fixture coverage but no eligible real trace; SWE pivot and the two dormant QA APIs have no eligible real trace. Tool comparison intentionally rejects boolean-as-integer acceptance in the source scorer. |
| [Evalchemy patch](../../integrations/evalchemy/README.md) | Six clean integrations (GPQA, MMLU-Pro, AIW, GSM8KPerturbed, opt-in JEEBench and AMC23); three boxed-math hybrids retain explicit missing-parse fallback. | 26 upstream extraction regressions and source exact/numeric parity cases pass. JEEBench constructor/extraction/evaluator fixtures preserve three repetitions and partial credit, with malformed references aborting batches; no matching saved traces. The other 33 custom benchmarks remain client/profile work. |
| [Harness patch](../../integrations/lm-eval-harness/README.md) | Guarded native contracts cover 11,191 statically eligible task configurations: 8,061 likelihood-choice, 2,785 exact-match, 45 AfriQA, 100 MasakhaNER and 100 MasakhaPOS and 31 TruthfulQA MC2 plus eight Hendrycks literal-math profiles and 19 AGIEval multi-answer choice configs plus 22 CrowS-Pairs preference and 20 Babilong substring configs. Source aggregation remains. | The new AfroBench profiles pass source API and evaluator fixture comparisons, with no matching saved model traces. Eligibility is not execution of every dataset. An additional 978 configs have opt-in single-rank ScriptSpec corpus routing; 523 remain without cutover. Corpus routing retains actual source metrics and has fixture-only validation. |
| [Harbor patches](../../integrations/harbor/README.md) | Four answer-file adapters call exact or MCQ primitives, and EvoEval, HumanEvalFix, BigCodeBench-Hard, AutoCodeBench, MMAU, CodePDE, ReplicationBench and CompileBench call the existing pytest route; BFCL, DABstep and tau3 retain source scorers behind structured ScriptSpec clients. Another 72 adapters need client integration. | The four answer clients match 12 pinned original task-script cases. Generated GAIA and nine pytest task images execute positive and negative verifyit cases through the actual Harbor Verifier. CodePDE covers all five PDE variants with the upstream nRMSE evaluator on bounded HDF5 fixtures and rejects forged candidate scores in adversarial checks. ReplicationBench preserves its nested comparator and artifact while rejecting boolean-as-number false positives and malformed trusted references. CompileBench's pinned Ubuntu and Alpine task images preserve source CTRF counts, fail closed on malformed tests, and reject three bounded candidate executable tamper attempts; its other 13 images and saved model rollouts remain unvalidated. BFCL and DABstep each match 11 bounded generated-image source/CLI/Harbor cases, including deliberate false-positive corrections and invalid trusted-task handling. Full-size CodePDE data, broader task instances, three other answer images and matching model traces remain unvalidated; AWS SSO expiry prevented BFCL tracker workspace replay. Tau3 retains separate real-run replay evidence. |
| [Task Trove integration](../../integrations/task-trove/README.md) | Explicit verifyit revision/dependency overlay, source converter migration, local Docker audit checkout, and task-owned archive script/setup namespace wrappers. | All rows' metadata scanned using bounded HTTP ranges; 19 converter and 12 mode/helper drift matrix; 8 local CLI integration cases; actual patched pipeline CLI and Dockerfile rewriting pass at scheduling/container I/O boundaries. |

Integration dependency patches record the required immutable API checkpoint.
They require a fetchable Git revision or the corresponding local checkout; an
unpushed local checkpoint does not establish published availability, updated
fork lockfiles, or deployed integration.

## Hardening evidence

The [replay report](e2e-replay.md) records 24 Evalchemy/harness runs matching
63,360 samples, 66/66 SkyRL pinned-native and 65/66 archived results, and 1,101
Harbor trials. Harbor's recovered zeros, infrastructure failures and database
discrepancies remain explicit exceptions; these replays do not establish full
dataset or deployment parity.

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
malformed judge replies counted as candidate outcomes. Declared report counts,
fresh JUnit output and completed test/package events prevent partial evidence
from awarding success. The central scalar/status/detail boundary rejects malformed
or nonfinite verdicts; only an explicit completed judge stop can award a score.
Judge failures now become
`infra_error`; valid judge zero remains a scored candidate. Candidate failure,
invalid task and infrastructure failure remain distinct, and unscored verdicts
remove scalar reward artifacts. Relevant tests exercise real subprocesses, local
HTTP endpoints, or the public verdict-writing boundary.

## Remaining scope and evidence limits

Most custom source semantics require adapters even when the execution primitive
exists. The linked specifications define request fields, comparison/aggregation,
status mapping, resource boundaries and regression fixtures. A `script` route
retaining the original scorer is an adapter mapping, not native equivalence.
Client composition and extensions of existing classes avoid new categories.
Unimplemented client routes and optional native-mode profiles remain explicit;
a contract specification is not executable parity.

A concrete reusable specification supplies the mapping when no clean primitive
mapping exists. The linked unimplemented profiles fulfill that mapping/specification role;
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
