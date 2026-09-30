# Harbor mapping

[The inventory](harbor_inventory.json) pins Harbor to
`6f94f2237224869a49c249a737d701147afc33b6`. It enumerates 87 adapters,
115 tracked task configurations and 128 executable test entrypoints. Each
adapter has file hashes and function locations for its verifier templates or
generators. [The semantic table](harbor_semantics.json) specifies concrete
primitive routes and score/extraction caveats for all 87 adapters. The generator
rejects new or removed adapters until their semantic contracts are reviewed.
Regenerate:

```sh
python tools/unification/harbor_inventory.py /path/to/harbor \
  --output docs/unification/harbor_inventory.json
```

Harbor's default verifier runs the task's own `tests/test.sh` or `test.bat`
inside its task environment and reads `/logs/verifier/reward.json` before
`reward.txt`. JSON supports a map of named numeric metrics. Script exit failure
with a valid reward is scored; failure without a reward is a classified runtime
error. Success without a reward is a task-authoring error. Environment upload,
download and deadline failures remain exceptions. Shared/separate verifier
containers and multi-step test overlays are runtime concerns owned by Harbor.

Clean test-suite routes map to `pytest`, `junit` and `gotest`; answer routes
map to `exact`, `mcq`, `numeric`, `json-schema` and `reasoning-gym`; Dolci adds
`math`, `stdio` and `ifeval`. Hosted judges require explicit native profiles.
Custom SQL/state/metric/artifact evaluators retain `script` only where those
checks have no clean primitive equivalent. Migration must redirect reward files into
`VERIFYIT_LOGS_DIR`, retain dependencies, services, working directory and hidden
test restoration, and explicitly choose `reward_key` for named metrics. Numeric
auxiliary metrics are retained in verdict detail. The selected scalar keeps
verifyit's existing [0,1] reward contract; out-of-range values continue to score
zero with the reported value in detail. Thus native unbounded/negative metrics
need an explicit benchmark transform before migration. This behavior is a
compatibility limit, not a faithful automatic mapping for every metric.

[The remote inventory](harbor_remote_inventory.json) closes the two remote
body gaps. CompileBench has 15 pytest task suites pinned to commit
`66e27468505706643088b79f8efad6260c274dc5`. DeepSWE’s declared registry digest
resolves 113 task archives: 35 use JUnit and 78 CTRF. Public metadata and only
3,759,388 archive bytes were retrieved; tests/configuration files were retained
and environment blobs were discarded. Every task includes source hashes,
report configuration and required/protected ID counts. [Extension specs](harbor_specs.md)
cover CTRF, judge profiles, artifact judges, native score transforms and decimal
rounding without adding verifier categories. Adapter and spec-needed routes
are explicit; executable parity is not implied by discovery or source review.
External custom `verifier.import_path` implementations remain outside the
repository's discoverable population.

[The fork patch](../../integrations/harbor/verifyit.patch) makes the default
Harbor verifier invoke verifyit when a task ships `tests/verifier.toml`; legacy
tasks retain their harness. The image must install verifyit and supply its
optional extras. The patch checks `verdict.json` before parsing reward files,
so an invalid task or infrastructure error cannot become a candidate zero.
It retains Harbor's outer deadline and artifact transfer. Its source patch
applies cleanly to the pinned revision. Three local integration regressions
pass using Harbor’s real verifier, a fake sandbox I/O boundary, and verifyit’s
real CLI: two unscored statuses reject stale rewards, and a declared spec
executes verifyit instead of the legacy harness. Container execution and the
complete upstream Harbor test suite still require validation before deployment.
The existing 12 local verifier tests also pass against the patched source.

Harbor's recent verifier-runtime crash classification protects deleted working
directories and OOM exits from being interpreted as missing rewards. Existing
verifyit coverage already checks a failed script without reward is an
infrastructure error and a failed script with reward remains scored. This
campaign reproduced a separate hole: malformed numeric authoritative files
fell through to valid stdout. Regression coverage now verifies the public
verdict is `infra_error` and stale scalar reward artifacts are removed.

DeepSWE’s shared grader merges duplicate test observations with failures winning.
Verifyit previously allowed a later passing duplicate to erase a failure in
JUnit, Go and pytest reports. Source-derived regressions reproduced that error
through public grading APIs; the parsers now retain failures for the same ID
within/across reports while keeping different class/package identities distinct.
Skipped-only observations retain their existing treatment. ARC-AGI-2 source
Python equality accepts boolean grid cells as integers; a typed constant JSON
schema covers the intended integer-grid contract, with a regression showing
valid integers pass and booleans fail. This tightening is explicitly different
from native permissive comparison.

## Client reuse and tested boundaries

All 87source contracts can use existing verifier categories; no unavoidable new
category is identified. 52entries specify an answer/report/judge primitive route;
35 retain custom native runtimes. Of those runtimes, tau3 has an executable
status-preserving client bridge, while 34remain client migration proposals.
The 19earlier extension proposals are client normalization/composition candidates,
not 19new categories: rounded decimal answers can be normalized before Exact,
CTRF can be converted to identity-preserving JUnit, and native judge/artifact
runtimes can emit structured ScriptSpec verdicts. Those proposals are not
claimed as tested implementations. Unbounded R2 cannot be projected without
a declared benchmark policy.

[Tau3's client patch](../../integrations/harbor/tau3-verifyit.patch) retains its
native evaluator and emits the existing scored/invalid_task/infra_error schema
through ScriptSpec.verdict_file. Valid zero remains scored; missing/invalid
runtime logs and caught runtime failures remain unscored with reward 0. Native
reward metadata is retained under detail.native. Five actual pinned-source
CLI/boundary cases verify this projection; the local regression runs a separate
native-result producer. No deployed tau2 runtime parity is claimed. Tau2's
similar native error statuses and GDB's import/benchmark/evaluation-error zero
paths remain explicit client status gaps in the semantic table.

Current verifyit script producers fail closed on nonzero exits even when they
write positive rewards. The structured verdict is authoritative and cannot be
replaced by scalar stdout. JUnit report paths are declared outputs: existing
matching files are removed before execution, after restore/setup, and paths
resolving outside the workspace are rejected before deletion. Interrupted
pytest and incomplete Go test/package streams cannot earn a positive reward.
