# Task Trove integration

The source pipeline patch applies to Marin
`b76d03131cd88bd9fc711dba206659027edba3a8`. Apply `verifyit.patch` at that
checkout root. Converter imports and generated checker environment accesses
use verifyit. Generated task images install the declared mode extras and map
old judge capability variables only when the corresponding new variable is absent.

The compatible verifyit API pin is
`91c55a49599fcdead3475f009e62da4e30ca4f27`. This commit is local and unpublished;
remote installation requires publishing that exact commit. For local validation,
install the corresponding local Git checkout instead. No dependency on a floating
branch is intended.

Before running the patched pipeline, run this directory's `install-host.sh <SHA>`
at the Marin checkout root. It declares `verifyit[all]` in the host `pyproject.toml`
and regenerates `uv.lock`. Commit both files so Marin's normal remote launch
propagates the same dependency to workers; a host-only pip installation does not
establish worker availability. Use the same verifyit revision explicitly:

```sh
uv run python -m experiments.post_training.tasktrove.pipeline --tool-ref <SHA>
```

The option is required and validates a full immutable SHA. Marin launch provenance
is checked separately and never substituted as a verifyit revision. Docker audit
requires `--tool-dir /path/to/verifyit` and copies that checkout into the build
context. Its generated local install retains mode extras and the Python floor.

For an extracted release task from
`open-athena/task-trove@9065fa568394f286dab0081e43dc76fc87c48984`, install the
pinned verifyit and declared mode extras in its image, then run:

```sh
python integrations/task-trove/migrate.py /path/to/extracted-task
```

The task-owned migration leaves original checkers and data unchanged. Script
specs invoke a wrapper that translates the execution-time tests/workspace/temporary
logs paths before running the original script with its arguments. Setup commands
receive equivalent legacy path variables. Other spec fields, including literal
expected answers, are preserved. Repeating the migration is idempotent.

The installed `tests/test.sh` maps TASKTROVE_JUDGE_{BASE_URL,API_KEY,MODEL} into
VERIFYIT equivalents only when new settings are absent; explicit empty settings
win. It prints no credentials. Missing or malformed judge capability remains an
infrastructure failure rather than candidate zero. The source code, metadata,
and drift/regression matrix are linked in [the Task Trove reference](../../docs/unification/task_trove.md).
No task archives, solutions, or deployment credentials are tracked.
