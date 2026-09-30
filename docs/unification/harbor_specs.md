# Harbor integration extensions

These extensions reuse existing verifier categories. They are specified here
because the current API does not express all native score/runtime contracts.
Until implemented and checked against the source, retain the original harness
behind `script`; do not claim a direct primitive conversion.

## Structured report

Extend execution report handling with a declared CTRF format and ID policy,
rather than introducing a domain-specific DeepSWE mode. Configuration names the
command, report paths, `name` or `suite.name` identity, `must_pass`,
`must_not_break`, setup/restoration and timeout. Parse CTRF `results.tests` and
JUnit `classname.name` into stable per-test outcomes. Missing/skipped required
IDs fail. Merge duplicate observed failures with worst-status-wins. Require
nonempty `must_pass` for DeepSWE tasks. Preserve binary reward and auxiliary
f2p/p2p/partial fractions and their denominators.

DeepSWE's pinned 113 tasks use 35 JUnit and 78 CTRF contracts. JUnit can reuse
`junit` after copying exact whitelists and patch preparation. CTRF currently
needs the report-format extension or its original script. Original Go JSON
and pytest execution can instead use `gotest`/`pytest` only after proving their
IDs match the task-local reporter fixups. Do not infer IDs from language.

Hidden-test patch application failure is infrastructure failure; candidate
patch application failure scores zero. The source's `reward.txt=-1` trap is an
infrastructure sentinel and must become an unscored verdict before any scalar
score normalization. The task-specific suite commands remain unchanged.

## Judge profile

Extend `judge` with an explicit native profile describing answer extraction,
prompt template, response parser/schema, aggregation and model capability.
This is the same reusable judge-profile gap described by the Evalchemy
inventory; benchmark names should not create new verifier categories.
Harbor has binary label parsers (CORRECT/INCORRECT, SimpleQA labels), rubric
criteria and composite score/inversion policies. Retain native prompt and
label interpretation until fixture parity proves the configured profile.
Transport/model/schema failures must remain infrastructure errors.

## Artifact judge

Extend judge input with declared image/audio/artifact attachments and extraction
rules. The attachment list must bind to immutable grading artifacts, preserve
MIME types and resolve workspace-relative paths. A text-only judge is not a
faithful replacement for WebVoyager browser screenshots or graphics metrics.
Host capabilities must declare supported modalities. Missing modality/model
capability is infrastructure failure; absent candidate artifacts can score zero
when the benchmark declares that outcome. Existing scientific metrics such as
HOTA or circuit fidelity remain executable scripts, not model judgements.

## Native score

Keep verifyit's public scalar reward in [0,1], but preserve native numeric
metric maps in verdict detail and require an explicit selected metric and
transform. A configured transform should state its input domain and direction,
for example TextArena `(native_reward+1)/2` for [-1,1] game results. Negative R2
and native loss metrics need an explicit task policy; silently treating them as
candidate zero loses the source contract. Failure sentinels must be classified
before transforming valid scores. Persist scalar reward only for scored
verdicts. GDB's NIMA /10 and Frontier-CS /100 transforms already exist upstream
and should be retained, not applied twice.

## Precision rounding

Extend numeric comparison with declared decimal-place rounding and tie rule
when the source policy requires it. Quantization and comparison must use the
same decimal context as the source. A tolerance comparator alone cannot model
rounding: two close values straddling a rounding boundary can differ, while
values farther apart inside one rounded bin can match. BixBench verified-50
uses this declared deterministic policy before falling back to a semantic
judge. Cover boundary ties and negative values with source-derived fixtures.
