"""Inventory pinned Evalchemy and harness sources without importing benchmark dependencies.

Run with ``uv run --with pyyaml python tools/unification/eval_inventory.py --sources PATH``.
"""

import argparse
import ast
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import yaml

from verifyit.adapters.harness_native import native_config_route


class SourceLoader(yaml.SafeLoader):
    pass


def tagged_value(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return {"tag": suffix, "value": loader.construct_scalar(node), "source_dir": str(loader.source_dir)}
    return {"tag": suffix, "value": loader.construct_sequence(node)}


SourceLoader.add_multi_constructor("!", tagged_value)


def revision(root):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def source_record(root, path):
    return {"path": str(path.relative_to(root)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def resolve_config(path, seen=None):
    path = path.expanduser().resolve()
    if seen is None:
        seen = set()
    if path in seen:
        raise ValueError(f"Cyclic YAML include: {path}")
    seen.add(path)
    loader = SourceLoader(path.read_text())
    loader.source_dir = path.parent
    try:
        config = loader.get_single_data() or {}
    finally:
        loader.dispose()
    if not isinstance(config, dict):
        return {}, []
    includes = config.pop("include", [])
    if isinstance(includes, str):
        includes = [includes]
    merged = {}
    evidence = []
    for include in includes:
        parent = path.parent / include
        inherited, ancestors = resolve_config(parent, seen)
        inherited.pop("task_list", None)
        merged.update(inherited)
        evidence.extend([str(parent), *ancestors])
    merged.update(config)
    return merged, evidence


def callable_record(root, path, node):
    return {
        **source_record(root, path),
        "function": node.name,
        "line": node.lineno,
        "calls": sorted({ast.unparse(call.func) for call in ast.walk(node) if isinstance(call, ast.Call)}),
    }


SPECIFICATIONS = {
    "metric": "lm_eval_mapping.md#metric-contract-response-and-aggregation-artifacts",
    "exact": "evalchemy_mapping.md#exact-harness-exact-normalization-and-alternative-references",
    "math": "evalchemy_mapping.md#math-profiles-symbolic-and-normalization-comparators",
    "ifeval": "evalchemy_mapping.md#ifeval-registry-official-checker-profile-and-result-vectors",
    "judge": "evalchemy_mapping.md#judge-classifier-explicit-prompt-and-label-protocol",
    "execution": "evalchemy_mapping.md#execution-contract-preserve-source-cases-and-metric-outputs",
}


def callables(root, directory):
    records = []
    for path in sorted(directory.rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                records.append(callable_record(root, path, node))
    return records


def harness_classification(path, config):
    task = config.get("task")
    custom = config.get("process_results")
    output = config.get("output_type", "class-defined" if config.get("class") else "generate_until")
    if output not in ("generate_until", "multiple_choice", "loglikelihood", "loglikelihood_rolling", "class-defined"):
        raise ValueError(f"Unclassified output type {output!r}: {path}")
    if isinstance(task, list) or (config.get("group") and not isinstance(task, str)):
        mapping = "orchestration"
        reason = "Task group expansion and dataset aggregation stay in harness."
    elif custom or config.get("class"):
        mapping = "metric_bridge"
        reason = "Preserve source callable and every structured per-sample/aggregate metric."
    elif output == "multiple_choice":
        mapping = "metric_bridge"
        reason = "Likelihood argmax, character/byte normalization, greedy flags and optional mutual " "information."
    elif output in ("loglikelihood", "loglikelihood_rolling"):
        mapping = "metric_bridge"
        reason = "Raw likelihood and weighted perplexity/bits aggregates are not bounded candidate rewards."
    else:
        mapping = "metric_bridge"
        reason = (
            "Generation filters and configured metrics require exact source semantics; text "
            "primitive equivalence unproven."
        )
    metrics = config.get("metric_list") or []
    metric_names = [item.get("metric") for item in metrics if isinstance(item, dict)]
    candidates = []
    if output == "generate_until" and "exact_match" in metric_names:
        candidates.append("exact")
        reason += (
            " Exact primitive differs on stripping, casefold versus lower, regex/punctuation "
            "normalization and multiple-reference reduction."
        )
    if "ifeval" in path.parts:
        candidates.append("ifeval")
        reason += (
            " Compare strict/loose instruction-level and prompt-level vectors separately; native "
            "IFEval registry coverage requires parity."
        )
    if any(name in path.parts for name in ("hendrycks_math", "minerva_math", "math_verify", "hrm8k")):
        candidates.append("math")
        reason += " Preserve benchmark box selection, normalization and fallback equivalence."
    return mapping, reason, candidates, output


def harness_records(root, directory):
    records = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or not (path.suffix == ".yaml" or path.name.endswith("_yaml")):
            continue
        config, includes = resolve_config(path)
        if not config:
            continue
        task = config.get("task")
        custom = config.get("process_results")
        mapping, reason, candidates, output = harness_classification(path, config)
        callable_evidence = []
        for value in (custom, config.get("class")):
            if isinstance(value, dict) and value.get("tag") == "function":
                symbol = value["value"]
                module, _, _function = symbol.rpartition(".")
                module_path = Path(value["source_dir"]) / (module.replace(".", "/") + ".py")
                if not module_path.exists():
                    module_path = root / (module.replace(".", "/") + ".py")
                callable_evidence.append(
                    {
                        "symbol": symbol,
                        **(source_record(root, module_path) if module_path.exists() else {"external_module": module}),
                    }
                )
        native_route = native_config_route(config) if isinstance(task, str) else None
        records.append(
            {
                **source_record(root, path),
                "task": task,
                "group": config.get("group"),
                "kind": "task" if isinstance(task, str) else "group" if mapping == "orchestration" else "template",
                "includes": [str(Path(p).relative_to(root)) for p in includes],
                "output_type": output,
                "process_results": custom,
                "class": config.get("class"),
                "metric_list": config.get("metric_list"),
                "filters": config.get("filter_list"),
                "mapping": native_route or mapping,
                "native_route": native_route,
                "reason": (
                    "Native source-normalized exact/likelihood selection; filters and aggregators remain source-owned."
                    if native_route
                    else reason
                ),
                "primitive_candidates": candidates,
                "callable_evidence": callable_evidence,
                "classification": (
                    "orchestration" if not isinstance(task, str) else "adapter" if native_route else "spec-needed"
                ),
                "required_specs": ([] if not isinstance(task, str) or native_route else ["metric", *candidates]),
                "existing_mode": (
                    "mcq"
                    if native_route == "likelihood_choice"
                    else "exact" if native_route else candidates[0] if candidates else "script"
                ),
                "source_scorer": custom or config.get("class") or "lm_eval.api.task.ConfigurableTask.process_results",
            }
        )

    def relative_tags(value):
        if isinstance(value, dict):
            return {
                key: str(Path(item).relative_to(root)) if key == "source_dir" else relative_tags(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [relative_tags(item) for item in value]
        return value

    return relative_tags(records)


PRIMITIVES = {
    "AMC23": "math",
    "AIME24": "math",
    "AIME25": "math",
    "HMMT": "math",
    "MATH500": "math",
    "JEEBench": "math",
    "GSM8KPerturbed": "exact",
    "GPQADiamond": "mcq",
    "MMLUPro": "mcq",
    "IFEval": "ifeval",
    "IFBench": "script",
    "AIW": "exact",
    "CruxEval": "script",
    "HumanEval": "script",
    "HumanEvalPlus": "script",
    "MBPP": "script",
    "MBPPPlus": "script",
    "BigCodeBench": "script",
    "CodeForces": "stdio",
    "CodeElo": "stdio",
    "LiveCodeBench": "script",
    "LiveCodeBenchv5": "script",
    "LiveCodeBenchv5_official": "script",
    "MultiPLE": "script",
    "SWEbench": "script",
    "SimpleQA": "judge",
    "SimpleQAMini": "judge",
    "FinanceBench": "judge",
    "HLE": "judge",
    "OlympiadBench": "math",
    "OlympiadBenchFull": "math",
    "OlympiadBenchDeterministic": "math",
    "MTBench": "judge",
    "WildBench": "judge",
    "alpaca_eval": "judge",
    "MixEval": "judge",
    "zeroeval": "script",
    "LiveBench": "script",
    "RepoBench": "script",
    "MRCR": "script",
    "NUPA-Loose": "script",
    "NUPA5K-Loose": "script",
}


def evalchemy_records(root):
    records = []
    for path in sorted((root / "eval/chat_benchmarks").glob("*/eval_instruct.py")):
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bases = [ast.unparse(base) for base in node.bases]
            if not any("Benchmark" in base for base in bases):
                continue
            metrics = {}
            for statement in node.body:
                if isinstance(statement, ast.Assign):
                    for target in statement.targets:
                        if isinstance(target, ast.Name) and target.id in ("METRICS", "PRIMARY_METRIC"):
                            metrics[target.id] = ast.literal_eval(statement.value)
            name = path.parent.name
            if name not in PRIMITIVES:
                raise ValueError(f"Unclassified new Evalchemy benchmark: {name}")
            scoring = [
                statement
                for statement in node.body
                if isinstance(statement, ast.FunctionDef) and statement.name == "evaluate_responses"
            ]
            evidence = [callable_record(root, path, statement) for statement in scoring]
            primitive = PRIMITIVES[name]
            caveats = {
                "math": (
                    "Box extraction, math-verify anchors versus Minerva fallback, list/vector semantics "
                    "and optional judge fallback must match."
                ),
                "mcq": (
                    "Retain benchmark extractor and option shuffle; use grade_mcq_candidate after "
                    "extraction. Per-category/repeat counts and errors stay upstream."
                ),
                "exact": (
                    "Benchmark normalization and reference selection must remain explicit; verifyit "
                    "strips/casefolds while source may use strict strings."
                ),
                "ifeval": (
                    "Compare instruction registry, strict/loose response transformations and prompt versus"
                    " instruction aggregate separately."
                ),
                "judge": (
                    "Keep exact prompt, response label taxonomy, retries and error records. Judge rubric "
                    "scale alone does not preserve these semantics."
                ),
                "stdio": (
                    "Preserve function-call versus stdin conventions, per-test timeouts, numerical "
                    "tolerance and compilation error categories."
                ),
                "script": (
                    "Existing execution primitive hosts original scorer. Named/structured metric bridge "
                    "preserves source vector; scalar script output alone loses information."
                ),
            }
            records.append(
                {
                    **source_record(root, path),
                    "benchmark": name,
                    "class": node.name,
                    "bases": bases,
                    "declared_metrics": metrics,
                    "primitive_candidate": PRIMITIVES.get(name),
                    "mapping": primitive,
                    "classification": (
                        "adapter"
                        if primitive == "mcq" or name in {"AIW", "GSM8KPerturbed"}
                        else ("adapter-hybrid" if name in {"AIME24", "AIME25", "MATH500"} else "spec-needed")
                    ),
                    "required_specs": (
                        []
                        if primitive == "mcq" or name in {"AIW", "GSM8KPerturbed"}
                        else [
                            primitive if primitive in SPECIFICATIONS else "execution",
                            "metric",
                        ]
                    ),
                    "clean_equivalence": primitive == "mcq" or name in {"AIW", "GSM8KPerturbed"},
                    "native_profile": ("boxed" if name in {"AIME24", "AIME25", "MATH500"} else None),
                    "source_retained_fallback": (
                        "minerva-on-missing-parse" if name in {"AIME24", "AIME25", "MATH500"} else None
                    ),
                    "scoring_evidence": evidence,
                    "contract": caveats[primitive],
                }
            )
    classes = {record["class"]: record for record in records}
    for record in records:
        if record["scoring_evidence"]:
            continue
        for base in record["bases"]:
            inherited = classes.get(base.rsplit(".", 1)[-1])
            if inherited is not None:
                record["scoring_evidence"] = inherited["scoring_evidence"]
                record["inherited_scorer"] = inherited["class"]
                break
    return records


def source_inventory(sources):
    roots = {name: sources / name for name in ("evalchemy", "lm-eval-harness")}
    outputs = {
        "evalchemy": {
            "revision": revision(roots["evalchemy"]),
            "benchmarks": evalchemy_records(roots["evalchemy"]),
            "grading_callables": callables(roots["evalchemy"], roots["evalchemy"] / "eval"),
        },
        "lm_eval": {
            "revision": revision(roots["lm-eval-harness"]),
            "configs": harness_records(roots["lm-eval-harness"], roots["lm-eval-harness"] / "lm_eval/tasks"),
            "grading_callables": callables(roots["lm-eval-harness"], roots["lm-eval-harness"] / "lm_eval/tasks"),
        },
    }
    for payload in outputs.values():
        payload["specifications"] = SPECIFICATIONS
    outputs["evalchemy"]["harness_overrides"] = harness_records(
        roots["evalchemy"], roots["evalchemy"] / "eval/lm_eval_tasks"
    )
    return outputs


def prepare_inventory(payload, evidence_path):
    functions = payload["grading_callables"]
    evidence_path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in functions))
    payload["python_functions_discovered"] = len(functions)
    payload["grading_callables"] = [
        record
        for record in functions
        if "process_results" in record["function"]
        or record["function"] == "evaluate_responses"
        or record["function"].startswith(("grade", "score"))
    ]
    contracts = {}
    for records_key in ("configs", "benchmarks", "harness_overrides"):
        for record in payload.get(records_key, []):
            for field in ("reason", "contract"):
                if field not in record:
                    continue
                contract = record.pop(field)
                identifier = hashlib.sha256(contract.encode()).hexdigest()[:12]
                contracts[identifier] = contract
                record["contract_id"] = identifier
    payload["contracts"] = contracts
    metric_contracts = {}
    filter_contracts = {}
    for records_key in ("configs", "harness_overrides"):
        for record in payload.get(records_key, []):
            for field, catalog in (("metric_list", metric_contracts), ("filters", filter_contracts)):
                value = record.pop(field)
                if value is not None:
                    encoded = json.dumps(value, sort_keys=True)
                    identifier = hashlib.sha256(encoded.encode()).hexdigest()[:12]
                    catalog[identifier] = value
                    record[field + "_id"] = identifier
            for key in list(record):
                if record[key] is None or record[key] == []:
                    del record[key]
    payload["metric_contracts"] = metric_contracts
    payload["filter_contracts"] = filter_contracts


def write_inventory(path, payload):
    lines = []
    for key, value in sorted(payload.items()):
        if isinstance(value, list):
            body = ",\n".join(json.dumps(record, sort_keys=True, separators=(",", ":")) for record in value)
            lines.append(json.dumps(key) + ":[\n" + body + "\n]")
        else:
            lines.append(json.dumps(key) + ":" + json.dumps(value, sort_keys=True, separators=(",", ":")))
    path.write_text("{\n" + ",\n".join(lines) + "\n}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/unification"))
    parser.add_argument("--runtime-index", type=Path, help="Verified TaskManager discovery JSON")
    parser.add_argument("--evidence", type=Path, help="Directory for transient full function graphs")
    args = parser.parse_args()
    args.sources = args.sources.resolve()

    outputs = source_inventory(args.sources)
    if args.runtime_index is not None:
        runtime = json.loads(args.runtime_index.read_text())
        records = {record["path"]: record for record in outputs["lm_eval"]["configs"]}
        scoring_entries = [entry for entry in runtime["entries"] if entry["kind"] in ("TASK", "PY_TASK")]
        missing = [entry for entry in scoring_entries if entry["path"] not in records]
        if missing:
            raise ValueError(f"Runtime tasks absent from inventory: {missing}")
        for inline in runtime["inline_tasks"]:
            source_path = args.sources / "lm-eval-harness" / inline["source_path"]
            _, reason, candidates, output = harness_classification(source_path, inline["config"])
            inline.update(
                classification="spec-needed",
                required_specs=["metric", *candidates],
                source_scorer="lm_eval.api.task.ConfigurableTask.process_results",
                output_type=output,
                existing_mode=candidates[0] if candidates else "script",
                contract=reason,
            )
            if set(inline["config"]) == {"task"}:
                inline.update(
                    classification="invalid-task-configuration",
                    source_failure="Group references unknown task name without task configuration",
                )
            declared_include = inline["config"].get("include")
            if isinstance(declared_include, str):
                include_path = source_path.parent / declared_include
                inline["declared_include"] = (
                    source_record(args.sources / "lm-eval-harness", include_path)
                    if include_path.exists()
                    else {"missing": declared_include}
                )
                inline["include_resolved_by_source_factory"] = False
        for member in runtime["invalid_group_members"]:
            member.update(
                classification="invalid-task-configuration",
                required_specs=["metric"],
                source_failure="TaskFactory requires task or group key in group member",
            )
        outputs["lm_eval"]["runtime_discovery"] = {
            "counts": runtime["counts"],
            "implementation_hashes": runtime["implementation_hashes"],
            "runtime_tasks_matched": len(scoring_entries),
            "unmatched_runtime_tasks": len(missing),
            "inline_tasks": runtime["inline_tasks"],
            "invalid_group_members": runtime["invalid_group_members"],
            "group_overrides": runtime["group_overrides"],
        }
    evidence_dir = args.evidence or args.sources.parent / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        prepare_inventory(payload, evidence_dir / f"{name}_function_graph.jsonl")
        counts = Counter(
            record["classification"]
            for key in ("benchmarks", "configs", "harness_overrides")
            for record in payload.get(key, [])
            if key == "benchmarks" or record["kind"] == "task"
        )
        payload["coverage_counts"] = {
            "adapter": counts["adapter"],
            "adapter-hybrid": counts["adapter-hybrid"],
            "spec-needed": counts["spec-needed"],
            "unknown": 0,
        }
        for records_key in ("benchmarks", "configs", "harness_overrides"):
            if records_key in payload:
                population = Counter(record["classification"] for record in payload[records_key])
                payload[records_key + "_coverage"] = {**dict(population), "unknown": 0}
        write_inventory(args.output / f"{name}_inventory.json", payload)
        print(name, dict(counts))


if __name__ == "__main__":
    main()
