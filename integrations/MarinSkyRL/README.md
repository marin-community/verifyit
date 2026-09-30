# MarinSkyRL integration

Source pin: `91c7a60e85e31b6933ab0ee732125b3338e82b89`. Apply the MCQ,
arithmetic and client-boundaries patches, then `reasoning-mcq-verifyit.patch`,
`tool-comparison-verifyit.patch` and `qa-verifyit.patch`. Apply the dependency pin
patch last. The latter pins the local
verifyit implementation checkpoint and raises the standalone gym Python floor
to >=3.11 and includes the `schema` and `reasoning-gym` extras. The source SHA must exist on the remote before external
installation. Do not silently replace a pinned Git dependency with a floating
branch. Regenerate fork locks in the fork's supported environment before use.

The MCQ patch retains source strict first-box extraction and binary reward,
and calls verifyit only for candidate correctness. Arithmetic patches retain
source AIME rational and strict-box equality, signed reward/length shaping, GSM8K final-line
and strict-first-marker equality. The original multi-turn controller retains format reward,
termination, and feedback. Client boundaries also route Search QA EM, rounded chemistry,
and both ARC grid comparisons through exact after source extraction/execution.
Malformed candidate grid cells retain rejection; invalid reference grids and nonfinite
chemistry references now fail closed rather than exploiting Python equality or raising during rounding.
The dependency pin includes the Exact/Math options, expanded client adapters and
fail-closed boundaries used by these patches.
Patched source regressions and verifyit API regression
counts are recorded in [the mapping](../../docs/unification/skyrl.md).

Real registered-environment replay validated 66 randomly selected execution links
from the complete eligible local artifact population: all matched pinned native
results and invoked installed verifyit. The [mapping](../../docs/unification/skyrl.md)
records population scope, one archive producer mismatch, and missing route traces.
GSM8K strict/final-line rejection now calls the client before source reward projection,
so missing markers remain zero while still producing a verifyit verdict.

The [coverage report](../../docs/unification/coverage-gaps.md) tracks eight later
opt-in cutovers. Reasoning Gym and Nemotron MCQA matched nine selected real
traces; the two tool-comparison routes with saved SkyRL Gym traces matched six.
The SWE pivot tool route and two exported QA APIs have no eligible real trace.
The tool comparator uses exact, numeric and JSON-schema primitives for typed
arguments and message actions. It rejects a boolean candidate for an integer
reference, which the source comparator accepts through Python's bool/int equality.
The campaign evidence is under `evidence/e2e/wiring/skyrl-reasoning-mcq/`,
`evidence/e2e/wiring/skyrl-tools/` and `evidence/e2e/wiring/skyrl-qa/`.


Apply `calendar-verifyit.patch` after `reasoning-mcq-verifyit.patch` to enable the
calendar task harness with `verifyit_enabled = true` in Nemotron environment config.
Its trusted ScriptSpec checker preserves valid source schedule semantics and rejects
malformed candidates/tasks with zero. Twelve source tests and three selected real
framework replays pass; evidence is under `evidence/e2e/wiring/skyrl-calendar`.
