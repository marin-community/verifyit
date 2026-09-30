# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
"""Inventory every tracked Harbor adapter and verifier entrypoint at a pinned head."""

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

REVISION = "6f94f2237224869a49c249a737d701147afc33b6"
ENTRYPOINTS = {"test.sh", "test.bat", "run-tests.sh"}


def inventory(source: Path) -> dict:
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if revision != REVISION:
        raise ValueError(f"expected pinned Harbor {REVISION}, got {revision}; review new contracts")
    files = subprocess.check_output(["git", "ls-files"], cwd=source, text=True).splitlines()
    adapter_names = sorted(
        {path.split("/")[1] for path in files if path.startswith("adapters/") and len(path.split("/")) > 2}
    )
    semantics_path = Path(__file__).resolve().parents[2] / "docs/unification/harbor_semantics.json"
    semantics = json.loads(semantics_path.read_text())
    contracts = {record["adapter"]: record for record in semantics["adapters"]}
    if semantics["revision"] != revision or set(contracts) != set(adapter_names):
        raise ValueError("curated semantics do not cover the pinned adapter population")
    records = []
    for name in adapter_names:
        adapter_files = [path for path in files if path.startswith(f"adapters/{name}/")]
        entries = [path for path in adapter_files if Path(path).name in ENTRYPOINTS]
        # Include generators: some adapters download the upstream grader or render a
        # dynamic test.sh rather than storing a static template in the repository.
        evidence = []
        for path in adapter_files:
            if Path(path).suffix not in {".py", ".sh", ".bat", ".toml"}:
                continue
            data = (source / path).read_bytes()
            text = data.decode(errors="replace")
            if not any(
                token in text for token in ("reward.json", "reward.txt", "test.sh", "test.bat", "tests/", "tests_dir")
            ) and not ("template" in path and Path(path).suffix == ".py"):
                continue
            functions = []
            if Path(path).suffix == ".py":
                try:
                    syntax = ast.parse(text)
                    functions = [
                        {"name": node.name, "line": node.lineno}
                        for node in ast.walk(syntax)
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                except SyntaxError:
                    if "template" not in path:
                        raise
                    functions = [{"name": "rendered-template", "line": 1}]
            evidence.append(
                {
                    "path": path,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "reward_channels": [channel for channel in ("reward.json", "reward.txt") if channel in text],
                    "functions": functions,
                }
            )
        if not evidence:
            evidence = [
                {"path": path, "sha256": hashlib.sha256((source / path).read_bytes()).hexdigest(), "reward_channels": []}
                for path in adapter_files
                if Path(path).name in {"README.md", "adapter.py"}
            ]
        records.append(
            {
                "adapter": name,
                "entrypoints": entries,
                "evidence": evidence,
                "primitives": contracts[name]["primitives"],
                "classification": contracts[name]["classification"],
                "contract": contracts[name]["contract"],
                "specification": contracts[name].get("specification"),
                "requirements": [
                    "retain task image, cwd, services, protected test upload and declared environment",
                    "redirect /logs/verifier reward artifacts into VERIFYIT_LOGS_DIR or copy them after execution",
                    "explicitly select reward_key for named metrics; selected reward must lie in [0,1]",
                    "retain native named metrics and apply an explicit benchmark score transform "
                    "when selected metric is outside [0,1]",
                    "preserve infrastructure errors and test evidence; "
                    "validate task-specific harness parity before replacement",
                ],
                "parity_verified": False,
            }
        )
    configs = [path for path in files if Path(path).name == "task.toml"]
    scripts = [path for path in files if Path(path).name in ENTRYPOINTS]
    return {
        "repository": "https://github.com/marin-community/harbor",
        "revision": revision,
        "scope": "curated semantic routes for every adapter; per-task execution parity not yet established",
        "adapters": len(records),
        "tracked_task_configs": len(configs),
        "tracked_test_entrypoints": len(scripts),
        "task_configs": configs,
        "test_entrypoints": scripts,
        "runtime_contract": {
            "path": "src/harbor/verifier/verifier.py",
            "verifyit_mode": "script",
            "classification": "adapter",
            "reward": (
                "reward.json named metric map takes precedence over reward.txt scalar; "
                "absent reward after nonzero exit is runtime error; "
                "absent reward after zero exit is task author error"
            ),
            "limitations": (
                "script default timeout is scored zero; Harbor outer deadline is an exception; "
                "retain Harbor timeout ownership in adapter. Arbitrary external custom "
                "import_path implementations cannot be inventoried from this repository."
            ),
        },
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(inventory(args.source), indent=2) + "\n")


if __name__ == "__main__":
    main()
