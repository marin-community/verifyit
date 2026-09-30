# Harbor integration

The coverage register identifies a shared-verifier boundary gap in 15 wired
Harbor routes. Harbor uploads their protected tests or references into the live
agent container before grading; a surviving candidate process can modify them.
A generated GAIA task reproduced the failure: the wrong answer `Boston` scored
one after the candidate changed the uploaded `New York` reference. Existing
source/CLI and generated-image parity cases establish grader behavior on bounded
fixtures, not protected-reference isolation. ARC-AGI-2 uses a separate verifier
image; the other wired routes require the boundary changes listed in the
[coverage report](../../docs/unification/coverage-gaps.md#shared-verifier-boundary)
before deployment. The GAIA reproduction is in
`evidence/e2e/wiring/harbor-answers/gaia-shared-reference-before.json`.

Apply `answer-routes.patch` to the pinned Harbor source for AIME, GAIA, GPQA
Diamond and SATBench. Their generated task scripts call the installed verifyit
answer client with source-specific extraction followed by exact or MCQ grading.
The four generated Dockerfiles pin verifyit
`08c14eaf912a940fc4e0401698f95b85250b0006`; this commit is local and must
be published before the remote Git install can resolve. All 12 original versus
patched task-script fixtures match when the pinned original runs in Docker.
One generated GAIA image was built with a wheel from the exact local commit and
ran positive and negative CLI cases. The local wheel replaced only the
unpublished remote install in that image. The other three task images and
matching saved model traces have not been validated. See
`evidence/e2e/wiring/harbor-answers/` for commands, hashes and verdicts.

Apply `arc-agi-2-separate-verifyit.patch` to the pinned Harbor source and pass
`--verifyit-enabled` when generating ARC-AGI-2 tasks. The agent image retains
the original task environment but contains no expected grid. Harbor transfers
only `/testbed/output.json` to a separate verifier image, which holds the
protected reference and calls verifyit's JSON-schema const grader. Rectangular
integer-grid checks reject source false positives from boolean and integral
float cells; invalid references remain unscored. Three seeded source-generated
test pairs matched original source, direct CLI and actual Harbor Trial positive
and wrong scores. A candidate background copier changed the shared-container
reference and falsely scored one before isolation; the same attack scored zero
with the separate verifier. Symlink and missing output, malformed reference,
and typed-cell cases were also checked. These are bounded fixtures, not saved
model rollouts or full benchmark accuracy validation. The generated verifier
Dockerfile pins local verifyit commit `2475a92bee1484c4db5fa35b1ff3efd7f2292bfe`;
the proof substituted an attested local wheel because the Git pin is not
published. Exact commands and hashes are in
`evidence/e2e/wiring/harbor-arc-agi-2/README.md`.

Apply `evoeval-pytest-verifyit.patch` after the Harbor dispatcher patch. The
generated EvoEval task declares `PytestSpec` over its protected test file;
verifyit's existing all-suite rule matches the source binary pytest result.
The task image installs `pytest-json-report` and verifyit
`1dd6292b54dd1c2525a1c1354d49940ba5ba6dbf`. A wheel built from that exact
local commit replaced only the unpublished remote install during image proof.
The generated image matched source test.sh, direct verifyit CLI and Harbor's
Verifier on one passing and one failing candidate. A malformed protected test
produced `infra_error` without a reward file. No matching saved model trace was
available. The reusable ScriptSpec bridge in that API commit is for task scripts
whose native reward policy cannot be represented by pytest directly.

Apply `humanevalfix-pytest-verifyit.patch` after the Harbor dispatcher patch.
Its generated task declares PytestSpec against protected `/tests/test_outputs.py`
while the candidate workspace remains `/workspace`.
The Python 3.12 task image installs `pytest-json-report` and verifyit
`1dd6292b54dd1c2525a1c1354d49940ba5ba6dbf`. A generated image matched
the pinned source script, verifyit CLI and actual Harbor Verifier on passing
and failing candidate files. Malformed protected-test collection remained
unscored. No matching saved model trace was available.

Apply `bigcodebench-hard-pytest-verifyit.patch` after the Harbor dispatcher
patch. Its generated task invokes protected `/tests/test_outputs.py` with
`PytestSpec.python` fixed to `/usr/local/bin/python3.10`; benchmark dependencies
and candidate code stay on Python 3.10. Verifyit runs in an isolated Python 3.11
environment. A generated image matched the pinned source test.sh, direct CLI and
actual Harbor Verifier for passing and failing candidates. Malformed protected
test collection remained unscored with no reward. No matching saved model trace
was available. The image proof substituted a wheel built from the pinned local
`1dd6292b54dd1c2525a1c1354d49940ba5ba6dbf` commit for the unpublished
remote Git install; the benchmark dependency layers were unchanged.

Apply `autocodebench-pytest-verifyit.patch` after the Harbor dispatcher patch.
The pinned base image lacks `uv`, which its original test.sh already requires;
the patched task image installs uv 0.7.13 for both the original script and
verifyit. Its generated `PytestSpec` runs protected `/tests/test_outputs.py` in
the task's uv-managed `/app/.venv` Python. Task-owned setup failures use
`setup_failure_is_infra = true`, supplied by verifyit commit
`3f21d36306c86861e5fdff0718bd72029328e752`. A generated image matched
original test.sh, direct CLI and Harbor Verifier for passing and failing
candidates. A wheel-install failure left no source reward and produced an
unscored verifyit verdict with no stale reward; malformed protected-test
collection also remained unscored. No matching saved model trace was available.
The image proof substituted a wheel from the exact local API commit for its
unpublished remote Git install.

Apply `mmau-pytest-verifyit.patch` after the Harbor dispatcher patch. The
generated task runs protected `/tests/test_outputs.py` in its uv-managed
`/app/.venv` Python; PytestSpec also passes source `--workdir /tests` and writes
the original `/logs/verifier/ctrf.json` alongside verifyit's JSON report.
The task image pins uv 0.7.13 and verifyit
`3f21d36306c86861e5fdff0718bd72029328e752`. A generated image matched
the pinned source script, direct CLI and actual Harbor Verifier on passing and
failing candidates. Source and verifyit CTRF pass/fail counts matched, and
Harbor retained the artifact. Malformed protected-test collection remained
unscored without a reward. No matching saved model trace was available. The
image proof substituted an exact-commit wheel for the unpublished Git install.

Apply `compilebench-pytest-verifyit.patch` after the Harbor dispatcher patch.
With `--verifyit-enabled`, the adapter fetches the pinned 15 CompileBench tasks
and declares each unchanged `/tests/test_outputs.py` suite to PytestSpec. Empty
required-ID lists keep the source all-tests binary reward; the source CTRF
artifact is retained. The Ubuntu and Alpine task images add a separate Python
3.11 verifier environment while preserving their build runtimes. The image
proof substituted a wheel from local verifyit commit
`eebc28fdb79fb66b800702715aa8dbecd5fbb3f0` for its unpublished Git install.
Generated cowsay and Alpine legacy-coreutils images matched the original
`test.sh`, direct CLI and actual Harbor Verifier on passing and missing-result
candidates. Malformed protected tests were unscored without a reward; an empty
suite scored zero under the existing PytestSpec policy. Three candidate
executable tamper probes did not produce a positive score. These are bounded
fixtures, not a general same-UID isolation proof. The other 13 task images and
matching saved model traces remain unvalidated. Evidence and exact replay
commands are in `evidence/e2e/wiring/harbor-compilebench/`.

`ds1000-numpy-verifyit.patch` is a partial, opt-in DS-1000 client checkpoint;
the canonical DS-1000 adapter remains pending. Its static gate selects 87 of
1,000 NumPy-only source contexts. Candidate code runs in an unprivileged
Landlock child and returns bounded typed values without pickle; the trusted
parent runs the source assertions. This rejects the pinned source's
`SystemExit(0)` false positive and candidate attempts to read references or
write a reward. All 87 source reference solutions and their result transports
passed under source Python 3.10 and NumPy 1.26.4. A smaller NumPy task image
matched source, CLI and actual Harbor Verifier on three generated tasks, with
negative and isolation cases. The exact full source image builds on amd64, but
Landlock is unavailable under this ARM host's amd64 emulation; the original
source image cannot build natively on ARM because its torch CPU wheel is
missing. The full image has source-only score evidence, not a verifier cutover.
No archived model workspaces were replayed. Exact commands, hashes, and
failure evidence are in `evidence/e2e/wiring/harbor-ds1000/README.md`.

Apply `codepde-pytest-verifyit.patch` after the Harbor dispatcher patch. Its
generated tasks declare PytestSpec against a protected `/tests/verifyit/` copy
of each upstream nRMSE evaluator. The original `test.sh` and evaluator remain
separate, so source grading keeps its existing import path. The patched image
pins verifyit `3f21d36306c86861e5fdff0718bd72029328e752` and preflights
Linux Landlock before scoring. An unprivileged candidate child receives public
initial inputs but cannot read the reference HDF5 or write reward files;
trusted code checks exact array shapes and finite values before the unchanged
upstream evaluator applies its binary nRMSE threshold. The evaluator reaps
detached children before consuming output. All five PDE variants matched
source `test.sh`, direct CLI and Harbor Verifier for reference and wrong solvers
in a generated image using bounded HDF5 fixtures. Seven adversarial cases
cover forged stdout, reference reads, reward writes, malformed arrays, and
missing or empty solvers. The image used a wheel from the exact local API
commit instead of the unpublished Git install. Full-size PDE data and matching
saved model traces remain unvalidated. Evidence is in
`evidence/e2e/wiring/harbor-codepde/`.

Apply `replicationbench-pytest-verifyit.patch` after the Harbor dispatcher
patch. Generated tasks use PytestSpec with the protected source comparator,
preserving its binary all-tests policy and `/logs/comparison_result.json`.
The task image pins verifyit `3f21d36306c86861e5fdff0718bd72029328e752`
and uses a wheel from that exact local commit in the bounded image proof.
Original `test.sh`, direct CLI and actual Harbor Verifier matched on nested
passing, wrong and missing-result fixtures. The patched comparator scores a
boolean-as-number candidate zero where the source awarded one. Trusted
references and tolerance shapes are checked in setup: malformed task data is
unscored, while explicit null remains valid. Broader task instances, scientific
data and saved model traces remain unvalidated. Evidence is in
`evidence/e2e/wiring/harbor-replicationbench/`.

Apply `bfcl-script-verifyit.patch` after the Harbor dispatcher patch. Its
generated `ScriptSpec` executes the original `test.sh` and category-specific
evaluator through verifyit's structured native-runtime bridge. The benchmark
continues on Python 3.10 for the tested Python categories; verifyit uses a
separate Python 3.11 environment pinned to local commit
`aece7bd55701b60945135c4091578bb49bbd726e`. The image proof replaced only
the unpublished Git install with a wheel from that exact commit. Eleven
generated-image cases ran the pinned source script, direct CLI and actual Harbor
Verifier, covering simple, live relevance, irrelevance and reordered parallel
calls. Boolean-as-number and overflowing numeric-string comparisons no longer
earn source false-positive credit. Invalid trusted references abort generation;
malformed protected evaluator code leaves no reward. Other categories and
archived candidate workspaces remain unvalidated while AWS SSO is expired.
Evidence is in `evidence/e2e/wiring/harbor-bfcl/`.

Apply `dabstep-script-verifyit.patch` after the Harbor dispatcher patch. Its
generated `ScriptSpec` runs the original `test.sh` and protected DABstep scorer
through the structured runtime bridge. The task image keeps the source Python
3.12 environment and installs verifyit separately on Python 3.11 from commit
`27b8c172c454c7c8b4ad32f238186b8d29b0d140`; the bounded image proof
substitutes a wheel built from that exact local commit for its unpublished Git
URL. Eleven generated-image cases ran the pinned source script, direct CLI and
actual Harbor Verifier. Numeric, text and order-independent list answers
matched source rewards. Nonfinite trusted numbers and punctuation-only trusted
answers no longer earn source false-positive credit; malformed protected scorer
code and invalid trusted references leave no reward. Broader task instances and
saved model-run workspaces remain unvalidated. Evidence is in
`evidence/e2e/wiring/harbor-dabstep/`.

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

Apply `tau3-verifyit.patch` after the dispatcher patch to migrate the tau3 client.
Generate tasks with `--verifyit-ref 91c55a49599fcdead3475f009e62da4e30ca4f27`;
this required immutable API pin supplies ScriptSpec.verdict_file. The commit is
local and unpublished, so remote image builds require publishing that exact
revision; local API tests use the corresponding Git checkout. The tau3 patch
retains evaluate.py, model/domain/trajectory behavior and native reward metadata.
Valid mismatch zero is scored; missing/invalid logs or caught runtime errors
are infra_error zero. This is a native-runtime client bridge, not a replacement
state-scoring primitive.

The tau3 client now writes `tests/tau2-assets.json` from immutable Git objects
at its declared tau2 revision. Before native evaluation, the bridge checks
Python source and domain assets against that trusted manifest and removes native
bytecode caches. Changed, missing, or redirected assets produce an unscored
infrastructure error. This catches direct edits to the base database; legitimate
trajectory mutations occur in memory during native replay. It does not establish
isolation from an agent with unrestricted root access to the grader interpreter.

For existing tau3 tasks, generate the manifest using the pinned runtime checkout:

```bash
python integrations/harbor/tau3_assets.py /path/to/tau2-bench airline /path/to/task/tests/tau2-assets.json
```

Use the task's actual domain and upload the manifest together with the updated
bridge through Harbor's tests upload. Replay evidence and limitations are in
[the Harbor replay report](../../docs/unification/harbor_replay.md).
