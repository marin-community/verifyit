# Harbor discovery snapshot

[The inventory](harbor_inventory.json) pins Harbor to
`6f94f2237224869a49c249a737d701147afc33b6`. It enumerates 87 adapters,
115 tracked task configurations and 128 executable test entrypoints. Each
adapter has file hashes for its verifier templates or generators. This is a
discovery checkpoint; per-adapter primitive semantics remain to be reviewed.
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

The reusable mapping for executable task harnesses is verifyit's existing
`script` primitive. It preserves domain-specific checks instead of replacing
them with inferred answer grading. Migration must redirect reward files into
`VERIFYIT_LOGS_DIR`, retain dependencies, services, working directory and hidden
test restoration, and explicitly choose `reward_key` for named metrics. Numeric
auxiliary metrics are retained in verdict detail. The selected scalar keeps
verifyit's existing [0,1] reward contract; out-of-range values continue to score
zero with the reported value in detail. Thus native unbounded/negative metrics
need an explicit benchmark transform before migration. This behavior is a
compatibility limit, not a faithful automatic mapping for every metric.

The inventory marks two remote-task adapters, `compilebench` and
`deepswe_litecontainer`, as `external-contract-needed`: their verifier bodies
are fetched elsewhere and this pinned repository does not establish those
contracts. Other adapters are `adapter`, not parity-verified. Hashing their
scripts establishes discovery coverage; it does not prove executable parity.
External custom `verifier.import_path` implementations are also outside the
repository's discoverable population. No new verifier category is justified
by these runtime gaps.

[The fork patch](../../tools/unification/harbor_verifyit.patch) makes the default
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
