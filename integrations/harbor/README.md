# Harbor integration

Apply `verifyit.patch` to Harbor
`6f94f2237224869a49c249a737d701147afc33b6`. Install verifyit and the extras
required by each task's `tests/verifier.toml` inside the verifier image. The
patch uses the installed console entrypoint; `python -m verifyit.grade` does
not execute the CLI. The task runtime retains Harbor's environment, hidden
file upload, artifact collection and outer deadline.

The patch checks `verdict.json` before scalar reward files and raises for
`invalid_task`/`infra_error`, preventing stale rewards from masking unscored
runs. Three added tests use the actual Harbor verifier and verifyit console
command behind a local sandbox boundary; 12 existing verifier tests pass.
Run `tests/unit/test_verifier_verifyit.py` with pytest-asyncio auto mode and
verifyit installed, then the original verifier tests. Container deployment is
not established by these local tests. The upstream task images and mode extras
remain necessary. See [the mapping](../../docs/unification/harbor.md) and
[extension specs](../../docs/unification/harbor_specs.md).
