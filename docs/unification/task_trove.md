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

The original graders implement the same spec dataclasses and modes. Seven
mode implementations are byte-identical after changing the package import
from tasktrove_verify to verifyit: csv-columns, gotest, ifeval, json-schema,
junit, reasoning-gym and xml-elements. The release uses no gotest or junit
rows. Other implementations have changed in verifyit; their regression review
belongs to the corresponding primitive. Dataset metadata proves routing and
population completeness. It does not prove every embedded archive faithfully
contains its declared mode. The 2.6 GB task archive was not downloaded.

Integration uses each archive's `tests/verifier.toml` with verifyit's CLI.
Replace the old package installation and module invocation in task images;
retain workspace, restored test paths, protected passing test identities,
judge model/base URL/API key, extraction options and per-test evidence.
Missing judge capability must remain an infrastructure error. Preserve the
release's retained-task policy: the 877,478 excluded upstream input rows are
not part of this dataset and must not be silently reintroduced.

Modes `script` and `stdio` retain task-specific executable checks, including
special judges; they do not become answer comparisons. The existing scalar
reward contract is [0,1]. Judge, reasoning-gym and partial-credit modes need
their declared score semantics preserved. Do not infer correctness from mode
names alone when adapting new task releases.
