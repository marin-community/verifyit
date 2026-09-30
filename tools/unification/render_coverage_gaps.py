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
| Harness 12,692 indexed task configs | 11,091 guarded native routes available | 1,601 configs retain source scoring; breakdown below |
| Evalchemy 42 custom benchmarks | 4 native integrations + 3 math hybrids | 35 not integrated (24 client/comparator audits + 11 native profile gaps) |
| Evalchemy 21 task overrides | 2 native exact integrations + 1 GSM hybrid | 18 not integrated; plus 1 orchestration group |
SKYRL_SUMMARY_ROW
| Harbor 87 adapters | tau3 structured native-runtime bridge | 86 not integrated; tau3 retains native evaluator |
| TaskTrove 81 cohorts, 861,848 metadata rows | all metadata routes and 19 converters/12 modes implemented | genuine archived task execution not validated; 0 unmapped metadata rows |

`capability_gap` means a proposed native contract is missing from an existing mode, not that the benchmark cannot execute through task-owned `ScriptSpec`. A source-preserving structured script bridge is an alternative where the task runtime and failure/metric contract are available. `not_integrated` means client wiring, source-contract translation or a comparator parity audit remains. `native_fallback` means an implemented cutover still calls a native source scorer. Validation-only gaps are listed separately; unavailable traces are never called unsupported.

## Harness: 1,601 non-native indexed configurations

The groups below are mutually exclusive. The exhaustive [register](coverage-gaps.json) contains every indexed config's name/path/hash, resolved metric options, source callable/hash/call evidence, status and coverage-contract reference. It also contains the 11,091 eligible records so counts can be audited; availability does not assert full dataset execution. The new 250 include 45 AfriQA exact/F1, 100 MasakhaNER span-F1, 100 MasakhaPOS token-accuracy and five ASK-GEC implicit-exact configurations; source API and evaluator fixtures pass, but no matching saved model traces were available.

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

The source population additionally has 834 groups and 456 templates (1,290 orchestration records). Runtime discovery matched all indexed tasks. Its 64 inline group members are separate: 60 declare include-based contracts whose includes the pinned source factory does not resolve, and 4 reference unknown task names. Seven malformed group members are retained as source configuration failures; these counts are not added to the indexed 1,601 gaps. Their complete names/configurations and failures are in the register.

## Evalchemy custom benchmarks

The 35 remaining custom benchmarks are named below. Script/stdio/pytest candidates already exist; source code extraction, trusted tests, resource/status rules and named aggregation still need client adapters. Math and judge rows preserve source-specific normalization, fallback and protocol requirements.

""" + table(
    "evalchemy-custom", {"not_integrated", "capability_gap"}
)
text += "\n\n### Implemented math/source fallbacks\n\n" + table("evalchemy-custom", {"native_fallback"})
text += "\n\n## Evalchemy overrides\n\n" + table("evalchemy-override", {"not_integrated", "native_fallback"})
text += """

## SkyRL

The 26 pending scoring routes comprise 19 active routes and 7 dormant implementations. Three dormant math variants are parity audits, not claims of a missing math API. Nineteen rows need a native comparator/registry/schema/judge profile in an existing class; a task-owned structured source bridge remains an alternative. The full register preserves active/dormant dispatch and source hashes.

""" + table(
    "MarinSkyRL", {"not_integrated", "capability_gap"}
)
text += "\n\nThe two external objectives are not correctness verifiers:\n\n" + table(
    "MarinSkyRL", {"not_a_correctness_verifier"}
)
text += (
    "\n\n## Harbor\n\nThe 86 unwired adapters are named individually. The historical 52 primitive-route and 34 runtime-bridge specifications are proposals, not 86 implemented cutovers.\n\n"
    + table("harbor", {"not_integrated"})
)
text += "\n\n### Retained native evaluator\n\n" + table("harbor", {"native_fallback"})
text += (
    "\n\n### Additional tracker replay requirements\n\nThese seven tracker datasets are separate from the 87 adapter census. Missing workspaces/provenance are artifact gaps, not unsupported verifier modes.\n\n"
    + table("harbor-tracker")
)
text += """

## Implemented but not validated

Harness 11,091 static-eligible configurations have implemented guards and representative source parity, but only PIQA/Winogrande/BoolQ have full selected real-run replays. The new 250 have source API and evaluator fixture validation without matching saved model traces. Evalchemy MMLUPro/GPQADiamond and AIME24/MATH500/GSM override have real replay evidence. AIW/GSM8KPerturbed/AIME25 have source parity but no validated tracker links. NQ-Open/TriviaQA source exact routes lack full dataset replay.

SkyRL AIME normal scoring has real replay evidence, but its strict-box subprofile has source-test validation only. Seven patched routes lack eligible replay links: three earlier routes, the Nemotron SWE pivot tool route, two dormant QA APIs and legacy text2sql. The latter have source-fixture parity; the SWE pivot dispatches to Harbor in the observed population.

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

The register covers pinned snapshots only, not future revisions or external plugins. Source revisions and exact evidence are stored per entity. Reconciliation is automatic: indexed harness 13,982 = 12,692 tasks + 834 groups + 456 templates; tasks 12,692 = 11,091 available + 1,601 remaining; Evalchemy 42 custom + 22 override configs; SkyRL 48 entries; Harbor 87 adapters; TaskTrove 81 cohorts with 861,848 rows plus 19 converter, 12 mode and 7 helper contracts. Seven Harbor tracker datasets and 64 harness inline definitions are separate populations and must not be added to those source denominators.

The [replay report](e2e-replay.md) records the earlier campaign baseline and exceptions: Evalchemy/harness 24 runs matched 63,360 samples; SkyRL 66/66 pinned-native and 65/66 archived results; Harbor 1,101 trials preserve 37 recovered zeros, 10 infrastructure failures and 3 database discrepancies. Later opt-in SkyRL cutovers add 18 selected real-trace matches under campaign `evidence/e2e/wiring/`; Reasoning Gym rejects boolean scorer results, and typed tool comparison rejects a boolean argument for an integer reference. Calendar rejects invalid clock values, boolean/negative/nonfinite durations and malformed reference constraints; zero durations retain source behavior. Full archived parity remains unvalidated.

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
    f"{skyrl_counts['not_integrated']} client/parity-audit routes + "
    f"{skyrl_counts['capability_gap']} native profile gaps; {external} external-objective placeholders separate |"
)
text = text.replace("SKYRL_SUMMARY_ROW", summary)
(root / "docs/unification/coverage-gaps.md").write_text(text)
