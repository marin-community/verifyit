"""Consolidate pinned source coverage without treating specifications as integrations."""

import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

from eval_inventory import resolve_config

from verifyit.adapters.harness_native import native_config_route
from verifyit.adapters.harness_runtime import corpus_config_profile

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
            or ("/okapi/truthfulqa_multilingual/" in record["path"] and record["path"].endswith("_mc2.yaml"))
            or ("/tasks/hendrycks_math/" in record["path"])
            or ("/tasks/crows_pairs/" in record["path"])
            or ("/tasks/babilong/" in record["path"])
            or ("/tasks/mmmu/" in record["path"])
            or ("/tasks/agieval/" in record["path"] and record.get("output_type") == "multiple_choice")
        ):
            route = record.get("native_route")
            if route is None:
                config, _ = resolve_config(sources / "lm-eval-harness" / record["path"])
                route = native_config_route(config)
                assert route in {
                    "afriqa_f1",
                    "ner_span_f1",
                    "pos_accuracy",
                    "exact_match",
                    "truthfulqa_mc2",
                    "hendrycks_literal_exact",
                    "agieval_mcqa",
                    "crows_pair_preference",
                    "babilong_substring",
                    "mmmu_typed_answers",
                }, record["path"]
            entity.update(
                status="native_route_available",
                kind="task",
                reason_id=route,
                reason=(
                    (
                        "Pinned MC2 source contract grades raw likelihoods and correctness labels "
                        "using stable probability mass "
                        "and exact index membership; fixture validation only."
                    )
                    if route == "truthfulqa_mc2"
                    else (
                        (
                            "Source extraction and pinned string normalization feed strict literal exact grading; "
                            "Malformed/nonfinite references abort and known normalization errors "
                            "never fall back to raw equality."
                        )
                        if route == "hendrycks_literal_exact"
                        else (
                            "Resolved configuration matches an implemented guarded default scorer route; "
                            "this is eligibility, not full dataset execution."
                        )
                    )
                ),
                primitive_candidates=(
                    ["exact"]
                    if route in {"truthfulqa_mc2", "hendrycks_literal_exact"}
                    else [record["existing_mode"]] if record["existing_mode"] != "script" else ["exact", "script"]
                ),
                needed_change="No known scorer change; validate task datasets/runtime before deployment.",
                validation_status=(
                    "real_trace"
                    if record["task"] in {"piqa", "winogrande", "boolq"}
                    else "configuration_eligible_not_dataset_validated"
                ),
            )
            if route == "mmmu_typed_answers":
                entity.update(
                    primitive_candidates=["exact", "mcq", "numeric"],
                    reason=(
                        "Pinned source multimodal prompt/image and answer extraction feed strict choice, "
                        "typed two-decimal numeric equality and literal substring primitives. "
                        "Unparsed choices score zero rather than source random guessing; empty or nonfinite "
                        "references abort the batch, and nonfinite candidates score zero."
                    ),
                    evidence=[
                        "integrations/lm-eval-harness/mmmu-typed-verifyit.patch",
                        "evidence/e2e/wiring/harness-mmmu/guards/guard-audit.json",
                        "evidence/e2e/wiring/harness-mmmu/cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-mmmu/source-failures/source-failures.json",
                        "evidence/e2e/wiring/harness-mmmu/manager-cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-mmmu/trace-census.json",
                    ],
                    validation_status="registered_guards_and_actual_multimodal_evaluator_fixtures_no_saved_trace",
                )
            if route == "babilong_substring":
                entity.update(
                    primitive_candidates=["exact"],
                    reason=(
                        "Pinned source response preprocessing runs exactly once; target strip/lower and "
                        "response lower feed explicit single-reference ExactSpec substring containment. "
                        "Internal whitespace and source lower semantics remain. Empty/malformed targets "
                        "abort; the original empty target scored one by vacuous containment."
                    ),
                    evidence=[
                        "integrations/lm-eval-harness/babilong-substring-verifyit.patch",
                        "evidence/e2e/wiring/harness-babilong/guards/guard-audit.json",
                        "evidence/e2e/wiring/harness-babilong/cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-babilong/source-empty/source-empty-reference.json",
                        "evidence/e2e/wiring/harness-babilong/manager-cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-babilong/trace-census.json",
                    ],
                    validation_status="registered_guards_and_actual_evaluator_fixtures_no_named_saved_trace",
                )
            if route == "crows_pair_preference":
                entity.update(
                    primitive_candidates=["mcq"],
                    reason=(
                        "Reversed raw likelihood choice preserves strict stereotype preference and ties; "
                        "verifyit computes the unbounded likelihood difference and original arithmetic means. "
                        "These are source bias/preference metrics, not universal correctness rewards. "
                        "Malformed samples and nonfinite means/stderr abort instead of exporting partial metrics."
                    ),
                    evidence=[
                        "integrations/lm-eval-harness/crows-pairs-verifyit.patch",
                        "evidence/e2e/wiring/harness-crows/guards/guard-audit.json",
                        "evidence/e2e/wiring/harness-crows/bootstrap-cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-crows/negative/boundary-guards.json",
                        "evidence/e2e/wiring/harness-crows/manager-bootstrap-cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-crows/trace-census.json",
                    ],
                    validation_status="registered_guards_and_actual_evaluator_fixtures_no_named_saved_trace",
                )
            if route == "agieval_mcqa":
                entity.update(
                    primitive_candidates=["mcq", "exact"],
                    reason=(
                        "Raw and character-normalized first-maximum likelihood winners are graded "
                        "against alternative gold indices through existing choice/exact primitives. "
                        "Both source acc/acc_norm means remain; malformed evidence aborts the batch."
                    ),
                    evidence=[
                        "integrations/lm-eval-harness/agieval-mcqa-verifyit.patch",
                        "evidence/e2e/wiring/harness-agieval/guards/guard-audit.json",
                        "evidence/e2e/wiring/harness-agieval/cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-agieval/negative/boundary-guards.json",
                        "evidence/e2e/wiring/harness-agieval/manager-cutover/evaluator-roundtrip.json",
                        "evidence/e2e/wiring/harness-agieval/trace-census.json",
                    ],
                    validation_status="registered_guards_and_actual_evaluator_fixtures_no_named_saved_trace",
                )
            if route == "hendrycks_literal_exact":
                entity.update(
                    evidence=[
                        "integrations/lm-eval-harness/hendrycks-exact-verifyit.patch",
                        "evidence/e2e/wiring/evalchemy-amc-math/guards/guard-audit.json",
                        "evidence/e2e/wiring/evalchemy-amc-math/math500-comparison.json",
                    ],
                    validation_status=(
                        "real_saved_responses_fresh_source_parity_different_producer_comparator"
                        if record["task"] == "hendrycks_math500"
                        else "registered_configuration_guard_and_source_evaluator_fixtures"
                    ),
                )
        else:
            config, _ = resolve_config(sources / "lm-eval-harness" / record["path"])
            runtime_profile = corpus_config_profile(config)
            if runtime_profile in {
                "translation_corpus",
                "rolling_likelihood_corpus",
                "likelihood_corpus",
                "code_text_smoothed_bleu",
                "xlsum_rouge_corpus",
            }:
                entity.update(
                    status="retained_runtime_available",
                    kind="task",
                    reason_id=runtime_profile,
                    reason=(
                        "A guarded single-rank ScriptSpec batch executes source process_results and "
                        "registered corpus aggregators, returning every raw observation and named point metric. "
                        "This retains source scoring and is not a native correctness projection."
                    ),
                    primitive_candidates=["script"],
                    needed_change=(
                        "Apply corpus-runtime-verifyit.patch and opt in via TaskManager metadata "
                        "verifyit_corpus_runtime=true; validate actual dataset records before deployment. "
                        "Distributed evaluation and unsupported grading overrides remain outside this profile."
                    ),
                    validation_status="source_and_evaluator_fixtures_not_saved_trace_validated",
                    runtime_profile=runtime_profile,
                    metric_profile=config.get("metric_list"),
                    output_type=config.get("output_type"),
                    limitations=[
                        "single_rank_only",
                        "default_ConfigurableTask_only",
                        "finite_JSON_only",
                        "fixture_only",
                    ],
                    evidence=[
                        "integrations/lm-eval-harness/corpus-runtime-verifyit.patch",
                        "evidence/e2e/wiring/harness-runtime/evaluator-roundtrip.json",
                    ],
                )
                entities.append(entity)
                continue
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
        if record["classification"] == "adapter" or name in {"JEEBench", "AMC23", "NUPA-Loose", "NUPA5K-Loose"}:
            entity.update(
                status="native_integrated",
                reason_id="custom_native",
                reason="Concrete source client patch calls an existing primitive after source extraction/normalization.",
                primitive_candidates=(
                    ["exact", "numeric"]
                    if name == "JEEBench"
                    else (
                        ["exact"]
                        if name == "AMC23"
                        else ["numeric" if name == "GSM8KPerturbed" else record["primitive_candidate"]]
                    )
                ),
                needed_change="No known scorer change.",
                validation_status=(
                    "real_trace" if name in {"MMLUPro", "GPQADiamond"} else "source_parity_no_tracker_trace"
                ),
            )
            if name == "JEEBench":
                entity.update(
                    reason=(
                        "Opt-in type dispatch composes strict exact option-set equality/subset credit "
                        "and numeric absolute tolerance .01; source extraction and repetition metrics remain. "
                        "Malformed references and unsupported uppercase labels fail closed."
                    ),
                    needed_change=(
                        "Enable verifyit_enabled=True through JEEBenchBenchmark or TaskManager "
                        "benchmark kwargs; validate saved runs when available."
                    ),
                    evidence=[
                        "integrations/evalchemy/jee-verifyit.patch",
                        "evidence/e2e/wiring/evalchemy-jee/source-roundtrip.json",
                    ],
                    validation_status="source_evaluator_fixtures_no_tracker_trace",
                )
            if name in {"NUPA-Loose", "NUPA5K-Loose"}:
                entity.update(
                    primitive_candidates=["exact"],
                    reason=(
                        "Source extraction prepares full digit-component tuples and aligned digits; "
                        "strict exact grading inside verifyit computes exact_match and digit_match. "
                        "All five metrics and source task/length/cross-bucket denominators remain. "
                        "Malformed reference representations abort mixed batches. Source preparation "
                        "omits signs, including scientific exponent signs: these are component metrics, "
                        "not mathematical numeric equivalence."
                    ),
                    needed_change=(
                        "Enable verifyit_enabled=True on the benchmark constructor. "
                        + (
                            "Three frozen saved model runs replay all 15,000 records with exact metric parity."
                            if name == "NUPA5K-Loose"
                            else "Shared scorer has source evaluator fixtures; no separate NUPA-Loose archive replay."
                        )
                    ),
                    evidence=[
                        "integrations/evalchemy/nupa-exact-verifyit.patch",
                        "evidence/e2e/wiring/evalchemy-nupa/final-cutover/source-roundtrip.json",
                        "evidence/e2e/wiring/evalchemy-nupa/source-reference/source-reference-positive.json",
                        "evidence/e2e/wiring/evalchemy-nupa/selection.json",
                        "evidence/e2e/wiring/evalchemy-nupa/implementation-provenance.json",
                    ],
                    validation_status=(
                        "three_full_saved_runs_15000_records_all_named_and_bucket_metrics_match"
                        if name == "NUPA5K-Loose"
                        else "source_evaluator_fixtures_shared_scorer_no_separate_archive"
                    ),
                )
                if name == "NUPA5K-Loose":
                    entity["evidence"].extend(
                        f"evidence/e2e/wiring/evalchemy-nupa/replay-{index}/replay.json" for index in range(3)
                    )
            if name == "AMC23":
                entity.update(
                    reason=(
                        "Pinned source normalization feeds strict exact equality; ten source repetitions "
                        "and boxed extraction remain. Known normalization failures no longer fall back "
                        "to raw equality."
                    ),
                    needed_change=(
                        "Enable verifyit_enabled=True through AMC23Benchmark or TaskManager; "
                        "no matching AMC23 archived inputs were found."
                    ),
                    evidence=[
                        "integrations/evalchemy/amc23-verifyit.patch",
                        "evidence/e2e/wiring/evalchemy-amc-math/guarded-amc/amc-roundtrip.json",
                    ],
                    validation_status="source_evaluator_fixtures_no_matching_archive",
                )
        elif name in {"HumanEval", "MBPP"}:
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_isolated_code_runtime",
                reason=(
                    "ScriptSpec retains source Python assertions and HumanEval shell tests in a trusted "
                    "supervisor while candidate functions run in isolated containers. Source pass@k "
                    "and MBPP sample annotations remain. Mixed completions match the untouched source "
                    "scorer in the same pinned Linux runtime; MBPP180/493 differ on macOS."
                ),
                primitive_candidates=["script"],
                needed_change=(
                    "Enable verifyit_enabled=True and load the pinned local candidate image. "
                    "Source fixtures are validated; archived model replay is not claimed."
                ),
                validation_status="source_custom_evaluator_fixtures_pinned_linux_no_archived_replay",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/custom-code-verifyit.patch",
                    "integrations/evalchemy/custom-code-source.json",
                    "integrations/lm-eval-harness/function-rpc-values-verifyit.patch",
                    "../evidence/e2e/wiring/evalchemy-code-family/comparison.json",
                    "../evidence/e2e/wiring/evalchemy-code-family/manager-humaneval/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-code-family/manager-mbpp/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-code-family/manager-supplemental/results.json",
                ],
            )
        elif name in {"HumanEvalPlus", "MBPPPlus"}:
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_isolated_plus_runtime",
                reason=(
                    "ScriptSpec retains source extended Python assertions, pass@k, scored_count and "
                    "sample annotations with isolated candidate calls. Plus uses bounded 16MiB frames "
                    "for measured source values; original code routes retain 1MiB. Three MBPPPlus "
                    "missing-assert profiles now reject wrong candidates that source scored one."
                ),
                primitive_candidates=["script"],
                needed_change=(
                    "Enable verifyit_enabled=True with the pinned candidate image. Frozen fixtures "
                    "use source default timeouts; four larger source fixtures use 30 seconds on both "
                    "routes. Archived replay is unclaimed; source runtime/platform defects remain documented."
                ),
                validation_status="source_custom_evaluator_fixtures_with_explicit_source_corrections_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/custom-plus-verifyit.patch",
                    "integrations/evalchemy/custom-plus-source.json",
                    "integrations/lm-eval-harness/function-rpc-plus-verifyit.patch",
                    "../evidence/e2e/wiring/evalchemy-plus/comparison.json",
                    "../evidence/e2e/wiring/evalchemy-plus/manager-humanevalplus/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-plus/manager-mbppplus/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-plus/manager-final-frame-humanevalplus/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-plus/manager-final-frame-mbppplus/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-plus/manager-presence/roundtrip.json",
                ],
            )
        elif name in {"SimpleQA", "SimpleQAMini", "OlympiadBench", "OlympiadBenchDeterministic", "OlympiadBenchFull"}:
            entity.update(
                status="native_fallback" if name == "OlympiadBenchDeterministic" else "retained_runtime_available",
                reason_id="custom_source_judge_protocol",
                reason=(
                    "Opt-in client preserves source prompts, SDK requests, token-budget retries, "
                    "label parsing, repetitions and pass@k. ScriptSpec executes judge transport and "
                    "ExactSpec grades labels; Olympiad math uses MathSpec with source Minerva fallback. "
                    "Deterministic Olympiad uses only the math route. Malformed judge responses abort "
                    "the whole batch with zero verifier reward instead of returning partial metrics."
                ),
                primitive_candidates=["math"] if name == "OlympiadBenchDeterministic" else ["script", "exact", "math"],
                needed_change=(
                    "Enable verifyit_enabled=True. Eight actual evaluator fixture scenarios match source; "
                    "three of thirteen OlympiadBench archived links are frozen but unavailable without "
                    "CoreWeave credentials. No archived replay or live judge scoring is claimed."
                ),
                validation_status="source_custom_evaluator_http_fixtures_no_archived_replay",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/shared-judges-verifyit.patch",
                    "integrations/evalchemy/shared-judges-source.json",
                    "../evidence/e2e/wiring/evalchemy-shared-judges/manager/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-shared-judges/manager-negative/negative.json",
                    "../evidence/e2e/wiring/evalchemy-shared-judges/archive-census.json",
                ],
            )
        elif name in {"IFEval", "IFBench"}:
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_source_instruction_predicates",
                reason=(
                    "Trusted source predicates register in existing IFEval mode under ScriptSpec; "
                    "native no-comma is reused. Original strict/loose variants, descriptor defaults, "
                    "per-prompt/instruction/type aggregates and source Python RNG behavior remain. "
                    "Language detector failures now score zero with explicit seed0 reproducibility; "
                    "malformed or vacuous descriptors and inconsistent child results abort batches."
                ),
                primitive_candidates=["ifeval", "script"],
                needed_change=(
                    "Enable verifyit_enabled=True. IFEval540 saved source responses match source "
                    "scores, not an archived validated score; one unmatched source prompt is recorded. "
                    "IFBench300 source metadata rows use synthetic responses. Three archived IFBench "
                    "links are frozen but credentials unavailable. IFEval's unrelated run_benchmark "
                    "typo remains; evaluate_responses is the tested boundary."
                ),
                validation_status=(
                    "real_response_source_parity_not_archived_score"
                    if name == "IFEval"
                    else "source_custom_evaluator_fixtures_no_archives"
                ),
                blockers=[],
                evidence=[
                    "integrations/evalchemy/instructions-verifyit.patch",
                    "integrations/evalchemy/instructions-source.json",
                    "../evidence/e2e/wiring/evalchemy-instructions/manager-final-ifeval/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-instructions/manager-final-ifbench/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-instructions/manager-negative-final/negative.json",
                    "../evidence/e2e/wiring/evalchemy-instructions/archive-census.json",
                ],
            )
        elif name in {"LiveCodeBench", "LiveCodeBenchv5", "LiveCodeBenchv5_official", "CodeElo", "CodeForces"}:
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_competitive_code_runtime",
                reason=(
                    "ScriptSpec supervises isolated candidate function/stdin execution and trusted "
                    "source comparison. Three LCB clients preserve argument/state and numeric/list "
                    "coercion; legacy CodeElo/CodeForces retain stdin reference cleanup and exact "
                    "equality. All difficulty and repetition aggregates remain in the original client."
                ),
                primitive_candidates=["script"],
                needed_change=(
                    "Enable verifyit_enabled=True and apply the pinned candidate/RPC exports. "
                    "Sixty-six fixture completion evaluations cover all five actual evaluators. "
                    "LCB retains 1 GiB AS/DATA/STACK bounds; legacy uncapped profiles inherit the "
                    "execution environment limit. Truncating integer-list coercion no longer "
                    "awards false credit. Baselines use the macOS source runtime; no archive "
                    "replay or broader platform/library equivalence is claimed."
                ),
                validation_status="source_custom_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/competitive-code-verifyit.patch",
                    "integrations/evalchemy/competitive-code-source.json",
                    "integrations/lm-eval-harness/function-rpc-memory-verifyit.patch",
                    "../evidence/e2e/wiring/evalchemy-competitive-code/manager-final/results.json",
                    "../evidence/e2e/wiring/evalchemy-competitive-code/cutover-resource-final/results.json",
                    "../evidence/e2e/wiring/evalchemy-competitive-code/negative-resource-final/results.json",
                    "../evidence/e2e/wiring/evalchemy-competitive-code/archive-census.json",
                ],
            )
        elif name in {"FinanceBench", "HLE"}:
            family = "financebench" if name == "FinanceBench" else "hle"
            entity.update(
                status="retained_runtime_available",
                reason_id=f"custom_{family}_judge_runtime",
                reason=(
                    "Source SDK requests and structured judge parsing run through ScriptSpec with "
                    "actual ExactSpec verdicts. HLE also uses exact grading for its default scoring "
                    "method, preserving literal whitespace and repeated metrics. Malformed trusted "
                    "references and incomplete judge batches abort without partial metrics."
                ),
                primitive_candidates=["exact", "script"],
                needed_change=(
                    "Enable verifyit_enabled=True and apply the exported source-specific client. "
                    "Actual evaluator fixtures preserve complete results and HTTP request bodies. "
                    "HLE's separate calibration CLI is excluded. FinanceBench has 14 tracker links, "
                    "with three frozen selections unavailable because archive credentials are absent; "
                    "no archived score replay is claimed for either benchmark."
                ),
                validation_status="source_custom_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    f"integrations/evalchemy/{family}-verifyit.patch",
                    f"integrations/evalchemy/{family}-source.json",
                    f"../evidence/e2e/wiring/evalchemy-{family}/manager/"
                    + ("roundtrip.json" if family == "financebench" else "results.json"),
                    f"../evidence/e2e/wiring/evalchemy-{family}/negative/"
                    + ("negative.json" if family == "financebench" else "results.json"),
                    f"../evidence/e2e/wiring/evalchemy-{family}/archive-census.json",
                ],
            )
        elif name == "CruxEval":
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_cruxeval_expression_runtime",
                reason=(
                    "ScriptSpec compares trusted Python literal references with isolated candidate "
                    "expression results using bounded typed RPC. Both input/output directions retain "
                    "source extraction, pass@1/pass@5 and per-task pass rates."
                ),
                primitive_candidates=["script"],
                needed_change=(
                    "Enable verifyit_enabled=True and load the pinned candidate image plus RPC "
                    "prerequisites. Ninety fixture evaluations cover nine frozen source tasks and "
                    "five mixed completions in both directions. Source nested-input regex truncation "
                    "remains unchanged. Malformed/missing batches abort, and missing command runtime "
                    "does not return partial metrics. Three of 14 archive links are frozen but "
                    "credentials are unavailable; no archived score replay is claimed."
                ),
                validation_status="source_custom_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/cruxeval-verifyit.patch",
                    "integrations/evalchemy/cruxeval-source.json",
                    "integrations/lm-eval-harness/function-rpc-bytes-verifyit.patch",
                    "../evidence/e2e/wiring/evalchemy-cruxeval/manager/results.json",
                    "../evidence/e2e/wiring/evalchemy-cruxeval/cutover-final/results.json",
                    "../evidence/e2e/wiring/evalchemy-cruxeval/negative/results.json",
                    "../evidence/e2e/wiring/evalchemy-cruxeval/archive-census.json",
                ],
            )
        elif name == "RepoBench":
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_repobench_similarity_runtime",
                reason=(
                    "ExactSpec grades source whitespace-token equality and ScriptSpec retains "
                    "fuzzywuzzy edit similarity. The client preserves source double rounding and "
                    "global weighted averages repeated under each language label."
                ),
                primitive_candidates=["exact", "script"],
                needed_change=(
                    "Enable verifyit_enabled=True and append the source RepoBench directory to "
                    "module lookup for its absolute imports. All six default language/subset cells "
                    "match source evaluator fixtures with 18 samples. Invalid or missing cells abort "
                    "the whole batch and clean temporary files. Evidence uses fuzzywuzzy 0.18.0 with "
                    "pure-Python difflib; cross-backend parity and archived replay are unclaimed. "
                    "The source evaluator does not call its imported CodeBLEU metric."
                ),
                validation_status="source_custom_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/repobench-verifyit.patch",
                    "integrations/evalchemy/repobench-source.json",
                    "../evidence/e2e/wiring/evalchemy-repobench/manager/results.json",
                    "../evidence/e2e/wiring/evalchemy-repobench/cutover-final/results.json",
                    "../evidence/e2e/wiring/evalchemy-repobench/negative/results.json",
                    "../evidence/e2e/wiring/evalchemy-repobench/archive-census.json",
                ],
            )
        elif name == "MixEval":
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_mixeval_parser_runtime",
                reason=(
                    "ScriptSpec retains source parser requests and weighted aggregates; ExactSpec "
                    "grades extracted labels and normalized substrings, and NumericSpec grades "
                    "source-rounded finite numbers. Missing interpretations receive minimum scores."
                ),
                primitive_candidates=["exact", "numeric", "script"],
                needed_change=(
                    "Enable verifyit_enabled=True. All eight default/hard parser profiles have "
                    "fixture evaluator evidence with 48 samples and 24 matching HTTP requests. "
                    "Source rule-MC aggregation lacks count metadata; the opt-in correction matches "
                    "an independent count/aggregate oracle. Blank responses and stale positive caches "
                    "cannot preserve credit; malformed judge batches abort. PYTHONHASHSEED=0 pins "
                    "source observation ordering. The unexposed base-model extraction flag is "
                    "unsupported. Existing cache files are neither trusted nor replaced. No archive replay."
                ),
                validation_status="source_custom_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/mixeval-verifyit.patch",
                    "integrations/evalchemy/mixeval-source.json",
                    "../evidence/e2e/wiring/evalchemy-mixeval/manager-final-hard/results.json",
                    "../evidence/e2e/wiring/evalchemy-mixeval/default-parallel/results.json",
                    "../evidence/e2e/wiring/evalchemy-mixeval/contract-census.json",
                    "../evidence/e2e/wiring/evalchemy-mixeval/source-count-defect.json",
                    "../evidence/e2e/wiring/evalchemy-mixeval/archive-census.json",
                ],
            )
        elif name == "WildBench":
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_wildbench_score_judge_runtime",
                reason=(
                    "ScriptSpec preserves score-mode source SDK requests and category aggregates; "
                    "JSONSchema validates finite judgments from 1 to 10. Structured original-response "
                    "blankness forces the source minimum 1, corresponding to verifyit reward 0."
                ),
                primitive_candidates=["script"],
                needed_change=(
                    "Enable verifyit_enabled=True. Six evaluator fixtures preserve source HTTP "
                    "bodies and metrics, including quoted prompt delimiters and fractional scores. "
                    "Eight malformed judge batches abort without partial metrics. Source default "
                    "configuration lacks max_tokens; both replay routes explicitly use its final "
                    "4096-token budget. Pairwise mode remains unsupported: the source evaluator "
                    "constructs None references and fails before judging. No archive replay claimed."
                ),
                validation_status="source_score_mode_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/wildbench-verifyit.patch",
                    "integrations/evalchemy/wildbench-source.json",
                    "../evidence/e2e/wiring/evalchemy-wildbench/manager/results.json",
                    "../evidence/e2e/wiring/evalchemy-wildbench/quoted-cutover/results.json",
                    "../evidence/e2e/wiring/evalchemy-wildbench/empty-structured/results.json",
                    "../evidence/e2e/wiring/evalchemy-wildbench/source-defects.json",
                    "../evidence/e2e/wiring/evalchemy-wildbench/archive-census.json",
                ],
            )
        elif name == "HMMT":
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_matharena_runtime",
                reason=(
                    "ScriptSpec runs pinned MathArena extraction in a candidate-only container, "
                    "then bounded explicit symbolic reconstruction and untouched source comparison "
                    "inside the supervised deadline. Trusted references stay outside that container. "
                    "Source unordered-list multiplicity, numeric tolerance and repeated metrics remain."
                ),
                primitive_candidates=["script"],
                needed_change=(
                    "Enable verifyit_enabled=True and load the pinned image/prerequisite RPC patches. "
                    "Three frozen questions use ten source repetitions through generation and evaluation; "
                    "78 supplemental comparisons cover all 30 gold canonical/wrong responses and 18 "
                    "alternative forms. Fixture-only: no archived score replay. Returned model_answers "
                    "are JSON primitives/display strings, not original symbolic objects. Unsupported "
                    "expressions score zero; bounded explicit nodes do not claim arbitrary SymPy equivalence."
                ),
                validation_status="source_generation_and_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/hmmt-verifyit.patch",
                    "integrations/evalchemy/hmmt-source.json",
                    "../evidence/e2e/wiring/evalchemy-hmmt/manager-final/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-hmmt/supplemental/results.json",
                    "../evidence/e2e/wiring/evalchemy-hmmt/negative/results.json",
                    "../evidence/e2e/wiring/evalchemy-hmmt/archive-census.json",
                ],
            )
        elif name == "MRCR":
            entity.update(
                status="retained_runtime_available",
                reason_id="custom_nonce_similarity_runtime",
                reason=(
                    "ExactSpec compares actual candidate prefix text with the nonce; ScriptSpec "
                    "retains source fractional SequenceMatcher similarity. Both generation scoring "
                    "and evaluate_responses call verifyit; evaluation recomputes raw output instead "
                    "of trusting stale or missing score fields. Source bin/needle aggregates remain."
                ),
                primitive_candidates=["exact", "script"],
                needed_change=(
                    "Enable verifyit_enabled=True. Seventy-four fixture samples cover all24 published "
                    "bin/needle cells and source unprefixed-reference behavior. Dataset selection "
                    "and model outputs are fixtures; no live inference or archive replay is claimed. "
                    "Three of fourteen tracker links are frozen but CoreWeave credentials unavailable."
                ),
                validation_status="source_generation_and_evaluator_fixtures_no_archives",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/mrcr-verifyit.patch",
                    "integrations/evalchemy/mrcr-source.json",
                    "../evidence/e2e/wiring/evalchemy-mrcr/manager/roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-mrcr/manager-negative/negative.json",
                    "../evidence/e2e/wiring/evalchemy-mrcr/archive-census.json",
                ],
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
    uncheatable_manifest = json.loads((root / "integrations/evalchemy/uncheatable-source.json").read_text())
    uncheatable_tasks = {
        f"uncheatable_eval_{Path(name).stem}"
        for name in uncheatable_manifest["files"]
        if name.endswith(".yaml") and not name.startswith("_")
    }
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
        elif name == "truthfulqa_mc2":
            entity.update(
                status="native_integrated",
                reason_id="override_probability_mass",
                reason=(
                    "Raw likelihoods and binary correctness labels are graded by stable probability mass "
                    "plus strict exact index membership."
                ),
                primitive_candidates=["exact"],
                needed_change=(
                    "No known scorer change; three selected saved links await S3 access " "and full archived replay."
                ),
                validation_status="source_evaluator_fixtures_not_archived_replay",
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
        elif name in uncheatable_tasks:
            entity.update(
                status="retained_runtime_available",
                reason_id="override_uncheatable_runtime",
                reason=(
                    "Installed source-pinned category callbacks and rolling likelihood observations "
                    "execute through ScriptSpec; source token/byte denominators and all three "
                    "corpus aggregates are retained. Single-rank execution only."
                ),
                primitive_candidates=["script"],
                needed_change="Validate archived rolling-likelihood runs when matching artifacts become available.",
                validation_status="source_evaluator_fixtures_only",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/uncheatable-runtime-verifyit.patch",
                    "integrations/evalchemy/install_uncheatable.py",
                    "../evidence/e2e/wiring/evalchemy-uncheatable/roundtrip/evaluator-roundtrip.json",
                    "../evidence/e2e/wiring/evalchemy-uncheatable/negative/negative-batches.json",
                    "../evidence/e2e/wiring/evalchemy-uncheatable/trace-census.json",
                ],
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
                    "existing_primitive_candidate": row.get(
                        "implemented_primitive_modes", ["mcq" if row["id"] == "mcq" else "exact"]
                    ),
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
    for entity in entities:
        if entity["entity_id"] in {
            "lm-eval-harness:lm_eval/tasks/drop/default.yaml",
            "evalchemy-override:eval/lm_eval_tasks/drop/drop.yaml",
        }:
            entity.update(
                status="retained_runtime_available",
                reason_id="drop_source_runtime",
                reason=(
                    "Pinned DROP multi-span EM/F1 executes through ScriptSpec; "
                    "source filters and numeric gating remain."
                ),
                primitive_candidates=["script"],
                needed_change="Enable verifyit_drop_runtime metadata; replay archived inputs when available.",
                validation_status="source_evaluator_fixtures_no_matching_archive",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/drop-runtime-verifyit.patch",
                    "../evidence/e2e/wiring/harness-drop/roundtrip-positive/roundtrip.json",
                    "../evidence/e2e/wiring/harness-drop/negative/negative-batches.json",
                    "../evidence/e2e/wiring/harness-drop/trace-census.json",
                ],
            )
    for entity in entities:
        if entity["entity_id"] in {
            "lm-eval-harness:lm_eval/tasks/humaneval/humaneval.yaml",
            "evalchemy-override:eval/lm_eval_tasks/humaneval/humaneval.yaml",
        }:
            entity.update(
                status="retained_runtime_available",
                reason_id="humaneval_function_runtime",
                reason=(
                    "ScriptSpec executes source HumanEval assertions against a persistent isolated function worker; "
                    "source completion construction and pass@1 metrics remain."
                ),
                primitive_candidates=["script"],
                needed_change="Enable verifyit_humaneval_runtime metadata with the pinned Docker image; pass@1 only.",
                validation_status="source_evaluator_fixtures_no_archived_replay",
                blockers=[],
                evidence=[
                    "integrations/evalchemy/humaneval-function-verifyit.patch",
                    "../evidence/e2e/wiring/harness-humaneval/roundtrip-final/roundtrip.json",
                    "../evidence/e2e/wiring/harness-humaneval/implementation-provenance.json",
                    "../evidence/e2e/wiring/harness-humaneval/trace-census.json",
                ],
            )
    bbq_manifest = json.loads((root / "integrations/lm-eval-harness/bbq-source.json").read_text())
    bbq_ids = {f"lm-eval-harness:{task['path']}" for task in bbq_manifest["tasks"]}
    for entity in entities:
        if entity["entity_id"] in bbq_ids:
            entity.update(
                status="native_route_available",
                reason_id="bbq_mcq_correctness",
                reason=(
                    "Existing MCQ grades the first maximum likelihood choice with all unknown alternatives "
                    "mapped to label 2. Source bias observation tuples and signed corpus aggregates remain client-owned."
                ),
                primitive_candidates=["mcq"],
                needed_change="Enable verifyit_bbq metadata; archived replay remains unvalidated.",
                validation_status="all_twenty_source_evaluator_fixtures_no_archived_replay",
                blockers=[],
                evidence=[
                    "integrations/lm-eval-harness/bbq-mcq-verifyit.patch",
                    "integrations/lm-eval-harness/bbq-source.json",
                    "../evidence/e2e/wiring/harness-bbq/roundtrip-final/roundtrip.json",
                    "../evidence/e2e/wiring/harness-bbq/negative/negative-batches.json",
                    "../evidence/e2e/wiring/harness-bbq/trace-census.json",
                ],
            )
    libra_manifest = json.loads((root / "integrations/lm-eval-harness/libra-source.json").read_text())
    libra_ids = {f"lm-eval-harness:{task['path']}" for task in libra_manifest["tasks"]}
    for entity in entities:
        if entity["entity_id"] in libra_ids:
            entity.update(
                status="native_route_available",
                reason_id="libra_exact_token_composition",
                reason=(
                    "Source morphology and length grouping feed existing exact substring, character-token F1 "
                    "and exact numeric-token comparison. First-positive set iteration remains hash-seed sensitive."
                ),
                primitive_candidates=["exact"],
                needed_change="Enable verifyit_libra with pinned morphology packages; archived replay unvalidated.",
                validation_status="all_eighteen_source_evaluator_fixtures_no_archived_replay",
                blockers=[],
                evidence=[
                    "integrations/lm-eval-harness/libra-primitives-verifyit.patch",
                    "integrations/lm-eval-harness/libra-source.json",
                    "../evidence/e2e/wiring/harness-libra/roundtrip-final/roundtrip.json",
                    "../evidence/e2e/wiring/harness-libra/negative/negative-batches.json",
                    "../evidence/e2e/wiring/harness-libra/hash-seed-parity.json",
                    "../evidence/e2e/wiring/harness-libra/trace-census.json",
                ],
            )
    mlqa_manifest = json.loads((root / "integrations/lm-eval-harness/mlqa-source.json").read_text())
    mlqa_ids = {f"lm-eval-harness:{task['path']}" for task in mlqa_manifest["tasks"]}
    for entity in entities:
        if entity["entity_id"] in mlqa_ids:
            entity.update(
                status="native_route_available",
                reason_id="mlqa_exact_token_composition",
                reason="Pinned source language normalization feeds existing strict exact and token-F1 grading.",
                primitive_candidates=["exact"],
                needed_change="Enable verifyit_mlqa metadata; archived replay remains unvalidated.",
                validation_status="all_forty_nine_source_evaluator_fixtures_no_archived_replay",
                blockers=[],
                evidence=[
                    "integrations/lm-eval-harness/mlqa-primitives-verifyit.patch",
                    "integrations/lm-eval-harness/mlqa-source.json",
                    "../evidence/e2e/wiring/harness-mlqa/roundtrip-final/roundtrip.json",
                    "../evidence/e2e/wiring/harness-mlqa/negative/negative-batches.json",
                    "../evidence/e2e/wiring/harness-mlqa/trace-census.json",
                ],
            )
    longbench_manifest = json.loads((root / "integrations/lm-eval-harness/longbench-source.json").read_text())
    longbench_routes = {f"lm-eval-harness:{task['path']}": task["route"] for task in longbench_manifest["tasks"]}
    for entity in entities:
        if entity["entity_id"] in longbench_routes:
            entity.update(
                status=longbench_routes[entity["entity_id"]],
                reason_id="longbench_composed_or_retained",
                reason="Source preparation feeds exact/token-F1 composition or pinned ScriptSpec ROUGE/code similarity.",
                primitive_candidates=["exact", "script"],
                needed_change="Enable verifyit_longbench with pinned dependencies; archived replay unvalidated.",
                validation_status="all_thirty_four_source_evaluator_fixtures_no_archived_replay",
                blockers=[],
                evidence=[
                    "integrations/lm-eval-harness/longbench-primitives-verifyit.patch",
                    "integrations/lm-eval-harness/longbench-source.json",
                    "../evidence/e2e/wiring/harness-longbench/roundtrip-final/roundtrip.json",
                    "../evidence/e2e/wiring/harness-longbench/manager-roundtrip/roundtrip.json",
                    "../evidence/e2e/wiring/harness-longbench/manager-negative/negative-batches.json",
                    "../evidence/e2e/wiring/harness-longbench/trace-census.json",
                ],
            )
    counts = Counter((e["source"], e["status"]) for e in entities)
    harness_gaps = [e for e in entities if e["source"] == "lm-eval-harness" and e["status"] == "not_integrated"]
    assert len(harness_gaps) == 370
    assert sum(e["status"] == "retained_runtime_available" and e["source"] == "lm-eval-harness" for e in entities) == 993
    assert sum(e["status"] == "native_route_available" and e["source"] == "lm-eval-harness" for e in entities) == 11329
    ids = [e["entity_id"] for e in entities]
    assert len(ids) == len(set(ids)), "duplicate coverage entities"
    tested_ledger = json.loads((root / "docs/unification/evals-tested-configs.json").read_text())
    tested_records = tested_ledger["records"]
    tested_ids = [record["entity_id"] for record in tested_records]
    assert len(tested_ids) == len(set(tested_ids)), "duplicate tested configurations"
    assert set(tested_ids) <= set(ids), "tested configuration missing from source census"
    tested_summary = {}
    for source in ("lm-eval-harness", "evalchemy-custom", "evalchemy-override"):
        source_entities = [e for e in entities if e["source"] == source and e["status"] != "orchestration"]
        selected = [r for r in tested_records if r["source"] == source]
        kinds = {
            kind: {r["entity_id"] for r in selected if any(e["kind"] == kind for e in r["evidence"])}
            for kind in ("fixture", "archive_score_parity", "real_response_source_parity_not_archive_score")
        }
        tested_summary[source] = {
            "total": len(source_entities),
            "e2e_tested": len(selected),
            "route_available": sum(
                e["status"]
                in ("native_route_available", "retained_runtime_available", "native_integrated", "native_fallback")
                for e in source_entities
            ),
            "archive_score_parity": len(kinds["archive_score_parity"]),
            "fixture_only": len(
                kinds["fixture"] - kinds["archive_score_parity"] - kinds["real_response_source_parity_not_archive_score"]
            ),
            "real_response_source_parity_not_archive_score": len(kinds["real_response_source_parity_not_archive_score"]),
        }
    payload = {
        "schema_version": 1,
        "tested_e2e": {
            "as_of": tested_ledger["as_of"],
            "summary": tested_summary,
            "ledger": "evals-tested-configs.json",
        },
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
