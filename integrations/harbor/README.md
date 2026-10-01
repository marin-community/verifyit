# Harbor runtime helpers

The opt-in Harbor client patch dispatches a task's `tests/verifier.toml` and
consumes verifyit's verdict and reward files. Install the verifier's optional
runtime dependencies in the task image. The helpers here do not install the
Harbor client patch.

The retained tau3 integration uses two helpers:

- `tau3_assets.py` builds trusted evaluator and database hashes from a pinned
  tau2 checkout during task generation.
- `tau3_bridge.py` invokes the task's native `evaluate.py` through `ScriptSpec`.
  Missing or invalid evaluator output is unscored with zero reward.

Generate the asset manifest and copy the bridge into a prepared tau3 task:

```bash
python integrations/harbor/tau3_assets.py "$TAU2_CHECKOUT" "$DOMAIN" "$TASK/tests/tau2-assets.json"
cp integrations/harbor/tau3_bridge.py "$TASK/tests/tau3_bridge.py"
```

The task must supply its trusted `config.json`, native evaluator, and tau2
runtime. Its ScriptSpec uses `path = "tau3_bridge.py"` and
`verdict_file = "result.json"`. This route retains the native evaluator.

Campaign patch exports and per-run provenance are stored outside the package
under `/Users/benfeuer/Documents/experiments/active/verifier-unification/artifacts/harbor`.
That directory contains the checksum manifest, application notes, and historical
validation limits. See the [unification overview](../../docs/unification/README.md)
for the current integration scope.
