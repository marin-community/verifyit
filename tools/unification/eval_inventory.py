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


def callables(root, directory):
    records = []
    for path in sorted(directory.rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                records.append(
                    {
                        **source_record(root, path),
                        "function": node.name,
                        "line": node.lineno,
                        "calls": sorted(
                            {ast.unparse(call.func) for call in ast.walk(node) if isinstance(call, ast.Call)}
                        ),
                    }
                )
    return records


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
        output = config.get("output_type", "generate_until")
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
        callable_evidence = []
        for value in (custom, config.get("class")):
            if isinstance(value, dict) and value.get("tag") == "function":
                symbol = value["value"]
                module, _, _function = symbol.rpartition(".")
                module_path = Path(value["source_dir"]) / (module.replace(".", "/") + ".py")
                if not module_path.exists():
                    module_path = root / (module.replace(".", "/") + ".py")
                callable_evidence.append(
                    {"symbol": symbol, "path": str(module_path.relative_to(root)) if module_path.exists() else None}
                )
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
                "mapping": mapping,
                "reason": reason,
                "primitive_candidates": candidates,
                "callable_evidence": callable_evidence,
                "classification": "orchestration" if mapping == "orchestration" else "adapter",
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
            evidence = [
                {
                    "path": str(path.relative_to(root)),
                    "function": statement.name,
                    "line": statement.lineno,
                    "calls": sorted(
                        {ast.unparse(call.func) for call in ast.walk(statement) if isinstance(call, ast.Call)}
                    ),
                }
                for statement in scoring
            ]
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
                    "mapping": "mcq" if primitive == "mcq" else "adapter_required",
                    "classification": "adapter",
                    "clean_equivalence": primitive == "mcq",
                    "scoring_evidence": evidence,
                    "contract": caveats[primitive],
                }
            )
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/unification"))
    args = parser.parse_args()
    roots = {name: args.sources / name for name in ("evalchemy", "lm-eval-harness")}
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
    outputs["evalchemy"]["harness_overrides"] = harness_records(
        roots["evalchemy"], roots["evalchemy"] / "eval/lm_eval_tasks"
    )
    evidence_dir = args.sources.parent / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        functions = payload["grading_callables"]
        (evidence_dir / f"{name}_function_graph.jsonl").write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in functions)
        )
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
    args.output.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        # One source record per line keeps the complete corpus reviewable.
        lines = []
        for key, value in sorted(payload.items()):
            if isinstance(value, list):
                body = ",\n".join(json.dumps(record, sort_keys=True, separators=(",", ":")) for record in value)
                lines.append(json.dumps(key) + ":[\n" + body + "\n]")
            else:
                lines.append(json.dumps(key) + ":" + json.dumps(value, sort_keys=True, separators=(",", ":")))
        (args.output / f"{name}_inventory.json").write_text("{\n" + ",\n".join(lines) + "\n}\n")
        print(name, {key: len(value) for key, value in payload.items() if isinstance(value, list)})
    print(Counter(record["kind"] for record in outputs["lm_eval"]["configs"]))


if __name__ == "__main__":
    main()
