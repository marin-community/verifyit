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

## Consolidation phase

The previous integration campaign reached **155/196** required routes with its
then-current implementations and evidence. That historical count is not fresh
validation of the consolidated implementation. Fresh acceptance is **6/196** after six SkyRL judge routes passed archived-response
replays. Shared core validation passed 857 tests, with two Go tests skipped because
the host lacks Go. The required population remains: 46 SkyRL routes, 87 Harbor routes, 42 Evalchemy custom benchmarks and
21 Evalchemy overrides. TaskTrove and coder1 are excluded; harness mapping counts
remain report-only rather than an exhaustive replay requirement.

The first Evalchemy slice replaces per-answer Script subprocesses and duplicated
judge transport/parsing with the existing Judge mode. SimpleQA, SimpleQAMini,
FinanceBench, OlympiadBench and OlympiadBenchFull have fresh local-HTTP framework
replays, including failed batches and empty candidates. These five routes are
fixture-tested, with archived-trace validation still pending, so they add no
acceptance credit yet. The Evalchemy slice removes 86 client production lines and adds 54
shared core lines: 32 fewer production lines overall, excluding tests and docs.
The SkyRL slice removes 115 client lines and adds 78 shared execution lines, a
net reduction of 37. No verifier mode was added.

Historical mappings and trace evidence remain in the linked coverage register.
Fresh route status is summarized here independently of generated historical tables:

| Routes | Fresh evidence | Acceptance |
|---|---|---|
| [Six SkyRL judge profiles](../../integrations/MarinSkyRL/judge-profiles-consolidation-source.json) | 36 archived-response rounds with original source results and HTTP request comparison | 6 accepted |
| SimpleQA, SimpleQAMini, FinanceBench, OlympiadBench, OlympiadBenchFull | Seven framework scenarios, 30 direct Judge outcomes, 45 malformed-batch aborts and empty-candidate zero corrections | Fixture-tested; archived validation pending |

Raw replay receipts are retained under the campaign evidence directory, outside
this repository; they are not claimed as committed test assets. The repository's
Judge tests and exported client tests cover the reusable contracts. Regenerating
the historical coverage tables does not overwrite this phase section.

## Pinned populations and mappings

| Source snapshot | Enumerated population | Mapping and specification evidence |
|---|---|---|
| [MarinSkyRL](skyrl.md), `91c7a60e85e31b6933ab0ee732125b3338e82b89` | 14 registered environments; 27 source-declared Nemotron Ultra generators, including the unimplemented IPI route; dormant verifier/scorer routes and external objectives are reconciled in the current coverage register | [Source-pinned inventory](skyrl.json); every entry links to a [reusable adapter contract](skyrl-adapter-specs.md) |
| [Harbor](harbor.md), `6f94f2237224869a49c249a737d701147afc33b6` | 87 adapters; 115 tracked task configurations; 128 executable test entrypoints | [Discovery inventory](harbor_inventory.json); [87 source-reviewed semantic mappings](harbor_semantics.json) |
| [Evalchemy](evalchemy_mapping.md), `e3f4a3d601896c437f37b0bd0a30e51651cce6d0` | 42 custom benchmark classes; 22 local harness overrides; 72 scoring entrypoints | [Inventory](evalchemy_inventory.json); mapping document specifies exact, math, instruction, judge, and execution profiles |
| [lm-eval-harness](lm_eval_mapping.md), `6d642546f4688648fced259eb3302efd36ece5af` (Evalchemy's v0.4.12 pin) | 13,982 configurations: 12,692 tasks, 834 groups, 456 templates; 123 scoring entrypoints | [Resolved configuration inventory](lm_eval_inventory.json); source metric and filter contracts; combined loader parity on 14,004 nonempty harness/override configurations |
| [Task Trove](task_trove.md), `open-athena/task-trove@9065fa568394f286dab0081e43dc76fc87c48984` | 861,848 retained rows; 81 mapping cohorts; 43 sources, 19 converters, 63 templates; 12 existing modes | [Full metadata inventory](task_trove_inventory.json); release grader pin `b76d03131cd88bd9fc711dba206659027edba3a8` |

Counts describe the pinned discoverable source populations. Runtime-expanded task
names, user-registered environments, external custom verifier imports, and remotely
fetched task bodies require their own source evidence. Dormant SkyRL code is
included separately from active dispatch. Group/template configurations describe
orchestration rather than independent correctness scorers.

## Integration status and entrypoints

The [coverage report](coverage-gaps.md) and its generated
[entity register](coverage-gaps.json) are authoritative for current campaign
counts, remaining contracts, and accepted execution evidence. Earlier mapping
and replay documents below describe their individual checkpoints; their counts
must not be added together or treated as current completion totals.

| Integration | Entry point and scope |
|---|---|
| SkyRL | [Patch instructions](../../integrations/MarinSkyRL/README.md) and [adapter contracts](skyrl-adapter-specs.md) cover existing primitives, client extraction, source-owned registries, and retained runtimes. The current report includes the previously omitted IPI generator and restores abstention completion after the tested empty-response correction; the correction is exported but not claimed deployed on SkyRL main. Published current-main routes and the larger historical campaign inventory are separate populations. |
| Evalchemy | [Patch instructions](../../integrations/evalchemy/README.md) and the [tested configuration ledger](evals-tested-configs.json) distinguish custom benchmarks, harness overrides, retained source scorers, and actual evaluator evidence. |
| lm-eval-harness | [Patch instructions](../../integrations/lm-eval-harness/README.md) describe guarded native contracts and structured source-runtime routing. Available configurations are not all individually executed; exhaustive harness replay is outside the required completion cohort. |
| Harbor | [Patch instructions](../../integrations/harbor/README.md) record source-specific task generation, separate verifier images, native primitive clients, and retained-runtime bridges. The coverage report identifies each tested adapter, remaining integration work, shared verifier boundaries, and candidate execution trust limitations. |
| Task Trove | [Migration instructions](../../integrations/task-trove/README.md) cover revision overlays, converter migration, and archive script/setup namespaces. Metadata and fixture validation do not establish genuine archived-task execution; Task Trove is outside the required completion cohort. |

Integration dependency patches record immutable API checkpoints. A checkpoint
must be published or supplied by the documented local wheel/checkout recipe to
build its task image. Installing verifyit does not apply client patches, update
fork lockfiles, or deploy integrations. MarinSkyRL's published dependency pin is
recorded separately in its [publication manifest](../../integrations/MarinSkyRL/publication-latest-main.json).
Publishing this mono-branch also publishes its ancestor core revisions, including
`a0861089947096aabe456ca4308ca46b1b001d7c` and
`d3edc5d240d53edbd0c0e4a53c0e112629550f7e`. Earlier references to those
revisions as unpublished describe the proof-time environment; they do not imply
that client lockfiles or deployed images have been updated.

The [verifier-boundary register](coverage-gaps.md#shared-verifier-boundary)
tracks outstanding isolation work separately from integration and ordinary score
parity. Separate verifier images protect source artifacts from the agent
container; code graders that execute candidate code within the grading runtime
retain an additional trust limitation. Neither fixture parity nor a private image
alone establishes complete hardening.

## Historical replay evidence

The earlier [replay report](e2e-replay.md) records 24 Evalchemy/harness runs matching
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
