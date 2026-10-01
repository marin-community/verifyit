# Harbor integration

The coverage register identifies a shared-verifier boundary gap in six wired
Harbor routes. Harbor uploads their protected tests or references into the live
agent container before grading; a surviving candidate process can modify them.
A generated GAIA task reproduced the failure: the wrong answer `Boston` scored
one after the candidate changed the uploaded `New York` reference. ARC-AGI-2,
AIME, GAIA, GPQA Diamond, SATBench and DABstep now use separate verifier
images on bounded generated tasks. The six remaining routes require the
boundary changes listed in the
[coverage report](../../docs/unification/coverage-gaps.md#shared-verifier-boundary)
before deployment. The GAIA reproduction is in
`evidence/e2e/wiring/harbor-answers/gaia-shared-reference-before.json`.

`answer-isolation-verifyit.patch` is a cumulative replacement for
`answer-routes.patch` against the same pinned Harbor revision. It generates a
separate verifier image for each of the four answer routes. Only the candidate
answer artifact crosses from the agent image; the trusted reference stays in
the verifier image. A generated GAIA task's wrong answer scored one when a
surviving candidate process changed the shared reference, and zero with the
separate verifier. Bounded source-generated Harbor trials scored correct/wrong
answers 1/0 for GAIA, AIME, GPQA Diamond, and SATBench; redirected and missing
GAIA artifacts scored zero. The patch pins verifyit `ca7fce7c50f61a3b4b26fe1f9609853effadb87c`.
Because that revision is local, the proof images substituted a wheel built from
its Git archive. The earlier 12 original-script versus patched-CLI fixture cases
remain in `evidence/e2e/wiring/harbor-answers/boundary-source-comparison.json`.
`evidence/e2e/wiring/harbor-answers/final-pin-manifest.json` records the
final verifier wheel and five rebuilt image digests. An empty GAIA reference
with a redirected candidate produced `invalid_task` and no reward file in
an actual Harbor trial. Independent positive/wrong and mutation replays matched.
These are generated fixtures, not saved model rollouts; wider task images
remain unvalidated.

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

Apply `mmau-isolation-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`; it replaces `mmau-pytest-verifyit.patch`.
The generated PytestSpec runs the protected source token comparator in a
separate Python 3.13 verifier image, transferring only `/app/answer.txt`.
The image installs pytest 8.4.1, pytest-json-ctrf 0.3.5 and verifyit
`ca7fce7c50f61a3b4b26fe1f9609853effadb87c`; the proof substitutes that commit's
local wheel for the unpublished Git install. The source `--workdir /tests`
and CTRF report remain intact. Candidate text uses verifyit's bounded regular
file reader. Setup rejects empty or malformed trusted references before grading;
these produce `infra_error` with zero reward and no Harbor reward file.

Three seeded source dataset tasks matched original pytest and isolated Harbor
scoring for positive and wrong answers. A wrong answer scored one after a live
agent rewrote the shared reference, then zero after isolation. Linked candidate
answers score zero. All 1,000 source references pass the added validation.
No matching saved model trace was available. Evidence and installed file hashes
are in `evidence/e2e/wiring/harbor-mmau/isolation-final-manifest.json`.

Apply `mmmlu-mcq-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`. The generated private verifier preserves
the source multilingual marker patterns, normalization and agent-log priority,
then grades the extracted label with existing McqSpec. It receives only
`/logs/agent`; the expected label remains in the verifier image. Repeated
identical labels retain their score, while conflicting explicit labels score
zero. This intentionally tightens the source's first-marker policy.

The image pins verifyit `ca7fce7c50f61a3b4b26fe1f9609853effadb87c`; local proofs
substitute the exact-commit wheel for its unpublished Git install. Eighteen
ordinary language and log-path fixtures ran the source script and actual Harbor
Trials: seventeen scores match and one conflicting-answer case changes from
one to zero. Primitive witnesses record actual MCQ calls in three languages.
No matching archived traces were available. These results cover ordinary score
parity, with no additional security validation. Evidence and installed hashes
are in `evidence/e2e/wiring/harbor-mmmlu/final-manifest.json`.

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

Apply `codepde-isolation-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`; it replaces `codepde-pytest-verifyit.patch`.
Generated tasks declare PytestSpec against the protected upstream nRMSE
evaluator in a separate verifier image. Only `/app/solver.py` transfers from
the stopped agent environment. Production Dockerfiles download the same
upstream HDF5 URL during the private image build, instead of accepting a file
from the agent workspace. Verifyit is pinned to
`ca7fce7c50f61a3b4b26fe1f9609853effadb87c`.

The existing unprivileged Landlock proxy passes public numerical inputs to
the candidate and validates returned shapes and finite values. The unchanged
upstream evaluator applies the binary 0.05 nRMSE threshold. Sandbox preflight
uses the protected worker file, so a missing candidate scores zero instead of
becoming an infrastructure failure. Ten actual isolated Harbor Trials matched
positive and wrong solvers across all five PDE families. These use existing
bounded HDF5 fixtures and the scientific fixture runtime with an exact-commit
wheel. Full production image builds, full-size datasets and archived model
traces remain unvalidated. Evidence and installed hashes are in
`evidence/e2e/wiring/harbor-codepde/isolation-final-manifest.json`.

Apply `replicationbench-isolation-verifyit.patch` after the Harbor dispatcher
and `answer-isolation-verifyit.patch` patches. It replaces the earlier
`replicationbench-pytest-verifyit.patch`. Generated tasks use PytestSpec with
the protected source comparator in a separate verifier image, preserving its
binary all-tests policy and `/logs/comparison_result.json`. Only the
candidate's `/app/result.json` transfers from the agent image; reference and
comparator files stay in the verifier image. The proof image pins verifyit
`ca7fce7c50f61a3b4b26fe1f9609853effadb87c` and substitutes a wheel from
that exact local commit for its unpublished Git install.
Original `test.sh`, direct CLI and actual Harbor Verifier matched on nested
passing, wrong and missing-result fixtures. The patched comparator scores a
boolean-as-number candidate zero where the source awarded one. Trusted
references and tolerance shapes are checked in setup: malformed task data is
unscored as `infra_error`, while explicit null remains valid. In an actual
Harbor Trial, a wrong result scored one when an agent mutated a valid config in
the shared container, then zero after isolation. Linked result files score
zero, and invalid trusted config leaves no reward. Broader task instances,
scientific data and saved model traces remain unvalidated. Evidence is in
`evidence/e2e/wiring/harbor-replicationbench/`.

Apply `bfcl-isolation-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`; it cumulatively replaces
`bfcl-script-verifyit.patch`. Its generated `ScriptSpec` executes the original
`test.sh` and category-specific evaluator in a separate verifier image. Only
`/app/result.json` crosses from the stopped agent environment. The evaluator
runs on Python 3.10; verifyit uses Python 3.11 pinned to
`ca7fce7c50f61a3b4b26fe1f9609853effadb87c`. Local image proofs substitute a wheel
from that commit for its unpublished Git install. Candidate JSON must be a
bounded regular file with finite values; linked files and special files fail
closed. Boolean-as-number and overflowing numeric-string comparisons no longer
earn source false-positive credit. Invalid trusted references abort generation.

All 13 categories generate isolated tasks. Eight actual Harbor Trials cover
passing and wrong simple, reordered parallel, irrelevance and live relevance
answers. A wrong answer scored one when a surviving agent process rewrote the
shared evaluator, then zero after isolation. This remains a retained source
scorer, not a native BFCL comparator. Java, JavaScript and other category
execution and archived candidate workspaces remain unvalidated. Evidence is in
`evidence/e2e/wiring/harbor-bfcl/isolation-final-manifest.json`.

Apply `dabstep-isolation-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`; it cumulatively replaces
`dabstep-script-verifyit.patch`. Its generated `ScriptSpec` runs the original
`test.sh` and protected scorer in a separate verifier image, transferring only
`/app/answer.txt` from the agent image. The agent retains its source Python
environment and data files. The verifier image pins verifyit
`ca7fce7c50f61a3b4b26fe1f9609853effadb87c` on Python 3.11; the bounded
proof substitutes the attested local wheel for its unpublished Git URL.
Eleven earlier generated-image cases ran the pinned source script, direct CLI
and actual Harbor Verifier. Numeric, text and order-independent list answers
matched source rewards. Nonfinite trusted numbers and punctuation-only trusted
answers no longer earn source false-positive credit; malformed protected scorer
code and invalid trusted references leave no reward. New actual Harbor Trial
fixtures scored correct/wrong answers 1/0 and a wrong-answer reference-change
trial zero after isolation. Broader task instances and saved model-run workspaces
remain unvalidated. Evidence is in `evidence/e2e/wiring/harbor-dabstep/` and
`evidence/e2e/wiring/harbor-answers/dabstep-isolation-manifest.json`.

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

## LAB-Bench FigQA

Apply `labbench-exact-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`, then generate tasks with the LAB-Bench
adapter's `--verifyit` option. The pinned adapter supports FigQA. Generation
freezes the shuffled public letter mapping and puts accepted letters in the
separate verifier image. Each accepted letter uses a strict ExactSpec; duplicate
choice text can therefore have two accepted letters. Malformed trusted labels
and blank or oversized choice sets fail task validation. Conflicting explicit
answer labels receive zero.

Thirteen generated fixture cases ran the source script with the same mapping
and actual Harbor Trials: twelve match and contradictory labels intentionally
change one to zero. Nine helper and generation tests pass. Final v2 images
include stricter trusted-input preflight, with independent manager Trials.
Provenance and original result hashes are in
`evidence/e2e/wiring/harbor-labbench/final-manifest.json`. No matching archived
model traces were available; validation covers ordinary parity, and security
scope remains unverified.

## Kumo

Apply `kumo-exact-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`, then pass `--verifyit-enabled` to Kumo's
adapter. The source Compose action service is retained. A separate grader
compares the first nonempty stripped answer line with trusted `valid_truth`
using strict ExactSpec. Action counts and relative counts remain auxiliary
verdict details; they do not alter reward. Invalid trusted references fail
task validation, and unreadable or invalid UTF-8 candidates score zero.

Nine ordinary cases across three seeded source-generated tasks match original
source scores and action metrics, with one real action-service call per Trial.
Five helper regressions pass. Independent manager positive/wrong Trials confirm
the final images. Provenance is in
`evidence/e2e/wiring/harbor-kumo/final-manifest.json`. No matching archived
model traces were available; security scope remains unverified.

## QuixBugs

Apply `quixbugs-pytest-verifyit.patch` after the Harbor dispatcher and
`answer-isolation-verifyit.patch`, then pass `--verifyit` to the QuixBugs
adapter. Both Python and Java use existing PytestSpec with the source-generated
wrappers and one-line-change requirement. The Java wrapper retains Gradle and
JUnit. A separate grader image owns original programs and tests; only the
candidate source file transfers from the agent. The Java grader retains network
access for the source Gradle dependency resolution.

Twelve ordinary cases across three seeded programs in both languages match
the original source script and actual Harbor Trials. Provenance is in
`evidence/e2e/wiring/harbor-quixbugs/final-manifest.json`. These are generated
program fixtures; archived model traces remain unverified. Candidate Python is
imported in the grader process and Java runs inside the grader container, so
candidate/assertion isolation is not established by the separate image.

## Reasoning Gym

Apply `reasoning-gym-verifyit.patch` after the Harbor dispatcher, then pass
`--verifyit` to the adapter. The client pins verifyit159d145 and
reasoning-gym0.1.25. Existing ReasoningGymSpec reads the source's protected
entry and dataset-parameter JSON from a separate verifier image. Configured
scoring matters: decimal precision4 rejects a near-miss that the legacy
default-configuration scorer accepted. Native partial credit is preserved.

Eight ordinary cases across three seeded configured source datasets match
the source scorer through actual Harbor Trials, including the decimal near-miss
and polynomial partial credit. Core/spec tests cover malformed parameters,
preflight before absent candidates, construction infrastructure failures and
legacy spec compatibility. Provenance is in
`evidence/e2e/wiring/harbor-reasoning-gym/final-manifest.json`. No matching
archived model traces were available; security scope remains unverified.

## ResearchCodeBench and SciCode source runtimes

Apply `research-code-bench-runtime-verifyit.patch` after the dispatcher patch.
It adds the shared source-runtime packaging helper; apply
`scicode-runtime-verifyit.patch` afterward for SciCode. Pass `--verifyit` to
either adapter. Generated tasks use ScriptSpec around the existing source
scorer in a separate verifier image. ResearchCodeBench retains snippet insertion,
pytest scoring and `code_lines`; SciCode retains fractional substep scores.
These are retained source runtimes, not native comparator replacements.

ResearchCodeBench matched nine ordinary source/Harbor cases: three direct-file
positive/wrong pairs and Codex-log insertion with correct, wrong and empty
outputs. The three tasks were sampled from five synthetic scalar operations.
This validates the adapter contract, not the actual ResearchCodeBench dataset;
the full production scientific dependency image was not built. SciCode matched
nine full/half/zero scores across three synthetic two-step HDF5 tasks, plus a
missing candidate scoring zero. Its source scientific image dependencies were
built, but the reference data is synthetic, not the full SciCode benchmark.
Neither result is archived model replay. Evidence and installed-image hashes
are in `evidence/e2e/wiring/harbor-research-code-bench/final-manifest.json` and
`evidence/e2e/wiring/harbor-scicode/final-manifest.json`.

SciCode generation rejects empty or malformed evaluated test lists and tasks
with no remaining evaluated steps, preserving documented prewritten/broken
exclusions. The original empty-step harness awarded one without testing an
implementation; the cutover rejects that task. Uncaught harness failures now
remain unscored zeroes instead of becoming the source shell's scored-zero
fallback. Seven regression tests cover these generation contracts.

Both routes execute candidate code inside their grader runtime. Separate images
do not establish candidate/assertion isolation; that trust boundary remains
unverified. Validation here covers ordinary score parity only.

### Build with the local verifyit revision

The generated Dockerfiles pin `a0861089947096aabe456ca4308ca46b1b001d7c`, a local,
unpushed commit. Their Git installation requirement cannot resolve remotely
until that commit is published. No push is required for local use: build a wheel
from the exact commit, then substitute it in each generated verifier image.
From the verifyit campaign worktree:

```sh
build_dir=$(mktemp -d)
git archive a0861089947096aabe456ca4308ca46b1b001d7c | tar -x -C "$build_dir"
uv build --wheel --out-dir "$build_dir/wheels" "$build_dir"
```

Set `task_dir` to one generated task and run this substitution before Harbor
builds its images. It retains the source Dockerfile's runtime dependencies.

```sh
python3 - "$task_dir" "$build_dir/wheels/verifyit-0.1.0-py3-none-any.whl" <<'PY'
import shutil
import sys
from pathlib import Path

tests = Path(sys.argv[1]) / "tests"
wheel = Path(sys.argv[2])
dockerfile = tests / "Dockerfile"
source = dockerfile.read_text()
requirement = "'verifyit @ git+https://github.com/marin-community/verifyit@a0861089947096aabe456ca4308ca46b1b001d7c'"
assert source.count(requirement) == 1
shutil.copy2(wheel, tests / wheel.name)
first, rest = source.split("\n", 1)
source = first + f"\nCOPY {wheel.name} /tmp/{wheel.name}\n" + rest
dockerfile.write_text(source.replace(requirement, f"/tmp/{wheel.name}"))
PY
```

The manifests record the exact local wheel hash. ResearchCodeBench proof images
also used a bounded pytest-only dependency image; the wheel substitution above
alone preserves its larger production image and does not claim that image has
been validated.

## LiveCodeBench

Apply `livecodebench-runtime-verifyit.patch` after
`research-code-bench-runtime-verifyit.patch`, which supplies the shared helper.
Pass `--verifyit` to the adapter. ScriptSpec retains the source stdin and
functional evaluators, including its Python equality rules. Generation strictly
validates trusted public/private case lists and rejects empty evaluated tasks;
compressed private references use the source-owned decoder. Candidate data does
not enter that decoder. Only completed aggregate scoring writes a reward;
missing and wrong candidates score zero, while incomplete grader runs remain
unscored.

Six source/Harbor positive/wrong pairs match across functional reverse, functional
sum and stdin product fixtures, each with compressed private cases. A missing
candidate also scores zero. The three tasks were sampled from five synthetic
operations, not actual LiveCodeBench data or archived model traces. Five ordinary
regressions cover malformed references and the source's zero-test success.
The source runtime image was built with the exact local core wheel substitution
shown above. Evidence is in
`evidence/e2e/wiring/harbor-livecodebench/final-manifest.json`. Candidate execution
inside the grader remains an unverified trust boundary.


## SimpleQA, HLE and OmniMath

Apply `judge-families-verifyit.patch` after the dispatcher patch and
`research-code-bench-runtime-verifyit.patch`. Pass `--verifyit` to each adapter.
The source judge runs inside ScriptSpec in a separate verifier image. It keeps
its original prompt, request parameters and answer extraction, while core
JSONSchema and Exact grade the raw response fields. Invalid JSON, incomplete
responses and judge failures remain unscored at minimum reward. No new core
verifier class is required.

Nine frozen source-generated fixtures, three per adapter, match native scores
and exact HTTP request bytes through actual Harbor Trials. OmniMath covers both
OpenAI and Anthropic. Seven additional fixtures exercise the source scorer's
string and range modes by changing trusted generated metadata; the adapter
itself always emits `llm_verifier`. Distinct Unicode strings now go through the
judge when ASCII normalization empties the reference, correcting source false
credit. Nonfinite or reversed trusted ranges raise within the retained runtime:
`infra_error`, reward zero, and no Harbor reward value. These are malformed tasks,
not candidate-wrong scored zeros.

These are controlled HTTP fixtures, not archived model-score replays. The fixture
agent image uses bounded Python 3.11 SDK dependencies rather than claiming a
production deployment of every original agent image. The separate verifier uses
core revision `a0861089947096aabe456ca4308ca46b1b001d7c`; until publication, use the
exact local archive-wheel substitution described above. Installation witnesses
hash all 41 core Python files and the task files inside actual grading containers.
Evidence, patch order, source hashes and independent manager roundtrips are under
`evidence/e2e/wiring/harbor-judge-family/implementation-provenance.json`.

## USACO

Apply `usaco-pytest-verifyit.patch` after
`research-code-bench-runtime-verifyit.patch`, which supplies the shared core pin.
Pass `--verifyit` to the adapter. The existing PytestSpec runs the unchanged
source pytest suite and batch judge in a separate image. Every judged case must
be accepted; a candidate that merely exists still scores zero when its judge
test fails. Task generation rejects empty/malformed reference cases, impossible
case counts and unavailable/nonfinite execution limits. Core pytest empty
collection and timeout behavior remain minimum-score outcomes.

Eight ordinary source/Harbor comparisons match across three synthetic task
fixtures: correct/wrong pairs, syntax-error and missing candidate. The source
comparison executes the source pytest command with its dependencies preinstalled;
it does not repeat the apt/uv bootstrap for every case. Four task-reference
regressions and two existing core minimum-score tests pass. Full Python3.13 task
images were built with the local-wheel substitution described above. These are
synthetic adapter fixtures, not actual USACO dataset or archived model coverage.
Candidate execution in the grader remains an unverified trust boundary. Evidence
is in `evidence/e2e/wiring/harbor-usaco/final-manifest.json`.


## AA-LCR and IneqMath

Apply `judge-extensions-verifyit.patch` after `judge-families-verifyit.patch`
and its dependencies. Both adapters accept `--verifyit`. The existing separate
Script runtime retains the source prompts and SDK request parameters, with raw
HTTP/schema checks before SDK coercion. AA-LCR accepts completed CORRECT or
INCORRECT labels; negated, ambiguous and malformed responses remain unscored.

IneqMath preserves both relation and bound contracts. Relation scoring retains
the six deterministic source shortcuts and chat extraction; invalid extraction
raises instead of choosing a random answer. Bound scoring retains extraction,
normalized equality and the structured equivalence judge. Empty normalized
trusted references and malformed boolean fields cannot receive credit. Judge
errors propagate through the Script verdict as unscored minimum reward, rather
than source negative sentinels or candidate-wrong scores.

Nine actual Harbor source/cutover fixture pairs match rewards and exact HTTP
request bytes. Four malformed-output fixtures record the intended corrections,
including native credit for “NOT CORRECT” and string-to-boolean coercion. The
native random fallback result is preserved without resampling. All thirteen
cutover containers include installed core and task hash witnesses. The tests use
controlled HTTP responses and bounded source-generated tasks, not archived model
scores or full production datasets. Use the same pinned local wheel substitution
as the preceding judge family. The complete source contract census, patch order,
source hashes and roundtrips are in
`evidence/e2e/wiring/harbor-judge-extensions/implementation-provenance.json`.


## Aider Polyglot

Apply `aider-polyglot-runtime-verifyit.patch` after the base dispatcher and
`research-code-bench-runtime-verifyit.patch`, then generate tasks with `--verifyit`.
All six source language runtimes use the existing ScriptSpec bridge. The separate
verifier receives the declared solution files and retains source test merging,
dependencies and binary all-pass scoring. Java resolves JAVA_HOME from its installed
JDK; the original amd64-only path failed on the ARM proof host.

The frozen sample contains one real upstream exercise for each language:
Python hangman, JavaScript connect, Java food-chain, C++ space-age, Go say and
Rust macros. Actual Harbor OracleAgent and NopAgent trials match eleven numeric
source scores. The C++ unfinished starter fails compilation before the source
publishes a reward; verifyit reports infra_error with minimum reward0 and Harbor
raises VerifyitUnscoredError. This remains an unscored result, not a scored zero.
All six reference solutions score1, including the corrected Java runtime.

`evidence/e2e/wiring/harbor-aider-polyglot/final-manifest.json` records the pinned
upstream selection, twelve final comparisons, original Java failure, separate
Java v2 proof, image/source hashes and independent manager Trials. Two malformed
exercise-reference regressions pass. These are real exercise fixtures, not archived
model replays or coverage of all 225 exercises. Candidate code executes inside the
source grader; candidate/assertion isolation remains unverified. No new security
tests were run. The local wheel substitution above is required for the unpushed
core pin; both source and verifier runtime images were built.


## CrustBench

Apply `crustbench-runtime-verifyit.patch` after the base dispatcher and
`research-code-bench-runtime-verifyit.patch`, then generate with `--verifyit`.
The existing ScriptSpec bridge runs the source Rust1.83 Cargo build/test runtime
in a separate image with candidate interface files. A completed failing Cargo
test summary retains scored0. Unknown build/setup failures remain unscored
minimum; an empty successful test suite also returns unscored minimum instead
of the source's positive reward.

The frozen real upstream sample is libbase122, rbtree_lab and utf8. Their starter
implementations build and fail six, six and 25 tests respectively; final source
and Harbor scores match0. No real completed implementation or reference oracle
was available. A separate synthetic scalar control matches1, and a separate
empty-suite control demonstrates source1 to verifyit infra_error minimum0.
These controls supplement the selected real tasks; they do not establish
production-positive or archived model coverage.

`evidence/e2e/wiring/harbor-crustbench/final-manifest.json` records the 100-project
runtime census, frozen selection, final v2 real-task and v3 control results,
source/task/image hashes and independent manager Trials. The earlier synthetic
control namespace error and its unscored result are retained separately. Four
Cargo completion regressions pass. Candidate code still executes inside the
source grader, so candidate/assertion isolation remains unverified. No new
security tests were run. Use the exact local core wheel recipe above for the
unpushed verifyit pin.


## Pixiu

Apply `pixiu-runtime-verifyit.patch` after the base dispatcher and
`research-code-bench-runtime-verifyit.patch`, then generate with `--verifyit`.
The existing ScriptSpec bridge transfers `/app/answer.txt` into a separate image
and retains Pixiu's eight per-task scoring branches and auxiliary metrics.
Classification with an empty answer now scores 0 instead of matching the first
choice. Trusted references are checked before candidate parsing; invalid setup
returns an unscored minimum. Empty relation references remain valid, including
an empty answer that correctly denotes no relations.

The source census maps 29 documented dataset names to eight scoring branches.
The 27-case fixture suite has 26 exact score and auxiliary-metric matches and
one intentional empty-classification change from 1 to 0. A malformed NER candidate
is retained as 0/0; a supplemental candidate with correct BIO labels scores 1/1.
Five output regressions pass. Final v6 differs from the full v5 suite only in
AST-identical formatting and has separate installed-image hashes and actual
framework checks. The manifest at
`evidence/e2e/wiring/harbor-pixiu/final-manifest.json` records the source, patch,
task and result hashes, plus independent manager Trials.

These are bounded scoring fixtures, not actual dataset conversions or archived
model replays. Aggregate metrics, including ROUGE and BARTScore, remain
source-owned and were not validated here. No new security tests were run.
Use the local core wheel recipe above for the unpublished verifyit revision.


## LLMSR-Bench

Apply `llmsr-runtime-verifyit.patch` after the base dispatcher and
`research-code-bench-runtime-verifyit.patch`, then generate with `--verifyit`.
The existing ScriptSpec bridge transfers the discovered equation into a
separate verifier image containing the source fitter and task CSVs. Finite
negative R² becomes scored 0; raw R² and the other diagnostics remain available.
The source threshold that rounds R² at or above 0.95 to 1 is unchanged. Trusted
CSV validation distinguishes invalid tasks from unavailable reference files.

The manifest at `evidence/e2e/wiring/harbor-llmsr/final-manifest.json` records
33 actual Harbor fixture roundtrips across all five source splits, including
literal equations, bounded TRF and BFGS fitting, and domain errors. There are
23 exact primary-score matches and 10 intentional negative-to-zero adaptations;
all 33 auxiliary metric payloads match. Three supplemental cases verify invalid
reference, missing reference and missing candidate statuses. Three ordinary
regression tests pass. Independent manager Trials verify BFGS and negative R².

The official dataset files returned HTTP 403 with the configured token. These
are declared synthetic source-schema fixtures, not official rows or archived
model traces. Candidate expressions execute within the source grader; that
trust boundary remains unverified. No new security tests were run. Use the
exact local wheel recipe above: the production Dockerfile references a local
verifyit revision that has not been published.
