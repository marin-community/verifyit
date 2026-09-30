# Partial coder1 integration

This opt-in client patch wires the pinned MarinSkyRL coder1 stdio, functional,
pytest, and solution_file payload forms through existing ScriptSpec, PytestSpec,
exact, and numeric graders. The whole coder1 route remains pending because the
source accepts arbitrary Python tests and the isolated proxy supports a bounded
subset of Python semantics.

Apply `dormant-math-verifyit.patch`, then `coder1-partial-verifyit.patch`, to
MarinSkyRL revision `91c7a60e85e31b6933ab0ee732125b3338e82b89`. Apply
`dependency-pin.patch` for the pinned verifyit implementation and pytest extra.
The framework requires its existing skyrl-gym SandboxClient and a working NeMo
Sandbox service; installing the standalone agent extra alone does not install
that runtime. Enable the existing task client flag `verifyit_enabled=True`.

Candidate code runs in isolated stateful sandbox sessions. Trusted assertions,
reference outputs, and verdict files remain outside those sessions. List/dict
identity, cycles, and mutations propagate through the bounded transport. Actual
candidate exceptions remain available to expected-exception tests; malformed
transport, nonfinite output, infrastructure failures, and failed cleanup cannot
produce a positive reward. Initialization and subsequent calls share a deadline.
The owning host removes predeclared sessions and terminates its nested pytest
process group even when the checker is killed.

Unsupported contracts return zero with an explicit unsupported-task result:
scalar/tuple identity, arbitrary class/type introspection, remote module bindings,
arrays/sets/bytes/custom host objects or callables as arguments, and unsupported
operator, conversion, hashing, context-manager, or async protocols. The admission
guards do not establish arbitrary Python equivalence. These limitations prevent
whole-route promotion.

Evidence lives in the campaign directory
`evidence/e2e/wiring/skyrl-coder1/`. Eight controlled GeneralReactTask cases cover
positive and wrong candidates for each form; pinned native Docker execution and
cutover execution agree on all eight. The manager independently executed both
sides. These are source-boundary fixtures, not archived trace replay: the full
5,460-item census contains no coder1 trace links.

The source suite passed 62 tests before the nested-process cleanup addition;
the subsequent focused run passed five tests, including that addition and all
four dispatch forms. The manager independently passed the nested cleanup test,
nonfinite transport exploit, graph identity, and metadata-collision regressions.
Run from the framework worktree:

```sh
.venv-replay/bin/python -m pytest skyrl-agent/tests/test_coder1_verifyit.py -q
```

The source before/after replay driver, commands, image digest, mounted source
hashes, raw verdicts, and precise pending contracts are saved beside
`native-provenance.json`, `manager-parity.json`, and `pending-contracts.json` in
that evidence directory. No archived E2E or complete coder1 coverage is claimed.
