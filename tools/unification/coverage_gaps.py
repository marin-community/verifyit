"""Consolidate pinned source coverage without treating specifications as integrations."""

import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

from eval_inventory import resolve_config

from verifyit.adapters.harness_native import native_config_route

CUSTOM = {
    "AMC23": (
        "math",
        (
            "Source Minerva normalization/SymPy comparison is not the boxed parser "
            "profile; retain no-parse and relation semantics in a client adapter."
        ),
    ),
    "HMMT": (
        "math",
        (
            "MathArena parse_answer/check_answers accepts structured answers and parser "
            "warnings; its comparator has not been mapped to the existing math profile."
        ),
    ),
    "JEEBench": (
        "math",
        (
            "Type-dependent compute_score dispatch distinguishes numeric, option and "
            "multi-answer cases; no task-type client dispatch is wired."
        ),
    ),
    "OlympiadBench": (
        "math/judge",
        (
            "Alternative-reference Minerva/SymPy comparison plus judge fallback requires "
            "explicit ordered fallback and the source judge protocol."
        ),
    ),
    "OlympiadBenchDeterministic": (
        "math",
        (
            "Deterministic alternative-reference Minerva/SymPy comparison needs source "
            "normalization and comparator parity before client wiring."
        ),
    ),
    "OlympiadBenchFull": (
        "math/judge",
        (
            "Full Olympiad grading combines answer alternatives, deterministic "
            "comparison and configured equivalence judge; source fallback ordering is "
            "not integrated."
        ),
    ),
    "IFEval": (
        "ifeval",
        (
            "Official instruction registry and strict/loose instruction/prompt vectors "
            "differ from approximate core checkers; implement the registry profile and "
            "preserve denominators."
        ),
    ),
    "IFBench": (
        "ifeval/script",
        (
            "IFBench evaluate_accuracy uses its instruction registry and named result "
            "vectors; no source registry adapter is wired."
        ),
    ),
    "FinanceBench": (
        "judge",
        (
            "judge_equivalence uses a pinned equivalence prompt, response parser, "
            "endpoint retries and named failure records; the default reference rubric is "
            "not equivalent."
        ),
    ),
    "HLE": (
        "judge",
        (
            "Source semantic-answer judge and repeated-trial scoring require its exact "
            "prompt/parser and failure contract, not the default rubric."
        ),
    ),
    "SimpleQA": (
        "judge",
        (
            "Source A/B/C classifier preserves correct/incorrect/not-attempted labels "
            "and attempted-denominator F1; core rubric does not expose that classifier "
            "profile."
        ),
    ),
    "SimpleQAMini": (
        "judge",
        (
            "Mini dataset uses the same A/B/C classifier and attempted-denominator "
            "metrics; no classifier client integration exists."
        ),
    ),
    "MTBench": (
        "judge",
        (
            "Single/pairwise multi-turn matches use task judge templates and "
            "turn-specific aggregation; rubric-only scoring loses match labels and turn "
            "metrics."
        ),
    ),
    "MixEval": (
        "judge",
        (
            "Source judge-result files and compute_metrics_p preserve task-specific "
            "evaluation labels and score aggregation; neither prompt/parser nor "
            "result-file adapter is wired."
        ),
    ),
    "WildBench": (
        "judge",
        (
            "Pairwise evaluator output and reference comparison require the exact source "
            "prompt/parser and per-item outcome aggregation."
        ),
    ),
    "alpaca_eval": (
        "judge/script",
        (
            "Alpaca evaluator pairwise annotations and leaderboard aggregation, "
            "including length control, are source-owned; no annotation-to-verdict client "
            "is integrated."
        ),
    ),
    "CodeElo": (
        "stdio/script",
        (
            "Source concurrent case execution and difficulty/rating statistics need "
            "stdin/callable case translation and retained rating aggregation."
        ),
    ),
    "CodeForces": (
        "stdio/script",
        (
            "Contest code case execution, difficulty groups and repeated success metrics "
            "need protected test inputs and an explicit task adapter."
        ),
    ),
    "BigCodeBench": (
        "script/pytest",
        (
            "Functional correctness runner requires its imports/resources and trusted "
            "tests; no candidate-artifact/restored-test adapter is wired."
        ),
    ),
    "CruxEval": (
        "script/exact",
        (
            "evaluate_generations runs input/output prediction cases with its "
            "serialization and execution harness; no case codec/source-output adapter is "
            "wired."
        ),
    ),
    "HumanEval": (
        "script/pytest",
        (
            "Functional correctness and pass@k need extracted candidate code, trusted "
            "tests and per-trial success records; benchmark client is not wired."
        ),
    ),
    "HumanEvalPlus": (
        "script/pytest",
        (
            "EvalPlus artifact validation and extended test cases need protected "
            "artifacts, source tolerances and pass@k aggregation; adapter is absent."
        ),
    ),
    "MBPP": (
        "script/pytest",
        (
            "MBPP callable tests and candidate extraction need protected task tests and "
            "per-trial pass records; adapter is absent."
        ),
    ),
    "MBPPPlus": (
        "script/pytest",
        (
            "EvalPlus MBPP extended tests and artifact validation need source "
            "tolerance/case semantics and protected fixtures; adapter is absent."
        ),
    ),
    "LiveCodeBench": (
        "stdio/script",
        (
            "Source run_test dispatch includes stdin and callable modes with "
            "compile/runtime/timeout labels; case codec and runner adapter are not "
            "integrated."
        ),
    ),
    "LiveCodeBenchv5": (
        "stdio/script",
        (
            "Version5 source tests retain stdin/callable dispatch, resource limits and "
            "repeated/pass@k statistics; client translation is absent."
        ),
    ),
    "LiveCodeBenchv5_official": (
        "script",
        (
            "Official evaluator owns its test serialization, runner dependencies and "
            "pass@k outputs; no protected source-runner ScriptSpec adapter is wired."
        ),
    ),
    "MultiPLE": (
        "script",
        (
            "Language-specific compiler/runtime dispatch and functional tests cannot be "
            "inferred as Python tests; explicit language images and source runner "
            "adapter are absent."
        ),
    ),
    "SWEbench": (
        "script",
        (
            "run_evaluation requires repository/image preparation, candidate patch "
            "application and protected test identities; no task-image adapter is wired."
        ),
    ),
    "RepoBench": (
        "exact/script",
        (
            "Both exact_match_score and edit_similarity_score are required; exact exists "
            "but source edit similarity and named aggregation remain unintegrated."
        ),
    ),
    "MRCR": (
        "script",
        (
            "Character similarity and needle/context-bin aggregates are non-binary "
            "source metrics; preserve them through a named-result script adapter."
        ),
    ),
    "NUPA-Loose": (
        "script/numeric",
        (
            "score_prediction exposes digit/format/task-length metrics; numeric "
            "tolerance alone is insufficient and the source metric adapter is absent."
        ),
    ),
    "NUPA5K-Loose": (
        "script/numeric",
        "5K variant shares digit/format and task/length-bucket metrics; no source metric adapter is wired.",
    ),
    "LiveBench": (
        "script",
        (
            "gen_judgments dispatches multiple category/task/date scorer families; no "
            "per-family trusted scorer and metric adapter is integrated."
        ),
    ),
    "zeroeval": (
        "script/exact",
        (
            "Private-solution evaluation and zebra_grid_eval_model require source task "
            "dispatch and grid/solution artifact handling; no adapter is wired."
        ),
    ),
}


def metric_name(value):
    return value if isinstance(value, str) else value.get("value", "callable") if isinstance(value, dict) else str(value)


def classify_harness(config):
    if config.get("class"):
        return (
            "python_class",
            (
                "Python task class owns request construction/scoring; ConfigurableTask-only "
                "routing cannot intercept its scorer."
            ),
            ["script"],
        )
    if config.get("process_results"):
        return (
            "custom_scorer",
            (
                "Configured process_results overrides the default scorer; its source "
                "callable, input shape and named metrics need an explicit client adapter."
            ),
            ["script"],
        )
    output = config.get("output_type", "generate_until")
    metrics = config.get("metric_list")
    if output in {"loglikelihood", "loglikelihood_rolling"}:
        return (
            "likelihood_aggregate",
            (
                "Raw likelihood/perplexity/bits metrics require weighted corpus statistics, "
                "not bounded candidate reward; preserve raw observations and source "
                "aggregation."
            ),
            ["script", "mcq"],
        )
    if metrics is None:
        return (
            "implicit_exact_default",
            (
                "Valid generate_until configuration inherits exact_match from "
                "DEFAULT_METRIC_REGISTRY; the current eligibility guard does not recognize "
                "this implicit default."
            ),
            ["exact"],
        )
    names = [metric_name(m.get("metric")) for m in metrics]
    if set(names) <= {"bleu", "chrf", "ter"}:
        return (
            "translation_metrics",
            (
                "Corpus BLEU/CHRF/TER need reference/prediction tuples and corpus "
                "aggregators; exact equality would discard graded translation metrics."
            ),
            ["script"],
        )
    if names == ["exact_match", "f1"]:
        return (
            "exact_plus_f1",
            (
                "Exact is reusable, but simultaneous token/span F1 and both named outputs "
                "are not implemented by the one-metric exact route."
            ),
            ["exact", "script"],
        )
    if names == ["f1"]:
        return (
            "generation_f1",
            (
                "Generation F1 needs its configured token/span scorer and aggregation; "
                "literal exact is not equivalent to partial overlap."
            ),
            ["exact", "script"],
        )
    if names == ["acc"]:
        return (
            "generation_accuracy",
            (
                "Source generation accuracy metric is not whitelisted by the exact-only "
                "generation route; audit its target typing/comparison and wire an explicit "
                "metric adapter."
            ),
            ["exact"],
        )
    if len(metrics) == 1 and isinstance(metrics[0].get("metric"), dict):
        return (
            "callable_generation_metric",
            (
                "A configured metric callable owns normalization/partial score semantics; "
                "source function evidence must drive client composition or retained-script "
                "integration."
            ),
            ["script", "exact"],
        )
    return (
        "mixed_callable_metrics",
        (
            "Multiple/callable generation metrics require all source named outputs and "
            "aggregators; the single exact projection cannot replace this profile."
        ),
        ["script", "exact"],
    )


def callable_contracts(source, config):
    evidence = []
    values = [config.get("process_results"), config.get("class")]
    for metric in config.get("metric_list") or []:
        values.extend([metric.get("metric"), metric.get("aggregation")])
    for value in values:
        if not isinstance(value, dict) or value.get("tag") != "function":
            continue
        symbol = value["value"]
        module, _, name = symbol.rpartition(".")
        base = Path(value["source_dir"])
        path = base / (module.replace(".", "/") + ".py")
        if not path.exists():
            path = source / (module.replace(".", "/") + ".py")
        item = {"symbol": symbol}
        if path.exists():
            item.update(path=str(path.relative_to(source)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            tree = ast.parse(path.read_text())
            node = next(
                (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name), None
            )
            if node is not None:
                item["line"] = node.lineno
                item["calls"] = sorted({ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)})
        else:
            item["external_module"] = module
        evidence.append(item)
    return evidence


def base_entity(source, record, revision, name):
    return {
        "source": source,
        "name": name,
        "entity_id": source + ":" + record["path"],
        "source_revision": revision,
        "source_evidence": [{"path": record["path"], "sha256": record["sha256"]}],
    }


def harness_entities(root, sources):
    inventory = json.loads((root / "docs/unification/lm_eval_inventory.json").read_text())
    entities = []
    for record in inventory["configs"]:
        entity = base_entity(
            "lm-eval-harness", record, inventory["revision"], record.get("task") or record.get("group") or record["path"]
        )
        if record["kind"] != "task":
            entity.update(
                status="orchestration",
                kind=record["kind"],
                reason_id="group_or_template",
                reason="Group expansion or inherited configuration template, not a separate candidate scorer.",
                primitive_candidates=[],
                needed_change="No separate verifier integration; validate referenced tasks.",
                validation_status="source_population_audit",
            )
        elif record.get("native_route") or (
            (
                "/afrobench/" in record["path"]
                and any(
                    f"/afrobench/{family}/prompt_" in record["path"] for family in ("afriqa", "masakhaner", "masakhapos")
                )
            )
            or (isinstance(record.get("task"), str) and record["task"].startswith("ask_gec_p"))
        ):
            route = record.get("native_route")
            if route is None:
                config, _ = resolve_config(sources / "lm-eval-harness" / record["path"])
                route = native_config_route(config)
                assert route in {"afriqa_f1", "ner_span_f1", "pos_accuracy", "exact_match"}, record["path"]
            entity.update(
                status="native_route_available",
                kind="task",
                reason_id=route,
                reason=(
                    "Resolved configuration matches an implemented guarded default scorer route; "
                    "this is eligibility, not full dataset execution."
                ),
                primitive_candidates=(
                    [record["existing_mode"]] if record["existing_mode"] != "script" else ["exact", "script"]
                ),
                needed_change="No known scorer change; validate task datasets/runtime before deployment.",
                validation_status=(
                    "real_trace"
                    if record["task"] in {"piqa", "winogrande", "boolq"}
                    else "configuration_eligible_not_dataset_validated"
                ),
            )
        else:
            config, _ = resolve_config(sources / "lm-eval-harness" / record["path"])
            group, reason, modes = classify_harness(config)
            contracts = callable_contracts(sources / "lm-eval-harness", config)
            entity.update(
                status="not_integrated",
                kind="task",
                reason_id=group,
                reason=reason,
                primitive_candidates=modes,
                needed_change=(
                    "Implement the source-specific adapter preserving the metric profile below; "
                    "source delegation currently provides compatibility only."
                ),
                validation_status="source_contract_only",
                blockers=["client_wiring"],
                metric_profile=config.get("metric_list"),
                output_type=config.get("output_type", "generate_until"),
                scorer_contracts=contracts,
            )
            if group == "implicit_exact_default":
                entity["needed_change"] = (
                    "Recognize the pinned registry's implicit generation exact default in "
                    "native_config_route and validate equivalent source scoring."
                )
        entities.append(entity)
    for index, record in enumerate(inventory["runtime_discovery"]["inline_tasks"]):
        entities.append(
            {
                "source": "lm-eval-harness-inline",
                "entity_id": f"lm-eval-harness-inline:{index}:{record['name']}",
                "name": record["name"],
                "source_revision": inventory["revision"],
                "status": "invalid_source" if record.get("source_failure") else "not_integrated",
                "reason_id": "invalid_inline" if record.get("source_failure") else "inline_override",
                "reason": record.get("source_failure")
                or (
                    "Inline group task configuration overrides an indexed task's scorer/metrics; "
                    "its effective contract needs a dedicated guarded adapter."
                ),
                "primitive_candidates": [record.get("existing_mode", "script")],
                "needed_change": (
                    "Repair malformed source configuration."
                    if record.get("source_failure")
                    else "Resolve the inline task's complete configuration and wire its effective source contract."
                ),
                "source_evidence": [{"path": record.get("source_path")}],
                "validation_status": "runtime_population_audit",
                "effective_config": record.get("config"),
                "source_scorer": record.get("source_scorer"),
            }
        )
    return entities, inventory["runtime_discovery"]


def evalchemy_entities(root):
    inventory = json.loads((root / "docs/unification/evalchemy_inventory.json").read_text())
    entities = []
    for record in inventory["benchmarks"]:
        name = record["benchmark"]
        entity = base_entity("evalchemy-custom", record, inventory["revision"], name)
        entity["source_evidence"].extend(record["scoring_evidence"])
        if record["classification"] == "adapter":
            entity.update(
                status="native_integrated",
                reason_id="custom_native",
                reason="Concrete source client patch calls an existing primitive after source extraction/normalization.",
                primitive_candidates=["numeric" if name == "GSM8KPerturbed" else record["primitive_candidate"]],
                needed_change="No known scorer change.",
                validation_status=(
                    "real_trace" if name in {"MMLUPro", "GPQADiamond"} else "source_parity_no_tracker_trace"
                ),
            )
        elif record["classification"] == "adapter-hybrid":
            entity.update(
                status="native_fallback",
                reason_id="minerva_fallback",
                reason=(
                    "Boxed math is integrated, but missing parse explicitly retains Minerva "
                    "comparison; complete native comparator equivalence is not implemented."
                ),
                primitive_candidates=["math"],
                needed_change=(
                    "Map the remaining Minerva normalization/comparison semantics without "
                    "changing no-parse fallback behavior."
                ),
                validation_status="source_parity_no_tracker_trace" if name == "AIME25" else "real_trace",
            )
        else:
            modes, reason = CUSTOM[name]
            entity.update(
                status="not_integrated",
                reason_id="custom_" + name,
                reason=reason,
                primitive_candidates=modes.split("/"),
                needed_change=(
                    "Implement this benchmark's client adapter and preserve its named/vector "
                    "metrics and failure contract."
                ),
                validation_status="source_contract_only",
                blockers=["client_wiring"],
            )
            if name in {
                "IFEval",
                "FinanceBench",
                "HLE",
                "SimpleQA",
                "SimpleQAMini",
                "MTBench",
                "MixEval",
                "WildBench",
                "alpaca_eval",
                "OlympiadBench",
                "OlympiadBenchFull",
            }:
                entity["status"] = "capability_gap"
                entity["blockers"].append("existing_mode_profile_or_comparator")
        entities.append(entity)
    for record in inventory["harness_overrides"]:
        name = record.get("task")
        entity = base_entity("evalchemy-override", record, inventory["revision"], name)
        if record["kind"] != "task":
            entity.update(
                status="orchestration",
                reason_id="override_group",
                reason="Group expands the fifteen uncheatable tasks; no separate scoring primitive.",
                primitive_candidates=[],
                needed_change="Validate constituent tasks.",
                validation_status="source_population_audit",
            )
        elif name in {"nq_open", "triviaqa"}:
            entity.update(
                status="native_integrated",
                reason_id="override_exact",
                reason="Configured source exact normalization is wired through the existing harness exact route.",
                primitive_candidates=["exact"],
                needed_change="No known scorer change; full dataset replay remains unvalidated.",
                validation_status="source_parity_not_dataset_validated",
            )
        elif name == "gsm8k":
            entity.update(
                status="native_fallback",
                reason_id="gsm_rational_symbolic",
                reason=(
                    "Canonical Fraction equality calls strict exact; non-rational predictions "
                    "retain source Minerva symbolic scoring."
                ),
                primitive_candidates=["exact", "math"],
                needed_change="Map non-rational Minerva semantics if removing source fallback is required.",
                validation_status="real_trace",
            )
        else:
            reason = (
                (
                    "Weighted raw likelihood/token/byte metrics need original observations and "
                    "corpus aggregation, not candidate exact reward."
                )
                if name.startswith("uncheatable_")
                else {
                    "drop": (
                        "DROP normalized exact and token F1 require both named outputs and "
                        "alternative/multi-span answer handling."
                    ),
                    "humaneval": (
                        "Generated code functional correctness requires trusted tests and execution "
                        "resource/pass@k handling."
                    ),
                    "truthfulqa_mc2": (
                        "MC2 normalizes exponentiated likelihood probability mass over true "
                        "alternatives; first-argmax MCQ is not equivalent."
                    ),
                }[name]
            )
            entity.update(
                status="not_integrated",
                reason_id="override_" + ("uncheatable_likelihood" if name.startswith("uncheatable_") else name),
                reason=reason,
                primitive_candidates=["script"] if name != "drop" else ["exact", "script"],
                needed_change=(
                    "Implement the source override adapter preserving its metric observations " "and source aggregation."
                ),
                validation_status="source_contract_only",
                blockers=["client_wiring"],
            )
        entities.append(entity)
    return entities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/unification/coverage-gaps.json"))
    args = parser.parse_args()
    args.sources = args.sources.resolve()
    root = Path.cwd()
    entities, runtime = harness_entities(root, args.sources)
    entities.extend(evalchemy_entities(root))
    fragments = []
    for path in sorted(args.fragments.glob("*.json")):
        if path.name not in {"skyrl.json", "harbor_trove.json"}:
            continue
        fragment = json.loads(path.read_text())
        fragments.append({"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        if path.name == "harbor_trove.json":
            for category, project in (
                ("harbor_entries", "harbor"),
                ("task_trove_cohorts", "task-trove"),
                ("tracker_replay_requirements", "harbor-tracker"),
            ):
                for row in fragment[category]:
                    source_evidence = row["source_evidence"]
                    if isinstance(source_evidence, dict):
                        source_evidence = [source_evidence]
                    entities.append(
                        {
                            **row,
                            "source": project,
                            "reason_id": row["gap_kind"],
                            "source_evidence": source_evidence,
                            "evidence": [e.split("#")[0] if ".json#" in e else e for e in row["evidence"]],
                            "validation_status": row.get("validation_limit", "dataset_execution_not_validated"),
                        }
                    )
            for category, project, key in (
                ("task_trove_converter_contracts", "task-trove-converter", "converter"),
                ("task_trove_mode_contracts", "task-trove-mode", "mode"),
                ("task_trove_helper_closure", "task-trove-helper", "source_path"),
            ):
                for row in fragment[category]:
                    name = row[key]
                    entities.append(
                        {
                            **row,
                            "source": project,
                            "name": name,
                            "entity_id": project + ":" + name,
                            "status": "implemented_not_validated",
                            "reason_id": "dataset_execution_not_validated",
                            "reason": (
                                "Implemented migration/source contract has focused regression evidence, "
                                "but complete genuine archived task execution is not validated."
                            ),
                            "needed_change": (
                                "Execute genuine task payloads and compare the native converter/mode "
                                "contract; no unsupported category is inferred."
                            ),
                            "primitive_candidates": row.get("modes", [row["mode"]] if "mode" in row else []),
                            "source_revision": "b76d03131cd88bd9fc711dba206659027edba3a8",
                            "source_evidence": [{"path": row["source_path"], "sha256": row["source_sha256"]}],
                            "validation_status": "focused_source_contract_not_full_dataset",
                        }
                    )
            continue
        for row in fragment["entries"]:
            source = row["source"]
            if row["status"].startswith("implemented"):
                row = {
                    **row,
                    "historical_primitive_candidates": row["existing_primitive_candidate"],
                    "existing_primitive_candidate": ["mcq" if row["id"] == "mcq" else "exact"],
                }
            project = "MarinSkyRL"
            entities.append(
                {
                    **{key: value for key, value in row.items() if key not in {"source", "id", "not_covered_reason"}},
                    "source": project,
                    "entity_id": project + ":" + row["id"],
                    "name": row["id"],
                    "source_revision": source["revision"],
                    "source_evidence": [source],
                    "reason": row["not_covered_reason"],
                    "reason_id": row["contract_family"],
                    "primitive_candidates": row["existing_primitive_candidate"],
                    "validation_status": row["validation_gap"],
                }
            )
    counts = Counter((e["source"], e["status"]) for e in entities)
    harness_gaps = [e for e in entities if e["source"] == "lm-eval-harness" and e["status"] == "not_integrated"]
    assert len(harness_gaps) == 1601
    assert sum(e["status"] == "native_route_available" and e["source"] == "lm-eval-harness" for e in entities) == 11091
    ids = [e["entity_id"] for e in entities]
    assert len(ids) == len(set(ids)), "duplicate coverage entities"
    payload = {
        "schema_version": 1,
        "scope": (
            "Pinned source snapshots and subsequent opt-in cutovers; route availability "
            "is separate from runtime validation."
        ),
        "counts": [
            {"source": source, "status": status, "count": count} for (source, status), count in sorted(counts.items())
        ],
        "harness_gap_groups": dict(sorted(Counter(e["reason_id"] for e in harness_gaps).items())),
        "runtime_population": runtime["counts"],
        "runtime_invalid_group_members": runtime["invalid_group_members"],
        "peer_fragments": fragments,
    }
    contracts = {}
    for entity in entities:
        contract = {
            key: entity.pop(key)
            for key in ("reason", "needed_change", "primitive_candidates", "validation_status")
            if key in entity
        }
        identifier = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()[:16]
        contracts[identifier] = contract
        entity["coverage_contract"] = identifier
    payload["coverage_contracts"] = dict(sorted(contracts.items()))
    header = json.dumps(payload, sort_keys=True, separators=(",", ":"))[:-1]
    args.output.write_text(
        header
        + ',\n"entities":[\n'
        + ",\n".join(json.dumps(e, sort_keys=True, separators=(",", ":")) for e in entities)
        + "\n]}\n"
    )
    print(json.dumps(payload["harness_gap_groups"], sort_keys=True))


if __name__ == "__main__":
    main()
