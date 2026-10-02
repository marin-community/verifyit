---
name: test-integration
description: Validate a verifyit cutover through actual client framework execution, inspect reproducible source and core evidence, and report the supported coverage honestly.
---

# Test an integration

Read [TESTING.md](../../../TESTING.md) and the integration's supported contract.
Exercise the client entry point through verifyit and back to the reported result;
direct primitive tests supplement this roundtrip.

## Select evidence before running

Record task identities, source revisions, and input hashes. Prefer available
genuine archived responses. Freeze a reproducible selection from the relevant
population before scoring, with enough cases to cover distinct supported paths.
If archives are unavailable, genuine public tasks with controlled responses can
test integration; label them separately from archived model executions and
historical producer-score replay. Never replace a failing selected case with an
easier one. Supplement selections that contain no positive cases.

Run the original and enabled framework paths on identical task and candidate
inputs. Capture full per-item results and aggregate metrics, including counts,
status, metric direction, and relevant RNG or filter behavior. State narrowly
which nondeterministic fields are excluded from comparison.

## Prove the path and installation

Capture raw primitive inputs and verdicts, source callback observations where
fallback is possible, and the framework's returned results. Inspect these records
to establish that core grading executed and influenced the result; a manifest,
function name, or agent's success summary is insufficient. Read the adapter to
check that it does not still grade or discard the core result.

Before claiming a usable published cutover, run from a clean install with
immutable client, companion, and verifyit pins. Remove checkout overlays such as
`PYTHONPATH`; inspect actual imported paths, installed module bytes, dependency
metadata, and image identity against those revisions. Test the disabled path
without verifyit available when it is optional. Preserve failed install proofs.

Include a genuine positive path, wrong candidates, and meaningful failure controls
for the contract: invalid references before candidate handling, missing outputs,
provider or protocol errors, or a hanging candidate when execution is involved.
Check statuses and reward files, not only numeric equality. Protected tests and
reports must remain outside candidate control. Follow
[write-tests](../write-tests/SKILL.md) for durable regressions; keep replay harnesses
and bulky evidence in the task's external artifact directory.

## Bound runs and investigate differences

Coordinate the session's resource budget before launching work. Record owned
process groups, container identities, deadlines, and output locations in the
task's job record. A tool timeout or lost session handle does not mean the job
stopped: inspect the original run before retrying. Reap owned processes and remove
owned containers in cleanup, then verify their absence. Do not kill unrelated jobs.

Preserve failed evidence in separate run directories. Diagnose differences using
the same inputs, source semantics, dependency versions, and execution environment.
A runtime floating-point difference is not automatically a verifyit improvement.
Do not weaken assertions or invent tolerances to obtain parity. Rerun the affected
scope after a behavior change; avoid repeating unchanged successful cohorts.

## Report what passed

Link raw comparisons, installation provenance, and observed cleanup. Distinguish
primitive mapping, wired dispatch, tested subcontracts, and reviewed integration
coverage. State whether evidence covers a working tree or a clean installation
of immutable published revisions; checkout tests alone do not establish
deployment readiness. Count only the supported scope demonstrated by inspected evidence;
partial branches do not complete an umbrella benchmark. Keep task declarations,
unique tasks, and executions as separate denominators. Record unsupported paths,
deliberate deviations, and missing archives without treating any as a passed test.
