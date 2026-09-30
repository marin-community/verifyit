"""Render the human-readable coverage report from the generated entity register."""

# Long lines in the embedded Markdown tables are preserved for readable output.
# ruff: noqa: E501

import json
from collections import Counter, defaultdict
from pathlib import Path

root = Path.cwd()
d = json.loads((root / "docs/unification/coverage-gaps.json").read_text())
rows = [{**r, **d["coverage_contracts"][r["coverage_contract"]]} for r in d["entities"]]


def clean(value):
    return str(value).replace("|", "/").replace("\n", " ")


def first(value):
    return value.split(". ")[0] + ("." if ". " in value else "")


def table(source, statuses=None):
    selected = [r for r in rows if r["source"] == source and (statuses is None or r["status"] in statuses)]
    result = ["| Entity | Status | Existing mode | Why / needed change |", "| --- | --- | --- | --- |"]
    for r in selected:
        reason = r["reason"]
        change = r["needed_change"]
        text = (
            first(reason)
            if change.startswith("Implement this benchmark's client adapter")
            else first(reason) + " " + first(change)
        )
        result.append(
            "| "
            + " | ".join(
                clean(x) for x in (r["name"], r["status"], ", ".join(r["primitive_candidates"]) or "none", text)
            )
            + " |"
        )
    return "\n".join(result)


text = """# Coverage gaps

The remaining work is primarily client integration, source-specific comparison/judge profiles, and execution validation. A specification is not an implemented migration. Retaining the source scorer is compatibility or a hybrid route, not complete native equivalence. No unavoidable new verifier category has been identified.

| Source population | Implemented / available | Remaining coverage |
| --- | --- | --- |
| Harness 12,692 indexed task configs | 11,221 guarded native routes + 978 retained-runtime routes available | 493 configs have no cutover; breakdown below |
| Evalchemy 42 custom benchmarks | 8 native integrations + 3 math hybrids | 31 not integrated (20 client/comparator audits + 11 native profile gaps) |
| Evalchemy 21 task overrides | 2 native exact integrations + 1 native MC2 probability-mass integration + 1 GSM hybrid | 17 not integrated; plus 1 orchestration group |
SKYRL_SUMMARY_ROW
HARBOR_SUMMARY_ROW
| TaskTrove 81 cohorts, 861,848 metadata rows | all metadata routes and 19 converters/12 modes implemented | genuine archived task execution not validated; 0 unmapped metadata rows |

`capability_gap` means a proposed native contract is missing from an existing mode, not that the benchmark cannot execute through task-owned `ScriptSpec`. A source-preserving structured script bridge is an alternative where the task runtime and failure/metric contract are available. `not_integrated` means client wiring, source-contract translation or a comparator parity audit remains. `native_fallback` means an implemented cutover still calls a native source scorer. Validation-only gaps are listed separately; unavailable traces are never called unsupported.

## Harness: 493 indexed configurations without a cutover

The groups below are mutually exclusive. The exhaustive [register](coverage-gaps.json) contains every indexed config's name/path/hash, resolved metric options, source callable/hash/call evidence, status and coverage-contract reference. It also contains the 11,221 eligible records so counts can be audited; availability does not assert full dataset execution. The new 250 include 45 AfriQA exact/F1, 100 MasakhaNER span-F1, 100 MasakhaPOS token-accuracy and five ASK-GEC implicit-exact configurations; source API and evaluator fixtures pass, but no matching saved model traces were available.

The additional 31 Okapi TruthfulQA MC2 configs grade raw likelihoods and binary correctness labels inside verifyit. Stable softmax weights strict exact-index correctness, preserving probability mass over all true alternatives rather than first-argmax MCQ. All 31 source-pinned task guards and three seeded actual evaluator fixtures pass; malformed samples abort the batch, and mutated callbacks, aggregations and filters fail before execution. Direct source exponentiation can underflow to NaN for finite likelihoods; the cutover deliberately preserves the mathematically defined stable probability ratio. All-correct vectors remain exactly one. These multilingual fixtures are not archived-run replay.

The eight Hendrycks Math tasks now preserve source dollar-span/boxed-reference extraction and source string normalization, then call strict exact grading. Callback/helper code, globals/defaults, source hashes, default filters and registered mean are guarded. Eight registered configs, three seeded evaluator fixtures and early drift failures pass. The Math500 task also matches an untouched-source baseline on all 1,500 raw responses from three previously frozen custom MATH500 runs. Their producer uses boxed symbolic grading, so the archived custom scores are not equivalent: 471/492/453 records differ. This validates real-response scoring, not the producer's original generation configuration or archive score reproduction.

The 30 MMMU subject configurations now grade source-extracted choices with MCQ, prepared numeric values with exact-tolerance NumericSpec, and textual answers with strict substring ExactSpec. The actual multimodal evaluator preserves image arguments, source two-decimal rounding, alternative references, single-character padding and normal metrics/stderr. All 30 registered guards and three seeded evaluator fixtures pass. Source random guessing on missing choices is removed; empty/nonfinite gold that formerly scored one now aborts the batch. Five early callback/helper/aggregation/filter drift cases reject before execution. These are source fixtures, not archived model-run replay.

The 978 retained-runtime configs comprise 868 BLEU/CHRF/TER profiles, 40 default rolling-likelihood profiles, 28 default likelihood profiles (10 arithmetic, ASDiv, and 17 LAMBADA configs), 6 CodeXGLUE code-to-text profiles, and 36 XLSUM ROUGE profiles (12 languages x 3 prompts). The real guards enumerate each config in the register. Opt-in task factory metadata `verifyit_corpus_runtime=true` executes one complete batch through `ScriptSpec`, preserving all source observations and point aggregates (including BLEU's 100-point scale and unbounded perplexity) without scalar clipping. These are single-rank source-runtime integrations, not native primitive replacements. CodeXGLUE accepts only the pinned callable/utils hashes and registered mean. Source add-one smoothing gives empty candidates positive credit; the client deliberately scores empty/whitespace output zero while retaining every sample in the denominator. Nonempty source scores match. XLSUM preserves source passthrough observations and actual ROUGE aggregation. Its point computation runs at the normal per-task aggregation position, with evaluate's uint32 seed transferred to the producer; caller RNG state is unchanged. Multi-task fixtures match source metrics, normal stderr behavior and final RNG state, including a preadvanced state. Unsupported filters are rejected before execution. Source and actual evaluator fixtures pass; matching archived runs were unavailable in the tracker; inspected named ASDiv generation artifacts use a different SkyRL contract, so they cannot serve as harness likelihood replay. Empty references/denominators, nonfinite samples, producer failures and omitted observations abort evaluation without positive aggregate output. Custom task classes, custom scorers, unsupported metric options and distributed execution are excluded.

| Reason group | Configs | Why | Needed change |
| --- | ---: | --- | --- |
"""
groupdesc = {
    "custom_scorer": (
        "Custom process_results overrides the default scorer.",
        "Wire the concrete source function/input/metric contract; use existing modes by proven composition or a structured trusted script.",
    ),
    "python_class": (
        "Python task classes own scoring/request construction.",
        "Patch the actual class scorer, not only ConfigurableTask.",
    ),
    "likelihood_aggregate": (
        "Raw likelihood, weighted perplexity and bits statistics are not bounded correctness rewards.",
        "Retain raw observations and corpus aggregation through a metric/script adapter.",
    ),
    "translation_metrics": (
        "BLEU/CHRF/TER score translation overlap and require corpus tuples.",
        "Keep all translation metrics with original corpus aggregators.",
    ),
    "exact_plus_f1": (
        "Exact equality is reusable; simultaneous token/span F1 is not implemented.",
        "Compose exact with the source F1 profile and preserve both outputs.",
    ),
    "generation_f1": (
        "Token/span overlap gives partial credit.",
        "Wire the configured F1 function/normalizer and aggregation.",
    ),
    "generation_accuracy": (
        "Generation accuracy is outside the exact-only whitelist.",
        "Audit target types/source comparison, then add an explicit client route.",
    ),
    "callable_generation_metric": (
        "A single configured metric callable owns its scorer semantics.",
        "Translate the named callable contract or execute its trusted script; evidence is per config.",
    ),
    "mixed_callable_metrics": (
        "Mixed callable metrics need every named result and aggregator.",
        "Implement the entire metric profile rather than scalar projection.",
    ),
    "implicit_exact_default": (
        "Five ASK-GEC prompts inherit exact_match from the source registry.",
        "Recognize this valid implicit default in the eligibility guard; existing exact already fits.",
    ),
}
for group, count in d["harness_gap_groups"].items():
    why, change = groupdesc[group]
    text += f"| {group} | {count} | {why} | {change} |\n"
text += """
The 5 implicit-default configs `ask_gec_p0` through `ask_gec_p4` now use the guarded exact route.

The source population additionally has 834 groups and 456 templates (1,290 orchestration records). Runtime discovery matched all indexed tasks. Its 64 inline group members are separate: 60 declare include-based contracts whose includes the pinned source factory does not resolve, and 4 reference unknown task names. Seven malformed group members are retained as source configuration failures; these counts are not added to the indexed 493 gaps. Their complete names/configurations and failures are in the register.

## Evalchemy custom benchmarks

The 34 remaining custom benchmarks are named below. Script/stdio/pytest candidates already exist; source code extraction, trusted tests, resource/status rules and named aggregation still need client adapters. Math and judge rows preserve source-specific normalization, fallback and protocol requirements.

""" + table(
    "evalchemy-custom", {"not_integrated", "capability_gap"}
)
text += "\n\n### Implemented math/source fallbacks\n\n" + table("evalchemy-custom", {"native_fallback"})
text += "\n\n## Evalchemy overrides\n\n" + table("evalchemy-override", {"not_integrated", "native_fallback"})
text += """

## SkyRL

SKYRL_PENDING_SUMMARY

""" + table(
    "MarinSkyRL", {"not_integrated", "capability_gap"}
)
text += "\n\nThe two external objectives are not correctness verifiers:\n\n" + table(
    "MarinSkyRL", {"not_a_correctness_verifier"}
)
text += (
    "\n\n## Harbor\n\nThe HARBOR_PENDING_COUNT unwired adapters are named individually. Four answer-file clients invoke exact or MCQ grading; EvoEval, HumanEvalFix, BigCodeBench-Hard, AutoCodeBench, MMAU, CodePDE, ReplicationBench and CompileBench invoke the existing pytest route. ARC-AGI-2 grades the output grid with JSON-schema const in a separate verifier image. BFCL, DABstep and tau3 retain source scorers behind structured ScriptSpec clients. The historical 52 primitive-route and 34 runtime-bridge specifications remain a planning inventory; HARBOR_NATIVE_COUNT primitive clients are now implemented.\n\n"
    + table("harbor", {"not_integrated"})
)
text += "\n\n### Wired primitive clients\n\n" + table("harbor", {"native_route_available"})
text += "\n\n### Retained source evaluators\n\n" + table("harbor", {"native_fallback"})
boundary_rows = [
    row
    for row in rows
    if row["source"] == "harbor" and row.get("boundary_hardening", {}).get("status") == "shared_candidate_reachable"
]
text += (
    "\n\n### Shared verifier boundary\n\n"
    "HARBOR_BOUNDARY_COUNT wired clients still grade in Harbor's shared agent container. "
    "Harbor uploads trusted files after the agent phase, while a surviving candidate process "
    "can modify them. A generated GAIA task reproduced a wrong answer scoring one after its "
    "uploaded reference changed. This establishes the shared-container failure mode, not a "
    "per-route exploit for every row. These routes have client wiring but require a protected "
    "verifier environment before deployment. ARC-AGI-2 uses a separate verifier and passed "
    "the corresponding mutation replay.\n\n"
    "| Wired route | Candidate-reachable trusted assets |\n"
    "| --- | --- |\n"
)
for row in boundary_rows:
    text += f"| {clean(row['name'])} | {clean(row['boundary_hardening']['trusted_assets'])} |\n"
text += (
    "\n\n### Additional tracker replay requirements\n\nThese seven tracker datasets are separate from the 87 adapter census. Missing workspaces/provenance are artifact gaps, not unsupported verifier modes.\n\n"
    + table("harbor-tracker")
)
text += """

## Implemented but not validated

Babilong adds 20 guarded configs using default-off single-reference ExactSpec substring containment. The source response preprocessor executes exactly once; only target strip/lower and response lower follow, preserving internal whitespace and source Unicode behavior. All 20 config guards and three seeded evaluator witnesses pass. Four ordinary source cases match; a source empty-target sample formerly scores one and its mixed cutover batch now aborts. No named matching tracker/local saved runs were found, so this is fixture-only validation.

CrowS-Pairs adds 22 guarded configs: strict stereo/anti-stereo preference preserves ties through reversed likelihood choice, with unbounded likelihood difference and the original arithmetic means computed in verifyit. Both source preference metrics and ordinary stderr match untouched source fixtures. Nonfinite means or stderr abort, including finite-observation overflow witnesses. All 22 config guards and three seeded evaluator witnesses pass. No named matching tracker/local saved runs were found; these are source fixtures, not archived replay.

AGIEval adds 19 guarded multi-answer choice configs: raw and character-normalized likelihood winners grade against alternative gold indices through existing MCQ/exact primitives. All 19 registered config guards and three seeded actual evaluator witnesses pass, including mixed-invalid-batch abort and four early drift guards. Unicode lengths and ties preserve fresh source per-record acc/acc_norm values. No AGIEval-named tracker or local JSON/JSONL/Markdown artifacts were found; this is source-fixture validation, not archived-run validation.

Harness 978 retained-runtime configurations have source/evaluator fixture validation, without matching saved tracker runs. Harness 11,221 static-eligible configurations have implemented guards and representative source parity, but only PIQA/Winogrande/BoolQ have full selected real-run replays. The new 250 have source API and evaluator fixture validation without matching saved model traces. Evalchemy MMLUPro/GPQADiamond and AIME24/MATH500/GSM override have real replay evidence. AIW/GSM8KPerturbed/AIME25 have source parity but no validated tracker links. JEEBench opt-in constructor/extraction/evaluator roundtrips preserve three repetitions and partial credit; malformed references abort batches, unsupported uppercase labels are penalized, and no matching saved run links were available. AMC23 opt-in constructor/extraction/evaluator fixtures preserve ten repetitions and call exact after the pinned normalizer. Four malformed-reference batches abort, including a source raw-fallback case that formerly scored one. No matching AMC23 tracker links or direct local inputs were found; the 291 named local inputs are SkyRL Hendrycks/aime traces. NUPA-Loose and NUPA5K-Loose now call strict exact grading for complete digit-component equality and aligned digit matches, retaining all five named metrics and task/length/cross-bucket denominators. Three frozen NUPA5K runs replay all 15,000 raw responses with no per-sample or aggregate differences; NUPA-Loose shares the scorer but has evaluator fixtures only. Invalid references abort without aggregate output. Source preparation discards signs, including scientific exponent signs; exact_match is a digit-component metric, not numeric equivalence. NQ-Open/TriviaQA source exact routes lack full dataset replay. The English TruthfulQA MC2 override has actual source/evaluator fixture parity; three of thirteen matching tracker links were frozen before scoring, but S3 access is unavailable and no matching local JSON/JSONL artifacts were found. No archived TruthfulQA replay is claimed.

Harbor AIME, GAIA, GPQA Diamond and SATBench match 12 original-source task-script cases using actual patched CLI calls. One generated GAIA image ran two candidate cases with verifyit installed from the exact local API commit. The frozen eval-policy tracker and local run-manifest census have no matching saved model traces. The other three task images have not been built and run.

Harbor EvoEval's generated PytestSpec preserves the original binary all-tests policy. A generated task image matched original test.sh, direct verifyit CLI and the actual Harbor Verifier for one passing and one failing candidate; malformed protected-test collection produced infra_error and removed stale reward output. No matching saved model trace was available.

Harbor HumanEvalFix's generated PytestSpec likewise matched original test.sh, verifyit CLI and the actual Harbor Verifier on one passing and one failing generated task image. A malformed protected test produced infra_error without a reward. No matching saved model trace was available.

Harbor BigCodeBench-Hard keeps benchmark pytest on Python 3.10 while verifyit runs in a separate Python 3.11 environment. Its generated image matched original test.sh, direct CLI and Harbor Verifier for passing and failing candidates; a malformed protected test remained unscored without a reward. No matching saved model trace was available.

Harbor AutoCodeBench uses the task's uv-managed Python for source and PytestSpec runs. Its base image lacked uv; the patched image installs pinned uv 0.7.13 before either path executes. A generated image matched original test.sh, direct CLI and Harbor Verifier for passing and failing candidates; wheel-install failure and malformed protected-test collection left no positive reward. No matching saved model trace was available.

Harbor MMAU preserves the source CTRF artifact with PytestSpec arguments alongside verifyit's JSON report. A generated image matched original test.sh, direct CLI and Harbor Verifier for passing and failing candidates; both paths emitted the same CTRF pass/fail counts and Harbor retained the artifact. Malformed protected-test collection remained unscored without a reward. No matching saved model trace was available.

Harbor CodePDE's generated PytestSpec runs the unchanged upstream nRMSE evaluator in a protected directory for each of five PDE variants. The candidate solver receives only public numerical inputs in an unprivileged Landlock child; trusted code validates exact shape and finite values before computing the source metric and binary 0.05 threshold. Ten generated-image reference/wrong cases matched original test.sh, CLI and Harbor Verifier on bounded HDF5 fixtures. Seven adversarial cases reject source false positives from forged stdout and reference reads, along with reward writes and malformed outputs; missing/empty solvers stay unscored. A detached candidate child was reaped before scoring. Full-size data and saved model traces remain unvalidated.

Harbor ReplicationBench's generated PytestSpec executes the protected source comparator and preserves its binary all-tests policy and comparison artifact. A generated image matched original test.sh, direct CLI and Harbor Verifier for nested passing, wrong and missing-result fixtures. The source accepted a boolean as a numeric answer; the patched comparator scores it zero. Explicit null remains valid, while absent or malformed trusted references and incompatible tolerances are unscored. These are bounded generated fixtures; broader task data and saved model traces remain unvalidated.

Harbor BFCL's structured ScriptSpec keeps the source evaluator and task Python, with verifyit on a separate Python 3.11 runtime. Eleven generated-image cases matched original test.sh, direct CLI and Harbor Verifier across simple, live relevance, irrelevance and parallel calls. Two source false positives from boolean/numeric and overflowing numeric-string comparisons score zero after hardening; a malformed protected evaluator is unscored. Other categories and the linked bfclparity-pi model workspaces remain unvalidated because the available AWS SSO token expired.

SkyRL AIME normal scoring has real replay evidence, but its strict-box subprofile has source-test validation only. Ten patched routes lack eligible replay links: three earlier routes, the Nemotron SWE pivot tool route, two dormant QA APIs, legacy text2sql and three dormant math APIs. These routes have source-fixture validation, with documented intentional math corrections; the SWE pivot dispatches to Harbor in the observed population.

""" + table(
    "MarinSkyRL", {"implemented_not_validated"}
)
text += """

TaskTrove's 81 cohorts below account for 861,848 metadata rows, 43 sources and 63 templates. All route to existing modes; the pipeline/install migration is implemented. Their embedded checker payloads and genuine candidate executions have not been replayed. This is a validation gap, not 81 unsupported benchmarks. Converter/mode/helper closure evidence is separately preserved in the register.

| Source | Rows | Converter | Existing modes |
| --- | ---: | --- | --- |
"""
groups = defaultdict(list)
for row in rows:
    if row["source"] == "task-trove":
        groups[row["name"]].append(row)
assert len(groups) == 43
for name, group in sorted(groups.items()):
    text += (
        "| "
        + " | ".join(
            clean(x)
            for x in (
                name,
                sum(r["rows"] for r in group),
                ", ".join(sorted({r["converter"] for r in group})),
                ", ".join(sorted({m for r in group for m in r["primitive_candidates"]})),
            )
        )
        + " |\n"
    )
text += """
## Scope, evidence and regeneration

The register covers pinned snapshots only, not future revisions or external plugins. Source revisions and exact evidence are stored per entity. Reconciliation is automatic: indexed harness 13,982 = 12,692 tasks + 834 groups + 456 templates; tasks 12,692 = 11,221 native available + 978 retained-runtime available + 493 remaining; Evalchemy 42 custom + 22 override configs; SkyRL 48 entries; Harbor 87 adapters; TaskTrove 81 cohorts with 861,848 rows plus 19 converter, 12 mode and 7 helper contracts. Seven Harbor tracker datasets and 64 harness inline definitions are separate populations and must not be added to those source denominators.

The [replay report](e2e-replay.md) records the earlier campaign baseline and exceptions: Evalchemy/harness 24 runs matched 63,360 samples; SkyRL 66/66 pinned-native and 65/66 archived results; Harbor 1,101 trials preserve 37 recovered zeros, 10 infrastructure failures and 3 database discrepancies. Later opt-in SkyRL cutovers add nine Reasoning Gym/MCQA, six tool, three calendar, three SQL, three Lean, six code, fifteen structured-output, twelve formatting and fifteen instruction random selections under campaign `evidence/e2e/wiring/`, plus two separately selected supplemental code positives; Reasoning Gym rejects boolean scorer results, and typed tool comparison rejects a boolean argument for an integer reference. Calendar rejects invalid clock values, boolean/negative/nonfinite durations and malformed reference constraints; zero durations retain source behavior. Full archived parity remains unvalidated.

Regenerate from the campaign worktree with the pinned read-only sources:

```bash
uv run python tools/unification/coverage_gaps.py --sources ../sources \\
  --fragments tools/unification/coverage_inputs
uv run python tools/unification/render_coverage_gaps.py
```

Each entity resolves `coverage_contract` in the top-level contract table for its reason, existing mode candidates, required change and validation status. Small curated peer inputs retain their exact source contracts; generated JSON is one entity per line and can be queried by source/name/status/reason. Raw datasets and replay credentials are not included.
"""
skyrl_counts = Counter(r["status"] for r in rows if r["source"] == "MarinSkyRL")
validated = skyrl_counts["implemented_validated"]
unvalidated = skyrl_counts["implemented_not_validated"]
external = skyrl_counts["not_a_correctness_verifier"]
scoring = sum(skyrl_counts.values()) - external
summary = (
    f"| SkyRL {scoring} scoring routes | {validated + unvalidated} source-patched "
    f"({validated} with selected real traces, {unvalidated} without eligible real traces) | "
    f"{skyrl_counts['not_integrated']} partial client/harness routes + "
    f"{skyrl_counts['capability_gap']} native profile gaps; {external} external-objective placeholders separate |"
)
text = text.replace("SKYRL_SUMMARY_ROW", summary)
pending_skyrl = [r for r in rows if r["source"] == "MarinSkyRL" and r["status"] in {"not_integrated", "capability_gap"}]
pending_active = sum(bool(r.get("active_in_pinned_dispatch")) for r in pending_skyrl)
pending_dormant = sum(bool(r.get("dormant")) for r in pending_skyrl)
text = text.replace(
    "SKYRL_PENDING_SUMMARY",
    f"The {len(pending_skyrl)} pending scoring routes comprise {pending_active} active routes and "
    f"{pending_dormant} dormant implementations. Three dormant math variants now have opt-in source "
    "integrations and fixture evidence; archived traces remain unavailable. "
    f"{skyrl_counts['capability_gap']} rows need a native comparator/registry/schema/judge profile in an "
    "existing class; a task-owned structured source bridge remains an alternative. "
    "The full register preserves active/dormant dispatch and source hashes.",
)
harbor_counts = Counter(r["status"] for r in rows if r["source"] == "harbor")
harbor_total = sum(harbor_counts.values())
harbor_native = harbor_counts["native_route_available"]
harbor_pending = harbor_counts["not_integrated"]
harbor_fallback = harbor_counts["native_fallback"]
assert harbor_total == 87
assert harbor_native + harbor_pending + harbor_fallback == harbor_total
assert (
    len(boundary_rows)
    + sum(
        r.get("boundary_hardening", {}).get("status") == "separate_verifier_validated"
        for r in rows
        if r["source"] == "harbor"
    )
    == harbor_native + harbor_fallback
)
text = text.replace(
    "HARBOR_SUMMARY_ROW",
    f"| Harbor {harbor_total} adapters | {harbor_native} native primitive clients + "
    f"{harbor_fallback} structured source-runtime bridges | {harbor_pending} not integrated; "
    f"{len(boundary_rows)} wired routes need verifier isolation |",
)
text = text.replace("HARBOR_PENDING_COUNT", str(harbor_pending))
text = text.replace("HARBOR_NATIVE_COUNT", str(harbor_native))
text = text.replace("HARBOR_BOUNDARY_COUNT", str(len(boundary_rows)))
(root / "docs/unification/coverage-gaps.md").write_text(text)
