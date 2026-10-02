---
name: add-integration
description: Add or consolidate a client framework's verifyit integration using existing grading primitives and minimal reusable extensions.
---

# Add an integration

Follow [repository ownership rules](../../../AGENTS.md#integration-ownership).
The deliverable is an opt-in client path with a stated supported contract and
reproducible installation instructions.

## Establish the contract

Read the actual producer, task specification, source grader, and framework call
sites at recorded revisions. Inspect real task records and emitted responses;
benchmark names and standalone grading functions do not establish the contract.
Include filters, extraction, reference alternatives, nulls, normalization,
rounding, aggregation, and reported metric direction where they affect results.
Separate bounded reward from diagnostic statistics such as perplexity.

State the supported task variants and entry points. A single language, filter,
or ordinary one-completion path does not establish support for every variant or
the general multi-completion API. Make unsupported opt-in inputs fail explicitly.
If internal source callables are part of the contract, reuse existing validation
of their pinned source and selected callable identity; matching a name is not enough.

## Choose the smallest shared implementation

Map each grading decision to an existing primitive or reducer before editing.
Adapters can prepare tokens, counts, rows, tool observations, and primitive specs;
the primitive must decide their correctness. Keep benchmark dispatch and runtime
assets in the client. For code execution, protect trusted checks and result
production from candidate modification or forgery. Choose the required process,
filesystem, or container boundary for the execution contract; separate containers
are not a universal requirement.

Search existing parsers, execution helpers, and consumers before adding an API.
If a contract cannot be expressed, describe the missing operation and propose a
minimal extension of the existing primitive. Specify policies that change the
answer, including multiplicity, empty references, missing observations, and
rounding. Avoid per-benchmark flags or callback-based source grading hidden in a
generic helper. Compare total production code added and removed across owners.

Validate trusted inputs before candidate-dependent early returns or side effects.
Preserve scored-zero, invalid-task, and infrastructure outcomes through the client,
including stale reward removal where files are used. Never drop failed components
from a denominator. Treat malformed or unrepresentable diagnostic results as
failures, not favorable values.

## Prepare in two stages

Use typed structural conversion followed by policy preparation. Structural
conversion preserves the information needed by the declared grading contract;
answer selection, coercion, truncation, reordering, or filtering may change grades
and must not be assumed safe. Name grade-affecting policies, preserve source
behavior by default, and record the effective policy and input provenance.
Preparation errors stop grading and retain candidate/task/infrastructure identity.
Import the released `harbor_config.errors.ErrorCategory` and `error_category`
API directly, with a declared package version/dependency. The reviewed Evalchemy configuration release has no error
taxonomy to import. Keep heavy framework runtimes excluded.

For every added structural-conversion or policy-preparation function, obtain an
independent clean-room [audit](../audit-preparation/SKILL.md) before acceptance or
publication. Implement one representative path first, then migrate callers in
reviewable stages. Defer a factory abstraction until a separate decision approves it.

## Wire and verify

Preserve the disabled source path, including optional-dependency behavior. Install
client and companion packages from immutable revisions when publishing a cutover;
document required extras, image builds or registry digests, and the actual opt-in
command. A local image ID or checkout-only import is not a reproducible install.

Use [test-integration](../test-integration/SKILL.md) for actual framework proofs.
When reading source fixes or finding edge cases, check the counterpart's existing
coverage and add a meaningful regression if it is missing, following
[write-tests](../write-tests/SKILL.md). Document deliberate behavior changes and
unresolved contracts. Do not preserve a demonstrated source fail-open solely for
parity; make the intended task policy and resulting difference reviewable.
