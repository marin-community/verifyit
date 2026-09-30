The patch targets marin-community/evalchemy
`e3f4a3d601896c437f37b0bd0a30e51651cce6d0`.
Install verifyit in the evaluation environment and apply `verifyit.patch` from
the Evalchemy checkout. Apply the separately pinned harness patch to its installed
harness dependency for native tasks.

GPQA Diamond and MMLU-Pro retain their answer extraction and aggregation. Their
extracted option letters now call verifyit's `grade_mcq_candidate`; GPQA declares
four options and MMLU-Pro ten. Category and repeat counts, standard errors and
sample records remain Evalchemy-owned.

The shared extraction boundary calls verifyit's completion adapter. Final content
takes precedence over reasoning; completed reasoning-only math answers require a
box, while truncated reasoning-only output supplies no answer. Inline reasoning
end markers are handled before benchmark box extraction. The patch retains the
benchmark's own box parser and stop-sequence handling.

The patch also routes AIW normalization through strict exact, GSM8KPerturbed
through zero-tolerance numeric, and the shared AIME/MATH500 boxed comparison
through math. Missing-parse Minerva fallback and judge prompts remain source-owned.
Further normalization/fallback contracts are described in
[the mapping](../../docs/unification/evalchemy_mapping.md).


The integration requires verifyit implementation commit
`87e4a72428695a7eedfa97c22868ea3aa2d1c651`, including JEEBench primitive composition and `math_answer_text`.
Apply `dependency-pin.patch` to declare that exact implementation in the source
project metadata. This commit remains local and unpublished: the remote Git URL
in the dependency patch is a publication target, not an available installation.
Evalchemy's lockfile must be regenerated when that dependency becomes fetchable.
For current validation in an environment with the pinned project's existing
dependencies installed, use the local Git commit and install the patched source
without resolving the unpublished remote dependency:

```bash
uv pip install --python /path/to/environment/bin/python 'verifyit[answer] @ git+file:///path/to/verifyit@87e4a72428695a7eedfa97c22868ea3aa2d1c651'
uv pip install --python /path/to/environment/bin/python --no-deps /path/to/patched-project
```

An isolated core-only installation from this exact local Git revision was
validated through the actual patched JEEBench extraction and evaluation pipeline:
five fixtures over three repetitions match source scores and aggregates, with 88
verifyit calls. Four malformed-reference batches abort without an aggregate.
Installed-package provenance and results are retained in campaign
`evidence/e2e/wiring/evalchemy-jee/installed-metadata.json` and `installed-replay/`.
No remote publication or live model endpoint was used.

The GSM8K override retains its version 3.3 extraction/Minerva contract. Its rational
shortcut uses strict verifyit exact on canonical Fraction values; non-rational
answers retain Minerva symbolic scoring. This client hybrid was exposed by real
recorded traces, so it is separate from upstream harness native-config eligibility.
Run the source parity regressions with the patched Evalchemy environment:

```bash
PYTHONPATH=/path/to/verifyit/src:/path/to/patched-evalchemy:/path/to/harness \
  /path/to/evalchemy/.venv/bin/python integrations/evalchemy/check_gsm_override.py \
  /path/to/original-evalchemy /path/to/patched-evalchemy
```


## JEEBench native client

Apply `jee-verifyit.patch` to the pinned Evalchemy checkout. The opt-in benchmark
constructor `JEEBenchBenchmark(verifyit_enabled=True)` and the existing public
`TaskManager(task_list=["JEEBench"], verifyit_enabled=True)` benchmark-kwargs
route (`from eval.task import TaskManager`) activate the client. No new CLI flag is claimed. The default source scorer
is unchanged, and the verifyit import is lazy. The dependency pin records the actual JEE API implementation checkpoint; it
remains local and unpublished.

The real `extract_answer` and `evaluate_responses` pipeline dispatches source
uppercase A–D option sets to strict exact matching, retains `.25` subset credit
for multiple-answer questions, and uses `NumericSpec` with absolute tolerance
`.01` and zero relative tolerance for integer/numeric questions. Three-repetition
score vectors, means, standard errors and sample metrics remain benchmark-owned.
Malformed/empty choice references and nonfinite/boolean numeric references return
`invalid_task` and abort the evaluation rather than being averaged into positive
scores. Unsupported uppercase candidate labels are scored zero; this tightens
the source's permissive letter filtering (e.g. `AE` formerly matched `A`).

Five actual benchmark fixture cases over three repetitions match every score and
aggregate, with 88 observed verifyit calls. Four malformed-reference batches abort
without returning an aggregate. No JEEBench model-run links were found in the
campaign tracker or local JSON/JSONL artifacts; this is source fixture validation,
not archived-trace replay. Reproducible evidence is in campaign
`evidence/e2e/wiring/evalchemy-jee/source_roundtrip.py` (supports `--output`).


The English TruthfulQA MC2 override uses the harness probability-mass integration
from this same dependency checkpoint. Apply the harness
`truthfulqa-mc2-verifyit.patch` after its base/corpus patches; no override scorer
file change is required. The pinned callback body is verified, then raw likelihoods
and binary labels are graded inside verifyit. Native/source evaluator fixtures and
an isolated installed-package replay match. Three saved run links are frozen in
campaign `evidence/e2e/wiring/harness-mc2/truthfulqa-selection.json`; S3 access is
currently unavailable, so no archived TruthfulQA replay is claimed.

AMC23 literal normalization
---------------------------
Apply `amc23-verifyit.patch` to the pinned Evalchemy source. Enable the public
constructor with `AMC23Benchmark(..., verifyit_enabled=True)`, or use
`from eval.task import TaskManager` and
`TaskManager(task_list=["AMC23"], verifyit_enabled=True)`. The manager forwards
accepted benchmark kwargs; this is not a new CLI flag. Source extraction and
ten repetition aggregates remain. Known normalization errors fail closed
instead of using the original raw-equality fallback. Evidence is under
`evidence/e2e/wiring/evalchemy-amc-math`; AMC23 validation uses source fixtures,
with no matching archived AMC23 inputs found.

## NUPA component metrics

Apply `nupa-exact-verifyit.patch` after the existing Evalchemy patches. Opt in
through the public benchmark constructor:

```python
from importlib import import_module

Benchmark = import_module("eval.chat_benchmarks.NUPA5K-Loose.eval_instruct").NUPA5KLooseBenchmark
benchmark = Benchmark(verifyit_enabled=True)
```

Use `NUPA-Loose` and `NUPALooseBenchmark` for the other variant. Default source
execution remains available. The adapter calls strict exact grading for the full
digit-component tuple and each source-aligned digit comparison. It retains
`exact_match`, `digit_match`, `dlength`, `format_valid_rate` and `no_answer_rate`,
including all task, length-bucket and combined group denominators. This is not
numeric tolerance: `1.00` and `1.0` are different component representations.
Source preparation removes signs, including scientific exponent signs; the
source-defined component metric consequently treats `1.23e-5` and `1.23e5`
alike. That limitation is retained explicitly rather than described as numerical
equivalence.

References must match the complete declared format and contain valid nonempty
digit components. A malformed reference such as `abc123` formerly scored one
against output `123`; the opt-in evaluator now aborts the entire mixed batch.
Unexpected extraction failures propagate, so no partial aggregate is returned.

Three seeded NUPA5K tracker links replay all 15,000 saved responses. Every sample
matches the archive across all five metrics, and all aggregate/bucket metrics
match precisely. The untouched source additionally matches the first complete
run. NUPA-Loose shares this scorer but has source evaluator fixtures only.
Evidence and independent rerun commands are under
`evidence/e2e/wiring/evalchemy-nupa`. Downloads comprise only active sample and
configuration/result shards (86,065,656 bytes), with archive checksums verified;
no model regeneration or dataset download is needed for replay.
