# Dormant math integration

Source: MarinSkyRL `91c7a60e85e31b6933ab0ee732125b3338e82b89`. Apply
`dormant-math-verifyit.patch` and the dependency pin, which includes verifyit
`cd4c4a9be9200a4da6d722503d04bc5408e98f17` and its `answer` extra. Standalone
agent installs can select `skyrl-agent[verifyit]` on Python >=3.11.

ToRL and DAPO opt in through the trusted `GeneralReactTask` instance's
`verifyit_enabled = true` field, or the class attribute. PRIME's exported
`compute_score` accepts the same keyword. Defaults retain source dispatch.
Extraction and source pure string normalization remain in the client. Scoring
uses existing exact, numeric and math APIs; ordered collections retain their
endpoints, and candidate matrix lists become numeric LaTeX matrices after safe
literal parsing. Bounded arithmetic interpretation supports the source's two pi
approximations. Candidate expressions never reach Python eval or source graders.

Binary PRIME/DAPO rewards retain their score/acc fields. ToRL retains +1/-1 and
its v2 wrong-answer score -0.5 when a boxed answer is recognized; missing format gets -1; invalid references or failed verifiers receive
its minimum -1. Backend timeouts become infrastructure failures in verifyit.
Nonfinite numbers, malformed structures, boolean matrix cells and executable
Python expressions reject. These deliberate checks tighten unsafe source behavior.

The 76 source tests exercise exported APIs and the real dormant task dispatch.
The 48 benign native/cutover fixture comparisons have eight documented changes:

- DAPO pi: its source fallback passes misspelled `tiemout` (naive_dapo.py:514).
- Both matrix cases: grader.py:286 onward checks an incorrectly escaped
  `"\begin{pmatrix}"` literal and uses candidate-derived eval. Safe matrix
  conversion and the math primitive produce the intended numeric equality.
- Both million expressions: source `_normalize` maps million to `*10^6`, but
  the integer-reference gate rejects that expression spelling; the symbolic
  fallback then uses the `timeout_limit` decorator as a context manager
  (grader.py:329,342,352), preventing the intended equivalence check.
- Both Point cases: grader.py:259 onward returns from comma comparison before
  reaching its Point projection at line279. The client performs that projection.
- ToRL `2x` versus `2`: raw math parsing reads the bare numeric prefix. Anchored
  parsing compares the complete expression and rejects this false positive.

Source hashes and exact line excerpts are recorded in campaign
`evidence/e2e/wiring/skyrl-dormant-math/source-contracts.json`. The comparison
runs with explicit multiprocessing `fork`, matching Linux source behavior.
Darwin's default spawn cannot pickle the original wrapped symbolic function;
that degraded native diagnostic remains separately preserved.

From the patched framework worktree, rerun:

```sh
PYTHONPATH="$PWD/skyrl-agent:$PWD/skyrl-gym:$PWD/skyrl-train" \
  .venv-replay/bin/python -m pytest skyrl-agent/tests/test_math_verifyit.py -q
PYTHONPATH="$PWD/skyrl-agent:$PWD/skyrl-gym:$PWD/skyrl-train" \
  .venv-replay/bin/python ../../evidence/e2e/wiring/skyrl-dormant-math/replay_fixtures.py \
  --native-start-method fork
```

No eligible archived trace exists for these dormant routes in the full
5,460-link census. Fixtures are source-boundary validation, not archived-trace
E2E proof or exhaustive mathematical acceptance equivalence.
