# Task Trove mapping

The pinned release `open-athena/task-trove@9065fa568394f286dab0081e43dc76fc87c48984`
already carries tasktrove-verify specs from Marin
`b76d03131cd88bd9fc711dba206659027edba3a8`. Its 861,848 retained tasks map to
12 existing verifyit primitives; no new category is needed.

[The machine-readable inventory](task_trove_inventory.json) covers every row,
aggregated into 81 source/family/template/converter/mode cohorts. The scanner
retrieved 982,482 bytes using HTTP byte ranges, including the parquet footer
and five metadata columns across all 48 row groups. It rejects servers that
ignore ranges and rejects mode or source totals differing from the pinned
release manifest. It found 43 sources, 19 converters and 63 template IDs.

```sh
uv run --with pyarrow python tools/unification/task_trove_inventory.py \
  --output docs/unification/task_trove_inventory.json
```

[The converter and drift matrix](task_trove_contracts.json) pins all 19 converter
modules/functions, their metadata populations, all 12 retained mode files, and
the shared extraction, execution, IFEval, spec and dispatch helpers by SHA256.
It also records unused Go/JUnit implementations. Identical dispatcher files do
not imply helper parity: `two_responses` now requires exactly two distinct
answers without empty interior sections; Go/JUnit/pytest preserve failing
duplicate identities; stdio rejects nonzero candidate exits even with correct
stdout; malformed authoritative script rewards and incomplete judge replies
remain unscored. Each changed edge links to named counterpart regression tests.
No output-size bound was added to stdio.

The matrix is regenerated from the pinned captured source:

```sh
uv run python tools/unification/task_trove_contract_inventory.py /path/to/pinned-source \
  --output docs/unification/task_trove_contracts.json
```

Dataset metadata proves routing and population completeness, not every embedded
archive's fidelity to its declared mode. The 2.6 GB task archive was not downloaded.
[The executable integration](../../integrations/task-trove/README.md) supplies a
pipeline patch, explicit immutable verifyit revision, host/worker dependency
overlay, local Docker audit checkout selection, and an idempotent existing-task
migration. Original archive scripts keep their legacy path reads through a
task-owned execution wrapper; core verifyit adds no global namespace aliases.
Eight local integration regressions cover judge precedence, real CLI rewards,
dynamic script logs, unchanged literal task data, idempotence, and setup paths.
Independent actual patched-source tests cover missing/invalid/explicit tool-ref
CLI behavior and generated-to-local Dockerfile rewriting with different extras.
These tests stop at remote scheduling/container I/O boundaries; they do not
claim a deployed release build.

Preserve workspace/restored test paths, protected IDs, judge endpoint/key/model,
extraction options and per-test evidence. Missing judge capability remains an
infrastructure error. The 877,478 excluded upstream input rows remain excluded.

Modes `script` and `stdio` retain task-specific executable checks, including
special judges; they do not become answer comparisons. The existing scalar
reward contract is [0,1]. Judge, reasoning-gym and partial-credit modes need
their declared score semantics preserved. Do not infer correctness from mode
names alone when adapting new task releases.
